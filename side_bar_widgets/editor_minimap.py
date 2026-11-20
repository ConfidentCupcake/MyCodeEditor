# A sampled, read-only overview owned by one QScintilla view.
from __future__ import annotations

from PyQt5.QtCore import QEvent, QRectF, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget

class EditorMinimap(QWidget):
    """Represents one editor view as a sampled document-density overview.
    Responsibilities:
        Own the overview cache, refresh timer, painting, and pointer navigation.
        Observe the supplied editor without creating another Scintilla document,
        lexer, undo history, or diagnostics pipeline.

        Lifetime:
        Qt parents this widget to the editor viewport. Call shutdown() before
        retiring the editor so callbacks stop even if worker cleanup delays deletion.

        Notes:
        Source-line lengths are UTF-8 byte counts, including line endings. The
        strokes approximate density; they are not miniature syntax-highlighted text.
    """
    SAMPLE_LIMIT = 2048
    
    def __init__(self, editor, width=96):
        # A viewport child stays clear of both native scrollbars.
        """Initialize the per-view widget, cache state, timer and signal subscriptions.
        
        Args:
                editor: A live QScintilla view with a viewport and vertiacal scrollbar.
                width: Requested width in logical pixels, clamped to 48 through 220.
                
            Side effects:
                Parents the widget to editor.viewport(), installs a resize event filter,
                and connects edit/scroll/update notifications. Starts explicitly hidden.
                No document text is copied and no refresh timer is started here.

            Ownership:
                The QTimer is a child of this widget. The editor is observed, not owned
                by this widget; never delete the editor from a minimap callback.
        """
        super().__init__(editor.viewport())
        self.editor = editor
        self._width = max(48, min(int(width), 220))
        self._original_margin = editor.SendScintilla(editor.SCI_GETMARGINRIGHT)
        self._enabled = False
        self._closed = False
        self._dirty = True
        self._samples = []
        self._background = QColor("#1e1f22")
        self._foreground = QColor("#858585")
        self._highlight = QColor(120, 150, 190, 75)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName("Document overview minimap")
        self.setToolTip("Clock or drag to scroll through this document")
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(180)
        self._timer.timeout.connect(self._rebuild_cache)
        self._connections = [
            (editor.textChanged, self.schedule_refresh),
            (editor.verticalScrollBar().valueChanged, self._repaint),
            (editor.SCN_UPDATEUI, self._repaint),
        ]
        for signal, slot in self._connections:
            signal.connect(slot)
        editor.viewport().installEventFilter(self)
        self.hide()
        
    
    def set_colors(self, background, foreground):
        """Replace the cached paint colors and request a repaint."""
        
        self._background = QColor(background)
        self._foreground = QColor(foreground)
        self.update()
        
    
    def set_map_visible(self, visible):
        """Apply the visibility preference and reserve or release editor text space."""
        
        if self._closed:
            return
        
        self._enabled = bool(visible)
        margin = self._original_margin + self._width if visible else self._original_margin
        self.editor.SendScintilla(self.editor.SCI_SETMARGINRIGHT, 0, margin)
        self._update_geometry()
        self.setVisible(self._enabled)
        if self._enabled:
            self.raise_()
            self.schedule_refresh()
        else:
            self._timer.stop()
            
    def schedule_refresh(self, *args):
        """Mark cached sample stale and debounce a visible refresh."""
        
        if self._closed:
            return
        self._dirty = True
        if self._enabled and self.isVisible():
            self._timer.start()
            
    def _repaint(self, *args):
        """Request an updated viewport marker without the density cache."""
        
        if not self._closed and self._enabled:
            self.update()
            
    
    def _update_geometry(self):
        """Align the overview with the right edge of the editor viewport."""
        viewport = self.editor.viewport()
        width = min(self._width, viewport.width())
        self.setGeometry(viewport.width() - width, 0, width, viewport.height())
        
    
    def eventFilter(self, watched, event):
        """Observe viewport resize event while preserving normal event delivery."""
        if not self._closed and event.type() == QEvent.Resize:
            self._update_geometry()
            self.schedule_refresh()
        return super().eventFilter(watched, event)
    
    
    def showEvent(self, event):
        """Schedule deferred sample work when a hidden overview becomes visible."""
        
        super().showEvent(event)
        if self._dirty:
            self.schedule_refresh()
            
    
    def _rebuild_cache(self):
        """Sample bounded native source-line lengths after the debounce timeout."""
        
        if self._closed or not self._enabled or not self.isVisible():
            return
        total = max(1, self.editor.lines())
        count = min(total, max(1, self.height()), self.SAMPLE_LIMIT)
        self._samples = []
        for row in range(count):
            line = row * (total - 1) // max(1, count - 1)
            length = self.editor.SendScintilla(self.editor.SCI_LINELENGTH, line)
            self._samples.append((line, min(120, max(0, length))))
        self._dirty = False
        self.update()
            
    
    def paintEvent(self, event):
        """Draw cached density strokes and the current document-space viewpoet marker."""
        
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._background)
        painter.setPen(self._foreground)
        total = max(1, self.editor.lines())
        height = max(1, self.height())
        for line, length in self._samples:
            y = min(height - 1, line * height // total)
            stroke = min(max(0, self.width() - 8), int(length * 0.7))
            if stroke:
                painter.drawLine(4, y, 4 + stroke, y)
                
        # firstVisibleLine counts display rows; folds/wraps change that maping.
        display_first = self.editor.firstVisibleLine()
        rows = max(1, self.editor.SendScintilla(self.editor.SCI_LINESONSCREEN))
        first = self.editor.SendScintilla(self.editor.SCI_DOCLINEFROMVISIBLE, display_first)
        last = self.editor.SendScintilla(self.editor.SCI_DOCLINEFROMVISIBLE, display_first + rows)
        first = min(total - 1, max(0, first))
        last = total if last < 0 else min(total, max(first + 1, last))
        top = first * height / total
        size = min(height - top, max(2.0, (last-first) * height / total))
        painter.fillRect(QRectF(0, top, self.width(), size), self._highlight)
        
    
    def _navigate(self, y):
        """Scroll the observed editor toward a source line selected by map position."""
        total = max(1, self.editor.lines())
        line = min(total - 1, max(0, int(y * total / max(1, self.height()))))
        self.editor.ensureLineVisible(line)
        display = self.editor.SendScintilla(self.editor.SCI_VISIBLEFROMDOCLINE, line)
        rows = max(1, self.editor.SendScintilla(self.editor.SCI_LINESONSCREEN))
        self.editor.setFirstVisibleLine(max(0, display - rows // 2))
        self.update()
        
    def mousePressEvent(self, event):
        """Begin pointer navigation from a left-button press."""
        if event.button() == Qt.LeftButton:
            self._navigate(event.pos().y())
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Continue navigation while the left mouse button is held."""
        if event.buttons() & Qt.LeftButton:
            self._navigate(event.pos().y())
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    
    def shutdown(self):
        """Release subscriptions and stop minimap work before editor retirement."""
        if self._closed:
            return
        self.set_map_visible(False)
        self._closed = True
        self._timer.stop()
        self.editor.viewport().removeEventFilter(self)
        for signal, slot in self._connections:
            signal.disconnect(slot)
        self._connections.clear()
    