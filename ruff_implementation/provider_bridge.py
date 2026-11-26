# Coordindate on Basedpyright process and each shared Python document once
from __future__ import annotations
from time import monotonic

from PyQt5 import sip
from PyQt5.QtCore import QObject, QProcess, QTimer

from ruff_implementation.type_client import TypeClient
from ruff_implementation.type_diagnostics import TypeVersions, convert_types
from ruff_implementation.diagnostic_layer import configure_document, paint_document



class ProviderBridge(QObject):
    """Own type synchronization, fresh publication and retiring child processes.
    
    A 100 ms GUI timer inspects metadata only. A changed buffer must stay quiet
    for 350 ms before its full text is copied and sent. Split views share one 
    analysis owner. No worker thread reads widgets and no keypress starts a child.
    """
    
    def __init__(self, window) -> None:
        """Install the coordinator after window.documents and Problems exist."""
        super().__init__(window)
        self.window = window
        self.closed = False
        self.live = {}
        self.observed = {}
        self.versions = TypeVersions()
        self.retired = []
        self.client = self._new_client(window.python_runner.interpreter)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.sync)
        self.timer.start()
        self.client.start()
        
    def _new_client(self, interpreter):
        """Construct and connect one stopped child; caller decides when to start."""
        client = TypeClient(interpreter, self.window._workspace_root, self)
        client.server_ready.connect(self.resync)
        client.server_stopped.connect(self._stopped)
        client.diagnostics_published.connect(self.receive_types)
        client.server_error.connect(self._error)
        return client


    def _error(self, message):
        """Show Basedpyright infrastructure errors in both terminal and status bar."""
        detail = "Basedpyright: " + message.replace("Ruff", "LSP")
        print("[Basedpyright LSP]", detail, flush=True)
        self.window.statusBar().showMessage(detail, 8000)


    def buffers(self):
        """Return live URI -> (shared document, owner controller) on the GUI thread."""
        result = {}
        for document in self.window.documents.all():
            editor = document.analysis_owner
            if editor is None or sip.isdeleted(editor) or getattr(editor, "large_file_mode", False):
                continue
            controller = getattr(editor, "ruff_lsp", None)
            if controller is not None and not controller._closed:
                result[controller.uri] = (document, controller)
        return result

    def resync(self):
        """Reopen live buffers after readiness; no earlier wire revision is retained."""
        self.versions.reset()
        self.observed.clear()
        self.sync()

    def _stopped(self):
        """Withdraw this servers session's results and prepare current buffers to reopen"""
        self.versions.reset()
        self.observed.clear()
        self.window.diagnostics_manager.clear_provider("basedpyright")
        for document, controller in self.live.values():
            paint_document(document, "basedpyright", [])

    def sync(self):
        """Retire missing buffers, detect edits and send only quiet unsent snapshots."""
        if self.closed:
            return
        for client in self.retired[:]:
            if client.process.state() == QProcess.NotRunning:
                self.retired.remove(client)
                client.deleteLater()

        current = self.buffers()
        now = monotonic()
        for uri, (document, controller) in self.live.items():
            if current.get(uri) != (document, controller):
                self.client.close_document(uri)
                self.versions.forget(uri)
                self.observed.pop(uri, None)
                self.window.diagnostics_manager.clear_collection("basedpyright", uri)
                paint_document(document, "basedpyright", [])

        self.live = current
        for uri, (document, controller) in current.items():
            configure_document(document, "basedpyright")
            revision = controller.document_version
            previous = self.observed.get(uri)
            if previous is None or previous[:2] != (controller, revision):
                self.observed[uri] = (controller, revision, now + 0.350)
                self.window.diagnostics_manager.clear_collection("basedpyright", uri)
                continue
            if (not self.client.is_ready or now < previous[2] or self.versions.is_sent(uri, controller, revision)):
                continue
            was_open = uri in self.versions.sent
            wire = self.versions.issue(uri, controller, revision)
            source = controller.editor.text()
            if was_open:
                self.client.change_document(uri, source, wire)
            else:
                self.client.open_document(uri, source, wire)


    def receive_types(self, uri, rows, wire_revision):
        """Publish only an exact current snapshot; malformed data keeps previous paint.

        Recheck the live store at callback time rather than trusting the last
        polling turn. Convert UTF-16 only after version and owner checks pass.
        The application Diagnostics keeps the local revision for navigation
        """
        pair = self.buffers().get(uri) if not self.closed else None
        if pair is None:
            return
        document, controller = pair
        revision = controller.document_version
        if not self.versions.accepts(uri, controller, revision, wire_revision):
            return

        editor = controller.editor
        try:
            result = convert_types(rows, uri, document.path, revision, editor.lines(), editor.text)
        except (ValueError, TypeError, UnicodeError) as error:
            self._error(f"Reject diagnostic snapshot: {error}")
            return
        self.window.diagnostics_manager.replace("basedpyright", uri, result)
        paint_document(document, "basedpyright", result)

    def restart(self, interpreter=None):
        """Replace the process after workspace/interpreter changes, retaining ownership.

        Old signals are disconnected before shutdown. Retiring QProcesses remain
        parented until stopped and the window includes them in its close wait.
        """
        if self.closed:
            return
        old = self.client
        old.server_ready.disconnect(self.resync)
        old.server_stopped.disconnect(self._stopped)
        old.diagnostics_published.disconnect(self.receive_types)
        old.server_error.disconnect(self._error)
        self._stopped()
        old.shutdown()
        self.retired.append(old)
        self.client = self._new_client(interpreter or self.window.python_runner.interpreter)
        self.client.start()


    def is_running(self):
        """Inspect current/retained process state without waiting in the GUI thread."""
        return any(client.process.state() != QProcess.NotRunning for client in [self.client, *self.retired])


    def shutdown(self):
        """Stop submission and begin asynchronous shutdown for every owned child.."""
        if self.closed:
            return
        self.closed = True
        self.timer.stop()
        for client in [self.client, *self.retired]:
            client.shutdown()





        
        
        
        
        
