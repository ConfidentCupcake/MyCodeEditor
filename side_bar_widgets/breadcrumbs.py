"""Compact, independently styled path and Python-scope breadcrumbs."""
from pathlib import Path

from PyQt5.QtCore import QEvent, QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLayout, QScrollArea, QSizePolicy,
    QToolButton, QWidget,
)


class Breadcrumbs(QScrollArea):
    """Display navigation targets without retaining an editor or changing files.

    Long paths scroll horizontally with the wheel/trackpad. Tab focuses each
    segment and scrolls it into view; Space activates that segment.
    Colors are scoped locally, so general button styles cannot turn the crumbs
    into padded boxes. Dimensions use Qt logical pixels and scale with DPI.
    """

    directory_requested = pyqtSignal(str)
    line_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        """Create an owned, frameless row with explicit background painting."""
        super().__init__(parent)
        self.setObjectName('DocumentBreadcrumbs')
        self.setFrameShape(QFrame.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumWidth(0)
        self.setFixedHeight(max(34, self.fontMetrics().height() + 14))
        self.setAccessibleName('Document breadcrumbs')
        self.setToolTip('Scroll to reveal long paths. Tab between segments.')
        self.viewport().setObjectName('BreadcrumbViewport')

        self.body = QWidget()
        self.body.setObjectName('BreadcrumbBody')
        self.body.setAttribute(Qt.WA_StyledBackground, True)
        self.row = QHBoxLayout(self.body)
        self.row.setContentsMargins(8, 3, 8, 3)
        self.row.setSpacing(0)
        # Let the content exceed the viewport width without compressing labels.
        self.row.setSizeConstraint(QLayout.SetMinimumSize)
        self.setWidget(self.body)
        self.setStyleSheet('''
            QScrollArea#DocumentBreadcrumbs,
            QWidget#BreadcrumbViewport, QWidget#BreadcrumbBody {
                background: #1e1f22;
                border: none;
            }
            QToolButton[breadcrumbSegment="true"] {
                background: transparent;
                color: #aeb4c0;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 0px 5px;
                margin: 0px;
                min-width: 0px;
            }
            QToolButton[breadcrumbCurrent="true"] { color: #dcdfe4; }
            QToolButton[breadcrumbSegment="true"]:hover {
                background: #2b3039;
                color: #ffffff;
            }
            QToolButton[breadcrumbSegment="true"]:pressed {
                background: #363e4b;
            }
            QToolButton[breadcrumbSegment="true"]:focus {
                border-color: #61afef;
            }
            QLabel[breadcrumbSeparator="true"] {
                background: transparent;
                color: #697180;
                border: none;
                padding: 0px 3px;
                margin: 0px;
            }
        ''')
        self._key = None
        self._tail = None
        # A parent-owned timer avoids callbacks into an already deleted widget.
        self._reveal_timer = QTimer(self)
        self._reveal_timer.setSingleShot(True)
        self._reveal_timer.timeout.connect(self._reveal_tail)

    def sizeHint(self):
        """Offer usable width without making a long path widen the window."""
        return QSize(400, self.height())

    def minimumSizeHint(self):
        """Allow the toolbar to shrink while keeping the row height stable."""
        return QSize(0, self.height())

    def configure_toolbar(self, toolbar):
        """Style the dedicated host; call before adding this widget to it."""
        toolbar.setObjectName('BreadcrumbBar')
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setAllowedAreas(Qt.TopToolBarArea)
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setFixedHeight(self.height() + 1)
        toolbar.setStyleSheet('''
            QToolBar#BreadcrumbBar {
                background: #1e1f22;
                border: none;
                border-bottom: 1px solid #30343c;
                padding: 0px;
                spacing: 0px;
            }
        ''')

    def set_location(self, path, scopes=()):
        """Rebuild changed targets and reveal the file or innermost scope.

        ``scopes`` contains (name, zero_based_start, end, depth) tuples, as
        supplied by topic 3's scope_ranges helper and MainWindow integration.
        """
        scopes = tuple(scopes)
        key = (str(path or ''), scopes)
        if key == self._key:
            return
        self._key = key
        self._reveal_timer.stop()
        self._tail = None
        while self.row.count():
            item = self.row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # Hide now: deleteLater alone leaves old controls briefly visible.
                widget.hide()
                widget.deleteLater()

        segments = []
        if path:
            resolved = Path(path).expanduser().absolute()
            for part in reversed(resolved.parents):
                target = str(part)
                segments.append((part.name or target, target,
                                 lambda p=target: self.directory_requested.emit(p)))
            segments.append((resolved.name, str(resolved),
                             lambda: self.line_requested.emit(0)))
        else:
            segments.append(('Untitled', 'Go to the first line',
                             lambda: self.line_requested.emit(0)))
        for name, start, _end, _depth in scopes:
            segments.append((name, f'Go to line {start + 1}',
                             lambda row=start: self.line_requested.emit(row)))

        for index, (label, tooltip, callback) in enumerate(segments):
            if index:
                separator = QLabel('\u203a', self.body)
                separator.setProperty('breadcrumbSeparator', True)
                separator.setAlignment(Qt.AlignCenter)
                separator.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                self.row.addWidget(separator)
            self._tail = self._button(
                label, tooltip, callback, current=index == len(segments) - 1)
        self.row.addStretch(1)
        self.row.activate()
        self._reveal_timer.start(0)

    def _button(self, text, tooltip, callback, current=False):
        """Create a text-only target with an explicit keyboard-focus state."""
        button = QToolButton(self.body)
        button.setProperty('breadcrumbSegment', True)
        button.setProperty('breadcrumbCurrent', current)
        button.setText(str(text).replace('&', '&&'))
        button.setToolTip(tooltip)
        button.setAccessibleName(str(text))
        button.setAutoRaise(True)
        button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        button.setFocusPolicy(Qt.StrongFocus)
        button.setCursor(Qt.PointingHandCursor)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setFixedHeight(self.height() - 6)
        button.ensurePolished()
        button.setFixedWidth(button.sizeHint().width())
        button.clicked.connect(lambda checked=False: callback())
        button.installEventFilter(self)
        self.row.addWidget(button)
        return button

    def _reveal_tail(self):
        """Keep the most specific target visible after Qt updates geometry."""
        if self._tail is not None:
            self.ensureWidgetVisible(self._tail, 8, 0)

    def resizeEvent(self, event):
        """Reveal the active end again after the viewport becomes narrower."""
        super().resizeEvent(event)
        if hasattr(self, '_reveal_timer'):
            self._reveal_timer.start(0)

    def eventFilter(self, watched, event):
        """Reveal offscreen segments reached by keyboard navigation."""
        if event.type() == QEvent.FocusIn and isinstance(watched, QToolButton):
            self.ensureWidgetVisible(watched, 8, 0)
        return super().eventFilter(watched, event)

    def wheelEvent(self, event):
        """Map either wheel axis to horizontal scrolling without a tall scrollbar."""
        bar = self.horizontalScrollBar()
        if not bar.maximum():
            event.ignore()
            return
        pixels = event.pixelDelta()
        delta = pixels.x() or pixels.y()
        if not delta:
            angle = event.angleDelta()
            delta = round((angle.x() or angle.y()) / 120 * 60)
        bar.setValue(bar.value() - delta)
        event.accept()

    def set_path(self, path):
        """Keep the existing path-only API compatible with previous callers."""
        self.set_location(path)