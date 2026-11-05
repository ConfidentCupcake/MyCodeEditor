# MyCodeEditor — complete topic-by-topic implementation guide

**Repository:** [ConfidentCupcake/MyCodeEditor](https://github.com/ConfidentCupcake/MyCodeEditor)  
**Pinned baseline:** [`211ac365134416c9cadee7e68e742ca32c48191b`](https://github.com/ConfidentCupcake/MyCodeEditor/tree/211ac365134416c9cadee7e68e742ca32c48191b) (`main`, commit “v1.0.1”, inspected 29 October 2026)  
**Launch:** `python main.py` from the activated editor environment in PyCharm.

This revision covers the original **30 features**, including a fresh review of topics **1–3**. Every chapter finishes its own implementation before the next topic starts:

**Topic → explanation and documentation → complete commented code and docstrings → exact file/method integration with OLD → NEW.**

There is no final combined integration chapter and no `EditorFeatureController` to paste afterward. New methods are installed directly into the existing classes at the shown boundaries. No automated test files or test-running checklist are part of this guide. Topic 16 is the requested test-runner *feature* in the editor.

## What the current repository actually contains

The files for topics 1–3 exist, but their imports and UI connections are absent from `main.py` at this revision. They therefore need both corrections and integration. In particular:

| Topic | Observed problem | Correction here |
|---|---|---|
| 1 | `QMenu QToolTip` is a descendant selector; `QTabBar::tab::selected` is incorrect; foreground differs from the intended palette | Correct selectors/colors, retain the module API and connect one generated stylesheet |
| 2 | `QIcon.on` does not exist; sidebar code still uses PNG QLabel updates | Correct `QIcon.On`, use SVG-backed keyboard-accessible buttons and update every dispatcher path |
| 3 | `QHBoxLayout()` is not attached to a widget; the module is unused | Owned scrollable layout, actual toolbar connections, cached Python scope navigation |

The other attached guides were used for structure and for the fuller behavior of these 30 topics. The separate 11-topic course and diagnostics/type/spelling guides describe additional systems; they are **not assumed installed** in this baseline. In particular, this guide does not call a nonexistent Problems/References panel or a nonexistent shared-document manager. Their lifecycle and integration lessons are reflected where applicable.

## How to apply one chapter

1. Use a working copy of the pinned revision. Preserve your uncommitted work before editing. A different commit can have different OLD blocks.
2. Apply only the prerequisites listed in that topic, then its complete file and integration steps. All paths are repository-relative. Preserve the actual spelling `code_inteligence`.
3. **OLD → NEW replaces only the displayed block in the named scope.** Keep the rest of that method and file. For a new file, there is no old code to delete.
4. New code is presented first for reading. The implementation section tells you where to paste it. Paste each definition **once**; repeated code in an OLD/NEW explanation is not a second installation.
5. Imports, initialization and menu additions often share anchors. Retain additions from earlier topics. When an OLD anchor line is still present, add the current topic beside it; do not replace the whole method with a baseline copy.
6. Some chapters show an explicit variant for an earlier installed topic. Use the variant matching your code. For shared modules, keep one identical copy. For the shared outline routing edit, apply it only once.
7. Save the files for the current chapter and start the editor. “Using this topic” identifies its real entry point; no additional chapters are required beyond the declared prerequisites.

Do not install the older combined controller alongside this guide. No existing source file needs deleting; obsolete statements and methods are replaced explicitly below. The generated native `.c`/extension output in Topic 25 is rebuilt from source.

## Independence and order

| Topic | Required prerequisite | Why |
|---|---|---|
| 4 | 1 | Uses the base stylesheet and `theme_qss` |
| 11 | 13 | History review uses the comparison dialog |
| 12 | 13 | External-conflict review uses the comparison dialog |
| 14 | 13 | Semantic rename preview uses the comparison dialog |
| 21 | 20 | Uses the renderer-aligned Markdown document model |
| 29 | 28 | Adds caching to the real shared analysis queue |

All other topics apply directly to the baseline. Topics 16 and 17 each include the same `process_runner.py`; install that shared file once. Neither requires the other feature.

**Complete implementation order: 1–10 → 13 → 11 → 12 → 14–30.** Chapters follow this order and retain their original topic numbers.

## Validation boundary

The exact integration anchors were checked against the fetched baseline, each topic with its declared prerequisites, and the combined source. The resulting Python was parsed and checked for undefined names. No automated test suite or interactive Windows/PyCharm GUI test was run for this revision. These are concrete implementations, not a claim of complete runtime certification. Relevant limits—such as recovery snapshot size, subprocess descendants and rename scope—are stated in the affected chapter.

## Contents

- [Topic 01: Unified design system](#topic-01)
- [Topic 02: Consistent SVG icons](#topic-02)
- [Topic 03: Breadcrumb navigation](#topic-03)
- [Topic 04: Compact and comfortable layouts](#topic-04)
- [Topic 05: Improved status bar](#topic-05)
- [Topic 06: Polished empty states](#topic-06)
- [Topic 07: Welcome screen](#topic-07)
- [Topic 08: Focus mode](#topic-08)
- [Topic 09: Workspace layout presets](#topic-09)
- [Topic 10: Automatic recovery](#topic-10)
- [Topic 13: Compare/diff editor](#topic-13)
- [Topic 11: Local file history](#topic-11)
- [Topic 12: External-change comparison](#topic-12)
- [Topic 14: Rename symbol with preview](#topic-14)
- [Topic 15: Workspace symbol search](#topic-15)
- [Topic 16: Test runner panel](#topic-16)
- [Topic 17: Run configurations](#topic-17)
- [Topic 18: Configurable keyboard shortcuts](#topic-18)
- [Topic 19: Smarter pair handling](#topic-19)
- [Topic 20: Outline and navigation](#topic-20)
- [Topic 21: Authoring tools](#topic-21)
- [Topic 22: Performance diagnostics mode](#topic-22)
- [Topic 23: Lazy initialization](#topic-23)
- [Topic 24: Background file hashing](#topic-24)
- [Topic 25: Incremental syntax highlighting](#topic-25)
- [Topic 26: Smarter Markdown preview updates](#topic-26)
- [Topic 27: Large-file mode](#topic-27)
- [Topic 28: Shared analysis scheduling](#topic-28)
- [Topic 29: Bounded result caching](#topic-29)
- [Topic 30: Pause hidden-panel work](#topic-30)

---

<a id="topic-01"></a>

## Topic 01: Unified design system

### 1. Topic explanation

A semantic widget palette and explicit hover, focus, disabled and selected states make menus, tabs and buttons consistent. The existing lexer theme continues to own document colors. Fix the current missing selector comma, incorrect selected-tab selector and unintended foreground value; preserve the existing design_settings.py public API.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt stylesheet reference](https://doc.qt.io/archives/qt-5.15/stylesheet-reference.html)

### 2. Topic code

#### `code_settings/design_settings.py` — updated existing module

Read the complete target implementation below. The implementation section shows the exact existing-code edits; do not paste this as a second class or a second module.

````python
"""Shared interface colors; document syntax colors remain lexer-owned."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DesignTokens:
    """Immutable semantic widget colors, independent of syntax-token themes."""
    paper: str = '#1e1f22'
    surface: str = '#262a33'
    foreground: str = '#dcdfe4'
    muted: str = '#969ba7'
    accent: str = '#61afef'
    border: str = '#3d424d'

def theme_qss(density='comfortable', tokens=None):
    """Generate fresh QSS; callers append it to the original base exactly once."""
    if density not in {'compact', 'comfortable'}:
        raise ValueError(f'Unsupported density: {density}')
    t = tokens or DesignTokens()
    pad = 3 if density == 'compact' else 7
    # Scope panel backgrounds so Scintilla and terminal surfaces keep their themes.
    return f"""
    QWidget[designPanel="true"] {{ background: {t.surface}; color: {t.foreground}; }}
    QMenu, QToolTip {{ background: {t.surface}; color: {t.foreground}; border: 1px solid {t.border}; }}
    QMenu::item:selected {{ background: {t.border}; }}
    QDockWidget::title {{ background: {t.surface}; color: {t.foreground}; padding: {pad}px; }}
    QPushButton {{ background: {t.surface}; color: {t.foreground}; border: 1px solid {t.border}; border-radius: 4px; padding: {pad}px; }}
    QToolButton {{ background: transparent; color: {t.foreground}; border: 1px solid transparent; border-radius: 4px; padding: {pad}px; }}
    QPushButton:hover, QPushButton:focus, QToolButton:hover, QToolButton:focus {{ border-color: {t.accent}; }}
    QToolButton:checked {{ background: {t.border}; }}
    QPushButton:disabled, QToolButton:disabled {{ color: {t.muted}; }}
    QTabBar::tab {{ background: {t.surface}; color: {t.foreground}; padding: {pad}px 12px; }}
    QTabBar::tab:selected {{ border-bottom: 2px solid {t.accent}; }}
    """
````

| Definition | Responsibility |
|---|---|
| `DesignTokens` | Immutable semantic widget colors, independent of syntax-token themes. |
| `theme_qss` | Generate fresh QSS; callers append it to the original base exactly once. |

### 3. Topic implementation — exact files and methods

#### Step 01.1: `code_settings/design_settings.py` — `module`

Replace only the following contiguous block. The context is from the pinned repository; keep all surrounding definitions.

**OLD**

````python
"""Shared Qt widget design tokens. Existing module: replace its contents."""
from __future__ import annotations
from dataclasses import dataclass 

@dataclass(frozen=True)
class DesignTokens:
    paper: str = '#1e1f22'
    surface: str = '#262a33'
    foreground: str = '#dcdf34'
    muted: str = '#969ba7'
    accent: str = '#61afef'
    border: str = '#3d424d'
    
def theme_qss(density: str = 'comfortable', tokens: DesignTokens | None = None) -> str:
    """Return deterministic widget styles; never append to themselves."""
    if density not in {'compact', 'comfortable'}:
        raise ValueError(f"Unsupported denisty: {density}")
    t = tokens or DesignTokens()
    padding = 3 if density == 'compact' else 7
    return f"""
    QMenu QToolTip {{ background: {t.surface}; color: {t.foreground}; border: 1px solid {t.border}; }}
    QDockWidget::title {{ background: {t.surface}; color: {t.foreground}; padding: {padding}px; }}
    QPushButton, QToolButton {{ color: {t.foreground}; border: 1px solid {t.border}; padding: {padding}px; }}
    QPushButton:hover, QToolButton:hover {{ border-color: {t.accent}; }}
    QTabBar::tab {{ background: {t.surface}; color: {t.foreground}; padding: {padding}px 12px; }}
    QTabBar::tab::selected {{ border-bottom: 2px solid {t.accent}; }}
    """
````

**NEW**

````python
"""Shared interface colors; document syntax colors remain lexer-owned."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DesignTokens:
    """Immutable semantic widget colors, independent of syntax-token themes."""
    paper: str = '#1e1f22'
    surface: str = '#262a33'
    foreground: str = '#dcdfe4'
    muted: str = '#969ba7'
    accent: str = '#61afef'
    border: str = '#3d424d'

def theme_qss(density='comfortable', tokens=None):
    """Generate fresh QSS; callers append it to the original base exactly once."""
    if density not in {'compact', 'comfortable'}:
        raise ValueError(f'Unsupported density: {density}')
    t = tokens or DesignTokens()
    pad = 3 if density == 'compact' else 7
    # Scope panel backgrounds so Scintilla and terminal surfaces keep their themes.
    return f"""
    QWidget[designPanel="true"] {{ background: {t.surface}; color: {t.foreground}; }}
    QMenu, QToolTip {{ background: {t.surface}; color: {t.foreground}; border: 1px solid {t.border}; }}
    QMenu::item:selected {{ background: {t.border}; }}
    QDockWidget::title {{ background: {t.surface}; color: {t.foreground}; padding: {pad}px; }}
    QPushButton {{ background: {t.surface}; color: {t.foreground}; border: 1px solid {t.border}; border-radius: 4px; padding: {pad}px; }}
    QToolButton {{ background: transparent; color: {t.foreground}; border: 1px solid transparent; border-radius: 4px; padding: {pad}px; }}
    QPushButton:hover, QPushButton:focus, QToolButton:hover, QToolButton:focus {{ border-color: {t.accent}; }}
    QToolButton:checked {{ background: {t.border}; }}
    QPushButton:disabled, QToolButton:disabled {{ color: {t.muted}; }}
    QTabBar::tab {{ background: {t.surface}; color: {t.foreground}; padding: {pad}px 12px; }}
    QTabBar::tab:selected {{ border-bottom: 2px solid {t.accent}; }}
    """
````

#### Step 01.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_settings.design_settings import theme_qss
````

#### Step 01.3: `main.py` — MainWindow.init_ui: after the complete stylesheet try/except

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self._outline_debounce = QTimer(self)
````

**NEW**

````python
        self._base_qss = self.styleSheet()
        self.setStyleSheet(self._base_qss + "\n" + theme_qss())

        self._outline_debounce = QTimer(self)
````

**Using this topic:** Start the editor normally. Menus, tabs and buttons now use the shared palette; syntax colors still come from the current lexer theme.


---

<a id="topic-02"></a>

## Topic 02: Consistent SVG icons

### 1. Topic explanation

Use bundled SVGs at the actual display scale, fix QIcon.on, and replace mouse-only labels with keyboard-accessible QToolButtons. All sidebar visibility changes use one state updater, including the dispatcher that previously bypassed the icon provider.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QIcon](https://doc.qt.io/archives/qt-5.15/qicon.html)
- [Qt 5.15 QToolButton](https://doc.qt.io/archives/qt-5.15/qtoolbutton.html)

### 2. Topic code

#### `markdowneditor_assets/icon_provider.py` — updated existing module

Read the complete target implementation below. The implementation section shows the exact existing-code edits; do not paste this as a second class or a second module.

````python
"""State-aware SVG icons from the existing application asset package."""
from functools import lru_cache
from pathlib import Path
from PyQt5.QtGui import QIcon
from markdowneditor_assets import asset_path

ALLOWED = frozenset({'folder', 'search', 'outline', 'terminal', 'console', 'settings'})

@lru_cache(maxsize=6)
def themed_icon(name: str) -> QIcon:
    """Load each validated SVG once, after QApplication has been created."""
    if name not in ALLOWED:
        raise ValueError(f'Unknown icon: {name}')
    normal = Path(asset_path(f'icons/{name}.svg'))
    if not normal.is_file():
        raise FileNotFoundError(normal)
    icon = QIcon(str(normal))
    selected = Path(asset_path(f'icons/{name}-active.svg'))
    if selected.is_file():
        icon.addFile(str(selected), mode=QIcon.Normal, state=QIcon.On)
        icon.addFile(str(selected), mode=QIcon.Active, state=QIcon.On)
    return icon
````

| Definition | Responsibility |
|---|---|
| `themed_icon` | Load each validated SVG once, after QApplication has been created. |

### 3. Topic implementation — exact files and methods

#### Step 02.1: `markdowneditor_assets/icon_provider.py` — `module`

Replace only the following contiguous block. The context is from the pinned repository; keep all surrounding definitions.

**OLD**

````python
# Validated icon access for existing bundled SVG assets.

from pathlib import Path
from PyQt5.QtGui import QIcon
from markdowneditor_assets import asset_path

ALLOWED = frozenset({'folder', 'search', 'outline', 'terminal', 'console', 'settings'})

def themed_icon(name: str) -> QIcon:
    """Return an icon with normal and checked SVG images."""
    if name not in ALLOWED:
        raise ValueError(f'Unknown icon: {name}')
    normal = Path(asset_path(f'icons/{name}.svg'))
    if not normal.is_file():
        raise FileNotFoundError(normal)
    icon = QIcon(str(normal))
    selected = Path(asset_path(f'icons/{name}-active.svg'))
    if selected.is_file():
        icon.addFile(str(selected), mode=QIcon.Normal, state=QIcon.on)
    return icon
````

**NEW**

````python
"""State-aware SVG icons from the existing application asset package."""
from functools import lru_cache
from pathlib import Path
from PyQt5.QtGui import QIcon
from markdowneditor_assets import asset_path

ALLOWED = frozenset({'folder', 'search', 'outline', 'terminal', 'console', 'settings'})

@lru_cache(maxsize=6)
def themed_icon(name: str) -> QIcon:
    """Load each validated SVG once, after QApplication has been created."""
    if name not in ALLOWED:
        raise ValueError(f'Unknown icon: {name}')
    normal = Path(asset_path(f'icons/{name}.svg'))
    if not normal.is_file():
        raise FileNotFoundError(normal)
    icon = QIcon(str(normal))
    selected = Path(asset_path(f'icons/{name}-active.svg'))
    if selected.is_file():
        icon.addFile(str(selected), mode=QIcon.Normal, state=QIcon.On)
        icon.addFile(str(selected), mode=QIcon.Active, state=QIcon.On)
    return icon
````

#### Step 02.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from markdowneditor_assets.icon_provider import themed_icon
````

#### Step 02.3: `main.py` — MainWindow.get_sidebar_label

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def get_sidebar_label(self, path, name):
        """Create a named clickable sidebar icon using the shared dispatcher."""
        label = QLabel(self)
        label.setPixmap(QPixmap(path).scaled(QSize(25, 25)))
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setFont(self.window_font)
        label.setToolTip(name.title())
        label.setCursor(Qt.PointingHandCursor)
        label.mousePressEvent = lambda e: self.show_hide_tab(e, name)
        return label
````

**NEW**

````python
    def get_sidebar_label(self, path, name):
        """Keep the existing factory API while providing real keyboard activation."""
        button = QToolButton(self)
        button.setIcon(themed_icon(name))
        button.setIconSize(QSize(25, 25))
        button.setCheckable(True)
        button.setChecked('-active' in str(path))
        button.setFocusPolicy(Qt.StrongFocus)
        button.setToolTip(name.title())
        button.setAccessibleName(name.title())
        button.clicked.connect(lambda checked=False, tool=name: self.show_hide_tab(None, tool))
        return button
````

#### Step 02.4: `main.py` — MainWindow._set_sidebar_icon

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _set_sidebar_icon(self, name: str, active: bool):
        """Reflect a tool's actual visibility using the existing icon variants."""
        label = self.sidebar_labels.get(name)
        if label is not None:
            suffix = "-active" if active else ""
            label.setPixmap(QPixmap(resource_path(f"icons/{name}{suffix}.png")).scaled(QSize(25,25)))
````

**NEW**

````python
    def _set_sidebar_icon(self, name: str, active: bool):
        """Synchronize checked state with the tool's actual visibility."""
        button = self.sidebar_labels.get(name)
        if button is not None:
            button.setChecked(bool(active))
````

#### Step 02.5: `main.py` — MainWindow.show_hide_tab

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def show_hide_tab(self, e, type_):
        """Dispatch left-clicks to tool actions or the three sidebar pages."""
        if e.button() != Qt.LeftButton:
            return
        
        # Return before changing page icons: opening a dock is independen of 
        # the currently selected Folder/Search/Outline page.
        if type_ in ("terminal", "console"):
            dock = self.terminal_dock if type_ == "terminal" else self.console_dock
            dock.show()
            dock.raise_()
            if type_ == "terminal":
                self.terminal.output.setFocus()
            return
        if type_ == "settings":
            self._set_sidebar_icon("settings", True)
            try:
                self.open_settings()
            finally:
                self._set_sidebar_icon("settings", False)
            return
            
            
        panels = {
            "folder": self.file_manager_frame,
            "search": self.search_frame,
            "outline": self.outline_frame,
        }
        # Update icon states. Reset all to gray, then set active to blue
        icon_map = {
            "folder": (resource_path("icons/folder.png"), resource_path(
                "icons/folder-active.png")),
            "search": (resource_path("icons/search.png"), resource_path(
                "icons/search-active.png")),
            "outline": (
                resource_path("icons/outline.png"),
                resource_path("icons/outline-active.png")),
        }
        # Reset all sidebar icons to inactive gray
        for name, (inactive, active) in icon_map.items():
            label = self.sidebar_labels.get(name)
            if label:
                label.setPixmap(QPixmap(inactive).scaled(QSize(25, 25)))

        target = panels.get(type_)
        if target is None:
            return

        # If the target panel is already showing, hide the side panel
        if self.side_panel.isVisible() and self.side_panel.currentWidget() is target:
            # Clicking the active panel hiddes is, resets to gray
            self.side_panel.hide()
            return

        # Otherwise, switch to the target panel and show it
        self.side_panel.setCurrentWidget(target)
        self.side_panel.show()

        label = self.sidebar_labels.get(type_)
        if label:
            label.setPixmap(QPixmap(icon_map[type_][1]).scaled(QSize(25, 25)))
        # Restore splitter sizes if the side panel was hidden (width 0)
        sizes = self.hs_split.sizes()
        if sizes and sizes[0] == 0:
            self.hs_split.setSizes([300, 550, 550])
````

**NEW**

````python
    def show_hide_tab(self, e, type_):
        """Dispatch left-clicks to tool actions or the three sidebar pages."""
        if e is not None and e.button() != Qt.LeftButton:
            return
        
        # Return before changing page icons: opening a dock is independen of 
        # the currently selected Folder/Search/Outline page.
        if type_ in ("terminal", "console"):
            dock = self.terminal_dock if type_ == "terminal" else self.console_dock
            dock.show()
            dock.raise_()
            if type_ == "terminal":
                self.terminal.output.setFocus()
            return
        if type_ == "settings":
            self._set_sidebar_icon("settings", True)
            try:
                self.open_settings()
            finally:
                self._set_sidebar_icon("settings", False)
            return
            
            
        panels = {
            "folder": self.file_manager_frame,
            "search": self.search_frame,
            "outline": self.outline_frame,
        }
        for name in panels:
            self._set_sidebar_icon(name, False)

        target = panels.get(type_)
        if target is None:
            return

        # If the target panel is already showing, hide the side panel
        if self.side_panel.isVisible() and self.side_panel.currentWidget() is target:
            # Clicking the active panel hiddes is, resets to gray
            self.side_panel.hide()
            return

        # Otherwise, switch to the target panel and show it
        self.side_panel.setCurrentWidget(target)
        self.side_panel.show()

        self._set_sidebar_icon(type_, True)
        # Restore splitter sizes if the side panel was hidden (width 0)
        sizes = self.hs_split.sizes()
        if sizes and sizes[0] == 0:
            self.hs_split.setSizes([300, 550, 550])
````

**Using this topic:** Activate sidebar tools with mouse, Tab and Space. The checked icon follows the tool, including dock close buttons.


---

<a id="topic-03"></a>

## Topic 03: Breadcrumb navigation

### 1. Topic explanation

Show clickable directory segments and the active Python class/function chain. Fix the unattached layout. Parsing is debounced after edits, cached until text changes, and skipped for large files; moving the caret uses cached ranges. Directory navigation does not silently change the workspace or restart Ruff.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Python AST source locations](https://docs.python.org/3/library/ast.html)
- [Qt 5.15 QScrollArea](https://doc.qt.io/archives/qt-5.15/qscrollarea.html)
- [Qt 5.15 QTimer](https://doc.qt.io/archives/qt-5.15/qtimer.html)

### 2. Topic code

#### `code_inteligence/breadcrumb_symbols.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Pure Python scope ranges for a cached breadcrumb model."""
import ast

def scope_ranges(source):
    """Return (name, start, end, depth) without importing or executing source."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError):
        return ()
    result = []
    def visit(node, depth):
        """Traverse conditional bodies too, retaining actual lexical nesting."""
        scope = isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        if scope:
            result.append((node.name, node.lineno - 1, node.end_lineno - 1, depth))
        for child in ast.iter_child_nodes(node):
            visit(child, depth + int(scope))
    visit(tree, 0)
    return tuple(result)
````

| Definition | Responsibility |
|---|---|
| `scope_ranges` | Return (name, start, end, depth) without importing or executing source. |

#### `side_bar_widgets/breadcrumbs.py` — updated existing module

Read the complete target implementation below. The implementation section shows the exact existing-code edits; do not paste this as a second class or a second module.

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

| Definition | Responsibility |
|---|---|
| `Breadcrumbs` | Emit directory or source-line targets without retaining an editor. |
| `Breadcrumbs.__init__` | Attach the layout to an owned widget; scroll long paths horizontally. |
| `Breadcrumbs.set_location` | Rebuild only when the displayed path or enclosing chain changes. |
| `Breadcrumbs._button` | Bind an immutable navigation target to an accessible push button. |
| `Breadcrumbs.set_path` | Preserve the original public API for path-only callers. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _breadcrumb_changed(self, editor):
        """Invalidate parsed scopes immediately; coalesce reparsing after typing."""
        editor._breadcrumb_scopes = None
        if editor is self.current_editor():
            self._breadcrumb_timer.start()

    def _refresh_breadcrumbs(self):
        """Use cached scope ranges on cursor moves; never parse every caret step."""
        if not hasattr(self, 'breadcrumbs'):
            return
        editor = self.current_editor()
        if editor is None:
            self.breadcrumbs.hide()
            return
        self.breadcrumbs.show()
        scopes = getattr(editor, '_breadcrumb_scopes', None)
        if scopes is None and not self._breadcrumb_timer.isActive():
            scopes = scope_ranges(editor.text()) if isinstance(editor, PythonEditor) and editor.length() < 2_000_000 else ()
            editor._breadcrumb_scopes = scopes
        row = editor.getCursorPosition()[0]
        chain = sorted((s for s in (scopes or ()) if s[1] <= row <= s[2]), key=lambda s: s[3])
        self.breadcrumbs.set_location(getattr(editor, 'path', None), chain)

    def _jump_breadcrumb(self, line):
        """Navigate the current document without retaining stale tab references."""
        editor = self.current_editor()
        if editor is not None:
            editor.setCursorPosition(min(line, editor.lines() - 1), 0)
            editor.ensureLineVisible(line)
            editor.setFocus()

    def _reveal_breadcrumb(self, directory):
        """Reveal a directory without replacing the project's analysis root."""
        index = self.file_manager.model.index(directory)
        if index.isValid():
            self.side_panel.setCurrentWidget(self.file_manager_frame)
            self.side_panel.show()
            self.file_manager.setRootIndex(self.file_manager.model.index(str(Path(directory).parent)))
            self.file_manager.setCurrentIndex(index)
            self.file_manager.scrollTo(index)
````

| Definition | Responsibility |
|---|---|
| `_breadcrumb_changed` | Invalidate parsed scopes immediately; coalesce reparsing after typing. |
| `_refresh_breadcrumbs` | Use cached scope ranges on cursor moves; never parse every caret step. |
| `_jump_breadcrumb` | Navigate the current document without retaining stale tab references. |
| `_reveal_breadcrumb` | Reveal a directory without replacing the project's analysis root. |

### 3. Topic implementation — exact files and methods

#### Step 03.1: create `code_inteligence/breadcrumb_symbols.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 03.2: `side_bar_widgets/breadcrumbs.py` — `module`

Replace only the following contiguous block. The context is from the pinned repository; keep all surrounding definitions.

**OLD**

````python
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
````

**NEW**

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

#### Step 03.3: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.breadcrumbs import Breadcrumbs
from code_inteligence.breadcrumb_symbols import scope_ranges
````

#### Step 03.4: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.breadcrumbs = Breadcrumbs(self)
        self.breadcrumb_bar = QToolBar('Breadcrumbs', self)
        self.breadcrumb_bar.setObjectName('BreadcrumbBar')
        self.breadcrumb_bar.addWidget(self.breadcrumbs)
        self.addToolBar(Qt.TopToolBarArea, self.breadcrumb_bar)
        self.breadcrumbs.directory_requested.connect(self._reveal_breadcrumb)
        self.breadcrumbs.line_requested.connect(self._jump_breadcrumb)
        self._breadcrumb_timer = QTimer(self)
        self._breadcrumb_timer.setSingleShot(True)
        self._breadcrumb_timer.setInterval(350)
        self._breadcrumb_timer.timeout.connect(self._refresh_breadcrumbs)
        self.tab_view.currentEditorChanged.connect(lambda *args: self._refresh_breadcrumbs())
        # Also catches Save As / rename without rewriting their save lifecycle.
        self._breadcrumb_path_timer = QTimer(self)
        self._breadcrumb_path_timer.timeout.connect(self._refresh_breadcrumbs)
        self._breadcrumb_path_timer.start(500)
````

#### Step 03.5: `main.py` — MainWindow._connect_editor: connect per-document breadcrumb invalidation

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        editor.textChanged.connect(self._outline_debounce.start)
````

**NEW**

````python
        editor.textChanged.connect(self._outline_debounce.start)
        editor.textChanged.connect(lambda ed=editor: self._breadcrumb_changed(ed))
        editor.cursorPositionChanged.connect(lambda *args: self._refresh_breadcrumbs())
````

#### Step 03.6: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _breadcrumb_changed(self, editor):
        """Invalidate parsed scopes immediately; coalesce reparsing after typing."""
        editor._breadcrumb_scopes = None
        if editor is self.current_editor():
            self._breadcrumb_timer.start()

    def _refresh_breadcrumbs(self):
        """Use cached scope ranges on cursor moves; never parse every caret step."""
        if not hasattr(self, 'breadcrumbs'):
            return
        editor = self.current_editor()
        if editor is None:
            self.breadcrumbs.hide()
            return
        self.breadcrumbs.show()
        scopes = getattr(editor, '_breadcrumb_scopes', None)
        if scopes is None and not self._breadcrumb_timer.isActive():
            scopes = scope_ranges(editor.text()) if isinstance(editor, PythonEditor) and editor.length() < 2_000_000 else ()
            editor._breadcrumb_scopes = scopes
        row = editor.getCursorPosition()[0]
        chain = sorted((s for s in (scopes or ()) if s[1] <= row <= s[2]), key=lambda s: s[3])
        self.breadcrumbs.set_location(getattr(editor, 'path', None), chain)

    def _jump_breadcrumb(self, line):
        """Navigate the current document without retaining stale tab references."""
        editor = self.current_editor()
        if editor is not None:
            editor.setCursorPosition(min(line, editor.lines() - 1), 0)
            editor.ensureLineVisible(line)
            editor.setFocus()

    def _reveal_breadcrumb(self, directory):
        """Reveal a directory without replacing the project's analysis root."""
        index = self.file_manager.model.index(directory)
        if index.isValid():
            self.side_panel.setCurrentWidget(self.file_manager_frame)
            self.side_panel.show()
            self.file_manager.setRootIndex(self.file_manager.model.index(str(Path(directory).parent)))
            self.file_manager.setCurrentIndex(index)
            self.file_manager.scrollTo(index)

    def current_editor(self):
````

**Using this topic:** Open a Python document, move inside a class or method and use the breadcrumb buttons to navigate. Directory buttons reveal the directory without restarting project analysis.


---

<a id="topic-04"></a>

## Topic 04: Compact and comfortable layouts

### 1. Topic explanation

Switch between compact and comfortable spacing, persist the choice, and rebuild styles from the base captured by Topic 1. Sidebar icon geometry changes too; the same code supports the baseline labels and Topic 2 buttons.

**Prerequisites:** Topic 01

**Documentation used:**

- [Qt 5.15 QSettings](https://doc.qt.io/archives/qt-5.15/qsettings.html)
- [Qt stylesheet reference](https://doc.qt.io/archives/qt-5.15/stylesheet-reference.html)

### 2. Topic code

This topic adds or changes methods in existing classes. Their complete code is included in the OLD → NEW steps below; there is no standalone helper file or later bootstrap to install.

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _apply_density(self, value):
        """Apply only supported density values and persist the selection."""
        value = value if value in ('compact', 'comfortable') else 'comfortable'
        self.setStyleSheet(self._base_qss + '\n' + theme_qss(value))
        for widget in self.sidebar_labels.values():
            widget.setFixedSize(38 if value == 'compact' else 48, 38 if value == 'compact' else 48)
        self.settings.setValue('layout_density', value)
````

| Definition | Responsibility |
|---|---|
| `_apply_density` | Apply only supported density values and persist the selection. |

### 3. Topic implementation — exact files and methods

#### Step 04.1: `main.py` — MainWindow.__init__, immediately after init_ui

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self._apply_density(self.settings.value('layout_density', 'comfortable', type=str))
````

#### Step 04.2: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        density_menu = menu_bar.addMenu('Layout Density')
        for density in ('compact', 'comfortable'):
            density_menu.addAction(density.title()).triggered.connect(
                lambda checked=False, value=density: self._apply_density(value))
````

#### Step 04.3: `main.py` — MainWindow: add methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _apply_density(self, value):
        """Apply only supported density values and persist the selection."""
        value = value if value in ('compact', 'comfortable') else 'comfortable'
        self.setStyleSheet(self._base_qss + '\n' + theme_qss(value))
        for widget in self.sidebar_labels.values():
            widget.setFixedSize(38 if value == 'compact' else 48, 38 if value == 'compact' else 48)
        self.settings.setValue('layout_density', value)

    def current_editor(self):
````

**Using this topic:** Use Layout Density → Compact or Comfortable. The choice survives restart.


---

<a id="topic-05"></a>

## Topic 05: Improved status bar

### 1. Topic explanation

Add clickable encoding/BOM, EOL, indentation and interpreter controls beside the existing cursor and Git labels. Show selection length, dirty state and Python run activity. Serialization-only BOM changes mark the buffer modified so close/save prompts remain correct.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QStatusBar](https://doc.qt.io/archives/qt-5.15/qstatusbar.html)
- [QScintilla editor API](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)

### 2. Topic code

#### `side_bar_widgets/status_item.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
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
        # A clickable QLabel otherwise cannot be reached with the keyboard.
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        """Invoke the setting on a left click only."""
        if event.button() == Qt.LeftButton:
            self.action()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """Let keyboard users activate the same control."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.action()
            event.accept()
            return
        super().keyPressEvent(event)
````

| Definition | Responsibility |
|---|---|
| `StatusItem` | A keyboard accessible, clickable status-bar item. |
| `StatusItem.__init__` | Bind a status value to its corresponding setting or chooser. |
| `StatusItem.mousePressEvent` | Invoke the setting on a left click only. |
| `StatusItem.keyPressEvent` | Let keyboard users activate the same control. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _refresh_document_status(self):
        """Read only metadata and the selection, not the entire document."""
        editor = self.current_editor()
        for widget in (self.encoding_status, self.eol_status, self.indent_status):
            widget.setEnabled(editor is not None and not editor.isReadOnly())
        interpreter = str(self.python_runner.interpreter)
        self.interpreter_status.setText(Path(interpreter).name)
        self.interpreter_status.setToolTip(interpreter)
        if editor is None:
            self.document_status.setText('No document')
            return
        self.encoding_status.setText('UTF-8 BOM' if getattr(editor, '_utf8_bom', False) else 'UTF-8')
        self.eol_status.setText({editor.EolWindows: 'CRLF', editor.EolUnix: 'LF', editor.EolMac: 'CR'}[editor.eolMode()])
        self.indent_status.setText(f"{'Tabs' if editor.indentationsUseTabs() else 'Spaces'}: {editor.tabWidth()}")
        selected = len(editor.selectedText()) if editor.hasSelectedText() else 0
        activity = 'Running Python' if self.python_runner.is_running() else 'Idle'
        self.document_status.setText(f"Selected {selected} | {'Modified' if editor.isModified() else 'Saved'} | {activity}")

    def _choose_document_encoding(self):
        """Change the UTF-8 serialization flag and participate in dirty tracking."""
        editor = self.current_editor()
        if editor is None or editor.isReadOnly():
            return
        values = ['UTF-8', 'UTF-8 BOM']
        value, ok = QInputDialog.getItem(self, 'Encoding', 'Save as:', values, int(getattr(editor, '_utf8_bom', False)), False)
        if ok and (value == values[1]) != getattr(editor, '_utf8_bom', False):
            editor._utf8_bom = value == values[1]
            editor.setModified(True)
            self._on_editor_text_changed(editor)
        self._refresh_document_status()

    def _choose_document_eol(self):
        """Convert line endings in one undo group and set the insertion mode."""
        editor = self.current_editor()
        if editor is None or editor.isReadOnly():
            return
        values = {'LF': editor.EolUnix, 'CRLF': editor.EolWindows, 'CR': editor.EolMac}
        value, ok = QInputDialog.getItem(self, 'Line endings', 'Convert to:', list(values), 0, False)
        if ok:
            editor.beginUndoAction()
            try:
                editor.convertEols(values[value])
                editor.setEolMode(values[value])
            finally:
                editor.endUndoAction()
        self._refresh_document_status()

    def _choose_document_indent(self):
        """Change future indentation for this tab without rewriting existing text."""
        editor = self.current_editor()
        if editor is None:
            return
        value, ok = QInputDialog.getItem(self, 'Indentation', 'Mode:', ['Tabs: 4', 'Spaces: 2', 'Spaces: 4', 'Spaces: 8'], 2, False)
        if ok:
            editor.setIndentationsUseTabs(value.startswith('Tabs'))
            editor.setTabWidth(int(value[-1]))
            editor.setIndentationWidth(int(value[-1]))
        self._refresh_document_status()
````

| Definition | Responsibility |
|---|---|
| `_refresh_document_status` | Read only metadata and the selection, not the entire document. |
| `_choose_document_encoding` | Change the UTF-8 serialization flag and participate in dirty tracking. |
| `_choose_document_eol` | Convert line endings in one undo group and set the insertion mode. |
| `_choose_document_indent` | Change future indentation for this tab without rewriting existing text. |

### 3. Topic implementation — exact files and methods

#### Step 05.1: create `side_bar_widgets/status_item.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 05.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.status_item import StatusItem
````

#### Step 05.3: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.encoding_status = StatusItem('UTF-8', self._choose_document_encoding, self)
        self.eol_status = StatusItem('LF', self._choose_document_eol, self)
        self.indent_status = StatusItem('Spaces: 4', self._choose_document_indent, self)
        self.interpreter_status = StatusItem('Python', self.choose_interpreter, self)
        self.document_status = QLabel(self)
        for item in (self.encoding_status, self.eol_status, self.indent_status, self.interpreter_status, self.document_status):
            self.statusBar().addPermanentWidget(item)
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._refresh_document_status)
        self._status_timer.start(250)
````

#### Step 05.4: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _refresh_document_status(self):
        """Read only metadata and the selection, not the entire document."""
        editor = self.current_editor()
        for widget in (self.encoding_status, self.eol_status, self.indent_status):
            widget.setEnabled(editor is not None and not editor.isReadOnly())
        interpreter = str(self.python_runner.interpreter)
        self.interpreter_status.setText(Path(interpreter).name)
        self.interpreter_status.setToolTip(interpreter)
        if editor is None:
            self.document_status.setText('No document')
            return
        self.encoding_status.setText('UTF-8 BOM' if getattr(editor, '_utf8_bom', False) else 'UTF-8')
        self.eol_status.setText({editor.EolWindows: 'CRLF', editor.EolUnix: 'LF', editor.EolMac: 'CR'}[editor.eolMode()])
        self.indent_status.setText(f"{'Tabs' if editor.indentationsUseTabs() else 'Spaces'}: {editor.tabWidth()}")
        selected = len(editor.selectedText()) if editor.hasSelectedText() else 0
        activity = 'Running Python' if self.python_runner.is_running() else 'Idle'
        self.document_status.setText(f"Selected {selected} | {'Modified' if editor.isModified() else 'Saved'} | {activity}")

    def _choose_document_encoding(self):
        """Change the UTF-8 serialization flag and participate in dirty tracking."""
        editor = self.current_editor()
        if editor is None or editor.isReadOnly():
            return
        values = ['UTF-8', 'UTF-8 BOM']
        value, ok = QInputDialog.getItem(self, 'Encoding', 'Save as:', values, int(getattr(editor, '_utf8_bom', False)), False)
        if ok and (value == values[1]) != getattr(editor, '_utf8_bom', False):
            editor._utf8_bom = value == values[1]
            editor.setModified(True)
            self._on_editor_text_changed(editor)
        self._refresh_document_status()

    def _choose_document_eol(self):
        """Convert line endings in one undo group and set the insertion mode."""
        editor = self.current_editor()
        if editor is None or editor.isReadOnly():
            return
        values = {'LF': editor.EolUnix, 'CRLF': editor.EolWindows, 'CR': editor.EolMac}
        value, ok = QInputDialog.getItem(self, 'Line endings', 'Convert to:', list(values), 0, False)
        if ok:
            editor.beginUndoAction()
            try:
                editor.convertEols(values[value])
                editor.setEolMode(values[value])
            finally:
                editor.endUndoAction()
        self._refresh_document_status()

    def _choose_document_indent(self):
        """Change future indentation for this tab without rewriting existing text."""
        editor = self.current_editor()
        if editor is None:
            return
        value, ok = QInputDialog.getItem(self, 'Indentation', 'Mode:', ['Tabs: 4', 'Spaces: 2', 'Spaces: 4', 'Spaces: 8'], 2, False)
        if ok:
            editor.setIndentationsUseTabs(value.startswith('Tabs'))
            editor.setTabWidth(int(value[-1]))
            editor.setIndentationWidth(int(value[-1]))
        self._refresh_document_status()

    def current_editor(self):
````

**Using this topic:** Click an encoding/EOL/indentation/interpreter status item to edit it. BOM/EOL changes participate in normal Save and close prompts.


---

<a id="topic-06"></a>

## Topic 06: Polished empty states

### 1. Topic explanation

Explain empty Outline and Search panels in the surfaces that actually exist in this baseline. Hints track row insertion/removal and resize without blocking clicks. This baseline has no Problems or References dock: those belong to the separate 11-topic guide and are not fabricated here.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QAbstractItemModel](https://doc.qt.io/archives/qt-5.15/qabstractitemmodel.html)
- [Qt 5.15 QWidget](https://doc.qt.io/archives/qt-5.15/qwidget.html)

### 2. Topic code

#### `side_bar_widgets/empty_state.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""An empty-state overlay tied to a real item view."""
from PyQt5 import sip
from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtWidgets import QLabel

class EmptyState(QObject):
    """Keep a noninteractive hint centered over an empty item view."""
    def __init__(self, view, message):
        super().__init__(view)
        self.view = view
        self.label = QLabel(message, view.viewport())
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        view.viewport().installEventFilter(self)
        for signal in (view.model().rowsInserted, view.model().rowsRemoved,
                       view.model().modelReset):
            signal.connect(self.refresh)
        self.refresh()

    def refresh(self, *args):
        """Show a hint only when the model has no root rows."""
        if sip.isdeleted(self.view) or sip.isdeleted(self.label):
            return
        self.label.setGeometry(self.view.viewport().rect())
        self.label.setVisible(self.view.model().rowCount() == 0)
        self.label.raise_()

    def eventFilter(self, watched, event):
        """Track viewport resizing without consuming its input."""
        if event.type() in (QEvent.Resize, QEvent.Show):
            self.refresh()
        return False
````

| Definition | Responsibility |
|---|---|
| `EmptyState` | Keep a noninteractive hint centered over an empty item view. |
| `EmptyState.refresh` | Show a hint only when the model has no root rows. |
| `EmptyState.eventFilter` | Track viewport resizing without consuming its input. |

### 3. Topic implementation — exact files and methods

#### Step 06.1: create `side_bar_widgets/empty_state.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 06.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.empty_state import EmptyState
````

#### Step 06.3: `main.py` — MainWindow.__init__, immediately after init_ui

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.outline_empty = EmptyState(self.outline_tree, 'No outline entries.\nOpen a document with headings or declarations.')
        self.search_empty = EmptyState(self.search_list_view, 'No search results.\nEnter a query above to search this workspace.')
````

**Using this topic:** Empty Outline and Search views now explain why no rows are displayed. Their normal UI remains usable.


---

<a id="topic-07"></a>

## Topic 07: Welcome screen

### 1. Topic explanation

Show a live welcome page when every tab group is empty. Offer recent files, recent projects, Open File/Open Folder and Python/Markdown/README templates. Templates open as dirty untitled documents, and the sidebar remains available.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QStackedWidget](https://doc.qt.io/archives/qt-5.15/qstackedwidget.html)
- [Qt 5.15 QSettings](https://doc.qt.io/archives/qt-5.15/qsettings.html)

### 2. Topic code

#### `side_bar_widgets/welcome_screen.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Recent files, recent projects and starter templates on the empty-workspace page."""
from pathlib import Path
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

TEMPLATES = {
    "Python script": (True, '"""Describe this script."""\n\n\ndef main():\n    """Run the script."""\n    print("Hello")\n\n\nif __name__ == "__main__":\n    main()\n'),
    "Markdown note": (False, '# New note\n\n## Notes\n\n'),
    "Markdown README": (False, '# Project name\n\n## Purpose\n\n## Installation\n\n## Usage\n\n'),
}


class Welcome(QWidget):
    """Show recent resources and templates only when every tab group is empty."""

    def __init__(self, recent, open_file, open_folder, parent=None, *, projects=(), create_template=None):
        """Keep callbacks and regenerate recent-resource buttons when shown."""
        super().__init__(parent)
        self.setProperty("designPanel", True)
        self.open_file, self.open_folder = open_file, open_folder
        self.create_template = create_template
        self.layout_ = QVBoxLayout(self)
        self.refresh(recent, projects)

    def _button(self, title, callback, tooltip=""):
        """Add one labeled navigation action with a captured immutable destination."""
        button = QPushButton(title, self)
        button.setToolTip(tooltip)
        button.clicked.connect(lambda _checked=False: callback())
        self.layout_.addWidget(button)

    def refresh(self, recent, projects=()):
        """Rebuild current settings data and show explicit empty-state labels."""
        while self.layout_.count():
            item = self.layout_.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        self.layout_.addWidget(QLabel("MarkdownEditor — Welcome"))
        self._button("Open file", self.open_file)
        self._button("Open folder", self.open_folder)
        for title, values, callback in (("Recent files", recent, self.open_file),
                                         ("Recent projects", projects, self.open_folder)):
            self.layout_.addWidget(QLabel(title))
            if not values:
                self.layout_.addWidget(QLabel("No recent entries yet"))
            for entry in list(values)[:10]:
                path = Path(entry)
                self._button(path.name, lambda p=path, fn=callback: fn(p), str(path))
        if self.create_template is not None:
            self.layout_.addWidget(QLabel("Start from a template"))
            for name in TEMPLATES:
                self._button(name, lambda n=name: self.create_template(n))
        self.layout_.addStretch(1)
````

| Definition | Responsibility |
|---|---|
| `Welcome` | Show recent resources and templates only when every tab group is empty. |
| `Welcome.__init__` | Keep callbacks and regenerate recent-resource buttons when shown. |
| `Welcome._button` | Add one labeled navigation action with a captured immutable destination. |
| `Welcome.refresh` | Rebuild current settings data and show explicit empty-state labels. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _refresh_welcome(self):
        """Refresh recent lists on transition to an empty workspace, not every tick."""
        empty = not bool(self.tab_view.all_editors())
        if empty and not self._welcome_visible:
            self.welcome_page.refresh(self.recent_files, self.settings.value('recent_projects', [], type=list))
        self._welcome_visible = empty
        self.editor_stack.setCurrentWidget(self.welcome_page if empty else self.tab_view)

    def _welcome_open_file(self, path=None):
        """Use normal file opening and its existing missing-file handling."""
        if path is None:
            self.open_file()
        else:
            self.open_recent_file(str(path))

    def _welcome_open_folder(self, path=None):
        """Open a chooser or a recent folder using one project lifecycle."""
        self.open_folder(path)
        self.welcome_page.refresh(self.recent_files, self.settings.value('recent_projects', [], type=list))

    def _welcome_template(self, name):
        """Create one language-correct unsaved draft from the built-in catalog."""
        python, text = TEMPLATES[name]
        previous = self.python_editor_active
        self.python_editor_active = python
        try:
            editor = self.new_file()
        finally:
            self.python_editor_active = previous
        editor.setText(text)
        editor.setModified(True)
        self._on_editor_text_changed(editor)
        self._refresh_welcome()
````

| Definition | Responsibility |
|---|---|
| `_refresh_welcome` | Refresh recent lists on transition to an empty workspace, not every tick. |
| `_welcome_open_file` | Use normal file opening and its existing missing-file handling. |
| `_welcome_open_folder` | Open a chooser or a recent folder using one project lifecycle. |
| `_welcome_template` | Create one language-correct unsaved draft from the built-in catalog. |

### 3. Topic implementation — exact files and methods

#### Step 07.1: create `side_bar_widgets/welcome_screen.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 07.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.welcome_screen import Welcome, TEMPLATES
````

#### Step 07.3: `main.py` — MainWindow.set_up_body: replace only the editor splitter slot

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.hs_split.addWidget(self.tab_view)
````

**NEW**

````python
        self.editor_stack = QStackedWidget(self)
        self.editor_stack.addWidget(self.tab_view)
        self.welcome_page = Welcome(
            self.recent_files, self._welcome_open_file, self._welcome_open_folder, self,
            projects=self.settings.value('recent_projects', [], type=list),
            create_template=self._welcome_template)
        self.editor_stack.addWidget(self.welcome_page)
        self.editor_stack.setCurrentWidget(self.welcome_page)
        self.hs_split.addWidget(self.editor_stack)
````

#### Step 07.4: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self._welcome_visible = False
        self._welcome_timer = QTimer(self)
        self._welcome_timer.timeout.connect(self._refresh_welcome)
        self._welcome_timer.start(250)
````

#### Step 07.5: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _refresh_welcome(self):
        """Refresh recent lists on transition to an empty workspace, not every tick."""
        empty = not bool(self.tab_view.all_editors())
        if empty and not self._welcome_visible:
            self.welcome_page.refresh(self.recent_files, self.settings.value('recent_projects', [], type=list))
        self._welcome_visible = empty
        self.editor_stack.setCurrentWidget(self.welcome_page if empty else self.tab_view)

    def _welcome_open_file(self, path=None):
        """Use normal file opening and its existing missing-file handling."""
        if path is None:
            self.open_file()
        else:
            self.open_recent_file(str(path))

    def _welcome_open_folder(self, path=None):
        """Open a chooser or a recent folder using one project lifecycle."""
        self.open_folder(path)
        self.welcome_page.refresh(self.recent_files, self.settings.value('recent_projects', [], type=list))

    def _welcome_template(self, name):
        """Create one language-correct unsaved draft from the built-in catalog."""
        python, text = TEMPLATES[name]
        previous = self.python_editor_active
        self.python_editor_active = python
        try:
            editor = self.new_file()
        finally:
            self.python_editor_active = previous
        editor.setText(text)
        editor.setModified(True)
        self._on_editor_text_changed(editor)
        self._refresh_welcome()

    def current_editor(self):
````

#### Step 07.6: `main.py` — MainWindow.open_folder

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def open_folder(self):
        """Select a project folder and retarget project-scoped services."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        new_folder = QFileDialog.getExistingDirectory(
            self,
            "Pick A Folder",
            "",
            options=options,
        )
        if not new_folder:
            return

        selected = Path(new_folder).resolve()
        self.file_manager.model.setRootPath(str(selected))
        self.file_manager.setRootIndex(self.file_manager.model.index(str(selected)))
        self.terminal.set_working_directory(selected, restart=True)
        self._refresh_git_state()

        new_workspace = self._discover_workspace_root(selected)
        if new_workspace != self._workspace_root:
            self._restart_ruff(
                python_executable=self.python_runner.interpreter,
                workspace_root=new_workspace,
            )

        self.statusBar().showMessage(f"Opened {selected}", 2_000)
````

**NEW**

````python
    def open_folder(self, folder=None):
        """Select a project folder and retarget project-scoped services."""
        new_folder = str(folder) if folder is not None else QFileDialog.getExistingDirectory(self, 'Pick A Folder', '')
        if not new_folder:
            return
        if not Path(new_folder).is_dir():
            QMessageBox.warning(self, 'Open folder', 'This folder no longer exists.')
            return

        selected = Path(new_folder).resolve()
        self.file_manager.model.setRootPath(str(selected))
        self.file_manager.setRootIndex(self.file_manager.model.index(str(selected)))
        self.terminal.set_working_directory(selected, restart=True)
        self._refresh_git_state()

        new_workspace = self._discover_workspace_root(selected)
        if new_workspace != self._workspace_root:
            self._restart_ruff(
                python_executable=self.python_runner.interpreter,
                workspace_root=new_workspace,
            )

        recent = self.settings.value('recent_projects', [], type=list)
        recent = [str(selected)] + [p for p in recent if p != str(selected)]
        self.settings.setValue('recent_projects', recent[:10])
        self.statusBar().showMessage(f"Opened {selected}", 2_000)
````

**Using this topic:** Close all tabs to reveal Welcome. Recent files/projects and templates use the existing document/project lifecycle.


---

<a id="topic-08"></a>

## Topic 08: Focus mode

### 1. Topic explanation

Hide sidebar, preview, docks, toolbars and menus, then restore their explicit visibility and central splitter sizes. Ctrl+Shift+F11 remains available while menus are hidden; tab switches cannot reopen a hidden preview.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QAction](https://doc.qt.io/archives/qt-5.15/qaction.html)
- [Qt 5.15 QWidget](https://doc.qt.io/archives/qt-5.15/qwidget.html)
- [Qt 5.15 QSplitter](https://doc.qt.io/archives/qt-5.15/qsplitter.html)

### 2. Topic code

#### `code_settings/focus_mode.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Reversible focus mode with visibility enforcement."""
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QDockWidget, QToolBar

class FocusMode(QObject):
    """Remember explicit hidden state, including central splitter panels."""
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.previous = None

    def toggle(self):
        """Hide optional surfaces or restore the captured state."""
        if self.previous is None:
            w = self.window
            self.split = w.hs_split.saveState()
            widgets = [w.side_bar, w.side_panel, w.preview, w.menuBar()]
            widgets += w.findChildren(QDockWidget) + w.findChildren(QToolBar)
            self.previous = [(item, not item.isHidden()) for item in widgets]
            for item, _ in self.previous:
                item.installEventFilter(self)
                item.hide()
        else:
            old, self.previous = self.previous, None
            for item, visible in old:
                item.removeEventFilter(self)
                item.setVisible(visible)
            self.window.hs_split.restoreState(self.split)

    def eventFilter(self, watched, event):
        """A tab switch must not reopen the preview during focus mode."""
        if self.previous is not None and event.type() == QEvent.Show:
            watched.hide()
        return False
````

| Definition | Responsibility |
|---|---|
| `FocusMode` | Remember explicit hidden state, including central splitter panels. |
| `FocusMode.toggle` | Hide optional surfaces or restore the captured state. |
| `FocusMode.eventFilter` | A tab switch must not reopen the preview during focus mode. |

### 3. Topic implementation — exact files and methods

#### Step 08.1: create `code_settings/focus_mode.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 08.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_settings.focus_mode import FocusMode
````

#### Step 08.3: `main.py` — MainWindow.__init__, immediately after init_ui

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.focus_mode = FocusMode(self)
````

#### Step 08.4: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        focus_action = menu_bar.addAction('Focus Mode')
        focus_action.setObjectName('view.focus')
        focus_action.setShortcut('Ctrl+Shift+F11')
        focus_action.setShortcutContext(Qt.ApplicationShortcut)
        self.addAction(focus_action)
        focus_action.triggered.connect(lambda: self.focus_mode.toggle())
````

**Using this topic:** Use Focus Mode or Ctrl+Shift+F11. The same shortcut restores the captured arrangement while menus are hidden.


---

<a id="topic-09"></a>

## Topic 09: Workspace layout presets

### 1. Topic explanation

Provide immediate Python Coding, Markdown Writing and Git Review presets, plus named saved layouts. Persist dock state, geometry, central splitter state, sidebar page and visibility. Restore is validated and rolls back if Qt rejects the saved state. Exit Focus Mode before applying a preset.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QMainWindow](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)
- [Qt 5.15 QSplitter](https://doc.qt.io/archives/qt-5.15/qsplitter.html)
- [Qt 5.15 QSettings](https://doc.qt.io/archives/qt-5.15/qsettings.html)

### 2. Topic code

This topic adds or changes methods in existing classes. Their complete code is included in the OLD → NEW steps below; there is no standalone helper file or later bootstrap to install.

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _layout_snapshot(self):
        """Capture central-widget state separately from QMainWindow dock state."""
        return {'docks': self.saveState(1), 'geometry': self.saveGeometry(),
                'split': self.hs_split.saveState(), 'page': self.side_panel.currentIndex(),
                'side': not self.side_panel.isHidden(), 'bar': not self.side_bar.isHidden(),
                'preview': not self.preview.isHidden()}

    def _apply_layout_snapshot(self, value):
        """Reject malformed records; the caller handles rollback after Qt failure."""
        if not isinstance(value, dict) or not all(k in value for k in ('docks', 'geometry', 'split', 'page', 'side', 'bar', 'preview')):
            return False
        if not all(isinstance(value[k], QByteArray) for k in ('docks', 'geometry', 'split')):
            return False
        if not isinstance(value['page'], int) or not 0 <= value['page'] < self.side_panel.count():
            return False
        if not (self.restoreGeometry(value['geometry']) and self.restoreState(value['docks'], 1) and self.hs_split.restoreState(value['split'])):
            return False
        self.side_panel.setCurrentIndex(value['page'])
        self.side_panel.setVisible(bool(value['side']))
        self.side_bar.setVisible(bool(value['bar']))
        self.preview.setVisible(bool(value['preview']))
        if value['preview']:
            self.render_preview()
        return True

    def _save_layout(self):
        """Persist a named layout without changing any document or tab group."""
        name, ok = QInputDialog.getText(self, 'Save layout', 'Name:')
        if not ok or not name.strip():
            return
        if getattr(getattr(self, 'focus_mode', None), 'previous', None) is not None:
            QMessageBox.information(self, 'Layout', 'Leave Focus Mode before saving a layout.')
            return
        values = self.settings.value('workspace_layouts_v3', {})
        values = values if isinstance(values, dict) else {}
        values[name.strip()] = self._layout_snapshot()
        self.settings.setValue('workspace_layouts_v3', values)

    def _choose_layout(self):
        """Choose from user-saved names; built-ins remain separate menu entries."""
        values = self.settings.value('workspace_layouts_v3', {})
        if not isinstance(values, dict) or not values:
            QMessageBox.information(self, 'Layout', 'No saved layouts yet.')
            return
        name, ok = QInputDialog.getItem(self, 'Layout', 'Restore:', sorted(values), 0, False)
        if ok:
            self._restore_layout(name)

    def _restore_layout(self, name):
        """Restore an override or apply an immediate built-in arrangement."""
        focus = getattr(self, 'focus_mode', None)
        if focus is not None and focus.previous is not None:
            focus.toggle()
        values = self.settings.value('workspace_layouts_v3', {})
        if isinstance(values, dict) and name in values:
            previous = self._layout_snapshot()
            if not self._apply_layout_snapshot(values[name]):
                self._apply_layout_snapshot(previous)
                QMessageBox.warning(self, 'Layout', 'Invalid saved layout; previous arrangement restored.')
            return
        for dock in self.findChildren(QDockWidget):
            dock.hide()
        self.side_bar.show()
        self.side_panel.setVisible(name != 'Markdown Writing')
        self.preview.setVisible(name == 'Markdown Writing')
        if name == 'Python Coding':
            self.side_panel.setCurrentWidget(self.outline_frame)
            self.console_dock.show()
            self.hs_split.setSizes([260, 900, 0])
        elif name == 'Markdown Writing':
            self.hs_split.setSizes([0, 650, 650])
            self.render_preview()
        elif name == 'Git Review':
            self.side_panel.setCurrentWidget(self.file_manager_frame)
            self.hs_split.setSizes([280, 900, 0])
            for dock in self.findChildren(QDockWidget):
                if dock.objectName() == 'GitHistoryDock':
                    dock.show()
````

| Definition | Responsibility |
|---|---|
| `_layout_snapshot` | Capture central-widget state separately from QMainWindow dock state. |
| `_apply_layout_snapshot` | Reject malformed records; the caller handles rollback after Qt failure. |
| `_save_layout` | Persist a named layout without changing any document or tab group. |
| `_choose_layout` | Choose from user-saved names; built-ins remain separate menu entries. |
| `_restore_layout` | Restore an override or apply an immediate built-in arrangement. |

### 3. Topic implementation — exact files and methods

#### Step 09.1: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.console_dock.setObjectName('ConsoleDock')
        self.terminal_dock.setObjectName('TerminalDock')
````

#### Step 09.2: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        layouts = menu_bar.addMenu('Workspace Layouts')
        for name in ('Python Coding', 'Markdown Writing', 'Git Review'):
            layouts.addAction(name).triggered.connect(lambda checked=False, n=name: self._restore_layout(n))
        layouts.addAction('Save Layout As...').triggered.connect(self._save_layout)
        layouts.addAction('Restore Saved Layout...').triggered.connect(self._choose_layout)
````

#### Step 09.3: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _layout_snapshot(self):
        """Capture central-widget state separately from QMainWindow dock state."""
        return {'docks': self.saveState(1), 'geometry': self.saveGeometry(),
                'split': self.hs_split.saveState(), 'page': self.side_panel.currentIndex(),
                'side': not self.side_panel.isHidden(), 'bar': not self.side_bar.isHidden(),
                'preview': not self.preview.isHidden()}

    def _apply_layout_snapshot(self, value):
        """Reject malformed records; the caller handles rollback after Qt failure."""
        if not isinstance(value, dict) or not all(k in value for k in ('docks', 'geometry', 'split', 'page', 'side', 'bar', 'preview')):
            return False
        if not all(isinstance(value[k], QByteArray) for k in ('docks', 'geometry', 'split')):
            return False
        if not isinstance(value['page'], int) or not 0 <= value['page'] < self.side_panel.count():
            return False
        if not (self.restoreGeometry(value['geometry']) and self.restoreState(value['docks'], 1) and self.hs_split.restoreState(value['split'])):
            return False
        self.side_panel.setCurrentIndex(value['page'])
        self.side_panel.setVisible(bool(value['side']))
        self.side_bar.setVisible(bool(value['bar']))
        self.preview.setVisible(bool(value['preview']))
        if value['preview']:
            self.render_preview()
        return True

    def _save_layout(self):
        """Persist a named layout without changing any document or tab group."""
        name, ok = QInputDialog.getText(self, 'Save layout', 'Name:')
        if not ok or not name.strip():
            return
        if getattr(getattr(self, 'focus_mode', None), 'previous', None) is not None:
            QMessageBox.information(self, 'Layout', 'Leave Focus Mode before saving a layout.')
            return
        values = self.settings.value('workspace_layouts_v3', {})
        values = values if isinstance(values, dict) else {}
        values[name.strip()] = self._layout_snapshot()
        self.settings.setValue('workspace_layouts_v3', values)

    def _choose_layout(self):
        """Choose from user-saved names; built-ins remain separate menu entries."""
        values = self.settings.value('workspace_layouts_v3', {})
        if not isinstance(values, dict) or not values:
            QMessageBox.information(self, 'Layout', 'No saved layouts yet.')
            return
        name, ok = QInputDialog.getItem(self, 'Layout', 'Restore:', sorted(values), 0, False)
        if ok:
            self._restore_layout(name)

    def _restore_layout(self, name):
        """Restore an override or apply an immediate built-in arrangement."""
        focus = getattr(self, 'focus_mode', None)
        if focus is not None and focus.previous is not None:
            focus.toggle()
        values = self.settings.value('workspace_layouts_v3', {})
        if isinstance(values, dict) and name in values:
            previous = self._layout_snapshot()
            if not self._apply_layout_snapshot(values[name]):
                self._apply_layout_snapshot(previous)
                QMessageBox.warning(self, 'Layout', 'Invalid saved layout; previous arrangement restored.')
            return
        for dock in self.findChildren(QDockWidget):
            dock.hide()
        self.side_bar.show()
        self.side_panel.setVisible(name != 'Markdown Writing')
        self.preview.setVisible(name == 'Markdown Writing')
        if name == 'Python Coding':
            self.side_panel.setCurrentWidget(self.outline_frame)
            self.console_dock.show()
            self.hs_split.setSizes([260, 900, 0])
        elif name == 'Markdown Writing':
            self.hs_split.setSizes([0, 650, 650])
            self.render_preview()
        elif name == 'Git Review':
            self.side_panel.setCurrentWidget(self.file_manager_frame)
            self.hs_split.setSizes([280, 900, 0])
            for dock in self.findChildren(QDockWidget):
                if dock.objectName() == 'GitHistoryDock':
                    dock.show()

    def current_editor(self):
````

**Using this topic:** Choose Workspace Layouts → Python Coding, Markdown Writing or Git Review, or save a named arrangement.


---

<a id="topic-10"></a>

## Topic 10: Automatic recovery

### 1. Topic explanation

Keep atomic, per-instance recovery drafts for saved and untitled buffers. A session lock prevents stealing drafts from another running editor. Capture only changed snapshots; preserve BOM and EOL metadata and restore into separate dirty tabs. Save and explicit Discard remove drafts; Cancel preserves them.

**Prerequisites:** None; apply directly to the pinned baseline.

**Operational details:** Recovery captures at most once per five seconds and skips unchanged payloads. Snapshot serialization and writes are synchronous in this implementation and bounded to 32 MB of source per draft; large drafts can pause the UI briefly. A failure is shown and existing snapshots are retained. This does not promise recovery of edits made after the last successful snapshot.

**Documentation used:**

- [Qt 5.15 QLockFile](https://doc.qt.io/archives/qt-5.15/qlockfile.html)
- [Qt 5.15 QStandardPaths](https://doc.qt.io/archives/qt-5.15/qstandardpaths.html)
- [Atomic replacement](https://docs.python.org/3/library/os.html#os.replace)

### 2. Topic code

#### `code_inteligence/document_recovery.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Atomic, isolated recovery snapshots; no source-file writes."""
import json
import os
import uuid
from pathlib import Path
from PyQt5.QtCore import QObject, QTimer, QStandardPaths, QLockFile
from PyQt5.QtWidgets import QMessageBox

class RecoveryManager(QObject):
    """Own the session lock and a timer for modified document snapshots."""
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.root = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)) / 'recovery_v2'
        self.directory = self.root / uuid.uuid4().hex
        self.directory.mkdir(parents=True)
        self.lock = QLockFile(str(self.directory / 'session.lock'))
        self.lock.setStaleLockTime(0)
        if not self.lock.tryLock(0):
            raise OSError('Could not lock recovery session')
        self.last = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture)
        self.timer.start(5000)

    def discard(self, editor):
        """Remove this session's draft only after a confirmed save/close."""
        key = getattr(editor, '_recovery_id', None)
        if key:
            self.last.pop(key, None)
            try:
                (self.directory / (key + '.json')).unlink(missing_ok=True)
            except OSError as error:
                self.window.statusBar().showMessage(str(error), 5000)

    def capture(self):
        """Use atomic replacement so crashes cannot truncate the last draft."""
        for editor in self.window.tab_view.all_editors():
            if not editor.isModified():
                self.discard(editor)
                continue
            if not getattr(editor, '_recovery_id', None):
                editor._recovery_id = uuid.uuid4().hex
            target = self.directory / (editor._recovery_id + '.json')
            temp = target.with_suffix('.tmp')
            payload = {'text': editor.text(), 'path': str(editor.path or ''),
                       'python': bool(editor.is_python_file),
                       'bom': bool(getattr(editor, '_utf8_bom', False)), 'eol': int(editor.eolMode())}
            if self.last.get(editor._recovery_id) == payload:
                continue
            try:
                if len(payload['text'].encode('utf-8')) > 32_000_000:
                    raise OSError('Draft exceeds the 32 MB recovery limit; save it explicitly')
                with temp.open('w', encoding='utf-8') as stream:
                    json.dump(payload, stream, ensure_ascii=False)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temp, target)
                self.last[editor._recovery_id] = payload
            except OSError as error:
                self.window.statusBar().showMessage('Recovery: ' + str(error), 5000)

    def offer(self):
        """Recover only unlocked prior sessions into independent new tabs."""
        for folder in self.root.iterdir():
            if not folder.is_dir() or folder == self.directory:
                continue
            lock = QLockFile(str(folder / 'session.lock'))
            lock.setStaleLockTime(0)
            if not lock.tryLock(0):
                continue
            try:
                for path in folder.glob('*.json'):
                    try:
                        if path.stat().st_size > 64_000_000:
                            raise ValueError('Recovery record exceeds 64 MB; retained on disk')
                        item = json.loads(path.read_text(encoding='utf-8'))
                        if not isinstance(item, dict) or not isinstance(item.get('text'), str):
                            raise ValueError('Invalid draft text')
                        answer = QMessageBox.question(self.window, 'Recover draft',
                            'Recover as a new unsaved tab?\n' + str(item.get('path') or 'Untitled'),
                            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                            QMessageBox.Yes)
                        if answer == QMessageBox.Cancel:
                            continue
                        if answer == QMessageBox.Yes:
                            old_mode = self.window.python_editor_active
                            self.window.python_editor_active = bool(item.get('python'))
                            try:
                                editor = self.window.new_file()
                            finally:
                                self.window.python_editor_active = old_mode
                            editor._utf8_bom = bool(item.get('bom', False))
                            eol = item.get('eol')
                            if eol in (editor.EolWindows, editor.EolUnix, editor.EolMac):
                                editor.setEolMode(eol)
                            editor.setText(item['text'])
                            editor.setModified(True)
                            self.window._dirty_editors.add(editor)
                            # Persist the recovered copy before deleting its predecessor.
                            self.capture()
                            if not (self.directory / (editor._recovery_id + '.json')).exists():
                                continue
                        path.unlink()
                    except (OSError, ValueError, TypeError) as error:
                        self.window.statusBar().showMessage('Recovery: ' + str(error), 5000)
            finally:
                lock.unlock()

    def finish(self):
        """Called only once all window-close prompts have succeeded."""
        self.timer.stop()
        for editor in self.window.tab_view.all_editors():
            self.discard(editor)
        self.lock.unlock()
````

| Definition | Responsibility |
|---|---|
| `RecoveryManager` | Own the session lock and a timer for modified document snapshots. |
| `RecoveryManager.discard` | Remove this session's draft only after a confirmed save/close. |
| `RecoveryManager.capture` | Use atomic replacement so crashes cannot truncate the last draft. |
| `RecoveryManager.offer` | Recover only unlocked prior sessions into independent new tabs. |
| `RecoveryManager.finish` | Called only once all window-close prompts have succeeded. |

### 3. Topic implementation — exact files and methods

#### Step 10.1: create `code_inteligence/document_recovery.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 10.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_inteligence.document_recovery import RecoveryManager
````

#### Step 10.3: `main.py` — MainWindow.__init__, immediately after init_ui

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.recovery = None
        try:
            self.recovery = RecoveryManager(self)
            QTimer.singleShot(0, self.recovery.offer)
        except OSError as error:
            QMessageBox.warning(self, 'Recovery unavailable', str(error))
````

#### Step 10.4: `main.py` — MainWindow._save_editor_to_path: successful save

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.mark_editor_clean(editor)
        return True
````

**NEW**

````python
        self.mark_editor_clean(editor)
        if self.recovery is not None:
            self.recovery.discard(editor)
        return True
````

#### Step 10.5: `main.py` — MainWindow.close_editor: after accepted prompt

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self._dirty_editors.discard(editor)
        self.tab_view.remove_editor(editor)
````

**NEW**

````python
        if self.recovery is not None:
            self.recovery.discard(editor)
        self._dirty_editors.discard(editor)
        self.tab_view.remove_editor(editor)
````

#### Step 10.6: `main.py` — MainWindow.closeEvent: after all prompts succeed

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
            self._close_prompts_complete = True
````

**NEW**

````python
            if self.recovery is not None:
                self.recovery.finish()
            self._close_prompts_complete = True
````

#### Step 10.7: `main.py` — MainWindow._convert_editor: transfer document metadata

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        new_editor._save_target = getattr(old, "_save_target", path)
````

**NEW**

````python
        new_editor._save_target = getattr(old, "_save_target", path)
        new_editor._recovery_id = getattr(old, "_recovery_id", None)
````

#### Step 10.8: `main.py` — MainWindow._convert_editor: retain recovery dirty state

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        new_editor.setTextSafely(text)
````

**NEW**

````python
        new_editor.setTextSafely(text)
        new_editor.setModified(was_dirty)
````

**Using this topic:** Recovery runs every five seconds. After an interrupted session, startup offers the unlocked drafts as separate unsaved tabs.


---

<a id="topic-13"></a>

## Topic 13: Compare/diff editor

### 1. Topic explanation

Compare the current buffer with disk, two chosen files, or Git HEAD. Two read-only panes highlight changed lines and synchronize scrolling; a unified diff preserves newline differences. Comparison never writes files. Git runs asynchronously and uses an argument vector, including on Windows.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Python difflib](https://docs.python.org/3/library/difflib.html)
- [Qt 5.15 QPlainTextEdit](https://doc.qt.io/archives/qt-5.15/qplaintextedit.html)
- [Git show](https://git-scm.com/docs/git-show)

### 2. Topic code

#### `side_bar_widgets/comparison_dialog.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Side-by-side immutable comparisons used by history, disk and rename previews."""
from difflib import SequenceMatcher, unified_diff
from PyQt5.QtGui import QColor, QTextCursor, QTextFormat
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
                             QPlainTextEdit, QTextEdit, QVBoxLayout)


class ComparisonDialog(QDialog):
    """Show two snapshots with line highlights and synchronized scrolling."""

    def __init__(self, before, after, title, parent=None, *, accept_text="Open draft"):
        """Build read-only panes; acceptance never writes a file by itself."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1100, 650)
        layout = QVBoxLayout(self)
        panes = QHBoxLayout()
        self.left, self.right = QPlainTextEdit(), QPlainTextEdit()
        for label, view, source in (("Current / before", self.left, before),
                                     ("Selected / proposed", self.right, after)):
            column = QVBoxLayout()
            column.addWidget(QLabel(label))
            view.setReadOnly(True)
            view.setPlainText(source)
            column.addWidget(view)
            panes.addLayout(column)
        layout.addLayout(panes)
        self._highlight(before, after)
        diff = QPlainTextEdit(self)
        diff.setReadOnly(True)
        pieces = unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before', tofile='after')
        diff.setPlainText(''.join(p if p.endswith('\n') else p + '\n' + chr(92) + ' No newline at end of file\n' for p in pieces) or 'No differences')
        layout.addWidget(diff)
        self.left.verticalScrollBar().valueChanged.connect(lambda value: self._scroll(self.left, self.right, value))
        self.right.verticalScrollBar().valueChanged.connect(lambda value: self._scroll(self.right, self.left, value))
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        if accept_text:
            accept = buttons.addButton(accept_text, QDialogButtonBox.AcceptRole)
            accept.clicked.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _scroll(self, source, target, value):
        """Map proportional scroll positions without feedback recursion."""
        bar = target.verticalScrollBar()
        bar.blockSignals(True)
        bar.setValue(round(value / max(1, source.verticalScrollBar().maximum()) * bar.maximum()))
        bar.blockSignals(False)

    def _highlight(self, before, after):
        """Color changed source lines, leaving both snapshots immutable."""
        selections = [[], []]
        for tag, a, b, c, d in SequenceMatcher(None, before.splitlines(), after.splitlines(), autojunk=True).get_opcodes():
            if tag == "equal":
                continue
            for side, view, start, end in ((0, self.left, a, b), (1, self.right, c, d)):
                for line in range(start, end):
                    selection = QTextEdit.ExtraSelection()
                    selection.cursor = QTextCursor(view.document().findBlockByNumber(line))
                    selection.format.setBackground(QColor("#593b40" if side == 0 else "#304d3f"))
                    selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                    selections[side].append(selection)
        self.left.setExtraSelections(selections[0])
        self.right.setExtraSelections(selections[1])
````

| Definition | Responsibility |
|---|---|
| `ComparisonDialog` | Show two snapshots with line highlights and synchronized scrolling. |
| `ComparisonDialog.__init__` | Build read-only panes; acceptance never writes a file by itself. |
| `ComparisonDialog._scroll` | Map proportional scroll positions without feedback recursion. |
| `ComparisonDialog._highlight` | Color changed source lines, leaving both snapshots immutable. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _compare_buffer_with_disk(self):
        """Read exact UTF-8 bytes without newline translation."""
        editor = self.current_editor()
        if editor is None or not getattr(editor, 'path', None):
            return
        try:
            disk = Path(editor.path).read_bytes().decode('utf-8-sig')
            ComparisonDialog(editor.text(), disk, 'Buffer / Disk', self, accept_text=None).exec_()
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'Compare', str(error))

    def _compare_two_files(self):
        """Open immutable file snapshots; never replace an open buffer."""
        paths = []
        for label in ('First file', 'Second file'):
            path, _ = QFileDialog.getOpenFileName(self, label)
            if not path:
                return
            paths.append(Path(path))
        try:
            left, right = [p.read_bytes().decode('utf-8-sig') for p in paths]
            ComparisonDialog(left, right, f'{paths[0].name} / {paths[1].name}', self, accept_text=None).exec_()
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'Compare', str(error))

    def _compare_git_head(self):
        """Resolve repository root and read HEAD with two nonblocking Git requests."""
        editor = self.current_editor()
        if editor is None or not getattr(editor, 'path', None):
            return
        if getattr(self, '_comparison_process', None) is not None:
            return
        path, source = Path(editor.path).resolve(), editor.text()
        process = QProcess(self)
        self._comparison_process = process
        self._comparison_bytes = bytearray()
        process.setWorkingDirectory(str(path.parent))
        def read():
            """Drain output while bounding retained Git data."""
            self._comparison_bytes.extend(bytes(process.readAllStandardOutput()))
            if len(self._comparison_bytes) > 16_000_000:
                process.kill()
        def finish(code, status):
            """Start the blob read only after Git returned a valid root."""
            read()
            if code == 0 and status == QProcess.NormalExit and getattr(process, '_phase', 0) == 0:
                try:
                    root = Path(bytes(self._comparison_bytes).decode('utf-8').strip())
                    relative = path.relative_to(root).as_posix()
                except (ValueError, UnicodeError):
                    code = -1
                else:
                    process._phase = 1
                    self._comparison_bytes.clear()
                    process.setWorkingDirectory(str(root))
                    process.start('git', ['show', 'HEAD:' + relative])
                    return
            data = bytes(self._comparison_bytes)
            self._comparison_process = None
            process.deleteLater()
            if getattr(self, '_close_prompts_complete', False):
                return
            if code != 0 or status != QProcess.NormalExit:
                QMessageBox.warning(self, 'Git compare', 'Git could not read HEAD for this file.')
                return
            try:
                before = data.decode('utf-8-sig')
                ComparisonDialog(before, source, 'Git HEAD / captured buffer', self, accept_text=None).exec_()
            except UnicodeError as error:
                QMessageBox.warning(self, 'Git compare', str(error))
        process.readyReadStandardOutput.connect(read)
        process.finished.connect(finish)
        process.errorOccurred.connect(lambda error: finish(-1, QProcess.CrashExit) if error == QProcess.FailedToStart else None)
        process.start('git', ['rev-parse', '--show-toplevel'])
````

| Definition | Responsibility |
|---|---|
| `_compare_buffer_with_disk` | Read exact UTF-8 bytes without newline translation. |
| `_compare_two_files` | Open immutable file snapshots; never replace an open buffer. |
| `_compare_git_head` | Resolve repository root and read HEAD with two nonblocking Git requests. |

### 3. Topic implementation — exact files and methods

#### Step 13.1: create `side_bar_widgets/comparison_dialog.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 13.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.comparison_dialog import ComparisonDialog
````

#### Step 13.3: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        compare_menu = menu_bar.addMenu('Compare')
        compare_menu.addAction('Buffer with Disk').triggered.connect(self._compare_buffer_with_disk)
        compare_menu.addAction('Two Files...').triggered.connect(self._compare_two_files)
        compare_menu.addAction('Git HEAD with Buffer').triggered.connect(self._compare_git_head)
````

#### Step 13.4: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _compare_buffer_with_disk(self):
        """Read exact UTF-8 bytes without newline translation."""
        editor = self.current_editor()
        if editor is None or not getattr(editor, 'path', None):
            return
        try:
            disk = Path(editor.path).read_bytes().decode('utf-8-sig')
            ComparisonDialog(editor.text(), disk, 'Buffer / Disk', self, accept_text=None).exec_()
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'Compare', str(error))

    def _compare_two_files(self):
        """Open immutable file snapshots; never replace an open buffer."""
        paths = []
        for label in ('First file', 'Second file'):
            path, _ = QFileDialog.getOpenFileName(self, label)
            if not path:
                return
            paths.append(Path(path))
        try:
            left, right = [p.read_bytes().decode('utf-8-sig') for p in paths]
            ComparisonDialog(left, right, f'{paths[0].name} / {paths[1].name}', self, accept_text=None).exec_()
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'Compare', str(error))

    def _compare_git_head(self):
        """Resolve repository root and read HEAD with two nonblocking Git requests."""
        editor = self.current_editor()
        if editor is None or not getattr(editor, 'path', None):
            return
        if getattr(self, '_comparison_process', None) is not None:
            return
        path, source = Path(editor.path).resolve(), editor.text()
        process = QProcess(self)
        self._comparison_process = process
        self._comparison_bytes = bytearray()
        process.setWorkingDirectory(str(path.parent))
        def read():
            """Drain output while bounding retained Git data."""
            self._comparison_bytes.extend(bytes(process.readAllStandardOutput()))
            if len(self._comparison_bytes) > 16_000_000:
                process.kill()
        def finish(code, status):
            """Start the blob read only after Git returned a valid root."""
            read()
            if code == 0 and status == QProcess.NormalExit and getattr(process, '_phase', 0) == 0:
                try:
                    root = Path(bytes(self._comparison_bytes).decode('utf-8').strip())
                    relative = path.relative_to(root).as_posix()
                except (ValueError, UnicodeError):
                    code = -1
                else:
                    process._phase = 1
                    self._comparison_bytes.clear()
                    process.setWorkingDirectory(str(root))
                    process.start('git', ['show', 'HEAD:' + relative])
                    return
            data = bytes(self._comparison_bytes)
            self._comparison_process = None
            process.deleteLater()
            if getattr(self, '_close_prompts_complete', False):
                return
            if code != 0 or status != QProcess.NormalExit:
                QMessageBox.warning(self, 'Git compare', 'Git could not read HEAD for this file.')
                return
            try:
                before = data.decode('utf-8-sig')
                ComparisonDialog(before, source, 'Git HEAD / captured buffer', self, accept_text=None).exec_()
            except UnicodeError as error:
                QMessageBox.warning(self, 'Git compare', str(error))
        process.readyReadStandardOutput.connect(read)
        process.finished.connect(finish)
        process.errorOccurred.connect(lambda error: finish(-1, QProcess.CrashExit) if error == QProcess.FailedToStart else None)
        process.start('git', ['rev-parse', '--show-toplevel'])

    def current_editor(self):
````

#### Step 13.5: `main.py` — MainWindow.closeEvent: stop owned work

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.stop()
````

**NEW**

````python
        process = getattr(self, '_comparison_process', None)
        if process is not None:
            process.kill()
        self.terminal.stop()
````

**If Topic 23 is already installed:** the terminal stop is guarded. Insert this topic’s shutdown statements immediately **before** that guard, using:

````python
        process = getattr(self, '_comparison_process', None)
        if process is not None:
            process.kill()
        if self.terminal is not None:
            self.terminal.stop()
````

#### Step 13.6: `main.py` — MainWindow._background_work_running: retain worker ownership

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _background_work_running(self) -> bool:
````

**NEW**

````python
    def _background_work_running(self) -> bool:
        process = getattr(self, '_comparison_process', None)
        if process is not None and process.state() != QProcess.NotRunning:
            return True
````

**Using this topic:** Use Compare → Buffer with Disk, Two Files or Git HEAD with Buffer. All comparison panes are read-only.


---

<a id="topic-11"></a>

## Topic 11: Local file history

### 1. Topic explanation

Retain the previous on-disk bytes before each successful replacement, deduplicate identical versions and bound retention per file. Select a timestamped version, compare it to the live buffer, then open a language-correct unsaved draft. The source file is never overwritten by history browsing.

**Prerequisites:** Topic 13

**Operational details:** History is bounded per path, not by a global quota across every project. A snapshot is taken before replacement, so a failed save may leave an extra harmless predecessor entry. Snapshot errors are reported but do not cancel the explicit file save.

**Documentation used:**

- [Qt 5.15 QSaveFile](https://doc.qt.io/archives/qt-5.15/qsavefile.html)
- [SHA-256 hashing](https://docs.python.org/3/library/hashlib.html)

### 2. Topic code

#### `code_inteligence/local_history.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Bounded atomic predecessor snapshots keyed by resolved file path."""
import hashlib
import time
from pathlib import Path
from PyQt5.QtCore import QSaveFile, QIODevice

class LocalHistory:
    """Preserve exact disk bytes; keep at most 25 versions and 64 MB per file."""
    def __init__(self, root: Path, keep=25, max_bytes=64_000_000):
        """Validate retention and create only the user-data root."""
        if keep < 1 or max_bytes < 1:
            raise ValueError('History retention must be positive')
        self.root, self.keep, self.max_bytes = Path(root), keep, max_bytes
        self.root.mkdir(parents=True, exist_ok=True)

    def _directory(self, path):
        """Distinguish equal filenames in different projects."""
        return self.root / hashlib.sha256(str(Path(path).resolve()).encode()).hexdigest()

    def record(self, path, data):
        """Deduplicate identical predecessors and commit snapshots atomically."""
        if len(data) > self.max_bytes:
            raise OSError('File exceeds the local-history per-file byte budget')
        versions = self.versions(path)
        if versions and versions[0].read_bytes() == data:
            return versions[0]
        directory = self._directory(path)
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / f'{time.time_ns()}.snapshot'
        output = QSaveFile(str(target))
        if not output.open(QIODevice.WriteOnly):
            raise OSError(output.errorString())
        if output.write(data) != len(data):
            output.cancelWriting()
            raise OSError(output.errorString())
        if not output.commit():
            raise OSError(output.errorString())
        total = 0
        for index, version in enumerate(self.versions(path)):
            total += version.stat().st_size
            if index >= self.keep or total > self.max_bytes:
                version.unlink(missing_ok=True)
        return target

    def versions(self, path):
        """Return newest snapshots first without interpreting their contents."""
        return sorted(self._directory(path).glob('*.snapshot'), reverse=True)
````

| Definition | Responsibility |
|---|---|
| `LocalHistory` | Preserve exact disk bytes; keep at most 25 versions and 64 MB per file. |
| `LocalHistory.__init__` | Validate retention and create only the user-data root. |
| `LocalHistory._directory` | Distinguish equal filenames in different projects. |
| `LocalHistory.record` | Deduplicate identical predecessors and commit snapshots atomically. |
| `LocalHistory.versions` | Return newest snapshots first without interpreting their contents. |

#### `side_bar_widgets/history_dialog.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Browse every retained local version without overwriting a document."""
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QListWidgetItem, QVBoxLayout


class HistoryDialog(QDialog):
    """Select one predecessor snapshot by timestamp and byte count."""

    def __init__(self, versions, parent=None):
        """List newest-first paths supplied by VersionStore, keeping paths as item data."""
        super().__init__(parent)
        self.setWindowTitle("Local file history")
        self.resize(640, 380)
        layout = QVBoxLayout(self)
        self.items = QListWidget(self)
        for path in versions:
            try:
                stamp = datetime.fromtimestamp(int(path.stem.split('-')[0]) / 1_000_000_000)
                label = f"{stamp:%Y-%m-%d %H:%M:%S.%f} — {path.stat().st_size:,} bytes"
            except (ValueError, OSError):
                continue
            item = QListWidgetItem(label, self.items)
            item.setData(Qt.UserRole, path)
        layout.addWidget(self.items)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.items.itemDoubleClicked.connect(lambda _item: self.accept())
        layout.addWidget(buttons)
        self.items.setCurrentRow(0)

    def selected_path(self):
        """Return the selected version or None when no readable entry remains."""
        item = self.items.currentItem()
        return item.data(Qt.UserRole) if item is not None else None
````

| Definition | Responsibility |
|---|---|
| `HistoryDialog` | Select one predecessor snapshot by timestamp and byte count. |
| `HistoryDialog.__init__` | List newest-first paths supplied by VersionStore, keeping paths as item data. |
| `HistoryDialog.selected_path` | Return the selected version or None when no readable entry remains. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _open_local_history(self):
        """Review a selected predecessor and recover it into an independent tab."""
        editor = self.current_editor()
        path = getattr(editor, 'path', None)
        if path is None or self.local_history is None:
            return
        try:
            versions = self.local_history.versions(Path(path))
            if not versions:
                QMessageBox.information(self, 'History', 'No snapshots yet.')
                return
            picker = HistoryDialog(versions, self)
            if picker.exec_() != QDialog.Accepted or picker.selected_path() is None:
                return
            raw = picker.selected_path().read_bytes()
            source = raw.decode('utf-8-sig')
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'History', str(error))
            return
        if ComparisonDialog(editor.text(), source, 'Local history', self).exec_() != QDialog.Accepted:
            return
        previous = self.python_editor_active
        self.python_editor_active = isinstance(editor, PythonEditor)
        try:
            draft = self.new_file()
        finally:
            self.python_editor_active = previous
        draft._utf8_bom = raw.startswith(UTF8_BOM)
        draft.setEolMode(draft.EolWindows if '\r\n' in source else draft.EolMac if '\r' in source else draft.EolUnix)
        draft.setText(source)
        draft.setModified(True)
        self._on_editor_text_changed(draft)
````

| Definition | Responsibility |
|---|---|
| `_open_local_history` | Review a selected predecessor and recover it into an independent tab. |

### 3. Topic implementation — exact files and methods

#### Step 11.1: create `code_inteligence/local_history.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 11.2: create `side_bar_widgets/history_dialog.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 11.3: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_inteligence.local_history import LocalHistory
from side_bar_widgets.history_dialog import HistoryDialog
from side_bar_widgets.comparison_dialog import ComparisonDialog
````

#### Step 11.4: `main.py` — MainWindow.__init__, immediately after init_ui

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.local_history = None
        try:
            self.local_history = LocalHistory(Path(QStandardPaths.writableLocation(
                QStandardPaths.AppLocalDataLocation)) / 'history')
        except OSError as error:
            QMessageBox.warning(self, 'History unavailable', str(error))
````

#### Step 11.5: `main.py` — MainWindow._save_editor_to_path: before temporary save file

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        temporary = None
        try:
````

**NEW**

````python
        if self.local_history is not None and target.is_file():
            try:
                self.local_history.record(target, target.read_bytes())
            except OSError as error:
                self.statusBar().showMessage('History snapshot failed: ' + str(error), 5000)
        temporary = None
        try:
````

#### Step 11.6: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        menu_bar.addAction('Open Local History').triggered.connect(self._open_local_history)
````

#### Step 11.7: `main.py` — MainWindow: add methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _open_local_history(self):
        """Review a selected predecessor and recover it into an independent tab."""
        editor = self.current_editor()
        path = getattr(editor, 'path', None)
        if path is None or self.local_history is None:
            return
        try:
            versions = self.local_history.versions(Path(path))
            if not versions:
                QMessageBox.information(self, 'History', 'No snapshots yet.')
                return
            picker = HistoryDialog(versions, self)
            if picker.exec_() != QDialog.Accepted or picker.selected_path() is None:
                return
            raw = picker.selected_path().read_bytes()
            source = raw.decode('utf-8-sig')
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'History', str(error))
            return
        if ComparisonDialog(editor.text(), source, 'Local history', self).exec_() != QDialog.Accepted:
            return
        previous = self.python_editor_active
        self.python_editor_active = isinstance(editor, PythonEditor)
        try:
            draft = self.new_file()
        finally:
            self.python_editor_active = previous
        draft._utf8_bom = raw.startswith(UTF8_BOM)
        draft.setEolMode(draft.EolWindows if '\r\n' in source else draft.EolMac if '\r' in source else draft.EolUnix)
        draft.setText(source)
        draft.setModified(True)
        self._on_editor_text_changed(draft)

    def current_editor(self):
````

**Using this topic:** Use Open Local History, select a snapshot, review the comparison and choose Open draft to recover without overwriting the source.


---

<a id="topic-12"></a>

## Topic 12: External-change comparison

### 1. Topic explanation

When Save detects a changed disk revision, show explicit Compare, Reload disk, Keep editing, Merge draft and Overwrite choices. A three-way merge uses the last accepted disk text; conflicting edits retain both alternatives in an unsaved draft. Recheck disk bytes after review before permitting overwrite.

**Prerequisites:** Topic 13

**Operational details:** The last-accepted-disk ancestor is recorded when a file is opened or saved with this topic installed. Merge draft is disabled if that ancestor is absent. Rechecking after review narrows the conflict window, but ordinary file replacement is not a cross-process filesystem transaction lock.

**Documentation used:**

- [Python difflib](https://docs.python.org/3/library/difflib.html)
- [Qt 5.15 QMessageBox](https://doc.qt.io/archives/qt-5.15/qmessagebox.html)

### 2. Topic code

#### `code_inteligence/text_comparison.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Read-only text differences and explicit merge drafts."""
from __future__ import annotations
import difflib


def unified_diff(before: str, after: str, left: str, right: str) -> str:
    """Return a readable diff with stable source labels."""
    return "".join(difflib.unified_diff(before.splitlines(keepends=True),
                                        after.splitlines(keepends=True),
                                        fromfile=left, tofile=right))


def three_way(base: str, ours: str, theirs: str) -> tuple[str, bool]:
    """Merge nonoverlapping line edits; retain both alternatives for conflicts.

    The return flag is true only when conflict markers were inserted. Adjacent
    replacements merge independently; insertions at the same boundary conflict
    unless both sides produced identical text. Inputs are never modified.
    """
    if ours == theirs:
        return ours, False
    if ours == base:
        return theirs, False
    if theirs == base:
        return ours, False
    original = base.splitlines(keepends=True)
    changes = []
    for side, text in enumerate((ours, theirs)):
        lines = text.splitlines(keepends=True)
        for tag, a, b, c, d in difflib.SequenceMatcher(None, original, lines, autojunk=False).get_opcodes():
            if tag != "equal":
                changes.append((a, b, side, lines[c:d]))
    changes.sort(key=lambda edit: (edit[0], edit[1], edit[2]))
    output, position, conflict = [], 0, False
    while changes:
        first = changes.pop(0)
        start, end, group = first[0], first[1], [first]
        while changes and (changes[0][0] < end or (
                changes[0][0] == end and (changes[0][0] == changes[0][1] or start == end))):
            change = changes.pop(0)
            end = max(end, change[1])
            group.append(change)
        output.extend(original[position:start])
        variants = []
        for side in (0, 1):
            result, cursor = [], start
            for a, b, owner, replacement in group:
                if owner == side:
                    result.extend(original[cursor:a])
                    result.extend(replacement)
                    cursor = b
            result.extend(original[cursor:end])
            variants.append(''.join(result))
        old = ''.join(original[start:end])
        left, right = variants
        if left == right or right == old:
            output.append(left)
        elif left == old:
            output.append(right)
        else:
            conflict = True
            # Markers always start on their own lines, including no-final-EOL files.
            output.append('<<<<<<< EDITOR\n' + left.rstrip('\n') + '\n=======\n' +
                          right.rstrip('\n') + '\n>>>>>>> DISK\n')
        position = end
    output.extend(original[position:])
    return ''.join(output), conflict
````

| Definition | Responsibility |
|---|---|
| `unified_diff` | Return a readable diff with stable source labels. |
| `three_way` | Merge nonoverlapping line edits; retain both alternatives for conflicts. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _resolve_external_conflict(self, editor, target):
        """Return True only for an explicit overwrite of the reviewed disk bytes."""
        try:
            raw = target.read_bytes()
            theirs = raw.decode('utf-8-sig')
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'External change', str(error))
            return False
        ours = editor.text()
        while True:
            box = QMessageBox(self)
            box.setWindowTitle('File changed on disk')
            box.setText('Choose how to handle the newer disk version.')
            compare = box.addButton('Compare', QMessageBox.ActionRole)
            reload_button = box.addButton('Reload disk', QMessageBox.DestructiveRole)
            merge = box.addButton('Merge draft', QMessageBox.ActionRole)
            overwrite = box.addButton('Overwrite disk', QMessageBox.DestructiveRole)
            keep = box.addButton('Keep editing', QMessageBox.RejectRole)
            box.setDefaultButton(keep)
            merge.setEnabled(isinstance(getattr(editor, '_disk_text', None), str))
            box.exec_()
            chosen = box.clickedButton()
            if chosen is compare:
                ComparisonDialog(ours, theirs, 'Buffer / external version', self, accept_text=None).exec_()
                continue
            if chosen is merge:
                merged, conflicts = three_way(editor._disk_text, ours, theirs)
                previous = self.python_editor_active
                self.python_editor_active = isinstance(editor, PythonEditor)
                try:
                    draft = self.new_file()
                finally:
                    self.python_editor_active = previous
                draft.setText(merged)
                draft.setModified(True)
                self._on_editor_text_changed(draft)
                self.statusBar().showMessage('Merge draft created' + ('; resolve conflict markers before saving' if conflicts else ''), 8000)
                return False
            if chosen not in (reload_button, overwrite):
                return False
            try:
                if target.read_bytes() != raw or editor.text() != ours:
                    QMessageBox.warning(self, 'External change', 'The file or buffer changed during review. Save again to review it.')
                    return False
            except OSError as error:
                QMessageBox.warning(self, 'External change', str(error))
                return False
            if chosen is overwrite:
                return True
            # Reload is explicit and undoable. Track the bytes accepted as the ancestor.
            editor.beginUndoAction()
            try:
                editor.selectAll()
                editor.replaceSelectedText(theirs)
            finally:
                editor.endUndoAction()
            editor._utf8_bom = raw.startswith(UTF8_BOM)
            editor.setEolMode(editor.EolWindows if '\r\n' in theirs else editor.EolMac if '\r' in theirs else editor.EolUnix)
            editor._disk_text = theirs
            editor._disk_digest = hashlib.sha256(raw).digest()
            self.mark_editor_clean(editor)
            return False
````

| Definition | Responsibility |
|---|---|
| `_resolve_external_conflict` | Return True only for an explicit overwrite of the reviewed disk bytes. |

### 3. Topic implementation — exact files and methods

#### Step 12.1: create `code_inteligence/text_comparison.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 12.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_inteligence.text_comparison import three_way
from side_bar_widgets.comparison_dialog import ComparisonDialog
````

#### Step 12.3: `main.py` — MainWindow.set_new_tab: retain the common ancestor

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        editor.setTextSafely(text)
````

**NEW**

````python
        editor.setTextSafely(text)
        editor._disk_text = text
````

#### Step 12.4: `main.py` — MainWindow._save_editor_to_path: successful revision

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        editor._disk_digest = hashlib.sha256(data).digest()
````

**NEW**

````python
        editor._disk_digest = hashlib.sha256(data).digest()
        editor._disk_text = data.decode("utf-8-sig")
````

#### Step 12.5: `main.py` — MainWindow._save_editor_to_path: replace the external-conflict prompt only

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
                reply = QMessageBox.warning(
                    self,
                    "File changed on disk",
                    f"'{logical_path.name}' changed outside the editor.\n"
                    "Overwrite the newer disk version?",
                    QMessageBox.Yes | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                if reply != QMessageBox.Yes:
                    return False
````

**NEW**

````python
                if not self._resolve_external_conflict(editor, target):
                    return False
````

#### Step 12.6: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _resolve_external_conflict(self, editor, target):
        """Return True only for an explicit overwrite of the reviewed disk bytes."""
        try:
            raw = target.read_bytes()
            theirs = raw.decode('utf-8-sig')
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'External change', str(error))
            return False
        ours = editor.text()
        while True:
            box = QMessageBox(self)
            box.setWindowTitle('File changed on disk')
            box.setText('Choose how to handle the newer disk version.')
            compare = box.addButton('Compare', QMessageBox.ActionRole)
            reload_button = box.addButton('Reload disk', QMessageBox.DestructiveRole)
            merge = box.addButton('Merge draft', QMessageBox.ActionRole)
            overwrite = box.addButton('Overwrite disk', QMessageBox.DestructiveRole)
            keep = box.addButton('Keep editing', QMessageBox.RejectRole)
            box.setDefaultButton(keep)
            merge.setEnabled(isinstance(getattr(editor, '_disk_text', None), str))
            box.exec_()
            chosen = box.clickedButton()
            if chosen is compare:
                ComparisonDialog(ours, theirs, 'Buffer / external version', self, accept_text=None).exec_()
                continue
            if chosen is merge:
                merged, conflicts = three_way(editor._disk_text, ours, theirs)
                previous = self.python_editor_active
                self.python_editor_active = isinstance(editor, PythonEditor)
                try:
                    draft = self.new_file()
                finally:
                    self.python_editor_active = previous
                draft.setText(merged)
                draft.setModified(True)
                self._on_editor_text_changed(draft)
                self.statusBar().showMessage('Merge draft created' + ('; resolve conflict markers before saving' if conflicts else ''), 8000)
                return False
            if chosen not in (reload_button, overwrite):
                return False
            try:
                if target.read_bytes() != raw or editor.text() != ours:
                    QMessageBox.warning(self, 'External change', 'The file or buffer changed during review. Save again to review it.')
                    return False
            except OSError as error:
                QMessageBox.warning(self, 'External change', str(error))
                return False
            if chosen is overwrite:
                return True
            # Reload is explicit and undoable. Track the bytes accepted as the ancestor.
            editor.beginUndoAction()
            try:
                editor.selectAll()
                editor.replaceSelectedText(theirs)
            finally:
                editor.endUndoAction()
            editor._utf8_bom = raw.startswith(UTF8_BOM)
            editor.setEolMode(editor.EolWindows if '\r\n' in theirs else editor.EolMac if '\r' in theirs else editor.EolUnix)
            editor._disk_text = theirs
            editor._disk_digest = hashlib.sha256(raw).digest()
            self.mark_editor_clean(editor)
            return False

    def current_editor(self):
````

#### Step 12.7: `main.py` — MainWindow._convert_editor: transfer document metadata

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        new_editor._save_target = getattr(old, "_save_target", path)
````

**NEW**

````python
        new_editor._save_target = getattr(old, "_save_target", path)
        new_editor._disk_text = getattr(old, "_disk_text", None)
````

**Using this topic:** Save a file whose disk revision changed. The conflict dialog presents the explicit choices; Merge draft creates a separate unsaved tab.


---

<a id="topic-14"></a>

## Topic 14: Rename symbol with preview

### 1. Topic explanation

Use Jedi semantic rename instead of replacing every same-spelled token. Plan in an isolated process, show every affected file, reject stale revisions, and apply the accepted changes to editor buffers as per-document undo groups. Save explicitly afterward through the normal atomic save/conflict/history pipeline; no background refactor writes project files.

**Prerequisites:** Topic 13

**Operational details:** This source workflow uses the editor Python (sys.executable) to run the helper with the existing Jedi dependency, and passes the selected project interpreter to Jedi. A frozen executable needs a separately configured Python helper launcher; do not launch the frozen editor executable as if it were Python. The helper rejects module/file moves, non-UTF-8 edits and workspaces beyond its explicit budget. Each affected buffer has its own Undo operation; there is no cross-file transactional Undo.

**Documentation used:**

- [Jedi Script.rename](https://jedi.readthedocs.io/en/latest/docs/api.html#jedi.Script.rename)
- [Jedi refactoring result classes](https://jedi.readthedocs.io/en/latest/docs/api-classes.html#refactoring)
- [Qt 5.15 QProcess](https://doc.qt.io/archives/qt-5.15/qprocess.html)

### 2. Topic code

#### `code_inteligence/rename_worker.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Isolated Jedi rename planner; reads source but never writes project files."""
import json
import keyword
import os
import sys
from pathlib import Path


def plan(request):
    """Capture bounded workspace bytes before asking Jedi for semantic changes."""
    import jedi
    root, path = Path(request['root']).resolve(), Path(request['path']).resolve()
    name = request['name']
    if not name.isidentifier() or keyword.iskeyword(name):
        raise ValueError('Choose a valid non-keyword Python identifier')
    if not path.is_relative_to(root):
        raise ValueError('The source must be inside the workspace')
    snapshots, total = {}, 0
    for folder, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'build', 'dist'} and not (Path(folder) / d).is_symlink()]
        for filename in files:
            item = Path(folder) / filename
            if item.suffix.lower() not in {'.py', '.pyi', '.pyw'} or item.is_symlink():
                continue
            raw = item.read_bytes()
            total += len(raw)
            if len(raw) > 2_000_000 or total > 32_000_000 or len(snapshots) >= 10000:
                raise ValueError('Workspace exceeds the bounded rename budget')
            snapshots[item.resolve()] = raw
    if path not in snapshots:
        raise ValueError('The source is excluded or linked; rename cannot be planned safely')
    source = snapshots[path].decode('utf-8-sig')
    environment = jedi.create_environment(request['interpreter'], safe=False)
    project = jedi.Project(str(root), environment_path=request['interpreter'])
    result = jedi.Script(source, path=path, project=project, environment=environment).rename(
        line=request['line'] + 1, column=request['column'], new_name=name)
    if list(result.get_renames()):
        raise ValueError('File/module moves are not supported by this text-rename command')
    edits = []
    for filename, changed in result.get_changed_files().items():
        target = Path(filename).resolve()
        if target not in snapshots or target.read_bytes() != snapshots[target]:
            raise ValueError('A target changed or lies outside the captured workspace')
        before = snapshots[target].decode('utf-8-sig')
        after = changed.get_new_code()
        eol = '\r\n' if '\r\n' in before else '\r' if '\r' in before else '\n'
        after = after.replace('\r\n', '\n').replace('\r', '\n').replace('\n', eol)
        edits.append({'path': str(target), 'before': before, 'after': after,
                      'bom': snapshots[target].startswith(b'\xef\xbb\xbf')})
    return edits

if __name__ == '__main__':
    try:
        response = {'edits': plan(json.load(sys.stdin))}
    except Exception as error:
        response = {'error': str(error)}
    sys.stdout.write(json.dumps(response, ensure_ascii=True))
````

| Definition | Responsibility |
|---|---|
| `plan` | Capture bounded workspace bytes before asking Jedi for semantic changes. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _rename_symbol_preview(self):
        """Start a read-only semantic plan only from a saved, unchanged workspace."""
        editor = self.current_editor()
        if not isinstance(editor, PythonEditor) or not editor.path:
            return
        if any(e.isModified() for e in self.tab_view.all_editors()):
            QMessageBox.information(self, 'Rename', 'Save or discard modified tabs before planning a workspace rename.')
            return
        if getattr(self, '_rename_process', None) is not None:
            return
        line, column = editor.getCursorPosition()
        name, ok = QInputDialog.getText(self, 'Rename symbol', 'New name:', text=editor.wordAtLineIndex(line, column))
        if not ok:
            return
        request = {'root': str(self._workspace_root), 'path': str(editor.path), 'name': name,
                   'line': line, 'column': column, 'interpreter': str(self.python_runner.interpreter)}
        process = QProcess(self)
        self._rename_process = process
        self._rename_output = bytearray()
        process.setProcessChannelMode(QProcess.SeparateChannels)
        def read():
            """Keep the plan bounded even if a helper fails noisily."""
            self._rename_output.extend(bytes(process.readAllStandardOutput()))
            if len(self._rename_output) > 64_000_000:
                process.kill()
        def finish(code, status):
            """Forget the process before opening modal review dialogs."""
            read()
            payload = bytes(self._rename_output)
            errors = bytes(process.readAllStandardError()).decode('utf-8', 'replace')
            self._rename_process = None
            process.deleteLater()
            if getattr(self, '_close_prompts_complete', False):
                return
            try:
                if code or status != QProcess.NormalExit:
                    raise ValueError(errors or 'Rename planner failed')
                response = json.loads(payload)
                if 'error' in response:
                    raise ValueError(response['error'])
                if str(self._workspace_root) != request['root'] or str(self.python_runner.interpreter) != request['interpreter']:
                    raise ValueError('Workspace or interpreter changed during planning')
                self._review_symbol_rename(response['edits'])
            except (ValueError, KeyError, TypeError, OSError) as error:
                QMessageBox.warning(self, 'Rename', str(error))
        process.readyReadStandardOutput.connect(read)
        process.finished.connect(finish)
        process.errorOccurred.connect(lambda error: finish(-1, QProcess.CrashExit) if error == QProcess.FailedToStart else None)
        # The helper needs Jedi from the editor environment; it analyzes the selected
        # project environment passed in request['interpreter'].
        process.start(sys.executable, [str(Path(__file__).parent / 'code_inteligence' / 'rename_worker.py')])
        process.write(json.dumps(request).encode('utf-8'))
        process.closeWriteChannel()

    def _review_symbol_rename(self, edits):
        """Validate all destinations before mutating any buffer; keep disk untouched."""
        if not edits:
            QMessageBox.information(self, 'Rename', 'No supported semantic changes were found.')
            return
        for edit in edits:
            if ComparisonDialog(edit['before'], edit['after'], edit['path'], self, accept_text='Approve this file').exec_() != QDialog.Accepted:
                return
        targets = []
        for edit in edits:
            path = Path(edit['path'])
            raw = path.read_bytes()
            expected = (UTF8_BOM if edit['bom'] else b'') + edit['before'].encode('utf-8')
            if raw != expected:
                raise ValueError(f'{path.name} changed during review; plan again')
            editor = self.tab_view.find_editor_by_path(path)
            if editor is not None and (editor.isModified() or editor.isReadOnly() or editor.text() != edit['before']):
                raise ValueError(f'{path.name} has a changed or read-only buffer')
            targets.append((edit, editor))
        # Opening clean tabs is reversible. Complete it before applying edits.
        loaded = []
        for edit, editor in targets:
            editor = editor or self.set_new_tab(Path(edit['path']))
            if editor is None or editor.isReadOnly() or editor.text() != edit['before']:
                raise ValueError('A destination could not be opened unchanged')
            loaded.append((edit, editor))
        for edit, editor in loaded:
            editor.beginUndoAction()
            try:
                editor.selectAll()
                editor.replaceSelectedText(edit['after'])
            finally:
                editor.endUndoAction()
        self.statusBar().showMessage('Rename applied to buffers. Review and use Save All; Undo is available in each affected tab.', 10000)
````

| Definition | Responsibility |
|---|---|
| `_rename_symbol_preview` | Start a read-only semantic plan only from a saved, unchanged workspace. |
| `_review_symbol_rename` | Validate all destinations before mutating any buffer; keep disk untouched. |

### 3. Topic implementation — exact files and methods

#### Step 14.1: create `code_inteligence/rename_worker.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 14.2: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        menu_bar.addAction('Rename Symbol with Preview').triggered.connect(self._rename_symbol_preview)
````

#### Step 14.3: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.comparison_dialog import ComparisonDialog
````

#### Step 14.4: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _rename_symbol_preview(self):
        """Start a read-only semantic plan only from a saved, unchanged workspace."""
        editor = self.current_editor()
        if not isinstance(editor, PythonEditor) or not editor.path:
            return
        if any(e.isModified() for e in self.tab_view.all_editors()):
            QMessageBox.information(self, 'Rename', 'Save or discard modified tabs before planning a workspace rename.')
            return
        if getattr(self, '_rename_process', None) is not None:
            return
        line, column = editor.getCursorPosition()
        name, ok = QInputDialog.getText(self, 'Rename symbol', 'New name:', text=editor.wordAtLineIndex(line, column))
        if not ok:
            return
        request = {'root': str(self._workspace_root), 'path': str(editor.path), 'name': name,
                   'line': line, 'column': column, 'interpreter': str(self.python_runner.interpreter)}
        process = QProcess(self)
        self._rename_process = process
        self._rename_output = bytearray()
        process.setProcessChannelMode(QProcess.SeparateChannels)
        def read():
            """Keep the plan bounded even if a helper fails noisily."""
            self._rename_output.extend(bytes(process.readAllStandardOutput()))
            if len(self._rename_output) > 64_000_000:
                process.kill()
        def finish(code, status):
            """Forget the process before opening modal review dialogs."""
            read()
            payload = bytes(self._rename_output)
            errors = bytes(process.readAllStandardError()).decode('utf-8', 'replace')
            self._rename_process = None
            process.deleteLater()
            if getattr(self, '_close_prompts_complete', False):
                return
            try:
                if code or status != QProcess.NormalExit:
                    raise ValueError(errors or 'Rename planner failed')
                response = json.loads(payload)
                if 'error' in response:
                    raise ValueError(response['error'])
                if str(self._workspace_root) != request['root'] or str(self.python_runner.interpreter) != request['interpreter']:
                    raise ValueError('Workspace or interpreter changed during planning')
                self._review_symbol_rename(response['edits'])
            except (ValueError, KeyError, TypeError, OSError) as error:
                QMessageBox.warning(self, 'Rename', str(error))
        process.readyReadStandardOutput.connect(read)
        process.finished.connect(finish)
        process.errorOccurred.connect(lambda error: finish(-1, QProcess.CrashExit) if error == QProcess.FailedToStart else None)
        # The helper needs Jedi from the editor environment; it analyzes the selected
        # project environment passed in request['interpreter'].
        process.start(sys.executable, [str(Path(__file__).parent / 'code_inteligence' / 'rename_worker.py')])
        process.write(json.dumps(request).encode('utf-8'))
        process.closeWriteChannel()

    def _review_symbol_rename(self, edits):
        """Validate all destinations before mutating any buffer; keep disk untouched."""
        if not edits:
            QMessageBox.information(self, 'Rename', 'No supported semantic changes were found.')
            return
        for edit in edits:
            if ComparisonDialog(edit['before'], edit['after'], edit['path'], self, accept_text='Approve this file').exec_() != QDialog.Accepted:
                return
        targets = []
        for edit in edits:
            path = Path(edit['path'])
            raw = path.read_bytes()
            expected = (UTF8_BOM if edit['bom'] else b'') + edit['before'].encode('utf-8')
            if raw != expected:
                raise ValueError(f'{path.name} changed during review; plan again')
            editor = self.tab_view.find_editor_by_path(path)
            if editor is not None and (editor.isModified() or editor.isReadOnly() or editor.text() != edit['before']):
                raise ValueError(f'{path.name} has a changed or read-only buffer')
            targets.append((edit, editor))
        # Opening clean tabs is reversible. Complete it before applying edits.
        loaded = []
        for edit, editor in targets:
            editor = editor or self.set_new_tab(Path(edit['path']))
            if editor is None or editor.isReadOnly() or editor.text() != edit['before']:
                raise ValueError('A destination could not be opened unchanged')
            loaded.append((edit, editor))
        for edit, editor in loaded:
            editor.beginUndoAction()
            try:
                editor.selectAll()
                editor.replaceSelectedText(edit['after'])
            finally:
                editor.endUndoAction()
        self.statusBar().showMessage('Rename applied to buffers. Review and use Save All; Undo is available in each affected tab.', 10000)

    def current_editor(self):
````

#### Step 14.5: `main.py` — MainWindow.closeEvent: stop owned work

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.stop()
````

**NEW**

````python
        process = getattr(self, '_rename_process', None)
        if process is not None:
            process.kill()
        self.terminal.stop()
````

**If Topic 23 is already installed:** the terminal stop is guarded. Insert this topic’s shutdown statements immediately **before** that guard, using:

````python
        process = getattr(self, '_rename_process', None)
        if process is not None:
            process.kill()
        if self.terminal is not None:
            self.terminal.stop()
````

#### Step 14.6: `main.py` — MainWindow._background_work_running: retain worker ownership

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _background_work_running(self) -> bool:
````

**NEW**

````python
    def _background_work_running(self) -> bool:
        process = getattr(self, '_rename_process', None)
        if process is not None and process.state() != QProcess.NotRunning:
            return True
````

**Using this topic:** Save modified tabs, put the caret on a Python symbol and choose Rename Symbol with Preview. Approve each proposed file; the result remains in buffers until you save.


---

<a id="topic-15"></a>

## Topic 15: Workspace symbol search

### 1. Topic explanation

Search Python declarations in the actual workspace root on an owned cancellable worker. Bound file sizes/counts and results, skip linked/environment directories, and reject results after the workspace changes. Results navigate to captured source paths and lines.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Python AST](https://docs.python.org/3/library/ast.html)
- [Qt 5.15 QThread](https://doc.qt.io/archives/qt-5.15/qthread.html)

### 2. Topic code

#### `code_inteligence/workspace_symbols.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Cancellable workspace declaration search without executing user code."""
import ast
import os
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal

class SymbolSearch(QThread):
    """Bound file sizes and report results through a queued Qt signal."""
    found = pyqtSignal(object)

    def __init__(self, root, query, parent=None):
        super().__init__(parent)
        self.root, self.query = Path(root), query.casefold()

    def run(self):
        """Walk directories with pruning; cancellation is checked per file."""
        rows = []
        scanned = 0
        for directory, folders, files in os.walk(self.root, followlinks=False):
            folders[:] = [name for name in folders if name not in
                {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}
                and not (Path(directory) / name).is_symlink()]
            for name in files:
                if self.isInterruptionRequested():
                    return
                path = Path(directory) / name
                if path.suffix.lower() not in {'.py', '.pyw', '.pyi'} or path.is_symlink():
                    continue
                scanned += 1
                if scanned > 10000:
                    self.found.emit((rows, True))
                    return
                try:
                    if path.stat().st_size > 2_000_000:
                        continue
                    tree = ast.parse(path.read_bytes().decode('utf-8-sig'))
                except (OSError, UnicodeError, SyntaxError, RecursionError):
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                        if self.query in node.name.casefold():
                            rows.append((node.name, str(path), node.lineno))
                            if len(rows) >= 200:
                                self.found.emit((rows, True))
                                return
        self.found.emit((rows, False))
````

| Definition | Responsibility |
|---|---|
| `SymbolSearch` | Bound file sizes and report results through a queued Qt signal. |
| `SymbolSearch.run` | Walk directories with pruning; cancellation is checked per file. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _find_workspace_symbols(self):
        """Start one search and retain it until its thread finishes."""
        if getattr(self, '_symbol_job', None) is not None:
            self._symbol_job.requestInterruption()
            return
        query, ok = QInputDialog.getText(self, 'Workspace Symbols', 'Name (invoke again to cancel):')
        if not ok or not query.strip():
            return
        job = SymbolSearch(self._workspace_root, query, self)
        self._symbol_root = self._workspace_root
        self._symbol_job = job
        job.found.connect(self._show_workspace_symbols)
        job.finished.connect(self._symbol_search_finished)
        job.start()

    def _symbol_search_finished(self):
        """Release a finished thread; never destroy a running QThread."""
        self._symbol_job.deleteLater()
        self._symbol_job = None

    def _show_workspace_symbols(self, result):
        """Navigate using the result's file/line, not parsed display text."""
        if getattr(self, '_close_prompts_complete', False) or self._symbol_root != self._workspace_root:
            return
        rows, truncated = result
        if not rows:
            QMessageBox.information(self, 'Symbols', 'No matches in searched UTF-8 Python files.')
            return
        labels = [f'{path}:{line} {name}' for name, path, line in rows]
        choice, ok = QInputDialog.getItem(self, 'Symbols',
            'Results (scan/result limit reached)' if truncated else 'Go to:', labels, 0, False)
        if ok:
            _, path, line = rows[labels.index(choice)]
            self._open_file_at_position(path, line - 1, 0)
````

| Definition | Responsibility |
|---|---|
| `_find_workspace_symbols` | Start one search and retain it until its thread finishes. |
| `_symbol_search_finished` | Release a finished thread; never destroy a running QThread. |
| `_show_workspace_symbols` | Navigate using the result's file/line, not parsed display text. |

### 3. Topic implementation — exact files and methods

#### Step 15.1: create `code_inteligence/workspace_symbols.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 15.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_inteligence.workspace_symbols import SymbolSearch
````

#### Step 15.3: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        menu_bar.addAction('Workspace Symbols').triggered.connect(self._find_workspace_symbols)
````

#### Step 15.4: `main.py` — MainWindow: add methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _find_workspace_symbols(self):
        """Start one search and retain it until its thread finishes."""
        if getattr(self, '_symbol_job', None) is not None:
            self._symbol_job.requestInterruption()
            return
        query, ok = QInputDialog.getText(self, 'Workspace Symbols', 'Name (invoke again to cancel):')
        if not ok or not query.strip():
            return
        job = SymbolSearch(self._workspace_root, query, self)
        self._symbol_root = self._workspace_root
        self._symbol_job = job
        job.found.connect(self._show_workspace_symbols)
        job.finished.connect(self._symbol_search_finished)
        job.start()

    def _symbol_search_finished(self):
        """Release a finished thread; never destroy a running QThread."""
        self._symbol_job.deleteLater()
        self._symbol_job = None

    def _show_workspace_symbols(self, result):
        """Navigate using the result's file/line, not parsed display text."""
        if getattr(self, '_close_prompts_complete', False) or self._symbol_root != self._workspace_root:
            return
        rows, truncated = result
        if not rows:
            QMessageBox.information(self, 'Symbols', 'No matches in searched UTF-8 Python files.')
            return
        labels = [f'{path}:{line} {name}' for name, path, line in rows]
        choice, ok = QInputDialog.getItem(self, 'Symbols',
            'Results (scan/result limit reached)' if truncated else 'Go to:', labels, 0, False)
        if ok:
            _, path, line = rows[labels.index(choice)]
            self._open_file_at_position(path, line - 1, 0)

    def current_editor(self):
````

#### Step 15.5: `main.py` — MainWindow._background_work_running: new thread ownership

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _background_work_running(self) -> bool:
````

**NEW**

````python
    def _background_work_running(self) -> bool:
        if getattr(self, "_symbol_job", None) is not None and self._symbol_job.isRunning():
            return True
````

#### Step 15.6: `main.py` — MainWindow.closeEvent: stop search before existing shutdown

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.stop()
````

**NEW**

````python
        if getattr(self, "_symbol_job", None) is not None:
            self._symbol_job.requestInterruption()
        self.terminal.stop()
````

**If Topic 23 is already installed:** the terminal stop is guarded. Insert this topic’s shutdown statements immediately **before** that guard, using:

````python
        if getattr(self, "_symbol_job", None) is not None:
            self._symbol_job.requestInterruption()
        if self.terminal is not None:
            self.terminal.stop()
````

**Using this topic:** Choose Workspace Symbols and enter a name fragment. Invoke it again during a scan to request cancellation.


---

<a id="topic-16"></a>

## Topic 16: Test runner panel

### 1. Topic explanation

Provide a structured pytest panel: collect exact node IDs, run all/selected tests, rerun failures, inspect phase outcomes and navigate to source. Use a dedicated process, bounded output, explicit Stop and owned shutdown. This implements the requested editor feature; the guide itself adds no automated verification suite.

**Prerequisites:** None; apply directly to the pinned baseline.

**Operational details:** Install pytest in the interpreter selected in the editor: `<selected-python> -m pip install pytest`. The bridge is a normal source file included by package discovery. Collection executes project/conftest code only when you click Collect or Run. Stop controls the immediate pytest process; it does not guarantee termination of arbitrary grandchildren.

**Documentation used:**

- [pytest report and collection hooks](https://docs.pytest.org/en/stable/reference/reference.html)
- [Qt 5.15 QProcess](https://doc.qt.io/archives/qt-5.15/qprocess.html)

### 2. Topic code

#### `python_editor/process_runner.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. If Topic 16 or 17 already created this identical shared module, keep that copy and do not create another.

````python
"""Owned argument-vector processes shared by Tests and named runs."""
from dataclasses import dataclass
from pathlib import Path
import codecs
from PyQt5.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, pyqtSignal

@dataclass(frozen=True)
class RunConfig:
    """One named process launch; env contains explicit overrides only."""

    name: str
    interpreter: str
    script: str
    cwd: str
    arguments: list[str]
    env: dict[str, str]


class ProcessPanel(QObject):
    """Launch a configuration or pytest via one QProcess and stream its output."""

    output = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, parent=None):
        """Connect process signals once; stop it during MainWindow close."""
        super().__init__(parent)
        self.process = QProcess(self)
        self.decoder = codecs.getincrementaldecoder("utf-8")("replace")
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._error)
        self._generation = 0
        self._reported = False

    def _read(self) -> None:
        """Decode incrementally enough for terminal-style test output."""
        self.output.emit(self.decoder.decode(bytes(self.process.readAllStandardOutput())))

    def _on_finished(self, code: int, _status) -> None:
        """Flush an incomplete UTF-8 sequence before publishing exit status."""
        self._read()
        tail = self.decoder.decode(b"", final=True)
        if tail:
            self.output.emit(tail)
        if not self._reported:
            self._reported = True
            self.finished.emit(code)

    def run(self, config: RunConfig) -> None:
        """Launch an explicit interpreter/script/cwd/argv/environment tuple."""
        validate_config(config)
        if self.process.state() != QProcess.NotRunning:
            raise RuntimeError("Another run is active")
        if not Path(config.interpreter).is_file() or not Path(config.cwd).is_dir():
            raise ValueError("Select a valid interpreter and working directory")
        # -m is the deliberate pytest module form. A normal named profile
        # points at a script relative to its declared working directory.
        if config.script != "-m" and not (Path(config.cwd) / config.script).is_file():
            raise ValueError("Select an existing script for this run profile")
        env = QProcessEnvironment.systemEnvironment()
        env.insert('PYTHONIOENCODING', 'utf-8')
        env.insert('PYTHONUNBUFFERED', '1')
        for key, value in config.env.items():
            env.insert(key, value)
        self.process.setProcessEnvironment(env)
        self.process.setWorkingDirectory(config.cwd)
        self.decoder = codecs.getincrementaldecoder("utf-8")("replace")
        # QProcess receives an argument vector. There is no shell to expand
        # quotes, glob characters, or environment variables unexpectedly.
        self._generation += 1
        self._reported = False
        self.process.start(config.interpreter, [config.script, *config.arguments])

    def pytest(self, interpreter: str, root: Path, target: Path | None = None) -> None:
        """Run the whole workspace or one selected test without shell parsing."""
        root = root.resolve()
        # The option vector is passed to QProcess unchanged; shell quoting is
        # neither needed nor safe for untrusted workspace file names.
        args = ["-m", "pytest", "-q", "--tb=short"]
        if target:
            target = target.resolve()
            if not target.is_relative_to(root):
                raise ValueError("Test file lies outside workspace")
            args.append(str(target))
        self.run(RunConfig("pytest", interpreter, args[0], str(root), args[1:], {}))

    def stop(self):
        """Terminate the owned process, forcing exit after two seconds if necessary."""
        if self.process.state() == QProcess.NotRunning:
            return
        generation = self._generation
        self.process.terminate()
        # A delayed kill must never affect a newer process launched in the same panel.
        QTimer.singleShot(2000, lambda: self.process.kill() if self._generation == generation
                          and self.process.state() != QProcess.NotRunning else None)

    def _error(self, error):
        """Report startup errors as completion because QProcess may omit finished."""
        self.output.emit(self.process.errorString() + "\n")
        if error == QProcess.FailedToStart and not self._reported:
            self._reported = True
            self.finished.emit(-1)


def validate_config(config):
    """Reject malformed persisted and edited fields before passing them to QProcess."""
    for name in ("name", "interpreter", "script", "cwd"):
        value = getattr(config, name)
        if not isinstance(value, str) or not value.strip() or "\0" in value:
            raise ValueError(f"{name} must be a nonempty string without NUL")
    if not isinstance(config.arguments, list) or any(not isinstance(arg, str) or "\0" in arg for arg in config.arguments):
        raise ValueError("Arguments must be a JSON list of strings without NUL")
    if not isinstance(config.env, dict) or any(not isinstance(k, str) or not isinstance(v, str)
            or not k or "=" in k or "\0" in k + v for k, v in config.env.items()):
        raise ValueError("Environment requires valid string keys and string values")
````

| Definition | Responsibility |
|---|---|
| `RunConfig` | One named process launch; env contains explicit overrides only. |
| `ProcessPanel` | Launch a configuration or pytest via one QProcess and stream its output. |
| `ProcessPanel.__init__` | Connect process signals once; stop it during MainWindow close. |
| `ProcessPanel._read` | Decode incrementally enough for terminal-style test output. |
| `ProcessPanel._on_finished` | Flush an incomplete UTF-8 sequence before publishing exit status. |
| `ProcessPanel.run` | Launch an explicit interpreter/script/cwd/argv/environment tuple. |
| `ProcessPanel.pytest` | Run the whole workspace or one selected test without shell parsing. |
| `ProcessPanel.stop` | Terminate the owned process, forcing exit after two seconds if necessary. |
| `ProcessPanel._error` | Report startup errors as completion because QProcess may omit finished. |
| `validate_config` | Reject malformed persisted and edited fields before passing them to QProcess. |

#### `python_editor/test_panel.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""A separate test-output dock with traceback navigation."""
from __future__ import annotations
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QDockWidget, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem, QAbstractItemView
from pathlib import Path
import re


class OutputView(QPlainTextEdit):
    """A read-only test log with guarded source navigation."""

    navigate = pyqtSignal(str, int)

    def __init__(self, root: Path, parent=None):
        """Resolve traceback filenames relative to a known workspace root."""
        super().__init__(parent)
        self.root = root.resolve()
        self.setReadOnly(True)
        self.setMaximumBlockCount(10000)

    def mouseDoubleClickEvent(self, event):
        """Open only a real workspace path from a valid pytest location."""
        line = self.cursorForPosition(event.pos()).block().text()
        # A Windows traceback begins with C:\ and may contain spaces. The
        # drive colon is part of the path; only the colon after .py is the
        # location separator.
        match = re.search(
            r"(?P<path>(?:[A-Za-z]:[\\/])?[^:\n]+?\.py):(?P<line>\d+)(?::|\b)",
            line,
        )
        if match:
            target = (self.root / match.group("path").strip()).resolve()
            if target.is_file() and target.is_relative_to(self.root):
                self.navigate.emit(str(target), max(0, int(match.group("line")) - 1))
                event.accept()
                return
        super().mouseDoubleClickEvent(event)


class TestDock(QDockWidget):
    """One reusable panel for test output, run and stop actions."""

    run_requested = pyqtSignal()
    collect_requested = pyqtSignal()
    targets_requested = pyqtSignal(list)
    stop_requested = pyqtSignal()
    navigate = pyqtSignal(str, int)

    def __init__(self, root: Path, parent=None):
        """Make stable objectName available to workspace layout presets."""
        super().__init__("Tests", parent)
        self.setObjectName("TestsDock")
        body = QWidget(self)
        layout = QVBoxLayout(body)
        controls = QHBoxLayout()
        self.run_button, self.stop_button = QPushButton("Run"), QPushButton("Stop")
        self.run_button.clicked.connect(self.run_requested)
        self.stop_button.clicked.connect(self.stop_requested)
        controls.addWidget(self.run_button)
        controls.addWidget(self.stop_button)
        self.collect_button = QPushButton("Collect")
        self.selected_button = QPushButton("Run selected")
        self.failed_button = QPushButton("Rerun failed")
        for button in (self.collect_button, self.selected_button, self.failed_button):
            controls.addWidget(button)
        self.collect_button.clicked.connect(self.collect_requested)
        self.selected_button.clicked.connect(self.run_selected)
        self.failed_button.clicked.connect(lambda: self.targets_requested.emit(sorted(self.failed)))
        layout.addLayout(controls)
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(["Test", "Result", "Seconds"])
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree.itemDoubleClicked.connect(self._navigate_item)
        layout.addWidget(self.tree)
        self.nodes, self.groups, self.failed = {}, {}, set()
        self.output = OutputView(root, body)
        self.output.navigate.connect(self.navigate)
        layout.addWidget(self.output)
        self.state = QLabel("No tests run yet", body)
        layout.addWidget(self.state)
        self.setWidget(body)

    def append(self, text: str) -> None:
        """Stream decoded test output without rebuilding the whole widget."""
        self.output.moveCursor(QTextCursor.End)
        self.output.insertPlainText(text)
        if self.output.document().characterCount() > 1_000_000:
            self.output.setPlainText(self.output.toPlainText()[-500_000:])

    def completed(self, code: int) -> None:
        """Report process status without mistaking all failures for assertions."""
        self.state.setText("Passed" if code == 0 else f"Process exit {code}; inspect output")

    def set_context(self, root, interpreter):
        """Reset collected identities when the workspace or interpreter changes."""
        self.output.root = Path(root).resolve()
        self.tree.clear()
        self.nodes.clear()
        self.groups.clear()
        self.failed.clear()
        self.state.setText("Collect tests for this workspace")

    def run_selected(self):
        """Emit exact node IDs for selected tests or file groups."""
        targets = [item.data(0, Qt.UserRole) for item in self.tree.selectedItems()]
        if targets:
            self.targets_requested.emit(list(dict.fromkeys(targets)))

    def _navigate_item(self, item, column):
        """Open a collected source location only inside the current workspace."""
        location = item.data(0, Qt.UserRole + 1)
        if location:
            path, line = location
            target = (self.output.root / path).resolve()
            if target.is_file() and target.is_relative_to(self.output.root):
                self.navigate.emit(str(target), max(0, line))

    def on_event(self, record):
        """Update collected test identities and phase-aware outcomes from JSON events."""
        event, nodeid = record.get("event"), record.get("nodeid", "")
        if event == "collection_error":
            self.append(record.get("text", "") + "\n")
            self.state.setText("Collection failed; inspect output")
            return
        if event == "collected":
            file = nodeid.split("::", 1)[0]
            if file not in self.groups:
                group = QTreeWidgetItem(self.tree, [file, "", ""])
                group.setData(0, Qt.UserRole, file)
                self.groups[file] = group
            item = self.nodes.get(nodeid)
            if item is None:
                item = QTreeWidgetItem(self.groups[file], [nodeid, "Collected", ""])
                item.setData(0, Qt.UserRole, nodeid)
                self.nodes[nodeid] = item
            item.setData(0, Qt.UserRole + 1, (record.get("path", file), record.get("line", 0)))
            self.tree.expandAll()
        elif event == "result" and nodeid in self.nodes:
            item = self.nodes[nodeid]
            outcome, phase = record["outcome"], record["phase"]
            if outcome == "failed":
                self.failed.add(nodeid)
            elif phase == "setup":
                self.failed.discard(nodeid)
            # A passing teardown must not overwrite a failed call or skipped setup.
            if outcome != "passed" or phase == "call" or phase == "setup":
                if nodeid not in self.failed or outcome == "failed":
                    item.setText(1, ("XFAIL" if record.get("xfail") and outcome == "skipped" else outcome.title()) + " / " + phase)
            item.setText(2, f"{float(record.get('duration', 0)):.3f}")
            if record.get("text"):
                item.setToolTip(1, record["text"])
````

| Definition | Responsibility |
|---|---|
| `OutputView` | A read-only test log with guarded source navigation. |
| `OutputView.__init__` | Resolve traceback filenames relative to a known workspace root. |
| `OutputView.mouseDoubleClickEvent` | Open only a real workspace path from a valid pytest location. |
| `TestDock` | One reusable panel for test output, run and stop actions. |
| `TestDock.__init__` | Make stable objectName available to workspace layout presets. |
| `TestDock.append` | Stream decoded test output without rebuilding the whole widget. |
| `TestDock.completed` | Report process status without mistaking all failures for assertions. |
| `TestDock.set_context` | Reset collected identities when the workspace or interpreter changes. |
| `TestDock.run_selected` | Emit exact node IDs for selected tests or file groups. |
| `TestDock._navigate_item` | Open a collected source location only inside the current workspace. |
| `TestDock.on_event` | Update collected test identities and phase-aware outcomes from JSON events. |

#### `python_editor/test_session.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Separate pytest process and incremental structured-event reader."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from PyQt5.QtCore import QObject, QProcess, QTimer, pyqtSignal
from python_editor.process_runner import ProcessPanel, RunConfig


class TestSession(QObject):
    """Own pytest independently of Run File and named run configurations."""
    event_ready = pyqtSignal(dict)
    output = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, parent=None):
        """Create the child process and one reusable event-poll timer."""
        super().__init__(parent)
        self.runner = ProcessPanel(self)
        self.runner.output.connect(self.output)
        self.runner.finished.connect(self._finished)
        self.timer = QTimer(self)
        self.timer.setInterval(80)
        self.timer.timeout.connect(self._read)
        self.directory, self.path, self.offset, self.partial = None, None, 0, b''
        self.valid = True

    def start(self, interpreter, root, targets=(), *, collect=False):
        """Run exact node IDs, or collect them, without converting them to shell text."""
        if self.is_running():
            raise RuntimeError('A test run is already active')
        if self.directory is not None:
            self.directory.cleanup()
        self.directory = TemporaryDirectory(prefix='markdowneditor-tests-')
        self.path = Path(self.directory.name) / 'events.jsonl'
        self.offset, self.partial = 0, b''
        self.valid = True
        root = Path(root).resolve()
        targets = list(targets)
        for nodeid in targets:
            file = nodeid.split('::', 1)[0]
            if file.startswith('-') or not (root / file).resolve().is_relative_to(root):
                raise ValueError('Test target must be inside the workspace')
        arguments = ['--events', str(self.path), '--', '-q', '--tb=short', '--color=no']
        if collect:
            arguments.append('--collect-only')
        arguments.extend(targets)
        self.runner.run(RunConfig('Tests', interpreter, str(Path(__file__).with_name('pytest_bridge.py')),
                                  str(root), arguments, {'PYTHONIOENCODING': 'utf-8', 'PYTHONUNBUFFERED': '1'}))
        self.timer.start()

    def _read(self):
        """Read only new bytes and retain a partial final JSON record until complete."""
        if not self.valid or self.path is None or not self.path.exists():
            return
        try:
            with self.path.open('rb') as stream:
                stream.seek(self.offset)
                chunk = stream.read()
                self.offset = stream.tell()
        except OSError as error:
            self.output.emit(str(error) + '\n')
            return
        lines = (self.partial + chunk).split(b'\n')
        self.partial = lines.pop()
        for line in lines:
            try:
                record = json.loads(line)
            except (ValueError, UnicodeError):
                continue
            if isinstance(record, dict) and isinstance(record.get('event'), str):
                self.event_ready.emit(record)

    def _finished(self, code):
        """Drain the last records before publishing process completion."""
        self.timer.stop()
        self._read()
        self.finished.emit(code)

    def stop(self):
        """Request termination with ProcessPanel's bounded kill fallback."""
        self.runner.stop()

    def is_running(self):
        """Report actual process lifetime for application shutdown polling."""
        return self.runner.process.state() != QProcess.NotRunning

    def invalidate(self):
        """Stop an old workspace run and discard its pending structured records."""
        self.valid = False
        self.timer.stop()
        self.stop()
````

| Definition | Responsibility |
|---|---|
| `TestSession` | Own pytest independently of Run File and named run configurations. |
| `TestSession.__init__` | Create the child process and one reusable event-poll timer. |
| `TestSession.start` | Run exact node IDs, or collect them, without converting them to shell text. |
| `TestSession._read` | Read only new bytes and retain a partial final JSON record until complete. |
| `TestSession._finished` | Drain the last records before publishing process completion. |
| `TestSession.stop` | Request termination with ProcessPanel's bounded kill fallback. |
| `TestSession.is_running` | Report actual process lifetime for application shutdown polling. |
| `TestSession.invalidate` | Stop an old workspace run and discard its pending structured records. |

#### `python_editor/pytest_bridge.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Run pytest in its selected interpreter and write structured events separately."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


class Reporter:
    """Translate pytest hooks to flushed JSON records without parsing terminal text."""

    def __init__(self, events: Path):
        """Own a fresh event file created by the editor for exactly one run."""
        self.handle = events.open('w', encoding='utf-8')

    def emit(self, kind, **data):
        """Append one complete UTF-8 record so the editor can read incrementally."""
        self.handle.write(json.dumps({'event': kind, **data}, ensure_ascii=False) + '\n')
        self.handle.flush()

    def pytest_collection_finish(self, session):
        """Publish every exact node ID, including parameterized test identities."""
        for item in session.items:
            path, line, _name = item.location
            self.emit('collected', nodeid=item.nodeid, path=str(path), line=line)

    def pytest_collectreport(self, report):
        """Report import/syntax failures separately from failed test assertions."""
        if report.failed:
            self.emit('collection_error', nodeid=report.nodeid, text=str(report.longrepr))

    def pytest_runtest_logreport(self, report):
        """Record setup/call/teardown outcomes, including skips and xfail metadata."""
        self.emit('result', nodeid=report.nodeid, phase=report.when,
                  outcome=report.outcome, duration=report.duration,
                  xfail=str(getattr(report, 'wasxfail', '')),
                  text=str(report.longrepr) if report.longrepr else '')

    def pytest_sessionfinish(self, session, exitstatus):
        """Write the final pytest exit code and close the event stream."""
        self.emit('finished', code=int(exitstatus))
        self.handle.close()


def main():
    """Invoke pytest with unmodified argument-vector entries after editor options."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--events', required=True, type=Path)
    options, arguments = parser.parse_known_args()
    if arguments[:1] == ['--']:
        arguments = arguments[1:]
    import pytest
    return pytest.main(arguments, plugins=[Reporter(options.events)])


if __name__ == '__main__':
    raise SystemExit(main())
````

| Definition | Responsibility |
|---|---|
| `Reporter` | Translate pytest hooks to flushed JSON records without parsing terminal text. |
| `Reporter.__init__` | Own a fresh event file created by the editor for exactly one run. |
| `Reporter.emit` | Append one complete UTF-8 record so the editor can read incrementally. |
| `Reporter.pytest_collection_finish` | Publish every exact node ID, including parameterized test identities. |
| `Reporter.pytest_collectreport` | Report import/syntax failures separately from failed test assertions. |
| `Reporter.pytest_runtest_logreport` | Record setup/call/teardown outcomes, including skips and xfail metadata. |
| `Reporter.pytest_sessionfinish` | Write the final pytest exit code and close the event stream. |
| `main` | Invoke pytest with unmodified argument-vector entries after editor options. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _run_tests(self, checked=False, *, targets=(), collect=False):
        """Use the current project/interpreter and never start over a live process."""
        if self.test_session.is_running():
            QMessageBox.information(self, 'Tests', 'Stop the active test run first.')
            return
        if any(editor.isModified() for editor in self.tab_view.all_editors()):
            answer = QMessageBox.question(self, 'Tests use saved files', 'Continue using the on-disk files?', QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
            if answer != QMessageBox.Yes:
                return
        context = (str(self._workspace_root), str(self.python_runner.interpreter))
        if self._test_context != context:
            self.tests_dock.set_context(*context)
            self._test_context = context
        self.tests_dock.show()
        self.tests_dock.output.clear()
        try:
            self.test_session.start(context[1], context[0], targets, collect=collect)
        except (OSError, ValueError, RuntimeError) as error:
            QMessageBox.warning(self, 'Tests', str(error))
````

| Definition | Responsibility |
|---|---|
| `_run_tests` | Use the current project/interpreter and never start over a live process. |

### 3. Topic implementation — exact files and methods

#### Step 16.1: create `python_editor/process_runner.py`

Use the complete module from section 2. Skip this creation if the identical shared file was already installed by Topic 16 or 17. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 16.2: create `python_editor/test_panel.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 16.3: create `python_editor/test_session.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 16.4: create `python_editor/pytest_bridge.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 16.5: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from python_editor.test_panel import TestDock
from python_editor.test_session import TestSession
````

#### Step 16.6: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.tests_dock = TestDock(self._workspace_root, self)
        self.test_session = TestSession(self)
        self._test_context = None
        self.addDockWidget(Qt.BottomDockWidgetArea, self.tests_dock)
        self.tests_dock.hide()
        self.tests_dock.run_requested.connect(self._run_tests)
        self.tests_dock.collect_requested.connect(lambda: self._run_tests(collect=True))
        self.tests_dock.targets_requested.connect(lambda targets: self._run_tests(targets=targets))
        self.tests_dock.stop_requested.connect(self.test_session.stop)
        self.tests_dock.navigate.connect(lambda path, line: self._open_file_at_position(path, line, 0))
        self.test_session.event_ready.connect(self.tests_dock.on_event)
        self.test_session.output.connect(self.tests_dock.append)
        self.test_session.finished.connect(self.tests_dock.completed)
````

#### Step 16.7: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        menu_bar.addAction('Tests').triggered.connect(lambda: self.tests_dock.show())
````

#### Step 16.8: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _run_tests(self, checked=False, *, targets=(), collect=False):
        """Use the current project/interpreter and never start over a live process."""
        if self.test_session.is_running():
            QMessageBox.information(self, 'Tests', 'Stop the active test run first.')
            return
        if any(editor.isModified() for editor in self.tab_view.all_editors()):
            answer = QMessageBox.question(self, 'Tests use saved files', 'Continue using the on-disk files?', QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
            if answer != QMessageBox.Yes:
                return
        context = (str(self._workspace_root), str(self.python_runner.interpreter))
        if self._test_context != context:
            self.tests_dock.set_context(*context)
            self._test_context = context
        self.tests_dock.show()
        self.tests_dock.output.clear()
        try:
            self.test_session.start(context[1], context[0], targets, collect=collect)
        except (OSError, ValueError, RuntimeError) as error:
            QMessageBox.warning(self, 'Tests', str(error))

    def current_editor(self):
````

#### Step 16.9: `main.py` — MainWindow.closeEvent: stop owned work

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.stop()
````

**NEW**

````python
        self.test_session.invalidate()
        self.terminal.stop()
````

**If Topic 23 is already installed:** the terminal stop is guarded. Insert this topic’s shutdown statements immediately **before** that guard, using:

````python
        self.test_session.invalidate()
        if self.terminal is not None:
            self.terminal.stop()
````

#### Step 16.10: `main.py` — MainWindow._background_work_running: retain worker ownership

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _background_work_running(self) -> bool:
````

**NEW**

````python
    def _background_work_running(self) -> bool:
        if getattr(self, 'test_session', None) is not None and self.test_session.is_running():
            return True
````

#### Step 16.11: `main.py` — MainWindow._restart_ruff: invalidate test context

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        old_client = self.ruff_lsp_client
````

**NEW**

````python
        if getattr(self, "test_session", None) is not None:
            self.test_session.invalidate()
            self._test_context = None
        old_client = self.ruff_lsp_client
````

**Using this topic:** Open Tests. Use Collect, Run, Run selected, Rerun failed or Stop. Double-click a collected item to open its source.


---

<a id="topic-17"></a>

## Topic 17: Run configurations

### 1. Topic explanation

Persist named script, interpreter, working directory, argument-vector and environment settings. Create, edit, delete and run profiles; keep output and Stop separate from the existing Run File process and from Tests. Malformed profiles are reported rather than overwritten. The process_runner.py module is shared with Topic 16; either topic can install it first.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QProcessEnvironment](https://doc.qt.io/archives/qt-5.15/qprocessenvironment.html)
- [Qt 5.15 QProcess](https://doc.qt.io/archives/qt-5.15/qprocess.html)
- [Qt 5.15 QSaveFile](https://doc.qt.io/archives/qt-5.15/qsavefile.html)

### 2. Topic code

#### `python_editor/run_configurations.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Persistent named launch configurations with explicit JSON argv/environment."""
from pathlib import Path
from dataclasses import asdict
import json
from PyQt5.QtCore import QSaveFile, QIODevice
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit
from python_editor.process_runner import RunConfig, validate_config


def atomic_bytes(path, data):
    """Commit a complete settings file or keep its previous bytes on failure."""
    path.parent.mkdir(parents=True, exist_ok=True)
    output = QSaveFile(str(path))
    if not output.open(QIODevice.WriteOnly):
        raise OSError(output.errorString())
    if output.write(data) != len(data):
        output.cancelWriting()
        raise OSError(output.errorString())
    if not output.commit():
        raise OSError(output.errorString())

def load_configs(path: Path) -> list[RunConfig]:
    """Parse user-owned JSON without executing its contents."""
    if not path.is_file():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("Run configurations must be a JSON list")
    configs = [RunConfig(**item) for item in value]
    for config in configs:
        validate_config(config)
    return configs


def save_configs(path: Path, configs: list[RunConfig]) -> None:
    """Atomically persist configurations outside the tracked workspace."""
    atomic_bytes(path, json.dumps([asdict(c) for c in configs], indent=2).encode())


class RunConfigDialog(QDialog):
    """Edit an explicit process launch without involving a shell."""

    def __init__(self, config: RunConfig, parent=None):
        """Populate typed fields from an existing run configuration."""
        super().__init__(parent)
        self.setWindowTitle("Run configuration")
        form = QFormLayout(self)
        self.fields = {}
        for key, value in (("name", config.name), ("interpreter", config.interpreter),
                           ("script", config.script), ("cwd", config.cwd),
                           ("arguments", json.dumps(config.arguments)),
                           ("env", json.dumps(config.env))):
            field = QLineEdit(value, self)
            self.fields[key] = field
            form.addRow(key.title(), field)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def value(self) -> RunConfig:
        """Parse arguments and environment, raising before any process starts."""
        data = {key: field.text() for key, field in self.fields.items()}
        arguments = json.loads(data["arguments"])
        if not isinstance(arguments, list) or any(not isinstance(arg, str) for arg in arguments):
            raise ValueError("Arguments must be a JSON list of strings")
        env = json.loads(data["env"])
        if not isinstance(env, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                                             for k, v in env.items()):
            raise ValueError("Environment must be a JSON object of string values")
        config = RunConfig(data["name"], data["interpreter"], data["script"],
                           data["cwd"], arguments, env)
        validate_config(config)
        return config
````

| Definition | Responsibility |
|---|---|
| `atomic_bytes` | Commit a complete settings file or keep its previous bytes on failure. |
| `load_configs` | Parse user-owned JSON without executing its contents. |
| `save_configs` | Atomically persist configurations outside the tracked workspace. |
| `RunConfigDialog` | Edit an explicit process launch without involving a shell. |
| `RunConfigDialog.__init__` | Populate typed fields from an existing run configuration. |
| `RunConfigDialog.value` | Parse arguments and environment, raising before any process starts. |

#### `python_editor/run_output.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Lazy, read-only output for named run configurations."""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton, QPlainTextEdit


class RunOutputDock(QDockWidget):
    """Show a named process's output without mixing it with pytest results."""
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Build a bounded output view with an explicit Stop button."""
        super().__init__("Run configuration output", parent)
        self.setObjectName("RunConfigurationOutputDock")
        body = QWidget(self)
        layout = QVBoxLayout(body)
        self.stop = QPushButton("Stop", body)
        self.stop.clicked.connect(self.stop_requested)
        self.output = QPlainTextEdit(body)
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(10000)
        layout.addWidget(self.stop)
        layout.addWidget(self.output)
        self.setWidget(body)

    def begin(self, name):
        """Clear previous output and identify the newly requested profile."""
        self.output.clear()
        self.setWindowTitle("Run: " + name)
        self.stop.setEnabled(True)

    def append(self, text):
        """Append streamed text exactly, including partial output lines."""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.output.setTextCursor(cursor)
        if self.output.document().characterCount() > 1_000_000:
            self.output.setPlainText(self.output.toPlainText()[-500_000:])

    def completed(self, code):
        """Display the exit status and disable Stop after process completion."""
        self.append(f"\nProcess exited with code {code}\n")
        self.stop.setEnabled(False)
````

| Definition | Responsibility |
|---|---|
| `RunOutputDock` | Show a named process's output without mixing it with pytest results. |
| `RunOutputDock.__init__` | Build a bounded output view with an explicit Stop button. |
| `RunOutputDock.begin` | Clear previous output and identify the newly requested profile. |
| `RunOutputDock.append` | Append streamed text exactly, including partial output lines. |
| `RunOutputDock.completed` | Display the exit status and disable Stop after process completion. |

#### `python_editor/process_runner.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. If Topic 16 or 17 already created this identical shared module, keep that copy and do not create another.

````python
"""Owned argument-vector processes shared by Tests and named runs."""
from dataclasses import dataclass
from pathlib import Path
import codecs
from PyQt5.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, pyqtSignal

@dataclass(frozen=True)
class RunConfig:
    """One named process launch; env contains explicit overrides only."""

    name: str
    interpreter: str
    script: str
    cwd: str
    arguments: list[str]
    env: dict[str, str]


class ProcessPanel(QObject):
    """Launch a configuration or pytest via one QProcess and stream its output."""

    output = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, parent=None):
        """Connect process signals once; stop it during MainWindow close."""
        super().__init__(parent)
        self.process = QProcess(self)
        self.decoder = codecs.getincrementaldecoder("utf-8")("replace")
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._error)
        self._generation = 0
        self._reported = False

    def _read(self) -> None:
        """Decode incrementally enough for terminal-style test output."""
        self.output.emit(self.decoder.decode(bytes(self.process.readAllStandardOutput())))

    def _on_finished(self, code: int, _status) -> None:
        """Flush an incomplete UTF-8 sequence before publishing exit status."""
        self._read()
        tail = self.decoder.decode(b"", final=True)
        if tail:
            self.output.emit(tail)
        if not self._reported:
            self._reported = True
            self.finished.emit(code)

    def run(self, config: RunConfig) -> None:
        """Launch an explicit interpreter/script/cwd/argv/environment tuple."""
        validate_config(config)
        if self.process.state() != QProcess.NotRunning:
            raise RuntimeError("Another run is active")
        if not Path(config.interpreter).is_file() or not Path(config.cwd).is_dir():
            raise ValueError("Select a valid interpreter and working directory")
        # -m is the deliberate pytest module form. A normal named profile
        # points at a script relative to its declared working directory.
        if config.script != "-m" and not (Path(config.cwd) / config.script).is_file():
            raise ValueError("Select an existing script for this run profile")
        env = QProcessEnvironment.systemEnvironment()
        env.insert('PYTHONIOENCODING', 'utf-8')
        env.insert('PYTHONUNBUFFERED', '1')
        for key, value in config.env.items():
            env.insert(key, value)
        self.process.setProcessEnvironment(env)
        self.process.setWorkingDirectory(config.cwd)
        self.decoder = codecs.getincrementaldecoder("utf-8")("replace")
        # QProcess receives an argument vector. There is no shell to expand
        # quotes, glob characters, or environment variables unexpectedly.
        self._generation += 1
        self._reported = False
        self.process.start(config.interpreter, [config.script, *config.arguments])

    def pytest(self, interpreter: str, root: Path, target: Path | None = None) -> None:
        """Run the whole workspace or one selected test without shell parsing."""
        root = root.resolve()
        # The option vector is passed to QProcess unchanged; shell quoting is
        # neither needed nor safe for untrusted workspace file names.
        args = ["-m", "pytest", "-q", "--tb=short"]
        if target:
            target = target.resolve()
            if not target.is_relative_to(root):
                raise ValueError("Test file lies outside workspace")
            args.append(str(target))
        self.run(RunConfig("pytest", interpreter, args[0], str(root), args[1:], {}))

    def stop(self):
        """Terminate the owned process, forcing exit after two seconds if necessary."""
        if self.process.state() == QProcess.NotRunning:
            return
        generation = self._generation
        self.process.terminate()
        # A delayed kill must never affect a newer process launched in the same panel.
        QTimer.singleShot(2000, lambda: self.process.kill() if self._generation == generation
                          and self.process.state() != QProcess.NotRunning else None)

    def _error(self, error):
        """Report startup errors as completion because QProcess may omit finished."""
        self.output.emit(self.process.errorString() + "\n")
        if error == QProcess.FailedToStart and not self._reported:
            self._reported = True
            self.finished.emit(-1)


def validate_config(config):
    """Reject malformed persisted and edited fields before passing them to QProcess."""
    for name in ("name", "interpreter", "script", "cwd"):
        value = getattr(config, name)
        if not isinstance(value, str) or not value.strip() or "\0" in value:
            raise ValueError(f"{name} must be a nonempty string without NUL")
    if not isinstance(config.arguments, list) or any(not isinstance(arg, str) or "\0" in arg for arg in config.arguments):
        raise ValueError("Arguments must be a JSON list of strings without NUL")
    if not isinstance(config.env, dict) or any(not isinstance(k, str) or not isinstance(v, str)
            or not k or "=" in k or "\0" in k + v for k, v in config.env.items()):
        raise ValueError("Environment requires valid string keys and string values")
````

| Definition | Responsibility |
|---|---|
| `RunConfig` | One named process launch; env contains explicit overrides only. |
| `ProcessPanel` | Launch a configuration or pytest via one QProcess and stream its output. |
| `ProcessPanel.__init__` | Connect process signals once; stop it during MainWindow close. |
| `ProcessPanel._read` | Decode incrementally enough for terminal-style test output. |
| `ProcessPanel._on_finished` | Flush an incomplete UTF-8 sequence before publishing exit status. |
| `ProcessPanel.run` | Launch an explicit interpreter/script/cwd/argv/environment tuple. |
| `ProcessPanel.pytest` | Run the whole workspace or one selected test without shell parsing. |
| `ProcessPanel.stop` | Terminate the owned process, forcing exit after two seconds if necessary. |
| `ProcessPanel._error` | Report startup errors as completion because QProcess may omit finished. |
| `validate_config` | Reject malformed persisted and edited fields before passing them to QProcess. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _profile_path(self):
        """Keep per-user launch settings outside tracked project source."""
        return Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)) / 'run_profiles.json'

    def _edit_run_profile(self):
        """Edit a validated profile; Cancel never modifies the stored file."""
        try:
            profiles = load_configs(self._profile_path())
            labels = ['Create new...'] + [p.name for p in profiles]
            name, ok = QInputDialog.getItem(self, 'Run profiles', 'Choose:', labels, 0, False)
            if not ok:
                return
            index = labels.index(name) - 1
            editor = self.current_editor()
            default = RunConfig('New profile', str(self.python_runner.interpreter), str(getattr(editor, 'path', '') or ''), str(self._workspace_root), [], {})
            if index >= 0:
                action, ok = QInputDialog.getItem(self, 'Profile', 'Action:', ['Edit', 'Delete'], 0, False)
                if not ok:
                    return
                if action == 'Delete':
                    del profiles[index]
                    save_configs(self._profile_path(), profiles)
                    return
                default = profiles[index]
            dialog = RunConfigDialog(default, self)
            if dialog.exec_() != QDialog.Accepted:
                return
            config = dialog.value()
            if any(p.name == config.name for i, p in enumerate(profiles) if i != index):
                raise ValueError('Another profile already uses that name')
            if index >= 0:
                profiles[index] = config
            else:
                profiles.append(config)
            save_configs(self._profile_path(), profiles)
        except (OSError, ValueError, TypeError) as error:
            QMessageBox.warning(self, 'Run profiles', str(error))

    def _run_profile(self):
        """Launch only after explicit selection; use each profile's interpreter."""
        try:
            profiles = load_configs(self._profile_path())
            if not profiles:
                QMessageBox.information(self, 'Run profiles', 'Create a profile first.')
                return
            names = [p.name for p in profiles]
            name, ok = QInputDialog.getItem(self, 'Run profile', 'Choose:', names, 0, False)
            if not ok:
                return
            config = profiles[names.index(name)]
            if self.profile_runner.process.state() != QProcess.NotRunning:
                raise ValueError('Stop the active profile before starting another')
            if any(e.isModified() for e in self.tab_view.all_editors()):
                if QMessageBox.question(self, 'Run uses saved files', 'Continue with on-disk files?', QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel) != QMessageBox.Yes:
                    return
            if self.profile_output is None:
                self.profile_output = RunOutputDock(self)
                self.addDockWidget(Qt.BottomDockWidgetArea, self.profile_output)
                self.profile_output.stop_requested.connect(self.profile_runner.stop)
                self.profile_runner.output.connect(self.profile_output.append)
                self.profile_runner.finished.connect(self.profile_output.completed)
            self.profile_output.begin(config.name)
            self.profile_output.show()
            self.profile_runner.run(config)
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            QMessageBox.warning(self, 'Run profile', str(error))
````

| Definition | Responsibility |
|---|---|
| `_profile_path` | Keep per-user launch settings outside tracked project source. |
| `_edit_run_profile` | Edit a validated profile; Cancel never modifies the stored file. |
| `_run_profile` | Launch only after explicit selection; use each profile's interpreter. |

### 3. Topic implementation — exact files and methods

#### Step 17.1: create `python_editor/run_configurations.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 17.2: create `python_editor/run_output.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 17.3: create `python_editor/process_runner.py`

Use the complete module from section 2. Skip this creation if the identical shared file was already installed by Topic 16 or 17. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 17.4: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from python_editor.process_runner import ProcessPanel, RunConfig
from python_editor.run_configurations import RunConfigDialog, load_configs, save_configs
from python_editor.run_output import RunOutputDock
````

#### Step 17.5: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.profile_runner = ProcessPanel(self)
        self.profile_output = None
````

#### Step 17.6: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        profiles = menu_bar.addMenu('Run Configurations')
        profiles.addAction('Create / Edit / Delete...').triggered.connect(self._edit_run_profile)
        profiles.addAction('Run...').triggered.connect(self._run_profile)
````

#### Step 17.7: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _profile_path(self):
        """Keep per-user launch settings outside tracked project source."""
        return Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)) / 'run_profiles.json'

    def _edit_run_profile(self):
        """Edit a validated profile; Cancel never modifies the stored file."""
        try:
            profiles = load_configs(self._profile_path())
            labels = ['Create new...'] + [p.name for p in profiles]
            name, ok = QInputDialog.getItem(self, 'Run profiles', 'Choose:', labels, 0, False)
            if not ok:
                return
            index = labels.index(name) - 1
            editor = self.current_editor()
            default = RunConfig('New profile', str(self.python_runner.interpreter), str(getattr(editor, 'path', '') or ''), str(self._workspace_root), [], {})
            if index >= 0:
                action, ok = QInputDialog.getItem(self, 'Profile', 'Action:', ['Edit', 'Delete'], 0, False)
                if not ok:
                    return
                if action == 'Delete':
                    del profiles[index]
                    save_configs(self._profile_path(), profiles)
                    return
                default = profiles[index]
            dialog = RunConfigDialog(default, self)
            if dialog.exec_() != QDialog.Accepted:
                return
            config = dialog.value()
            if any(p.name == config.name for i, p in enumerate(profiles) if i != index):
                raise ValueError('Another profile already uses that name')
            if index >= 0:
                profiles[index] = config
            else:
                profiles.append(config)
            save_configs(self._profile_path(), profiles)
        except (OSError, ValueError, TypeError) as error:
            QMessageBox.warning(self, 'Run profiles', str(error))

    def _run_profile(self):
        """Launch only after explicit selection; use each profile's interpreter."""
        try:
            profiles = load_configs(self._profile_path())
            if not profiles:
                QMessageBox.information(self, 'Run profiles', 'Create a profile first.')
                return
            names = [p.name for p in profiles]
            name, ok = QInputDialog.getItem(self, 'Run profile', 'Choose:', names, 0, False)
            if not ok:
                return
            config = profiles[names.index(name)]
            if self.profile_runner.process.state() != QProcess.NotRunning:
                raise ValueError('Stop the active profile before starting another')
            if any(e.isModified() for e in self.tab_view.all_editors()):
                if QMessageBox.question(self, 'Run uses saved files', 'Continue with on-disk files?', QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel) != QMessageBox.Yes:
                    return
            if self.profile_output is None:
                self.profile_output = RunOutputDock(self)
                self.addDockWidget(Qt.BottomDockWidgetArea, self.profile_output)
                self.profile_output.stop_requested.connect(self.profile_runner.stop)
                self.profile_runner.output.connect(self.profile_output.append)
                self.profile_runner.finished.connect(self.profile_output.completed)
            self.profile_output.begin(config.name)
            self.profile_output.show()
            self.profile_runner.run(config)
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            QMessageBox.warning(self, 'Run profile', str(error))

    def current_editor(self):
````

#### Step 17.8: `main.py` — MainWindow.closeEvent: stop owned work

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.stop()
````

**NEW**

````python
        self.profile_runner.stop()
        self.terminal.stop()
````

**If Topic 23 is already installed:** the terminal stop is guarded. Insert this topic’s shutdown statements immediately **before** that guard, using:

````python
        self.profile_runner.stop()
        if self.terminal is not None:
            self.terminal.stop()
````

#### Step 17.9: `main.py` — MainWindow._background_work_running: retain worker ownership

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _background_work_running(self) -> bool:
````

**NEW**

````python
    def _background_work_running(self) -> bool:
        if getattr(self, 'profile_runner', None) is not None and self.profile_runner.process.state() != QProcess.NotRunning:
            return True
````

**Using this topic:** Use Run Configurations → Create / Edit / Delete, then Run. Enter arguments as JSON strings, for example ["--name", "a value with spaces"].


---

<a id="topic-18"></a>

## Topic 18: Configurable keyboard shortcuts

### 1. Topic explanation

Discover the actual static menu actions, preserve their QAction callbacks and stable menu-path IDs, and configure their keyboard shortcuts. Validate exact and prefix collisions against other actions/shortcuts before mutation. Restore the complete saved map together so swapped bindings work; reject invalid saved maps without partial changes.

**Prerequisites:** None; apply directly to the pinned baseline.

**Operational details:** This registry configures menu QActions and checks Qt shortcut collisions. It does not rewrite every internal Scintilla key binding. IDs based on menu paths remain stable while those static labels remain unchanged. Dynamic Open Recent entries are deliberately excluded.

**Documentation used:**

- [Qt 5.15 QAction](https://doc.qt.io/archives/qt-5.15/qaction.html)
- [Qt 5.15 QKeySequence](https://doc.qt.io/archives/qt-5.15/qkeysequence.html)

### 2. Topic code

#### `code_settings/shortcuts.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Stable action IDs and a small shortcut editor."""
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QMenu, QShortcut, QInputDialog, QMessageBox

class ShortcutManager(QObject):
    """Register real actions before restoring overrides; do not duplicate them."""
    def __init__(self, window, actions):
        super().__init__(window)
        self.window, self.actions = window, actions
        desired = {key: str(window.settings.value('shortcuts_v2/' + key, action.shortcut().toString(QKeySequence.PortableText))) for key, action in actions.items()}
        try:
            parsed = {key: QKeySequence(value, QKeySequence.PortableText) for key, value in desired.items()}
            nonempty = [(key, value) for key, value in parsed.items() if not value.isEmpty()]
            for index, (key, value) in enumerate(nonempty):
                if any(value.matches(other) != QKeySequence.NoMatch or other.matches(value) != QKeySequence.NoMatch for _, other in nonempty[index+1:]):
                    raise ValueError('Saved shortcuts conflict; defaults retained')
            for key, value in parsed.items():
                if desired[key].strip() and value.isEmpty():
                    raise ValueError('Invalid saved shortcut; defaults retained')
            for key, value in parsed.items():
                actions[key].setShortcut(value)
        except ValueError as error:
            window.statusBar().showMessage(str(error), 6000)

    @staticmethod
    def discover(menu_bar):
        """Use existing actions; exclude dynamic recent-file entries."""
        found = {}
        def visit(menu, prefix):
            """Create stable IDs from static menu paths, not object addresses."""
            for action in menu.actions():
                if action.isSeparator():
                    continue
                text = action.text().replace('&', '').strip()
                key = prefix + '/' + text
                child = action.menu()
                if child is not None:
                    if text != 'Open Recent':
                        visit(child, key)
                elif text:
                    command = action.objectName() or key
                    found[command] = action
        visit(menu_bar, '')
        return found

    def assign(self, key, text, persist=True):
        """Reject exact or prefix conflicts across application actions."""
        sequence = QKeySequence(text, QKeySequence.PortableText)
        if text.strip() and sequence.isEmpty():
            raise ValueError('Invalid key sequence')
        target = self.actions[key]
        sequences = []
        for action in self.window.findChildren(QAction):
            if action is not target:
                sequences.extend(action.shortcuts())
        sequences.extend(item.key() for item in self.window.findChildren(QShortcut))
        if not sequence.isEmpty():
            for other in sequences:
                if not other.isEmpty() and (sequence.matches(other) != QKeySequence.NoMatch
                        or other.matches(sequence) != QKeySequence.NoMatch):
                    raise ValueError('Shortcut conflicts with an existing command')
        target.setShortcut(sequence)
        if persist:
            self.window.settings.setValue('shortcuts_v2/' + key,
                sequence.toString(QKeySequence.PortableText))

    def edit(self):
        """Choose an action and a portable Qt key sequence."""
        key, ok = QInputDialog.getItem(self.window, 'Shortcuts', 'Command:',
                                      sorted(self.actions), 0, False)
        if not ok:
            return
        text, ok = QInputDialog.getText(self.window, 'Shortcut', 'Sequence (blank removes):',
            text=self.actions[key].shortcut().toString(QKeySequence.PortableText))
        if ok:
            try:
                self.assign(key, text)
            except ValueError as error:
                QMessageBox.warning(self.window, 'Shortcut', str(error))
````

| Definition | Responsibility |
|---|---|
| `ShortcutManager` | Register real actions before restoring overrides; do not duplicate them. |
| `ShortcutManager.discover` | Use existing actions; exclude dynamic recent-file entries. |
| `ShortcutManager.assign` | Reject exact or prefix conflicts across application actions. |
| `ShortcutManager.edit` | Choose an action and a portable Qt key sequence. |

### 3. Topic implementation — exact files and methods

#### Step 18.1: create `code_settings/shortcuts.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 18.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_settings.shortcuts import ShortcutManager
````

#### Step 18.3: `main.py` — MainWindow.__init__, immediately after init_ui

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.shortcut_manager = ShortcutManager(self, ShortcutManager.discover(self.menuBar()))
        self.menuBar().addAction('Configure Shortcuts').triggered.connect(self.shortcut_manager.edit)
````

**Using this topic:** Choose Configure Shortcuts. Select a real menu command and enter a portable Qt sequence; a blank value removes the QAction shortcut.


---

<a id="topic-19"></a>

## Topic 19: Smarter pair handling

### 1. Topic explanation

Provide selection wrapping, matching delimiters, closer overtyping and empty-pair Backspace in both editors. Work with Scintilla UTF-8 byte positions and only neighboring bytes/selected text, avoiding a full-document copy per key. Conservatively defer inside Python strings/comments, escaped quotes, words, completions and multi-selections.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Scintilla editing and byte positions](https://www.scintilla.org/ScintillaDoc.html)
- [QScintilla editor API](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)

### 2. Topic code

#### `code_inteligence/pair_handling.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Byte-safe, narrowly scoped QScintilla pair edits."""
from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciScintilla as S

PAIRS = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'", '`': '`'}

def handle_pair(editor, event):
    """Return True only when this handler consumes an ordinary typing event."""
    if editor.isReadOnly() or event.modifiers() & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier):
        return False
    if editor.SendScintilla(S.SCI_AUTOCACTIVE):
        return False
    a = editor.SendScintilla(S.SCI_GETSELECTIONSTART)
    b = editor.SendScintilla(S.SCI_GETSELECTIONEND)
    pos = editor.SendScintilla(S.SCI_GETCURRENTPOS)
    if editor.SendScintilla(S.SCI_GETSELECTIONS) != 1:
        return False
    left_byte = editor.SendScintilla(S.SCI_GETCHARAT, pos - 1) if pos else 0
    right_byte = editor.SendScintilla(S.SCI_GETCHARAT, pos)
    before = bytes([left_byte]) if left_byte else b''
    after = bytes([right_byte]) if right_byte else b''
    typed = event.text()
    replacement = None
    caret = a
    if event.key() == Qt.Key_Backspace and a == b and before:
        left = before.decode('ascii', errors='ignore')
        if left in PAIRS and after == PAIRS[left].encode():
            a, b, replacement, caret = pos-1, pos+1, '', pos-1
    elif typed and typed in PAIRS.values() and a == b and after == typed.encode():
        editor.SendScintilla(S.SCI_SETSEL, pos+1, pos+1)
        return True
    elif typed and typed in PAIRS:
        if typed in "'\"`" and a == b and before and (before.isalnum() or before == b'\\'):
            return False
        if a == b and getattr(editor, 'is_python_file', False):
            lexer = editor.lexer()
            style = editor.SendScintilla(S.SCI_GETSTYLEAT, max(0, pos - 1))
            if lexer is None or style in (getattr(lexer, 'STRING', 3), getattr(lexer, 'COMMENTS', 6), getattr(lexer, 'DOCSTRING', 27)):
                return False
        selected = editor.selectedText()
        replacement = typed + selected + PAIRS[typed]
        caret = a + len((typed + selected).encode('utf-8'))
    if replacement is None:
        return False
    editor.beginUndoAction()
    try:
        editor.SendScintilla(S.SCI_SETSEL, a, b)
        editor.replaceSelectedText(replacement)
        editor.SendScintilla(S.SCI_SETSEL, caret, caret)
    finally:
        editor.endUndoAction()
    return True
````

| Definition | Responsibility |
|---|---|
| `handle_pair` | Return True only when this handler consumes an ordinary typing event. |

### 3. Topic implementation — exact files and methods

#### Step 19.1: create `code_inteligence/pair_handling.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 19.2: `markdown_editor/markdowneditor.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_editor.markdowncustomlexer import MarkdownCustomLexer
````

**NEW**

````python
from markdown_editor.markdowncustomlexer import MarkdownCustomLexer
from code_inteligence.pair_handling import handle_pair
````

#### Step 19.3: `markdown_editor/markdowneditor.py` — MarkdownEditor.keyPressEvent

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_Space:
            self.autoCompleteFromAll()
        else:
            return super().keyPressEvent(e)
````

**NEW**

````python
    def keyPressEvent(self, e: QKeyEvent) -> None:
        """Preserve completion shortcuts and delegate ordinary pair input."""
        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Space:
            self.autoCompleteFromAll()
        elif not handle_pair(self, e):
            super().keyPressEvent(e)
````

#### Step 19.4: `python_editor/pythoneditor.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from code_inteligence.indentation_helper import indentation_for_new_line
````

**NEW**

````python
from code_inteligence.indentation_helper import indentation_for_new_line
from code_inteligence.pair_handling import handle_pair
````

#### Step 19.5: `python_editor/pythoneditor.py` — PythonEditor.keyPressEvent

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def keyPressEvent(self, event: QKeyEvent) -> None:
            """Handle editor shortcuts, indentation, and signature scheduling."""
            # Do this before early returns for completion acceptance/indentation.
            if self.is_python_file and event.key() in (
                    Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape):
                self._dismiss_signature()

            if event.key() == Qt.Key.Key_F12:
                self.goto_definition()
                return

            if (
                    event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and event.key() == Qt.Key.Key_Space
                    and self.is_python_file
            ):
                line, column = self.getCursorPosition()
                self._manual_completion_generation = self.auto_completer.get_completions(
                    line + 1,
                    column,
                    self.text(),
                )
                return

            if (
                    event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and event.key() == Qt.Key.Key_X
                    and not self.hasSelectedText()
            ):
                line, _column = self.getCursorPosition()
                self.setSelection(line, 0, line, self.lineLength(line))
                self.cut()
                return

            if (
                    event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and self.SendScintilla(SCI_AUTOCACTIVE)
            ):
                return super().keyPressEvent(event)

            if (
                    self.is_python_file
                    and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and event.modifiers() == Qt.KeyboardModifier.NoModifier
                    and not self.hasSelectedText()
            ):
                self._handle_python_return()
                return

            if event.text() == "(" and self.is_python_file and not self._shutting_down:
                line, column = self.getCursorPosition()
                before = self.text(line)[:column]
                if self._has_callable_before_parenthesis(before):
                    # Let the base handler insert '(' first. The delayed lookup then
                    # sees the cursor/source state Jedi expects.
                    self._signature_timer.start()

            return super().keyPressEvent(event)
````

**NEW**

````python
    def keyPressEvent(self, event: QKeyEvent) -> None:
            """Handle editor shortcuts, indentation, and signature scheduling."""
            # Do this before early returns for completion acceptance/indentation.
            if self.is_python_file and event.key() in (
                    Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape):
                self._dismiss_signature()

            if event.key() == Qt.Key.Key_F12:
                self.goto_definition()
                return

            if (
                    event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and event.key() == Qt.Key.Key_Space
                    and self.is_python_file
            ):
                line, column = self.getCursorPosition()
                self._manual_completion_generation = self.auto_completer.get_completions(
                    line + 1,
                    column,
                    self.text(),
                )
                return

            if (
                    event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and event.key() == Qt.Key.Key_X
                    and not self.hasSelectedText()
            ):
                line, _column = self.getCursorPosition()
                self.setSelection(line, 0, line, self.lineLength(line))
                self.cut()
                return

            if (
                    event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and self.SendScintilla(SCI_AUTOCACTIVE)
            ):
                return super().keyPressEvent(event)

            if (
                    self.is_python_file
                    and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and event.modifiers() == Qt.KeyboardModifier.NoModifier
                    and not self.hasSelectedText()
            ):
                self._handle_python_return()
                return

            if event.text() == "(" and self.is_python_file and not self._shutting_down:
                line, column = self.getCursorPosition()
                before = self.text(line)[:column]
                if self._has_callable_before_parenthesis(before):
                    # Let the base handler insert '(' first. The delayed lookup then
                    # sees the cursor/source state Jedi expects.
                    self._signature_timer.start()

            if handle_pair(self, event):
                return
            return super().keyPressEvent(event)
````

**Using this topic:** Type a bracket/quote, wrap a selection or press Backspace between an empty pair. Undo groups preserve a complete pair edit.


---

<a id="topic-20"></a>

## Topic 20: Outline and navigation

### 1. Topic explanation

Populate the actual outline tree with nested Python declarations and Markdown headings recognized by the same Python-Markdown configuration as preview. Navigation retains source line numbers; fenced examples do not become headings. Keep the existing symbol_clicked signal and replace all direct Python-only refresh paths.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Python-Markdown tree processors](https://python-markdown.github.io/extensions/api/)
- [TOC IDs](https://python-markdown.github.io/extensions/toc/)
- [Python AST](https://docs.python.org/3/library/ast.html)

### 2. Topic code

#### `code_inteligence/outline_parsers.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Plain immutable outline rows: (depth, label, zero-based line, column)."""
import ast
import re

def python_outline(text):
    """Return nested declarations without executing the source."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError):
        return ()
    rows = []
    def walk(node, depth):
        for child in ast.iter_child_nodes(node):
            declaration = isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            if declaration:
                kind = 'class' if isinstance(child, ast.ClassDef) else 'def'
                # Jump to line start: AST columns are UTF-8 bytes, not QScintilla indices.
                rows.append((depth, f'{kind} {child.name}', child.lineno-1, 0))
            walk(child, depth + int(declaration))
    walk(tree, 0)
    return tuple(rows)

def markdown_outline(text):
    """Use the preview dialect and return exact source heading destinations."""
    from markdown_editor.document_model import parse_headings
    return tuple((h.level - 1, h.title, h.line, 0) for h in parse_headings(text))
````

| Definition | Responsibility |
|---|---|
| `python_outline` | Return nested declarations without executing the source. |
| `markdown_outline` | Use the preview dialect and return exact source heading destinations. |

#### `side_bar_widgets/document_outline.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""An extended tree retaining the baseline symbol_clicked contract."""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem
from side_bar_widgets.code_outline import CodeOutlineTree
from code_inteligence.outline_parsers import python_outline, markdown_outline

class DocumentOutline(CodeOutlineTree):
    """Consume plain rows, keeping widgets out of parsing and caches."""
    def update_document(self, text, python):
        """Parse according to the actual editor type."""
        rows = python_outline(text) if python else markdown_outline(text)
        self.update_rows(rows)

    def update_rows(self, rows):
        """Rebuild hierarchy; source positions remain immutable item data."""
        self.clear()
        stack = []
        for depth, label, line, column in rows:
            while stack and stack[-1][0] >= depth:
                stack.pop()
            parent = stack[-1][1] if stack else self
            item = QTreeWidgetItem(parent, [label])
            item.setData(0, Qt.UserRole, (line, column))
            stack.append((depth, item))
        self.expandAll()
````

| Definition | Responsibility |
|---|---|
| `DocumentOutline` | Consume plain rows, keeping widgets out of parsing and caches. |
| `DocumentOutline.update_document` | Parse according to the actual editor type. |
| `DocumentOutline.update_rows` | Rebuild hierarchy; source positions remain immutable item data. |

#### `markdown_editor/document_model.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Use the application's actual Python-Markdown dialect for headings and links."""
from __future__ import annotations
from dataclasses import dataclass
from html.parser import HTMLParser
import re
import uuid
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

EXTENSIONS = ['extra', 'codehilite', 'toc', 'sane_lists', 'nl2br', 'admonition', 'smarty', 'meta']


@dataclass(frozen=True)
class Heading:
    """A rendered heading with its exact source line and final preview anchor."""
    level: int
    title: str
    line: int
    slug: str


class SourceLines(Treeprocessor):
    """Remove temporary source markers before TOC generates heading IDs."""

    def __init__(self, md, pattern):
        """Retain a unique marker pattern belonging to one parse."""
        super().__init__(md)
        self.pattern = pattern

    def run(self, root):
        """Attach source lines only to nodes the real parser recognized as headings."""
        for heading in root.iter():
            if heading.tag not in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
                continue
            for node in heading.iter():
                for attribute in ('text', 'tail'):
                    value = getattr(node, attribute)
                    if value:
                        match = self.pattern.search(value)
                        if match:
                            heading.set('data-source-line', match.group(1))
                            setattr(node, attribute, self.pattern.sub('', value))


class CollectHeadings(Treeprocessor):
    """Read IDs after the built-in TOC processor has resolved duplicate headings."""

    def run(self, root):
        """Capture only mapped source headings; generated TOC headings are excluded."""
        self.md.source_headings = [
            Heading(int(node.tag[1]), ''.join(node.itertext()),
                    int(node.get('data-source-line')), node.get('id', ''))
            for node in root.iter()
            if node.tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'} and node.get('data-source-line') is not None
        ]


class SourceMap(Extension):
    """Install source tracking around the standard inline and TOC processors."""

    def __init__(self, pattern):
        """Keep the marker regex without altering Markdown extension configuration."""
        super().__init__()
        self.pattern = pattern

    def extendMarkdown(self, md):
        """Remove markers after inline parsing and collect final IDs after TOC."""
        md.treeprocessors.register(SourceLines(md, self.pattern), 'source-lines', 15)
        md.treeprocessors.register(CollectHeadings(md), 'source-headings', 1)


def renderer():
    """Create the same configured renderer used by the editor preview."""
    return markdown.Markdown(extensions=EXTENSIONS)


def parse_headings(source: str) -> list[Heading]:
    """Map ATX/setext headings while letting the real parser reject code examples.

    Temporary private markers carry line numbers into parsed headings. They are
    removed before slug generation. This analysis copy is never shown in preview.
    """
    identity = uuid.uuid4().hex
    pattern = re.compile('\ue000' + identity + r':(\d+)\ue001')
    lines = source.splitlines()
    marked = list(lines)
    prefix = r'(?:[ \t]*>[ \t]*)*[ \t]*(?:(?:[-+*]|\d+\.)[ \t]+)?'
    for number, line in enumerate(lines):
        atx = re.match(r'^(' + prefix + r'#{1,6}[ \t]*)', line)
        if atx:
            cut = atx.end()
            marked[number] = line[:cut] + f'\ue000{identity}:{number}\ue001' + line[cut:]
        elif (number and lines[number - 1].strip()
              and not re.match(r"^[ \t]*(?:`{3,}|~{3,}|<)", lines[number - 1])
              and re.fullmatch(prefix + r"(?:=+|-+)[ \t]*", line)):
            # Mark the preceding text, preserving indentation and quote prefixes.
            previous = marked[number - 1]
            if not pattern.search(previous):
                leading = re.match(r'^' + prefix, previous).end()
                marked[number - 1] = previous[:leading] + f'\ue000{identity}:{number - 1}\ue001' + previous[leading:]
    md = markdown.Markdown(extensions=[*EXTENSIONS, SourceMap(pattern)])
    md.convert('\n'.join(marked))
    return md.source_headings


class LinkCollector(HTMLParser):
    """Read links and image destinations after Markdown grammar has been resolved."""

    def __init__(self):
        """Initialize a parser that decodes HTML entities in attribute values."""
        super().__init__(convert_charrefs=True)
        self.links = []

    def handle_starttag(self, tag, attrs):
        """Collect destinations from real anchor/image elements, including references."""
        attribute = 'href' if tag == 'a' else 'src' if tag == 'img' else None
        if attribute:
            value = dict(attrs).get(attribute)
            if value is not None:
                self.links.append(value)


def rendered_links(source):
    """Return parsed destinations, including nested parentheses and reference links."""
    parser = LinkCollector()
    parser.feed(renderer().convert(source))
    return list(dict.fromkeys(parser.links))
````

| Definition | Responsibility |
|---|---|
| `Heading` | A rendered heading with its exact source line and final preview anchor. |
| `SourceLines` | Remove temporary source markers before TOC generates heading IDs. |
| `SourceLines.__init__` | Retain a unique marker pattern belonging to one parse. |
| `SourceLines.run` | Attach source lines only to nodes the real parser recognized as headings. |
| `CollectHeadings` | Read IDs after the built-in TOC processor has resolved duplicate headings. |
| `CollectHeadings.run` | Capture only mapped source headings; generated TOC headings are excluded. |
| `SourceMap` | Install source tracking around the standard inline and TOC processors. |
| `SourceMap.__init__` | Keep the marker regex without altering Markdown extension configuration. |
| `SourceMap.extendMarkdown` | Remove markers after inline parsing and collect final IDs after TOC. |
| `renderer` | Create the same configured renderer used by the editor preview. |
| `parse_headings` | Map ATX/setext headings while letting the real parser reject code examples. |
| `LinkCollector` | Read links and image destinations after Markdown grammar has been resolved. |
| `LinkCollector.__init__` | Initialize a parser that decodes HTML entities in attribute values. |
| `LinkCollector.handle_starttag` | Collect destinations from real anchor/image elements, including references. |
| `rendered_links` | Return parsed destinations, including nested parentheses and reference links. |

### 3. Topic implementation — exact files and methods

#### Step 20.1: create `code_inteligence/outline_parsers.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 20.2: create `side_bar_widgets/document_outline.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 20.3: create `markdown_editor/document_model.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 20.4: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.document_outline import DocumentOutline
````

#### Step 20.5: `main.py` — MainWindow.set_up_body

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.outline_tree = CodeOutlineTree()
````

**NEW**

````python
        self.outline_tree = DocumentOutline()
````

#### Step 20.6: `main.py` — MainWindow._update_outline

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _update_outline(self):
        editor = self.current_editor()
        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
````

**NEW**

````python
    def _update_outline(self):
        """Refresh both supported document types and clear stale rows."""
        editor = self.current_editor()
        if editor is None:
            self.outline_tree.clear()
        else:
            self.outline_tree.update_document(editor.text(), isinstance(editor, PythonEditor))
````

#### Step 20.7: `main.py` — MainWindow.set_new_tab AND _on_current_editor_changed (two identical blocks)

Apply to both named methods. If an earlier topic already changed this exact block to NEW, keep NEW and skip this repeated routing edit.

**OLD**

````python
        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.outline_tree.clear()
````

**NEW**

````python
        self._update_outline()
````

**Using this topic:** Open Outline and switch between Python and Markdown tabs. Activate a row to navigate to its stored source line.


---

<a id="topic-21"></a>

## Topic 21: Authoring tools

### 1. Topic explanation

Provide TOC insertion, heading links, tables from JSON rows, relative file/image links, checkbox toggling and local-link validation. Derive heading anchors and links from the preview dialect, preserve undo grouping and EOL mode, and retain the HTML sanitizer with only heading id attributes added.

**Prerequisites:** Topic 20

**Documentation used:**

- [Python-Markdown TOC](https://python-markdown.github.io/extensions/toc/)
- [URL parsing and quoting](https://docs.python.org/3/library/urllib.parse.html)
- [Bleach allowlists](https://bleach.readthedocs.io/en/latest/clean.html)

### 2. Topic code

#### `code_inteligence/markdown_authoring.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Authoring transforms aligned with the existing preview renderer."""
import re
import markdown

def make_toc(text):
    """Use the same Markdown extensions as MainWindow, including duplicate IDs."""
    parser = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'sane_lists',
        'nl2br', 'admonition', 'smarty', 'meta'])
    parser.convert(text)
    rows = []
    def walk(tokens, depth=0):
        for item in tokens:
            label = ''.join(chr(92) + ch if ch in (chr(92), '[', ']') else ch for ch in item['name'])
            rows.append('  '*depth + f"- [{label}](#{item['id']})")
            walk(item['children'], depth+1)
    walk(parser.toc_tokens)
    return '\n'.join(rows)

def toggle_checkbox(line):
    """Change only the leading task marker, preserving the rest of the line."""
    return re.sub(r'^(\s*[-*+]\s+)\[([ xX])\]',
        lambda match: match[1] + ('[x]' if match[2] == ' ' else '[ ]'), line, count=1)
````

| Definition | Responsibility |
|---|---|
| `make_toc` | Use the same Markdown extensions as MainWindow, including duplicate IDs. |
| `toggle_checkbox` | Change only the leading task marker, preserving the rest of the line. |

#### `markdown_editor/authoring_tools.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Markdown table and relative-link helpers."""
from __future__ import annotations
from pathlib import Path
import os
import re
import html


def table(rows: list[list[str]]) -> str:
    """Make a pipe table, escaping pipes and preserving explicit cell counts."""
    if not rows or not rows[0]:
        raise ValueError("A table needs a header row")
    width = len(rows[0])
    def row(values):
        """Escape Markdown separators inside each cell."""
        if len(values) != width:
            raise ValueError("Every row needs the same number of columns")
        # A literal cell pipe must not create an extra Markdown column.
        return "| " + " | ".join(html.escape(str(value)).replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("|", r"\|") for value in values) + " |"
    return "\n".join([row(rows[0]), row(["---"] * width),
                      *(row(values) for values in rows[1:])])


def relative_link(document: Path, target: Path, *, image: bool = False, alt: str = "") -> str:
    """Create a portable, URL-escaped Markdown link relative to a document."""
    from urllib.parse import quote
    # Markdown moves with the document; cwd may be another folder entirely.
    relative = os.path.relpath(target.resolve(), document.resolve().parent)
    url = quote(Path(relative).as_posix(), safe="/.-_~")
    label = (alt or target.stem).replace("[", r"\[").replace("]", r"\]")
    return f"{'!' if image else ''}[{label}]({url})"


def broken_local_links(document: Path, text: str) -> list[tuple[int, str]]:
    """Check renderer-resolved local paths and Markdown heading fragments.

    A line number of zero means the rendered destination has no unique source
    location (for example a reused reference). The UI displays its URL directly.
    Remote schemes are never fetched by this local validation command.
    """
    from urllib.parse import unquote, urlsplit
    from markdown_editor.document_model import rendered_links, parse_headings
    bad = []
    current = {heading.slug for heading in parse_headings(text)}
    for value in rendered_links(text):
        parts = urlsplit(value)
        if parts.scheme or parts.netloc:
            continue
        path = document.parent / unquote(parts.path) if parts.path else document
        if parts.path and not path.exists():
            bad.append((0, value))
            continue
        if parts.fragment:
            if not parts.path:
                ids = current
            elif path.suffix.lower() in {".md", ".markdown"} and path.is_file():
                try:
                    ids = {h.slug for h in parse_headings(path.read_text(encoding="utf-8-sig"))}
                except (OSError, UnicodeError):
                    bad.append((0, value))
                    continue
            else:
                continue
            if unquote(parts.fragment) not in ids:
                bad.append((0, value))
    return bad
````

| Definition | Responsibility |
|---|---|
| `table` | Make a pipe table, escaping pipes and preserving explicit cell counts. |
| `relative_link` | Create a portable, URL-escaped Markdown link relative to a document. |
| `broken_local_links` | Check renderer-resolved local paths and Markdown heading fragments. |

#### `markdown_editor/heading_navigation.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Heading navigation and TOCs using the same anchors as the actual preview."""
from markdown_editor.document_model import Heading, parse_headings


def markdown_headings(text: str) -> list[Heading]:
    """Return real rendered ATX/setext headings with zero-based source positions."""
    return parse_headings(text)


def heading_link(source: str, line: int) -> str:
    """Create a link to an exact source heading using its final preview ID."""
    for heading in markdown_headings(source):
        if heading.line == line:
            title = heading.title.replace('[', r'\[').replace(']', r'\]')
            return f'[{title}](#{heading.slug})'
    raise ValueError('No heading at selected line')


def toc(source: str) -> str:
    """Build a heading list in one parse using the actual preview's anchor IDs."""
    lines = []
    for heading in markdown_headings(source):
        title = heading.title.replace("[", r"\[").replace("]", r"\]")
        lines.append("  " * (heading.level - 1) + f"- [{title}](#{heading.slug})")
    return "\n".join(lines)
````

| Definition | Responsibility |
|---|---|
| `markdown_headings` | Return real rendered ATX/setext headings with zero-based source positions. |
| `heading_link` | Create a link to an exact source heading using its final preview ID. |
| `toc` | Build a heading list in one parse using the actual preview's anchor IDs. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _insert_toc(self):
        """Insert at the caret with the current document's EOL convention."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        eol = {QsciScintilla.EolWindows: '\r\n', QsciScintilla.EolUnix: '\n',
               QsciScintilla.EolMac: '\r'}[editor.eolMode()]
        text = make_toc(editor.text()).replace('\n', eol)
        if text:
            editor.beginUndoAction()
            try:
                editor.replaceSelectedText(text + eol)
            finally:
                editor.endUndoAction()

    def _toggle_checkbox(self):
        """Select only the current line's text; retain its newline bytes."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        line, column = editor.getCursorPosition()
        old = editor.text(line).rstrip('\r\n')
        new = toggle_checkbox(old)
        if new != old:
            start = editor.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, line)
            editor.beginUndoAction()
            try:
                editor.SendScintilla(QsciScintilla.SCI_SETSEL, start, start + len(old.encode('utf-8')))
                editor.replaceSelectedText(new)
                editor.setCursorPosition(line, column)
            finally:
                editor.endUndoAction()
````

| Definition | Responsibility |
|---|---|
| `_insert_toc` | Insert at the caret with the current document's EOL convention. |
| `_toggle_checkbox` | Select only the current line's text; retain its newline bytes. |

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _insert_markdown_text(self, text):
        """Replace the selection as one undoable edit using this tab's EOL mode."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or editor.isReadOnly():
            return
        eol = {editor.EolWindows: '\r\n', editor.EolUnix: '\n', editor.EolMac: '\r'}[editor.eolMode()]
        editor.beginUndoAction()
        try:
            editor.replaceSelectedText(text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', eol))
        finally:
            editor.endUndoAction()

    def _insert_markdown_table(self):
        """Validate rectangular JSON rows before inserting a Markdown table."""
        text, ok = QInputDialog.getMultiLineText(self, 'Table', 'JSON rows; first row is the header:', '[["Name", "Value"], ["Example", "1"]]')
        if not ok:
            return
        try:
            rows = json.loads(text)
            if not isinstance(rows, list) or not all(isinstance(row, list) for row in rows):
                raise ValueError('Use a JSON list of rows')
            self._insert_markdown_text(table(rows) + '\n')
        except (TypeError, ValueError) as error:
            QMessageBox.warning(self, 'Table', str(error))

    def _insert_markdown_link(self, image):
        """Create a relative URL only after a document has a real location."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or not editor.path:
            QMessageBox.information(self, 'Link', 'Save a Markdown document first.')
            return
        path, _ = QFileDialog.getOpenFileName(self, 'Choose image' if image else 'Choose file')
        if path:
            try:
                self._insert_markdown_text(relative_link(Path(editor.path), Path(path), image=image))
            except (OSError, ValueError) as error:
                QMessageBox.warning(self, 'Link', str(error))

    def _insert_heading_link(self):
        """Select a rendered heading; duplicate labels keep separate source targets."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        source = editor.text()
        headings = markdown_headings(source)
        labels = [f'{h.title} (line {h.line + 1})' for h in headings]
        if not labels:
            return
        choice, ok = QInputDialog.getItem(self, 'Heading link', 'Heading:', labels, 0, False)
        if ok:
            self._insert_markdown_text(heading_link(source, headings[labels.index(choice)].line))

    def _check_local_links(self):
        """Validate local paths/fragments without making any network request."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or not editor.path:
            return
        try:
            bad = broken_local_links(Path(editor.path), editor.text())
            QMessageBox.information(self, 'Local links', '\n'.join(url for _, url in bad) or 'No broken local destinations found.')
        except (ValueError, OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'Local links', str(error))
````

| Definition | Responsibility |
|---|---|
| `_insert_markdown_text` | Replace the selection as one undoable edit using this tab's EOL mode. |
| `_insert_markdown_table` | Validate rectangular JSON rows before inserting a Markdown table. |
| `_insert_markdown_link` | Create a relative URL only after a document has a real location. |
| `_insert_heading_link` | Select a rendered heading; duplicate labels keep separate source targets. |
| `_check_local_links` | Validate local paths/fragments without making any network request. |

### 3. Topic implementation — exact files and methods

#### Step 21.1: create `code_inteligence/markdown_authoring.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 21.2: create `markdown_editor/authoring_tools.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 21.3: create `markdown_editor/heading_navigation.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 21.4: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_inteligence.markdown_authoring import make_toc, toggle_checkbox
````

#### Step 21.5: `main.py` — module-level MARKDOWN_ALLOWED_ATTRIBUTES

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    "a": ["href", "title"],
````

**NEW**

````python
    "a": ["href", "title"],
    **{f"h{level}": ["id"] for level in range(1, 7)},
````

#### Step 21.6: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        authoring = menu_bar.addMenu('Markdown Tools')
        authoring.addAction('Insert TOC').triggered.connect(self._insert_toc)
        authoring.addAction('Toggle Checkbox').triggered.connect(self._toggle_checkbox)
````

#### Step 21.7: `main.py` — MainWindow: add methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _insert_toc(self):
        """Insert at the caret with the current document's EOL convention."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        eol = {QsciScintilla.EolWindows: '\r\n', QsciScintilla.EolUnix: '\n',
               QsciScintilla.EolMac: '\r'}[editor.eolMode()]
        text = make_toc(editor.text()).replace('\n', eol)
        if text:
            editor.beginUndoAction()
            try:
                editor.replaceSelectedText(text + eol)
            finally:
                editor.endUndoAction()

    def _toggle_checkbox(self):
        """Select only the current line's text; retain its newline bytes."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        line, column = editor.getCursorPosition()
        old = editor.text(line).rstrip('\r\n')
        new = toggle_checkbox(old)
        if new != old:
            start = editor.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, line)
            editor.beginUndoAction()
            try:
                editor.SendScintilla(QsciScintilla.SCI_SETSEL, start, start + len(old.encode('utf-8')))
                editor.replaceSelectedText(new)
                editor.setCursorPosition(line, column)
            finally:
                editor.endUndoAction()

    def current_editor(self):
````

#### Step 21.8: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from markdown_editor.authoring_tools import table, relative_link, broken_local_links
from markdown_editor.heading_navigation import heading_link, markdown_headings
````

#### Step 21.9: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        extra_authoring = menu_bar.addMenu('Markdown Insert')
        extra_authoring.addAction('Table...').triggered.connect(self._insert_markdown_table)
        extra_authoring.addAction('File Link...').triggered.connect(lambda: self._insert_markdown_link(False))
        extra_authoring.addAction('Image Link...').triggered.connect(lambda: self._insert_markdown_link(True))
        extra_authoring.addAction('Heading Link...').triggered.connect(self._insert_heading_link)
        extra_authoring.addAction('Check Local Links').triggered.connect(self._check_local_links)
````

#### Step 21.10: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _insert_markdown_text(self, text):
        """Replace the selection as one undoable edit using this tab's EOL mode."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or editor.isReadOnly():
            return
        eol = {editor.EolWindows: '\r\n', editor.EolUnix: '\n', editor.EolMac: '\r'}[editor.eolMode()]
        editor.beginUndoAction()
        try:
            editor.replaceSelectedText(text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', eol))
        finally:
            editor.endUndoAction()

    def _insert_markdown_table(self):
        """Validate rectangular JSON rows before inserting a Markdown table."""
        text, ok = QInputDialog.getMultiLineText(self, 'Table', 'JSON rows; first row is the header:', '[["Name", "Value"], ["Example", "1"]]')
        if not ok:
            return
        try:
            rows = json.loads(text)
            if not isinstance(rows, list) or not all(isinstance(row, list) for row in rows):
                raise ValueError('Use a JSON list of rows')
            self._insert_markdown_text(table(rows) + '\n')
        except (TypeError, ValueError) as error:
            QMessageBox.warning(self, 'Table', str(error))

    def _insert_markdown_link(self, image):
        """Create a relative URL only after a document has a real location."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or not editor.path:
            QMessageBox.information(self, 'Link', 'Save a Markdown document first.')
            return
        path, _ = QFileDialog.getOpenFileName(self, 'Choose image' if image else 'Choose file')
        if path:
            try:
                self._insert_markdown_text(relative_link(Path(editor.path), Path(path), image=image))
            except (OSError, ValueError) as error:
                QMessageBox.warning(self, 'Link', str(error))

    def _insert_heading_link(self):
        """Select a rendered heading; duplicate labels keep separate source targets."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        source = editor.text()
        headings = markdown_headings(source)
        labels = [f'{h.title} (line {h.line + 1})' for h in headings]
        if not labels:
            return
        choice, ok = QInputDialog.getItem(self, 'Heading link', 'Heading:', labels, 0, False)
        if ok:
            self._insert_markdown_text(heading_link(source, headings[labels.index(choice)].line))

    def _check_local_links(self):
        """Validate local paths/fragments without making any network request."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or not editor.path:
            return
        try:
            bad = broken_local_links(Path(editor.path), editor.text())
            QMessageBox.information(self, 'Local links', '\n'.join(url for _, url in bad) or 'No broken local destinations found.')
        except (ValueError, OSError, UnicodeError) as error:
            QMessageBox.warning(self, 'Local links', str(error))

    def current_editor(self):
````

**Using this topic:** Use Markdown Tools and Markdown Insert. Save the Markdown file before creating relative file/image links or checking local destinations.


---

<a id="topic-22"></a>

## Topic 22: Performance diagnostics mode

### 1. Topic explanation

Measure sanitized Markdown conversion duration only while enabled; keep the last 500 samples and expose a report command. This measures CPU-side conversion, not Chromium painting.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Python performance clock](https://docs.python.org/3/library/time.html#time.perf_counter)

### 2. Topic code

#### `code_inteligence/performance.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Opt-in timing measurements."""
import logging
import time
from contextlib import contextmanager

LOGGER = logging.getLogger('markdown_editor.performance')

class PerformanceMonitor:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.samples = []

    @contextmanager
    def measure(self, operation: str):
        if not self.enabled:
            yield
            return
        start = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self.samples.append((operation, duration_ms))
            self.samples = self.samples[-500:]
            LOGGER.debug('%s took %.1f ms', operation, duration_ms)
````

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _timing_report(self):
        """Display a bounded timing sample summary without changing logging setup."""
        samples = self.performance.samples
        text = '\n'.join(f'{name}: {ms:.2f} ms' for name, ms in samples[-30:])
        QMessageBox.information(self, 'Timing report', text or 'No samples. Enable diagnostics and edit Markdown.')
````

| Definition | Responsibility |
|---|---|
| `_timing_report` | Display a bounded timing sample summary without changing logging setup. |

### 3. Topic implementation — exact files and methods

#### Step 22.1: create `code_inteligence/performance.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 22.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_inteligence.performance import PerformanceMonitor
````

#### Step 22.3: `main.py` — MainWindow.__init__: before Markdown renderer

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.md = markdown.Markdown(
````

**NEW**

````python
        self.performance = PerformanceMonitor(False)
        self.md = markdown.Markdown(
````

#### Step 22.4: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        perf = menu_bar.addAction('Performance Diagnostics')
        perf.setCheckable(True)
        perf.toggled.connect(lambda on: setattr(self.performance, 'enabled', on))
        menu_bar.addAction('Timing Report').triggered.connect(self._timing_report)
````

#### Step 22.5: `main.py` — MainWindow: add methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _timing_report(self):
        """Display a bounded timing sample summary without changing logging setup."""
        samples = self.performance.samples
        text = '\n'.join(f'{name}: {ms:.2f} ms' for name, ms in samples[-30:])
        QMessageBox.information(self, 'Timing report', text or 'No samples. Enable diagnostics and edit Markdown.')

    def current_editor(self):
````

#### Step 22.6: `main.py` — MainWindow.render_preview

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        safe_body = self._render_markdown_safely(editor.text())
````

**NEW**

````python
        with self.performance.measure("markdown_preview"):
            safe_body = self._render_markdown_safely(editor.text())
````

**Using this topic:** Enable Performance Diagnostics, edit Markdown and open Timing Report. Topic 25 also records Python-lexer durations when both are installed.


---

<a id="topic-23"></a>

## Topic 23: Lazy initialization

### 1. Topic explanation

Defer expensive Console and Terminal bodies until their stable dock shells first appear. Reuse each body thereafter; every Run action still shows the console before launching. Project changes remember the latest terminal directory without starting a hidden PTY. The named run-output dock in Topic 17 is already lazy.

**Prerequisites:** None; apply directly to the pinned baseline.

**Operational details:** This chapter defers Console and Terminal. Tests remains eager in Topic 16, and named Run output is already lazy in Topic 17. The existing Ruff service still starts normally.

**Documentation used:**

- [Qt 5.15 QDockWidget](https://doc.qt.io/archives/qt-5.15/qdockwidget.html)
- [Qt 5.15 QWidget](https://doc.qt.io/archives/qt-5.15/qwidget.html)

### 2. Topic code

#### `side_bar_widgets/deferred_dock.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Construct expensive terminal/console widgets only when their dock first shows."""
from PyQt5.QtWidgets import QDockWidget


class DeferredDock(QDockWidget):
    """Keep a cheap stable dock shell so saved layouts can restore before construction."""

    def __init__(self, title, name, factory, parent=None):
        """Store a factory; no child process or expensive body is created yet."""
        super().__init__(title, parent)
        self.setObjectName(name)
        self.factory, self.body = factory, None
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)

    def ensure(self):
        """Create and parent exactly one body, preserving it across later hide/show cycles."""
        if self.body is None:
            self.body = self.factory()
            self.setWidget(self.body)
        return self.body

    def showEvent(self, event):
        """Construct the body before Qt paints a newly visible dock."""
        self.ensure()
        super().showEvent(event)
````

| Definition | Responsibility |
|---|---|
| `DeferredDock` | Keep a cheap stable dock shell so saved layouts can restore before construction. |
| `DeferredDock.__init__` | Store a factory; no child process or expensive body is created yet. |
| `DeferredDock.ensure` | Create and parent exactly one body, preserving it across later hide/show cycles. |
| `DeferredDock.showEvent` | Construct the body before Qt paints a newly visible dock. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _make_console_body(self):
        """Construct and connect one console only when it is first requested."""
        self.console = ConsoleWidget(self.python_runner, self)
        self.console.run_btn.clicked.connect(self.run_current_file)
        return self.console

    def _make_terminal_body(self):
        """Start the terminal in the most recently selected project directory."""
        self.terminal = TerminalWidget(parent=self, working_directory=self._terminal_directory)
        return self.terminal
````

| Definition | Responsibility |
|---|---|
| `_make_console_body` | Construct and connect one console only when it is first requested. |
| `_make_terminal_body` | Start the terminal in the most recently selected project directory. |

### 3. Topic implementation — exact files and methods

#### Step 23.1: create `side_bar_widgets/deferred_dock.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 23.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.deferred_dock import DeferredDock
````

#### Step 23.3: `main.py` — MainWindow.set_up_console_dock

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def set_up_console_dock(self):
        """Create the bottom console panel."""
        self.console = ConsoleWidget(self.python_runner, self)
        self.console.run_btn.clicked.connect(self.run_current_file)

        dock = QDockWidget("Python Console", self)
        dock.setWidget(self.console)
        dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

        dock.hide()
        self.console_dock = dock
        
        terminal_directory = (self._workspace_root if hasattr(sys, "_MEIPASS") else self.file_manager.current_folder or self._workspace_root)
        
        # Terminal (new)
        self.terminal = TerminalWidget(parent=self, working_directory=terminal_directory)
        t_dock = QDockWidget("Terminal", self)
        t_dock.setWidget(self.terminal)
        t_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.BottomDockWidgetArea, t_dock)

        t_dock.hide()
        self.terminal_dock = t_dock
        # Menu shortcuts, Run, and the dock close button must update the icons too;
        dock.visibilityChanged.connect(lambda visible: self._set_sidebar_icon("console", visible))
        t_dock.visibilityChanged.connect(lambda visible: self._set_sidebar_icon("terminal", visible))
````

**NEW**

````python
    def set_up_console_dock(self):
        """Create stable cheap dock shells; factories own expensive bodies."""
        self.console = None
        self.terminal = None
        self._terminal_directory = self._workspace_root if hasattr(sys, '_MEIPASS') else self.file_manager.current_folder or self._workspace_root
        self.console_dock = DeferredDock('Python Console', 'ConsoleDock', self._make_console_body, self)
        self.terminal_dock = DeferredDock('Terminal', 'TerminalDock', self._make_terminal_body, self)
        for dock in (self.console_dock, self.terminal_dock):
            self.addDockWidget(Qt.BottomDockWidgetArea, dock)
            dock.hide()
        self.console_dock.visibilityChanged.connect(lambda visible: self._set_sidebar_icon('console', visible))
        self.terminal_dock.visibilityChanged.connect(lambda visible: self._set_sidebar_icon('terminal', visible))
````

#### Step 23.4: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _make_console_body(self):
        """Construct and connect one console only when it is first requested."""
        self.console = ConsoleWidget(self.python_runner, self)
        self.console.run_btn.clicked.connect(self.run_current_file)
        return self.console

    def _make_terminal_body(self):
        """Start the terminal in the most recently selected project directory."""
        self.terminal = TerminalWidget(parent=self, working_directory=self._terminal_directory)
        return self.terminal

    def current_editor(self):
````

#### Step 23.5: `main.py` — MainWindow.open_folder: do not create a hidden terminal

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.set_working_directory(selected, restart=True)
````

**NEW**

````python
        self._terminal_directory = selected
        if self.terminal is not None:
            self.terminal.set_working_directory(selected, restart=True)
````

#### Step 23.6: `main.py` — MainWindow.closeEvent: optional terminal

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.stop()
````

**NEW**

````python
        if self.terminal is not None:
            self.terminal.stop()
````

**Using this topic:** Console and Terminal are constructed on first opening. Normal Run commands show the console before execution.


---

<a id="topic-24"></a>

## Topic 24: Background file hashing

### 1. Topic explanation

Watch open file paths and their parent directories, rearm watches after atomic replacement, and hash changed files in a cancellable worker. Keep only the latest queued path per editor, reject results after save/rename/close, and mark external changes without replacing the accepted save-time digest.

**Prerequisites:** None; apply directly to the pinned baseline.

**Operational details:** File notifications are hints: parent-directory watches cover atomic replacement, but platform watch limits still apply. The explicit Check Disk Change action remains available, and the existing synchronous save-time digest remains authoritative.

**Documentation used:**

- [Qt 5.15 QFileSystemWatcher](https://doc.qt.io/archives/qt-5.15/qfilesystemwatcher.html)
- [Qt 5.15 QThread](https://doc.qt.io/archives/qt-5.15/qthread.html)
- [Python hashlib](https://docs.python.org/3/library/hashlib.html)

### 2. Topic code

#### `code_inteligence/file_hash_worker.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Cancellable streaming digest job; never access Qt widgets in run()."""
import hashlib
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal

class HashJob(QThread):
    """Own one immutable path and emit digest/error in one result signal."""
    result = pyqtSignal(object)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = Path(path)

    def run(self):
        """Read bounded chunks and reject a file changed during the read."""
        try:
            before = self.path.stat()
            digest = hashlib.sha256()
            with self.path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''):
                    if self.isInterruptionRequested():
                        return
                    digest.update(block)
            after = self.path.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                raise OSError('File changed while hashing; retry')
            self.result.emit((digest.digest(), None))
        except OSError as error:
            self.result.emit((None, str(error)))
````

| Definition | Responsibility |
|---|---|
| `HashJob` | Own one immutable path and emit digest/error in one result signal. |
| `HashJob.run` | Read bounded chunks and reject a file changed during the read. |

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _check_disk_async(self):
        """Start one read-only job, capturing the accepted revision at dispatch."""
        if getattr(self, '_hash_job', None) is not None:
            return
        editor = self.current_editor()
        path = getattr(editor, 'path', None)
        if path is None:
            return
        job = HashJob(path, self)
        self._hash_job = job
        self._hash_context = (editor, str(path), getattr(editor, '_disk_digest', None))
        job.result.connect(self._disk_hash_result)
        job.finished.connect(self._hash_finished)
        job.start()

    def _disk_hash_result(self, result):
        """Ignore results from tabs saved, renamed or closed during the read."""
        editor, path, expected = self._hash_context
        if editor not in self.tab_view.all_editors():
            return
        if str(editor.path) != path or getattr(editor, '_disk_digest', None) != expected:
            return
        digest, error = result
        editor._external_change_hint = bool(error or digest != expected)
        message = error or ('File changed on disk' if digest != expected else 'Disk version unchanged')
        self.statusBar().showMessage(message, 5000)

    def _hash_finished(self):
        """Release both success and failure jobs after the thread exits."""
        self._hash_job.deleteLater()
        self._hash_job = None
        self._hash_context = None
        QTimer.singleShot(0, self._next_disk_hash)
````

| Definition | Responsibility |
|---|---|
| `_check_disk_async` | Start one read-only job, capturing the accepted revision at dispatch. |
| `_disk_hash_result` | Ignore results from tabs saved, renamed or closed during the read. |
| `_hash_finished` | Release both success and failure jobs after the thread exits. |

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _sync_disk_watches(self):
        """Rearm replaced files and remove retired paths without hashing every tick."""
        editors = [e for e in self.tab_view.all_editors() if getattr(e, 'path', None)]
        files = {str(Path(e.path).absolute()) for e in editors}
        directories = {str(Path(p).parent) for p in files}
        existing = set(self._disk_watch.files()) | set(self._disk_watch.directories())
        wanted = files | directories
        removed = existing - wanted
        if removed:
            self._disk_watch.removePaths(sorted(removed))
        added = [p for p in wanted - existing if Path(p).exists()]
        if added:
            self._disk_watch.addPaths(added)
        self._disk_pending = {e: p for e, p in self._disk_pending.items() if e in editors}
        self._next_disk_hash()

    def _queue_disk_path(self, path):
        """Coalesce a file notification by editor identity."""
        for editor in self.tab_view.all_editors():
            if getattr(editor, 'path', None) and str(Path(editor.path).absolute()) == path:
                self._disk_pending[editor] = path
        self._next_disk_hash()

    def _queue_disk_directory(self, directory):
        """Directory watches catch delete/recreate and atomic replacement."""
        for editor in self.tab_view.all_editors():
            if getattr(editor, 'path', None) and str(Path(editor.path).absolute().parent) == directory:
                self._disk_pending[editor] = str(Path(editor.path).absolute())
        self._next_disk_hash()

    def _next_disk_hash(self):
        """Run one queued immutable path at a time and retain worker ownership."""
        if getattr(self, '_close_prompts_complete', False) or getattr(self, '_hash_job', None) is not None or not self._disk_pending:
            return
        editor = next(iter(self._disk_pending))
        path = self._disk_pending.pop(editor)
        if editor not in self.tab_view.all_editors():
            return
        job = HashJob(path, self)
        self._hash_job = job
        self._hash_context = (editor, str(editor.path), getattr(editor, '_disk_digest', None))
        job.result.connect(self._disk_hash_result)
        job.finished.connect(self._hash_finished)
        job.start()
````

| Definition | Responsibility |
|---|---|
| `_sync_disk_watches` | Rearm replaced files and remove retired paths without hashing every tick. |
| `_queue_disk_path` | Coalesce a file notification by editor identity. |
| `_queue_disk_directory` | Directory watches catch delete/recreate and atomic replacement. |
| `_next_disk_hash` | Run one queued immutable path at a time and retain worker ownership. |

### 3. Topic implementation — exact files and methods

#### Step 24.1: create `code_inteligence/file_hash_worker.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 24.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_inteligence.file_hash_worker import HashJob
````

#### Step 24.3: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        menu_bar.addAction('Check Disk Change').triggered.connect(self._check_disk_async)
````

#### Step 24.4: `main.py` — MainWindow: add methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _check_disk_async(self):
        """Start one read-only job, capturing the accepted revision at dispatch."""
        if getattr(self, '_hash_job', None) is not None:
            return
        editor = self.current_editor()
        path = getattr(editor, 'path', None)
        if path is None:
            return
        job = HashJob(path, self)
        self._hash_job = job
        self._hash_context = (editor, str(path), getattr(editor, '_disk_digest', None))
        job.result.connect(self._disk_hash_result)
        job.finished.connect(self._hash_finished)
        job.start()

    def _disk_hash_result(self, result):
        """Ignore results from tabs saved, renamed or closed during the read."""
        editor, path, expected = self._hash_context
        if editor not in self.tab_view.all_editors():
            return
        if str(editor.path) != path or getattr(editor, '_disk_digest', None) != expected:
            return
        digest, error = result
        editor._external_change_hint = bool(error or digest != expected)
        message = error or ('File changed on disk' if digest != expected else 'Disk version unchanged')
        self.statusBar().showMessage(message, 5000)

    def _hash_finished(self):
        """Release both success and failure jobs after the thread exits."""
        self._hash_job.deleteLater()
        self._hash_job = None
        self._hash_context = None
        QTimer.singleShot(0, self._next_disk_hash)

    def current_editor(self):
````

#### Step 24.5: `main.py` — MainWindow.closeEvent: cancel hash job

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.stop()
````

**NEW**

````python
        if getattr(self, "_hash_job", None) is not None:
            self._hash_job.requestInterruption()
        self.terminal.stop()
````

**If Topic 23 is already installed:** the terminal stop is guarded. Insert this topic’s shutdown statements immediately **before** that guard, using:

````python
        if getattr(self, "_hash_job", None) is not None:
            self._hash_job.requestInterruption()
        if self.terminal is not None:
            self.terminal.stop()
````

#### Step 24.6: `main.py` — MainWindow._background_work_running: await hash job

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _background_work_running(self) -> bool:
````

**NEW**

````python
    def _background_work_running(self) -> bool:
        if getattr(self, "_hash_job", None) is not None and self._hash_job.isRunning():
            return True
````

#### Step 24.7: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self._disk_watch = QFileSystemWatcher(self)
        self._disk_pending = {}
        self._disk_watch.fileChanged.connect(self._queue_disk_path)
        self._disk_watch.directoryChanged.connect(self._queue_disk_directory)
        self._disk_watch_timer = QTimer(self)
        self._disk_watch_timer.timeout.connect(self._sync_disk_watches)
        self._disk_watch_timer.start(1000)
````

#### Step 24.8: `main.py` — MainWindow: new methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _sync_disk_watches(self):
        """Rearm replaced files and remove retired paths without hashing every tick."""
        editors = [e for e in self.tab_view.all_editors() if getattr(e, 'path', None)]
        files = {str(Path(e.path).absolute()) for e in editors}
        directories = {str(Path(p).parent) for p in files}
        existing = set(self._disk_watch.files()) | set(self._disk_watch.directories())
        wanted = files | directories
        removed = existing - wanted
        if removed:
            self._disk_watch.removePaths(sorted(removed))
        added = [p for p in wanted - existing if Path(p).exists()]
        if added:
            self._disk_watch.addPaths(added)
        self._disk_pending = {e: p for e, p in self._disk_pending.items() if e in editors}
        self._next_disk_hash()

    def _queue_disk_path(self, path):
        """Coalesce a file notification by editor identity."""
        for editor in self.tab_view.all_editors():
            if getattr(editor, 'path', None) and str(Path(editor.path).absolute()) == path:
                self._disk_pending[editor] = path
        self._next_disk_hash()

    def _queue_disk_directory(self, directory):
        """Directory watches catch delete/recreate and atomic replacement."""
        for editor in self.tab_view.all_editors():
            if getattr(editor, 'path', None) and str(Path(editor.path).absolute().parent) == directory:
                self._disk_pending[editor] = str(Path(editor.path).absolute())
        self._next_disk_hash()

    def _next_disk_hash(self):
        """Run one queued immutable path at a time and retain worker ownership."""
        if getattr(self, '_close_prompts_complete', False) or getattr(self, '_hash_job', None) is not None or not self._disk_pending:
            return
        editor = next(iter(self._disk_pending))
        path = self._disk_pending.pop(editor)
        if editor not in self.tab_view.all_editors():
            return
        job = HashJob(path, self)
        self._hash_job = job
        self._hash_context = (editor, str(editor.path), getattr(editor, '_disk_digest', None))
        job.result.connect(self._disk_hash_result)
        job.finished.connect(self._hash_finished)
        job.start()

    def current_editor(self):
````

**Using this topic:** Open-file notifications queue background hashes. Check Disk Change also requests an explicit read; save-time conflict detection still uses a fresh digest.


---

<a id="topic-25"></a>

## Topic 25: Incremental syntax highlighting

### 1. Topic explanation

Reuse Markdown line-state checkpoints and complete Python scanner snapshots. Invalidate checkpoints before changed prefixes and resume the production scanner rather than calculating an unused range. Update the matching Cython scanner API; an old native binary safely falls back to Python. Full text retrieval/comparison remains linear; this reduces repeated scanning/styling, not all document work.

**Prerequisites:** None; apply directly to the pinned baseline.

**Operational details:** The Python fallback works immediately. For the optional native path, close the editor, install Cython/setuptools in the editor environment if needed, then run `python python_editor/setup.py build_ext --inplace` from the repository root. This regenerates lexer_fast.c and the platform extension; do not paste generated C manually. Keep style_chunk and all other native helpers. STATE_API = 2 prevents loading the old scanner contract.

**Documentation used:**

- [QsciLexerCustom](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciLexerCustom.html)
- [Scintilla lexing](https://www.scintilla.org/ScintillaDoc.html#Lexing)
- [Cython compilation](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html)

### 2. Topic code

#### `python_editor/lexer_checkpoints.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Sparse complete scanner snapshots used by production Python and Cython lexers."""
from __future__ import annotations


class LexerCheckpoints:
    """Cache scanner locals only at safe line boundaries, bounded per document."""

    def __init__(self, *, enabled: bool = True, verify: bool = False, limit: int = 512):
        """Enable production reuse; optionally compare every lookup to a full scan."""
        if limit < 1:
            raise ValueError("Checkpoint capacity must be positive")
        self.enabled, self.verify, self.limit = enabled, verify, limit
        self.source, self.states, self.scanned_to = b"", {0: None}, 0

    def invalidate(self, current: bytes) -> None:
        """Discard states at/after the changed line and three-byte lookahead."""
        if current == self.source:
            return
        matched = 0
        for old, new in zip(self.source, current):
            if old != new:
                break
            matched += 1
        # Triple-quote lookahead can make a change affect earlier bytes. Rewind
        # before that lookahead, then to a full line boundary in the old prefix.
        safe = current.rfind(b"\n", 0, max(0, matched - 3)) + 1
        self.states = {p: state for p, state in self.states.items() if p < safe}
        self.states[0] = None
        self.scanned_to = min(self.scanned_to, safe)
        self.source = current

    def state_before(self, current: bytes, target: int, scanner) -> int:
        """Resume the actual scanner from complete locals and return packed style bits."""
        self.invalidate(current)
        target = max(0, min(target, len(current)))
        if not self.enabled:
            return scanner(current, target)
        position = max(p for p in self.states if p <= target)
        result = scanner(current, target, self.states[position], self.states)
        self.scanned_to = max(self.scanned_to, target)
        # Keep zero plus the most recent offsets. A miss safely rescans from zero.
        for old in sorted(self.states)[1:-self.limit]:
            self.states.pop(old, None)
        if self.verify:
            expected = scanner(current, target)
            if result != expected:
                self.enabled = False
                self.states = {0: None}
                raise AssertionError("Incremental scanner differs from full-prefix scan")
        return result
````

| Definition | Responsibility |
|---|---|
| `LexerCheckpoints` | Cache scanner locals only at safe line boundaries, bounded per document. |
| `LexerCheckpoints.__init__` | Enable production reuse; optionally compare every lookup to a full scan. |
| `LexerCheckpoints.invalidate` | Discard states at/after the changed line and three-byte lookahead. |
| `LexerCheckpoints.state_before` | Resume the actual scanner from complete locals and return packed style bits. |

#### `python_editor/setup.py` — updated existing module

Read the complete target implementation below. The implementation section shows the exact existing-code edits; do not paste this as a second class or a second module.

````python
"""Build the optional packaged Cython lexer from the repository root."""
from pathlib import Path
from setuptools import Extension, setup
from Cython.Build import cythonize

# Explicit module naming makes the compiled module importable from root and wheels.
setup(
    name="markdowneditor-native-lexer",
    packages=[],
    ext_modules=cythonize(
        [Extension("python_editor.lexer_fast", [str(Path(__file__).with_name("lexer_fast.pyx"))])],
        compiler_directives={"boundscheck": False, "wraparound": False,
                             "cdivision": True, "language_level": 3},
    ),
)
````

### 3. Topic implementation — exact files and methods

#### Step 25.1: create `python_editor/lexer_checkpoints.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 25.2: `python_editor/setup.py` — `module`

Replace only the following contiguous block. The context is from the pinned repository; keep all surrounding definitions.

**OLD**

````python
# setup.py
# Build script for compiling the Cython lexer.
# Run python stup.py build_ext --inplace

# This produces:
#       Windows: lexer_fast.cp3xx-win_amd64.pyd
#       Linux: lexer_fast.cpython-3xx-x86_64-inux-gnu.so


from pathlib import Path

from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        str(Path(__file__).with_name("lexer_fast.pyx")),
        compiler_directives={
            # boundscheck=False: disable IndexError checking oin array access
            # We manually check bounds, so thi is safe. Gives ~20% speedup.
            "boundscheck": False,
            
            # wraparound=False: disable negative indexing (text[-1])
            # We never use negative indicies. Gives ~10% speedup.
            "wraparound": False,
            
            # cdivision=True: use C division instead of Python division
            # Faster for integer division.
            "cdivision": True,
            
            # language_level=3: use Python 3 semantics for strings/bytes
            "language_level": "3",
        }
    )
)
````

**NEW**

````python
"""Build the optional packaged Cython lexer from the repository root."""
from pathlib import Path
from setuptools import Extension, setup
from Cython.Build import cythonize

# Explicit module naming makes the compiled module importable from root and wheels.
setup(
    name="markdowneditor-native-lexer",
    packages=[],
    ext_modules=cythonize(
        [Extension("python_editor.lexer_fast", [str(Path(__file__).with_name("lexer_fast.pyx"))])],
        compiler_directives={"boundscheck": False, "wraparound": False,
                             "cdivision": True, "language_level": 3},
    ),
)
````

#### Step 25.3: `markdown_editor/markdowncustomlexer.py` — MarkdownCustomLexer.styleText

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def styleText(self, start: int, end: int) -> None:
        full_text = self.editor.text()
        start_char = self._byte_pos_to_char_index(full_text, start)
        end_char = self._byte_pos_to_char_index(full_text, end)
        in_fence, fence_char, fence_len, in_comment = self._state_before(full_text, start_char)
        partial_first = start_char > 0 and full_text[start_char - 1] != "\n"

        self.startStyling(start)
        lines = full_text[start_char:end_char].split("\n")
        for index, line in enumerate(lines):
            in_fence, fence_char, fence_len, in_comment = self._style_line_with_comments(
                line,
                in_fence,
                fence_char,
                fence_len,
                in_comment,
                force_inline=partial_first and index == 0,
            )
            if index != len(lines) - 1:
                self.setStyling(1, self.DEFAULT)
````

**NEW**

````python
    def styleText(self, start: int, end: int) -> None:
        """Reuse line states and propagate changes until a stable suffix."""
        text = self.editor.text()
        parts = text.split('\n')
        lines = [part + ('\n' if index < len(parts)-1 else '')
                 for index, part in enumerate(parts)]
        old = getattr(self, '_line_states', [])
        # Cache entries are (exact line text, incoming state, outgoing state).
        prefix = 0
        while prefix < min(len(lines), len(old)) and lines[prefix] == old[prefix][0]:
            prefix += 1
        suffix = 0
        while suffix < min(len(lines), len(old))-prefix and lines[-1-suffix] == old[-1-suffix][0]:
            suffix += 1
        offsets = [0]
        for line in lines:
            offsets.append(offsets[-1] + len(line.encode('utf-8')))
        import bisect
        requested = max(0, bisect.bisect_right(offsets, start)-1)
        first = min(prefix, requested, len(lines)-1)
        cache = old[:first]
        state = cache[-1][2] if cache else (False, None, 0, False)
        self.startStyling(offsets[first])
        for index in range(first, len(lines)):
            # Scintilla retains styles on the unchanged shifted suffix. Reuse it
            # only after satisfying the requested byte range and matching state.
            if suffix and index >= len(lines)-suffix and offsets[index] >= end:
                old_index = len(old) - (len(lines)-index)
                if old[old_index][1] == state:
                    cache.extend(old[old_index:])
                    break
            incoming = state
            line = lines[index]
            body = line[:-1] if line.endswith('\n') else line
            state = self._style_line_with_comments(body, *state, force_inline=False)
            if line.endswith('\n'):
                self.setStyling(1, self.DEFAULT)
            cache.append((line, incoming, state))
        self._line_states = cache
````

#### Step 25.4: `python_editor/custompythonlexer.py` — module native-import block

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
try:
    from lexer_fast import style_chunk as _cython_style
    from lexer_fast import compute_state_before as _cython_state
    _HAS_CYTHON = True
except ImportError:
    _HAS_CYTHON = False
````

**NEW**

````python
from python_editor.lexer_checkpoints import LexerCheckpoints

try:
    from python_editor.lexer_fast import style_chunk as _cython_style
    from python_editor.lexer_fast import compute_state_before as _cython_state
    from python_editor.lexer_fast import STATE_API
    _HAS_CYTHON = STATE_API == 2
except ImportError:
    _HAS_CYTHON = False
````

#### Step 25.5: `python_editor/custompythonlexer.py` — _py_compute_state

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
def _py_compute_state(text, target_pos):
    """Scan from byte 0 to target_pos and return the packed lexer state.
    `text` must be a bytes object; all positions/lengths are byte-based."""
    target_pos = min(target_pos, len(text))
    length = len(text)
    i = 0
    in_string = in_comment = triple_string = 0
    string_delim = ""
    in_fstring = escape_next = in_fexpr = fexpr_depth = is_docstring = 0
    bracket_depth = pending_def = pending_class = 0
    expect_docstring = at_class_body = 0

    while i < target_pos:
        c = text[i:i + 1].decode("latin-1")

        if in_fexpr:
            if c == "}":
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                i += 1
                continue
            if c == "{":
                fexpr_depth += 1
                i += 1
                continue
            if c in "frb" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") in "\"'":
                # decode to a 1-char string — bytes indexing gives an int here
                delim = text[i + 1:i + 2].decode("latin-1")
                i += 2
                if i + 1 < length and text[i:i + 1].decode("latin-1") == delim and text[i + 1:i + 2].decode("latin-1") == delim:
                    i += 2
                    i = _py_skip_string(text, i, target_pos, delim, True)
                else:
                    i = _py_skip_string(text, i, target_pos, delim, False)
                continue
            if c in "\"'":
                delim = c
                i += 1
                if i + 1 < length and text[i:i + 1].decode("latin-1") == delim and text[i + 1:i + 2].decode("latin-1") == delim:
                    i += 2
                    i = _py_skip_string(text, i, target_pos, delim, True)
                else:
                    i = _py_skip_string(text, i, target_pos, delim, False)
                continue
            i += 1
            continue

        if in_comment:
            if c in "\n\r":
                in_comment = 0
            i += 1
            continue

        if in_string:
            if escape_next:
                escape_next = 0
                i += 1
                continue
            if c == "\\":
                escape_next = 1
                i += 1
                continue
            if triple_string:
                if c in "\"'":
                    if i + 2 < length and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                        in_string = triple_string = string_delim = 0
                        in_fstring = is_docstring = 0
                        i += 3
                        continue
                    i += 1
                    continue
                if in_fstring and c == "{":
                    if i + 1 < length and text[i + 1:i + 2].decode("latin-1") == "{":
                        i += 2
                        continue
                    in_fexpr = 1
                    fexpr_depth = 1
                    i += 1
                    continue
                i += 1
                continue
            if c == string_delim:
                in_string = string_delim = in_fstring = is_docstring = 0
                i += 1
                continue
            if in_fstring and c == "{":
                if i + 1 < length and text[i + 1:i + 2].decode("latin-1") == "{":
                    i += 2
                    continue
                in_fexpr = 1
                fexpr_depth = 1
                i += 1
                continue
            i += 1
            continue

        # not in string/comment
        if c in "frb" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") in "\"'":
            next_c = text[i + 1:i + 2].decode("latin-1")
            if i + 3 < length and text[i + 2:i + 3].decode("latin-1") == next_c and text[i + 3:i + 4].decode("latin-1") == next_c:
                in_string = triple_string = 1
                string_delim = next_c
                in_fstring = 1 if c == "f" else 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 4
                continue
            in_string = 1
            triple_string = 0
            string_delim = next_c
            in_fstring = 1 if c == "f" else 0
            expect_docstring = 0
            i += 2
            continue

        if c in "\"'":
            if i + 2 < length and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                in_string = triple_string = 1
                string_delim = c
                in_fstring = 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 3
                continue
            in_string = 1
            triple_string = 0
            string_delim = c
            in_fstring = 0
            expect_docstring = 0
            i += 1
            continue

        if c == "#":
            in_comment = 1
            i += 1
            continue

        if c in "([{":
            bracket_depth += 1
            i += 1
            continue
        if c in ")]}":
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        if c == ":":
            if bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = pending_class = 0
            i += 1
            continue

        if c == "-" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") == ">":
            i += 2
            continue

        if c.isalpha() or c == "_":
            start = i
            i += 1
            while i < target_pos and (text[i:i + 1].decode("latin-1").isalnum() or text[i:i + 1].decode("latin-1") == "_"):
                i += 1
            word = text[start:i].decode("utf-8", errors="replace")
            if word == "def":
                pending_def = 1
                pending_class = 0
                at_class_body = 0
            elif word == "class":
                pending_class = 1
                pending_def = 0
                at_class_body = 0
            else:
                expect_docstring = 0
            continue

        i += 1

    return _py_pack_state(in_string, in_comment, triple_string, string_delim,
                          in_fstring, escape_next, in_fexpr, fexpr_depth,
                          is_docstring, expect_docstring, at_class_body)
````

**NEW**

````python
def _py_compute_state(text, target_pos, snapshot=None, checkpoints=None):
    """Scan from byte 0 to target_pos and return the packed lexer state.
    ``snapshot`` restores all scanner locals at a safe line boundary. Optional
    ``checkpoints`` receives complete snapshots; packed style bits alone omit
    bracket and pending-definition state and must never be used to resume.
    """
    target_pos = min(target_pos, len(text))
    length = len(text)
    i = 0
    in_string = in_comment = triple_string = 0
    string_delim = ""
    in_fstring = escape_next = in_fexpr = fexpr_depth = is_docstring = 0
    bracket_depth = pending_def = pending_class = 0
    expect_docstring = at_class_body = 0

    if snapshot is not None:
        (i, in_string, in_comment, triple_string, string_delim, in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring, bracket_depth, pending_def, pending_class, expect_docstring, at_class_body) = snapshot
    next_checkpoint = i + 4096

    while i < target_pos:
        # Nested f-expression strings use a skip routine, so never checkpoint
        # there: a resume would lose that routine's internal string state.
        if checkpoints is not None and i >= next_checkpoint and not in_fexpr and text[i - 1] == 10:
            checkpoints[i] = (i, in_string, in_comment, triple_string, string_delim, in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring, bracket_depth, pending_def, pending_class, expect_docstring, at_class_body)
            next_checkpoint = i + 4096
        c = text[i:i + 1].decode("latin-1")

        if in_fexpr:
            if c == "}":
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                i += 1
                continue
            if c == "{":
                fexpr_depth += 1
                i += 1
                continue
            if c in "frb" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") in "\"'":
                # decode to a 1-char string — bytes indexing gives an int here
                delim = text[i + 1:i + 2].decode("latin-1")
                i += 2
                if i + 1 < length and text[i:i + 1].decode("latin-1") == delim and text[i + 1:i + 2].decode("latin-1") == delim:
                    i += 2
                    i = _py_skip_string(text, i, target_pos, delim, True)
                else:
                    i = _py_skip_string(text, i, target_pos, delim, False)
                continue
            if c in "\"'":
                delim = c
                i += 1
                if i + 1 < length and text[i:i + 1].decode("latin-1") == delim and text[i + 1:i + 2].decode("latin-1") == delim:
                    i += 2
                    i = _py_skip_string(text, i, target_pos, delim, True)
                else:
                    i = _py_skip_string(text, i, target_pos, delim, False)
                continue
            i += 1
            continue

        if in_comment:
            if c in "\n\r":
                in_comment = 0
            i += 1
            continue

        if in_string:
            if escape_next:
                escape_next = 0
                i += 1
                continue
            if c == "\\":
                escape_next = 1
                i += 1
                continue
            if triple_string:
                if c in "\"'":
                    if i + 2 < length and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                        in_string = triple_string = string_delim = 0
                        in_fstring = is_docstring = 0
                        i += 3
                        continue
                    i += 1
                    continue
                if in_fstring and c == "{":
                    if i + 1 < length and text[i + 1:i + 2].decode("latin-1") == "{":
                        i += 2
                        continue
                    in_fexpr = 1
                    fexpr_depth = 1
                    i += 1
                    continue
                i += 1
                continue
            if c == string_delim:
                in_string = string_delim = in_fstring = is_docstring = 0
                i += 1
                continue
            if in_fstring and c == "{":
                if i + 1 < length and text[i + 1:i + 2].decode("latin-1") == "{":
                    i += 2
                    continue
                in_fexpr = 1
                fexpr_depth = 1
                i += 1
                continue
            i += 1
            continue

        # not in string/comment
        if c in "frb" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") in "\"'":
            next_c = text[i + 1:i + 2].decode("latin-1")
            if i + 3 < length and text[i + 2:i + 3].decode("latin-1") == next_c and text[i + 3:i + 4].decode("latin-1") == next_c:
                in_string = triple_string = 1
                string_delim = next_c
                in_fstring = 1 if c == "f" else 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 4
                continue
            in_string = 1
            triple_string = 0
            string_delim = next_c
            in_fstring = 1 if c == "f" else 0
            expect_docstring = 0
            i += 2
            continue

        if c in "\"'":
            if i + 2 < length and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                in_string = triple_string = 1
                string_delim = c
                in_fstring = 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 3
                continue
            in_string = 1
            triple_string = 0
            string_delim = c
            in_fstring = 0
            expect_docstring = 0
            i += 1
            continue

        if c == "#":
            in_comment = 1
            i += 1
            continue

        if c in "([{":
            bracket_depth += 1
            i += 1
            continue
        if c in ")]}":
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        if c == ":":
            if bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = pending_class = 0
            i += 1
            continue

        if c == "-" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") == ">":
            i += 2
            continue

        if c.isalpha() or c == "_":
            start = i
            i += 1
            while i < target_pos and (text[i:i + 1].decode("latin-1").isalnum() or text[i:i + 1].decode("latin-1") == "_"):
                i += 1
            word = text[start:i].decode("utf-8", errors="replace")
            if word == "def":
                pending_def = 1
                pending_class = 0
                at_class_body = 0
            elif word == "class":
                pending_class = 1
                pending_def = 0
                at_class_body = 0
            else:
                expect_docstring = 0
            continue

        i += 1

    return _py_pack_state(in_string, in_comment, triple_string, string_delim,
                          in_fstring, escape_next, in_fexpr, fexpr_depth,
                          is_docstring, expect_docstring, at_class_body)
````

#### Step 25.6: `python_editor/custompythonlexer.py` — PyCustomLexer.styleText

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def styleText(self, start: int, end: int) -> None:
        full_text = self.editor.text()
        text_bytes = full_text.encode('utf-8')

        start_char = self._byte_pos_to_char_index(full_text, start)
        end_char = self._byte_pos_to_char_index(full_text, end)

        start_byte = len(full_text[:start_char].encode('utf-8'))
        end_byte = len(full_text[:end_char].encode('utf-8'))

        # Compute the correct lexer state at start_byte by scanning from byte 0.
        # This is necessary because QScintilla may call styleText for
        # non-contiguous regions (e.g. when the user scrolls).
        if _HAS_CYTHON:
            prev_state = _cython_state(text_bytes, start_byte)
            final_state, styled_tokens = _cython_style(
                text_bytes,
                start_byte,
                end_byte,
                prev_state,
                self._keyword_set,
                self._builtin_set,
                self._magic_set,
            )
        else:
            # Pure-Python fallback - identical logic to lexer_fast.pyx
            prev_state = _py_compute_state(text_bytes, start_byte)
            final_state, styled_tokens = _py_style_chunk(
                text_bytes,
                start_byte,
                end_byte,
                prev_state,
                self._keyword_set,
                self._builtin_set,
                self._magic_set,
            )

        self.startStyling(start)
        for byte_len, style_id in styled_tokens:
            self.setStyling(byte_len, style_id)

        self._prev_state = final_state
````

**NEW**

````python
    def styleText(self, start: int, end: int) -> None:
        """Style byte ranges using invalidated, complete prefix-state checkpoints.

        Both scanners expose the same resume protocol. Styling token generation
        remains unchanged; only the repeated prefix-state scan is shortened.
        """
        from time import perf_counter
        began = perf_counter()
        source = self.editor.text().encode("utf-8")
        start, end = max(0, min(start, len(source))), min(end, len(source))
        if end <= start:
            return
        if not hasattr(self, "_checkpoints"):
            self._checkpoints = LexerCheckpoints()
        scanner = _cython_state if _HAS_CYTHON else _py_compute_state
        styler = _cython_style if _HAS_CYTHON else _py_style_chunk
        state = self._checkpoints.state_before(source, start, scanner)
        final_state, tokens = styler(source, start, end, state,
                                    self._keyword_set, self._builtin_set, self._magic_set)
        self.startStyling(start)
        for length, style in tokens:
            self.setStyling(length, style)
        self._prev_state = final_state
        # Seed sparse snapshots during the first long paint so later scrolling can
        # resume nearby. Packed style_chunk state is deliberately never cached.
        if end > self._checkpoints.scanned_to + 4096:
            self._checkpoints.state_before(source, end, scanner)
        monitor = getattr(self.editor.window(), 'performance', None)
        if monitor is not None and monitor.enabled:
            monitor.samples.append(('python_lexing', (perf_counter() - began) * 1000))
            del monitor.samples[:-500]
````

#### Step 25.7: `python_editor/lexer_fast.pyx` — module compute_state_before; retain style_chunk

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
def compute_state_before(bytes text, int target_pos):
    cdef int length = len(text)
    if target_pos > length:
        target_pos = length

    cdef int i = 0
    cdef int start
    cdef unsigned char c
    cdef unsigned char next_c
    cdef int delim
    cdef int in_string = 0
    cdef int in_comment = 0
    cdef int triple_string = 0
    cdef int string_delim = 0
    cdef int in_fstring = 0
    cdef int escape_next = 0
    cdef int in_fexpr = 0
    cdef int fexpr_depth = 0
    cdef int is_docstring = 0

    cdef int bracket_depth = 0
    cdef int pending_def = 0
    cdef int pending_class = 0
    cdef int expect_docstring = 0
    cdef int at_class_body = 0

    while i < target_pos:
        c = text[i]

        # ---- inside f-string expression { ... } ----
        if in_fexpr:
            if c == 125:  # }
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                i += 1
                continue
            if c == 123:  # {
                fexpr_depth += 1
                i += 1
                continue
            # prefixed nested string
            if (c == 102 or c == 114 or c == 98) and i + 1 < target_pos:
                next_c = text[i + 1]
                if next_c == 34 or next_c == 39:
                    delim = next_c
                    i += 2
                    if i + 1 < length and text[i] == delim and text[i+1] == delim:
                        i += 2
                        _skip_string(text, target_pos, &i, delim, 1)
                    else:
                        _skip_string(text, target_pos, &i, delim, 0)
                    continue
            if c == 34 or c == 39:
                delim = c
                i += 1
                if i + 1 < length and text[i] == delim and text[i+1] == delim:
                    i += 2
                    _skip_string(text, target_pos, &i, delim, 1)
                else:
                    _skip_string(text, target_pos, &i, delim, 0)
                continue
            i += 1
            continue

        # ---- comment ----
        if in_comment:
            if c == 10 or c == 13:
                in_comment = 0
            i += 1
            continue

        # ---- inside string ----
        if in_string:
            if escape_next:
                escape_next = 0
                i += 1
                continue
            if c == 92:
                escape_next = 1
                i += 1
                continue
            if triple_string:
                if c == 34 or c == 39:
                    if i + 2 < length and text[i+1] == c and text[i+2] == c:
                        in_string = 0
                        triple_string = 0
                        string_delim = 0
                        in_fstring = 0
                        is_docstring = 0
                        i += 3
                        continue
                    i += 1
                    continue
                if in_fstring and c == 123:
                    if i + 1 < length and text[i+1] == 123:
                        i += 2
                        continue
                    in_fexpr = 1
                    fexpr_depth = 1
                    i += 1
                    continue
                i += 1
                continue
            # single-line string
            if c == string_delim:
                in_string = 0
                string_delim = 0
                in_fstring = 0
                is_docstring = 0
                i += 1
                continue
            if in_fstring and c == 123:
                if i + 1 < length and text[i+1] == 123:
                    i += 2
                    continue
                in_fexpr = 1
                fexpr_depth = 1
                i += 1
                continue
            i += 1
            continue

        # ---- not in string/comment ----

        # string prefix f/r/b
        if (c == 102 or c == 114 or c == 98) and i + 1 < target_pos:
            next_c = text[i + 1]
            if next_c == 34 or next_c == 39:
                if i + 3 < length and text[i+2] == next_c and text[i+3] == next_c:
                    in_string = 1
                    triple_string = 1
                    string_delim = next_c
                    in_fstring = 1 if (c == 102) else 0
                    if expect_docstring:
                        is_docstring = 1
                    expect_docstring = 0
                    i += 4
                    continue
                in_string = 1
                triple_string = 0
                string_delim = next_c
                in_fstring = 1 if (c == 102) else 0
                expect_docstring = 0
                i += 2
                continue

        # regular string
        if c == 34 or c == 39:
            if i + 2 < length and text[i+1] == c and text[i+2] == c:
                in_string = 1
                triple_string = 1
                string_delim = c
                in_fstring = 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 3
                continue
            in_string = 1
            triple_string = 0
            string_delim = c
            in_fstring = 0
            expect_docstring = 0
            i += 1
            continue

        # comment
        if c == 35:
            in_comment = 1
            i += 1
            continue

        # brackets
        if c == 40 or c == 91 or c == 123:
            bracket_depth += 1
            i += 1
            continue
        if c == 41 or c == 93 or c == 125:
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        # colon
        if c == 58:
            if bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = 0
                pending_class = 0
            i += 1
            continue

        # arrow ->
        if c == 45 and i + 1 < target_pos and text[i+1] == 62:
            i += 2
            continue

        # identifier
        if is_alpha(c):
            start = i
            i += 1
            while i < target_pos and is_alnum(text[i]):
                i += 1
            if text[start:i] == b"def":
                pending_def = 1
                pending_class = 0
                at_class_body = 0
            elif text[start:i] == b"class":
                pending_class = 1
                pending_def = 0
                at_class_body = 0
            else:
                expect_docstring = 0
            continue

        # newline (do NOT reset expect_docstring/pending_def here -
        # docstrings live on the line after the def/class header)
        if c == 10 or c == 13:
            i += 1
            continue

        i += 1

    return pack_state(in_string, in_comment, triple_string,
                      string_delim, in_fstring, escape_next,
                      in_fexpr, fexpr_depth, is_docstring,
                      expect_docstring, at_class_body)


# --- The full styler ---
````

**NEW**

````python
STATE_API = 2


def compute_state_before(bytes text, int target_pos, snapshot=None, checkpoints=None):
    """Scan from a complete safe snapshot and cache resumable line boundaries."""
    cdef int length = len(text)
    if target_pos > length:
        target_pos = length

    cdef int i = 0
    cdef int start
    cdef unsigned char c
    cdef unsigned char next_c
    cdef int delim
    cdef int in_string = 0
    cdef int in_comment = 0
    cdef int triple_string = 0
    cdef int string_delim = 0
    cdef int in_fstring = 0
    cdef int escape_next = 0
    cdef int in_fexpr = 0
    cdef int fexpr_depth = 0
    cdef int is_docstring = 0

    cdef int bracket_depth = 0
    cdef int pending_def = 0
    cdef int pending_class = 0
    cdef int expect_docstring = 0
    cdef int at_class_body = 0

    if snapshot is not None:
        (i, in_string, in_comment, triple_string, string_delim, in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring, bracket_depth, pending_def, pending_class, expect_docstring, at_class_body) = snapshot
    next_checkpoint = i + 4096

    while i < target_pos:
        # Nested f-expression strings use a skip routine, so never checkpoint
        # there: a resume would lose that routine's internal string state.
        if checkpoints is not None and i >= next_checkpoint and not in_fexpr and text[i - 1] == 10:
            checkpoints[i] = (i, in_string, in_comment, triple_string, string_delim, in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring, bracket_depth, pending_def, pending_class, expect_docstring, at_class_body)
            next_checkpoint = i + 4096
        c = text[i]

        # ---- inside f-string expression { ... } ----
        if in_fexpr:
            if c == 125:  # }
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                i += 1
                continue
            if c == 123:  # {
                fexpr_depth += 1
                i += 1
                continue
            # prefixed nested string
            if (c == 102 or c == 114 or c == 98) and i + 1 < target_pos:
                next_c = text[i + 1]
                if next_c == 34 or next_c == 39:
                    delim = next_c
                    i += 2
                    if i + 1 < length and text[i] == delim and text[i+1] == delim:
                        i += 2
                        _skip_string(text, target_pos, &i, delim, 1)
                    else:
                        _skip_string(text, target_pos, &i, delim, 0)
                    continue
            if c == 34 or c == 39:
                delim = c
                i += 1
                if i + 1 < length and text[i] == delim and text[i+1] == delim:
                    i += 2
                    _skip_string(text, target_pos, &i, delim, 1)
                else:
                    _skip_string(text, target_pos, &i, delim, 0)
                continue
            i += 1
            continue

        # ---- comment ----
        if in_comment:
            if c == 10 or c == 13:
                in_comment = 0
            i += 1
            continue

        # ---- inside string ----
        if in_string:
            if escape_next:
                escape_next = 0
                i += 1
                continue
            if c == 92:
                escape_next = 1
                i += 1
                continue
            if triple_string:
                if c == 34 or c == 39:
                    if i + 2 < length and text[i+1] == c and text[i+2] == c:
                        in_string = 0
                        triple_string = 0
                        string_delim = 0
                        in_fstring = 0
                        is_docstring = 0
                        i += 3
                        continue
                    i += 1
                    continue
                if in_fstring and c == 123:
                    if i + 1 < length and text[i+1] == 123:
                        i += 2
                        continue
                    in_fexpr = 1
                    fexpr_depth = 1
                    i += 1
                    continue
                i += 1
                continue
            # single-line string
            if c == string_delim:
                in_string = 0
                string_delim = 0
                in_fstring = 0
                is_docstring = 0
                i += 1
                continue
            if in_fstring and c == 123:
                if i + 1 < length and text[i+1] == 123:
                    i += 2
                    continue
                in_fexpr = 1
                fexpr_depth = 1
                i += 1
                continue
            i += 1
            continue

        # ---- not in string/comment ----

        # string prefix f/r/b
        if (c == 102 or c == 114 or c == 98) and i + 1 < target_pos:
            next_c = text[i + 1]
            if next_c == 34 or next_c == 39:
                if i + 3 < length and text[i+2] == next_c and text[i+3] == next_c:
                    in_string = 1
                    triple_string = 1
                    string_delim = next_c
                    in_fstring = 1 if (c == 102) else 0
                    if expect_docstring:
                        is_docstring = 1
                    expect_docstring = 0
                    i += 4
                    continue
                in_string = 1
                triple_string = 0
                string_delim = next_c
                in_fstring = 1 if (c == 102) else 0
                expect_docstring = 0
                i += 2
                continue

        # regular string
        if c == 34 or c == 39:
            if i + 2 < length and text[i+1] == c and text[i+2] == c:
                in_string = 1
                triple_string = 1
                string_delim = c
                in_fstring = 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 3
                continue
            in_string = 1
            triple_string = 0
            string_delim = c
            in_fstring = 0
            expect_docstring = 0
            i += 1
            continue

        # comment
        if c == 35:
            in_comment = 1
            i += 1
            continue

        # brackets
        if c == 40 or c == 91 or c == 123:
            bracket_depth += 1
            i += 1
            continue
        if c == 41 or c == 93 or c == 125:
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        # colon
        if c == 58:
            if bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = 0
                pending_class = 0
            i += 1
            continue

        # arrow ->
        if c == 45 and i + 1 < target_pos and text[i+1] == 62:
            i += 2
            continue

        # identifier
        if is_alpha(c):
            start = i
            i += 1
            while i < target_pos and is_alnum(text[i]):
                i += 1
            if text[start:i] == b"def":
                pending_def = 1
                pending_class = 0
                at_class_body = 0
            elif text[start:i] == b"class":
                pending_class = 1
                pending_def = 0
                at_class_body = 0
            else:
                expect_docstring = 0
            continue

        # newline (do NOT reset expect_docstring/pending_def here -
        # docstrings live on the line after the def/class header)
        if c == 10 or c == 13:
            i += 1
            continue

        i += 1

    return pack_state(in_string, in_comment, triple_string,
                      string_delim, in_fstring, escape_next,
                      in_fexpr, fexpr_depth, is_docstring,
                      expect_docstring, at_class_body)


# --- The full styler ---
````

**Using this topic:** The fallback scanner works after the source edits. Build the optional Cython extension only if you want that path; the version check rejects stale binaries.


---

<a id="topic-26"></a>

## Topic 26: Smarter Markdown preview updates

### 1. Topic explanation

Coalesce Markdown edits through the existing timer, skip hidden previews and unchanged content, reset delivery state after shell reloads and render when the panel becomes visible. Preserve scroll position and keep sanitized HTML inside a JSON-encoded JavaScript payload.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QTimer](https://doc.qt.io/archives/qt-5.15/qtimer.html)
- [Qt 5.15 QWebEnginePage](https://doc.qt.io/archives/qt-5.15/qwebenginepage.html)
- [Bleach clean](https://bleach.readthedocs.io/en/latest/clean.html)

### 2. Topic code

#### `markdown_editor/preview_visibility.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Refresh a preview after its show event has completed."""
from PyQt5.QtCore import QObject, QEvent, QTimer

class PreviewVisibility(QObject):
    """Queue one refresh without doing renderer work inside a show event."""
    def __init__(self, widget, callback):
        """Parent the timer/filter to the preview so no stale callback survives."""
        super().__init__(widget)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(callback)
        widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        """Schedule after visibility is true; preserve normal Qt event handling."""
        if event.type() == QEvent.Show:
            self.timer.start(0)
        return False
````

| Definition | Responsibility |
|---|---|
| `PreviewVisibility` | Queue one refresh without doing renderer work inside a show event. |
| `PreviewVisibility.__init__` | Parent the timer/filter to the preview so no stale callback survives. |
| `PreviewVisibility.eventFilter` | Schedule after visibility is true; preserve normal Qt event handling. |

### 3. Topic implementation — exact files and methods

#### Step 26.1: create `markdown_editor/preview_visibility.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 26.2: `main.py` — MainWindow.init_ui: existing preview timer

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self._debounce.setInterval(100)
````

**NEW**

````python
        self._debounce.setInterval(220)
````

#### Step 26.3: `main.py` — MainWindow.render_preview: after readiness guard

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        if not isinstance(editor, MarkdownEditor) or not self._preview_ready:
            return
````

**NEW**

````python
        if not isinstance(editor, MarkdownEditor) or not self._preview_ready:
            return
        if not self.preview.isVisible():
            return
        fingerprint = (id(editor), hashlib.sha256(editor.text().encode('utf-8')).digest())
        if fingerprint == getattr(self, '_preview_fingerprint', None):
            return
````

#### Step 26.4: `main.py` — MainWindow.render_preview: after successful dispatch

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.preview.page().runJavaScript(script)
````

**NEW**

````python
        self.preview.page().runJavaScript(script)
        self._preview_fingerprint = fingerprint
````

#### Step 26.5: `main.py` — MainWindow._on_preview_loaded

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self._preview_ready = bool(ok)
````

**NEW**

````python
        self._preview_fingerprint = None
        self._preview_ready = bool(ok)
````

#### Step 26.6: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from markdown_editor.preview_visibility import PreviewVisibility
````

#### Step 26.7: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self._preview_visibility = PreviewVisibility(self.preview, self.render_preview)
````

#### Step 26.8: `main.py` — MainWindow.render_preview: preserve scroll in a function scope

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        script = f'document.getElementById("content").innerHTML = {payload};'
````

**NEW**

````python
        script = f'(() => {{ const y = window.scrollY; document.getElementById("content").innerHTML = {payload}; window.scrollTo(0, y); }})();'
````

**Using this topic:** Edit a Markdown tab or show its hidden preview. The next coalesced visible update retains sanitization and scroll position.


---

<a id="topic-27"></a>

## Topic 27: Large-file mode

### 1. Topic explanation

Pause optional lexer/outline/preview/word-count work and Python helper requests for large files, including buffers that grow past the threshold during editing. Keep typing, save conflicts, recovery and dirty tracking active. A per-tab explicit override restores normal analysis. This is a workload policy, not a promise that arbitrarily large files have constant-time edits.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Scintilla document length and lexing](https://www.scintilla.org/ScintillaDoc.html)
- [QScintilla editor API](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)

### 2. Topic code

This topic adds or changes methods in existing classes. Their complete code is included in the OLD → NEW steps below; there is no standalone helper file or later bootstrap to install.

#### New methods in existing classes

These methods are complete here and are repeated with the exact insertion anchor in the implementation steps. Install each method only once.

**File:** `main.py`; **class:** `MainWindow`; keep four-space class indentation.

````python
    def _set_large_file_mode(self, editor, enabled):
        """Suspend optional work while retaining the lexer for restoration."""
        editor.large_file_mode = bool(enabled)
        if enabled:
            if editor.lexer() is not None:
                editor._large_saved_lexer = editor.lexer()
                editor.setLexer(None)
            for name in ('_autocomplete_timer', '_ruff_hover_timer', '_signature_timer'):
                timer = getattr(editor, name, None)
                if timer is not None:
                    timer.stop()
            for worker_name in ('auto_completer', 'definition_finder', 'hover_helper', 'signature_helper'):
                worker = getattr(editor, worker_name, None)
                if worker is not None:
                    worker.invalidate()
            editor.SendScintilla(QsciScintilla.SCI_AUTOCCANCEL)
            controller = getattr(editor, 'ruff_lsp', None)
            if controller is not None:
                controller.change_timer.stop()
        else:
            lexer = getattr(editor, '_large_saved_lexer', None)
            if lexer is not None:
                editor.setLexer(lexer)
                editor.recolor()
            controller = getattr(editor, 'ruff_lsp', None)
            if controller is not None:
                if not getattr(controller, '_opened', False):
                    controller.open_document()
                else:
                    controller._on_text_changed()
        self.statusBar().showMessage('Large-file mode ' + ('enabled' if enabled else 'disabled'), 4000)

    def _toggle_large_file_mode(self):
        """Allow an explicit override for the active document."""
        editor = self.current_editor()
        if editor is not None:
            editor._large_file_override = getattr(editor, 'large_file_mode', False)
            self._set_large_file_mode(editor, not editor._large_file_override)
            self._preview_fingerprint = None
            if isinstance(editor, MarkdownEditor) and not editor.large_file_mode:
                self.preview.show()
            self._update_outline()
            self.render_preview()
````

| Definition | Responsibility |
|---|---|
| `_set_large_file_mode` | Suspend optional work while retaining the lexer for restoration. |
| `_toggle_large_file_mode` | Allow an explicit override for the active document. |

### 3. Topic implementation — exact files and methods

#### Step 27.1: `main.py` — MainWindow: add methods immediately before current_editor

Insert the complete new methods immediately before the existing `MainWindow.current_editor`. The final header in NEW is the original method header: retain its original body beneath it. These methods are class members, not nested functions inside `current_editor`.

**OLD**

````python
    def current_editor(self):
````

**NEW**

````python
    def _set_large_file_mode(self, editor, enabled):
        """Suspend optional work while retaining the lexer for restoration."""
        editor.large_file_mode = bool(enabled)
        if enabled:
            if editor.lexer() is not None:
                editor._large_saved_lexer = editor.lexer()
                editor.setLexer(None)
            for name in ('_autocomplete_timer', '_ruff_hover_timer', '_signature_timer'):
                timer = getattr(editor, name, None)
                if timer is not None:
                    timer.stop()
            for worker_name in ('auto_completer', 'definition_finder', 'hover_helper', 'signature_helper'):
                worker = getattr(editor, worker_name, None)
                if worker is not None:
                    worker.invalidate()
            editor.SendScintilla(QsciScintilla.SCI_AUTOCCANCEL)
            controller = getattr(editor, 'ruff_lsp', None)
            if controller is not None:
                controller.change_timer.stop()
        else:
            lexer = getattr(editor, '_large_saved_lexer', None)
            if lexer is not None:
                editor.setLexer(lexer)
                editor.recolor()
            controller = getattr(editor, 'ruff_lsp', None)
            if controller is not None:
                if not getattr(controller, '_opened', False):
                    controller.open_document()
                else:
                    controller._on_text_changed()
        self.statusBar().showMessage('Large-file mode ' + ('enabled' if enabled else 'disabled'), 4000)

    def _toggle_large_file_mode(self):
        """Allow an explicit override for the active document."""
        editor = self.current_editor()
        if editor is not None:
            editor._large_file_override = getattr(editor, 'large_file_mode', False)
            self._set_large_file_mode(editor, not editor._large_file_override)
            self._preview_fingerprint = None
            if isinstance(editor, MarkdownEditor) and not editor.large_file_mode:
                self.preview.show()
            self._update_outline()
            self.render_preview()

    def current_editor(self):
````

#### Step 27.2: `main.py` — MainWindow.set_up_menu

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        menu_bar = self.menuBar()
````

**NEW**

````python
        menu_bar = self.menuBar()
        menu_bar.addAction('Toggle Large-file Mode').triggered.connect(self._toggle_large_file_mode)
````

#### Step 27.3: `main.py` — MainWindow.set_new_tab: before loading text

Apply this replacement **only inside `set_new_tab`**. Identical lines in other methods are not part of this step.

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        editor.setTextSafely(text)
````

**NEW**

````python
        self._set_large_file_mode(editor, len(raw) >= 2_000_000 or raw.count(b'\n') >= 49_999)
        editor.setTextSafely(text)
````

#### Step 27.4: `main.py` — MainWindow.render_preview

Apply this replacement **only inside `render_preview`**. Identical lines in other methods are not part of this step.

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        editor = self.current_editor()
````

**NEW**

````python
        editor = self.current_editor()
        if getattr(editor, "large_file_mode", False):
            self.preview.hide()
            return
````

#### Step 27.5: `main.py` — MainWindow._update_outline

Apply this replacement **only inside `_update_outline`**. Identical lines in other methods are not part of this step.

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        editor = self.current_editor()
````

**NEW**

````python
        editor = self.current_editor()
        if getattr(editor, "large_file_mode", False):
            self.outline_tree.clear()
            return
````

#### Step 27.6: `main.py` — MainWindow.update_word_count

Apply this replacement **only inside `update_word_count`**. Identical lines in other methods are not part of this step.

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        editor = self.current_editor()
````

**NEW**

````python
        editor = self.current_editor()
        if getattr(editor, "large_file_mode", False):
            self.word_count_label.setText("Large-file mode")
            return
````

#### Step 27.7: `python_editor/pythoneditor.py` — PythonEditor._trigger_autocomplete

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _trigger_autocomplete(self):
````

**NEW**

````python
    def _trigger_autocomplete(self):
        if getattr(self, "large_file_mode", False):
            return
````

#### Step 27.8: `python_editor/pythoneditor.py` — PythonEditor._trigger_ruff_hover

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _trigger_ruff_hover(self):
````

**NEW**

````python
    def _trigger_ruff_hover(self):
        if getattr(self, "large_file_mode", False):
            return
````

#### Step 27.9: `python_editor/pythoneditor.py` — PythonEditor._trigger_signature_help

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _trigger_signature_help(self):
````

**NEW**

````python
    def _trigger_signature_help(self):
        if getattr(self, "large_file_mode", False):
            return
````

#### Step 27.10: `ruff_implementation/ruff_lsp_controller.py` — RuffLspController._on_text_changed

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _on_text_changed(self):
````

**NEW**

````python
    def _on_text_changed(self):
        if getattr(self.editor, "large_file_mode", False):
            return
````

#### Step 27.11: `ruff_implementation/ruff_lsp_controller.py` — RuffLspController._send_change

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _send_change(self):
````

**NEW**

````python
    def _send_change(self):
        if getattr(self.editor, "large_file_mode", False):
            return
````

#### Step 27.12: `ruff_implementation/ruff_lsp_controller.py` — RuffLspController.open_document

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def open_document(self):
````

**NEW**

````python
    def open_document(self):
        if getattr(self.editor, "large_file_mode", False):
            return
````

#### Step 27.13: `main.py` — MainWindow.set_new_tab AND _on_current_editor_changed; skip if topic 20 is present

Apply to both named methods. If an earlier topic already changed this exact block to NEW, keep NEW and skip this repeated routing edit.

**OLD**

````python
        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.outline_tree.clear()
````

**NEW**

````python
        self._update_outline()
````

#### Step 27.14: `main.py` — MainWindow._apply_editor_settings: preserve large mode

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        # the phantom string). SCI_COLOURISE (4003) with (0, -1) forces the
        # NEW lexer to restyle the entire document right now.
        editor.SendScintilla(4003, 0, -1)
````

**NEW**

````python
        # the phantom string). SCI_COLOURISE (4003) with (0, -1) forces the
        # NEW lexer to restyle the entire document right now.
        editor.SendScintilla(4003, 0, -1)

        if getattr(editor, "large_file_mode", False):
            self._set_large_file_mode(editor, True)
````

#### Step 27.15: `main.py` — MainWindow._on_editor_text_changed: apply automatic size transitions

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self._dirty_editors.add(editor)
````

**NEW**

````python
        if not getattr(editor, '_large_file_override', False):
            large = editor.length() >= 2_000_000 or editor.lines() >= 50_000
            if large != getattr(editor, 'large_file_mode', False):
                self._set_large_file_mode(editor, large)
        self._dirty_editors.add(editor)
````

#### Step 27.16: `ruff_implementation/ruff_lsp_controller.py` — RuffLspController.sync_from_editor: avoid loading large text into Ruff

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def sync_from_editor(self):
````

**NEW**

````python
    def sync_from_editor(self):
        if getattr(self.editor, "large_file_mode", False):
            return
````

#### Step 27.17: `python_editor/pythoneditor.py` — PythonEditor.keyPressEvent: manual completion

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
                self._manual_completion_generation = self.auto_completer.get_completions(
````

**NEW**

````python
                if getattr(self, "large_file_mode", False):
                    return
                self._manual_completion_generation = self.auto_completer.get_completions(
````

#### Step 27.18: `main.py` — MainWindow._convert_editor: apply policy before loading text

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        new_editor.setTextSafely(text)
````

**NEW**

````python
        new_editor._large_file_override = getattr(old, "_large_file_override", False)
        self._set_large_file_mode(new_editor, getattr(old, "large_file_mode", False))
        new_editor.setTextSafely(text)
````

**Using this topic:** Large-file policy applies on open and after growth during editing. Toggle Large-file Mode changes the active tab’s override.


---

<a id="topic-28"></a>

## Topic 28: Shared analysis scheduling

### 1. Topic explanation

Serialize the existing Jedi completion, signature, documentation and definition providers on one application-owned worker queue. Replace superseded requests per provider, deliver on the GUI thread and discard stale document/caret/environment results. Ruff retains its own language-server protocol; semantic rename runs in its isolated process from Topic 14.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Executor/Future lifecycle](https://docs.python.org/3/library/concurrent.futures.html)
- [Jedi API and thread safety](https://jedi.readthedocs.io/en/latest/docs/api.html)
- [Qt queued connections](https://doc.qt.io/archives/qt-5.15/qt.html#ConnectionType-enum)

### 2. Topic code

#### `code_inteligence/analysis_key.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Immutable context for asynchronous analysis delivery."""
from dataclasses import dataclass

@dataclass(frozen=True)
class RequestKey:
    """Identity required to reject analysis produced for obsolete content."""

    path: str
    revision: int
    interpreter: str
    workspace: str
    kind: str

    document: str = ""
    line: int = 1
    column: int = 0
    source_hash: str = ""
````

| Definition | Responsibility |
|---|---|
| `RequestKey` | Identity required to reject analysis produced for obsolete content. |

#### `code_inteligence/analysis_scheduler.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""One application-owned worker queue for all Jedi providers and workspace scans."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, Future
from time import perf_counter
from PyQt5.QtCore import QCoreApplication, QObject, Qt, pyqtSignal
from code_inteligence.analysis_key import RequestKey


class AnalysisQueue(QObject):
    """Serialize immutable jobs; publish current results on the GUI thread.

    A lane is a (document identity, request kind) pair. The queue owns running
    jobs after tabs close. Worker closures must never capture an editor widget.
    """
    ready = pyqtSignal(object, object)
    measured = pyqtSignal(str, float)
    idle = pyqtSignal()
    _deliver = pyqtSignal(object, object, int, float)

    def __init__(self, parent=None):
        """Create one worker because Jedi's fast parser is not thread-safe."""
        super().__init__(parent)
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="editor-analysis")
        self.latest, self.pending_by_kind = {}, {}
        self.futures = set()
        self._serial, self._closing = 0, False
        self._deliver.connect(self._receive, Qt.QueuedConnection)

    def submit(self, key: RequestKey, work) -> None:
        """Replace pending work in one lane and reuse exact immutable results."""
        if self._closing:
            return
        lane = (key.document, key.kind)
        self._serial += 1
        serial = self._serial
        self.latest[lane] = (key, serial)
        previous = self.pending_by_kind.pop(lane, None)
        if previous is not None:
            previous.cancel()
        started = perf_counter()
        future = self.pool.submit(work)
        self.futures.add(future)
        self.pending_by_kind[lane] = future
        # Queue delivery even when the job completes before callback registration.
        future.add_done_callback(lambda done: self._deliver.emit(
            key, done, serial, perf_counter() - started))

    def _receive(self, key, future, serial, elapsed) -> None:
        """Drain futures and reject stale serials even when keys are identical."""
        self.futures.discard(future)
        lane = (key.document, key.kind)
        if self.pending_by_kind.get(lane) is future:
            self.pending_by_kind.pop(lane, None)
        self.measured.emit(key.kind, elapsed)
        if not self._closing and self.latest.get(lane) == (key, serial):
            try:
                value = future.result()
            except Exception as error:
                value = error
            self.ready.emit(key, value)
        if not self.futures:
            self.idle.emit()

    def cancel(self, document: str, kind: str | None = None) -> None:
        """Invalidate one provider or all providers belonging to a document."""
        for lane in list(self.latest):
            if lane[0] == document and (kind is None or lane[1] == kind):
                self.latest.pop(lane, None)
                future = self.pending_by_kind.pop(lane, None)
                if future is not None:
                    future.cancel()

    def invalidate_all(self) -> None:
        """Reject old environment results on workspace or interpreter changes."""
        self.latest.clear()
        for future in self.pending_by_kind.values():
            future.cancel()
        self.pending_by_kind.clear()

    def shutdown(self) -> None:
        """Stop submissions without blocking the GUI on running Python work."""
        if self._closing:
            return
        self._closing = True
        self.invalidate_all()
        self.pool.shutdown(wait=False, cancel_futures=True)

    def is_running(self) -> bool:
        """Keep application ownership until queued deliveries have drained."""
        return bool(self.futures)


def shared_analysis() -> AnalysisQueue:
    """Return the single analysis queue owned by the current QApplication."""
    app = QCoreApplication.instance()
    if app is None:
        raise RuntimeError("Create QApplication before analysis providers")
    queue = getattr(app, "_markdown_analysis_queue", None)
    if queue is None or queue._closing:
        queue = AnalysisQueue(app)
        app._markdown_analysis_queue = queue
    return queue
````

| Definition | Responsibility |
|---|---|
| `AnalysisQueue` | Serialize immutable jobs; publish current results on the GUI thread. |
| `AnalysisQueue.__init__` | Create one worker because Jedi's fast parser is not thread-safe. |
| `AnalysisQueue.submit` | Replace pending work in one lane and reuse exact immutable results. |
| `AnalysisQueue._receive` | Drain futures and reject stale serials even when keys are identical. |
| `AnalysisQueue.cancel` | Invalidate one provider or all providers belonging to a document. |
| `AnalysisQueue.invalidate_all` | Reject old environment results on workspace or interpreter changes. |
| `AnalysisQueue.shutdown` | Stop submissions without blocking the GUI on running Python work. |
| `AnalysisQueue.is_running` | Keep application ownership until queued deliveries have drained. |
| `shared_analysis` | Return the single analysis queue owned by the current QApplication. |

#### `code_inteligence/analysis_provider.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Immutable Jedi requests and adapters preserving existing editor signals."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import sys
import uuid
from PyQt5.QtCore import QObject, pyqtSignal
from code_inteligence.analysis_key import RequestKey
from code_inteligence.analysis_scheduler import shared_analysis


def evaluate(key: RequestKey, source: str):
    """Run in the worker, returning plain data without live Jedi or Qt objects.

    Script, Name and Signature objects remain inside this function. The selected
    interpreter and workspace determine imports and reference-search scope.
    """
    import jedi
    jedi.settings.fast_parser = False
    environment = jedi.create_environment(key.interpreter, safe=False)
    project = jedi.Project(key.workspace, environment_path=key.interpreter)
    script = jedi.Script(code=source, path=key.path or None,
                         environment=environment, project=project)
    if key.kind == "completion":
        return tuple(item.name for item in script.complete(key.line, key.column))
    if key.kind == "signature":
        results = script.get_signatures(key.line, key.column)
        if not results:
            return ""
        result = results[0]
        return f"{result.name}({', '.join(p.to_string() for p in result.params)})\n{result.docstring(raw=True)}".rstrip()
    if key.kind == "documentation":
        results = script.help(key.line, key.column)
        if not results:
            return ""
        result = results[0]
        return f"{result.name}\n({result.type})\n{result.docstring()}"
    if key.kind == "definition":
        results = script.goto(key.line, key.column, follow_imports=True)
        return next(((str(n.module_path), n.line, n.column) for n in results
                     if n.module_path is not None and n.line is not None), None)
    if key.kind == "references":
        return tuple((str(n.module_path), n.line - 1, n.column, n.name)
                     for n in script.get_references(key.line, key.column, include_builtins=False)
                     if n.module_path is not None and n.line is not None)
    raise ValueError(f"Unknown analysis kind: {key.kind}")


class AnalysisProvider(QObject):
    """Preserve generation-based APIs while sharing one application worker."""
    finished = pyqtSignal()

    def __init__(self, kind: str, editor=None):
        """Own GUI state only; application ownership keeps background jobs alive."""
        super().__init__(editor)
        self.kind, self.editor = kind, editor
        self.identity = str(uuid.uuid4())
        self.queue = shared_analysis()
        self.queue.ready.connect(self._receive)
        self._generation, self._key, self._shutting_down = 0, None, False
        self.file_path = None

    @property
    def generation(self):
        """Return the revision accepted by existing editor result slots."""
        return self._generation

    def context(self):
        """Read live workspace and interpreter values on the GUI thread."""
        window = self.editor.window() if self.editor is not None else None
        runner = getattr(window, "python_runner", None)
        interpreter = getattr(runner, "interpreter", sys.executable)
        root = Path(getattr(window, "_workspace_root", Path.cwd())).resolve()
        return str(interpreter), str(root)

    def request(self, line, column, source, path=None):
        """Capture text/caret/environment while honoring large-file policy."""
        if self._shutting_down:
            return None
        self.invalidate()
        if self.editor is not None and (getattr(self.editor, 'large_file_mode', False) or self.editor.length() >= 2_000_000):
            if not getattr(self.editor, '_large_file_override', False):
                return self._generation
        lines = source.splitlines() or [""]
        line = max(1, min(line, len(lines)))
        column = max(0, min(column, len(lines[line - 1])))
        interpreter, workspace = self.context()
        editor_path = getattr(self.editor, "path", None) if self.editor is not None else None
        path = str(editor_path or path or self.file_path or "")
        # A content digest and caret are needed: same-revision carets can differ.
        key = RequestKey(path, 0, interpreter, workspace, self.kind,
                         self.identity, line, column, sha256(source.encode()).hexdigest())
        self._key = key
        self.queue.submit(key, lambda: evaluate(key, source))
        return self._generation

    def _receive(self, key, value):
        """Check text, path and environment again before publishing results."""
        if self._shutting_down or key != self._key:
            return
        if self.context() != (key.interpreter, key.workspace):
            self.invalidate()
            return
        if self.editor is not None:
            if sha256(self.editor.text().encode()).hexdigest() != key.source_hash:
                self.invalidate()
                return
            if str(getattr(self.editor, "path", None) or "") != key.path:
                self.invalidate()
                return
        self._key = None
        self.deliver(self._generation, value)
        self.finished.emit()

    def deliver(self, generation, value):
        """Require each adapter to translate plain results to its public signals."""
        raise NotImplementedError

    def invalidate(self):
        """Cancel queued work and reject any running result from this provider."""
        self._generation += 1
        self._key = None
        self.queue.cancel(self.identity, self.kind)

    def isRunning(self):
        """Report delivery state for the existing asynchronous editor close path."""
        return self._key is not None

    def shutdown(self):
        """Detach the editor while immutable jobs remain queue-owned."""
        self._shutting_down = True
        self.invalidate()
        self.finished.emit()
````

| Definition | Responsibility |
|---|---|
| `evaluate` | Run in the worker, returning plain data without live Jedi or Qt objects. |
| `AnalysisProvider` | Preserve generation-based APIs while sharing one application worker. |
| `AnalysisProvider.__init__` | Own GUI state only; application ownership keeps background jobs alive. |
| `AnalysisProvider.generation` | Return the revision accepted by existing editor result slots. |
| `AnalysisProvider.context` | Read live workspace and interpreter values on the GUI thread. |
| `AnalysisProvider.request` | Capture text/caret/environment while honoring large-file policy. |
| `AnalysisProvider._receive` | Check text, path and environment again before publishing results. |
| `AnalysisProvider.deliver` | Require each adapter to translate plain results to its public signals. |
| `AnalysisProvider.invalidate` | Cancel queued work and reject any running result from this provider. |
| `AnalysisProvider.isRunning` | Report delivery state for the existing asynchronous editor close path. |
| `AnalysisProvider.shutdown` | Detach the editor while immutable jobs remain queue-owned. |

#### `code_inteligence/autocompleter.py` — updated existing module

Read the complete target implementation below. The implementation section shows the exact existing-code edits; do not paste this as a second class or a second module.

````python
"""Shared-queue adapter for autocompleter."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class AutoCompleter(AnalysisProvider):
    """Deliver plain completion names to the editor's existing QsciAPIs list."""
    completions_ready = pyqtSignal(int, list)
    error = pyqtSignal(str)

    def __init__(self, file_path=None, api=None, editor=None):
        """Keep the legacy constructor arguments while accepting the owning tab."""
        super().__init__("completion", editor)
        self.file_path, self.api = file_path, api

    def get_completions(self, line, index, text):
        """Submit a captured buffer and return its UI generation."""
        return self.request(line, index, text, self.file_path)

    def deliver(self, generation, value):
        """Convert immutable worker results to the existing list signal."""
        if isinstance(value, Exception):
            self.error.emit(str(value))
        else:
            self.completions_ready.emit(generation, list(value))
````

| Definition | Responsibility |
|---|---|
| `AutoCompleter` | Deliver plain completion names to the editor's existing QsciAPIs list. |
| `AutoCompleter.__init__` | Keep the legacy constructor arguments while accepting the owning tab. |
| `AutoCompleter.get_completions` | Submit a captured buffer and return its UI generation. |
| `AutoCompleter.deliver` | Convert immutable worker results to the existing list signal. |

#### `code_inteligence/signature_helper.py` — updated existing module

Read the complete target implementation below. The implementation section shows the exact existing-code edits; do not paste this as a second class or a second module.

````python
"""Shared-queue adapter for signature helper."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class SignatureHelper(AnalysisProvider):
    """Publish signature text from the shared queue."""
    signature_ready = pyqtSignal(int, str)
    signature_empty = pyqtSignal(int)

    def __init__(self, editor=None):
        """Bind the provider to the tab supplying environment and size policy."""
        super().__init__("signature", editor)

    def get_signatures(self, line, column, code, file_path=None):
        """Submit a call-site snapshot using Jedi's one-based line numbers."""
        return self.request(line, column, code, file_path)

    def deliver(self, generation, value):
        """Publish a signature or request dismissal of an obsolete tooltip."""
        if isinstance(value, Exception) or not value:
            self.signature_empty.emit(generation)
        else:
            self.signature_ready.emit(generation, value)
````

| Definition | Responsibility |
|---|---|
| `SignatureHelper` | Publish signature text from the shared queue. |
| `SignatureHelper.__init__` | Bind the provider to the tab supplying environment and size policy. |
| `SignatureHelper.get_signatures` | Submit a call-site snapshot using Jedi's one-based line numbers. |
| `SignatureHelper.deliver` | Publish a signature or request dismissal of an obsolete tooltip. |

#### `code_inteligence/hover_helper.py` — updated existing module

Read the complete target implementation below. The implementation section shows the exact existing-code edits; do not paste this as a second class or a second module.

````python
"""Shared-queue adapter for hover helper."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class HoverHelper(AnalysisProvider):
    """Provide explicitly requested documentation through shared analysis."""
    hover_info_ready = pyqtSignal(int, str)
    hover_info_empty = pyqtSignal(int)

    def __init__(self, editor=None):
        """Capture the owning tab without exposing it to the worker."""
        super().__init__("documentation", editor)

    def get_hover(self, line, column, code, file_path=None):
        """Submit the identifier selected by the documentation action."""
        return self.request(line, column, code, file_path)

    def deliver(self, generation, value):
        """Pass escaped-by-the-popup text, never live Jedi objects, to the UI."""
        if isinstance(value, Exception) or not value:
            self.hover_info_empty.emit(generation)
        else:
            self.hover_info_ready.emit(generation, value)
````

| Definition | Responsibility |
|---|---|
| `HoverHelper` | Provide explicitly requested documentation through shared analysis. |
| `HoverHelper.__init__` | Capture the owning tab without exposing it to the worker. |
| `HoverHelper.get_hover` | Submit the identifier selected by the documentation action. |
| `HoverHelper.deliver` | Pass escaped-by-the-popup text, never live Jedi objects, to the UI. |

#### `code_inteligence/definition_finder.py` — updated existing module

Read the complete target implementation below. The implementation section shows the exact existing-code edits; do not paste this as a second class or a second module.

````python
"""Shared-queue adapter for definition finder."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class DefinitionFinder(AnalysisProvider):
    """Resolve definitions without a separate QThread or concurrent Jedi call."""
    definition_found = pyqtSignal(int, str, int, int)
    definition_not_found = pyqtSignal(int)
    error = pyqtSignal(int, str)

    def __init__(self, editor=None):
        """Use the same queue and environment as completion and documentation."""
        super().__init__("definition", editor)

    def find(self, line, column, code, file_path=None):
        """Submit a definition request for an immutable source snapshot."""
        return self.request(line, column, code, file_path)

    def deliver(self, generation, value):
        """Preserve one-based result lines expected by PythonEditor."""
        if isinstance(value, Exception):
            self.error.emit(generation, str(value))
        elif value is None:
            self.definition_not_found.emit(generation)
        else:
            self.definition_found.emit(generation, *value)
````

| Definition | Responsibility |
|---|---|
| `DefinitionFinder` | Resolve definitions without a separate QThread or concurrent Jedi call. |
| `DefinitionFinder.__init__` | Use the same queue and environment as completion and documentation. |
| `DefinitionFinder.find` | Submit a definition request for an immutable source snapshot. |
| `DefinitionFinder.deliver` | Preserve one-based result lines expected by PythonEditor. |

### 3. Topic implementation — exact files and methods

#### Step 28.1: create `code_inteligence/analysis_key.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 28.2: create `code_inteligence/analysis_scheduler.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 28.3: create `code_inteligence/analysis_provider.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 28.4: `code_inteligence/autocompleter.py` — `module`

Replace only the following contiguous block. The context is from the pinned repository; keep all surrounding definitions.

**OLD**

````python
from PyQt5.QtCore import QThread, pyqtSignal
from jedi import Script


class AutoCompleter(QThread):
    completions_ready = pyqtSignal(int, list)
    error = pyqtSignal(str)

    def __init__(self, file_path, api=None):
        super().__init__(None)
        self.file_path = file_path
        self.api = api
        self._generation = 0
        self._running_generation = 0
        self._request = (1, 0, "")
        self._pending = None
        self._shutting_down = False
        self.finished.connect(self._start_pending)

    def get_completions(self, line, index, text):
        if self._shutting_down:
            return None
        self._generation += 1
        request = (self._generation, line, index, text)
        if self.isRunning():
            self._pending = request
        else:
            self._start_request(request)
        return self._generation

    def invalidate(self):
        """Invalidate a running result when the editor revision/position changes."""
        self._generation += 1
        self._pending = None

    def _start_request(self, request):
        generation, line, index, text = request
        lines = text.splitlines() or [""]
        line = max(1, min(line, len(lines)))
        index = max(0, min(index, len(lines[line - 1])))
        self._running_generation = generation
        self._request = (line, index, text)
        self.start()

    def _start_pending(self):
        if not self._shutting_down and self._pending is not None:
            request, self._pending = self._pending, None
            self._start_request(request)

    def run(self):
        try:
            line, index, text = self._request
            names = [item.name for item in Script(
                code=text, path=self.file_path
            ).complete(line, index)]
            if not self._shutting_down:
                self.completions_ready.emit(self._running_generation, names)
        except Exception as error:
            if not self._shutting_down:
                self.error.emit(str(error))

    def shutdown(self):
        self._shutting_down = True
        self._pending = None
        self.requestInterruption()

    @property
    def generation(self):
        return self._generation
````

**NEW**

````python
"""Shared-queue adapter for autocompleter."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class AutoCompleter(AnalysisProvider):
    """Deliver plain completion names to the editor's existing QsciAPIs list."""
    completions_ready = pyqtSignal(int, list)
    error = pyqtSignal(str)

    def __init__(self, file_path=None, api=None, editor=None):
        """Keep the legacy constructor arguments while accepting the owning tab."""
        super().__init__("completion", editor)
        self.file_path, self.api = file_path, api

    def get_completions(self, line, index, text):
        """Submit a captured buffer and return its UI generation."""
        return self.request(line, index, text, self.file_path)

    def deliver(self, generation, value):
        """Convert immutable worker results to the existing list signal."""
        if isinstance(value, Exception):
            self.error.emit(str(value))
        else:
            self.completions_ready.emit(generation, list(value))
````

#### Step 28.5: `code_inteligence/signature_helper.py` — `module`

Replace only the following contiguous block. The context is from the pinned repository; keep all surrounding definitions.

**OLD**

````python
from PyQt5.QtCore import QThread, pyqtSignal
from jedi import Script


class SignatureHelper(QThread):
    """Run Jedi signature lookups and discard superseded results."""

    signature_ready = pyqtSignal(int, str)
    signature_empty = pyqtSignal(int)

    def __init__(self):
        super().__init__(None)
        self._generation = 0
        self._request = None
        self._pending = None
        self._shutting_down = False
        self.finished.connect(self._start_pending)

    def get_signatures(self, line: int, column: int, code: str, file_path: str = None):
        if self._shutting_down:
            return
        self._generation += 1
        request = (self._generation, line, column, code, file_path)
        if self.isRunning():
            self._pending = request
            return
        self._request = request
        self.start()

    def invalidate(self):
        self._generation += 1
        self._pending = None

    def _start_pending(self):
        if self._shutting_down or self._pending is None:
            return
        self._request, self._pending = self._pending, None
        self.start()

    def run(self):
        generation, line, column, code, file_path = self._request
        try:
            signatures = Script(code=code, path=file_path).get_signatures(
                line=line, column=column
            )
            if self._shutting_down:
                return
            if not signatures:
                self.signature_empty.emit(generation)
                return
            signature = signatures[0]
            params = [param.to_string() for param in signature.params]
            result = f"{signature.name}({', '.join(params)})"
            docstring = signature.docstring(raw=True)
            if docstring:
                result += f"\n{docstring}"
            self.signature_ready.emit(generation, result)
        except Exception:
            if not self._shutting_down:
                self.signature_empty.emit(generation)

    @property
    def generation(self):
        return self._generation

    def shutdown(self):
        self._shutting_down = True
        self._pending = None
        self.requestInterruption()
````

**NEW**

````python
"""Shared-queue adapter for signature helper."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class SignatureHelper(AnalysisProvider):
    """Publish signature text from the shared queue."""
    signature_ready = pyqtSignal(int, str)
    signature_empty = pyqtSignal(int)

    def __init__(self, editor=None):
        """Bind the provider to the tab supplying environment and size policy."""
        super().__init__("signature", editor)

    def get_signatures(self, line, column, code, file_path=None):
        """Submit a call-site snapshot using Jedi's one-based line numbers."""
        return self.request(line, column, code, file_path)

    def deliver(self, generation, value):
        """Publish a signature or request dismissal of an obsolete tooltip."""
        if isinstance(value, Exception) or not value:
            self.signature_empty.emit(generation)
        else:
            self.signature_ready.emit(generation, value)
````

#### Step 28.6: `code_inteligence/hover_helper.py` — `module`

Replace only the following contiguous block. The context is from the pinned repository; keep all surrounding definitions.

**OLD**

````python
from PyQt5.QtCore import QThread, pyqtSignal
from jedi import Script


class HoverHelper(QThread):
    """Run Jedi hover lookups while always replaying the newest request."""

    hover_info_ready = pyqtSignal(int, str)
    hover_info_empty = pyqtSignal(int)

    def __init__(self):
        super().__init__(None)
        self._generation = 0
        self._request = None
        self._pending = None
        self._shutting_down = False
        self.finished.connect(self._start_pending)

    def get_hover(self, line: int, column: int, code: str, file_path: str = None):
        if self._shutting_down:
            return
        self._generation += 1
        request = (self._generation, line, column, code, file_path)
        if self.isRunning():
            self._pending = request
            return
        self._request = request
        self.start()

    def invalidate(self):
        self._generation += 1
        self._pending = None

    def _start_pending(self):
        if self._shutting_down or self._pending is None:
            return
        self._request, self._pending = self._pending, None
        self.start()

    def run(self):
        generation, line, column, code, file_path = self._request
        try:
            results = Script(code=code, path=file_path).help(line=line, column=column)
            if self._shutting_down:
                return
            if not results:
                self.hover_info_empty.emit(generation)
                return
            name = results[0]
            parts = [name.name] if name.name else []
            if name.type:
                parts.append(f"({name.type})")
            try:
                docstring = name.docstring()
            except (AttributeError, TypeError):
                docstring = name.docstring_raw()
            if docstring:
                parts.append("\n" + docstring)
            if parts:
                self.hover_info_ready.emit(generation, "\n".join(parts))
            else:
                self.hover_info_empty.emit(generation)
        except Exception:
            if not self._shutting_down:
                self.hover_info_empty.emit(generation)

    @property
    def generation(self):
        return self._generation

    def shutdown(self):
        self._shutting_down = True
        self._pending = None
        self.requestInterruption()
````

**NEW**

````python
"""Shared-queue adapter for hover helper."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class HoverHelper(AnalysisProvider):
    """Provide explicitly requested documentation through shared analysis."""
    hover_info_ready = pyqtSignal(int, str)
    hover_info_empty = pyqtSignal(int)

    def __init__(self, editor=None):
        """Capture the owning tab without exposing it to the worker."""
        super().__init__("documentation", editor)

    def get_hover(self, line, column, code, file_path=None):
        """Submit the identifier selected by the documentation action."""
        return self.request(line, column, code, file_path)

    def deliver(self, generation, value):
        """Pass escaped-by-the-popup text, never live Jedi objects, to the UI."""
        if isinstance(value, Exception) or not value:
            self.hover_info_empty.emit(generation)
        else:
            self.hover_info_ready.emit(generation, value)
````

#### Step 28.7: `code_inteligence/definition_finder.py` — `module`

Replace only the following contiguous block. The context is from the pinned repository; keep all surrounding definitions.

**OLD**

````python
from PyQt5.QtCore import QThread, pyqtSignal
from jedi import Script


class DefinitionFinder(QThread):
    """Find definitions asynchronously and replay the most recent request."""

    definition_found = pyqtSignal(int, str, int, int)
    definition_not_found = pyqtSignal(int)
    error = pyqtSignal(int, str)

    def __init__(self):
        super().__init__(None)
        self._generation = 0
        self._request = None
        self._pending = None
        self._shutting_down = False
        self.finished.connect(self._start_pending)

    def find(self, line: int, column: int, code: str, file_path: str = None):
        if self._shutting_down:
            return
        self._generation += 1
        request = (self._generation, line, column, code, file_path)
        if self.isRunning():
            self._pending = request
            return
        self._request = request
        self.start()

    def invalidate(self):
        self._generation += 1
        self._pending = None

    def _start_pending(self):
        if self._shutting_down or self._pending is None:
            return
        self._request, self._pending = self._pending, None
        self.start()

    def run(self):
        generation, line, column, code, file_path = self._request
        try:
            definitions = Script(code=code, path=file_path).goto(
                line=line, column=column, follow_imports=True
            )
            if self._shutting_down:
                return
            if not definitions or definitions[0].module_path is None:
                self.definition_not_found.emit(generation)
                return
            definition = definitions[0]
            self.definition_found.emit(
                generation, str(definition.module_path), definition.line, definition.column
            )
        except Exception as exc:
            if not self._shutting_down:
                self.error.emit(generation, str(exc))

    @property
    def generation(self):
        return self._generation

    def shutdown(self):
        self._shutting_down = True
        self._pending = None
        self.requestInterruption()
````

**NEW**

````python
"""Shared-queue adapter for definition finder."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class DefinitionFinder(AnalysisProvider):
    """Resolve definitions without a separate QThread or concurrent Jedi call."""
    definition_found = pyqtSignal(int, str, int, int)
    definition_not_found = pyqtSignal(int)
    error = pyqtSignal(int, str)

    def __init__(self, editor=None):
        """Use the same queue and environment as completion and documentation."""
        super().__init__("definition", editor)

    def find(self, line, column, code, file_path=None):
        """Submit a definition request for an immutable source snapshot."""
        return self.request(line, column, code, file_path)

    def deliver(self, generation, value):
        """Preserve one-based result lines expected by PythonEditor."""
        if isinstance(value, Exception):
            self.error.emit(generation, str(value))
        elif value is None:
            self.definition_not_found.emit(generation)
        else:
            self.definition_found.emit(generation, *value)
````

#### Step 28.8: `python_editor/pythoneditor.py` — PythonEditor.__init__: pass provider owner

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
self.signature_helper = SignatureHelper()
````

**NEW**

````python
self.signature_helper = SignatureHelper(self)
````

#### Step 28.9: `python_editor/pythoneditor.py` — PythonEditor.__init__: pass provider owner

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
self.hover_helper = HoverHelper()
````

**NEW**

````python
self.hover_helper = HoverHelper(self)
````

#### Step 28.10: `python_editor/pythoneditor.py` — PythonEditor.__init__: pass provider owner

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
self.definition_finder = DefinitionFinder()
````

**NEW**

````python
self.definition_finder = DefinitionFinder(self)
````

#### Step 28.11: `python_editor/pythoneditor.py` — PythonEditor.__init__: pass provider owner

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
str(self.full_path) if self.full_path else None, self._api
````

**NEW**

````python
str(self.full_path) if self.full_path else None, self._api, self
````

#### Step 28.12: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from code_inteligence.analysis_scheduler import shared_analysis
````

#### Step 28.13: `main.py` — MainWindow.__init__: immediately after init_ui()

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self.analysis_queue = shared_analysis()
````

#### Step 28.14: `main.py` — MainWindow._restart_ruff: invalidate environment-bound work

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        old_client = self.ruff_lsp_client
````

**NEW**

````python
        shared_analysis().invalidate_all()
        old_client = self.ruff_lsp_client
````

#### Step 28.15: `main.py` — MainWindow.closeEvent: stop owned work

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.terminal.stop()
````

**NEW**

````python
        self.analysis_queue.shutdown()
        self.terminal.stop()
````

**If Topic 23 is already installed:** the terminal stop is guarded. Insert this topic’s shutdown statements immediately **before** that guard, using:

````python
        self.analysis_queue.shutdown()
        if self.terminal is not None:
            self.terminal.stop()
````

#### Step 28.16: `main.py` — MainWindow._background_work_running: retain worker ownership

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _background_work_running(self) -> bool:
````

**NEW**

````python
    def _background_work_running(self) -> bool:
        if getattr(self, 'analysis_queue', None) is not None and self.analysis_queue.is_running():
            return True
````

**Using this topic:** Completion, signatures, documentation and Go to Definition keep their existing commands while sharing the owned queue.


---

<a id="topic-29"></a>

## Topic 29: Bounded result caching

### 1. Topic explanation

Cache successful exact-context analysis results using bounded LRU retention by both entry count and estimated bytes. Keys include source digest, path, document, caret, request kind, workspace and interpreter. Cache hits are delivered asynchronously through the same stale-request checks; environment changes clear the cache.

**Prerequisites:** Topic 28

**Documentation used:**

- [OrderedDict LRU operations](https://docs.python.org/3/library/collections.html#collections.OrderedDict)
- [Python object sizes](https://docs.python.org/3/library/sys.html#sys.getsizeof)

### 2. Topic code

#### `code_inteligence/analysis_cache.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Bounded LRU storage for plain immutable analysis results."""
from collections import OrderedDict
import sys

class LRU:
    """Bound entry count and estimated Python object memory."""
    def __init__(self, size=64, max_bytes=4_000_000):
        """Reject invalid limits instead of silently disabling eviction."""
        if size < 1 or max_bytes < 1:
            raise ValueError('Cache limits must be positive')
        self.size, self.max_bytes = size, max_bytes
        self.values, self.costs, self.bytes = OrderedDict(), {}, 0

    def get(self, key):
        """Promote an existing key; membership distinguishes cached None."""
        self.values.move_to_end(key)
        return self.values[key]

    def put(self, key, value):
        """Never retain a single oversized result or any QWidget/Jedi object."""
        def cost(item, seen):
            """Estimate nested immutable containers without double-counting."""
            if id(item) in seen:
                return 0
            seen.add(id(item))
            total = sys.getsizeof(item)
            if isinstance(item, (tuple, list)):
                total += sum(cost(child, seen) for child in item)
            elif isinstance(item, dict):
                total += sum(cost(k, seen) + cost(v, seen) for k, v in item.items())
            elif hasattr(item, '__dict__'):
                total += cost(vars(item), seen)
            return total
        amount = cost((key, value), set())
        if key in self.values:
            self.values.pop(key)
            self.bytes -= self.costs.pop(key)
        if amount > self.max_bytes:
            return
        self.values[key] = value
        self.costs[key] = amount
        self.bytes += amount
        while len(self.values) > self.size or self.bytes > self.max_bytes:
            oldest, _ = self.values.popitem(last=False)
            self.bytes -= self.costs.pop(oldest)

    def clear(self):
        """Invalidate environment-dependent data and accounting together."""
        self.values.clear()
        self.costs.clear()
        self.bytes = 0
````

| Definition | Responsibility |
|---|---|
| `LRU` | Bound entry count and estimated Python object memory. |
| `LRU.__init__` | Reject invalid limits instead of silently disabling eviction. |
| `LRU.get` | Promote an existing key; membership distinguishes cached None. |
| `LRU.put` | Never retain a single oversized result or any QWidget/Jedi object. |
| `LRU.clear` | Invalidate environment-dependent data and accounting together. |

### 3. Topic implementation — exact files and methods

#### Step 29.1: create `code_inteligence/analysis_cache.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 29.2: `code_inteligence/analysis_scheduler.py` — module imports added in Topic 28

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from code_inteligence.analysis_key import RequestKey
````

**NEW**

````python
from code_inteligence.analysis_key import RequestKey
from code_inteligence.analysis_cache import LRU
````

#### Step 29.3: `code_inteligence/analysis_scheduler.py` — AnalysisQueue.__init__

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.futures = set()
````

**NEW**

````python
        self.futures = set()
        self.cache = LRU()
````

#### Step 29.4: `code_inteligence/analysis_scheduler.py` — AnalysisQueue.submit: queued cache delivery

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        started = perf_counter()
````

**NEW**

````python
        if key in self.cache.values:
            future = Future()
            future.set_result(self.cache.get(key))
            self.futures.add(future)
            self._deliver.emit(key, future, serial, 0.0)
            return
        started = perf_counter()
````

#### Step 29.5: `code_inteligence/analysis_scheduler.py` — AnalysisQueue._receive: cache only current successful results

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
            self.ready.emit(key, value)
````

**NEW**

````python
            if not isinstance(value, Exception):
                self.cache.put(key, value)
            self.ready.emit(key, value)
````

#### Step 29.6: `code_inteligence/analysis_scheduler.py` — AnalysisQueue.invalidate_all

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.latest.clear()
````

**NEW**

````python
        self.latest.clear()
        self.cache.clear()
````

**Using this topic:** No new command is required. The queue reuses successful exact-context results and evicts older or oversized values.


---

<a id="topic-30"></a>

## Topic 30: Pause hidden-panel work

### 1. Topic explanation

Pause parsing and tree reconstruction for the real Outline panel while hidden. Record invalidation and refresh from the active buffer after Show. The preview has its own visibility handling in Topic 26; Tests must keep collecting outcomes while hidden. No diagnostics are discarded and no invented Problems/References/minimap dock is added.

**Prerequisites:** None; apply directly to the pinned baseline.

**Documentation used:**

- [Qt 5.15 QWidget](https://doc.qt.io/archives/qt-5.15/qwidget.html)
- [Qt 5.15 QEvent](https://doc.qt.io/archives/qt-5.15/qevent.html)
- [Qt 5.15 QTimer](https://doc.qt.io/archives/qt-5.15/qtimer.html)

### 2. Topic code

#### `side_bar_widgets/visibility_refresh.py` — new module

Create this file in its existing source folder and paste this complete module at line 1. No extra package directory is required.

````python
"""Trigger a refresh after a widget is shown and layout state has settled."""
from PyQt5.QtCore import QObject, QEvent, QTimer

class VisibilityRefresh(QObject):
    """A small event filter with a Qt-owned deferred callback."""
    def __init__(self, widget, callback):
        super().__init__(widget)
        self.callback = callback
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(callback)
        widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        """Queue once when shown; do not consume the event."""
        if event.type() == QEvent.Show:
            self.timer.start(0)
        return False
````

| Definition | Responsibility |
|---|---|
| `VisibilityRefresh` | A small event filter with a Qt-owned deferred callback. |
| `VisibilityRefresh.eventFilter` | Queue once when shown; do not consume the event. |

### 3. Topic implementation — exact files and methods

#### Step 30.1: create `side_bar_widgets/visibility_refresh.py`

Use the complete module from section 2. **OLD:** no file in the baseline. **NEW:** the complete named module above. Do not delete another file.

#### Step 30.2: `main.py` — module imports

Add these imports once at module scope, alongside the displayed existing import. Preserve other topics’ imports already below the same anchor.

**OLD**

````python
from markdown_python_editor import __version__
````

**NEW**

````python
from markdown_python_editor import __version__
from side_bar_widgets.visibility_refresh import VisibilityRefresh
````

#### Step 30.3: `main.py` — MainWindow.__init__, immediately after init_ui

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
        self.init_ui()
````

**NEW**

````python
        self.init_ui()
        self._outline_visibility = VisibilityRefresh(self.outline_tree, self._update_outline)
````

#### Step 30.4: `main.py` — MainWindow.set_new_tab AND _on_current_editor_changed (skip if topic 20 already replaced these blocks)

Apply to both named methods. If an earlier topic already changed this exact block to NEW, keep NEW and skip this repeated routing edit.

**OLD**

````python
        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.outline_tree.clear()
````

**NEW**

````python
        self._update_outline()
````

#### Step 30.5: `main.py` — MainWindow._update_outline: visibility guard

Replace only the displayed block in the named method/location. Retain adjacent additions from earlier topics.

**OLD**

````python
    def _update_outline(self):
````

**NEW**

````python
    def _update_outline(self):
        if not self.outline_tree.isVisible():
            self._outline_dirty = True
            return
        self._outline_dirty = False
````

**Using this topic:** Hide Outline while editing, then show it. It refreshes from the current document rather than rebuilding the hidden tree on every debounce.


---

## Reference-guide review notes

| Attached guide | How it informed this revision |
|---|---|
| `CodeEditor_Implementation_12(1).md` | Restored fuller behavior for navigation, profiles, pytest results, authoring and Python/Cython checkpoints; removed the need for its final all-feature controller |
| `CodeEditor_Implementation_11(1).md` | Used its topic-local implementation structure and ownership/dirty-state practices; its separate 11 features are not implicitly installed |
| `MarkdownEditor_DIAGNOSTICS_AND_HIGHLIGHTING_FIX_GUIDE(1).md` | Preserved current worker shutdown, lexer ownership and Ruff integration rather than replacing them wholesale with an older snapshot |
| `MarkdownEditor_FEATURE_IMPLEMENTATION_GUIDE(2).md` | Cross-checked command reuse, Unicode edit coordinates and document lifecycle boundaries |
| `MarkdownEditor_COMPLETE_NEW_IMPLEMENTATION_GUIDE_2026-10-28(1).md` | Retained the original 30-topic scope and corrected invalid paths, missing operations and disconnected hooks |
| `MarkdownEditor_TYPE_AND_SPELLING_IMPLEMENTATION_GUIDE (2).md` | Followed its explicit OLD → NEW method-level structure and stale-result/Qt-lifetime safeguards; did not invent installed type/spelling modules |

Keep the current repository’s preview sanitization, atomic saves, external revision digest, Ruff process and asynchronous close machinery. This guide extends their actual methods and shows the relevant changes inside each topic.
