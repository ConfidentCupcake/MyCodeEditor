# Topic 3 correction — compact breadcrumb styling

**For the already-installed Topic 3 in MyCodeEditor. Updated 4 November 2026.**

The original guide caused the visual problem: it did not style the scroll-area body/viewport or its toolbar, and the breadcrumb push buttons inherited the general button borders and padding. A maximum height of 65 also allowed an unnecessarily tall row. This correction gives the row an explicit dark background, text-only segments, chevron separators, subtle hover and a visible keyboard-focus outline.

The navigation API and existing scope parser stay compatible. Apply these **two edits**, then restart the editor. Do not add a second breadcrumb instance or repeat `init_ui()`.

## 1. Replace the breadcrumb module

**File:** `side_bar_widgets/breadcrumbs.py`  
**Operation:** replace the whole file.  
**OLD:** the previous Topic 3 module shown below. If your file has additional custom methods, preserve them separately before replacing it.

````python
"""Scrollable document paths and cached Python scope navigation."""
from pathlib import Path
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QScrollArea

class Breadcrumbs(QScrollArea):
    """Emit directory or source-line targets without retaining an editor."""
    directory_requested = pyqtSignal(str)
    line_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        """Attach the layout to an owned widget; scroll long paths horizontally."""
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.body = QWidget(self)
        self.row = QHBoxLayout(self.body)
        self.row.setContentsMargins(4, 2, 4, 2)
        self.row.setSpacing(2)
        self.setWidget(self.body)
        self.setMaximumHeight(65)
        self._key = None

    def set_location(self, path, scopes=()):
        """Rebuild only when the displayed path or enclosing chain changes."""
        key = (str(path or ''), tuple(scopes))
        if key == self._key:
            return
        self._key = key
        while self.row.count():
            item = self.row.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        if path:
            resolved = Path(path).expanduser().absolute()
            for part in reversed(resolved.parents):
                self._button(part.name or str(part), str(part),
                             lambda p=str(part): self.directory_requested.emit(p))
            self._button(resolved.name, str(resolved), lambda: self.line_requested.emit(0))
        else:
            self._button('Untitled', '', lambda: self.line_requested.emit(0))
        for name, start, end, depth in scopes:
            self._button(name, f'Line {start + 1}', lambda row=start: self.line_requested.emit(row))
        self.row.addStretch(1)

    def _button(self, text, tooltip, callback):
        """Bind an immutable navigation target to an accessible push button."""
        button = QPushButton(text, self.body)
        button.setFlat(True)
        button.setToolTip(tooltip)
        button.clicked.connect(lambda checked=False: callback())
        self.row.addWidget(button)

    def set_path(self, path):
        """Preserve the original public API for path-only callers."""
        self.set_location(path)
````

**NEW — complete replacement with comments and docstrings:**

````python
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
````

The local style uses the screenshot's dark palette and is independent of Topic 1. It styles the viewport and body as well as the outer scroll area. The toolbar gets its own matching background and a thin bottom divider. General button spacing from Topics 1 and 4 no longer controls breadcrumb spacing. The row is at least 34 logical pixels high and adapts to the inherited font size at construction; the toolbar adds a one-pixel divider. This is a dark-theme implementation, not automatic light/dark theme detection.

Long paths scroll with the mouse wheel or trackpad. Tab reveals offscreen segments, and Space activates them. Rebuilding hides old controls immediately before their deferred deletion. A parent-owned timer reveals the current file/scope after Qt has laid out the new row.

## 2. Replace the toolbar construction block

**File:** `main.py`  
**Class/method:** `MainWindow.__init__`, in the Topic 3 setup after `self.init_ui()`.  
**Operation:** replace these existing five lines; retain everything before and after them.

**OLD:**

````python
        self.breadcrumbs = Breadcrumbs(self)
        self.breadcrumb_bar = QToolBar('Breadcrumbs', self)
        self.breadcrumb_bar.setObjectName('BreadcrumbBar')
        self.breadcrumb_bar.addWidget(self.breadcrumbs)
        self.addToolBar(Qt.TopToolBarArea, self.breadcrumb_bar)
````

**NEW:**

````python
        self.breadcrumbs = Breadcrumbs(self)
        self.breadcrumb_bar = QToolBar('Breadcrumbs', self)
        self.breadcrumbs.configure_toolbar(self.breadcrumb_bar)
        self.breadcrumb_bar.addWidget(self.breadcrumbs)
        # Give the path its own row if another top toolbar already exists.
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, self.breadcrumb_bar)
````

Your existing `directory_requested` / `line_requested` connections, both timers, `_connect_editor` additions, `_refresh_breadcrumbs`, `_breadcrumb_changed`, `_jump_breadcrumb`, `_reveal_breadcrumb`, and `code_inteligence/breadcrumb_symbols.py` remain installed exactly once. No new imports in `main.py` are needed: `Qt`, `QToolBar`, and `Breadcrumbs` were already used by this block. `configure_toolbar` comes from the replacement class above.

## 3. Verification

Start the editor with `python main.py` after saving both edits.

- Open a file: expect a compact, dark breadcrumb row and chevrons between text segments; there should be no pale scroll-area rectangle or permanently boxed buttons.
- Hover a segment: expect a subtle fill. Tab to a segment: expect a blue focus outline. Press Space: directory segments reveal the directory; file/scope segments move to the expected source line.
- Narrow the window or open a deep path: wheel/trackpad movement reveals the full path, and Tab brings offscreen targets into view.
- Switch tabs or move between Python scopes: old segments should disappear immediately without overlapping the new ones.

A one-off offscreen PyQt5 component check passed with the repository stylesheet plus Topic 1's stylesheet and a 13-point font. It checked compact geometry, signal targets, keyboard activation, overflow at a 280-pixel window width, focus reveal, Untitled, and repeated rebuilds. The rendered result was visually inspected. Your modified Windows application was not run.

The duplicated menu groups and partially covered `set_path` control in the screenshot need separate investigation if they remain. The screenshot does not establish their cause. Inspect your current `MainWindow.__init__`, `init_ui`, and `set_up_menu` call sites and additional breadcrumb/demo widgets; this styling correction does not change menu construction.

## Documentation

- [Qt 5.15 QScrollArea: child sizing and scrolling](https://doc.qt.io/archives/qt-5.15/qscrollarea.html)
- [Qt 5.15 stylesheet selectors and cascading](https://doc.qt.io/archives/qt-5.15/stylesheet-syntax.html)
- [Qt 5.15 QToolBar: embedded widgets and toolbar properties](https://doc.qt.io/archives/qt-5.15/qtoolbar.html)
- [Qt 5.15 QTimer: owned single-shot callbacks](https://doc.qt.io/archives/qt-5.15/qtimer.html)
