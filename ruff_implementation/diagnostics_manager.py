from __future__ import annotations
from typing import Any

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from ruff_implementation.diagnostics_model import Diagnostic

class DiagnosticsManager(QObject):
    """Store complete diagnostic snapshot by provider and document."""
    
    changed = pyqtSignal(list)
    
    def __init__(self, parent: Any=None) -> None:
        """Create an empty provider/document snapshot map owned by the GUI thread."""
        super().__init__(parent)
        self._collections: dict[tuple[str, str], tuple[Diagnostic, ...]] = {}
        self._publish_timer = QTimer(self)
        self._publish_timer.setSingleShot(True)
        self._publish_timer.setInterval(0)
        self._publish_timer.timeout.connect(self._publish)

    def _publish(self) -> None:
        """Emit the newest combined snapshot once the GUI evnet loop resumes.

        Several provider updates in one turn share a single refresh. The
        store itself if updated synchronously, so all() always returns current
        data. This timer is GUI-owned; providers must publish through Qt signals
        when their work happens on another thread.
        """
        self.changed.emit(self.all())


    def _schedule_publish(self) -> None:
        """Queue one refresh without restarting an already pending timer."""
        if not self._publish_timer.isActive():
            self._publish_timer.start()


    def clear_collection(self, provider: str, uri: str) -> None:
        """Remove only this provider's results for one document.

        Provider controllers use this on closure, relocation or invalidation.
        clear_documents is revered to a document-wide lifecycle owner; a Ruff
        refresh must never erase Basedpyright or spelling results.
        """
        if self._collections.pop((provider, uri), None) is not None:
            self._schedule_publish()


    def replace(self, provider: str, uri: str, diagnostics: list[Diagnostic]) -> None:
        """Validate snapshot identity and replace or remove exactly one provider/document collection."""
        if any(item.provider != provider or item.uri != uri for item in diagnostics):
            raise ValueError("Diagnostic collection identity does not match its contents.")
        key = (provider, uri)
        if diagnostics:
            self._collections[key] = tuple(diagnostics)
        else:
            self._collections.pop(key, None)
        self._schedule_publish()

    def clear_document(self, uri: str) -> None:
        """Remove every provider collections belonging to one document URI."""
        self._collections = {key: value for key, value in self._collections.items() if key[1] != uri}
        self._schedule_publish()

    def clear_provider(self, provider: str) -> None:
        """Remoce a provider after its environment or server instance changes."""
        self._collections = {key: value for key, value in self._collections.items() if key[0] != provider}
        self._schedule_publish()
        
    def all(self) -> list[Diagnostic]:
        """Return a deterministic severity/path/position ordering of all retained diagnostics."""
        values = [item for group in self._collections.values() for item in group]
        return sorted(values, key=lambda item: (-int(item.severity), str(item.path or ""), item.source_range.start.line, item.source_range.start.column))


