# Debounce and apply pure fold models to QSciScintilla.
from __future__ import annotations
from typing import Any

import hashlib

from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtGui import QColor

from code_intelligence.fold_model import markdown_fold_lines, python_fold_lines
from code_intelligence.performance import timed


SCI_SETFOLDLEVEL: int = 2222
SC_FOLDLEVELBASE: int = 0x400
SC_FOLDLEVELHEADERFLAG: int = 0x2000



class FoldingController(QObject):
    """Own folding configuration and incremental scheduling for one editor."""
    def __init__(self, editor: Any, language: str, margin: int = 2) -> None:
        """Configure the folding margin and debounce model recalculation after text changes."""
    
        super().__init__(editor)
        self.editor = editor
        self.language = language
        self._last_digest = b""
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(180)
        self._timer.timeout.connect(self.recalculate)
        self.editor.setFolding(QsciScintilla.BoxedTreeFoldStyle, margin)
        self.editor.setMarginWidth(margin, 16)
        self.apply_theme()
        self.editor.textChanged.connect(self.schedule)
        self.schedule()
        
    def apply_theme(self) -> None:
        """Match the folding gutter and markers to the current editor theme."""
        lexer = self.editor.lexer()
        background = (lexer.paper(0) if lexer is not None else QColor("#1e1f22"))
        foreground = (lexer.color(0) if lexer is not None else QColor("#abb2bf"))
        
        self.editor.setFoldMarginColors(background, foreground)
        
        for marker in range(25,32): 
            self.editor.setMarkerForegroundColor(foreground, marker)
            self.editor.setMarkerBackgroundColor(background, marker)
            
        
    
    def schedule(self) -> None:
        """Restart the short quiet-period timer after an edit."""
        self._timer.start()
    
    @timed("gui.folding")
    def recalculate(self) -> None:
        """Compute and publish fold metadata when document text changed."""
        text = self.editor.text()
        digest = hashlib.blake2b(text.encode("utf-8"), digest_size=16).digest()
        if digest == self._last_digest:
            return
        model = python_fold_lines(text) if self.language == "python" else markdown_fold_lines(text)
        for line_number in range(self.editor.lines()):
            item = model[line_number] if line_number < len(model) else type(model[0])(0)
            level = SC_FOLDLEVELBASE + item.depth
            if item.header:
               level |= SC_FOLDLEVELHEADERFLAG
            self.editor.SendScintilla(SCI_SETFOLDLEVEL, line_number, level)
        self._last_digest = digest
    
    def set_all(self, expanded: Any) -> None:
        """Set all fold headers explicitly; do not interpret foldAll's children flags as state."""
        self.recalculate()
        for line in range(self.editor.lines()):
            level = self.editor.SendScintilla(self.editor.SCI_GETFOLDLEVEL, line)
            if level & SC_FOLDLEVELHEADERFLAG:
                current = bool(self.editor.SendScintilla(self.editor.SCI_GETFOLDEXPANDED, line))
                if current != expanded:
                    self.editor.foldLine(line)
        
        
        
    