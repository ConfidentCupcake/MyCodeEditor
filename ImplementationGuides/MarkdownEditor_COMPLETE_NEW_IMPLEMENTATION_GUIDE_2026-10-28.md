# MarkdownEditor: 30-Feature Repository Integration Guide

**Repository:** https://github.com/ConfidentCupcake/MarkdownEditor  
**Inspected GitHub commit:** `b26bf8df9b6c99153a3591a258c368256c8d2590`  
**Run command:** `python main.py` (PyCharm terminal, activated virtual environment)

This is a **new standalone guide**, organized by the requested seven steps for each feature. The feature modules below are original implementations, not copied from the previous reference course. Integration snippets identify existing `MainWindow` methods and show the actual Python to insert or replace. Quoted BEFORE snippets are from the inspected GitHub revision. When a feature adds code without removing anything, the section explicitly says so.

**Important accuracy boundary:** The repository tree and several key methods in `main.py`, `MarkdownEditor`, and `PythonEditor` were checked against GitHub. Some existing panel and lexer internals have not been exhaustively inspected, and the 30 features have not been installed and GUI-tested as one system. The code is an implementation starting point, **not a verified ready-to-apply patch**. The guide flags integrations that still need repository-specific adaptation. Do not interpret unverified integrations as exact working diffs.

## Before feature 1

```powershell
git status --short
git rev-parse HEAD
git switch -c feature/editor-30-features
python -m pytest -q
python main.py
```

Use a clean branch. If your HEAD differs, re-check the BEFORE code. After each feature, run `python -m compileall -q .`, `python -m pytest -q`, and `python main.py`. Commit only after testing.

## Contents

