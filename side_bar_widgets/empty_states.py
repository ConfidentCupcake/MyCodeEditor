"""An empty-state overlay tied to a real item view."""
from PyQt5 import sip
from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtWidgets import QLabel

class EmptyState(QObject):
    """Keep a noninteractive hint centered over an empty item view."""
    def __init__(self, view, message):
        super().__init__(view)
        self.view = view 
        self.label = QLabel(message,view.viewport())
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        view.viewport().installEventFilter(self)
        for signal in (view.model().rowsInserted, view.model().rowsRemoved, view.model().modelReset):
            signal.connect(self.refresh)
        self.refresh()
        
    def refresh(self, *args):
        """Show a hint only when the model has no root."""
        if sip.isdeleted(self.view) or sip.isdeleted(self.label):
            return
        self.label.setGeometry(self.view.viewport().rect())
        self.label.setVisible(self.view.model().rowCount() == 0)
        self.label.raise_()
        
    def eventFilter(self, watched, event):
        """Track viewport rezising without consuming its input."""
        if event.type() in (QEvent.Resize, QEvent.Show):
            self.refresh()
        return False
        
        