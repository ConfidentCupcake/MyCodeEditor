# A basedpyright specialization for the asynchronous lsp_to_character transport
from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt5.QtCore import QObject

from ruff_implementation.ruff_lsp_client import RuffLspClient
from ruff_implementation.type_protocol import server_reply, settings_for


class TypeClient(RuffLspClient):
    """Own one type-server process; leave document/view ownership to pyspellchecker.
    
    The inherited transport supplies framing, request deadlines, bounded restarts
    and asynchronous shutdown. This subclass supplies only launch, capability
    negotiation and server specific configuration.
    """
    def __init__(self, interpreter: str, root: Path, parent: QObject | None = None) -> None:
        """Configure a stopped client using an absolute selected interpreter.
        
        interpreter must have basedpyright installed. The metadata lookup runs
        in that interpreter, never on the GUI thread. No child starts until start()
        is called. root: Path, is resolved by the base transport.
        """
        super().__init__(interpreter, root, parent)
        self.analysis_interpreter = interpreter
        self.launch_arguments = [
            "-c", 
            "from importlib.metadata import distribution; "
            "next(e for e in distribution('basedpyright').entry_points " 
            "if e.group == 'console_scripts' and e.name == 'basedpyright-langserver')"
            ".load()()",
            "--stdio",
        ]
            
    def configuration(self) -> dict[str, Any]:
        """Return in settings tree for initialization and configuration requests."""
        return settings_for(self.analysis_interpreter)
    
    def _folders(self) -> list[dict[str, str]]:
        """Describe this client's single workspace in LSP URI form."""
        return [{"uri": self.workspace_root.as_uri(), "name": self.workspace_root.name}]
    
    def _initialize(self) -> None:
        """Send initialize after QProcess.started, advertising implemented features.
        
        Only UTF-16 is offered so the pyspellchecker conversion has one explicit contract.
        Dynamic registration, process UI, completion and workspace edits are not advertised.
        Existing editor completion remains unchanged.
        """
        self.request("initialize", {
            "processId": None,
            "rootUri": self.workspace_root.as_uri(),
            "workspaceFolders": self._folders(),
            "capabilities": {
                "general": {"positionEncodings": ["utf-16"]},
                "workspace": {"configuration": True, "workspaceFolders": True},
                "textDocument": {
                    "synchronization": {"dynamicRegistration": False},
                    "publishDiagnostics": {"versionSupport": True},
                },
            },
        }, self._on_initialized)
    
    def _on_initialized(self, result: Any, error: Any) -> None:
        """Validate the handshake, send settings, then announce readiness.
        
        A failure kills this process without retrying an incompatible protocol.
        A missing positionEncoding means UTF-16 under LSP. 
        Settings are sent before server_ready lets pyspellchecker open documents. 
        No widget is accessed.
        """
        self._initialize_timer.stop()
        if self._shutting_down or not self._started:
            return
        caps = result.get("capabilities") if isinstance(result, dict) else None
        if (error is not None or not isinstance(caps, dict) or caps.get("positionEncoding", "utf-16") != "utf-16"):
            self.server_error.emit(f"Basedpyright initialization failed: {error or 'invalid capabilities/encoding'}")
            self._suppress_restart_once = True
            self.process.kill()
            return
        
        self.position_encoding = "utf-16"
        self.notify("initialized", {})
        self._initialized = True
        self.notify("workspace/didChangeConfiguration", {"settings": self.configuration()})
        self._stable_timer.start()
        self.server_ready.emit()
        
    def _handle_message(self, message: Any) -> None:
        """Answer supported server requests or delegate to the transport router.
        
        The pure helper never consumes diagnostics or responses to our own requests.
        Those retain the inherited timeout and callback behavior.
        """
        reply = server_reply(message, self.configuration(), self._folders())
        if reply is not None:
            self._send(reply)
            return
        super()._handle_message(message)
        