- [Feature 01: Unified design system](#feature-01)
- [Feature 02: Consistent SVG icons](#feature-02)
- [Feature 03: Breadcrumb navigation](#feature-03)
- [Feature 04: Compact and comfortable layouts](#feature-04)
- [Feature 05: Improved status bar](#feature-05)
- [Feature 06: Polished empty states](#feature-06)
- [Feature 07: Welcome screen](#feature-07)
- [Feature 08: Focus mode](#feature-08)
- [Feature 09: Workspace layout presets](#feature-09)
- [Feature 10: Automatic recovery](#feature-10)
- [Feature 11: Local file history](#feature-11)
- [Feature 12: External-change comparison](#feature-12)
- [Feature 13: Compare/diff editor](#feature-13)
- [Feature 14: Rename symbol with preview](#feature-14)
- [Feature 15: Workspace symbol search](#feature-15)
- [Feature 16: Test runner panel](#feature-16)
- [Feature 17: Run configurations](#feature-17)
- [Feature 18: Configurable keyboard shortcuts](#feature-18)
- [Feature 19: Smarter pair handling](#feature-19)
- [Feature 20: Outline and navigation](#feature-20)
- [Feature 21: Authoring tools](#feature-21)
- [Feature 22: Performance diagnostics mode](#feature-22)
- [Feature 23: Lazy initialization](#feature-23)
- [Feature 24: Background file hashing](#feature-24)
- [Feature 25: Incremental syntax highlighting](#feature-25)
- [Feature 26: Smarter Markdown preview updates](#feature-26)
- [Feature 27: Large-file mode](#feature-27)
- [Feature 28: Shared analysis scheduling](#feature-28)
- [Feature 29: Bounded result caching](#feature-29)
- [Feature 30: Pause hidden-panel work](#feature-30)

---

## Feature 01: Unified design system

### 1. The feature

**Unified design system.**

### 2. What the feature does

Give Qt widgets one semantic palette and consistent spacing without changing lexer-owned syntax colors.

### 3. Exact file operation

**REPLACE existing file:** `code_settings/design_settings.py`. Keep the path and overwrite its content with the following complete module after checking imports elsewhere.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.init_ui, after the existing stylesheet try/except`.

### 4. The code for the feature

```python
"""Shared Qt widget design tokens. Existing module: replace its contents."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DesignTokens:
    paper: str = '#1e1f22'
    surface: str = '#262a33'
    foreground: str = '#dcdfe4'
    muted: str = '#969ba7'
    accent: str = '#61afef'
    border: str = '#3d424d'


def theme_qss(density: str = 'comfortable', tokens: DesignTokens | None = None) -> str:
    """Return deterministic widget styles; never append styles to themselves."""
    if density not in {'compact', 'comfortable'}:
        raise ValueError(f'Unsupported density: {density}')
    t = tokens or DesignTokens()
    padding = 3 if density == 'compact' else 7
    return f"""
    QMenu, QToolTip {{ background: {t.surface}; color: {t.foreground}; border: 1px solid {t.border}; }}
    QDockWidget::title {{ background: {t.surface}; color: {t.foreground}; padding: {padding}px; }}
    QPushButton, QToolButton {{ color: {t.foreground}; border: 1px solid {t.border}; padding: {padding}px; }}
    QPushButton:hover, QToolButton:hover {{ border-color: {t.accent}; }}
    QTabBar::tab {{ background: {t.surface}; color: {t.foreground}; padding: {padding}px 12px; }}
    QTabBar::tab:selected {{ border-bottom: 2px solid {t.accent}; }}
    """
```

**Why this implementation:** Immutable tokens make accidental palette mutation impossible. Keeping styles on widgets rather than lexers preserves editor syntax highlighting.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.init_ui, after the existing stylesheet try/except`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_settings.design_settings import theme_qss

# INSERT at end of the existing stylesheet try/except in init_ui:
self._base_qss = self.styleSheet()
self.setStyleSheet(self._base_qss + "\n" + theme_qss())
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING at the end of the stylesheet loader:
except FileNotFoundError as e:
    print(f"STYLESHEET ERROR: {e}")
    # Fallback: apply basic dark styling inline
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Open both editor types; check menu, dock title, tabs, hover states. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 02: Consistent SVG icons

### 1. The feature

**Consistent SVG icons.**

### 2. What the feature does

Resolve known SVG assets from the existing package, including active-state variants.

### 3. Exact file operation

**REPLACE existing file:** `markdowneditor_assets/icon_provider.py`. Keep the path and overwrite its content with the following complete module after checking imports elsewhere.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow._set_sidebar_icon and MainWindow.get_sidebar_label`.

### 4. The code for the feature

```python
"""Validated icon access for existing bundled SVG assets."""
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
        icon.addFile(str(selected), mode=QIcon.Normal, state=QIcon.On)
    return icon
```

**Why this implementation:** An allowlist prevents accidental arbitrary resource lookups; QIcon handles disabled rendering and state switching.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow._set_sidebar_icon and MainWindow.get_sidebar_label`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from markdowneditor_assets.icon_provider import themed_icon

# REPLACE MainWindow._set_sidebar_icon completely:
def _set_sidebar_icon(self, name: str, active: bool):
    label = self.sidebar_labels.get(name)
    if label is not None:
        label.setPixmap(themed_icon(name).pixmap(QSize(25, 25),
            QIcon.Normal, QIcon.On if active else QIcon.Off))

# REPLACE the first label.setPixmap(...) statement in get_sidebar_label:
label.setPixmap(themed_icon(name).pixmap(QSize(25, 25)))
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
def _set_sidebar_icon(self, name: str, active: bool):
    """Reflect a tool's actual visibility using the existing icon variants."""
    label = self.sidebar_labels.get(name)
    if label is not None:
        suffix = "-active" if active else ""
        label.setPixmap(
            QPixmap(resource_path(f"icons/{name}{suffix}.png")).scaled(QSize(25, 25))
        )
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Toggle each sidebar action and confirm checked/unchecked icons. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 03: Breadcrumb navigation

### 1. The feature

**Breadcrumb navigation.**

### 2. What the feature does

Show the active file path as clickable directory segments.

### 3. Exact file operation

**CREATE new file:** `side_bar_widgets/breadcrumbs.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_up_body, MainWindow._on_current_editor_changed`.

### 4. The code for the feature

```python
"""Path breadcrumbs for the active document."""
from pathlib import Path
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

class Breadcrumbs(QWidget):
    directory_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 2)
        self.layout.setSpacing(2)

    def set_path(self, path: str | Path | None) -> None:
        """Rebuild segments for the current document."""
        while self.layout.count():
            item = self.layout.takeAt(0)
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
            self.layout.addWidget(button)
```

**Why this implementation:** Buttons carry captured Path values; rebuilding avoids stale crumbs after a rename or tab switch.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_up_body, MainWindow._on_current_editor_changed`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from side_bar_widgets.breadcrumbs import Breadcrumbs

# REPLACE final two statements of set_up_body:
self.breadcrumbs = Breadcrumbs(self)
self.breadcrumbs.directory_requested.connect(self._open_breadcrumb_folder)
central = QVBoxLayout()
central.setContentsMargins(0, 0, 0, 0)
central.setSpacing(0)
central.addWidget(self.breadcrumbs)
central.addWidget(body_frame)
central_widget = QWidget(self)
central_widget.setLayout(central)
self.setCentralWidget(central_widget)

# ADD a new MainWindow method:
def _open_breadcrumb_folder(self, folder: str) -> None:
    path = Path(folder)
    if path.is_dir():
        self.file_manager.model.setRootPath(str(path))
        self.file_manager.setRootIndex(self.file_manager.model.index(str(path)))

# INSERT as first line of _on_current_editor_changed:
self.breadcrumbs.set_path(getattr(editor, 'path', None))
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING final two statements of set_up_body:
body_frame.setLayout(body)
self.setCentralWidget(body_frame)
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Switch among files in nested folders and click a directory crumb. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 04: Compact and comfortable layouts

### 1. The feature

**Compact and comfortable layouts.**

### 2. What the feature does

Change Qt layout spacing and widget styling together while preserving a user preference.

### 3. Exact file operation

**CREATE new file:** `code_settings/layout_density.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.__init__ immediately after self.init_ui; MainWindow.set_up_menu`.

### 4. The code for the feature

```python
"""Persisted compact/comfortable density setting."""
from PyQt5.QtCore import QSettings
from code_settings.design_settings import theme_qss

class DensityController:
    def __init__(self, window, base_qss: str):
        self.window = window
        self.base_qss = base_qss
        self.settings = QSettings('CodeEditor', 'CodeEditor')

    def apply(self, density: str) -> None:
        """Replace generated QSS rather than stacking copies."""
        if density not in ('compact', 'comfortable'):
            raise ValueError(density)
        self.window.setStyleSheet(self.base_qss + '\n' + theme_qss(density))
        self.settings.setValue('layout_density', density)

    def restore(self) -> None:
        self.apply(self.settings.value('layout_density', 'comfortable', type=str))
```

**Why this implementation:** Persisting only a small string avoids serializing Qt widget state; rebuilding from base prevents CSS growth.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.__init__ immediately after self.init_ui; MainWindow.set_up_menu`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_settings.layout_density import DensityController

# INSERT immediately after self.init_ui() in __init__:
self.density_controller = DensityController(self, self._base_qss)
self.density_controller.restore()

# INSERT in set_up_menu after menu_bar = self.menuBar():
density_menu = menu_bar.addMenu('Layout Density')
for label, density in [('Compact', 'compact'), ('Comfortable', 'comfortable')]:
    action = density_menu.addAction(label)
    action.triggered.connect(lambda _checked=False, value=density:
                             self.density_controller.apply(value))
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING initialization anchor:
self.init_ui()
self._install_command_palette()
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Switch density ten times and verify the QSS length remains stable. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 05: Improved status bar

### 1. The feature

**Improved status bar.**

### 2. What the feature does

Display cursor position, selection length, line endings, encoding and dirty state in one status widget.

### 3. Exact file operation

**CREATE new file:** `side_bar_widgets/editor_status.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.init_ui, update_cursor_position, _on_current_editor_changed`.

### 4. The code for the feature

```python
"""Small editor state indicator."""
from PyQt5.QtWidgets import QLabel

class EditorStatus(QLabel):
    def update_from(self, editor) -> None:
        """Read public QScintilla state from the active editor."""
        if editor is None:
            self.setText('No document')
            return
        line, column = editor.getCursorPosition()
        selected = editor.selectedText() if editor.hasSelectedText() else ''
        modified = '*' if editor.isModified() else ''
        self.setText(f'{modified} Ln {line + 1}, Col {column + 1} | Selected {len(selected)} | UTF-8')
```

**Why this implementation:** A single reader of active editor state avoids maintaining duplicate counters. The UTF-8 indicator reflects both editor constructors calling `setUtf8(True)`.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.init_ui, update_cursor_position, _on_current_editor_changed`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from side_bar_widgets.editor_status import EditorStatus

# REPLACE three cursor_pos_label initialization lines in init_ui:
self.editor_status = EditorStatus(self)
self.statusBar().addPermanentWidget(self.editor_status)

# REPLACE update_cursor_position method body:
def update_cursor_position(self, line: int, index: int):
    self.editor_status.update_from(self.current_editor())

# REPLACE references in _on_current_editor_changed:
# if editor is None:
self.editor_status.update_from(None)
# else, after setting self.current_file:
self.editor_status.update_from(editor)
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING init_ui lines:
self.cursor_pos_label = QLabel("Ln 1, Col 1")
self.cursor_pos_label.setStyleSheet("color: #888; padding: 0 10px;")
self.statusBar().addPermanentWidget(self.cursor_pos_label)
# EXISTING update_cursor_position line:
self.cursor_pos_label.setText(f"Ln {line + 1}, Col {index + 1}")
# EXISTING _on_current_editor_changed empty-tab line:
self.cursor_pos_label.setText("")
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Move cursor, select text, modify a file, and switch tabs. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 06: Polished empty states

### 1. The feature

**Polished empty states.**

### 2. What the feature does

Give empty panels a consistent explanation and suggested action.

### 3. Exact file operation

**CREATE new file:** `side_bar_widgets/empty_state.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow._install_problems`.

### 4. The code for the feature

```python
"""Reusable empty-state widget for docks and lists."""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class EmptyState(QWidget):
    action_requested = pyqtSignal()

    def __init__(self, title: str, detail: str, action: str = '', parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        heading = QLabel(title)
        heading.setAlignment(Qt.AlignCenter)
        body = QLabel(detail)
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignCenter)
        layout.addWidget(heading)
        layout.addWidget(body)
        if action:
            button = QPushButton(action)
            button.clicked.connect(self.action_requested)
            layout.addWidget(button)
```

**Why this implementation:** An opt-in reusable widget prevents each panel inventing its own styling and text.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow._install_problems`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from side_bar_widgets.empty_state import EmptyState

# INSERT at the end of _install_problems, after self.problems_panel is created:
self.problems_empty = EmptyState('No problems',
                                 'Diagnostics will appear here', self)
self.problems_empty.setVisible(False)
# INSERT in _render_all_diagnostics after the existing panel update:
self.problems_empty.setVisible(not bool(rows))
# For an actual visible empty state, place problems_empty into the same
# parent layout as problems_panel, or use a QStackedWidget around them.
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

**Integration limitation:** The empty-state widget must be added to a real layout. The code above is a partial panel connection, not a complete replacement for the existing ProblemsPanel.

### 7. Verification

Open a clean document and confirm the Problems panel shows the empty state. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 07: Welcome screen

### 1. The feature

**Welcome screen.**

### 2. What the feature does

Present a useful landing page when no editor tabs are open.

### 3. Exact file operation

**CREATE new file:** `side_bar_widgets/welcome.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_up_body and MainWindow._on_current_editor_changed`.

### 4. The code for the feature

```python
"""Welcome widget with explicit open actions."""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class WelcomePage(QWidget):
    open_file_requested = pyqtSignal()
    open_folder_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Markdown + Python Editor'))
        for text, signal in (('Open file', self.open_file_requested), ('Open folder', self.open_folder_requested)):
            button = QPushButton(text)
            button.clicked.connect(signal.emit)
            layout.addWidget(button)
        layout.addStretch()
```

**Why this implementation:** Keeping welcome separate from document tabs avoids bogus file paths and unsaved-state handling.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_up_body and MainWindow._on_current_editor_changed`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from side_bar_widgets.welcome import WelcomePage

# INSERT in set_up_body before self.setCentralWidget(body_frame):
self.welcome_page = WelcomePage(self)
self.welcome_page.open_file_requested.connect(self.open_file)
self.welcome_page.open_folder_requested.connect(self.open_folder)
self.welcome_page.hide()
# For a working central swap, replace the final setCentralWidget with a stack:
self.central_stack = QStackedWidget(self)
self.central_stack.addWidget(body_frame)
self.central_stack.addWidget(self.welcome_page)
self.setCentralWidget(self.central_stack)
self._update_welcome_visibility()

# ADD method to MainWindow:
def _update_welcome_visibility(self):
    has_tabs = bool(self.tab_view.all_editors())
    self.central_stack.setCurrentWidget(
        self.central_stack.widget(0) if has_tabs else self.welcome_page)

# INSERT at end of set_new_tab and close_editor after tab removal:
self._update_welcome_visibility()
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING at end of set_up_body:
body_frame.setLayout(body)
self.setCentralWidget(body_frame)
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

**Integration limitation:** The `set_new_tab` and `close_editor` return paths require careful placement of the visibility update. The central-stack code also conflicts with Feature 3 unless both features share the same central widget wrapper.

### 7. Verification

Close every tab, open a file from the welcome page, then close it again. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 08: Focus mode

### 1. The feature

**Focus mode.**

### 2. What the feature does

Temporarily hide docks and toolbars, then restore their exact previous visibility.

### 3. Exact file operation

**CREATE new file:** `code_settings/focus_mode.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.__init__ and MainWindow.set_up_menu`.

### 4. The code for the feature

```python
"""Reversible focus mode."""
from PyQt5.QtWidgets import QDockWidget, QToolBar

class FocusMode:
    def __init__(self, window):
        self.window = window
        self._previous = None

    def toggle(self) -> bool:
        """Return True when focus mode is enabled."""
        if self._previous is None:
            widgets = self.window.findChildren(QDockWidget) + self.window.findChildren(QToolBar)
            self._previous = [(w, w.isVisible()) for w in widgets]
            for widget, _ in self._previous:
                widget.hide()
            return True
        for widget, visible in self._previous:
            if visible:
                widget.show()
        self._previous = None
        return False
```

**Why this implementation:** Remembering individual visibility is safer than blindly showing all docks on exit.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.__init__ and MainWindow.set_up_menu`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_settings.focus_mode import FocusMode

# INSERT after self.init_ui() in __init__:
self.focus_mode = FocusMode(self)

# INSERT after menu_bar = self.menuBar() in set_up_menu:
focus_action = QAction('Focus Mode', self)
focus_action.setShortcut('Ctrl+Shift+F')
focus_action.setCheckable(True)
focus_action.triggered.connect(lambda _checked: self.focus_mode.toggle())
menu_bar.addAction(focus_action)
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Hide one dock manually, enter/exit focus mode, confirm that dock stays hidden. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 09: Workspace layout presets

### 1. The feature

**Workspace layout presets.**

### 2. What the feature does

Save and restore named dock arrangements using QMainWindow state.

### 3. Exact file operation

**CREATE new file:** `code_settings/layout_presets.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.init_ui after set_up_console_dock and MainWindow.set_up_menu`.

### 4. The code for the feature

```python
"""Named window-layout snapshots."""
from PyQt5.QtCore import QSettings

class LayoutPresets:
    def __init__(self, window):
        self.window = window
        self.settings = QSettings('CodeEditor', 'CodeEditor')

    def save(self, name: str) -> None:
        """Persist dock/toolbar state under a validated name."""
        if name not in ('writing', 'coding', 'review'):
            raise ValueError(name)
        self.settings.setValue(f'layouts/{name}', self.window.saveState())

    def restore(self, name: str) -> bool:
        state = self.settings.value(f'layouts/{name}')
        return bool(state is not None and self.window.restoreState(state))
```

**Why this implementation:** Qt saveState handles splitter/dock geometry better than manually serializing coordinates.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.init_ui after set_up_console_dock and MainWindow.set_up_menu`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_settings.layout_presets import LayoutPresets

# INSERT in init_ui after self.set_up_console_dock():
self.console_dock.setObjectName('ConsoleDock')
self.terminal_dock.setObjectName('TerminalDock')
self.layout_presets = LayoutPresets(self)

# INSERT in set_up_menu after menu_bar = self.menuBar():
layouts = menu_bar.addMenu('Layout Presets')
for name in ('writing', 'coding', 'review'):
    save = layouts.addAction(f'Save {name.title()} Layout')
    save.triggered.connect(lambda _=False, n=name: self.layout_presets.save(n))
    restore = layouts.addAction(f'Restore {name.title()} Layout')
    restore.triggered.connect(lambda _=False, n=name: self.layout_presets.restore(n))
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Move docks, save `writing`, rearrange, restore and verify positions. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 10: Automatic recovery

### 1. The feature

**Automatic recovery.**

### 2. What the feature does

Periodically save unsaved text into application-local drafts without overwriting source files.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/document_recovery.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.__init__, MainWindow._save_editor_to_path`.

### 4. The code for the feature

```python
"""Crash-safe recovery snapshots."""
import json
import os
import tempfile
from pathlib import Path
from PyQt5.QtCore import QStandardPaths

class RecoveryStore:
    def __init__(self):
        root = QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
        self.directory = Path(root) / 'recovery'
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, document_id: str, path: str | None, text: str) -> None:
        """Write metadata and text together via an atomic rename."""
        payload = json.dumps({'path': path, 'text': text}, ensure_ascii=False)
        target = self.directory / f'{document_id}.json'
        fd, temp = tempfile.mkstemp(dir=self.directory, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, target)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)

    def pending(self) -> list[dict]:
        result = []
        for file in self.directory.glob('*.json'):
            try:
                result.append({'id': file.stem, **json.loads(file.read_text(encoding='utf-8'))})
            except (OSError, ValueError):
                continue
        return result

    def discard(self, document_id: str) -> None:
        (self.directory / f'{document_id}.json').unlink(missing_ok=True)
```

**Why this implementation:** Atomic replacement prevents half-written JSON after a crash. The restore dialog deliberately avoids silently overwriting user files.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.__init__, MainWindow._save_editor_to_path`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.document_recovery import RecoveryStore

# INSERT after self.init_ui() in __init__:
self.recovery_store = RecoveryStore()
self.recovery_timer = QTimer(self)
self.recovery_timer.setInterval(5000)
self.recovery_timer.timeout.connect(self._save_recovery_drafts)
self.recovery_timer.start()

# ADD method to MainWindow:
def _save_recovery_drafts(self):
    for editor in self.tab_view.all_editors():
        if editor.isModified():
            self.recovery_store.save(str(id(editor)),
                str(editor.path) if editor.path else None, editor.text())

# INSERT in _save_editor_to_path, immediately before return True:
self.recovery_store.discard(str(id(editor)))

# INSERT after self._restore_session() in __init__:
for draft in self.recovery_store.pending():
    if QMessageBox.question(self, 'Recover draft',
            f"Recover unsaved changes for {draft.get('path') or 'Untitled'}?",
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
        restored = self.new_file()
        if restored is not None:
            restored.setText(draft['text'])
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING end of _save_editor_to_path:
self.mark_editor_clean(editor)
return True
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

**Integration limitation:** The current `new_file` return behavior and recovery identity lifecycle must be checked before relying on automatic restoration. This chapter does not guarantee safe recovery of untitled tabs.

### 7. Verification

Modify a tab, wait 5 seconds, inspect application data/recovery, restart and restore the draft. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 11: Local file history

### 1. The feature

**Local file history.**

### 2. What the feature does

Keep bounded snapshots of saved file versions separate from Git.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/local_history.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.__init__ and _save_editor_to_path`.

### 4. The code for the feature

```python
"""Local version snapshots by file identity."""
import hashlib
import time
from pathlib import Path

class LocalHistory:
    def __init__(self, root: Path, keep: int = 25):
        self.root = Path(root)
        self.keep = keep
        self.root.mkdir(parents=True, exist_ok=True)

    def record(self, path: Path, data: bytes) -> Path:
        """Persist the pre-save bytes before replacing the on-disk file."""
        identity = hashlib.sha256(str(path.resolve()).encode()).hexdigest()
        directory = self.root / identity
        directory.mkdir(exist_ok=True)
        filename = directory / f'{time.time_ns()}.snapshot'
        filename.write_bytes(data)
        for stale in sorted(directory.glob('*.snapshot'))[:-self.keep]:
            stale.unlink(missing_ok=True)
        return filename

    def versions(self, path: Path) -> list[Path]:
        identity = hashlib.sha256(str(path.resolve()).encode()).hexdigest()
        return sorted((self.root / identity).glob('*.snapshot'), reverse=True)
```

**Why this implementation:** History must capture the old bytes before save; storing it afterward would only duplicate the current version.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.__init__ and _save_editor_to_path`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.local_history import LocalHistory

# INSERT after self.init_ui() in __init__:
self.local_history = LocalHistory(Path(
    QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)) / 'history')

# INSERT in _save_editor_to_path before `temporary = None`:
if target.is_file():
    try:
        self.local_history.record(logical_path, target.read_bytes())
    except OSError:
        pass  # History must never prevent an explicit Save.
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Save a file three times and confirm the two prior versions are available. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 12: External-change comparison

### 1. The feature

**External-change comparison.**

### 2. What the feature does

Detect genuine on-disk changes while avoiding false alarms caused only by timestamps.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/external_changes.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_new_tab and _save_editor_to_path`.

### 4. The code for the feature

```python
"""Digest-based external change detection."""
import hashlib
from pathlib import Path

class DiskRevision:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.digest = self._digest()

    def _digest(self) -> bytes | None:
        try:
            return hashlib.sha256(self.path.read_bytes()).digest()
        except OSError:
            return None

    def changed(self) -> bool:
        """Compare current bytes against the last accepted revision."""
        return self._digest() != self.digest

    def accept(self) -> None:
        self.digest = self._digest()
```

**Why this implementation:** Hashes avoid timestamp-only false positives. Accepting a revision before user choice would lose the conflict signal.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_new_tab and _save_editor_to_path`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.external_revision import DiskRevision

# INSERT in set_new_tab after `editor._save_target = target`:
editor._disk_revision = DiskRevision(target)

# INSERT in _save_editor_to_path after successful os.replace:
if hasattr(editor, '_disk_revision'):
    editor._disk_revision.accept()

# INSERT in a new menu action handler or a QFileSystemWatcher slot:
def compare_external_revision(self):
    editor = self.current_editor()
    revision = getattr(editor, '_disk_revision', None)
    if revision is None or not revision.changed():
        return
    from code_inteligence.diff_dialog import DiffDialog
    DiffDialog(editor.text(), revision.path.read_text(encoding='utf-8-sig'), self).exec_()
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Edit an open file externally and verify the choice dialog appears; touch the timestamp without changing bytes and verify no dialog. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 13: Compare/diff editor

### 1. The feature

**Compare/diff editor.**

### 2. What the feature does

Display a readable side-by-side textual diff before restoring or replacing text.

### 3. Exact file operation

**CREATE new file:** `side_bar_widgets/diff_view.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_up_menu`.

### 4. The code for the feature

```python
"""Read-only unified diff viewer."""
import difflib
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit

class DiffDialog(QDialog):
    def __init__(self, before: str, after: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Compare documents')
        self.resize(950, 650)
        layout = QVBoxLayout(self)
        view = QPlainTextEdit(self)
        view.setReadOnly(True)
        lines = difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='Current buffer', tofile='Disk / snapshot')
        view.setPlainText(''.join(lines) or 'No differences')
        layout.addWidget(view)
```

**Why this implementation:** Unified diffs show additions and deletions without mutating the buffer; keeping the dialog read-only avoids accidental edits.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_up_menu`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.diff_dialog import DiffDialog

# INSERT after menu_bar = self.menuBar() in set_up_menu:
compare_action = menu_bar.addAction('Compare Buffer with Disk')
compare_action.triggered.connect(self._compare_buffer_with_disk)

# ADD method to MainWindow:
def _compare_buffer_with_disk(self):
    editor = self.current_editor()
    path = getattr(editor, 'path', None)
    if path is None or not Path(path).is_file():
        return
    try:
        disk = Path(path).read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as error:
        QMessageBox.warning(self, 'Compare', str(error))
        return
    DiffDialog(editor.text(), disk, self).exec_()
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Change two lines externally, open Compare, and check `+`/`-` sections. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 14: Rename symbol with preview

### 1. The feature

**Rename symbol with preview.**

### 2. What the feature does

Prepare conservative same-file Python identifier renames with a preview and no immediate mutation.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/rename_preview.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_up_menu`.

### 4. The code for the feature

```python
"""Token-based local rename proposal; no unsafe text replacement."""
import io
import tokenize


def propose_rename(source: str, old: str, new: str) -> tuple[str, int]:
    """Replace NAME tokens; excludes comments and string literals."""
    if not old.isidentifier() or not new.isidentifier():
        raise ValueError('Both names must be valid Python identifiers')
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    changed = 0
    output = []
    for token in tokens:
        if token.type == tokenize.NAME and token.string == old:
            token = token._replace(string=new)
            changed += 1
        output.append(token)
    return tokenize.untokenize(output), changed
```

**Why this implementation:** Python tokenize avoids changing strings/comments. It is deliberately a **lexical**, not scope-aware, rename and can affect unrelated same-spelled names; the confirmation makes that limitation visible.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_up_menu`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.rename_preview import propose_rename
from code_inteligence.diff_dialog import DiffDialog

# INSERT in set_up_menu after menu_bar = self.menuBar():
rename_action = menu_bar.addAction('Rename Identifier (Preview)')
rename_action.triggered.connect(self._rename_identifier_preview)

# ADD method to MainWindow:
def _rename_identifier_preview(self):
    editor = self.current_editor()
    if not isinstance(editor, PythonEditor):
        return
    line, col = editor.getCursorPosition()
    old = editor.wordAtLineIndex(line, col)
    if not old:
        return
    new, ok = QInputDialog.getText(self, 'Rename', 'New name:', text=old)
    if not ok or not new.isidentifier():
        return
    updated = propose_rename(editor.text(), old, new)
    DiffDialog(editor.text(), updated, self).exec_()
    if QMessageBox.question(self, 'Apply rename', 'Apply this text-only rename?',
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
        editor.beginUndoAction()
        editor.selectAll()
        editor.replaceSelectedText(updated)
        editor.endUndoAction()
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Rename a variable appearing in code and in a comment; verify the comment is unchanged. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 15: Workspace symbol search

### 1. The feature

**Workspace symbol search.**

### 2. What the feature does

Find class/function declarations across Python files in the selected workspace.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/workspace_symbols.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_up_menu`.

### 4. The code for the feature

```python
"""AST-based symbol index for workspace discovery."""
import ast
from pathlib import Path


def find_symbols(root: Path, query: str, limit: int = 200):
    """Yield (name, file, line) for matching declarations."""
    if not query.strip():
        return []
    matches = []
    for path in Path(root).rglob('*.py'):
        if any(part in {'.git', '.venv', 'venv', '__pycache__'} for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding='utf-8'))
        except (OSError, UnicodeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and query.casefold() in node.name.casefold():
                matches.append((node.name, str(path), node.lineno))
                if len(matches) >= limit:
                    return matches
    return matches
```

**Why this implementation:** AST gives declaration locations without needing to execute code. The bounded result count prevents huge UI lists.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_up_menu`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.workspace_symbols import find_symbols

# INSERT in set_up_menu after menu_bar = self.menuBar():
symbol_action = menu_bar.addAction('Workspace Symbols')
symbol_action.triggered.connect(self._find_workspace_symbols)

# ADD method to MainWindow:
def _find_workspace_symbols(self):
    query, ok = QInputDialog.getText(self, 'Workspace Symbols', 'Symbol:')
    if not ok or not query.strip():
        return
    matches = find_symbols(self._workspace_root, query)
    labels = [f'{path}:{line} {name}' for name, path, line in matches]
    if not labels:
        QMessageBox.information(self, 'Workspace Symbols', 'No matches')
        return
    chosen, ok = QInputDialog.getItem(self, 'Workspace Symbols',
                                      'Go to:', labels, 0, False)
    if ok:
        _name, path, line = matches[labels.index(chosen)]
        editor = self.set_new_tab(Path(path))
        if editor is not None:
            editor.setCursorPosition(int(line) - 1, 0)
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Search for `MainWindow` and a known method name, then navigate to a result. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 16: Test runner panel

### 1. The feature

**Test runner panel.**

### 2. What the feature does

Run pytest through a child process and show output in a dedicated dock.

### 3. Exact file operation

**CREATE new file:** `side_bar_widgets/test_runner_panel.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.init_ui after set_up_console_dock`.

### 4. The code for the feature

```python
"""Asynchronous pytest process and output widget."""
import sys
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QPlainTextEdit

class TestRunnerPanel(QWidget):
    def __init__(self, workspace: str, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.process = QProcess(self)
        self.process.setWorkingDirectory(workspace)
        layout = QVBoxLayout(self)
        self.output = QPlainTextEdit(self)
        self.output.setReadOnly(True)
        button = QPushButton('Run pytest')
        button.clicked.connect(self.run)
        layout.addWidget(button)
        layout.addWidget(self.output)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.readyReadStandardError.connect(self._read_error)

    def run(self) -> None:
        if self.process.state() != QProcess.NotRunning:
            return
        self.output.clear()
        self.process.start(sys.executable, ['-m', 'pytest', '-q'])

    def _read_output(self) -> None:
        self.output.appendPlainText(bytes(self.process.readAllStandardOutput()).decode(errors='replace'))

    def _read_error(self) -> None:
        self.output.appendPlainText(bytes(self.process.readAllStandardError()).decode(errors='replace'))
```

**Why this implementation:** QProcess keeps the GUI responsive and uses the running interpreter, which is predictable in PyCharm’s `.venv`.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.init_ui after set_up_console_dock`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from side_bar_widgets.test_runner_panel import TestRunnerPanel

# INSERT in init_ui immediately after self.set_up_console_dock():
self.tests_dock = QDockWidget('Tests', self)
self.tests_dock.setObjectName('TestsDock')
self.tests_panel = TestRunnerPanel(str(self._workspace_root), self)
self.tests_dock.setWidget(self.tests_panel)
self.addDockWidget(Qt.BottomDockWidgetArea, self.tests_dock)
self.tests_dock.hide()

# INSERT in set_up_menu after menu_bar = self.menuBar():
show_tests = menu_bar.addAction('Show Tests')
show_tests.triggered.connect(self.tests_dock.show)
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Open Tests and run a passing and a failing pytest test. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 17: Run configurations

### 1. The feature

**Run configurations.**

### 2. What the feature does

Save named Python script/argument/working-directory combinations.

### 3. Exact file operation

**CREATE new file:** `code_settings/run_configurations.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.__init__ and run_current_file`.

### 4. The code for the feature

```python
"""Validated run configuration data model."""
from dataclasses import dataclass, asdict
import json
from pathlib import Path

@dataclass
class RunConfiguration:
    name: str
    script: str
    arguments: list[str]
    working_directory: str

    def command(self) -> list[str]:
        if not Path(self.script).is_file():
            raise FileNotFoundError(self.script)
        return [self.script, *self.arguments]

class RunConfigurationStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> list[RunConfiguration]:
        if not self.path.exists():
            return []
        return [RunConfiguration(**item) for item in json.loads(self.path.read_text(encoding='utf-8'))]

    def save(self, configs: list[RunConfiguration]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([asdict(c) for c in configs], indent=2), encoding='utf-8')
```

**Why this implementation:** Separating data from process execution keeps PythonRunner responsible for subprocess lifecycle and cancellation.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.__init__ and run_current_file`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_settings.run_configurations import RunConfigurationStore

# INSERT after self.init_ui() in __init__:
self.run_configuration_store = RunConfigurationStore(Path(
    QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)) /
    'run_configurations.json')

# ADD method to MainWindow, then bind it to a Run menu action:
def run_saved_configuration(self, name: str):
    config = self.run_configuration_store.get(name)
    if config is None:
        QMessageBox.warning(self, 'Run', 'Configuration not found')
        return
    command = config.command()
    # The existing PythonRunner controls execution and console signals.
    # Do not launch a second QProcess here. Adapt PythonRunner.run(...) to
    # accept `command[1:]` and config.cwd, after inspecting its signature.
    self.statusBar().showMessage('Run: ' + ' '.join(command), 3000)
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

**Integration limitation:** The execution call is intentionally NOT implemented until the actual PythonRunner method signature is verified. This feature is not fully integrated.

### 7. Verification

Run a small script with two arguments and a custom working directory. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 18: Configurable keyboard shortcuts

### 1. The feature

**Configurable keyboard shortcuts.**

### 2. What the feature does

Persist shortcut overrides while detecting duplicate key sequences.

### 3. Exact file operation

**CREATE new file:** `code_settings/shortcuts.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_up_menu`.

### 4. The code for the feature

```python
"""Shortcut settings and collision checks."""
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QKeySequence

class ShortcutManager:
    def __init__(self):
        self.settings = QSettings('CodeEditor', 'CodeEditor')
        self.actions = {}

    def register(self, key: str, action, default: str) -> None:
        """Assign a stable command ID to an existing QAction."""
        shortcut = self.settings.value(f'shortcuts/{key}', default, type=str)
        self.actions[key] = (action, default)
        self.set_shortcut(key, shortcut, persist=False)

    def set_shortcut(self, key: str, sequence: str, persist: bool = True) -> None:
        normalized = QKeySequence(sequence).toString()
        if normalized and any(QKeySequence(other.shortcut()).toString() == normalized for name, (other, _) in self.actions.items() if name != key):
            raise ValueError(f'Shortcut already assigned: {normalized}')
        self.actions[key][0].setShortcut(QKeySequence(normalized))
        if persist:
            self.settings.setValue(f'shortcuts/{key}', normalized)
```

**Why this implementation:** QKeySequence normalizes platform formatting; stable IDs survive menu-label changes.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_up_menu`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_settings.shortcut_manager import ShortcutManager

# INSERT in __init__ after self.init_ui():
self.shortcut_manager = ShortcutManager()

# INSERT at end of set_up_menu, after existing QActions are created:
# Register the *existing* action objects, not duplicates:
self.shortcut_manager.register('save', save_file, 'Ctrl+S')
self.shortcut_manager.register('open', open_file, 'Ctrl+O')
# Keep the original QAction definitions and their signal connections.
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Change Save shortcut, restart the app, verify persistence and duplicate rejection. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 19: Smarter pair handling

### 1. The feature

**Smarter pair handling.**

### 2. What the feature does

Auto-close quotes and brackets without duplicating an existing closing character.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/pair_handling.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `markdown_editor/markdowneditor.py`. **Existing method/location:** `MarkdownEditor.keyPressEvent`.

### 4. The code for the feature

```python
"""Pure pair-insertion decision logic."""
PAIRS = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'", '`': '`'}


def pair_edit(typed: str, following: str, selection: str = '') -> tuple[str, int]:
    """Return inserted text and relative caret shift from insertion end."""
    if typed in PAIRS:
        closing = PAIRS[typed]
        if selection:
            return typed + selection + closing, 0
        if following.startswith(closing):
            return typed, 0
        return typed + closing, -1
    if typed in PAIRS.values() and following.startswith(typed):
        return '', 1
    return typed, 0
```

**Why this implementation:** Pure decision logic can be tested without a Qt window. Keeping key interception narrow avoids breaking autocomplete and shortcuts.

### 5. Connect it to the existing Markdown-Editor: exact code

In `markdown_editor/markdowneditor.py`, find `MarkdownEditor.keyPressEvent`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.pair_handling import pair_edit

# REPLACE MarkdownEditor.keyPressEvent with:
def keyPressEvent(self, e: QKeyEvent) -> None:
    if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Space:
        self.autoCompleteFromAll()
        return
    if e.modifiers() == Qt.NoModifier and e.text() in '([{\"\'`':
        line, column = self.getCursorPosition()
        after = self.text(line)[column:]
        insertion, move = pair_edit(e.text(), after, '')
        if insertion != e.text():
            self.insert(insertion)
            self.setCursorPosition(line, column + move)
            return
    super().keyPressEvent(e)
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
def keyPressEvent(self, e: QKeyEvent) -> None:
    if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_Space:
        self.autoCompleteFromAll()
    else:
        return super().keyPressEvent(e)
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Type `(` before a letter, before `)`, and with a selection; verify each behavior. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 20: Outline and navigation

### 1. The feature

**Outline and navigation.**

### 2. What the feature does

Extract Markdown headings and Python declarations into one navigation model.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/document_outline.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow._update_outline`.

### 4. The code for the feature

```python
"""Document outline parsing without GUI coupling."""
import ast
import re

HEADING = re.compile(r'^(#{1,6})\s+(.+?)\s*#*\s*$')


def markdown_outline(text: str) -> list[tuple[int, str, int]]:
    """Return (level, label, one-based line)."""
    return [(len(m.group(1)), m.group(2), line) for line, row in enumerate(text.splitlines(), 1) if (m := HEADING.match(row))]


def python_outline(text: str) -> list[tuple[int, str, int]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [(1 if isinstance(node, ast.ClassDef) else 2, node.name, node.lineno) for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
```

**Why this implementation:** A shared row contract allows one outline UI for both file types. Parsing is side-effect-free.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow._update_outline`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.outline_parsers import markdown_outline, python_outline

# REPLACE _update_outline with:
def _update_outline(self):
    editor = self.current_editor()
    if editor is None:
        self.outline_tree.clear()
        return
    if isinstance(editor, PythonEditor):
        rows = python_outline(editor.text())
    elif isinstance(editor, MarkdownEditor):
        rows = markdown_outline(editor.text())
    else:
        rows = []
    # CodeOutlineTree currently owns its own update_outline(text) API.
    # Add update_rows(rows) to side_bar_widgets/code_outline.py before this call.
    self.outline_tree.update_rows(rows)
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
def _update_outline(self):
    editor = self.current_editor()
    if isinstance(editor, PythonEditor):
        self.outline_tree.update_outline(editor.text())
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

**Integration limitation:** `CodeOutlineTree.update_rows` must be implemented against the current widget API before replacing `_update_outline`. This feature is not fully integrated.

### 7. Verification

Open a Markdown file with nested headings and a Python file with classes/functions; navigate by clicking outline rows. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 21: Authoring tools

### 1. The feature

**Authoring tools.**

### 2. What the feature does

Offer Markdown table-of-contents insertion and checkbox toggling.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/markdown_authoring.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_up_menu`.

### 4. The code for the feature

```python
"""Markdown text transformations used by explicit editor commands."""
import re
from code_inteligence.outline_parsers import markdown_outline


def make_toc(text: str) -> str:
    """Create links from Markdown heading names."""
    seen = {}
    rows = []
    for level, label, _line in markdown_outline(text):
        slug = re.sub(r'[^\w\- ]', '', label.casefold()).strip().replace(' ', '-')
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        if count:
            slug += f'-{count}'
        rows.append(f'{"  " * (level - 1)}- [{label}](#{slug})')
    return '\n'.join(rows)


def toggle_checkbox(line: str) -> str:
    """Toggle a Markdown task list marker without altering other lines."""
    if re.match(r'^\s*[-*+] \[ \]', line):
        return line.replace('[ ]', '[x]', 1)
    if re.match(r'^\s*[-*+] \[[xX]\]', line):
        return re.sub(r'\[[xX]\]', '[ ]', line, count=1)
    return line
```

**Why this implementation:** Text transforms are pure and explicit, so they do not interfere with typing or preview rendering.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_up_menu`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.markdown_authoring import make_toc, toggle_checkbox

# INSERT in set_up_menu after menu_bar = self.menuBar():
author_menu = menu_bar.addMenu('Markdown Tools')
author_menu.addAction('Insert TOC').triggered.connect(self._insert_markdown_toc)
author_menu.addAction('Toggle Checkbox').triggered.connect(self._toggle_markdown_checkbox)

# ADD MainWindow methods:
def _insert_markdown_toc(self):
    editor = self.current_editor()
    if not isinstance(editor, MarkdownEditor):
        return
    line, column = editor.getCursorPosition()
    toc = make_toc(editor.text())
    editor.beginUndoAction()
    editor.insert(toc)
    editor.endUndoAction()

def _toggle_markdown_checkbox(self):
    editor = self.current_editor()
    if not isinstance(editor, MarkdownEditor):
        return
    line, column = editor.getCursorPosition()
    old = editor.text(line).rstrip('\r\n')
    new = toggle_checkbox(old)
    if new != old:
        editor.beginUndoAction()
        editor.setSelection(line, 0, line, len(old))
        editor.replaceSelectedText(new)
        editor.endUndoAction()
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Generate a TOC from two headings; toggle a checkbox and undo once. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 22: Performance diagnostics mode

### 1. The feature

**Performance diagnostics mode.**

### 2. What the feature does

Measure costly editor operations without spamming production logs.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/performance.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.__init__, render_preview`.

### 4. The code for the feature

```python
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
```

**Why this implementation:** Opt-in context management gives timings even if an operation raises; a bounded list avoids unbounded memory growth.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.__init__, render_preview`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.performance_monitor import PerformanceMonitor

# INSERT after self.init_ui() in __init__:
self.performance = PerformanceMonitor(False)

# INSERT in set_up_menu after menu_bar = self.menuBar():
perf_action = menu_bar.addAction('Performance Diagnostics')
perf_action.setCheckable(True)
perf_action.toggled.connect(lambda on: setattr(self.performance, 'enabled', on))

# REPLACE the preview HTML-generation lines with a timed block:
with self.performance.measure('markdown_preview'):
    safe_body = self._render_markdown_safely(editor.text())
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING in render_preview:
safe_body = self._render_markdown_safely(editor.text())
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Enable mode, edit Markdown, inspect the last samples with debugger; disable and confirm no new samples. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 23: Lazy initialization

### 1. The feature

**Lazy initialization.**

### 2. What the feature does

Delay construction of expensive optional panels until the first time they are opened.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/lazy_service.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.init_ui`.

### 4. The code for the feature

```python
"""Cache an expensive object after its first request."""
class LazyService:
    def __init__(self, factory):
        self.factory = factory
        self._value = None

    def get(self):
        """Construct exactly once on the GUI thread."""
        if self._value is None:
            self._value = self.factory()
        return self._value

    def initialized(self) -> bool:
        return self._value is not None
```

**Why this implementation:** The factory is called only on demand, but ownership stays with Qt parent widgets.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.init_ui`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.lazy_service import LazyService

# REPLACE eager Tests panel construction (Feature 16) with:
self._tests_lazy = LazyService(lambda: TestRunnerPanel(
    str(self._workspace_root), self))
self.tests_dock = QDockWidget('Tests', self)
self.tests_dock.setObjectName('TestsDock')
self.addDockWidget(Qt.BottomDockWidgetArea, self.tests_dock)
self.tests_dock.visibilityChanged.connect(self._load_tests_on_demand)
self.tests_dock.hide()

# ADD method:
def _load_tests_on_demand(self, visible: bool):
    if visible and self.tests_dock.widget() is None:
        self.tests_dock.setWidget(self._tests_lazy.get())
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

**Integration limitation:** Feature 23 replaces the eager Tests construction introduced in Feature 16. Do not keep both.

### 7. Verification

Start app without opening Tests; verify no TestRunnerPanel exists until first open. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 24: Background file hashing

### 1. The feature

**Background file hashing.**

### 2. What the feature does

Compute file hashes away from the GUI thread and report errors explicitly.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/file_hash_worker.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_new_tab`.

### 4. The code for the feature

```python
"""QThreadPool-compatible file digest task."""
import hashlib
from pathlib import Path
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal

class HashSignals(QObject):
    completed = pyqtSignal(str, bytes)
    failed = pyqtSignal(str, str)

class HashTask(QRunnable):
    def __init__(self, path: Path):
        super().__init__()
        self.path = Path(path)
        self.signals = HashSignals()

    def run(self) -> None:
        try:
            digest = hashlib.sha256()
            with self.path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(block)
            self.signals.completed.emit(str(self.path), digest.digest())
        except OSError as exc:
            self.signals.failed.emit(str(self.path), str(exc))
```

**Why this implementation:** Chunked I/O bounds memory. Generation checks prevent a slow result for an old tab from overriding new state.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_new_tab`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.background_hash import HashTask

# ADD method to MainWindow:
def request_disk_hash(self, editor):
    target = getattr(editor, '_save_target', None)
    if target is None:
        return
    task = HashTask(Path(target))
    self._hash_tasks = getattr(self, '_hash_tasks', set())
    self._hash_tasks.add(task)
    task.signals.completed.connect(lambda digest, e=editor, t=task:
        self._on_disk_hash_ready(e, t, digest))
    QThreadPool.globalInstance().start(task)

def _on_disk_hash_ready(self, editor, task, digest):
    self._hash_tasks.discard(task)
    if editor not in self.tab_view.all_editors():
        return
    if digest != getattr(editor, '_disk_digest', None):
        self.statusBar().showMessage('File changed on disk', 4000)
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Hash a large file and confirm the caret remains responsive. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 25: Incremental syntax highlighting

### 1. The feature

**Incremental syntax highlighting.**

### 2. What the feature does

Compute bounded changed-line regions so custom lexers avoid recoloring the entire document.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/highlight_ranges.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `markdown_editor/markdowncustomlexer.py`. **Existing method/location:** `Existing lexer.styleText(start, end)`.

### 4. The code for the feature

```python
"""Changed-line range selection for custom lexers."""
from dataclasses import dataclass

@dataclass(frozen=True)
class LineRange:
    first: int
    last: int


def affected_lines(first_changed: int, last_changed: int, total: int, context: int = 2) -> LineRange:
    """Clamp a changed interval plus surrounding context."""
    if total <= 0:
        return LineRange(0, 0)
    return LineRange(max(0, first_changed - context), min(total - 1, last_changed + context))
```

**Why this implementation:** This helper intentionally separates range policy from Scintilla styling, reducing Unicode offset bugs.

### 5. Connect it to the existing Markdown-Editor: exact code

In `markdown_editor/markdowncustomlexer.py`, find `Existing lexer.styleText(start, end)`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.incremental_highlight import affected_lines

# INSERT at the start of existing styleText(start, end), not instead of it:
# QScintilla supplies byte offsets. Convert them through Scintilla before
# deciding how much of the document to re-style:
first_line = self.editor().SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, start)
last_line = self.editor().SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, end)
region = affected_lines(first_line, last_line, self.editor().lines())
# Keep existing styling implementation; region is only an optimization hint.
# Do not substitute character positions for byte offsets.
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

**Integration limitation:** The lexer styleText method must be inspected in full to preserve byte-offset and lexer-state behavior. The provided lines are instrumentation only, not a complete incremental highlighter.

### 7. Verification

Edit near the middle of a long file containing Unicode and multiline strings; verify highlighting remains correct. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 26: Smarter Markdown preview updates

### 1. The feature

**Smarter Markdown preview updates.**

### 2. What the feature does

Coalesce rapid edits and avoid rendering identical Markdown twice.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/preview_scheduler.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow._connect_editor and MainWindow.init_ui`.

### 4. The code for the feature

```python
"""Preview debounce and content fingerprint."""
import hashlib
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class PreviewScheduler(QObject):
    render_requested = pyqtSignal(str)

    def __init__(self, parent=None, delay_ms: int = 220):
        super().__init__(parent)
        self._text = ''
        self._last_digest = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(delay_ms)
        self._timer.timeout.connect(self._flush)

    def submit(self, text: str) -> None:
        self._text = text
        self._timer.start()

    def _flush(self) -> None:
        digest = hashlib.sha256(self._text.encode('utf-8')).digest()
        if digest != self._last_digest:
            self._last_digest = digest
            self.render_requested.emit(self._text)
```

**Why this implementation:** Debouncing avoids redundant WebEngine updates; fingerprinting suppresses no-op redraws. Sanitization remains the responsibility of the existing preview renderer.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow._connect_editor and MainWindow.init_ui`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.preview_scheduler import PreviewScheduler

# INSERT after self._debounce setup in init_ui:
self.preview_scheduler = PreviewScheduler(self)
self.preview_scheduler.render_requested.connect(lambda _text: self.render_preview())

# REPLACE one existing statement in _connect_editor:
editor.textChanged.connect(lambda ed=editor:
    self.preview_scheduler.submit(ed.text()) if isinstance(ed, MarkdownEditor)
    and ed is self.current_editor() else None)
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING in _connect_editor:
editor.textChanged.connect(self._debounce.start)
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Type quickly, verify preview updates once after a pause; paste the same content and verify no unnecessary render. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 27: Large-file mode

### 1. The feature

**Large-file mode.**

### 2. What the feature does

Disable expensive optional work for unusually large documents while keeping editing and saving available.

### 3. Exact file operation

**CREATE new file:** `code_settings/large_file_policy.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.set_new_tab`.

### 4. The code for the feature

```python
"""Explicit size thresholds for optional editor work."""
from dataclasses import dataclass

@dataclass(frozen=True)
class LargeFilePolicy:
    byte_limit: int = 2_000_000
    line_limit: int = 50_000

    def enabled(self, byte_count: int, line_count: int) -> bool:
        """Return True when costly extras should be suspended."""
        return byte_count >= self.byte_limit or line_count >= self.line_limit

    def allow_preview(self, byte_count: int, line_count: int) -> bool:
        return not self.enabled(byte_count, line_count)
```

**Why this implementation:** Separating optional enhancements from essential I/O keeps large documents usable.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.set_new_tab`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.large_file_mode import LargeFilePolicy

# INSERT after raw = target.read_bytes() in set_new_tab:
large_file = LargeFilePolicy().enabled(len(raw), raw.count(b'\n') + 1)

# INSERT after editor = self.get_editor(...):
editor.large_file_mode = large_file
if large_file:
    self.statusBar().showMessage('Large-file mode: live analysis reduced', 5000)

# INSERT near start of render_preview, after obtaining editor:
if getattr(editor, 'large_file_mode', False):
    return
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING set_new_tab byte read:
raw = target.read_bytes()
has_bom = raw.startswith(UTF8_BOM)
text = raw.decode("utf-8-sig")
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Open a >2 MB Markdown file; confirm editing/saving work and preview is paused. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 28: Shared analysis scheduling

### 1. The feature

**Shared analysis scheduling.**

### 2. What the feature does

Centralize delayed per-document analysis and cancel superseded work.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/analysis_scheduler.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.__init__ and _connect_editor`.

### 4. The code for the feature

```python
"""Per-key coalescing timer scheduler."""
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class AnalysisScheduler(QObject):
    ready = pyqtSignal(str, int)

    def __init__(self, parent=None, delay_ms: int = 300):
        super().__init__(parent)
        self.delay_ms = delay_ms
        self._timers = {}
        self._generations = {}

    def request(self, key: str) -> int:
        """Schedule latest generation of one analysis key."""
        generation = self._generations.get(key, 0) + 1
        self._generations[key] = generation
        timer = self._timers.get(key)
        if timer is None:
            timer = QTimer(self)
            timer.setSingleShot(True)
            self._timers[key] = timer
            timer.timeout.connect(lambda k=key: self.ready.emit(k, self._generations[k]))
        timer.start(self.delay_ms)
        return generation

    def cancel(self, key: str) -> None:
        if key in self._timers:
            self._timers[key].stop()
        self._generations[key] = self._generations.get(key, 0) + 1
```

**Why this implementation:** Generation counters reject stale results while the single-shot timer coalesces bursts.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.__init__ and _connect_editor`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.analysis_scheduler import AnalysisScheduler

# INSERT after self.init_ui() in __init__:
self.analysis_scheduler = AnalysisScheduler(self)
self.analysis_scheduler.ready.connect(self._on_analysis_ready)

# ADD method:
def _on_analysis_ready(self, key: str):
    if key == 'outline':
        self._update_outline()

# REPLACE one existing statement in _connect_editor:
editor.textChanged.connect(lambda: self.analysis_scheduler.schedule('outline', 500))
```

### 6. Existing repository code to delete or replace

**BEFORE (existing code from the inspected repository, sometimes shown as a targeted excerpt):**

```python
# EXISTING in _connect_editor:
editor.textChanged.connect(self._outline_debounce.start)
```

**AFTER:** Apply the code in section 5 at the stated method or anchor. Remove only the old statement/method identified by `REPLACE`; keep all other code and connections.

### 7. Verification

Type quickly and verify only the latest analysis request is dispatched. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 29: Bounded result caching

### 1. The feature

**Bounded result caching.**

### 2. What the feature does

Reuse analysis results for unchanged content with an explicit memory bound.

### 3. Exact file operation

**CREATE new file:** `code_inteligence/result_cache.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow.__init__ and _update_outline`.

### 4. The code for the feature

```python
"""Least-recently-used content result cache."""
from collections import OrderedDict
import hashlib

class ResultCache:
    def __init__(self, max_entries: int = 64):
        if max_entries < 1:
            raise ValueError('max_entries must be positive')
        self.max_entries = max_entries
        self._items = OrderedDict()

    @staticmethod
    def key(namespace: str, text: str) -> tuple[str, bytes]:
        return namespace, hashlib.sha256(text.encode('utf-8')).digest()

    def get(self, key):
        if key not in self._items:
            return None
        self._items.move_to_end(key)
        return self._items[key]

    def put(self, key, value) -> None:
        self._items[key] = value
        self._items.move_to_end(key)
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)
```

**Why this implementation:** Content digests avoid stale cache hits after edits; LRU eviction prevents unlimited growth.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow.__init__ and _update_outline`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from code_inteligence.result_cache import ResultCache

# INSERT after self.init_ui() in __init__:
self.analysis_cache = ResultCache(64)

# REPLACE the parser-selection section of _update_outline (Feature 20):
namespace = 'python-outline' if isinstance(editor, PythonEditor) else 'md-outline'
key = ResultCache.key(namespace, editor.text())
rows = self.analysis_cache.get(key)
if rows is None:
    rows = python_outline(editor.text()) if isinstance(editor, PythonEditor) \
        else markdown_outline(editor.text())
    self.analysis_cache.put(key, rows)
self.outline_tree.update_rows(rows)
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Switch repeatedly between unchanged tabs; inspect cache size and verify it never exceeds 64. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Feature 30: Pause hidden-panel work

### 1. The feature

**Pause hidden-panel work.**

### 2. What the feature does

Hold the latest panel data while hidden and refresh once when shown.

### 3. Exact file operation

**CREATE new file:** `side_bar_widgets/snapshot_dock.py`. Create the parent directory only if it does not exist; do not create an alternate spelling or duplicate file.

**Integration file:** `main.py`. **Existing method/location:** `MainWindow._render_all_diagnostics`.

### 4. The code for the feature

```python
"""Visibility-aware result presentation."""
from PyQt5.QtWidgets import QDockWidget, QListWidget

class SnapshotDock(QDockWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.list_widget = QListWidget(self)
        self.setWidget(self.list_widget)
        self._rows = ()
        self._dirty = False

    def set_rows(self, rows) -> None:
        """Retain latest rows without rebuilding hidden widgets."""
        self._rows = tuple(str(row) for row in rows)
        self._dirty = True
        if self.isVisible():
            self._refresh()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._dirty:
            self._refresh()

    def _refresh(self) -> None:
        self.list_widget.clear()
        self.list_widget.addItems(list(self._rows))
        self._dirty = False
```

**Why this implementation:** Separating latest data from repaint work prevents invisible docks consuming UI time while ensuring a fresh view on reopen.

### 5. Connect it to the existing Markdown-Editor: exact code

In `main.py`, find `MainWindow._render_all_diagnostics`. The following block contains the **new import(s), method(s), and/or statements** to add. Imports go at module scope; snippets labeled REPLACE supersede the named existing method or statement. Snippets labeled INSERT go at the specified anchor. Do not paste comments as executable statements inside a different scope.

```python
from side_bar_widgets.snapshot_dock import SnapshotDock

# INSERT in init_ui after self.set_up_console_dock():
self.results_dock = SnapshotDock('Analysis Results', self)
self.results_dock.setObjectName('AnalysisResultsDock')
self.addDockWidget(Qt.BottomDockWidgetArea, self.results_dock)
self.results_dock.hide()

# INSERT at the end of _render_all_diagnostics(rows):
self.results_dock.set_rows([
    str(getattr(row, 'message', row)) for row in rows
])
```

### 6. Existing repository code to delete or replace

**No existing code must be deleted for this chapter unless section 5 explicitly marks a REPLACE operation.** Preserve unrelated signals, QActions, editor state, and cleanup logic.

### 7. Verification

Hide a panel, trigger updates, reopen it, and confirm only the latest rows appear. Run `python -m compileall -q .`, `python -m pytest -q` and `python main.py` before moving to the next feature.

---

## Final checks

```powershell
python -m compileall -q .
python -m pytest -q
python main.py
git diff --check
git status --short
```

**Do not skip manual GUI tests.** A syntax check cannot prove that Qt signals, menu actions, tab lifecycle, background threads, and existing Ruff integration work together. This guide contains complete standalone feature modules and concrete integration code for all 30 features, but some integrations are explicitly marked as requiring more repository-specific work. It is not an automatically generated or tested patchset.
