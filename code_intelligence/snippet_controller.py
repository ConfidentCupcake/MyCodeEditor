# Maintain snippet fields in absolute UTF-8 byte coordinates.

from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QObject
from code_intelligence.snippet_parser import Placeholder, parse_snippet


class SnippetController(QObject):
    """Navigate supported fields and cancel on edits outside the active field."""
    
    def __init__(self, editor: Any) -> None:
        """Observe modification positions rather than guessing from total text length."""
        super().__init__(editor)
        self.editor = editor
        self.spans = []
        self.index = -1
        self.inserting = False
        editor.SCN_MODIFIED.connect(self._modified)
        
    @property
    def active(self):
        """Return whether a field is currently available for Tab navigation."""
        return 0 <= self.index < len(self.spans)
    
    def cancel(self) -> None:
        """Forget navigation ranges while retaining all inserted text."""
        self.spans = []
        self.index = -1
        
    def insert(self, source: Any) -> None:
        """Replace the selection once and convert character fields to byte ranges."""
        if self.editor.isReadOnly():
            return
        parsed = parse_snippet(source)
        editor = self.editor
        start = min(editor.SendScintilla(editor.SCI_GETANCHOR), editor.SendScintilla(editor.SCI_GETCURRENTPOS))
        self.cancel()
        self.inserting = True
        editor.beginUndoAction()
        try:
            editor.replaceSelectedText(parsed.text)
        finally:
            editor.endUndoAction()
            self.inserting = False
            
        self.spans = [Placeholder(field.number, start + len(parsed.text[:field.start].encode("utf-8")), start + len(parsed.text[:field.end].encode("utf-8"))) for field in parsed.placeholders]
        self.index = 0 if self.spans else -1
        self._select_active()
        
        
    def _modified(self, position: Any, kind: Any, text: Any, length: Any, *unused: Any) -> None:
        """Update fields by actual edit position; reject edits outside the active field."""
        if self.inserting or not self.active or not (kind & 3):
            return
        field = self.spans[self.index]
        deleted = length if kind & 2 else 0
        if position < field.start or position + deleted > field.end:
            self.cancel()
            return
        delta = -length if kind & 2 else length
        old_end = field.end 
        self.spans[self.index] = Placeholder(field.number, field.start, field.end + delta)
        # Number navigation order is not spatial order: compare byte positions.
        for index, other in enumerate(self.spans):
            if index != self.index and other.start >= old_end:
                self.spans[index] = Placeholder(other.number, other.start + delta, other.end + delta)
                
    
    def handle_tab(self, backwards: bool=False) -> bool:
        """Move to the previous/next field, or finish after the final field."""
        if not self.active:
            return False
        self.index += -1 if backwards else 1
        if not self.active:
            self.cancel()
        else:
            self._select_active()
        return True
    
    def _select_active(self) -> None:
        """Selected the active byte span through QScintilla's Unicode-aware conversion."""
        if self.active:
            field = self.spans[self.index]
            self.editor.setSelection(*self.editor.lineIndexFromPosition(field.start), *self.editor.lineIndexFromPosition(field.end))
            
        
