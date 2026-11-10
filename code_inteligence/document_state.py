# One document state shared by multiple view, with a legacy dirty-set adapter.
from __future__ import annotations

from collections.abc import MutableSet
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from weakref import WeakKeyDictionary, WeakSet

from PyQt5.QtCore import QObject, pyqtSignal


@dataclass(eq=False)
class DocumentState:
    """Shared identity and flags; cursor, selection and pin state remain per-view."""
    path: Path | None
    dirty: bool = False
    read_only: bool = False
    externally_changed: bool = False
    disk_digest: bytes | None = None
    revision: int = 0
    views: WeakSet = field(default_factory=WeakSet)
    analysis_owner: object = None
    

@dataclass
class TabState:
    """Placement-independent flags belonging to one editor view."""
    pinned: bool = False
    preview: bool = False
    

@dataclass(frozen=True)
class ClosedTab:
    """A disk-backed reopen record; unsaved text is not a reopen snapshot."""
    path: Path
    python_mode: bool
    line: int
    column: int
    

class DocumentStateStore(QObject):
    """Own document/view associations without retaining closed editor widgets."""
    stateChanged = pyqtSignal(object)
    
    def __init__(self, parent: Any=None) -> None:
        """Create separate shared-document and per-tab maps."""
        super().__init__(parent)
        self.documents = WeakKeyDictionary()
        self.tabs = WeakKeyDictionary()
        self.recently_closed = []
        
    def attach(self, view: Any, path: Any=None, document: Any=None) -> Any:
        """Attach a new view; share state only when explicitly sharing its QsciDocument."""
        if view in self.documents:
            return self.documents[view]
        document = document or DocumentState(Path(path) if path else None)
        document.views.add(view)
        if document.analysis_owner is None:
            document.analysis_owner = view
        self.documents[view] = document
        self.tabs[view] = TabState()
        return document
    
    def document(self, view: Any) -> Any:
        """Return the one shared state for an attached editor."""
        return self.documents[view]
    
    def tab(self, view: Any) -> Any:
        """Return flags belogning only to the requested view."""
        return self.tabs[view]
    
    def all(self) -> Any:
        """Return each shared document once, preserving live view-map order."""
        return list(dict.fromkeys(self.documents.values()))
    
    def set_dirty(self, view: Any, dirty: Any) -> None:
        """Change shared dirty state and promote all edited previews to permanent tabs."""
        document = self.document(view)
        document.dirty = bool(dirty)
        if dirty:
            document.revision += 1
            for item in document.views:
                self.tab(item).preview = False
        self.stateChanged.emit(document)
        
    def detach(self, view: Any) -> Any:
        """Remove a view; the lifecycle coordinator transfers Ruff ownership first."""
        document = self.documents.pop(view, None)
        self.tabs.pop(view, None)
        if document is not None:
            document.views.discard(view)
            if document.analysis_owner is view:
                document.analysis_owner = next(iter(document.views), None)
        return document
    
    def remember_closed(self, view: Any, python_mode: Any) -> None:
        """Keep at most twenty disk-backed reopen locations, newest first."""
        document = self.document(view)
        if document.path is not None:
            line, column = view.getCursorPosition()
            self.recently_closed.insert(0, ClosedTab(document.path, python_mode, line, column))
            del self.recently_closed[20:]
            
class DirtyViews(MutableSet):
    """Adapt existing dirty-set callers to the store without a second source of truth."""
    
    def __init__(self, store: Any) -> None:
        """Retain the shared state store used by all membership and mutation operations."""
        self.store = store
        
    def __contains__(self, view: Any) -> Any:
        """Report shared dirtines for any attached view of the docuemnt."""
        return view in self.store.documents and self.store.document(view).dirty
    
    def __iter__(self) -> Any:
        """Yiel one representative per dirty document dor save/close prompt loops."""
        return iter([doc.analysis_owner for doc in self.store.all() if doc.dirty])
    
    def __len__(self) -> Any:
        """Count dirty documents rather than duplicate views."""
        return sum(doc.dirty for doc in self.store.all())
    
    def add(self, view: Any) -> None:
        """Mark the attached document dirty through its central state owner."""
        self.store.set_dirty(view, True)
    
    def discard(self, view: Any) -> None:
        """Clear dirtiness for every view after and explicit save or discard decision."""
        if view in self.store.documents:
            self.store.set_dirty(view, False)
            
            
        
        
        
    
