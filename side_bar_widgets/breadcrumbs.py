# Path breadcrums for the active documen.
from pathlib import Path
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

class Breadcrumbs(QWidget):
    directory_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.row = QHBoxLayout()
        self.row.setContentsMargins(4, 2, 4, 2)
        self.row.setSpacing(2)
        
    def set_path(self, path: str | Path | None) -> None:
        """Rebuild segments for the current document."""
        while self.row.count():
            item = self.row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not path:
            return
        resolved = Path(path).expanduser().absolute()
        parts = list(reversed(resolved.parents)) + [resolved]
        for part in parts:
            button = QPushButton(part.name or str(part))
            button.setFlat(True)
            button.clicked.connect(lambda _checked=False, p=part: self.directory_requested.emit(str(p if p.is_dir() else p.parent)))
            self.row.addWidget(button)
        