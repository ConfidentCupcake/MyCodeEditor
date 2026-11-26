"""
Qt JSON-RPC transport for the official "ruff server" language server.

This class intentionally contains no QScintilla code. Its Job is only:

1. Start one persistent 'python -m ruff server' process.
2. Send Language Server Protocol (LSP) requests and notifications.
3. Decode LSP Content Length framed messages from the server.
4. Emit Qt signals for diagnostics and server failures.

The GUI/editor layer lives in ruff_lsp_controller.py
"""

from __future__ import annotations

import json
from pathlib import Path

from PyQt5.QtCore import QObject, QProcess, QTimer, pyqtSignal


class RuffLspClient(QObject):
    """Persistent JSON-RPC client for the official "ruff server" process."""

    # Emitted whenever Ruff sends textDocument/publishDiagnostics.
    # Arguments:
    #   1. uri: LSP document URI, e.g. file:///C:/project/example.py
    #   2. diagnostics: list[dict] in standard LSP Diagnostic format
    #   3. version: LSP document version or None if the server omitted it

    diagnostics_published = pyqtSignal(str, object, object)

    # A non-fatal infrastructure message. MainWindow can show it in the statusBar
    # while detailed text is still printed to the PowerShell log,

    server_error = pyqtSignal(str)

    # Emitted exactly after the initialize -> initialized handshake completes.
    # RuffLspController instances us this to send their didOpen notification.
    server_ready = pyqtSignal()
    server_stopped = pyqtSignal()

    def __init__(self, python_executable: str, workspace_root: Path, parent=None):
        """
        Store workspace details and connect QProcess signals.

        Parameters:
            python_executable:
                The user-selected Python interpreter. It must have Ruff installed,
                because the process is started as: <python_executable> -m ruff server.
            workspace_root:
                Folder containing pyproject.toml, ruff.toml, or .ruff.toml.
            parent:
                Normally MainWindow, Qt will then destroy this client
                when the application window is destroyed.
        """
        super().__init__(parent)
        
        self.python_executable = python_executable
        self.workspace_root = Path(workspace_root).resolve()

        # QProcess asynchronously runs Ruff without freezing the Qt GUI thread.
        # Unlike subprocess.run(), it remains alive for the entire application.
        self.process = QProcess(self)

        # LSP messages can arrive split over several readyRead events, or many messages can arrive together.
        # This buffer holds unread raw bytes until a complete Content-Length-framed JSON message can be assembled.
        self._read_buffer = bytearray()

        # Every JSON-RPC request must have a unique integer ID.
        # Notifications intentionally do NOT have IDs and do not recieve responses.
        self._next_request_id = 1

        # request_id -> callback (result, error)
        # Formatting and code-action requests will use this later.
        self._pending_requests = {}

        # These flags distinguish "process exists" from "LSP handshake finished".
        self._started = False
        self._initialized = False
        self._shutting_down = False
        self._suppress_restart_once = False

        # QProcess signals fire on the Qt event loop. All UI-facing work remains
        # in the main Qt thread, which avoids unsafe widget access from threads.
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.errorOccurred.connect(self._on_process_error)
        self.process.finished.connect(self._on_finished)
        
        self.position_encoding = "utf-16"
        self._restart_attempts = 0
        self._max_restart_attempts = 3
        self._request_timers = {}
        self.launch_arguments = ["-m", "ruff", "server"]
        self.process.started.connect(self._initialize)
        self._initialize_timer = QTimer(self)
        self._initialize_timer.setSingleShot(True)
        self._initialize_timer.setInterval(10000)
        self._initialize_timer.timeout.connect(self._initialization_expired)
        self._restart_timer = QTimer(self)
        self._restart_timer.setSingleShot(True)
        self._restart_timer.timeout.connect(self.start)
        self._stable_timer = QTimer(self)
        self._stable_timer.setSingleShot(True)
        self._stable_timer.setInterval(60000)
        self._stable_timer.timeout.connect(self._reset_retries_if_stable)

    @property
    def is_ready(self) -> bool:
        """Return True only after Ruff completed LSP initialization."""
        return self._initialized and self.process.state() == QProcess.Running

    def start(self):
        """Start Ruff asynchronously; process.started begins the LSP handshake.
        
        Never wait for process creation on the GUI thread. A ten-second timer 
        covers both launch and initialize; retries remain bounded separately.
        Repeated calls while starting/running or shutting down are harmless.
        """
        if self._started or self._shutting_down:
            return
        self._restart_timer.stop()
        self._started = True
        self.process.setWorkingDirectory(str(self.workspace_root))
        self._initialize_timer.start()
        self.process.start(self.python_executable, self.launch_arguments)
        
    def _initialization_expired(self):
        """Abort a hung launch/handshake without blocking or claiming success."""
        if self._shutting_down or self.is_ready:
            return
        self.server_error.emit("Ruff launch/initialize timed out after 10 seconds.")
        if self.process.state() == QProcess.NotRunning:
            self._on_finished(-1, QProcess.CrashExit)
        else:
            self.process.kill()


    def _initialize(self):
        """
        Send the mandatory LSP initialize request.

        The LSP server will respond to this request with a capabilities object.
        Only after recieving that response may the client send 'initialized'.
        """
        workspace_uri = self.workspace_root.as_uri()

        params = {
            # The LSP field normally accepts an OS process ID. None is valid when the editor
            # foes not need the server to monitor client termination.
            "processId": None,
            # rootUri/workspaceFolders identify where Ruff should discover the
            # project's pyproject.toml, ruff.toml, or .ruff.toml configuration.
            "rootUri": workspace_uri,
            "workspaceFolders": [
                {
                    "uri": workspace_uri,
                    "name": self.workspace_root.name,
                }
            ],
            # Capabilities describe what the CLIENT supports, not what Ruff does.
            "capabilities": {
                "general": {
                    # LSP character position require in agreed encoding. Ask for UTF-8
                    # first because this editor is Scintilla/QScintilla-based.
                    # A future Unicode regression test must verify this selection.
                    "positionEncodings": ["utf-8", "utf-16"],
                },
                "textDocument": {
                    "synchronization": {
                        "dynamicRegistration": False,
                        "willSave": False,
                        "didSave": False,
                    },
                    "publishDiagnostics": {
                        # Accept related information if Ruff provides it.
                        "relatedInformation": True,
                        # Accept document version in pushed diagnostics.
                        # Version values allow controllers to reject stale result ranges.
                        "versionSupport": True,
                    },
                    "codeAction": {
                        # Advertise the action kinds this editor intends to support
                        # in the phase-two quick-fix implementation.
                        "codeActionLiteralSupport": {
                            "codeActionKind": {
                                "valueSet": [
                                    "",
                                    "quickfix",
                                    "source",
                                    "source.fixAll",
                                    "source.organizeImports",
                                ]
                            }
                        }
                    },
                },
                "workspace": {
                    "workspaceFolders": True,
                },
            },
            # Ruff-specific LSP setting. Ruff's existing pyproject.toml remains the source
            # of lint/format configuration. This only controls server integration behavior.
            "initializationOptions": {
                "settings": {
                    "configurationPreference": "filesystemFirst",
                    # Explicitly retain real-time parser/syntax diagnostics.
                    "showSyntaxErrors": True,
                    # Use debug only while integrating.
                    # Change to "warn" after success to reduce stderr logging noise.
                    "logLevel": "warn",
                }
            },
        }

        # 'initialize' is a REQUEST. The callback runs when Ruff responds with
        # matching JSON-RPC id, or with a JSON-RPC error.
        self.request("initialize", params, self._on_initialized)

    def _on_initialized(self, result, error):
        """Publish readiness only after a valid capability response and encoding.
        
        Failure is infrastructure failure, never a successful empty diagnostic snapshot.
        Invalid capabilities stop retries until the client is replaced.
        Owned timers are stopped on termination so an older run cannot reset a later 
        run's retry counter.
        """
        self._initialize_timer.stop()
        if self._shutting_down or not self._started:
            return
        capabilities = result.get("capabilities") if isinstance(result, dict) else None
        encoding = capabilities.get("positionEncoding", "utf-16") if isinstance(capabilities, dict) else None
        if error is not None or encoding not in {"utf-8", "utf-16"}:
            self.server_error.emit(f"Ruff initialization failed: {error or 'invalid capabilities/encoding'}")
            self._suppress_restart_once = True
            self.process.kill()
            return
        self.position_encoding = encoding
        self.notify("initialized", {})
        self._initialized = True
        self._stable_timer.start()
        self.server_ready.emit()
        
        
    def _reset_retries_if_stable(self):
        if self.is_ready and not self._shutting_down:
            self._restart_attempts = 0

    def open_document(self, uri: str, text: str, version: int):
        """Send the intitial in-memory content for one Python editor tab."""
        if not self.is_ready:
            return

        # After didOpen, LSP treats the supplied text as the authorative buffer.
        # The document does not need to be saved before Ruff can diagnose it.
        self.notify(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": "python",
                    "version": version,
                    "text": text,
                }
            },
        )

    def change_document(self, uri: str, text: str, version: int):
        """
        Syncronize a changed QScintilla buffer using full-text replacement.

        LSP supports incremental rangedm but complete buffer sync is safer for the first implementation.
        It elimates range calculation bugs and is practical because Ruff is fast and the controller debounces rapid typing.
        """
        if not self.is_ready:
            return

        self.notify(
            "textDocument/didChange",
            {
                "textDocument": {
                    "uri": uri,
                    "version": version,
                },
                # No 'range' means the entire document is replaced by this text.
                "contentChanges": [{"text": text}],
            },
        )

    def close_document(self, uri: str):
        """Tell Ruff it cna discard in-memory state for a closed tab."""
        if self.is_ready:
            self.notify(
                "textDocument/didClose",
                {"textDocument": {"uri": uri}},
            )

    def request(self, method: str, params, callback, timeout_ms: int = 10000):
        """Send one request with a bounded lifetime and invoke callback once.
        
        callback(result, error) runs on the GUI thread. A timeout or transport
        failure is an error, not a successful empty result. At most 128 requests
        reamin pending. The returned integer identifies a sent request; None
        means it was rejected before sending. params=None omits the field.
        """
        if len(self._pending_requests) >= 128:
            callback(None, {"code": -32000, "message": "Too many pending LSP requests"})
            return None
        request_id = self._next_request_id
        self._next_request_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params
        self._pending_requests[request_id] = callback
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._request_expired(request_id))
        self._request_timers[request_id] = timer
        timer.start(max(1, timeout_ms))
        if not self._send(payload):
            self._finish_request(request_id, None, {"code": -32000, "message": "Ruff server is not running"})
        return request_id
        
    
    def _finish_request(self, request_id, result, error):
        """Detach pending state before invoking application code; ignore late replies."""
        callback = self._pending_requests.pop(request_id, None)
        timer = self._request_timers.pop(request_id, None)
        if timer is not None:
            timer.stop()
            timer.deleteLater()
        if callback is not None:
            callback(result, error)
            
    
    def _request_expired(self, request_id):
        """Cancel outstanding work best-effort and complete locally with an error."""
        if request_id not in self._pending_requests:
            return
        if self.is_ready:
            self.notify("$/cancelRequest", {"id": request_id})
        self._finish_request(request_id, None, {"code": -32800, "message": "LSP request timed out"})

    def notify(self, method: str, params: dict):
        """Send one JSON-RPC notification with no request id."""
        self._send(
            {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
            }
        )

    def _send(self, payload: dict):
        """Frame and write a UTF-8 JSON-RPC message to Ruff stdin."""
        if self.process.state() != QProcess.Running:
            self.server_error.emit("Ruff server is not running.")
            return False

        # Compact JSON is optional but produces fewer bytes over the local pipe.
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

        # LSP framing uses the NUMBER OF UTF-8 BYTES, not len(str) characters.
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")

        # QProcess.write queues the bytes asynchronously to Ruff's stdin.
        self.process.write(header + body)
        return True

    def _read_stdout(self):
        """Read server output and extract every complete LSP-frame message."""
        self._read_buffer.extend(bytes(self.process.readAllStandardOutput()))
        if len(self._read_buffer) > 16 * 1024 * 1024:
            self._read_buffer.clear()
            self.server_error.emit("Ruff LSP input exceeded the 16 MiB safety limit.")
            self.process.kill()
            return

        while True:
            # Every LSP header ends with CRLF CRLF. If it is incomplete, preserve
            # current bytes and wait for Qt to emit readyReadStandardOutput again.
            header_end = self._read_buffer.find(b"\r\n\r\n")
            if header_end < 0:
                return

            header = self._read_buffer[:header_end].decode("ascii", errors="replace")

            content_length = None
            for line in header.split("\r\n"):
                name, seperator, value = line.partition(":")
                if seperator and name.lower() == "content-length":
                    try:
                        content_length = int(value.strip())
                    except ValueError:
                        content_length = None
                    break

            if content_length is None or content_length < 0 or content_length > 16 * 1024 * 1024:
                # Continueing after a broke header makes framing ambigous.
                # Clear it ans surface and actionable infrastructure error instead.
                self.server_error.emit(
                    "Ruff server sent an invalid or missing Content-Length header."
                )
                self._read_buffer.clear()
                self.process.kill()
                return

            message_start = header_end + 4
            message_end = message_start + content_length

            # Header arrived, but the JSON body has not finished arriving yet.
            if len(self._read_buffer) < message_end:
                return

            body = bytes(self._read_buffer[message_start:message_end])

            # Remove this complete message before processing it. A handler mey synchronously
            # cuase new server traffic; buffer state stays correct.
            del self._read_buffer[:message_end]

            try:
                message = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                self.server_error.emit(f"Invalid JSON-RPC payload from Ruff: {error}")
                continue
            self._handle_message(message)

    def _handle_message(self, message):
            """Validate JSON-RPC envelopes before routing replies or diagnostics.

            JSON arrays/scalars are not valid individual LSP messages. Unknown
            server requests receive MethodNotFound so the peer is not left waiting.
            A valid empty diagnostics list is forwarded; malformed data is not
            substituted with an empty list because that would erase real problems.
            """
            if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                self.server_error.emit("Invalid JSON-RPC message envelope from Ruff.")
                return
            if "id" in message:
                request_id = message["id"]
                if type(request_id) not in (int, str):
                    self.server_error.emit("Invalid JSON-RPC request identifier.")
                    return
                if "method" in message:
                    self._send({"jsonrpc": "2.0", "id": request_id,
                                "error": {"code": -32601, "message": "Unsupported server request"}})
                    return
                if ("result" in message) == ("error" in message):
                    self.server_error.emit("Invalid JSON-RPC response shape.")
                    return
                self._finish_request(request_id, message.get("result"), message.get("error"))
                return
            if message.get("method") == "textDocument/publishDiagnostics":
                params = message.get("params")
                if not isinstance(params, dict):
                    self.server_error.emit("Invalid Ruff diagnostic parameters.")
                    return
                uri, diagnostics, version = params.get("uri"), params.get("diagnostics"), params.get("version")
                if (not isinstance(uri, str) or not isinstance(diagnostics, list)
                        or any(not isinstance(item, dict) for item in diagnostics)
                        or (version is not None and type(version) is not int)):
                    self.server_error.emit("Invalid Ruff diagnostic publication.")
                    return
                self.diagnostics_published.emit(uri, diagnostics, version)

    def _read_stderr(self):
        """Print Ruff LSP logs without confusing them with protocol stdout."""
        text = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace")
        if text.strip():
            print(f"[Ruff LSP] {text.rstrip()}")

    def _on_process_error(self, error):
        """Convert QProcess startup/runtime failure into a visible Qt signal."""
        if not self._shutting_down:
            self.server_error.emit("Ruff server process error: " + self.process.errorString())
        if error == QProcess.FailedToStart:
            self._on_finished(-1, QProcess.CrashExit)

    def _on_finished(self, exit_code, _exit_status):
        """Clear state and retry failed startup only a bounded number of times."""
        if not self._started:
            return
        self._initialized = False
        self._started = False
        self._initialize_timer.stop()
        self._stable_timer.stop()
        self._read_buffer.clear()
        self.server_stopped.emit()
        for request_id in list(self._pending_requests):
            self._finish_request(request_id, None, {"code": -32000, "message": "Ruff server stopped"})

        if self._suppress_restart_once:
            self._suppress_restart_once = False
            return
        if self._shutting_down:
            return

        self._restart_attempts += 1
        if self._restart_attempts > self._max_restart_attempts:
            self.server_error.emit(
                "Ruff disabled after repeated startup failures. "
                "Check the selected interpreter in Settings."
            )
            return

        delay_ms = min(30_000, 1000 * 2 ** (self._restart_attempts - 1))
        self.server_error.emit(
            f"Ruff stopped with exit code {exit_code}; "
            f"retry {self._restart_attempts}/{self._max_restart_attempts}."
        )
        self._restart_timer.start(delay_ms)

    def shutdown(self):
        """Perform the LSP shutdown → exit sequence, then enforce a timeout."""
        self._shutting_down = True
        self._restart_timer.stop()
        self._initialize_timer.stop()
        self._stable_timer.stop()
        if self.process.state() == QProcess.NotRunning:
            return

        def after_shutdown(_result, error):
            if error is None and self.process.state() == QProcess.Running:
                self.notify("exit", {})
            else:
                self._force_stop()

        if self._initialized:
            # LSP shutdown has no params. Sending {} is invalid for Ruff.
            self.request("shutdown", None, after_shutdown)
            QTimer.singleShot(2000, self._force_stop)
        else:
            self._force_stop()

    def _force_stop(self):
        """Kill only when graceful shutdown did not finish."""
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
