# Welcome actions and recent recources, without a second editor stack.
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QScrollArea, QVBoxLayout, QWidget
)


TEMPLATES = {
    "Python script": (True, '"""Describe this script."""\n\n\ndef main():\n    """Run the script."""\n    print("Hello")\n\n\nif __name__ == "__main__":\n    main()\n'),
    "Markdown note": (False, "# New note\n\n## Notes\n\n"),
    "Markdown README": (False, "# Project name\n\n## Purpose\n\n## Installation\n\n## Usage\n\n"),
}


class WelcomeScreen(QScrollArea):
    """Emit user intentions; MainWindow owns opening and document creation."""
    
    openFileRequested = pyqtSignal()
    openFolderRequested = pyqtSignal()
    recentFileRequested = pyqtSignal(str)
    recentProjectRequested = pyqtSignal(str)
    templateRequested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        content = QWidget(self)
        content.setProperty("designPanel", True)
        self.setWidget(content)
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        title = QLabel("Welcome to MyCodeEditor", content)
        title.setTextFormat(Qt.PlainText)
        font = title.font()
        font.setPointSize(font.pointSize() + 5)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addWidget(QLabel("Open a file or folder, or start an unsaved document.", content))
        buttons = QHBoxLayout()
        for label, signal in (("Open file", self.openFileRequested),
                              ("Open folder", self.openFolderRequested)):
            button = QPushButton(label, content)
            button.clicked.connect(lambda checked=False, target=signal: target.emit())
            buttons.addWidget(button)
        layout.addLayout(buttons)
        layout.addWidget(QLabel("Start from a template", content))
        for name in TEMPLATES:
            button = QPushButton(name, content)
            button.clicked.connect(lambda checked=False, key=name: self.templateRequested.emit(key))
            layout.addWidget(button)
        self.recent_files = self._make_list(layout, "Recent files", content)
        self.recent_projects = self._make_list(layout, "Recent projects", content)
        self.recent_files.itemActivated.connect(
            lambda item: self.recentFileRequested.emit(item.data(Qt.UserRole)))
        self.recent_projects.itemActivated.connect(
            lambda item: self.recentProjectRequested.emit(item.data(Qt.UserRole)))
        layout.addStretch(1)

    @staticmethod
    def _make_list(layout, title, parent):
        layout.addWidget(QLabel(title + " — double-click or press Enter", parent))
        widget = QListWidget(parent)
        widget.setAccessibleName(title)
        widget.setMinimumHeight(100)
        widget.setMaximumHeight(180)
        layout.addWidget(widget)
        return widget

    @staticmethod
    def _fill(widget, entries):
        widget.clear()
        paths = [entry for entry in entries if isinstance(entry, str) and entry][:10]
        if not paths:
            item = QListWidgetItem("No recent entries yet", widget)
            item.setFlags(Qt.NoItemFlags)
            return
        for entry in paths:
            path = Path(entry)
            item = QListWidgetItem(f"{path.name or entry} — {path.parent}", widget)
            item.setToolTip(entry)
            item.setData(Qt.UserRole, entry)

    def refresh(self, files, projects):
        """Keep full paths as item data; display names are only labels."""
        self._fill(self.recent_files, files)
        self._fill(self.recent_projects, projects)