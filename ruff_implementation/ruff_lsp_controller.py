"""Bridge one PythonEditor document to the shared Ruff languafe server."""

from __future__ import annotations

from itertools import count
from pathlib import Path
from typing import Any
from uuid import uuid4

from PyQt5.QtCore import QObject, QPoint, QTimer, pyqtSignal
from PyQt5.QtWidgets import QMenu, QMessageBox, QToolTip

from code_intelligence.lsp_coordinates import lsp_to_character
from code_intelligence.performance import timed
from ruff_implementation.ruff_diagnostics_model import RuffDiagnostic, RuffPosition, RuffSeverity
from ruff_implementation.ruff_diagnostics_view import RuffDiagnosticView
from ruff_implementation.workspace_edit import WorkspaceEditApplier, WorkspaceEditError


class RuffLspController(QObject):
    """Keep one QScintilla Python document synchronized with Ruff LSP."""
    diagnostics_changed = pyqtSignal(object, list)
    _document_versions = count(1)
    
    def __init__(self, editor, client, parent=None):
        # Parent this controller to the editor unless a different explicit parent was supplied.
        # Destroying the tab then also destroys its controller.
        super().__init__(parent or editor)

        self.editor = editor
        self.client = client
        self._uri = self._uri_for_path(editor.full_path)
        
        # Reuse the existing visual layer. It remains responsible only for QScintilla
        # indicators, marker circles, tooltips and range caching.
        self.view = RuffDiagnosticView(editor)
        
        # LSP versions begin at an integer and must increase for every didChange.
        self.document_version = next(self._document_versions)
        
        # didOpen must be sent exactly once per URI/server lifecycle.
        self._opened = False
        self._closed = False
        self._action_generation = 0
        self._pending_diagnostics = False
        
        # Full-buffer updates are delayed slightly while a user is typing.
        # This prevents sending one didChange messafe for every individual keypress.
        self.change_timer = QTimer(self)
        self.change_timer.setSingleShot(True)
        self.change_timer.setInterval(180)
        self.change_timer.timeout.connect(self._send_change)
        
        # QScintilla emits textChanged for user input, pasted text, fixes, etc.
        editor.textChanged.connect(self._on_text_changed)
        
        # If Ruff is still starting when this tab is constructed, open_document
        # wil run as soon as initialize/initialized completes.
        client.server_ready.connect(self.open_document)
        client.server_stopped.connect(self._on_server_stopped)

        client.diagnostics_published.connect(self._on_diagnostics_published)
        if client.is_ready:
            self.open_document()
    
    @property
    def uri(self) -> str:
        """Return the stable LSP URI identifying this document to Ruff."""
        return self._uri

    @staticmethod
    def _uri_for_path(path) -> str:
        if path is None:
            path = Path.cwd() / f"untitled-{uuid4().hex}.py"
        return Path(path).resolve().as_uri()

    def _retire_display(self):
        """Withdraw Ruff state after an identity or server-lifecycle change.

        Unlike an ordinary edit, relocation. source replacement or server
        replacement must not retain old paint. Stop a queued send, invalidate
        action menus, remove hover/Problems data and clear Ruff-owned visuals.
        This does not emit diagnostics_changed: retirement is not a clean result.
        """
        self.change_timer.stop()
        self._action_generation += 1
        self._pending_diagnostics = True
        QToolTip.hideText()
        self.view.clear()
        self._clear_problem_rows()

    def _on_server_stopped(self):
        """Retire a stopped session before server_ready can reopen this buffer."""
        self._opened = False
        self._retire_display()

    def relocate(self, path):
        """Migrate this open buffer to a new URI after Save As or rename."""
        self._retire_display()
        old_uri = self._uri
        if self._opened and self.client.is_ready:
            self.client.close_document(old_uri)
        self._uri = self._uri_for_path(path)
        self._opened = False
        self.document_version = next(self._document_versions)
        self.open_document()

    def set_client(self, client):
        """Reconnect this document when the selected Ruff interpreter changes."""
        try:
            self.client.server_ready.disconnect(self.open_document)
            self.client.server_stopped.disconnect(self._on_server_stopped)
            self.client.diagnostics_published.disconnect(self._on_diagnostics_published)
        except TypeError:
            pass
        self._retire_display()
        self.client = client
        self._opened = False
        client.server_ready.connect(self.open_document)
        client.server_stopped.connect(self._on_server_stopped)
        client.diagnostics_published.connect(self._on_diagnostics_published)
        if client.is_ready:
            self.open_document()
        
    def open_document(self):
        """Send didOpen once after the shared server is ready."""
        if self._closed or self._opened or not self.client.is_ready:
            return
        
        self.client.open_document(
            self.uri,
            self.editor.text(),
            self.document_version,
        )
        self._opened = True
        
    def sync_from_editor(self):
        """Synchronize editor text after programmatic loading with blocked signals."""
        if self._closed:
            return
        self._retire_display()
        # setTextSafely() blocks editor.textChanged while loading a disk file.
        # Therefore this method manually creates a new LSP document version for the newly loaded source text.
        self.document_version = next(self._document_versions)
        
        if not self._opened:
            # Ruff may still be starting. If it is ready, this sends didOpen with the current loaded text.
            # If it is not ready yet, the existing server_ready -> open_document signal connection will do so later.
            self.open_document()
            return
        
        if not self.client.is_ready:
            return
            
        # The Ruff server already knows this document, but perbiously recieved the empty editor text during 
        # PythonEditor construction. Replace it immediately with the actual source read from disk.
        self.client.change_document(self.uri, self.editor.text(), self.document_version)
    
    @timed("gui.ruff_edit")
    def _on_text_changed(self):
        """Advance the source revision while retaining only visual pending ranges.

        On the first edit of a pending burst, remove stale hover/action metadata
        and Problems rows. Scintilla retains and adjusts existing indicator
        ranges as text changes. No full-buffer copy occurs on the normal open
        path; the existing single-shot timer sends after typing becomes quiet.
        """
        if self._closed:
            return
        if not self._pending_diagnostics:
            self._pending_diagnostics = True
            self.view.by_line.clear()
            QToolTip.hideText()
            self._clear_problem_rows()
        self.document_version = next(self._document_versions)
        if not self._opened:
            self.open_document()
        if self._opened:
            self.change_timer.start()

    
    @timed("gui.ruff_send")
    def _send_change(self):
        """Transmit the current complete QScintilla text buffer to Ruff."""
        if self._closed or not self._opened or not self.client.is_ready:
            return

        self.client.change_document(
            self.uri,
            self.editor.text(),
            self.document_version,
        )

    def _lsp_column_to_character(self, line: int, column: int) -> int:
        """Convert one current line and reject clamped or split-character offsets.

        The shared converter remains available to other features. This stricter
        diagnostic boundary verifies a round trip so malformed provider data
        cannot be silently painted over a neighboring character.
        """
        if type(line) is not int or not 0 <= line < self.editor.lines():
            raise ValueError("Diagnostic line is outside the document")
        text = self.editor.text(line).rstrip("\r\n")
        encoding = self.client.position_encoding
        character = lsp_to_character(text, column, encoding)
        prefix = text[:character]
        units = {"utf-8": lambda: len(prefix.encode("utf-8")),
                 "utf-16": lambda: len(prefix.encode("utf-16-le")) // 2,
                 "utf-32": lambda: len(prefix)}[encoding]()
        if units != column:
            raise ValueError("Diagnostic column exceeds a line or splits a character")
        return character
    
    @timed("gui.ruff_publish")
    def _on_diagnostics_published(self, uri: str, raw_diagnostics, version):
        """Replace Ruff paint only for a complete current successful snapshot.

        Empty lists are meaningful successes and clear old ranges. Unversioned,
        stale, malformed or stopped-session data cannot clear pending paint.
        Validation finishes before the first visual or Problems mutation.
        """
        if (self._closed or not self._opened or not self.client.is_ready or uri != self.uri
                or type(version) is not int or version != self.document_version):
            return
        if not isinstance(raw_diagnostics, list):
            self.client.server_error.emit("Ruff diagnostics must be a list.")
            return
        try:
            diagnostics = [self._to_diagnostic(raw) for raw in raw_diagnostics]
        except (ValueError, TypeError, AttributeError, OverflowError, UnicodeError):
            self.client.server_error.emit("Ruff sent invalid diagnostic coordinates or fields.")
            return
        self._pending_diagnostics = False
        self.view.render(diagnostics)
        self.diagnostics_changed.emit(self.editor, diagnostics)

    def _to_diagnostic(self, raw: dict) -> RuffDiagnostic:
        """Validate one complete diagnostic against current source coordinates.

        Required nested ranges and message text are checked before constructing
        the display object. Endpoints use the negotiated encoding. Raw protocol
        data is preserved so Topic 04 can request the matching Ruff code action.
        """
        if not isinstance(raw, dict) or not isinstance(raw.get("message"), str):
            raise ValueError("Invalid diagnostic object/message")
        span = raw.get("range")
        if not isinstance(span, dict):
            raise ValueError("Invalid diagnostic range")
        points = []
        for name in ("start", "end"):
            point = span.get(name)
            if not isinstance(point, dict):
                raise ValueError("Invalid diagnostic endpoint")
            line, column = point.get("line"), point.get("character")
            points.append(RuffPosition(line, self._lsp_column_to_character(line, column)))
        start, end = points
        if (end.line, end.column) < (start.line, start.column):
            raise ValueError("Reversed diagnostic range")
        severity = raw.get("severity", 2)
        if type(severity) is not int or severity not in (1, 2, 3, 4):
            raise ValueError("Invalid diagnostic severity")
        return RuffDiagnostic(
            code=str(raw.get("code", "Ruff")), message=raw["message"],
            severity={1: RuffSeverity.ERROR, 2: RuffSeverity.WARNING,
                      3: RuffSeverity.INFO, 4: RuffSeverity.INFO}[severity],
            start=start, end=end, revision=self.document_version, raw=raw,
        )


    def hover(self, position) -> bool:
        """Show current Ruff hover text; retained pending paint is noninteractive."""
        if self._closed or self._pending_diagnostics or not self._opened:
            QToolTip.hideText()
            return False
        # SCI_POSITIONFROMPOINT (2022) returns a Scintilla byte position at the
        # mouse coordinate. -1 means the pointer is outside text content.
        byte_position = self.editor.SendScintilla(
            2022,
            position.x(),
            position.y(),
        )
        if byte_position < 0:
            QToolTip.hideText()
            return False

        # Ask Scintilla to map its own byte position to a line, without copying
        # or decoding the entire document for a hover event.
        line = self.editor.SendScintilla(self.editor.SCI_LINEFROMPOSITION, byte_position)
        diagnostic = self.view.at_line(line)

        if diagnostic:
            QToolTip.showText(
                self.editor.mapToGlobal(position),
                self.view.tooltip(diagnostic),
                self.editor,
            )
            return True

        QToolTip.hideText()
        return False

    def context_menu(self, event: Any, view: Any=None) -> bool | None:
        """Request fixes for the exact current diagnostic under the pointer.

        view may be a split view sharing the controller's document. Its mouse
        coordinates identify a Scintilla byte position in that shared buffer.
        Only QPoint is retained after this method returns, since Qt owns the
        temporary event object. Return False to preserve the editor's fallback
        context menu when no current diagnostic covers the clicked position.
        """
        view = view or self.editor
        position = view.SendScintilla(view.SCI_POSITIONFROMPOINT, event.pos().x(), event.pos().y())
        if position < 0:
            return False
        location = self.editor.lineIndexFromPosition(position)
        candidates = []
        for group in self.view.by_line.values():
            for diagnostic in group:
                start = diagnostic.start.line, diagnostic.start.column
                end = diagnostic.end.line, diagnostic.end.column
                if diagnostic.revision == self.document_version and (start <= location < end or start == end == location):
                    candidates.append(diagnostic)
        diagnostic = max(candidates, key=lambda item: item.severity, default=None)
        if diagnostic is None:
            return False
        point = QPoint(event.globalPos())
        identity = self._action_identity()
        
        def receive(actions: Any, error: Any, uri: Any, revision: Any) -> None:
            """Build a temporary menu, then recheck identity after its event loop."""
            if not self._action_is_current(identity):
                return
            if error:
                QMessageBox.warning(self.editor, "Quick fixes", str(error))
                return
            menu = QMenu(self.editor)
            try:
                pairs = []
                for action in actions:
                    if not isinstance(action, dict):
                        continue
                    item = menu.addAction(str(action.get("title", "Quick fix")))
                    item.setEnabled(not bool(action.get("disabled")))
                    pairs.append((item, action))
                
                if not pairs:
                    menu.addAction("No quick fix available").setEnabled(False)
                chosen = menu.exec_(point)
                if not self._action_is_current(identity):
                    return
                for item, action in pairs:
                    if chosen is item:
                        try:
                            self.apply_code_action(action, uri, revision)
                        except WorkspaceEditError as error:
                            QMessageBox.warning(self.editor, "Quick fixes", str(error))
                        break
            finally:
                menu.deleteLater()

        self.request_quick_fixes(diagnostic, receive)
        return True
                    

    def shutdown(self):
        """Stop synchronization, tell Ruff the tab is closed, clear visuals."""
        self._clear_problem_rows()
        if self._closed:
            return
        self._closed = True
        self.change_timer.stop()
        # didClose is sent only after didOpen; otherwise the server has never
        # heard about this document and closing it would be meaningless.
        if self._opened:
            self.client.close_document(self.uri)
        try:
            self.client.server_ready.disconnect(self.open_document)
            self.client.server_stopped.disconnect(self._on_server_stopped)
            self.client.diagnostics_published.disconnect(self._on_diagnostics_published)
        except TypeError:
            pass
        self.view.clear()

    def _clear_problem_rows(self) -> None:
        """Remove this URI's Problems rows when its text or lifecycle changes."""
        manager = getattr(self.editor.window(), "diagnostics_manager", None)
        if manager is not None:
            manager.clear_collection("ruff", self.uri)
            
    def request_quick_fixes(self, diagnostic: Any, callback: Any) -> None:
        """Request fixes for a current diagnostic and discard obsolete replies.

        callback receives (actions, error, uri, revision) on the GUI thread.
        The raw LSP diagnostic supplies its original negotiated range and data.
        A stale request is reported immediately. A reply whose document or server
        identity changed is dropped because the menu no longer describes that
        document. The existing transport owns request IDs and response delivery.
        """
        identity = self._action_identity()
        uri, revision, client, generation = identity
        raw = diagnostic.raw
        if (not self._action_is_current(identity) or diagnostic.revision != revision
                or not isinstance(raw, dict) or not isinstance(raw.get("range"), dict)):
            callback([], {"message": "Diagnostic is stale or has no LSP range"}, uri, revision)
            return
        self.change_timer.stop()
        self._send_change()

        def receive(result: Any, error: Any) -> None:
            """Release a reply only while its captured action identity is valid."""
            if not self._action_is_current(identity):
                return
            if error is None and not isinstance(result, (list, type(None))):
                error = {"message": "Malformed code-action response"}
            callback(result if isinstance(result, list) else [], error, uri, revision)

        client.request("textDocument/codeAction", {
            "textDocument": {"uri": uri},
            "range": raw["range"],
            "context": {"diagnostics": [raw], "only": ["quickfix"], "triggerKind": 1},
        }, receive)
    def apply_code_action(self, action: Any, uri: Any, revision: Any) -> None:
        """Validate a complete direct WorkspaceEdit and apply it as one Undo group.

        Args:
            action: Selected LSP CodeAction dictionary, including its edit.
            uri: Document URI captured when requesting this action.
            revision: Local buffer revision captured with that URI.

        Raises:
            WorkspaceEditError: The action is disabled, malformed, requires a
                command/resolve step, or its edit fails identity/range validation.

        The caller checks server identity immediately  before invoking this method.
        WorkspaceEditApplier checks document identity and read-only state again.
        No prefix of a rejected edit is applied
        """
        if (not isinstance(action, dict) or action.get("disabled") or action.get("command") or not isinstance(action.get("edit"), dict)):
            raise WorkspaceEditError("This action requires an unsupported command or resolve step")
        WorkspaceEditApplier(self).apply(action["edit"], uri, revision)

    def _action_identity(self):
        """Return the current document and server-session identity.

        The client object detects interpreter replacement. The generation detects
        a process restart within that object. URI/revision detect relocation and edits,
        including Undo/Redo through the existing revision counter.
        """
        return self.uri, self.document_version, self.client, self._action_generation

    def _action_is_current(self, identity) -> bool:
        """Require a live open document, ready server and unchanged identity."""
        return (not self._closed and self._opened and self.client.is_ready and self._action_identity() == identity)

        
        
        
        