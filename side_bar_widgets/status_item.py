"""Keyboard-accessible status bar settings."""
from __future__ import annotations
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

class StatusItem(QLabel):
    """A keyboard accessible, clickable status-bar item."""
    def __init__(self, text: str, action, parent=None):
        """Bind a status value to its corresponding setting or chooser."""
        super().__init__(text, parent)
        self.action = action
        # A clickable QLab;e otherwise cannot be reache with the keyboard.
        self.setFocusPolicy(Qt.StrongFocus) 
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, ev):
        """Invoke the setting on a left click only."""
        if ev.button() == Qt.LeftButton:
            self.action()
        super().mousePressEvent(ev)
        
    def keyPressEvent(self, ev):
        """Let keyboard users activate the same control."""
        if ev.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.action()
            ev.accept()
            return
        super().keyPressEvent(ev)
        