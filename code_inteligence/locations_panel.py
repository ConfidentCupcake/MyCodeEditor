from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal


@dataclass(frozen=True)
class SourceLocation:
    """Store a disk path and zero-based line/character column for navigation."""
    path: Path
    line: int
    column: int
    label: str
    

class LocationsPanel(QTreeWidget):
    """Display provider-independent reference locations and emit selected records."""
    locationActivated = pyqtSignal(object)
    
    def __init__(self, parent: Any=None) -> None:
        """Create the symbol/path/line/column view and connect row activation."""
        super().__init__(parent)
        self.setHeaderLabels(("Symbol", "File", "Line", "Column"))
        self.itemActivated.connect(self._activate)
        
        
    def set_locations(self, locations: list[SourceLocation]) -> None:
        """Sort and replace rows while retaining each original location as hidden item data."""
        self.clear()
        for location in sorted(locations, key=lambda x: (str(x.path), x.line, x.column)):
            row = QTreeWidgetItem((location.label, location.path.name, str(location.line + 1), str(location.column + 1)))
            row.setToolTip(1, str(location.path))
            row.setData(0, Qt.UserRole, location)
            self.addTopLevelItem(row)
            
    def _activate(self, item: Any, _column: Any) -> None:
        """Emit the source location attached to the activated row."""
        location = item.data(0, Qt.UserRole)
        if location:
            self.locationActivated.emit(location)