# MarkdownEditor — complete topic-by-topic implementation guide

Each topic follows **Topic explanation → Topic code → Topic implementation**, and finishes with how to use that feature in the running editor. There is no combined integration step at the end.

The target is the current [ConfidentCupcake/MarkdownEditor repository](https://github.com/ConfidentCupcake/MarkdownEditor). All paths are relative to the repository root. Keep the spelling `code_inteligence`. The named source folders already exist; no new top-level package or package marker is needed. Runtime recovery/history/profile directories are created by their code.

Integration methods go directly into the existing classes. Do not create `editor_extensions.py`, `EditorExtensions`, `EditorFeatureController`, or another all-feature coordinator.

## Implementation order

The chapters below are arranged in a working order while retaining their original topic numbers. A topic marked **None** can start from the current repository. Where a topic shares working infrastructure, its prerequisites are explicit. Install only the topic and its listed prerequisites if you do not want the full guide.

For all features, follow the chapter order shown below. Finish a topic’s implementation before starting the next; you can run `python main.py` from the repository root after each completed topic.

Exact method names and code anchors are used instead of line numbers that shift after edits. Replace only the shown block unless told to replace a whole method/file. Keep earlier additions when another topic inserts at the same anchor. Add each import and method once. Optional integration blocks apply only when their named topic is installed.

These instructions start from the current repository, rather than a local copy with the previous combined controller already installed. They do not require the separate feature guide. No existing repository file needs deletion; obsolete blocks and complete replacements are identified within their topic.


| Order | Topic | Required topics |
|---:|---|---|
| 1 | [1. Unified design system](#topic-1) | None |
| 2 | [2. Consistent SVG icons](#topic-2) | None |
| 3 | [4. Compact and comfortable layouts](#topic-4) | 1 |
| 4 | [5. Improved status bar](#topic-5) | None |
| 5 | [6. Polished empty states](#topic-6) | None |
| 6 | [7. Welcome screen](#topic-7) | None |
| 7 | [8. Focus mode](#topic-8) | None |
| 8 | [9. Workspace layout presets](#topic-9) | 8 |
| 9 | [10. Automatic recovery](#topic-10) | None |
| 10 | [12. External-change comparison](#topic-12) | None |
| 11 | [13. Compare/diff editor](#topic-13) | None |
| 12 | [11. Local file history](#topic-11) | 10, 13 |
| 13 | [17. Run configurations](#topic-17) | 10 |
| 14 | [16. Test runner panel](#topic-16) | 17 |
| 15 | [18. Configurable keyboard shortcuts](#topic-18) | None |
| 16 | [19. Smarter pair handling](#topic-19) | None |
| 17 | [20. Outline and navigation](#topic-20) | None |
| 18 | [3. Breadcrumb navigation](#topic-3) | 20 |
| 19 | [21. Authoring tools](#topic-21) | 20 |
| 20 | [22. Performance diagnostics mode](#topic-22) | None |
| 21 | [23. Lazy initialization](#topic-23) | None |
| 22 | [24. Background file hashing](#topic-24) | None |
| 23 | [25. Incremental syntax highlighting](#topic-25) | None |
| 24 | [26. Smarter Markdown preview updates](#topic-26) | None |
| 25 | [27. Large-file mode](#topic-27) | None |
| 26 | [28. Shared analysis scheduling](#topic-28) | None |
| 27 | [14. Rename symbol with preview](#topic-14) | 10, 12, 13, 28 |
| 28 | [15. Workspace symbol search](#topic-15) | 28 |
| 29 | [29. Bounded result caching](#topic-29) | 28 |
| 30 | [30. Pause hidden-panel work](#topic-30) | 6, 20, 28 |


<a id="topic-1"></a>
## 1. Unified design system

### Topic explanation

One semantic palette gives menus, tabs, buttons, and dock headers consistent colors. Generated QSS supplies the shared widget rules; syntax tokens and terminal ANSI colors keep their existing theme owners.

The design module supplies semantic colors and spacing through scoped Qt stylesheets. MainWindow stores the original stylesheet and regenerates additions from that base, so repeated application does not accumulate old rules. Syntax colors continue to come from the editor’s existing lexer/theme.


**Documentation:**

- [Qt 5 style sheets](https://doc.qt.io/archives/qt-5.15/stylesheet.html)
- [Qt 5 style sheet reference](https://doc.qt.io/archives/qt-5.15/stylesheet-reference.html)

### Topic code


#### Create file: `code_settings/design_system.py`

**Folder:** `code_settings/` already exists. **File:** `design_system.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Shared interface colors and density rules."""
from __future__ import annotations


PALETTE = {"paper": "#1e1f22", "surface": "#262a33", "text": "#dcdfe4",
           "muted": "#969ba7", "accent": "#61afef", "border": "#3d424d"}


def theme_qss(density: str = "comfortable") -> str:
    """Generate one scoped widget stylesheet from shared semantic tokens."""
    if density not in ("compact", "comfortable"):
        raise ValueError("unknown density")
    # The density choice changes geometry; colors still come from one palette.
    pad = 3 if density == "compact" else 7
    # Property selectors scope the design to widgets explicitly opted in.
    return """
    QWidget[designPanel="true"] { background: %(surface)s; color: %(text)s; }
    QDockWidget::title { background: %(surface)s; color: %(text)s;
                         padding: %(pad)spx; border-bottom: 1px solid %(border)s; }
    QMenu { background: %(surface)s; color: %(text)s; border: 1px solid %(border)s; }
    QMenu::item:selected { background: %(border)s; }
    QPushButton { background: %(surface)s; color: %(text)s;
                  border: 1px solid %(border)s; border-radius: 4px;
                  padding: %(pad)spx; }
    QPushButton:hover { border-color: %(accent)s; }
    QPushButton:disabled { color: %(muted)s; }
    QToolButton { color: %(text)s; background: transparent;
                  border: 1px solid transparent; border-radius: 4px;
                  padding: %(pad)spx; }
    QToolButton:hover, QToolButton:focus { border-color: %(accent)s; }
    QToolButton:checked { background: %(border)s; }
    QToolButton:disabled { color: %(muted)s; }
    QTabBar::tab { background: %(surface)s; color: %(text)s;
                   padding: %(pad)spx 12px; }
    QTabBar::tab:selected { border-bottom: 2px solid %(accent)s; }
    """ % {**PALETTE, "pad": pad}
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `theme_qss` | Generate one scoped widget stylesheet from shared semantic tokens. |


### Topic implementation

**Required first:** None.


#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def apply_design_density(self, density: str) -> None:
        """Rebuild UI spacing from the original stylesheet exactly once.

        QSettings stores geometry preference; theme JSON continues to own
        syntax colors. Keeping the original QSS prevents a growing cascade
        when users switch compact/comfortable repeatedly.
        """
        from code_settings.design_system import theme_qss

        additions = theme_qss(density)  # Validate before persisting a bad value.
        self._base_qss = getattr(self, "_base_qss", self.styleSheet())
        self.settings.setValue("ui_density", density)
        self.setStyleSheet(self._base_qss + additions)
```



#### Edit `main.py` — `MainWindow.__init__`

Apply the scoped stylesheet once the existing widgets are built.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self.apply_design_density(self.settings.value("ui_density", "comfortable", type=str))
```



#### Add at the end of `main.py` — `MainWindow._apply_settings`

Regenerate from the saved base stylesheet after settings change. Add the following at method-body indentation after the existing body, immediately before the next method definition at class indentation. Keep earlier additions in this method.

```python
        self.apply_design_density(self.settings.value("ui_density", "comfortable", type=str))
```



**Use this topic:** Run `python main.py` from the repository root. Open the editor and inspect menus, buttons and dock titles for the shared colors and padding.


<a id="topic-2"></a>
## 2. Consistent SVG icons

### Topic explanation

A single icon provider resolves the existing packaged SVG assets and supplies normal/active states. Sidebar controls become keyboard-accessible QToolButtons with a real checked state.

The icon provider loads the repository’s existing SVGs and supplies Qt checked/selected states. Sidebar controls become keyboard-operable QToolButtons. The existing sidebar dispatcher is updated with them; it accepts button activation without needing a mouse event.


**Documentation:**

- [Qt QIcon states](https://doc.qt.io/archives/qt-5.15/qicon.html)
- [Qt QToolButton](https://doc.qt.io/archives/qt-5.15/qtoolbutton.html)

### Topic code


#### Create file: `markdowneditor_assets/icon_provider.py`

**Folder:** `markdowneditor_assets/` already exists. **File:** `icon_provider.py`. Create the file and paste the complete contents starting at line 1.

```python
"""State-aware icons from the existing SVG assets."""
from __future__ import annotations
from PyQt5.QtGui import QIcon
from markdowneditor_assets import asset_path
from pathlib import Path


def themed_icon(name: str) -> QIcon:
    """Load existing 24px SVG icons with actual disabled/selected Qt states."""
    # Do not turn arbitrary text into an asset path; the sidebar has six
    # supported actions and an explicit allowlist is easier to review.
    if name not in {"folder", "search", "outline", "terminal", "console", "settings"}:
        raise ValueError("unsupported icon")
    path = Path(asset_path(f"icons/{name}.svg"))
    icon = QIcon(str(path))
    # Qt generates a disabled palette variant when no explicit asset is added.
    active = Path(asset_path(f"icons/{name}-active.svg"))
    if active.is_file():
        icon.addFile(str(active), mode=QIcon.Normal, state=QIcon.On)
    return icon
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `themed_icon` | Load existing 24px SVG icons with actual disabled/selected Qt states. |


### Topic implementation

**Required first:** None.


#### Replace `main.py` — `MainWindow.get_sidebar_label`

Replace the old QLabel/pixmap sidebar behavior with a stateful SVG tool button. Delete this method’s complete current definition, from `def get_sidebar_label(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def get_sidebar_label(self, path, name):
        """Create a keyboard-operable 24px SVG sidebar action.

        The path argument remains for compatibility with set_up_body; the
        semantic icon name selects the packaged SVG and its active variant.
        """
        from markdowneditor_assets.icon_provider import themed_icon

        button = QToolButton(self.side_bar)
        button.setIcon(themed_icon(name))
        button.setIconSize(QSize(24, 24))
        button.setCheckable(True)
        button.setChecked(name == "folder")
        button.setToolTip(name.title())
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(
            lambda _checked=False, selected=name: self.show_hide_tab(None, selected)
        )
        return button
```



#### Replace `main.py` — `MainWindow._set_sidebar_icon`

Replace the old QLabel/pixmap sidebar behavior with a stateful SVG tool button. Delete this method’s complete current definition, from `def _set_sidebar_icon(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _set_sidebar_icon(self, name: str, active: bool):
        """Reflect a tool's actual visibility using the existing icon variants."""
        button = self.sidebar_labels.get(name)
        if button is not None:
            button.setChecked(active)
```



#### Replace `main.py` — `MainWindow.show_hide_tab`

Handle button activation with no mouse event and update selected SVG states through the new tool-button API. Delete this method’s complete current definition, from `def show_hide_tab(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
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
        target = panels.get(type_)
        if target is None:
            return

        # If the target panel is already showing, hide the side panel
        if self.side_panel.isVisible() and self.side_panel.currentWidget() is target:
            # Clicking the active panel hides it and clears selected SVG.
            self.side_panel.hide()
            self._set_sidebar_icon(type_, False)
            return

        # Otherwise, switch to the target panel and show it
        self.side_panel.setCurrentWidget(target)
        self.side_panel.show()
        if type_ == "outline":
            self._update_outline()

        for name in ("folder", "search", "outline"):
            self._set_sidebar_icon(name, name == type_)
        # Restore splitter sizes if the side panel was hidden (width 0)
        sizes = self.hs_split.sizes()
        if sizes and sizes[0] == 0:
            self.hs_split.setSizes([300, 550, 550])
```



**Use this topic:** Run `python main.py` from the repository root. Use the sidebar by mouse and keyboard; active buttons use the selected SVG state.


<a id="topic-4"></a>
## 4. Compact and comfortable layouts

### Topic explanation

Compact and comfortable modes change shared padding and sidebar geometry while preserving document text, selections, and syntax colors. QSettings retains the selected mode.

The density actions call the design method from Topic 1 with explicit compact/comfortable values. QSettings retains the choice and the next launch reapplies it. Only widget geometry changes; file contents and syntax colors do not.


**Documentation:**

- [Qt style sheets](https://doc.qt.io/archives/qt-5.15/stylesheet.html)
- [Qt QSettings](https://doc.qt.io/archives/qt-5.15/qsettings.html)

### Topic code


No new source file is needed. The complete topic methods belong to `MainWindow` in the existing `main.py`:

```python
    def _install_topic_4(self):
        """Expose the density commands in the existing menu bar."""
        menu = self.menuBar().addMenu('Density')
        action_0 = menu.addAction('Compact')
        action_0.setObjectName("topic.4.0")
        action_0.triggered.connect(lambda checked=False: self.apply_design_density("compact"))
        action_1 = menu.addAction('Comfortable')
        action_1.setObjectName("topic.4.1")
        action_1.triggered.connect(lambda checked=False: self.apply_design_density("comfortable"))
```


The implementation section identifies their exact insertion points and startup connections. Paste each method only once.


### Topic implementation

**Required first:** Topic 1.


#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_topic_4(self):
        """Expose the density commands in the existing menu bar."""
        menu = self.menuBar().addMenu('Density')
        action_0 = menu.addAction('Compact')
        action_0.setObjectName("topic.4.0")
        action_0.triggered.connect(lambda checked=False: self.apply_design_density("compact"))
        action_1 = menu.addAction('Comfortable')
        action_1.setObjectName("topic.4.1")
        action_1.triggered.connect(lambda checked=False: self.apply_design_density("comfortable"))
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_topic_4()
```



**Use this topic:** Run `python main.py` from the repository root. Choose Density → Compact or Comfortable; reopen the editor to see the saved choice.


<a id="topic-5"></a>
## 5. Improved status bar

### Topic explanation

The status bar exposes UTF-8/BOM, line endings, indentation, interpreter, and process activity beside the existing cursor and Git labels. Clickable values also accept keyboard activation.

Clickable status labels edit the current view’s UTF-8 BOM preference, line-ending mode and indentation. Encoding and EOL changes mark serialization dirty. The interpreter label uses the existing interpreter picker, and existing process signals update the activity label.


**Documentation:**

- [Qt status bar](https://doc.qt.io/archives/qt-5.15/qstatusbar.html)
- [QScintilla overview](https://www.riverbankcomputing.com/software/qscintilla/intro)

### Topic code


#### Create file: `side_bar_widgets/status_item.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `status_item.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `StatusItem` | A keyboard accessible, clickable status-bar item. |
| `StatusItem.__init__` | Bind a status value to its corresponding setting or chooser. |
| `StatusItem.mousePressEvent` | Invoke the setting on a left click only. |
| `StatusItem.keyPressEvent` | Let keyboard users activate the same control. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.status_item import StatusItem
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _guide_install_status(self) -> None:
        """Add metadata beside the existing Ln/Col, cat and Git labels."""
        window = self
        self.encoding = StatusItem("UTF-8", self._guide_choose_encoding, window)
        self.line_ending = StatusItem("LF", self._guide_choose_line_ending, window)
        self.indent = StatusItem("Spaces: 4", self._guide_choose_indentation, window)
        self.interpreter = StatusItem("Python", window.choose_interpreter, window)
        self.activity = QLabel("Idle", window)
        for item in (self.encoding, self.line_ending, self.indent, self.interpreter,
                     self.activity):
            window.statusBar().addPermanentWidget(item)
        window.python_runner.process_started.connect(lambda: self.activity.setText("Running Python"))
        window.python_runner.process_finished.connect(lambda _code: self.activity.setText("Idle"))

    def _guide_choose_encoding(self) -> None:
        """Choose the UTF-8 BOM bit used by the existing atomic save path."""
        from PyQt5.QtWidgets import QInputDialog
        editor = self.current_editor()
        if editor is None:
            return
        choice, ok = QInputDialog.getItem(self, "Encoding", "Save as",
                                          ["UTF-8", "UTF-8 BOM"],
                                          1 if getattr(editor, "_utf8_bom", False) else 0, False)
        if ok:
            editor._utf8_bom = choice == "UTF-8 BOM"
            self._on_editor_text_changed(editor)
            self._update_status_metadata(editor)

    def _guide_choose_line_ending(self) -> None:
        """Set a QScintilla EOL mode and mark byte serialization as dirty."""
        from PyQt5.Qsci import QsciScintilla
        from PyQt5.QtWidgets import QInputDialog
        editor = self.current_editor()
        if editor is None:
            return
        value, ok = QInputDialog.getItem(self, "Line endings", "Choose",
                                         ["LF", "CRLF", "CR"], 0, False)
        if ok:
            modes = {"LF": QsciScintilla.EolUnix,
                     "CRLF": QsciScintilla.EolWindows,
                     "CR": QsciScintilla.EolMac}
            editor.setEolMode(modes[value])
            self._on_editor_text_changed(editor)
            self._update_status_metadata(editor)

    def _guide_choose_indentation(self) -> None:
        """Select tabs or space width for the active editor only."""
        from PyQt5.QtWidgets import QInputDialog
        editor = self.current_editor()
        if editor is None:
            return
        value, ok = QInputDialog.getItem(self, "Indentation", "Choose",
                                         ["Tabs: 4", "Spaces: 2", "Spaces: 4", "Spaces: 8"],
                                         2, False)
        if ok:
            editor.setIndentationsUseTabs(value.startswith("Tabs"))
            editor.setTabWidth(int(value[-1]))
            self._update_status_metadata(editor)

    def _update_status_metadata(self, editor):
        """Display serialization and indentation choices for the current view."""
        if not hasattr(self, "encoding"):
            return
        if editor is None:
            for label in (self.encoding, self.line_ending, self.indent):
                label.setText("")
            return
        self.encoding.setText("UTF-8 BOM" if getattr(editor, "_utf8_bom", False) else "UTF-8")
        self.line_ending.setText({0: "CRLF", 1: "CR", 2: "LF"}.get(editor.eolMode(), "LF"))
        self.indent.setText(("Tabs" if editor.indentationsUseTabs() else "Spaces") + f": {editor.tabWidth()}")
        self.interpreter.setText(Path(self.python_runner.interpreter).name)
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._guide_install_status()
```



#### Insert at the start of `main.py` — `MainWindow._on_current_editor_changed`

Refresh these labels whenever focus changes. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        self._update_status_metadata(editor)
```



#### Add at the end of `main.py` — `MainWindow._restart_ruff`

Refresh the displayed interpreter after its client changes. Add the following at method-body indentation after the existing body, immediately before the next method definition at class indentation. Keep earlier additions in this method.

```python
        self._update_status_metadata(self.current_editor())
```



**Use this topic:** Run `python main.py` from the repository root. Activate the UTF-8, line-ending and indentation labels, then save a document with the chosen serialization.


<a id="topic-6"></a>
## 6. Polished empty states

### Topic explanation

Empty states explain why a panel has no results and what the user can do next, instead of leaving a blank area.

EmptyState explains an empty Git panel and offers an action. SnapshotDock stores result data even when hidden and rebuilds its visible rows when needed. MainWindow feeds Ruff diagnostics into Problems and creates a References shell; Topic 30 later connects semantic reference searching. The original Git graph and worker remain intact.


**Documentation:**

- [Qt stacked widgets](https://doc.qt.io/archives/qt-5.15/qstackedwidget.html)

### Topic code


#### Create file: `side_bar_widgets/empty_state.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `empty_state.py`. Create the file and paste the complete contents starting at line 1.

```python
"""A reusable explanation and action for an empty panel."""
from __future__ import annotations
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class EmptyState(QWidget):
    """Explain why a panel has no rows and provide a relevant next action."""

    def __init__(self, title: str, hint: str, button: str, action, parent=None):
        """Create a reusable empty state without owning application logic."""
        super().__init__(parent)
        self.setProperty("designPanel", True)
        layout = QVBoxLayout(self)
        self.title_label = QLabel(title)
        self.hint_label = QLabel(hint)
        # Keep these labels accessible so a provider can change the reason
        # from "no repository" to "no commits" without rebuilding the dock.
        for label in (self.title_label, self.hint_label):
            label.setWordWrap(True)
            layout.addWidget(label)
        launch = QPushButton(button)
        launch.clicked.connect(action)
        layout.addWidget(launch)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `EmptyState` | Explain why a panel has no rows and provide a relevant next action. |
| `EmptyState.__init__` | Create a reusable empty state without owning application logic. |


#### Create file: `side_bar_widgets/snapshot_dock.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `snapshot_dock.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Deferred presentation for Problems and References while retaining latest data."""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDockWidget, QLabel, QStackedWidget, QTreeWidget, QTreeWidgetItem


class SnapshotDock(QDockWidget):
    """Keep newest plain rows while hidden and rebuild exactly once on showing."""
    navigate = pyqtSignal(str, int, int)

    def __init__(self, title, object_name, parent=None):
        """Create a stable dock shell with explicit empty and populated states."""
        super().__init__(title, parent)
        self.setObjectName(object_name)
        self.stack = QStackedWidget(self)
        self.empty = QLabel('No results yet', self)
        self.empty.setWordWrap(True)
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(['Description', 'Location'])
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.tree)
        self.setWidget(self.stack)
        self.rows, self.dirty, self.rebuilds = (), True, 0
        self.visibilityChanged.connect(self.refresh)
        self.tree.itemActivated.connect(self._activate)

    def set_rows(self, rows, empty='No results'):
        """Retain immutable (description, path, line, column) rows without hidden repaint."""
        self.rows = tuple(tuple(row) for row in rows)
        self.empty.setText(empty)
        self.dirty = True
        self.refresh()

    def refresh(self, visible=None):
        """Rebuild only when visible and dirty; essential snapshot storage is independent."""
        if not self.isVisible() or not self.dirty:
            return
        self.tree.clear()
        for description, path, line, column in self.rows:
            item = QTreeWidgetItem(self.tree, [description, f'{path}:{line + 1}'])
            item.setData(0, Qt.UserRole, (path, line, column))
        self.stack.setCurrentWidget(self.tree if self.rows else self.empty)
        self.dirty = False
        self.rebuilds += 1

    def _activate(self, item, column):
        """Emit the precise zero-based location attached to a result row."""
        location = item.data(0, Qt.UserRole)
        if location:
            self.navigate.emit(*location)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `SnapshotDock` | Keep newest plain rows while hidden and rebuild exactly once on showing. |
| `SnapshotDock.__init__` | Create a stable dock shell with explicit empty and populated states. |
| `SnapshotDock.set_rows` | Retain immutable (description, path, line, column) rows without hidden repaint. |
| `SnapshotDock.refresh` | Rebuild only when visible and dirty; essential snapshot storage is independent. |
| `SnapshotDock._activate` | Emit the precise zero-based location attached to a result row. |


### Topic implementation

**Required first:** None.


#### Edit `main.py` — `MainWindow.init_ui`

Replace only the dock’s widget assignment with a graph/empty-state stack.

Inside this method, find exactly:

```python
        self.git_graph_dock.setWidget(self.git_graph)
```

Replace only that block with:

```python
        # The graph and its empty explanation are two views of one Git model.
        # Do not destroy the graph when the dock is hidden or the repo changes.
        from side_bar_widgets.empty_state import EmptyState
        self.git_pages = QStackedWidget(self.git_graph_dock)
        self.git_pages.addWidget(self.git_graph)
        self.git_empty = EmptyState("No Git repository",
                                    "Open a folder containing a Git repository.",
                                    "Open folder", self.open_folder, self.git_graph_dock)
        self.git_pages.addWidget(self.git_empty)
        self.git_pages.setCurrentWidget(self.git_empty)
        self.git_graph_dock.setWidget(self.git_pages)
```



#### Replace `main.py` — `MainWindow._on_git_snapshot`

Keep the existing Git model and show an explanation when it has no displayable rows. Delete this method’s complete current definition, from `def _on_git_snapshot(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _on_git_snapshot(self, snapshot) -> None:
        """Update branch identity and graph from the same Git snapshot."""
        identity = snapshot.branch or (
            f"detached@{snapshot.head_short}" if snapshot.head_short else "unborn"
        )
        self.git_branch_label.setText(f"Git: {identity}")
        self.git_branch_label.setToolTip(str(snapshot.root))
        self.git_graph.set_snapshot(snapshot)
        if not snapshot.commits:
            self.git_empty.title_label.setText("No commits yet")
            self.git_empty.hint_label.setText("This Git repository has no history to display.")
        self.git_pages.setCurrentWidget(self.git_graph if snapshot.commits else self.git_empty)
```



#### Replace `main.py` — `MainWindow._on_git_failure`

Keep the existing Git model and show an explanation when it has no displayable rows. Delete this method’s complete current definition, from `def _on_git_failure(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _on_git_failure(self, message: str) -> None:
        """Clear stale repository identity without interrupting editing."""
        self.git_branch_label.setText("No Git repository")
        self.git_branch_label.setToolTip(message)
        
        # Do not call git_branch_label.clear(); that erases the message just set.
        self.git_graph.clear()
        self.git_empty.title_label.setText("No Git repository")
        self.git_empty.hint_label.setText(message)
        self.git_pages.setCurrentWidget(self.git_empty)
```



#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.snapshot_dock import SnapshotDock
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_result_panels(self):
        """Create lightweight Problems and References docks with explicit empty states."""
        self.problem_rows = {}
        self.problems = SnapshotDock("Problems", "ProblemsDock", self)
        self.references = SnapshotDock("References", "ReferencesDock", self)
        menu = self.menuBar().addMenu("Analysis panels")
        for dock in (self.problems, self.references):
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            dock.hide()
            dock.navigate.connect(self._open_file_at_position)
            menu.addAction(dock.toggleViewAction())
        self.references.set_rows((), "No references requested yet")

    def _guide_diagnostics_changed(self, editor, diagnostics):
        """Retain current Ruff data while deferring hidden Problems tree rebuilding."""
        path = str(getattr(editor, "path", None) or "")
        self.problem_rows[id(editor)] = [(f"{d.code}: {d.message}", path, d.start.line, d.start.column)
                                        for d in diagnostics if path]
        self.problems.set_rows([row for rows in self.problem_rows.values() for row in rows],
                               "No reported problems in open saved Python files")

    def _remove_problem_rows(self, editor):
        """Clear a retired or edited view's diagnostic snapshot."""
        self.problem_rows.pop(id(editor), None)
        self.problems.set_rows([row for rows in self.problem_rows.values() for row in rows],
                               "No reported problems in open saved Python files")
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_result_panels()
```



#### Insert at the start of `main.py` — `MainWindow._on_ruff_diagnostics`

Feed the dock while retaining existing Ruff feedback. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if hasattr(self, "problems"):
            self._guide_diagnostics_changed(editor, diagnostics)
```



#### Insert at the start of `main.py` — `MainWindow._dispose_editor`

Remove rows before retiring their editor. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        self._remove_problem_rows(editor)
```



#### Edit `main.py` — `MainWindow._on_editor_text_changed`

Discard stale diagnostic positions on edits.

Inside this method, find exactly:

```python
        self._dirty_editors.add(editor)
```

Replace only that block with:

```python
        self._dirty_editors.add(editor)
        self._remove_problem_rows(editor)
```



**Use this topic:** Run `python main.py` from the repository root. Show Git History in a folder without Git history, and Analysis panels → Problems/References for their empty explanations.


<a id="topic-7"></a>
## 7. Welcome screen

### Topic explanation

The welcome screen offers recent files, recent projects, Open actions, and built-in Python/Markdown/README templates. It appears when the tab collection is empty and opens templates as unsaved drafts.

A QStackedWidget contains the existing central editor widget and a Welcome page. It switches to Welcome only when all split groups are empty. Recent-project buttons use a validated folder-opening method, and templates create unsaved drafts so they cannot overwrite an existing file.


**Documentation:**

- [Qt main-window center](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)
- [Qt stacked widgets](https://doc.qt.io/archives/qt-5.15/qstackedwidget.html)

### Topic code


#### Create file: `side_bar_widgets/welcome_screen.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `welcome_screen.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Welcome` | Show recent resources and templates only when every tab group is empty. |
| `Welcome.__init__` | Keep callbacks and regenerate recent-resource buttons when shown. |
| `Welcome._button` | Add one labeled navigation action with a captured immutable destination. |
| `Welcome.refresh` | Rebuild current settings data and show explicit empty-state labels. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.welcome_screen import Welcome
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _open_draft(self, source, python=False):
        """Create editable draft text without assigning an overwrite destination."""
        previous = self.python_editor_active
        self.python_editor_active = python
        try:
            editor = self.new_file()
            editor.setText(source)
            return editor
        finally:
            self.python_editor_active = previous
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_welcome(self):
        """Wrap the existing central editor widget in an editor/welcome stack."""
        original = self.takeCentralWidget()
        self.welcome_stack = QStackedWidget(self)
        self.welcome_stack.addWidget(original)
        self.welcome = Welcome(self.recent_files,
            lambda path=None: self.open_recent_file(str(path)) if path else self.open_file(),
            lambda path=None: self.open_folder(path), self,
            projects=self.settings.value("recent_projects", [], type=list),
            create_template=self._guide_create_template)
        self.welcome_stack.addWidget(self.welcome)
        self.setCentralWidget(self.welcome_stack)
        self._refresh_welcome()

    def _refresh_welcome(self):
        """Show the welcome page only when all split groups are empty."""
        if not hasattr(self, "welcome_stack"):
            return
        empty = not list(self.tab_view.all_editors())
        self.welcome.refresh(self.recent_files, self.settings.value("recent_projects", [], type=list))
        self.welcome_stack.setCurrentWidget(self.welcome if empty else self.welcome_stack.widget(0))

    def _guide_create_template(self, name):
        """Open a selected starter as an unsaved document of the correct editor type."""
        from side_bar_widgets.welcome_screen import TEMPLATES
        python, source = TEMPLATES[name]
        self._open_draft(source, python)
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_welcome()
```



#### Insert at the start of `main.py` — `MainWindow._on_current_editor_changed`

Select the correct page after tab changes. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        self._refresh_welcome()
```



#### Edit `main.py` — `MainWindow.new_file`

Refresh after adding the new tab, including the first document.

Inside this method, find exactly:

```python
        return editor
```

Replace only that block with:

```python
        self._refresh_welcome()
        return editor
```



#### Edit `main.py` — `MainWindow.set_new_tab`

Refresh after adding the new tab, including the first document.

Inside this method, find exactly:

```python
        return editor
```

Replace only that block with:

```python
        self._refresh_welcome()
        return editor
```



#### Replace `main.py` — `MainWindow.open_folder`

Accept recent-project paths, validate them and retain a bounded recent-project list. The model root update must be outside the invalid-directory branch. Delete this method’s complete current definition, from `def open_folder(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def open_folder(self, folder=None):
        """Open a chosen/recent project and retarget live services without forcing a PTY."""
        if not folder:
            folder = QFileDialog.getExistingDirectory(self, "Pick a folder", "",
                                                      options=QFileDialog.DontUseNativeDialog)
        if not folder:
            return
        selected = Path(folder).resolve()
        if not selected.is_dir():
            QMessageBox.warning(self, "Open project", f"Folder does not exist: {selected}")
            return
        self.file_manager.model.setRootPath(str(selected))
        self.file_manager.setRootIndex(self.file_manager.model.index(str(selected)))
        if self.terminal is not None:
            self.terminal.set_working_directory(selected, restart=True)
        self._refresh_git_state()
        root = self._discover_workspace_root(selected)
        if root != self._workspace_root:
            self._restart_ruff(self.python_runner.interpreter, root)
        recent = self.settings.value("recent_projects", [], type=list)
        recent = [str(selected)] + [p for p in recent if p != str(selected)]
        self.settings.setValue("recent_projects", recent[:10])
        self._refresh_welcome()
        self.statusBar().showMessage(f"Opened {selected}", 2000)
```



**Use this topic:** Run `python main.py` from the repository root. Close all tabs to show Welcome. Use a recent project, file or template.


<a id="topic-8"></a>
## 8. Focus mode

### Topic explanation

Focus mode snapshots the current docks, splitter, sidebar, side panel, and menu visibility, then hides distractions. Exiting restores that snapshot rather than applying a canned arrangement.

Layouts captures the window’s dock state, central splitter and visibility before hiding distractions. Its shortcut is also added to the window itself so it remains reachable while the menu bar is hidden. Restoring focus mode uses that exact prior snapshot.


**Documentation:**

- [Qt saveState/restoreState](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)
- [Qt shortcuts](https://doc.qt.io/archives/qt-5.15/qshortcut.html)

### Topic code


#### Create file: `code_settings/workspace_layouts.py`

**Folder:** `code_settings/` already exists. **File:** `workspace_layouts.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Named layout snapshots and reversible focus mode."""
from __future__ import annotations
from PyQt5.QtWidgets import QDockWidget


class Layouts:
    """Persist named dock/split layouts and reversible focus mode."""

    def __init__(self, window):
        """Own only layout snapshots; the QMainWindow owns its child widgets."""
        self.window = window
        self.before_focus = None

    def save(self, name: str) -> None:
        """Capture dock geometry and the three-pane splitter in QSettings."""
        self.window.settings.setValue(f"layouts/{name}/window", self.window.saveState())
        self.window.settings.setValue(f"layouts/{name}/split", self.window.hs_split.saveState())

    def restore(self, name):
        """Restore saved geometry atomically, or apply one of three built-in layouts."""
        settings = self.window.settings
        state = settings.value(f"layouts/{name}/window")
        split = settings.value(f"layouts/{name}/split")
        if state is None or split is None:
            return self._builtin(name)
        old_state, old_split = self.window.saveState(), self.window.hs_split.saveState()
        if self.window.restoreState(state) and self.window.hs_split.restoreState(split):
            return True
        self.window.restoreState(old_state)
        self.window.hs_split.restoreState(old_split)
        return False

    def focus(self, enabled: bool) -> None:
        """Temporarily hide side panels and docks without overwriting a preset."""
        if enabled and self.before_focus is None:
            # Snapshot both QMainWindow docks and the unrelated central splitter.
            self.before_focus = (self.window.saveState(), self.window.hs_split.saveState(),
                                 self.window.side_bar.isVisible(), self.window.side_panel.isVisible(),
                                 self.window.menuBar().isVisible())
            for dock in self.window.findChildren(QDockWidget):
                dock.hide()
            self.window.side_bar.hide()
            self.window.side_panel.hide()
            self.window.menuBar().hide()
        elif not enabled and self.before_focus is not None:
            # Restoration uses the exact preceding layout, not a canned preset.
            state, split, bar, panel, menu = self.before_focus
            self.window.restoreState(state)
            self.window.hs_split.restoreState(split)
            self.window.side_bar.setVisible(bar)
            self.window.side_panel.setVisible(panel)
            self.window.menuBar().setVisible(menu)
            self.before_focus = None

    def _builtin(self, name):
        """Apply default Python, Markdown or Git geometry before a user saves an override."""
        if name not in {"Python Coding", "Markdown Writing", "Git Review"}:
            return False
        window = self.window
        for dock in window.findChildren(QDockWidget):
            dock.hide()
        window.menuBar().show()
        window.side_bar.show()
        window.side_panel.setVisible(name != "Markdown Writing")
        window.preview.setVisible(name == "Markdown Writing")
        if name == "Python Coding":
            window.side_panel.setCurrentWidget(window.outline_frame)
            window.console_dock.show()
            window.hs_split.setSizes([260, 900, 0])
        elif name == "Markdown Writing":
            window.hs_split.setSizes([0, 600, 600])
            window.render_preview()
        else:
            for dock in window.findChildren(QDockWidget):
                if dock.objectName() == "GitHistoryDock":
                    dock.show()
            window.side_panel.setCurrentWidget(window.file_manager_frame)
            window.hs_split.setSizes([280, 900, 0])
        return True
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Layouts` | Persist named dock/split layouts and reversible focus mode. |
| `Layouts.__init__` | Own only layout snapshots; the QMainWindow owns its child widgets. |
| `Layouts.save` | Capture dock geometry and the three-pane splitter in QSettings. |
| `Layouts.restore` | Restore saved geometry atomically, or apply one of three built-in layouts. |
| `Layouts.focus` | Temporarily hide side panels and docks without overwriting a preset. |
| `Layouts._builtin` | Apply default Python, Markdown or Git geometry before a user saves an override. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_settings.workspace_layouts import Layouts
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_focus_mode(self):
        """Keep a window-level shortcut reachable while the menu bar is hidden."""
        self.layouts = Layouts(self)
        menu = self.menuBar().addMenu("Workspace layout")
        action = menu.addAction("Focus mode")
        action.setObjectName("view.focus")
        action.setShortcut("Ctrl+Shift+F11")
        action.setShortcutContext(Qt.ApplicationShortcut)
        self.addAction(action)
        action.triggered.connect(lambda: self.layouts.focus(self.layouts.before_focus is None))
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_focus_mode()
```



#### Edit `main.py` — `MainWindow.set_up_console_dock`

Give the existing console a persistent dock identity.

Inside this method, find exactly:

```python
        dock = QDockWidget("Python Console", self)
```

Replace only that block with:

```python
        dock = QDockWidget("Python Console", self)
        dock.setObjectName("ConsoleDock")
```



#### Edit `main.py` — `MainWindow.set_up_console_dock`

Give the existing terminal a persistent dock identity.

Inside this method, find exactly:

```python
        t_dock = QDockWidget("Terminal", self)
```

Replace only that block with:

```python
        t_dock = QDockWidget("Terminal", self)
        t_dock.setObjectName("TerminalDock")
```



**Use this topic:** Run `python main.py` from the repository root. Press Ctrl+Shift+F11 to enter focus mode and press it again to restore the previous layout.


<a id="topic-9"></a>
## 9. Workspace layout presets

### Topic explanation

Python Coding, Markdown Writing, and Git Review work immediately as built-in layouts. Named saved layouts retain QMainWindow state, geometry, splitter sizes, and central-panel visibility.

The same Layouts helper supplies Python Coding, Markdown Writing and Git Review presets. Saving a named layout persists the dock and splitter states. Restoration falls back to the built-in preset when no saved state exists and rolls back a failed restore.


**Documentation:**

- [Qt main-window state](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)
- [Qt settings](https://doc.qt.io/archives/qt-5.15/qsettings.html)

### Topic code


No new source file is needed. The complete topic methods belong to `MainWindow` in the existing `main.py`:

```python
    def _guide_save_layout(self) -> None:
        """Capture the current layout under a reusable preset name."""
        from PyQt5.QtWidgets import QInputDialog
        name, accepted = QInputDialog.getText(self, "Save layout", "Name")
        if accepted and name.strip():
            self.layouts.save(name.strip())
```

```python
    def _install_topic_9(self):
        """Expose the layout presets commands in the existing menu bar."""
        menu = self.menuBar().addMenu('Layout presets')
        action_0 = menu.addAction('Python Coding')
        action_0.setObjectName("topic.9.0")
        action_0.triggered.connect(lambda checked=False: self.layouts.restore('Python Coding'))
        action_1 = menu.addAction('Markdown Writing')
        action_1.setObjectName("topic.9.1")
        action_1.triggered.connect(lambda checked=False: self.layouts.restore('Markdown Writing'))
        action_2 = menu.addAction('Git Review')
        action_2.setObjectName("topic.9.2")
        action_2.triggered.connect(lambda checked=False: self.layouts.restore('Git Review'))
        action_3 = menu.addAction('Save current layout')
        action_3.setObjectName("topic.9.3")
        action_3.triggered.connect(lambda checked=False: self._guide_save_layout())
```


The implementation section identifies their exact insertion points and startup connections. Paste each method only once.


### Topic implementation

**Required first:** Topic 8.


#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _guide_save_layout(self) -> None:
        """Capture the current layout under a reusable preset name."""
        from PyQt5.QtWidgets import QInputDialog
        name, accepted = QInputDialog.getText(self, "Save layout", "Name")
        if accepted and name.strip():
            self.layouts.save(name.strip())
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_topic_9(self):
        """Expose the layout presets commands in the existing menu bar."""
        menu = self.menuBar().addMenu('Layout presets')
        action_0 = menu.addAction('Python Coding')
        action_0.setObjectName("topic.9.0")
        action_0.triggered.connect(lambda checked=False: self.layouts.restore('Python Coding'))
        action_1 = menu.addAction('Markdown Writing')
        action_1.setObjectName("topic.9.1")
        action_1.triggered.connect(lambda checked=False: self.layouts.restore('Markdown Writing'))
        action_2 = menu.addAction('Git Review')
        action_2.setObjectName("topic.9.2")
        action_2.triggered.connect(lambda checked=False: self.layouts.restore('Git Review'))
        action_3 = menu.addAction('Save current layout')
        action_3.setObjectName("topic.9.3")
        action_3.triggered.connect(lambda checked=False: self._guide_save_layout())
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_topic_9()
```



**Use this topic:** Run `python main.py` from the repository root. Use Layout presets to select a built-in layout or save the current one under a name.


<a id="topic-10"></a>
## 10. Automatic recovery

### Topic explanation

Automatic recovery saves dirty document snapshots to application data every five seconds. Recovery records retain identity and logical path, and reopening creates a draft so disk files are not silently overwritten.

RecoveryStore atomically writes dirty-buffer snapshots under the application data directory. A per-buffer UUID survives editor-mode conversion. MainWindow owns the five-second timer, offers restoration into unsaved copies, and removes snapshots only after successful save or accepted discard/close decisions.


**Documentation:**

- [Python tempfile](https://docs.python.org/3/library/tempfile.html)
- [Qt application data paths](https://doc.qt.io/archives/qt-5.15/qstandardpaths.html)

### Topic code


#### Create file: `code_inteligence/document_recovery.py`

**Folder:** `code_inteligence/` already exists. **File:** `document_recovery.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Atomic dirty-buffer snapshots separate from saved-file sessions."""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import os
import tempfile
import time


def atomic_bytes(path: Path, data: bytes) -> None:
    """Replace a file on the same filesystem, flushing before rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            staged = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        # Rename in the same directory atomically makes a reader see either
        # the old complete file or the new complete file.
        if path.exists():
            os.chmod(staged, path.stat().st_mode & 0o777)
        os.replace(staged, path)
        staged = None
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


class RecoveryStore:
    """Keep dirty buffers apart from normal saved-tab session metadata."""

    def __init__(self, directory: Path):
        """Use a local user data location, never a project repository."""
        self.directory = directory

    def write(self, identity: str, path: Path | None, text: str,
              python: bool = False) -> None:
        """Atomically replace one dirty-buffer snapshot and its path metadata."""
        # A stable UUID survives Save As; the path is only a recovery hint.
        key = hashlib.sha256(identity.encode()).hexdigest()
        payload = {"id": identity, "path": str(path) if path else None,
                   "text": text, "python": python, "saved_at": time.time()}
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        # The reader's maximum applies to the entire JSON record, not only
        # to the text field. Never write a snapshot it would later refuse.
        if len(encoded) > 16_000_000:
            raise ValueError("Recovery snapshot exceeds the 16 MB limit")
        atomic_bytes(self.directory / f"{key}.json", encoded)

    def forget(self, identity: str) -> None:
        """Delete a snapshot only after its editor is saved or discarded."""
        key = hashlib.sha256(identity.encode()).hexdigest()
        (self.directory / f"{key}.json").unlink(missing_ok=True)

    def pending(self) -> list[dict]:
        """Read available snapshots, skipping damaged or oversized records."""
        result = []
        for file in self.directory.glob("*.json"):
            try:
                if file.stat().st_size > 16_000_000:
                    continue
                item = json.loads(file.read_text(encoding="utf-8"))
                if (isinstance(item, dict)
                        and isinstance(item.get("id"), str)
                        and isinstance(item.get("text"), str)
                        and (item.get("path") is None or isinstance(item.get("path"), str))
                        and isinstance(item.get("saved_at", 0), (int, float))):
                    result.append(item)
            except (OSError, ValueError, TypeError):
                continue
        return sorted(result, key=lambda item: item.get("saved_at", 0), reverse=True)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `atomic_bytes` | Replace a file on the same filesystem, flushing before rename. |
| `RecoveryStore` | Keep dirty buffers apart from normal saved-tab session metadata. |
| `RecoveryStore.__init__` | Use a local user data location, never a project repository. |
| `RecoveryStore.write` | Atomically replace one dirty-buffer snapshot and its path metadata. |
| `RecoveryStore.forget` | Delete a snapshot only after its editor is saved or discarded. |
| `RecoveryStore.pending` | Read available snapshots, skipping damaged or oversized records. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
import uuid
from code_inteligence.document_recovery import RecoveryStore
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_recovery(self):
        """Create recovery storage and start periodic dirty-buffer snapshots."""
        root = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        self.recovery = RecoveryStore(root / "recovery")
        self._recovery_timer = QTimer(self)
        self._recovery_timer.setInterval(5000)
        self._recovery_timer.timeout.connect(self._guide_flush_recovery)
        self._recovery_timer.start()

    def _forget_recovery(self, editor):
        """Remove a snapshot only after a successful save or explicit discard."""
        try:
            self.recovery.forget(editor._recovery_id)
        except OSError as error:
            self.statusBar().showMessage(f"Recovery cleanup failed: {error}", 5000)

    def _guide_flush_recovery(self) -> None:
        """Snapshot dirty buffers every five seconds without touching disk files."""
        for editor in self.tab_view.all_editors():
            if editor in self._dirty_editors:
                try:
                    self.recovery.write(editor._recovery_id, getattr(editor, "path", None),
                                        editor.text(), isinstance(editor, PythonEditor))
                except (OSError, ValueError) as error:
                    # A periodic Qt slot must report an I/O failure rather
                    # than unwind into Qt's event loop.
                    self.statusBar().showMessage(f"Recovery unavailable: {error}", 5000)

    def _guide_restore_recovery(self) -> None:
        """Ask before restoring snapshots; never overwrite a newer disk file."""
        for item in self.recovery.pending():
            if QMessageBox.question(self, "Recover buffer",
                                    f"Restore unsaved content from {item['path'] or 'Untitled'}?",
                                    QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                continue
            previous_mode = self.python_editor_active
            self.python_editor_active = bool(item.get("python"))
            try:
                editor = self.new_file()
            finally:
                self.python_editor_active = previous_mode
            editor.setText(item["text"])
            editor._recovery_id = item["id"]
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_recovery()
```



#### Edit `main.py` — `MainWindow.__init__`

Ask about recovery after normal saved-file session restoration.

Inside this method, find exactly:

```python
        self._restore_session()
```

Replace only that block with:

```python
        self._restore_session()
        self._guide_restore_recovery()
```



#### Insert at the start of `main.py` — `MainWindow._connect_editor`

Assign each new buffer a stable snapshot identity. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if not hasattr(editor, "_recovery_id"):
            editor._recovery_id = str(uuid.uuid4())
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

Delete its recovery snapshot only after the atomic save succeeded.

Inside this method, find exactly:

```python
        self.mark_editor_clean(editor)
```

Replace only that block with:

```python
        self.mark_editor_clean(editor)
        self._forget_recovery(editor)
```



#### Edit `main.py` — `MainWindow.close_editor`

A successful close has resolved save/discard; Cancel already returned above.

Inside this method, find exactly:

```python
        self._dirty_editors.discard(editor)
```

Replace only that block with:

```python
        self._forget_recovery(editor)
        self._dirty_editors.discard(editor)
```



#### Edit `main.py` — `MainWindow.closeEvent`

Accepted application-close decisions remove obsolete snapshots. Cancel leaves recovery running.

Inside this method, find exactly:

```python
            self._close_prompts_complete = True
```

Replace only that block with:

```python
            for view in self.tab_view.all_editors():
                self._forget_recovery(view)
            self._recovery_timer.stop()
            self._close_prompts_complete = True
```



#### Edit `main.py` — `MainWindow._convert_editor`

Keep the same recovery record when Save As converts editor language.

Inside this method, find exactly:

```python
        new_editor.setTextSafely(text)
```

Replace only that block with:

```python
        new_editor.setTextSafely(text)
        new_editor._recovery_id = old._recovery_id
```



**Use this topic:** Run `python main.py` from the repository root. Edit a buffer and leave it dirty for at least five seconds. Recovery snapshots are offered on the next launch if an earlier session ended without resolving that buffer.


<a id="topic-12"></a>
## 12. External-change comparison

### Topic explanation

External edits are detected through filesystem hints followed by background content hashing. Saving a changed file offers reload, keep-buffer, or a three-way merge draft based on the last known disk text.

The editor remembers its last accepted disk text as the common ancestor. A conflicting save offers reload, explicit overwrite, or a new merge draft. The pure comparison helper produces conservative conflict markers when it cannot safely combine changes. Only the overwrite choice continues the pending save.


**Documentation:**

- [Python hashlib](https://docs.python.org/3/library/hashlib.html)
- [Qt message boxes](https://doc.qt.io/archives/qt-5.15/qmessagebox.html)

### Topic code


#### Create file: `code_inteligence/text_comparison.py`

**Folder:** `code_inteligence/` already exists. **File:** `text_comparison.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `unified_diff` | Return a readable diff with stable source labels. |
| `three_way` | Merge nonoverlapping line edits; retain both alternatives for conflicts. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.text_comparison import three_way
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _guide_external_conflict(self, editor, raw: bytes) -> str:
        """Offer reload, keep, or an explicit conflict-marker merge draft."""
        disk = raw.decode("utf-8-sig")
        dialog = QMessageBox(self)
        dialog.setWindowTitle("External change")
        dialog.setText("The file changed on disk while this buffer was open.")
        reload = dialog.addButton("Reload disk", QMessageBox.AcceptRole)
        keep = dialog.addButton("Keep buffer", QMessageBox.DestructiveRole)
        merge = dialog.addButton("Merge in new tab", QMessageBox.ActionRole)
        dialog.addButton(QMessageBox.Cancel)
        dialog.exec_()
        chosen = dialog.clickedButton()
        if chosen is reload:
            editor.setTextSafely(disk)
            editor._disk_text = disk
            editor._disk_digest = hashlib.sha256(raw).digest()
            editor._external_changed = False
            editor._utf8_bom = raw.startswith(b"\xef\xbb\xbf")
            from PyQt5.Qsci import QsciScintilla
            crlf = raw.count(b"\r\n")
            lf = raw.count(b"\n") - crlf
            cr = raw.count(b"\r") - crlf
            mode = (QsciScintilla.EolWindows if crlf >= max(lf, cr) and crlf else
                    QsciScintilla.EolMac if cr > max(crlf, lf) else QsciScintilla.EolUnix)
            editor.setEolMode(mode)
            if isinstance(editor, PythonEditor) and editor.ruff_lsp is not None:
                editor.ruff_lsp.sync_from_editor()
            self.mark_editor_clean(editor)
            if hasattr(self, "recovery"):
                self._forget_recovery(editor)
            return "cancel-save"
        if chosen is keep:
            return "overwrite"
        if chosen is merge:
            # Without a stored common ancestor, never claim a clean merge.
            result, _conflict = three_way(getattr(editor, "_disk_text", ""), editor.text(), disk)
            previous_mode = self.python_editor_active
            self.python_editor_active = isinstance(editor, PythonEditor)
            try:
                draft = self.new_file()
            finally:
                self.python_editor_active = previous_mode
            draft.setText(result)
        return "cancel-save"
```



#### Edit `main.py` — `MainWindow.set_new_tab`

Retain the opened disk text as the common ancestor for a merge draft.

Inside this method, find exactly:

```python
        editor.setTextSafely(text)
```

Replace only that block with:

```python
        editor.setTextSafely(text)
        editor._disk_text = text
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

Advance the common ancestor only after a successful save.

Inside this method, find exactly:

```python
        editor._disk_digest = hashlib.sha256(data).digest()
```

Replace only that block with:

```python
        editor._disk_digest = hashlib.sha256(data).digest()
        editor._disk_text = data.decode("utf-8-sig")
```



#### Edit `main.py` — `MainWindow._convert_editor`

Preserve the merge base when changing editor language.

Inside this method, find exactly:

```python
        new_editor.setTextSafely(text)
```

Replace only that block with:

```python
        new_editor.setTextSafely(text)
        new_editor._disk_text = getattr(old, "_disk_text", "")
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

Replace only the external-change yes/cancel branch. Reload or merge cancels this save; only Keep buffer proceeds.

Inside this method, find exactly:

```python
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
```

Replace only that block with:

```python
                try:
                    disk_bytes = target.read_bytes()
                    disk_bytes.decode("utf-8-sig")
                except (OSError, UnicodeError) as error:
                    QMessageBox.warning(self, "External change", str(error))
                    return False
                if self._guide_external_conflict(editor, disk_bytes) != "overwrite":
                    return False
```



**Use this topic:** Run `python main.py` from the repository root. Change an open file from another program, then save its edited buffer to see reload, keep, merge-draft and cancel choices.


<a id="topic-13"></a>
## 13. Compare/diff editor

### Topic explanation

Read-only side-by-side comparison supports buffer versus disk, two selected files, Git HEAD versus buffer, and historical versions. Changed lines are highlighted and scroll positions are synchronized proportionally.

ComparisonDialog shows read-only text panes with changed regions highlighted. MainWindow supplies buffer/disk, two-file and Git HEAD comparisons, catches read/decode errors and opens accepted text as an unsaved draft. No comparison writes either source automatically.


**Documentation:**

- [Python difflib](https://docs.python.org/3/library/difflib.html)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)
- [Qt plain-text editor](https://doc.qt.io/archives/qt-5.15/qplaintextedit.html)

### Topic code


#### Create file: `side_bar_widgets/comparison_dialog.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `comparison_dialog.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Side-by-side immutable comparisons used by history, disk and rename previews."""
from difflib import SequenceMatcher
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
        for tag, a, b, c, d in SequenceMatcher(None, before.splitlines(), after.splitlines(), autojunk=False).get_opcodes():
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `ComparisonDialog` | Show two snapshots with line highlights and synchronized scrolling. |
| `ComparisonDialog.__init__` | Build read-only panes; acceptance never writes a file by itself. |
| `ComparisonDialog._scroll` | Map proportional scroll positions without feedback recursion. |
| `ComparisonDialog._highlight` | Color changed source lines, leaving both snapshots immutable. |


### Topic implementation

**Required first:** None.


#### Shared draft helper in `main.py`

If `_open_draft` was already added by another topic, keep that single definition. Otherwise add this method after `MainWindow._show_update_dialog`, inside the class:

```python
    def _open_draft(self, source, python=False):
        """Create editable draft text without assigning an overwrite destination."""
        previous = self.python_editor_active
        self.python_editor_active = python
        try:
            editor = self.new_file()
            editor.setText(source)
            return editor
        finally:
            self.python_editor_active = previous
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _guide_compare(self, before, after, title):
        """Return explicit approval from a side-by-side, read-only comparison."""
        from side_bar_widgets.comparison_dialog import ComparisonDialog
        label = "Apply rename" if title == "Review rename" else "Open draft"
        return ComparisonDialog(before, after, title, self,
                                accept_text=label).exec_() == QDialog.Accepted

    def _guide_compare_disk(self) -> None:
        """Compare current UTF-8 buffer to the actual symlink-safe disk target."""
        editor = self.current_editor()
        if editor is None or getattr(editor, "path", None) is None:
            return
        try:
            # set_new_tab/_save_editor_to_path already resolved a symlink-safe
            # target, so importing main as a second module is unnecessary.
            target = Path(getattr(editor, "_save_target", editor.path))
            disk = target.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, "Compare", str(error))
            return
        if self._guide_compare(editor.text(), disk, "Buffer versus disk"):
            self._open_draft(disk, isinstance(editor, PythonEditor))

    def _guide_compare_files(self) -> None:
        """Compare two UTF-8 files and optionally open the right-hand text as a draft."""
        from PyQt5.QtWidgets import QFileDialog
        selected = []
        for caption in ("First file", "Second file"):
            filename, _filter = QFileDialog.getOpenFileName(self, caption)
            if not filename:
                return
            selected.append(Path(filename))
        try:
            left, right = (path.read_text(encoding="utf-8-sig") for path in selected)
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, "Compare files", str(error))
            return
        if self._guide_compare(left, right, "Two files"):
            self._open_draft(right, is_python_path(selected[1]))

    def _guide_compare_git_head(self) -> None:
        """Compare the unsaved buffer with this file's Git HEAD bytes."""
        import subprocess
        editor = self.current_editor()
        if editor is None or not getattr(editor, "path", None):
            return
        try:
            folder = Path(editor.path).parent
            root = Path(subprocess.check_output(
                ["git", "-C", str(folder), "rev-parse", "--show-toplevel"],
                stderr=subprocess.STDOUT, text=True,
            ).strip()).resolve()
            path = Path(editor.path).resolve()
            if not path.is_relative_to(root):
                raise ValueError("File is outside the Git repository")
            relative = path.relative_to(root).as_posix()
            before = subprocess.check_output(
                ["git", "-C", str(root), "show", "HEAD:" + relative],
                stderr=subprocess.STDOUT,
            ).decode("utf-8-sig")
        except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as error:
            QMessageBox.warning(self, "Git comparison", str(error))
            return
        if self._guide_compare(before, editor.text(), "Git HEAD versus buffer"):
            self._open_draft(editor.text(), isinstance(editor, PythonEditor))
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_topic_13(self):
        """Expose the compare commands in the existing menu bar."""
        menu = self.menuBar().addMenu('Compare')
        action_0 = menu.addAction('Buffer with disk')
        action_0.setObjectName("topic.13.0")
        action_0.triggered.connect(lambda checked=False: self._guide_compare_disk())
        action_1 = menu.addAction('Two files')
        action_1.setObjectName("topic.13.1")
        action_1.triggered.connect(lambda checked=False: self._guide_compare_files())
        action_2 = menu.addAction('Buffer with Git HEAD')
        action_2.setObjectName("topic.13.2")
        action_2.triggered.connect(lambda checked=False: self._guide_compare_git_head())
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_topic_13()
```



**Use this topic:** Run `python main.py` from the repository root. Use Compare to select a buffer/disk, two-file or Git HEAD comparison.


<a id="topic-11"></a>
## 11. Local file history

### Topic explanation

Local history retains earlier saved file bytes with bounded per-file retention. The history browser lists retained timestamps and sizes, lets you compare any selected version, and opens an accepted version as a new draft.

VersionStore retains bounded pre-save bytes under the application data directory. The save workflow records them only after the primary atomic save succeeds. HistoryDialog selects a version; the comparison workflow opens an accepted version as a new draft rather than silently replacing the current document.


**Documentation:**

- [Python pathlib](https://docs.python.org/3/library/pathlib.html)
- [Python os.replace](https://docs.python.org/3/library/os.html#os.replace)
- [Qt list widgets](https://doc.qt.io/archives/qt-5.15/qlistwidget.html)

### Topic code


#### Create file: `code_inteligence/local_history.py`

**Folder:** `code_inteligence/` already exists. **File:** `local_history.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Bounded predecessor snapshots of successfully saved documents."""
from __future__ import annotations
from code_inteligence.document_recovery import atomic_bytes
from pathlib import Path
import hashlib
import time


class VersionStore:
    """Bounded content-addressed history outside the working tree."""

    def __init__(self, directory: Path, *, keep: int = 30):
        """Choose a per-user storage directory and retention limit."""
        self.directory, self.keep = directory, keep

    def _directory_for(self, path: Path) -> Path:
        """Give distinct projects distinct folders even with identical names."""
        return self.directory / hashlib.sha256(str(path.resolve()).encode()).hexdigest()

    def record(self, path: Path, previous: bytes) -> Path:
        """Record predecessor bytes after the document replacement has succeeded."""
        directory = self._directory_for(path)
        directory.mkdir(parents=True, exist_ok=True)
        name = f"{time.time_ns()}-{hashlib.sha256(previous).hexdigest()[:12]}.bin"
        version = directory / name
        atomic_bytes(version, previous)
        # Keep is per logical file, not a global limit across all projects.
        for stale in sorted(directory.glob("*.bin"), reverse=True)[self.keep:]:
            stale.unlink(missing_ok=True)
        return version

    def versions(self, path: Path) -> list[Path]:
        """Return newest snapshots first for comparison and recovery."""
        return sorted(self._directory_for(path).glob("*.bin"), reverse=True)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `VersionStore` | Bounded content-addressed history outside the working tree. |
| `VersionStore.__init__` | Choose a per-user storage directory and retention limit. |
| `VersionStore._directory_for` | Give distinct projects distinct folders even with identical names. |
| `VersionStore.record` | Record predecessor bytes after the document replacement has succeeded. |
| `VersionStore.versions` | Return newest snapshots first for comparison and recovery. |


#### Create file: `side_bar_widgets/history_dialog.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `history_dialog.py`. Create the file and paste the complete contents starting at line 1.

```python
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
                stamp = datetime.fromtimestamp(int(path.name.split('-')[0]) / 1_000_000_000)
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `HistoryDialog` | Select one predecessor snapshot by timestamp and byte count. |
| `HistoryDialog.__init__` | List newest-first paths supplied by VersionStore, keeping paths as item data. |
| `HistoryDialog.selected_path` | Return the selected version or None when no readable entry remains. |


### Topic implementation

**Required first:** Topic 10, Topic 13.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.local_history import VersionStore
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_history(self):
        """Keep bounded pre-save file versions outside the project directory."""
        root = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        self.history = VersionStore(root / "history")
        menu = self.menuBar().addMenu("Local history")
        menu.addAction("Browse local history", self._guide_browse_history)

    def _record_history(self, path, raw):
        """Record pre-save bytes after the main save has succeeded."""
        if raw is None:
            return
        try:
            self.history.record(Path(path), raw)
        except OSError as error:
            self.statusBar().showMessage(f"History unavailable: {error}", 5000)

    def _guide_browse_history(self):
        """Choose any retained version, compare it and open an explicitly accepted draft."""
        from side_bar_widgets.history_dialog import HistoryDialog
        editor = self.current_editor()
        if editor is None or not getattr(editor, "path", None):
            return
        dialog = HistoryDialog(self.history.versions(Path(editor.path)), self)
        if dialog.exec_() != QDialog.Accepted or dialog.selected_path() is None:
            return
        try:
            old = dialog.selected_path().read_text(encoding="utf-8-sig")
            if self._guide_compare(editor.text(), old, "Compare selected local version"):
                self._open_draft(old, isinstance(editor, PythonEditor))
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self, "Local history", str(error))
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_history()
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

Capture the previous complete bytes before replacing the target.

Inside this method, find exactly:

```python
            data = self._encode_editor_text(editor, formatted)
```

Replace only that block with:

```python
            previous_bytes = target.read_bytes() if target.exists() else None
            data = self._encode_editor_text(editor, formatted)
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

A failed primary save never creates a misleading saved-version record.

Inside this method, find exactly:

```python
        self.mark_editor_clean(editor)
```

Replace only that block with:

```python
        self.mark_editor_clean(editor)
        self._record_history(logical_path, previous_bytes)
```



**Use this topic:** Run `python main.py` from the repository root. Save successive changes to a file, then choose Local history → Browse local history and open an accepted version as a draft.


<a id="topic-17"></a>
## 17. Run configurations

### Topic explanation

Named run configurations persist explicit interpreter, script, working directory, argument list, and environment overrides. A separate lazily created output dock displays streamed output, exit status, and Stop.

RunConfig validates a named executable/script/cwd/argument/environment profile. Profiles are atomically persisted outside the project. ProcessPanel streams output without shell interpolation and provides bounded termination; RunOutputDock displays it separately from the repository’s existing normal Run output.


**Documentation:**

- [Qt process environment](https://doc.qt.io/archives/qt-5.15/qprocessenvironment.html)
- [Python JSON](https://docs.python.org/3/library/json.html)

### Topic code


#### Create file: `python_editor/run_configurations.py`

**Folder:** `python_editor/` already exists. **File:** `run_configurations.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Named process settings and argument-vector execution."""
from __future__ import annotations
from PyQt5.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, pyqtSignal
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit
from code_inteligence.document_recovery import atomic_bytes
from dataclasses import asdict, dataclass
from pathlib import Path
import codecs
import json


@dataclass(frozen=True)
class RunConfig:
    """One named process launch; env contains explicit overrides only."""

    name: str
    interpreter: str
    script: str
    cwd: str
    arguments: list[str]
    env: dict[str, str]


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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `RunConfig` | One named process launch; env contains explicit overrides only. |
| `load_configs` | Parse user-owned JSON without executing its contents. |
| `save_configs` | Atomically persist configurations outside the tracked workspace. |
| `ProcessPanel` | Launch a configuration or pytest via one QProcess and stream its output. |
| `ProcessPanel.__init__` | Connect process signals once; stop it during MainWindow close. |
| `ProcessPanel._read` | Decode incrementally enough for terminal-style test output. |
| `ProcessPanel._on_finished` | Flush an incomplete UTF-8 sequence before publishing exit status. |
| `ProcessPanel.run` | Launch an explicit interpreter/script/cwd/argv/environment tuple. |
| `ProcessPanel.pytest` | Run the whole workspace or one selected test without shell parsing. |
| `ProcessPanel.stop` | Terminate the owned process, forcing exit after two seconds if necessary. |
| `ProcessPanel._error` | Report startup errors as completion because QProcess may omit finished. |
| `RunConfigDialog` | Edit an explicit process launch without involving a shell. |
| `RunConfigDialog.__init__` | Populate typed fields from an existing run configuration. |
| `RunConfigDialog.value` | Parse arguments and environment, raising before any process starts. |
| `validate_config` | Reject malformed persisted and edited fields before passing them to QProcess. |


#### Create file: `python_editor/run_output.py`

**Folder:** `python_editor/` already exists. **File:** `run_output.py`. Create the file and paste the complete contents starting at line 1.

```python
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

    def completed(self, code):
        """Display the exit status and disable Stop after process completion."""
        self.append(f"\nProcess exited with code {code}\n")
        self.stop.setEnabled(False)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `RunOutputDock` | Show a named process's output without mixing it with pytest results. |
| `RunOutputDock.__init__` | Build a bounded output view with an explicit Stop button. |
| `RunOutputDock.begin` | Clear previous output and identify the newly requested profile. |
| `RunOutputDock.append` | Append streamed text exactly, including partial output lines. |
| `RunOutputDock.completed` | Display the exit status and disable Stop after process completion. |


### Topic implementation

**Required first:** Topic 10.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from python_editor.run_configurations import ProcessPanel, RunConfig, RunConfigDialog, load_configs, save_configs
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_run_profiles(self):
        """Own one profile process and its output dock independently of normal Run."""
        from python_editor.run_output import RunOutputDock
        self.runner = ProcessPanel(self)
        self.run_output = RunOutputDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.run_output)
        self.run_output.hide()
        self.runner.output.connect(self.run_output.append)
        self.runner.finished.connect(self.run_output.completed)
        self.run_output.stop_requested.connect(self.runner.stop)
        menu = self.menuBar().addMenu("Run profiles")
        menu.addAction("Run configuration", self._guide_run_configuration)

    def _guide_run_configuration(self) -> None:
        """Edit one persistent launch profile and run it after validation."""
        from PyQt5.QtWidgets import QInputDialog
        location = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)) / "run-configs.json"
        try:
            configs = load_configs(location)
        except (ValueError, TypeError, OSError) as error:
            QMessageBox.warning(self, "Run configurations", str(error))
            return
        if configs:
            labels = [c.name for c in configs]
            chosen, ok = QInputDialog.getItem(self, "Run configurations",
                                              "Select", labels + ["New…"], 0, False)
            if not ok:
                return
            current = configs[labels.index(chosen)] if chosen != "New…" else None
        else:
            current = None
        config = current or RunConfig("New", self.python_runner.interpreter,
                                      "", str(self._workspace_root), [], {})
        dialog = RunConfigDialog(config, self)
        if dialog.exec_() != QDialog.Accepted:
            return
        try:
            result = dialog.value()
            configs = [c for c in configs if c.name != result.name] + [result]
            save_configs(location, configs)
            self.run_output.show()
            self.run_output.begin(result.name)
            self.runner.run(result)
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            QMessageBox.warning(self, "Run configuration", str(error))
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_run_profiles()
```



#### Insert at the start of `main.py` — `MainWindow._background_work_running`

Wait for this topic’s worker without blocking the GUI thread. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if self.runner.process.state() != QProcess.NotRunning:
            return True
```



#### Edit `main.py` — `MainWindow.closeEvent`

Stop this topic’s work only after the close prompts have been accepted.

Inside this method, find exactly:

```python
        self.terminal.stop()
```

Replace only that block with:

```python
        self.runner.stop()
        self.terminal.stop()
```



**Use this topic:** Run `python main.py` from the repository root. Use Run profiles → Run configuration to create a profile and start it. Its own output dock provides Stop.


<a id="topic-16"></a>
## 16. Test runner panel

### Topic explanation

The Tests dock collects exact pytest node IDs, groups them by file, runs the workspace or selected cases, retains failed IDs for rerun, shows structured results and text output, and offers Stop. It owns a process separate from Run File and run profiles.

TestSession owns a dedicated process using the selected interpreter. A small pytest bridge writes structured collection/outcome events; TestDock displays node IDs and output and supports collection, selected runs, rerunning failures, Stop and source navigation. This is an editor feature, not a test suite for this guide.


**Documentation:**

- [Qt QProcess](https://doc.qt.io/archives/qt-5.15/qprocess.html)
- [pytest usage](https://docs.pytest.org/en/stable/how-to/usage.html)
- [pytest hooks and reports](https://docs.pytest.org/en/stable/reference/reference.html)
- [Writing pytest plugins](https://docs.pytest.org/en/stable/how-to/writing_plugins.html)

### Topic code


#### Create file: `python_editor/test_panel.py`

**Folder:** `python_editor/` already exists. **File:** `test_panel.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
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


#### Create file: `python_editor/test_session.py`

**Folder:** `python_editor/` already exists. **File:** `test_session.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Separate pytest process and incremental structured-event reader."""
from __future__ import annotations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from PyQt5.QtCore import QObject, QProcess, QTimer, pyqtSignal
from python_editor.run_configurations import ProcessPanel, RunConfig


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
        with self.path.open('rb') as stream:
            stream.seek(self.offset)
            chunk = stream.read()
            self.offset = stream.tell()
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `TestSession` | Own pytest independently of Run File and named run configurations. |
| `TestSession.__init__` | Create the child process and one reusable event-poll timer. |
| `TestSession.start` | Run exact node IDs, or collect them, without converting them to shell text. |
| `TestSession._read` | Read only new bytes and retain a partial final JSON record until complete. |
| `TestSession._finished` | Drain the last records before publishing process completion. |
| `TestSession.stop` | Request termination with ProcessPanel's bounded kill fallback. |
| `TestSession.is_running` | Report actual process lifetime for application shutdown polling. |
| `TestSession.invalidate` | Stop an old workspace run and discard its pending structured records. |


#### Create file: `python_editor/pytest_bridge.py`

**Folder:** `python_editor/` already exists. **File:** `pytest_bridge.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Reporter` | Translate pytest hooks to flushed JSON records without parsing terminal text. |
| `Reporter.__init__` | Own a fresh event file created by the editor for exactly one run. |
| `Reporter.emit` | Append one complete UTF-8 record so the editor can read incrementally. |
| `Reporter.pytest_collection_finish` | Publish every exact node ID, including parameterized test identities. |
| `Reporter.pytest_collectreport` | Report import/syntax failures separately from failed test assertions. |
| `Reporter.pytest_runtest_logreport` | Record setup/call/teardown outcomes, including skips and xfail metadata. |
| `Reporter.pytest_sessionfinish` | Write the final pytest exit code and close the event stream. |
| `main` | Invoke pytest with unmodified argument-vector entries after editor options. |


### Topic implementation

**Required first:** Topic 17.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from python_editor.test_panel import TestDock
from python_editor.test_session import TestSession
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_test_runner(self):
        """Connect a dedicated pytest process to its test-tree/output dock."""
        self.test_session = TestSession(self)
        self.tests = self._guide_make_tests()
        self.tests.hide()
        menu = self.menuBar().addMenu("Tests")
        menu.addAction("Run workspace tests", lambda: self._guide_run_tests())
        menu.addAction("Collect tests", lambda: self._guide_run_tests(collect=True))
        menu.addAction(self.tests.toggleViewAction())

    def _guide_make_tests(self):
        """Create the collected-test tree and connect its dedicated runner once."""
        dock = TestDock(self._workspace_root, self)
        if not self.restoreDockWidget(dock):
            self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.test_session.output.connect(dock.append)
        self.test_session.finished.connect(dock.completed)
        self.test_session.event_ready.connect(dock.on_event)
        dock.run_requested.connect(self._guide_run_tests)
        dock.collect_requested.connect(lambda: self._guide_run_tests(collect=True))
        dock.targets_requested.connect(lambda targets: self._guide_run_tests(targets))
        dock.stop_requested.connect(self.test_session.stop)
        dock.navigate.connect(lambda path, line: self._open_file_at_position(path, line, 0))
        return dock

    def _guide_run_tests(self, targets=None, collect=False):
        """Run workspace, selected node IDs, or collection in a separate pytest process."""
        try:
            dock = self.tests
            dock.show()
            dock.output.clear()
            dock.state.setText("Collecting…" if collect else "Running…")
            if collect:
                dock.set_context(self._workspace_root, self.python_runner.interpreter)
            self.test_session.start(self.python_runner.interpreter,
                                    self._workspace_root, targets or (), collect=collect)
        except (OSError, ValueError, RuntimeError) as error:
            QMessageBox.warning(self, "Tests", str(error))
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_test_runner()
```



#### Insert at the start of `main.py` — `MainWindow._background_work_running`

Wait for this topic’s worker without blocking the GUI thread. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if self.test_session.is_running():
            return True
```



#### Edit `main.py` — `MainWindow.closeEvent`

Stop this topic’s work only after the close prompts have been accepted.

Inside this method, find exactly:

```python
        self.terminal.stop()
```

Replace only that block with:

```python
        self.test_session.invalidate()
        self.terminal.stop()
```



#### Add at the end of `main.py` — `MainWindow._restart_ruff`

Discard collected node IDs when the project or interpreter changes. Add the following at method-body indentation after the existing body, immediately before the next method definition at class indentation. Keep earlier additions in this method.

```python
        self.test_session.invalidate()
        self.tests.set_context(self._workspace_root, self.python_runner.interpreter)
```



#### Pytest runtime dependency

The editor feature runs pytest using the selected project interpreter. In that environment, install pytest with `python -m pip install pytest`. This guide creates no test files; the panel discovers the project’s existing tests.


**Use this topic:** Run `python main.py` from the repository root. Select a project interpreter with pytest installed, then use Tests → Collect tests or Run workspace tests. No new test files are required by this guide.


<a id="topic-18"></a>
## 18. Configurable keyboard shortcuts

### Topic explanation

The shortcut editor lists stable command IDs and changes the existing QAction bindings. Core editor actions and new feature actions share one registry, including the focus-mode escape action.

MainWindow collects existing live QActions rather than copying callbacks. Explicit object names identify feature actions; existing menu paths identify unnamed legacy actions. Shortcuts validates all bindings before applying any, and ShortcutDialog persists accepted overrides. The dialog re-collects actions so later topic menus are included.


**Documentation:**

- [Qt QAction](https://doc.qt.io/archives/qt-5.15/qaction.html)
- [Qt QKeySequence](https://doc.qt.io/archives/qt-5.15/qkeysequence.html)

### Topic code


#### Create file: `code_settings/keyboard_shortcuts.py`

**Folder:** `code_settings/` already exists. **File:** `keyboard_shortcuts.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Shortcut validation and editing for existing QAction objects."""
from __future__ import annotations
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QKeySequenceEdit, QComboBox, QMessageBox, QVBoxLayout
import json


class Shortcuts:
    """Apply user-defined QAction shortcuts while refusing collisions."""

    def __init__(self, settings):
        """Use the application's existing QSettings instance."""
        self.settings = settings

    def bind(self, actions: dict[str, QAction], overrides: dict[str, str]) -> None:
        """Validate every binding before mutating any action."""
        from PyQt5.QtGui import QKeySequence
        keys = {}
        # First pass detects all collisions. No QAction changes until it passes.
        for command, action in actions.items():
            requested = overrides.get(command, action.shortcut().toString())
            sequence = QKeySequence(requested)
            normalized = sequence.toString()
            if requested and not normalized:
                raise ValueError(f"Invalid shortcut for {command}")
            if normalized in keys and normalized:
                raise ValueError(f"Shortcut conflict: {command} and {keys[normalized]}")
            keys[normalized] = command
        for command, action in actions.items():
            action.setShortcut(overrides.get(command, action.shortcut().toString()))
        self.settings.setValue("shortcuts", json.dumps(overrides))


class ShortcutDialog(QDialog):
    """Search QAction names and edit one shortcut after conflict validation."""

    def __init__(self, actions, settings, parent=None):
        """Retain command IDs and existing QActions, not copies of their text."""
        super().__init__(parent)
        self.setWindowTitle("Keyboard shortcuts")
        self.actions, self.settings = actions, settings
        layout = QVBoxLayout(self)
        self.command = QComboBox(self)
        self.command.setEditable(True)
        self.command.addItems(sorted(actions))
        layout.addWidget(self.command)
        self.sequence = QKeySequenceEdit(self)
        layout.addWidget(self.sequence)
        self.command.currentTextChanged.connect(self._load)
        self._load(self.command.currentText())
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load(self, command: str) -> None:
        """Show the existing binding only for a known command ID."""
        action = self.actions.get(command)
        if action is not None:
            self.sequence.setKeySequence(action.shortcut())

    def accept(self) -> None:
        """Commit a single binding only after checking every QAction."""
        command = self.command.currentText().strip()
        try:
            if command not in self.actions:
                raise ValueError("Unknown command ID")
            overrides = json.loads(self.settings.value("shortcuts", "{}", type=str))
            overrides[command] = self.sequence.keySequence().toString()
            Shortcuts(self.settings).bind(self.actions, overrides)
        except (ValueError, TypeError) as error:
            QMessageBox.warning(self, "Shortcuts", str(error))
            return
        super().accept()
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Shortcuts` | Apply user-defined QAction shortcuts while refusing collisions. |
| `Shortcuts.__init__` | Use the application's existing QSettings instance. |
| `Shortcuts.bind` | Validate every binding before mutating any action. |
| `ShortcutDialog` | Search QAction names and edit one shortcut after conflict validation. |
| `ShortcutDialog.__init__` | Retain command IDs and existing QActions, not copies of their text. |
| `ShortcutDialog._load` | Show the existing binding only for a known command ID. |
| `ShortcutDialog.accept` | Commit a single binding only after checking every QAction. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_settings.keyboard_shortcuts import Shortcuts, ShortcutDialog
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _collect_shortcut_actions(self):
        """Collect live leaf actions using explicit IDs or a stable menu-path fallback."""
        actions = {}
        def visit(menu, prefix):
            """Walk submenus without copying action callbacks or shortcut state."""
            for action in menu.actions():
                label = action.text().replace("&", "").strip()
                if action.menu() is not None:
                    visit(action.menu(), prefix + "/" + label)
                elif not action.isSeparator() and label:
                    key = action.objectName() or prefix + "/" + label
                    actions[key] = action
        for action in self.menuBar().actions():
            if action.menu() is not None:
                visit(action.menu(), action.text().replace("&", ""))
        return actions

    def _install_shortcuts(self):
        """Create the shortcut editor and apply saved overrides after all menus exist."""
        menu = self.menuBar().addMenu("Shortcuts")
        action = menu.addAction("Configure shortcuts")
        action.setObjectName("settings.shortcuts")
        action.triggered.connect(self._configure_shortcuts)
        # Startup callbacks added by other topics finish before this queued call.
        QTimer.singleShot(0, self._load_shortcut_overrides)

    def _load_shortcut_overrides(self):
        """Validate stored overrides against the currently available live actions."""
        try:
            overrides = json.loads(self.settings.value("shortcuts", "{}", type=str))
            Shortcuts(self.settings).bind(self._collect_shortcut_actions(), overrides)
        except (TypeError, ValueError) as error:
            self.statusBar().showMessage(f"Invalid shortcut settings: {error}", 5000)

    def _configure_shortcuts(self):
        """Edit current menu actions, including menus introduced by later topics."""
        ShortcutDialog(self._collect_shortcut_actions(), self.settings, self).exec_()
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_shortcuts()
```



**Use this topic:** Run `python main.py` from the repository root. Choose Shortcuts → Configure shortcuts; select a known command and save a non-conflicting binding.


<a id="topic-19"></a>
## 19. Smarter pair handling

### Topic explanation

Pair handling wraps selections, inserts matching delimiters, skips an existing closer, and deletes an empty pair as one undo action. Context guards avoid unwanted quote insertion inside Python strings/comments, escaped quotes, and apostrophes in words.

The pure pair helpers use Scintilla byte positions, wrap selections as one undo operation, skip existing closing characters and remove empty pairs together. Their calls are inserted into both editor key handlers without replacing completion/indentation or Python signature scheduling.


**Documentation:**

- [QScintilla overview](https://www.riverbankcomputing.com/software/qscintilla/intro)
- [Python Unicode encodings](https://docs.python.org/3/howto/unicode.html)

### Topic code


#### Create file: `code_inteligence/pair_handling.py`

**Folder:** `code_inteligence/` already exists. **File:** `pair_handling.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Undoable bracket and quote handling shared by both editors."""
from __future__ import annotations


PAIRS = {"(": ")", "[": "]", "{": "}", "'": "'", '"': '"', "`": "`"}


def pair_key(editor, key: str) -> bool:
    """Handle simple bracket/quote keys in one undo action; otherwise defer."""
    if key not in PAIRS and key not in PAIRS.values():
        return False
    selected = editor.selectedText().replace("\u2029", "\n")
    line, column = editor.getCursorPosition()
    close = PAIRS.get(key)
    if selected and close is not None:
        editor.beginUndoAction()
        try:
            editor.replaceSelectedText(key + selected + close)
        finally:
            editor.endUndoAction()
        return True
    # Closing a previously inserted pair should move the cursor, not double it.
    # QScintilla's high-level line/index API counts Unicode characters.
    # Raw SendScintilla document positions count UTF-8 bytes; do not mix them.
    if key in PAIRS.values() and editor.text(line)[column:column + 1] == key:
        editor.setCursorPosition(line, column + 1)
        return True
    if close is None or not pairing_allowed(editor, key, line, column):
        return False
    editor.beginUndoAction()
    try:
        editor.insert(key + close)
    finally:
        editor.endUndoAction()
    editor.setCursorPosition(line, column + 1)
    return True


def empty_pair_backspace(editor) -> bool:
    """Delete both adjacent pair characters on Backspace, keeping one undo."""
    if editor.hasSelectedText():
        return False
    line, column = editor.getCursorPosition()
    text = editor.text(line)
    if column == 0 or column >= len(text):
        return False
    if PAIRS.get(text[column - 1]) != text[column]:
        return False
    # One undo group means Undo restores the complete pair, not half of it.
    editor.beginUndoAction()
    try:
        editor.setSelection(line, column - 1, line, column + 1)
        editor.removeSelectedText()
    finally:
        editor.endUndoAction()
    return True

def pairing_allowed(editor, key, line, column):
    """Avoid escaped quotes, word-internal apostrophes, and Python string/comment pairs."""
    before = editor.text(line)[:column]
    if key in {"'", '"', "`"}:
        escapes = len(before) - len(before.rstrip("\\"))
        if escapes % 2 or (before and (before[-1].isalnum() or before[-1] == "_")):
            return False
    if getattr(editor, "is_python_file", False):
        from python_editor.custompythonlexer import _py_compute_state
        source = editor.text().encode("utf-8")
        position = editor.positionFromLineIndex(line, column)
        state = _py_compute_state(source, position)
        if state & 3:  # Prefix state bit 0 is string; bit 1 is comment.
            return False
    return True
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `pair_key` | Handle simple bracket/quote keys in one undo action; otherwise defer. |
| `empty_pair_backspace` | Delete both adjacent pair characters on Backspace, keeping one undo. |
| `pairing_allowed` | Avoid escaped quotes, word-internal apostrophes, and Python string/comment pairs. |


### Topic implementation

**Required first:** None.


#### Imports in `python_editor/pythoneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.pair_handling import pair_key, empty_pair_backspace
```



#### Replace `python_editor/pythoneditor.py` — `PythonEditor.keyPressEvent`

Add byte-correct pair handling while retaining completion, indentation and signature scheduling. Delete this method’s complete current definition, from `def keyPressEvent(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
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

            # Pairing runs after callable detection so inserting '(' through
            # pair_key still schedules the existing signature helper.
            if event.modifiers() in (Qt.NoModifier, Qt.ShiftModifier):
                if event.key() == Qt.Key_Backspace and empty_pair_backspace(self):
                    event.accept()
                    return
                if pair_key(self, event.text()):
                    event.accept()
                    return

            return super().keyPressEvent(event)
```



#### Imports in `markdown_editor/markdowneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.pair_handling import pair_key, empty_pair_backspace
```



#### Replace `markdown_editor/markdowneditor.py` — `MarkdownEditor.keyPressEvent`

Add byte-correct pair handling while retaining completion, indentation and signature scheduling. Delete this method’s complete current definition, from `def keyPressEvent(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def keyPressEvent(self, e: QKeyEvent) -> None:
        """Insert smart pairs while preserving the existing Ctrl+Space action."""
        if e.modifiers() == Qt.KeyboardModifier.ControlModifier and e.key() == Qt.Key.Key_Space:
            self.autoCompleteFromAll()
            return
        if e.modifiers() in (Qt.NoModifier, Qt.ShiftModifier):
            if e.key() == Qt.Key_Backspace and empty_pair_backspace(self):
                e.accept()
                return
            if pair_key(self, e.text()):
                e.accept()
                return
        return super().keyPressEvent(e)
```



**Use this topic:** Run `python main.py` from the repository root. Type an opening bracket or quote, wrap a selection, skip an existing closer, or Backspace between an empty pair.


<a id="topic-20"></a>
## 20. Outline and navigation

### Topic explanation

Python scope navigation and Markdown outline navigation use source-aware records. Markdown headings follow the actual Python-Markdown dialect, including setext headings and duplicate anchors such as setup_1. TOC and heading links reuse those records.

The Markdown document model uses the same rendering extensions as preview to assign headings and slugs, including duplicate and Unicode headings. Heading navigation and MarkdownOutline reuse that model. MainWindow switches between the existing Python outline and Markdown outline, and the sanitizer preserves generated heading IDs.


**Documentation:**

- [Python regular expressions](https://docs.python.org/3/library/re.html)
- [Qt tree widget](https://doc.qt.io/archives/qt-5.15/qtreewidget.html)
- [Python-Markdown TOC and IDs](https://python-markdown.github.io/extensions/toc/)
- [Python-Markdown extension API](https://python-markdown.github.io/extensions/api/)

### Topic code


#### Create file: `markdown_editor/document_model.py`

**Folder:** `markdown_editor/` already exists. **File:** `document_model.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
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


#### Create file: `markdown_editor/heading_navigation.py`

**Folder:** `markdown_editor/` already exists. **File:** `heading_navigation.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `markdown_headings` | Return real rendered ATX/setext headings with zero-based source positions. |
| `heading_link` | Create a link to an exact source heading using its final preview ID. |
| `toc` | Build a heading list in one parse using the actual preview's anchor IDs. |


#### Create file: `side_bar_widgets/markdown_outline.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `markdown_outline.py`. Create the file and paste the complete contents starting at line 1.

```python
"""A heading tree beside the existing Python outline."""
from __future__ import annotations
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from markdown_editor.heading_navigation import markdown_headings


class MarkdownOutline(QTreeWidget):
    """Show headings outside fenced blocks with source-line navigation."""

    activated_line = pyqtSignal(int)

    def __init__(self, parent=None):
        """Connect activation once and hide the single-column header."""
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.itemActivated.connect(self._activate)
        self.itemClicked.connect(self._activate)

    def refresh(self, source: str) -> None:
        """Build a heading hierarchy without running a Markdown renderer."""
        self.clear()
        stack = []
        for heading in markdown_headings(source):
            while stack and stack[-1][0] >= heading.level:
                stack.pop()
            parent = stack[-1][1] if stack else self
            item = QTreeWidgetItem(parent)
            item.setText(0, heading.title)
            item.setData(0, Qt.UserRole, heading.line)
            stack.append((heading.level, item))
        self.expandAll()

    def _activate(self, item, _column: int) -> None:
        """Emit the source line for a clicked heading."""
        line = item.data(0, Qt.UserRole)
        if line is not None:
            self.activated_line.emit(line)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `MarkdownOutline` | Show headings outside fenced blocks with source-line navigation. |
| `MarkdownOutline.__init__` | Connect activation once and hide the single-column header. |
| `MarkdownOutline.refresh` | Build a heading hierarchy without running a Markdown renderer. |
| `MarkdownOutline._activate` | Emit the source line for a clicked heading. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.markdown_outline import MarkdownOutline
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_markdown_outline(self):
        """Add a Markdown outline beside the existing Python outline tree."""
        self.md_outline = MarkdownOutline(self)
        self.md_outline.activated_line.connect(self._jump_heading)
        self.outline_frame.layout().addWidget(self.md_outline)
        self.md_outline.hide()

    def _jump_heading(self, line):
        """Move the active editor to a selected zero-based heading line."""
        editor = self.current_editor()
        if editor is not None:
            editor.setCursorPosition(line, 0)
            editor.ensureLineVisible(line)
            editor.setFocus()
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_markdown_outline()
```



#### Replace `main.py` — `MainWindow._update_outline`

Retain the existing Python outline and select the Markdown tree only for Markdown tabs. Delete this method’s complete current definition, from `def _update_outline(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _update_outline(self):
        """Select the language outline and rebuild it from the current buffer."""
        editor = self.current_editor()
        if not hasattr(self, "md_outline"):
            return
        self.md_outline.setVisible(isinstance(editor, MarkdownEditor))
        self.outline_tree.setVisible(isinstance(editor, PythonEditor))
        if isinstance(editor, MarkdownEditor):
            self.md_outline.refresh(editor.text())
        elif isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.md_outline.clear()
            self.outline_tree.clear()
```



#### Insert at the start of `main.py` — `MainWindow._on_current_editor_changed`

Refresh the newly focused document’s headings. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        self._update_outline()
```



#### Heading IDs in `main.py`

Replace the entire module-level `MARKDOWN_ALLOWED_ATTRIBUTES` assignment, immediately before `MARKDOWN_ALLOWED_PROTOCOLS`, with:

```python
MARKDOWN_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "th": ["align"],
    "td": ["align"],
    **{f"h{level}": ["id"] for level in range(1, 7)},
}
```

This preserves generated heading anchors while retaining the existing tag and protocol allowlists.


**Use this topic:** Run `python main.py` from the repository root. Open Markdown and show Outline. Activate a heading and use the preview heading anchors.


<a id="topic-3"></a>
## 3. Breadcrumb navigation

### Topic explanation

Breadcrumbs show the active document and its containing Python class/function. Symbol extraction uses Python AST ranges, so a method belongs to its containing class rather than to the most recently encountered name.

A pure symbol index identifies Python definitions and the shared Markdown heading parser provides heading locations. MainWindow places the breadcrumb above the current central widget and updates it only for the active editor. Button callbacks capture coordinates rather than retaining editor widgets.


**Documentation:**

- [Python AST locations](https://docs.python.org/3/library/ast.html)
- [Qt layouts](https://doc.qt.io/archives/qt-5.15/qhboxlayout.html)

### Topic code


#### Create file: `code_inteligence/symbol_index.py`

**Folder:** `code_inteligence/` already exists. **File:** `symbol_index.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Python source symbols and bounded workspace indexing."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import ast
import os


@dataclass(frozen=True)
class Symbol:
    """A workspace symbol with a zero-based QScintilla destination."""

    path: Path
    name: str
    kind: str
    line: int
    column: int
    parent: str = ""
    end_line: int = 0


def python_symbols(path: Path, source: str) -> list[Symbol]:
    """Parse definitions without executing user code; reject incomplete syntax."""
    # Parsing is safe for an untrusted project: ast.parse builds a syntax tree
    # and does not import a module or execute any of its top-level statements.
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    result = []

    def visit(body, parent=""):
        """Walk immediate members so a method retains its class breadcrumb."""
        for node in body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                # AST lines are 1-based; the editor's line API is 0-based.
                result.append(Symbol(path, node.name, kind, node.lineno - 1,
                                     node.col_offset, parent,
                                     getattr(node, "end_lineno", node.lineno) - 1))
                visit(node.body, f"{parent}.{node.name}".strip("."))
    visit(tree.body)
    return result


def symbol_at(symbols: list[Symbol], line: int) -> list[Symbol]:
    """Return the enclosing symbol chain for a zero-based source line."""
    # AST end_lineno prevents a method breadcrumb leaking into the next class.
    eligible = [item for item in symbols if item.line <= line <= item.end_line]
    return sorted(eligible, key=lambda item: (item.line, -item.end_line))


def workspace_symbols(root: Path, *, limit: int = 2000) -> list[Symbol]:
    """Build a bounded index, skipping virtualenvs and unreadable files."""
    result = []
    skip = {".git", ".venv", "venv", "__pycache__", "build", "dist"}
    for folder, dirs, files in os.walk(root):
        # Mutating dirs in-place tells os.walk not to descend into these trees.
        dirs[:] = [name for name in dirs if name not in skip]
        for name in files:
            if not name.endswith((".py", ".pyi")):
                continue
            path = Path(folder) / name
            try:
                if path.is_symlink():
                    continue
                if path.stat().st_size > 2_000_000:
                    continue
                result.extend(python_symbols(path, path.read_text(encoding="utf-8-sig")))
            except (OSError, UnicodeError):
                continue
            if len(result) >= limit:
                return result[:limit]
    return result
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Symbol` | A workspace symbol with a zero-based QScintilla destination. |
| `python_symbols` | Parse definitions without executing user code; reject incomplete syntax. |
| `python_symbols.visit` | Walk immediate members so a method retains its class breadcrumb. |
| `symbol_at` | Return the enclosing symbol chain for a zero-based source line. |
| `workspace_symbols` | Build a bounded index, skipping virtualenvs and unreadable files. |


#### Create file: `side_bar_widgets/breadcrumb.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `breadcrumb.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Clickable document and symbol navigation."""
from __future__ import annotations
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget
from code_inteligence.symbol_index import python_symbols
from code_inteligence.symbol_index import symbol_at
from markdown_editor.heading_navigation import markdown_headings
from pathlib import Path


class Breadcrumb(QWidget):
    """A clickable project/file/symbol chain above the active editor group."""

    def __init__(self, navigate, parent=None):
        """Keep a navigation callback to avoid retaining individual editors."""
        super().__init__(parent)
        self.setProperty("designPanel", True)
        self.navigate = navigate
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(8, 2, 8, 2)
        self.row.addStretch(1)

    def show_location(self, root: Path, path: Path | None, source: str,
                      line: int, python: bool):
        """Replace the breadcrumb on focus, edit and cursor changes."""
        # Discard old buttons before adding targets from the new active editor.
        # The callback captures coordinates, not an editor object that may die.
        while self.row.count():
            item = self.row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if path is None:
            names = [("Untitled", 0, 0)]
        else:
            names = [(root.name, 0, 0), (path.name, 0, 0)]
            if python:
                names += [(s.name, s.line, s.column)
                          for s in symbol_at(python_symbols(path, source), line)]
            else:
                names += [(h.title, h.line, 0)
                          for h in markdown_headings(source) if h.line <= line][-1:]
        for label, row, column in names:
            button = QPushButton(label, self)
            button.setFlat(True)
            button.clicked.connect(lambda _checked=False, r=row, c=column:
                                   self.navigate(r, c))
            self.row.addWidget(button)
        self.row.addStretch(1)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Breadcrumb` | A clickable project/file/symbol chain above the active editor group. |
| `Breadcrumb.__init__` | Keep a navigation callback to avoid retaining individual editors. |
| `Breadcrumb.show_location` | Replace the breadcrumb on focus, edit and cursor changes. |


### Topic implementation

**Required first:** Topic 20.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.breadcrumb import Breadcrumb
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_breadcrumb(self):
        """Place a breadcrumb above the existing central widget without rebuilding it."""
        original = self.takeCentralWidget()
        wrapper = QWidget(self)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        self.breadcrumb = Breadcrumb(self._guide_jump, self)
        layout.addWidget(self.breadcrumb)
        layout.addWidget(original)
        self.setCentralWidget(wrapper)

    def _guide_jump(self, line: int, column: int) -> None:
        """Navigate inside the focused document using QScintilla coordinates."""
        editor = self.current_editor()
        if editor is not None:
            editor.setCursorPosition(line, column)
            editor.ensureLineVisible(line)
            editor.setFocus()

    def _guide_cursor_changed(self, editor) -> None:
        """Render a location only for the active tab to avoid stale callbacks."""
        if editor is not self.current_editor():
            return
        line, _column = editor.getCursorPosition()
        large = (getattr(editor, "_large_file_mode", False)
                 and not getattr(editor, "_large_file_override", False))
        self.breadcrumb.show_location(self._workspace_root,
                                      getattr(editor, "path", None),
                                      "" if large else editor.text(),
                                      line, isinstance(editor, PythonEditor))
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_breadcrumb()
```



#### Insert at the start of `main.py` — `MainWindow._on_editor_cursor_changed`

Update only the active editor’s symbol path. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if hasattr(self, "breadcrumb"):
            self._guide_cursor_changed(editor)
```



#### Insert at the start of `main.py` — `MainWindow._on_current_editor_changed`

Clear or refresh the breadcrumb after a tab switch. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if hasattr(self, "breadcrumb"):
            self.breadcrumb.setVisible(editor is not None)
            if editor is not None:
                self._guide_cursor_changed(editor)
```



**Use this topic:** Run `python main.py` from the repository root. Open Python or Markdown, move the caret into a definition/heading, and activate a breadcrumb segment.


<a id="topic-21"></a>
## 21. Authoring tools

### Topic explanation

Markdown authoring adds validated table rows, relative links, image links, heading links, and a local-link check. Link checking inspects rendered destinations, so reference-style links follow the same parser as preview.

Authoring helpers construct escaped Markdown tables and relative file/image links. The link checker examines rendered local URLs rather than treating web URLs as paths. Heading-link and table-of-contents actions reuse Topic 20’s heading identities. Dialog inputs are validated before inserting generated text.


**Documentation:**

- [Python urllib.parse](https://docs.python.org/3/library/urllib.parse.html)
- [Python os.path](https://docs.python.org/3/library/os.path.html)
- [Python-Markdown reference](https://python-markdown.github.io/reference/)
- [HTMLParser](https://docs.python.org/3/library/html.parser.html)

### Topic code


#### Create file: `markdown_editor/authoring_tools.py`

**Folder:** `markdown_editor/` already exists. **File:** `authoring_tools.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Markdown table and relative-link helpers."""
from __future__ import annotations
from pathlib import Path
import os
import re


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
        return "| " + " | ".join(value.replace("|", r"\|") for value in values) + " |"
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `table` | Make a pipe table, escaping pipes and preserving explicit cell counts. |
| `table.row` | Escape Markdown separators inside each cell. |
| `relative_link` | Create a portable, URL-escaped Markdown link relative to a document. |
| `broken_local_links` | Check renderer-resolved local paths and Markdown heading fragments. |


### Topic implementation

**Required first:** Topic 20.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from markdown_editor.authoring_tools import broken_local_links, relative_link, table
from markdown_editor.heading_navigation import toc
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _guide_insert_table(self):
        """Validate user-entered JSON rows before inserting a table as one undo step."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        value, accepted = QInputDialog.getMultiLineText(self, "Insert table", "Rows as JSON; first row is the header", '[["Column A", "Column B"], ["", ""]]')
        if not accepted:
            return
        try:
            rows = json.loads(value)
            if not isinstance(rows, list) or any(not isinstance(row, list) or
                    any(not isinstance(cell, str) for cell in row) for row in rows):
                raise ValueError("Use a JSON list of rows containing strings")
            content = table(rows)
        except (ValueError, TypeError) as error:
            QMessageBox.warning(self, "Table", str(error))
            return
        editor.beginUndoAction()
        try:
            editor.insert(content)
        finally:
            editor.endUndoAction()

    def _guide_insert_link(self, image=False) -> None:
        """Pick a local target and write a relative, escaped Markdown URL."""
        from PyQt5.QtWidgets import QFileDialog
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or not editor.path:
            return
        value, _filter = QFileDialog.getOpenFileName(self, "Link target",
                                                    str(Path(editor.path).parent))
        if value:
            editor.insert(relative_link(Path(editor.path), Path(value), image=image))

    def _guide_check_links(self) -> None:
        """Summarize broken local paths without treating URLs as files."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or not editor.path:
            return
        bad = broken_local_links(Path(editor.path), editor.text())
        QMessageBox.information(self, "Local links",
                                "\n".join(link for _line, link in bad[:20])
                                if bad else "All checked local links exist")

    def _guide_insert_toc(self) -> None:
        """Insert a generated heading index at the current Markdown caret."""
        editor = self.current_editor()
        if isinstance(editor, MarkdownEditor):
            editor.insert(toc(editor.text()) + "\n")

    def _guide_insert_heading_link(self):
        """Offer rendered headings and insert a correctly escaped local anchor link."""
        from markdown_editor.heading_navigation import markdown_headings, heading_link
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        headings = markdown_headings(editor.text())
        if not headings:
            return
        labels = [f"{h.title} (line {h.line + 1})" for h in headings]
        choice, accepted = QInputDialog.getItem(self, "Heading link", "Heading", labels, 0, False)
        if accepted:
            editor.insert(heading_link(editor.text(), headings[labels.index(choice)].line))
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_topic_21(self):
        """Expose the markdown tools commands in the existing menu bar."""
        menu = self.menuBar().addMenu('Markdown tools')
        action_0 = menu.addAction('Insert table')
        action_0.setObjectName("topic.21.0")
        action_0.triggered.connect(lambda checked=False: self._guide_insert_table())
        action_1 = menu.addAction('Insert relative link')
        action_1.setObjectName("topic.21.1")
        action_1.triggered.connect(lambda checked=False: self._guide_insert_link())
        action_2 = menu.addAction('Insert image')
        action_2.setObjectName("topic.21.2")
        action_2.triggered.connect(lambda checked=False: self._guide_insert_link(image=True))
        action_3 = menu.addAction('Check local links')
        action_3.setObjectName("topic.21.3")
        action_3.triggered.connect(lambda checked=False: self._guide_check_links())
        action_4 = menu.addAction('Insert table of contents')
        action_4.setObjectName("topic.21.4")
        action_4.triggered.connect(lambda checked=False: self._guide_insert_toc())
        action_5 = menu.addAction('Insert heading link')
        action_5.setObjectName("topic.21.5")
        action_5.triggered.connect(lambda checked=False: self._guide_insert_heading_link())
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_topic_21()
```



**Use this topic:** Run `python main.py` from the repository root. Use Markdown tools for a table, link, image, heading link, table of contents or local-link report.


<a id="topic-22"></a>
## 22. Performance diagnostics mode

### Topic explanation

Performance diagnostics are opt-in and store bounded in-memory samples for startup, preview conversion/delivery, lexer work, and shared analysis requests. The timings view summarizes count and durations without recording source text.

Timings keeps bounded in-memory duration samples only while opted in. MainWindow records Markdown conversion time and displays summaries. If the shared queue is installed, its completion signal also reports analysis timings. These records contain operation names and durations, not source text or paths.


**Documentation:**

- [Python time.perf_counter](https://docs.python.org/3/library/time.html#time.perf_counter)
- [Qt QWebEnginePage](https://doc.qt.io/archives/qt-5.15/qwebenginepage.html)

### Topic code


#### Create file: `code_settings/performance_diagnostics.py`

**Folder:** `code_settings/` already exists. **File:** `performance_diagnostics.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Bounded elapsed-time samples for measured operations."""
from __future__ import annotations


class Timings:
    """Keep recent durations in memory; no user source or filenames are logged."""

    def __init__(self, limit: int = 100, enabled: bool = True):
        """Bound the number of samples per measured operation."""
        if limit < 1:
            raise ValueError("Sample limit must be positive")
        self.enabled = enabled
        self.limit, self.samples = limit, {}

    def observe(self, name: str, elapsed: float) -> None:
        """Record elapsed milliseconds for startup, preview and analysis."""
        if not self.enabled:
            return
        # perf_counter() reports seconds; users inspect milliseconds here.
        values = self.samples.setdefault(name, [])
        values.append(elapsed * 1000)
        del values[:-self.limit]

    def summary(self) -> dict[str, tuple[int, float]]:
        """Return count and slowest duration for each operation."""
        return {key: (len(values), max(values)) for key, values in self.samples.items()}
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Timings` | Keep recent durations in memory; no user source or filenames are logged. |
| `Timings.__init__` | Bound the number of samples per measured operation. |
| `Timings.observe` | Record elapsed milliseconds for startup, preview and analysis. |
| `Timings.summary` | Return count and slowest duration for each operation. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
import time
from code_settings.performance_diagnostics import Timings
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_timings(self):
        """Create opt-in, bounded in-memory timing samples and their menu."""
        self.timings = Timings(enabled=self.settings.value("performance_diagnostics", False, type=bool))
        if hasattr(self, "analysis"):
            self.analysis.measured.connect(self.timings.observe)
        menu = self.menuBar().addMenu("Performance")
        enabled = menu.addAction("Enable performance diagnostics")
        enabled.setCheckable(True)
        enabled.setChecked(self.timings.enabled)
        enabled.toggled.connect(self._guide_set_diagnostics_enabled)
        menu.addAction("Performance timings", self._guide_show_timings)

    def _guide_show_timings(self) -> None:
        """Present bounded performance samples without path or source data."""
        values = self.timings.summary()
        detail = "\n".join(f"{name}: {count} samples, max {slow:.1f} ms"
                           for name, (count, slow) in sorted(values.items()))
        QMessageBox.information(self, "Performance timings",
                                detail or "No samples yet")

    def _guide_set_diagnostics_enabled(self, enabled):
        """Persist opt-in in-memory timings; source text and file paths are never recorded."""
        self.timings.enabled = enabled
        self.settings.setValue("performance_diagnostics", enabled)
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_timings()
```



#### Edit `main.py` — `MainWindow.render_preview`

Measure conversion without storing paths or source text.

Inside this method, find exactly:

```python
        safe_body = self._render_markdown_safely(editor.text())
```

Replace only that block with:

```python
        started = time.perf_counter()
        safe_body = self._render_markdown_safely(editor.text())
        if hasattr(self, "timings"):
            self.timings.observe("preview.convert", time.perf_counter() - started)
```



#### Edit `main.py` — `MainWindow.render_preview`

Measure asynchronous WebEngine completion separately from Markdown conversion.

Inside this method, find exactly:

```python
        self.preview.page().runJavaScript(script)
```

Replace only that block with:

```python
        web_started = time.perf_counter()
        self.preview.page().runJavaScript(script, lambda result:
            self.timings.observe("preview.webengine", time.perf_counter() - web_started)
            if hasattr(self, "timings") else None)
```



**Use this topic:** Run `python main.py` from the repository root. Enable Performance → Enable performance diagnostics, edit Markdown, then open Performance timings.


<a id="topic-23"></a>
## 23. Lazy initialization

### Topic explanation

Tests, run-profile output, terminal, and console bodies are created on first use. Terminal and console retain cheap named dock shells so layout restoration still has stable dock identities.

DeferredDock creates stable dock shells immediately and calls each widget factory only on first show. The terminal process therefore does not start just because the application launches. Optional instructions also defer the Test runner and Run configurations displays when those topics are installed; their process owners remain independent.


**Documentation:**

- [Qt dock widgets](https://doc.qt.io/archives/qt-5.15/qdockwidget.html)
- [Qt main-window restoreDockWidget](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)

### Topic code


#### Create file: `side_bar_widgets/lazy_panel.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `lazy_panel.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Construct an optional panel once when requested."""
from __future__ import annotations


class LazyWidget:
    """Build an optional panel once, on first open, then reuse it."""

    def __init__(self, factory):
        """Store the creation callback, not a half-constructed QWidget."""
        self.factory = factory
        self.value = None

    def get(self):
        """Construct once and return the same widget on later requests."""
        if self.value is None:
            # Keep the signal connections and scroll state from the first show.
            self.value = self.factory()
        return self.value
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `LazyWidget` | Build an optional panel once, on first open, then reuse it. |
| `LazyWidget.__init__` | Store the creation callback, not a half-constructed QWidget. |
| `LazyWidget.get` | Construct once and return the same widget on later requests. |


#### Create file: `side_bar_widgets/deferred_dock.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `deferred_dock.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `DeferredDock` | Keep a cheap stable dock shell so saved layouts can restore before construction. |
| `DeferredDock.__init__` | Store a factory; no child process or expensive body is created yet. |
| `DeferredDock.ensure` | Create and parent exactly one body, preserving it across later hide/show cycles. |
| `DeferredDock.showEvent` | Construct the body before Qt paints a newly visible dock. |


### Topic implementation

**Required first:** None.


#### Replace `main.py` — `MainWindow.set_up_console_dock`

Replace eager body construction with stable named dock shells. A shown dock creates its body once. Delete this method’s complete current definition, from `def set_up_console_dock(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def set_up_console_dock(self):
        """Create stable lazy Console/Terminal dock shells for layout restoration."""
        from side_bar_widgets.deferred_dock import DeferredDock
        self.console_dock = DeferredDock("Python Console", "ConsoleDock", self._make_console, self)
        self.terminal_dock = DeferredDock("Terminal", "TerminalDock", self._make_terminal, self)
        for name, dock in (("console", self.console_dock), ("terminal", self.terminal_dock)):
            self.addDockWidget(Qt.BottomDockWidgetArea, dock)
            dock.hide()
            dock.visibilityChanged.connect(lambda visible, n=name: self._set_sidebar_icon(n, visible))
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _make_console(self):
        """Connect the existing PythonRunner to one console on first visible use."""
        self.console = ConsoleWidget(self.python_runner, self)
        self.console.run_btn.clicked.connect(self.run_current_file)
        return self.console

    def _make_terminal(self):
        """Start a PTY only when the terminal is first opened, using the current folder."""
        directory = self.file_manager.current_folder or self._workspace_root
        self.terminal = TerminalWidget(parent=self, working_directory=directory)
        return self.terminal
```



#### Edit `main.py` — `MainWindow.closeEvent`

A terminal that was never opened has no process to stop.

Inside this method, find exactly:

```python
        self.terminal.stop()
```

Replace only that block with:

```python
        if self.terminal is not None:
            self.terminal.stop()
```



#### `main.py` — `MainWindow.open_folder`

The terminal call must be guarded as follows. If Topic 7 already supplied this exact guard, keep it; otherwise replace the unguarded call inside `open_folder`:

```python
        if self.terminal is not None:
            self.terminal.set_working_directory(selected, restart=True)
```



#### If Topic 16 is installed: defer the test dock

Apply the next two edits only when the Test runner topic is installed. Otherwise skip them; ordinary console/terminal laziness is already complete.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.lazy_panel import LazyWidget
```



#### Edit `main.py` — `MainWindow._install_test_runner`

Defer the test-tree widget until the first run or explicit show.

Inside this method, find exactly:

```python
        self.tests = self._guide_make_tests()
        self.tests.hide()
```

Replace only that block with:

```python
        self.tests = LazyWidget(self._guide_make_tests)
```



#### Edit `main.py` — `MainWindow._install_test_runner`

Expose the not-yet-constructed panel with a factory-backed action.

Inside this method, find exactly:

```python
        menu.addAction(self.tests.toggleViewAction())
```

Replace only that block with:

```python
        menu.addAction("Show test panel", lambda: self.tests.get().show())
```



#### Edit `main.py` — `MainWindow._guide_run_tests`

Materialize the test dock at the point of use.

Inside this method, find exactly:

```python
            dock = self.tests
```

Replace only that block with:

```python
            dock = self.tests.get()
```



#### Edit `main.py` — `MainWindow._restart_ruff`

Refresh an existing test panel without forcing construction.

Inside this method, find exactly:

```python
        self.tests.set_context(self._workspace_root, self.python_runner.interpreter)
```

Replace only that block with:

```python
        if self.tests.value is not None:
            self.tests.value.set_context(self._workspace_root, self.python_runner.interpreter)
```



#### If Topic 17 is installed: defer profile output

Apply the following edits only when Run configurations is installed.


#### Edit `main.py` — `MainWindow._install_run_profiles`

Keep process ownership eager but create its display only when requested.

Inside this method, find exactly:

```python
        self.run_output = RunOutputDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.run_output)
        self.run_output.hide()
        self.runner.output.connect(self.run_output.append)
        self.runner.finished.connect(self.run_output.completed)
        self.run_output.stop_requested.connect(self.runner.stop)
```

Replace only that block with:

```python
        self.run_output = LazyWidget(self._guide_make_run_output)
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _guide_make_run_output(self):
        """Create a distinct named-profile output dock and connect its Stop action once."""
        from python_editor.run_output import RunOutputDock
        dock = RunOutputDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.runner.output.connect(dock.append)
        self.runner.finished.connect(dock.completed)
        dock.stop_requested.connect(self.runner.stop)
        return dock
```



#### Edit `main.py` — `MainWindow._guide_run_configuration`

Open the lazy output before starting the process.

Inside this method, find exactly:

```python
            self.run_output.show()
            self.run_output.begin(result.name)
```

Replace only that block with:

```python
            self.run_output.get().show()
            self.run_output.get().begin(result.name)
```



**Use this topic:** Run `python main.py` from the repository root. Launch the editor with console/terminal hidden, then show either dock to create its body on demand.


<a id="topic-24"></a>
## 24. Background file hashing

### Topic explanation

Background hashing detects changed disk bytes without doing watcher-triggered reads on the GUI thread.

FileHashQueue hashes changed disk targets in a worker. MainWindow watches files and parents, rearms watches after atomic replacement, and attaches buffer revision/path tokens to each request. Stale or retired-view results are discarded. Hashing provides a non-destructive external-change hint; the existing save workflow still makes the final conflict decision.


**Documentation:**

- [Qt QFileSystemWatcher](https://doc.qt.io/archives/qt-5.15/qfilesystemwatcher.html)
- [Python futures](https://docs.python.org/3/library/concurrent.futures.html)

### Topic code


#### Create file: `code_inteligence/file_hash_queue.py`

**Folder:** `code_inteligence/` already exists. **File:** `file_hash_queue.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Background file hashing with identity and generation checks."""
from __future__ import annotations
from PyQt5.QtCore import QObject, pyqtSignal
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib


class FileHashQueue(QObject):
    """Hash changed files off the GUI thread and bind answers to generations."""

    changed = pyqtSignal(object, object, object)
    _done = pyqtSignal(object, object, object, object)

    def __init__(self, parent=None):
        """Use a single worker because disk reads are mostly I/O bound."""
        super().__init__(parent)
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="file-hash")
        self.pending = {}
        self.futures = set()
        self._done.connect(self._on_done)

    def check(self, path: Path, identity: object, generation: int) -> None:
        """Associate an immutable path with editor identity and edit generation."""
        path = Path(path).resolve()
        # A Save As replaces this tuple; old results are ignored on delivery.
        self.pending[identity] = (path, generation)
        def read():
            """Read exact bytes and return the digest; errors become results."""
            try:
                return hashlib.sha256(path.read_bytes()).digest()
            except OSError as error:
                return error
        future = self.pool.submit(read)
        self.futures.add(future)
        def completed(f):
            """Deliver errors and cancellations too so shutdown can drain."""
            try:
                result = f.result()
            except Exception as error:
                result = error
            self._done.emit(identity, (path, generation), result, f)
        future.add_done_callback(completed)

    def _on_done(self, identity, request, digest, future) -> None:
        """Discard a result after edit, rename, Save As or tab closure."""
        self.futures.discard(future)
        if self.pending.get(identity) == request and isinstance(digest, bytes):
            self.changed.emit(identity, request, digest)

    def forget(self, identity) -> None:
        """Invalidate all outstanding work for a retired editor."""
        self.pending.pop(identity, None)

    def shutdown(self) -> None:
        """Stop accepting pending work without blocking application close."""
        self.pending.clear()
        self.pool.shutdown(wait=False, cancel_futures=True)

    def is_running(self) -> bool:
        """Report pending jobs for MainWindow's existing asynchronous close."""
        return bool(self.futures)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `FileHashQueue` | Hash changed files off the GUI thread and bind answers to generations. |
| `FileHashQueue.__init__` | Use a single worker because disk reads are mostly I/O bound. |
| `FileHashQueue.check` | Associate an immutable path with editor identity and edit generation. |
| `FileHashQueue.check.read` | Read exact bytes and return the digest; errors become results. |
| `FileHashQueue.check.completed` | Deliver errors and cancellations too so shutdown can drain. |
| `FileHashQueue._on_done` | Discard a result after edit, rename, Save As or tab closure. |
| `FileHashQueue.forget` | Invalidate all outstanding work for a retired editor. |
| `FileHashQueue.shutdown` | Stop accepting pending work without blocking application close. |
| `FileHashQueue.is_running` | Report pending jobs for MainWindow's existing asynchronous close. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.file_hash_queue import FileHashQueue
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_file_hashing(self):
        """Own asynchronous disk hints separately from the synchronous save decision."""
        self.hashes = FileHashQueue(self)
        self.hashes.changed.connect(self._guide_hash_ready)
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self._guide_file_changed)
        self.file_watcher.directoryChanged.connect(self._guide_directory_changed)
        self._watched_editors = {}

    def _retire_hash_view(self, editor):
        """Invalidate retired-view requests and remove unneeded file/directory watches."""
        self._watched_editors.pop(id(editor), None)
        self.hashes.forget(id(editor))
        targets = {str(Path(view._save_target).resolve()) for view in self._watched_editors.values()
                   if getattr(view, "_save_target", None) is not None}
        folders = {str(Path(path).parent) for path in targets}
        stale = [path for path in self.file_watcher.files() if path not in targets]
        stale += [path for path in self.file_watcher.directories() if path not in folders]
        if stale:
            self.file_watcher.removePaths(stale)

    def _close_file_hashing(self):
        """Stop hints and keep queue ownership until running reads finish."""
        paths = self.file_watcher.files() + self.file_watcher.directories()
        if paths:
            self.file_watcher.removePaths(paths)
        self.hashes.shutdown()

    def _guide_track_file(self, editor) -> None:
        """Watch a saved target and re-add it after atomic replacement."""
        path = getattr(editor, "_save_target", None)
        if path is None:
            return
        target = str(Path(path).resolve())
        parent = str(Path(target).parent)
        if parent not in self.file_watcher.directories():
            self.file_watcher.addPath(parent)
        if Path(target).is_file() and target not in self.file_watcher.files():
            self.file_watcher.addPath(target)

    def _guide_directory_changed(self, folder: str) -> None:
        """Reattach file watches after an external atomic rename/save."""
        for editor in tuple(self._watched_editors.values()):
            target = getattr(editor, "_save_target", None)
            if target is None or str(Path(target).resolve().parent) != folder:
                continue
            filename = str(Path(target).resolve())
            if Path(filename).is_file() and filename not in self.file_watcher.files():
                self.file_watcher.addPath(filename)
                self._guide_file_changed(filename)

    def _guide_file_changed(self, filename: str) -> None:
        """Send a watcher hint to the worker without reading bytes on the GUI."""
        target = Path(filename).resolve()
        for identity, editor in tuple(self._watched_editors.items()):
            if (getattr(editor, "_save_target", None) is not None
                    and Path(editor._save_target).resolve() == target):
                self.hashes.check(target, identity, getattr(editor, "_revision", 0))
        # QSaveFile/os.replace commonly removes a file watcher registration.
        if target.is_file() and filename not in self.file_watcher.files():
            self.file_watcher.addPath(filename)

    def _guide_hash_ready(self, identity, request, digest: bytes) -> None:
        """Ignore obsolete results and show a non-destructive disk-change hint."""
        editor = self._watched_editors.get(identity)
        if editor is None:
            return
        path, generation = request
        if (getattr(editor, "_revision", 0) != generation
                or getattr(editor, "_save_target", None) is None
                or Path(editor._save_target).resolve() != path):
            return
        if digest != getattr(editor, "_disk_digest", None):
            editor._external_changed = True
            if editor is self.current_editor():
                self.statusBar().showMessage("File changed on disk; compare before saving", 6000)
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_file_hashing()
```



#### Insert at the start of `main.py` — `MainWindow._connect_editor`

Track a saved document’s target when its signals are attached. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        self._watched_editors[id(editor)] = editor
        self._guide_track_file(editor)
```



#### Edit `main.py` — `MainWindow._on_editor_text_changed`

Discard a completed hash if the buffer changed while it was calculated.

Inside this method, find exactly:

```python
        self._dirty_editors.add(editor)
```

Replace only that block with:

```python
        self._dirty_editors.add(editor)
        editor._revision = getattr(editor, "_revision", 0) + 1
```



#### Insert at the start of `main.py` — `MainWindow._dispose_editor`

Forget closed-view requests before widget retirement. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        self._retire_hash_view(editor)
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

Rearm a watch removed by atomic save.

Inside this method, find exactly:

```python
        self.mark_editor_clean(editor)
```

Replace only that block with:

```python
        self.mark_editor_clean(editor)
        editor._external_changed = False
        self._guide_track_file(editor)
```



#### Edit `main.py` — `MainWindow.on_file_rename`

Start monitoring the renamed target.

Inside this method, find exactly:

```python
            editor.full_path = updated_path.absolute()
```

Replace only that block with:

```python
            editor.full_path = updated_path.absolute()
            editor._save_target = save_target(updated_path)
            self._guide_track_file(editor)
```



#### Insert at the start of `main.py` — `MainWindow._background_work_running`

Retain queue ownership until callbacks drain. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if self.hashes.is_running():
            return True
```



#### Edit `main.py` — `MainWindow.closeEvent`

Stop filesystem hints after close decisions. If Topic 23 is absent, insert `_close_file_hashing()` immediately before the original unguarded `self.terminal.stop()` instead.

Inside this method, find exactly:

```python
        if self.terminal is not None:
            self.terminal.stop()
```

Replace only that block with:

```python
        self._close_file_hashing()
        if self.terminal is not None:
            self.terminal.stop()
```



**Use this topic:** Run `python main.py` from the repository root. Modify an open saved file externally; the editor reports the change after the background hash completes.


<a id="topic-25"></a>
## 25. Incremental syntax highlighting

### Topic explanation

Incremental syntax-state scanning is enabled in the production Python lexer and the native Cython scanner. Sparse checkpoints retain every scanner-local value needed to resume; edits invalidate affected prefixes before reuse.

LexerCheckpoints retains complete scanner snapshots at safe line boundaries and invalidates from before an edit. Both Python and Cython scanners accept the same snapshot tuple. The native STATE_API guard falls back to Python when an old binary is installed. Apply the Python and native source changes together.


**Documentation:**

- [QScintilla introduction](https://www.riverbankcomputing.com/software/qscintilla/intro)
- [Scintilla lexing](https://www.scintilla.org/ScintillaDoc.html)
- [Cython compilation](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html)
- [QScintilla custom lexer](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciLexerCustom.html)

### Topic code


#### Create file: `python_editor/lexer_checkpoints.py`

**Folder:** `python_editor/` already exists. **File:** `lexer_checkpoints.py`. Create the file and paste the complete contents starting at line 1.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `LexerCheckpoints` | Cache scanner locals only at safe line boundaries, bounded per document. |
| `LexerCheckpoints.__init__` | Enable production reuse; optionally compare every lookup to a full scan. |
| `LexerCheckpoints.invalidate` | Discard states at/after the changed line and three-byte lookahead. |
| `LexerCheckpoints.state_before` | Resume the actual scanner from complete locals and return packed style bits. |


#### Replace file: `python_editor/setup.py`

**Folder:** `python_editor/` already exists. **File:** `setup.py`. Replace the complete file contents starting at line 1. Keep the same filename.

```python
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
```


### Topic implementation

**Required first:** None.


#### Imports in `python_editor/custompythonlexer.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from python_editor.lexer_checkpoints import LexerCheckpoints
```



#### Native imports in `python_editor/custompythonlexer.py`

Replace the first native-import `try/except`, before `_resource_path`, with:

```python
try:
    from python_editor.lexer_fast import style_chunk as _cython_style
    from python_editor.lexer_fast import compute_state_before as _cython_state
    from python_editor.lexer_fast import STATE_API
    _HAS_CYTHON = STATE_API == 2
except ImportError:
    _HAS_CYTHON = False
```

The version guard keeps an old installed binary from receiving the new snapshot API.


#### Replace `_py_compute_state` in `python_editor/custompythonlexer.py`

Replace the entire module-level function immediately before `_py_style_chunk`. Keep `_py_style_chunk` and all style definitions.

```python
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
```



#### Replace `python_editor/custompythonlexer.py` — `PyCustomLexer.styleText`

Resume scanning from a valid checkpoint and keep the native/fallback state formats identical. Delete this method’s complete current definition, from `def styleText(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
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
        features = getattr(self.editor.window(), "features", None)
        if features is not None:
            features.timings.observe("python-lexing", perf_counter() - began)
```



#### `python_editor/lexer_fast.pyx`

Replace `compute_state_before`, after `_skip_string` and before `def style_chunk`. Include `STATE_API = 2` immediately above it. Keep `style_chunk` and the other helpers unchanged.

```cython
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
```

From the repository root, rebuild with:

```bash
python python_editor/setup.py build_ext --inplace
```

A C compiler and Cython are needed only for the native build. The updated Python fallback runs when the native extension is unavailable. Do not delete other lexer files.


**Use this topic:** Run `python main.py` from the repository root. Edit Python around multiline strings, f-strings and block boundaries; the lexer reuses valid earlier scanner state.


<a id="topic-26"></a>
## 26. Smarter Markdown preview updates

### Topic explanation

Markdown preview edits are debounced and hashed for the active document. Hidden previews and large files skip optional conversion; showing preview explicitly renders current content. Repeated JavaScript updates use a local function scope.

PreviewSchedule coalesces requests for the active Markdown editor and skips repeated identity/content digests. Hidden previews do no conversion. MainWindow updates only the sanitized HTML body and preserves scroll; showing preview again forces one current render. Retiring an editor cancels the stored widget reference.


**Documentation:**

- [Qt QTimer](https://doc.qt.io/archives/qt-5.15/qtimer.html)
- [Python hashlib](https://docs.python.org/3/library/hashlib.html)
- [Bleach sanitizer](https://bleach.readthedocs.io/en/latest/clean.html)

### Topic code


#### Create file: `markdown_editor/preview_scheduler.py`

**Folder:** `markdown_editor/` already exists. **File:** `preview_scheduler.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Coalesce Markdown preview changes for the active document."""
from __future__ import annotations
from PyQt5.QtCore import QObject, QTimer
import hashlib


class PreviewSchedule(QObject):
    """Coalesce Markdown edits and avoid needless full-page refreshes."""

    def __init__(self, render, parent=None):
        """Hold only the latest selected editor and its digest."""
        super().__init__(parent)
        self.render = render
        self.last = None
        self.editor = None
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(180)
        self.timer.timeout.connect(self.flush)

    def changed(self, editor) -> None:
        """Restart the debounce timer for the currently visible Markdown tab."""
        self.editor = editor
        self.timer.start()

    def flush(self) -> None:
        """Render only if the visible editor's source actually changed."""
        editor = self.editor
        if editor is None or editor is not self.parent().current_editor():
            return
        preview = getattr(self.parent(), "preview", None)
        if preview is not None and not preview.isVisible():
            return
        # The digest includes the document body; the cache key also includes
        # editor identity so equal text in two tabs does not confuse ownership.
        digest = hashlib.sha256(editor.text().encode("utf-8")).digest()
        key = (id(editor), digest)
        if self.last != key:
            self.render()
            self.last = key
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `PreviewSchedule` | Coalesce Markdown edits and avoid needless full-page refreshes. |
| `PreviewSchedule.__init__` | Hold only the latest selected editor and its digest. |
| `PreviewSchedule.changed` | Restart the debounce timer for the currently visible Markdown tab. |
| `PreviewSchedule.flush` | Render only if the visible editor's source actually changed. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from markdown_editor.preview_scheduler import PreviewSchedule
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _queue_preview(self):
        """Schedule the active Markdown document without retaining another tab's source."""
        editor = self.current_editor()
        if isinstance(editor, MarkdownEditor):
            self.preview_schedule.changed(editor)

    def _retire_preview(self, editor):
        """Drop a pending editor reference before its widget is destroyed."""
        if self.preview_schedule.editor is editor:
            self.preview_schedule.timer.stop()
            self.preview_schedule.editor = None
```



#### Edit `main.py` — `MainWindow.init_ui`

Create the preview scheduler before the existing text debounce connects.

Inside this method, find exactly:

```python
        self._debounce = QTimer(self)
```

Replace only that block with:

```python
        self.preview_schedule = PreviewSchedule(self.render_preview, self)
        self._debounce = QTimer(self)
```



#### Edit `main.py` — `MainWindow.init_ui`

Route the existing debounce through identity/digest checking.

Inside this method, find exactly:

```python
        self._debounce.timeout.connect(self.render_preview)
```

Replace only that block with:

```python
        self._debounce.timeout.connect(self._queue_preview)
```



#### Edit `main.py` — `MainWindow.render_preview`

Skip hidden preview conversion while preserving the sanitizer.

Inside this method, find exactly:

```python
        safe_body = self._render_markdown_safely(editor.text())
```

Replace only that block with:

```python
        if not self.preview.isVisible():
            return
        safe_body = self._render_markdown_safely(editor.text())
```



#### Edit `main.py` — `MainWindow.render_preview`

Replace only the body and restore scroll instead of navigating WebEngine.

Inside this method, find exactly:

```python
        script = f'document.getElementById("content").innerHTML = {payload};'
```

Replace only that block with:

```python
        script = (
            "(() => { const previous = window.scrollY;"
            f'document.getElementById("content").innerHTML = {payload};'
            "window.scrollTo(0, previous); })();"
        )
```



#### Edit `main.py` — `MainWindow.toggle_preview`

A newly shown preview must render the latest text once.

Inside this method, find exactly:

```python
            self.hs_split.setSizes([250, 575, 575])
```

Replace only that block with:

```python
            self.hs_split.setSizes([250, 575, 575])
            self.preview_schedule.last = None
            self._queue_preview()
```



#### Insert at the start of `main.py` — `MainWindow._dispose_editor`

Cancel the pending view reference before destruction. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        self._retire_preview(editor)
```



#### Edit `main.py` — `MainWindow.closeEvent`

Stop preview scheduling before the existing terminal shutdown. Without Topic 23, insert the stop call immediately before the original `self.terminal.stop()` instead.

Inside this method, find exactly:

```python
        if self.terminal is not None:
            self.terminal.stop()
```

Replace only that block with:

```python
        self.preview_schedule.timer.stop()
        if self.terminal is not None:
            self.terminal.stop()
```



**Use this topic:** Run `python main.py` from the repository root. Edit Markdown, switch tabs, hide/show preview and scroll it; updates apply to the latest active document.


<a id="topic-27"></a>
## 27. Large-file mode

### Topic explanation

Large-file mode measures current UTF-8 byte length, including growth during editing. It pauses optional analysis/presentation work above two million bytes while editing and saving remain available; a per-tab override explicitly re-enables optional features.

The size policy uses Scintilla’s byte count to avoid copying an oversized buffer merely to decide whether to update it. Optional outline, preview and automatic semantic work can pause, with an explicit per-view override. Save, dirty tracking and recovery are not stopped.


**Documentation:**

- [QScintilla introduction](https://www.riverbankcomputing.com/software/qscintilla/intro)
- [Python bytes](https://docs.python.org/3/library/stdtypes.html#bytes)

### Topic code


#### Create file: `code_settings/large_file_policy.py`

**Folder:** `code_settings/` already exists. **File:** `large_file_policy.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Decide whether optional presentation work fits the document budget."""
from __future__ import annotations


def file_size_mode(size: int, *, threshold: int = 2_000_000) -> bool:
    """Decide whether optional preview, minimap and analysis should pause."""
    # Saving, dirty tracking and recovery are outside this optional budget.
    return size >= threshold


def should_update_panel(panel, editor, *, threshold: int = 2_000_000) -> bool:
    """Skip hidden and large-document presentation work, not state changes."""
    # A hidden panel can rebuild once on show; document state still changes.
    if not panel.isVisible():
        return False
    if getattr(editor, "_large_file_override", False):
        return True
    if getattr(editor, "_large_file_mode", False):
        return False
    # Scintilla already knows the buffer length. Avoid making a full Python
    # copy of the document on every optional panel repaint.
    return not file_size_mode(editor.length(), threshold=threshold)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `file_size_mode` | Decide whether optional preview, minimap and analysis should pause. |
| `should_update_panel` | Skip hidden and large-document presentation work, not state changes. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_settings.large_file_policy import file_size_mode
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_large_file_mode(self):
        """Expose a per-view override without changing save, close or recovery behavior."""
        menu = self.menuBar().addMenu("Large files")
        menu.addAction("Toggle optional work for current tab", self._toggle_large_file_work)

    def _optional_work_allowed(self, editor):
        """Allow optional work below the byte budget or after explicit per-view override."""
        return editor is not None and (not file_size_mode(editor.length())
                                      or getattr(editor, "_large_file_override", False))

    def _toggle_large_file_work(self):
        """Toggle expensive presentation/analysis only for the active oversized view."""
        editor = self.current_editor()
        if editor is None or not file_size_mode(editor.length()):
            return
        editor._large_file_override = not getattr(editor, "_large_file_override", False)
        self._update_outline()
        self.render_preview()
        self.statusBar().showMessage("Optional work enabled" if editor._large_file_override
                                     else "Optional work paused", 3000)
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_large_file_mode()
```



#### Edit `main.py` — `MainWindow.render_preview`

Gate expensive presentation using Scintilla’s byte count, without copying the buffer.

Inside this method, find exactly:

```python
        editor = self.current_editor()
```

Replace only that block with:

```python
        editor = self.current_editor()
        if not self._optional_work_allowed(editor):
            return
```



#### Edit `main.py` — `MainWindow._update_outline`

Gate expensive presentation using Scintilla’s byte count, without copying the buffer.

Inside this method, find exactly:

```python
        editor = self.current_editor()
```

Replace only that block with:

```python
        editor = self.current_editor()
        if not self._optional_work_allowed(editor):
            return
```



#### Insert at the start of `python_editor/pythoneditor.py` — `PythonEditor._trigger_autocomplete`

Pause optional semantic work on oversized buffers. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if self.length() >= 2_000_000 and not getattr(self, "_large_file_override", False):
            return
```



#### Insert at the start of `python_editor/pythoneditor.py` — `PythonEditor._trigger_signature_help`

Pause optional semantic work on oversized buffers. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if self.length() >= 2_000_000 and not getattr(self, "_large_file_override", False):
            return
```



#### Insert at the start of `python_editor/pythoneditor.py` — `PythonEditor.goto_definition`

Pause optional semantic work on oversized buffers. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if self.length() >= 2_000_000 and not getattr(self, "_large_file_override", False):
            return
```



#### If Topic 26 is installed

In `markdown_editor/preview_scheduler.py`, inside `PreviewSchedule.flush`, insert the following immediately before `digest = hashlib.sha256(...)` so hashing a paused large preview is skipped too:

```python
        if editor.length() >= 2_000_000 and not getattr(editor, "_large_file_override", False):
            return
```



**Use this topic:** Run `python main.py` from the repository root. Open a document of at least 2,000,000 bytes; use Large files → Toggle optional work for current tab to enable optional work explicitly.


<a id="topic-28"></a>
## 28. Shared analysis scheduling

### Topic explanation

One application-owned worker serializes Jedi completion, signatures, documentation, definitions, references, rename, and workspace scans. Request lanes are separated by document and kind; closing a tab invalidates its deliveries while the queue retains running-worker ownership.

AnalysisQueue serializes immutable jobs and keeps worker ownership at QApplication scope. Generation/serial checks reject stale replies; per-editor AnalysisProvider adapters preserve the existing public signals. The initial scheduler in this topic is deliberately uncached; Topic 29 adds bounded reuse afterward. RequestKey lives in analysis_cache.py as a data-only identity until then.


**Documentation:**

- [Python futures](https://docs.python.org/3/library/concurrent.futures.html)
- [Jedi API](https://jedi.readthedocs.io/en/latest/docs/api.html)
- [Qt connection types](https://doc.qt.io/archives/qt-5.15/qt.html#ConnectionType-enum)

### Topic code


#### Create file: `code_inteligence/analysis_cache.py`

**Folder:** `code_inteligence/` already exists. **File:** `analysis_cache.py`. Create the file and paste the complete contents starting at line 1. At this stage it contains only RequestKey; caching is introduced by Topic 29.

```python
"""Immutable identities for scheduled analysis requests."""
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `RequestKey` | Identity required to reject analysis produced for obsolete content. |


#### Create file: `code_inteligence/analysis_scheduler.py`

**Folder:** `code_inteligence/` already exists. **File:** `analysis_scheduler.py`. Create the file and paste the complete contents starting at line 1.

```python
"""One application-owned worker queue for all Jedi providers and workspace scans."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, Future
from time import perf_counter
from PyQt5.QtCore import QCoreApplication, QObject, Qt, pyqtSignal
from code_inteligence.analysis_cache import RequestKey


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
        """Replace pending work in one lane and submit an immutable request."""
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `AnalysisQueue` | Serialize immutable jobs; publish current results on the GUI thread. |
| `AnalysisQueue.__init__` | Create one worker because Jedi's fast parser is not thread-safe. |
| `AnalysisQueue.submit` | Replace pending work in one lane and submit an immutable request. |
| `AnalysisQueue._receive` | Drain futures and reject stale serials even when keys are identical. |
| `AnalysisQueue.cancel` | Invalidate one provider or all providers belonging to a document. |
| `AnalysisQueue.invalidate_all` | Reject old environment results on workspace or interpreter changes. |
| `AnalysisQueue.shutdown` | Stop submissions without blocking the GUI on running Python work. |
| `AnalysisQueue.is_running` | Keep application ownership until queued deliveries have drained. |
| `shared_analysis` | Return the single analysis queue owned by the current QApplication. |


#### Create file: `code_inteligence/analysis_provider.py`

**Folder:** `code_inteligence/` already exists. **File:** `analysis_provider.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Immutable Jedi requests and adapters preserving existing editor signals."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import sys
import uuid
from PyQt5.QtCore import QObject, pyqtSignal
from code_inteligence.analysis_cache import RequestKey
from code_inteligence.analysis_scheduler import shared_analysis


def evaluate(key: RequestKey, source: str):
    """Run in the worker, returning plain data without live Jedi or Qt objects.

    Script, Name and Signature objects remain inside this function. The selected
    interpreter and workspace determine imports and reference-search scope.
    """
    import jedi
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
        if self.editor is not None and self.editor.length() > 2_000_000:
            if not getattr(self.editor, "_large_file_override", False):
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
```


**Code explanation:**

| Class, function or method | Responsibility |
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


#### Replace file: `code_inteligence/autocompleter.py`

**Folder:** `code_inteligence/` already exists. **File:** `autocompleter.py`. Replace the complete file contents starting at line 1. Keep the same filename.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `AutoCompleter` | Deliver plain completion names to the editor's existing QsciAPIs list. |
| `AutoCompleter.__init__` | Keep the legacy constructor arguments while accepting the owning tab. |
| `AutoCompleter.get_completions` | Submit a captured buffer and return its UI generation. |
| `AutoCompleter.deliver` | Convert immutable worker results to the existing list signal. |


#### Replace file: `code_inteligence/signature_helper.py`

**Folder:** `code_inteligence/` already exists. **File:** `signature_helper.py`. Replace the complete file contents starting at line 1. Keep the same filename.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `SignatureHelper` | Publish signature text from the shared queue. |
| `SignatureHelper.__init__` | Bind the provider to the tab supplying environment and size policy. |
| `SignatureHelper.get_signatures` | Submit a call-site snapshot using Jedi's one-based line numbers. |
| `SignatureHelper.deliver` | Publish a signature or request dismissal of an obsolete tooltip. |


#### Replace file: `code_inteligence/hover_helper.py`

**Folder:** `code_inteligence/` already exists. **File:** `hover_helper.py`. Replace the complete file contents starting at line 1. Keep the same filename.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `HoverHelper` | Provide explicitly requested documentation through shared analysis. |
| `HoverHelper.__init__` | Capture the owning tab without exposing it to the worker. |
| `HoverHelper.get_hover` | Submit the identifier selected by the documentation action. |
| `HoverHelper.deliver` | Pass escaped-by-the-popup text, never live Jedi objects, to the UI. |


#### Replace file: `code_inteligence/definition_finder.py`

**Folder:** `code_inteligence/` already exists. **File:** `definition_finder.py`. Replace the complete file contents starting at line 1. Keep the same filename.

```python
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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `DefinitionFinder` | Resolve definitions without a separate QThread or concurrent Jedi call. |
| `DefinitionFinder.__init__` | Use the same queue and environment as completion and documentation. |
| `DefinitionFinder.find` | Submit a definition request for an immutable source snapshot. |
| `DefinitionFinder.deliver` | Preserve one-based result lines expected by PythonEditor. |


#### Replace file: `code_inteligence/references_finder.py`

**Folder:** `code_inteligence/` already exists. **File:** `references_finder.py`. Replace the complete file contents starting at line 1. Keep the same filename.

```python
"""Shared-queue adapter for references finder."""
from PyQt5.QtCore import pyqtSignal
from code_inteligence.analysis_provider import AnalysisProvider


class ReferencesFinder(AnalysisProvider):
    """Find project references using the same serialized Jedi queue."""
    references_found = pyqtSignal(int, list)
    references_empty = pyqtSignal(int)
    error = pyqtSignal(int, str)

    def __init__(self, editor=None):
        """Bind navigation results to the source tab's lifetime."""
        super().__init__("references", editor)

    def find_references(self, line, column, code, file_path=None):
        """Search references for a captured source position and project."""
        return self.request(line, column, code, file_path)

    def deliver(self, generation, value):
        """Emit zero-based locations for the new references dock."""
        if isinstance(value, Exception):
            self.error.emit(generation, str(value))
        elif not value:
            self.references_empty.emit(generation)
        else:
            self.references_found.emit(generation, list(value))
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `ReferencesFinder` | Find project references using the same serialized Jedi queue. |
| `ReferencesFinder.__init__` | Bind navigation results to the source tab's lifetime. |
| `ReferencesFinder.find_references` | Search references for a captured source position and project. |
| `ReferencesFinder.deliver` | Emit zero-based locations for the new references dock. |


### Topic implementation

**Required first:** None.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.analysis_scheduler import shared_analysis
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_analysis_queue(self):
        """Keep one queue alive until all editor and workspace jobs have drained."""
        self.analysis = shared_analysis()
        if hasattr(self, "timings"):
            self.analysis.measured.connect(self.timings.observe)
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_analysis_queue()
```



#### Insert at the start of `main.py` — `MainWindow._background_work_running`

Retain application-level jobs even after editor providers detach. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if self.analysis.is_running():
            return True
```



#### Edit `main.py` — `MainWindow.closeEvent`

Stop queue submissions after accepted close prompts. Without Topic 23, insert `self.analysis.shutdown()` before the original terminal stop line instead.

Inside this method, find exactly:

```python
        if self.terminal is not None:
            self.terminal.stop()
```

Replace only that block with:

```python
        self.analysis.shutdown()
        if self.terminal is not None:
            self.terminal.stop()
```



#### Add at the end of `main.py` — `MainWindow._restart_ruff`

Reject results computed for the old workspace or interpreter. Add the following at method-body indentation after the existing body, immediately before the next method definition at class indentation. Keep earlier additions in this method.

```python
        self.analysis.invalidate_all()
        for view in self.tab_view.all_editors():
            if isinstance(view, PythonEditor):
                for provider in view._analysis_workers():
                    provider.invalidate()
```



#### Imports in `python_editor/pythoneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.references_finder import ReferencesFinder
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Parent the provider to its editor so requests capture live context.

Inside this method, find exactly:

```python
SignatureHelper()
```

Replace only that block with:

```python
SignatureHelper(self)
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Parent the provider to its editor so requests capture live context.

Inside this method, find exactly:

```python
HoverHelper()
```

Replace only that block with:

```python
HoverHelper(self)
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Parent the provider to its editor so requests capture live context.

Inside this method, find exactly:

```python
DefinitionFinder()
```

Replace only that block with:

```python
DefinitionFinder(self)
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Give completion requests the owning editor identity.

Inside this method, find exactly:

```python
str(self.full_path) if self.full_path else None, self._api
```

Replace only that block with:

```python
str(self.full_path) if self.full_path else None, self._api, self
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Create the references provider and invalidate all providers on edits.

Inside this method, find exactly:

```python
        self.definition_finder = DefinitionFinder(self)
```

Replace only that block with:

```python
        self.references_finder = ReferencesFinder(self)
        self.definition_finder = DefinitionFinder(self)
        self.textChanged.connect(self._invalidate_analysis)
```



#### Replace `python_editor/pythoneditor.py` — `PythonEditor._cursorPositionChanged`

Track all providers in the existing generation and retirement lifecycle. Delete this method’s complete current definition, from `def _cursorPositionChanged(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _cursorPositionChanged(self, line: int, index: int) -> None:
        """Called when the cursor moves. Starts a debounce timer instead
        of immediately running Jedi analysis."""
        if not self.is_python_file or self._loading_text or self._shutting_down:
            return
        # Store the position and restart the timer
        # will fire 300ms after the LAST cursor movement
        # If the user keeps moving the cursor, the timer keeps resetting
        self._pending_line = line
        self._pending_index = index
        for helper_name in ("auto_completer", "signature_helper", "definition_finder", "references_finder"):
            helper = getattr(self, helper_name, None)
            if helper is not None:
                helper.invalidate()
        self._autocomplete_timer.start()
```



#### Replace `python_editor/pythoneditor.py` — `PythonEditor._analysis_workers`

Track all providers in the existing generation and retirement lifecycle. Delete this method’s complete current definition, from `def _analysis_workers(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _analysis_workers(self):
        """Return every per-editor QThread that must outlive the tab."""
        names = (
            "auto_completer",
            "definition_finder",
            "hover_helper",
            "signature_helper",
            "references_finder",
        )
        return [getattr(self, name) for name in names if hasattr(self, name)]
```



#### Add methods to `python_editor/pythoneditor.py` — `PythonEditor`

Add the common edit-invalidation slot. Insert the following **after the complete `PythonEditor.closeEvent` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _invalidate_analysis(self):
        """Invalidate every provider after edits, including stationary-caret changes."""
        for provider in self._analysis_workers():
            provider.invalidate()
        if self.length() > 2_000_000 and not getattr(self, "_large_file_override", False):
            self._autocomplete_timer.stop()
            if hasattr(self, "_api"):
                self._api.clear()
```



**Use this topic:** Run `python main.py` from the repository root. Use existing completion, documentation, signatures and Go to Definition in Python; their requests now share one background queue.


<a id="topic-14"></a>
## 14. Rename symbol with preview

### Topic explanation

Python rename runs Jedi in the shared analysis queue, previews every affected file, and applies only an explicitly accepted, still-current plan. Identifier validation rejects keywords; writes preserve source encoding, BOM, line endings, and permission mode.

The shared queue runs Jedi rename planning off the GUI thread. FileEdit stores exact before/after bytes. The GUI checks workspace/interpreter and dirty buffers, displays the complete plan, then rechecks disk bytes before applying. Open affected buffers reload only after the approved write. Existing local history is used when Topic 11 is also installed.


**Documentation:**

- [Jedi rename API](https://jedi.readthedocs.io/en/latest/docs/api.html)
- [Jedi refactoring objects](https://jedi.readthedocs.io/en/latest/docs/api-classes.html)
- [Python encoding detection](https://docs.python.org/3/library/tokenize.html#tokenize.detect_encoding)

### Topic code


#### Create file: `code_inteligence/symbol_rename.py`

**Folder:** `code_inteligence/` already exists. **File:** `symbol_rename.py`. Create the file and paste the complete contents starting at line 1.

```python
"""Preview and revision-checked application of Jedi rename edits."""
from __future__ import annotations
from code_inteligence.document_recovery import atomic_bytes
from code_inteligence.text_comparison import unified_diff
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileEdit:
    """A proposed rename for a file at an exact on-disk revision."""

    path: Path
    before: bytes
    after: bytes


def plan_rename(root: Path, path: Path, source: str, line: int,
                column: int, name: str, interpreter: str | None = None) -> list[FileEdit]:
    """Ask Jedi for edits and reject file moves and outside-workspace writes."""
    import jedi
    import keyword
    import io
    import tokenize
    if not name.isidentifier() or keyword.iskeyword(name):
        raise ValueError("New name must be a Python identifier")
    root, path = root.resolve(), path.resolve()
    if not path.is_relative_to(root):
        raise ValueError("Source must be inside the workspace")
    # Jedi uses one-based lines; QScintilla supplied the zero-based line.
    refactor = jedi.Script(code=source, path=path,
                           project=jedi.Project(path=str(root)),
                           environment=jedi.create_environment(interpreter, safe=False) if interpreter else None).rename(
                               line=line + 1, column=column, new_name=name)
    if list(refactor.get_renames()):
        raise ValueError("Module/file renames need a separate file-move workflow")
    edits = []
    for changed_path, changed in refactor.get_changed_files().items():
        original_path = Path(changed_path)
        target = original_path.resolve()
        if not target.is_relative_to(root) or original_path.is_symlink():
            raise ValueError("Rename would write outside workspace or through a link")
        # Capture the exact original bytes so Apply can reject a stale preview.
        before = target.read_bytes()
        # Save all open buffers before planning: Jedi sees source for the active
        # tab and disk for other files; mixing revisions would make a bad plan.
        encoding, _ = tokenize.detect_encoding(io.BytesIO(before).readline)
        original = before.decode(encoding)
        if target == path and original.replace("\r\n", "\n").replace("\r", "\n") != source.replace("\r\n", "\n").replace("\r", "\n"):
            raise ValueError("Save the active file before planning a rename")
        result = changed.get_new_code().replace("\r\n", "\n").replace("\r", "\n")
        eol = "\r\n" if "\r\n" in original else "\r" if "\r" in original else "\n"
        edits.append(FileEdit(target, before, result.replace("\n", eol).encode(encoding)))
    return edits


def rename_preview(edits: list[FileEdit]) -> str:
    """Join file-scoped diffs for confirmation before any writes."""
    return "\n".join(unified_diff(edit.before.decode("utf-8-sig", errors="replace"),
                                  edit.after.decode("utf-8-sig", errors="replace"), str(edit.path),
                                  str(edit.path)) for edit in edits)


def apply_rename(edits: list[FileEdit]) -> None:
    """Check every original revision before applying the approved edit set."""
    # Validate all files first; otherwise a changed last file could leave
    # earlier files renamed while the operation is rejected.
    if any(edit.path.read_bytes() != edit.before for edit in edits):
        raise RuntimeError("A target changed after the rename preview")
    written = []
    try:
        for edit in edits:
            atomic_bytes(edit.path, edit.after)
            written.append(edit)
    except OSError:
        for edit in reversed(written):
            atomic_bytes(edit.path, edit.before)
        raise
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `FileEdit` | A proposed rename for a file at an exact on-disk revision. |
| `plan_rename` | Ask Jedi for edits and reject file moves and outside-workspace writes. |
| `rename_preview` | Join file-scoped diffs for confirmation before any writes. |
| `apply_rename` | Check every original revision before applying the approved edit set. |


### Topic implementation

**Required first:** Topic 10, Topic 12, Topic 13, Topic 28.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
import time
from code_inteligence.analysis_cache import RequestKey
from code_inteligence.symbol_rename import apply_rename, plan_rename, rename_preview
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _guide_rename_symbol(self):
        """Submit semantic rename planning off-thread and review its exact result later."""
        editor = self.current_editor()
        if not isinstance(editor, PythonEditor) or not editor.path:
            return
        if self._dirty_editors:
            QMessageBox.warning(self, "Rename", "Save all modified tabs first")
            return
        name, accepted = QInputDialog.getText(self, "Rename symbol", "New name")
        if not accepted:
            return
        line, column = editor.getCursorPosition()
        root, path, source = self._workspace_root, Path(editor.path), editor.text()
        interpreter = self.python_runner.interpreter
        key = RequestKey(str(path), time.monotonic_ns(), interpreter, str(root), "rename")
        self.analysis.submit(key, lambda: plan_rename(root, path, source, line, column, name, interpreter))

    def _guide_rename_ready(self, key, edits):
        """Review a current rename plan and revalidate every affected file on Apply."""
        if key.workspace != str(self._workspace_root) or key.interpreter != self.python_runner.interpreter:
            return
        if isinstance(edits, Exception):
            QMessageBox.warning(self, "Rename", str(edits))
            return
        if self._dirty_editors:
            QMessageBox.warning(self, "Rename", "A buffer changed while the plan was calculated; save and retry")
            return
        if not edits or not self._guide_compare("", rename_preview(edits), "Review rename"):
            return
        try:
            if self._dirty_editors:
                raise RuntimeError("An open buffer changed during review; save and retry")
            apply_rename(edits)
            if hasattr(self, "history"):
                for edit in edits:
                    try:
                        self.history.record(edit.path, edit.before)
                    except OSError as error:
                        self.statusBar().showMessage(f"History copy failed: {error}", 6000)
            affected = {edit.path for edit in edits}
            for view in self.tab_view.all_editors():
                if getattr(view, "path", None) and Path(view.path).resolve() in affected:
                    raw = Path(view.path).read_bytes()
                    view.setTextSafely(raw.decode("utf-8-sig"))
                    view._disk_text = raw.decode("utf-8-sig")
                    view._utf8_bom = raw.startswith(UTF8_BOM)
                    view._disk_digest = hashlib.sha256(raw).digest()
                    if isinstance(view, PythonEditor) and view.ruff_lsp is not None:
                        view.ruff_lsp.sync_from_editor()
                    self.mark_editor_clean(view)
            self.analysis.invalidate_all()
        except (OSError, UnicodeError, ValueError, RuntimeError) as error:
            QMessageBox.warning(self, "Rename", str(error))

    def _install_rename(self):
        """Connect rename replies without taking ownership of the shared queue."""
        self.analysis = shared_analysis()
        self.analysis.ready.connect(self._receive_rename)
        menu = self.menuBar().addMenu("Rename")
        menu.addAction("Rename symbol with preview", self._guide_rename_symbol)

    def _receive_rename(self, key, result):
        """Dispatch only rename jobs to the rename review workflow."""
        if key.kind == "rename":
            self._guide_rename_ready(key, result)
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_rename()
```



**Use this topic:** Run `python main.py` from the repository root. Save modified tabs, place the caret on a Python symbol and choose Rename → Rename symbol with preview. Review the proposed files before applying.


<a id="topic-15"></a>
## 15. Workspace symbol search

### Topic explanation

Workspace search scans Python definitions under the actual workspace root, skips excluded directories, tolerates invalid files, and navigates to a selected definition.

The pure AST index scans the workspace with its stated file and size bounds. MainWindow submits a fresh background request, rejects obsolete workspace/interpreter results, filters by name and opens the selected zero-based source position. Breadcrumb UI is not required.


**Documentation:**

- [Python AST](https://docs.python.org/3/library/ast.html)
- [Python os.walk](https://docs.python.org/3/library/os.html#os.walk)

### Topic code


#### Shared file: `code_inteligence/symbol_index.py`

**Folder:** `code_inteligence/` already exists. **File:** `symbol_index.py`. If an earlier topic already created this exact file, keep it. Otherwise create it with the complete contents below.

```python
"""Python source symbols and bounded workspace indexing."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import ast
import os


@dataclass(frozen=True)
class Symbol:
    """A workspace symbol with a zero-based QScintilla destination."""

    path: Path
    name: str
    kind: str
    line: int
    column: int
    parent: str = ""
    end_line: int = 0


def python_symbols(path: Path, source: str) -> list[Symbol]:
    """Parse definitions without executing user code; reject incomplete syntax."""
    # Parsing is safe for an untrusted project: ast.parse builds a syntax tree
    # and does not import a module or execute any of its top-level statements.
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    result = []

    def visit(body, parent=""):
        """Walk immediate members so a method retains its class breadcrumb."""
        for node in body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                # AST lines are 1-based; the editor's line API is 0-based.
                result.append(Symbol(path, node.name, kind, node.lineno - 1,
                                     node.col_offset, parent,
                                     getattr(node, "end_lineno", node.lineno) - 1))
                visit(node.body, f"{parent}.{node.name}".strip("."))
    visit(tree.body)
    return result


def symbol_at(symbols: list[Symbol], line: int) -> list[Symbol]:
    """Return the enclosing symbol chain for a zero-based source line."""
    # AST end_lineno prevents a method breadcrumb leaking into the next class.
    eligible = [item for item in symbols if item.line <= line <= item.end_line]
    return sorted(eligible, key=lambda item: (item.line, -item.end_line))


def workspace_symbols(root: Path, *, limit: int = 2000) -> list[Symbol]:
    """Build a bounded index, skipping virtualenvs and unreadable files."""
    result = []
    skip = {".git", ".venv", "venv", "__pycache__", "build", "dist"}
    for folder, dirs, files in os.walk(root):
        # Mutating dirs in-place tells os.walk not to descend into these trees.
        dirs[:] = [name for name in dirs if name not in skip]
        for name in files:
            if not name.endswith((".py", ".pyi")):
                continue
            path = Path(folder) / name
            try:
                if path.is_symlink():
                    continue
                if path.stat().st_size > 2_000_000:
                    continue
                result.extend(python_symbols(path, path.read_text(encoding="utf-8-sig")))
            except (OSError, UnicodeError):
                continue
            if len(result) >= limit:
                return result[:limit]
    return result
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Symbol` | A workspace symbol with a zero-based QScintilla destination. |
| `python_symbols` | Parse definitions without executing user code; reject incomplete syntax. |
| `python_symbols.visit` | Walk immediate members so a method retains its class breadcrumb. |
| `symbol_at` | Return the enclosing symbol chain for a zero-based source line. |
| `workspace_symbols` | Build a bounded index, skipping virtualenvs and unreadable files. |


### Topic implementation

**Required first:** Topic 28.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
import time
from code_inteligence.analysis_cache import RequestKey
from code_inteligence.symbol_index import workspace_symbols
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _guide_find_symbol(self) -> None:
        """Submit a bounded AST index on a worker, never in the click handler."""
        from PyQt5.QtWidgets import QInputDialog
        query, accepted = QInputDialog.getText(self, "Workspace symbols", "Name")
        if not accepted:
            return
        self._symbol_query = query
        root = self._workspace_root
        # Workspace files may change without an editor event. Use a fresh
        # generation for each explicit search rather than reusing stale cache.
        key = RequestKey("", time.monotonic_ns(), self.python_runner.interpreter,
                         str(root), "workspace-symbols")
        self.analysis.submit(key, lambda: workspace_symbols(root))

    def _guide_analysis_ready(self, key, value) -> None:
        """Reject a result after the active workspace or interpreter changes."""
        if key.kind != "workspace-symbols" or key.workspace != str(self._workspace_root):
            return
        if key.interpreter != self.python_runner.interpreter:
            return
        if isinstance(value, Exception):
            QMessageBox.warning(self, "Symbols", str(value))
            return
        from PyQt5.QtWidgets import QInputDialog
        query = self._symbol_query
        results = [s for s in value if query.casefold() in s.name.casefold()][:100]
        labels = [f"{s.name} — {s.path.relative_to(self._workspace_root)}:{s.line + 1}"
                  for s in results]
        if not labels:
            QMessageBox.information(self, "Symbols", "No matching symbols")
            return
        picked, ok = QInputDialog.getItem(self, "Symbols", "Definition", labels, 0, False)
        if ok:
            item = results[labels.index(picked)]
            self._open_file_at_position(str(item.path), item.line, item.column)

    def _install_workspace_symbols(self):
        """Expose background workspace indexing independently of breadcrumb navigation."""
        self.analysis = shared_analysis()
        self.analysis.ready.connect(self._guide_analysis_ready)
        menu = self.menuBar().addMenu("Symbols")
        menu.addAction("Workspace symbol search", self._guide_find_symbol)
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_workspace_symbols()
```



**Use this topic:** Run `python main.py` from the repository root. Choose Symbols → Workspace symbol search and activate a returned definition.


<a id="topic-29"></a>
## 29. Bounded result caching

### Topic explanation

A bounded LRU retains successful exact-key analysis results. Keys include document identity, path, source digest, caret, request kind, workspace, and interpreter. Errors are not cached; environment changes clear retained results.

LRU promotes recent successful results and evicts old entries beyond its capacity. Cache keys include source identity/hash, caret, request kind, interpreter and workspace. Hits are queued through the same delivery path as fresh results, failures are not retained, and environment changes clear the cache. A menu action displays the entry count and clears it on request.


**Documentation:**

- [Python OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)

### Topic code


#### Replace file: `code_inteligence/analysis_cache.py`

**Folder:** `code_inteligence/` already exists. **File:** `analysis_cache.py`. Replace the complete file contents starting at line 1. Keep the same filename.

```python
"""Revision and environment keyed bounded result storage."""
from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass


class LRU:
    """A small revision-aware cache whose keys include environment identity."""

    def __init__(self, size: int = 64):
        """Fix the maximum retained number of entries."""
        if size < 1:
            raise ValueError("Cache capacity must be positive")
        self.size, self.values = size, OrderedDict()

    def get(self, key):
        """Read and promote a recently used result."""
        if key not in self.values:
            return None
        self.values.move_to_end(key)
        return self.values[key]

    def put(self, key, value) -> None:
        """Insert a result, evicting old revisions automatically."""
        self.values[key] = value
        self.values.move_to_end(key)
        # OrderedDict keeps the oldest entry at the front after each promotion.
        while len(self.values) > self.size:
            self.values.popitem(last=False)


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
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `LRU` | A small revision-aware cache whose keys include environment identity. |
| `LRU.__init__` | Fix the maximum retained number of entries. |
| `LRU.get` | Read and promote a recently used result. |
| `LRU.put` | Insert a result, evicting old revisions automatically. |
| `RequestKey` | Identity required to reject analysis produced for obsolete content. |


### Topic implementation

**Required first:** Topic 28.


#### Imports in `code_inteligence/analysis_scheduler.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.analysis_cache import LRU
```



#### Edit `code_inteligence/analysis_scheduler.py` — `AnalysisQueue.__init__`

Create the bounded result store alongside owned jobs.

Inside this method, find exactly:

```python
        self.futures = set()
```

Replace only that block with:

```python
        self.cache, self.futures = LRU(), set()
```



#### Edit `code_inteligence/analysis_scheduler.py` — `AnalysisQueue.submit`

Reuse only exact immutable request identities.

Inside this method, find exactly:

```python
        started = perf_counter()
```

Replace only that block with:

```python
        if key in self.cache.values:
            # Queue delivery even for a hit: callers record their key after submit returns.
            future = Future()
            future.set_result(self.cache.get(key))
            self.futures.add(future)
            self._deliver.emit(key, future, serial, 0.0)
            return
        started = perf_counter()
```



#### Edit `code_inteligence/analysis_scheduler.py` — `AnalysisQueue._receive`

Do not cache transient failures.

Inside this method, find exactly:

```python
            self.ready.emit(key, value)
```

Replace only that block with:

```python
            if not isinstance(value, Exception):
                self.cache.put(key, value)
            self.ready.emit(key, value)
```



#### Edit `code_inteligence/analysis_scheduler.py` — `AnalysisQueue.invalidate_all`

A workspace/interpreter change discards cached results as well as live requests.

Inside this method, find exactly:

```python
        self.latest.clear()
```

Replace only that block with:

```python
        self.latest.clear()
        self.cache.values.clear()
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _show_analysis_cache(self):
        """Show the bounded entry count and allow explicit cache clearing."""
        cache = self.analysis.cache
        answer = QMessageBox.question(self, "Analysis cache",
            f"{len(cache.values)} of {cache.size} entries retained. Clear cached results?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            cache.values.clear()
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_topic_29(self):
        """Expose the analysis cache commands in the existing menu bar."""
        menu = self.menuBar().addMenu('Analysis cache')
        action_0 = menu.addAction('Inspect / clear cache')
        action_0.setObjectName("topic.29.0")
        action_0.triggered.connect(lambda checked=False: self._show_analysis_cache())
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_topic_29()
```



**Use this topic:** Run `python main.py` from the repository root. Repeat an identical analysis request and inspect Analysis cache → Inspect / clear cache for its bounded retained entry count.


<a id="topic-30"></a>
## 30. Pause hidden-panel work

### Topic explanation

Problems, References, Markdown outline, and a lightweight clickable minimap defer presentation rebuilding while hidden. The minimap paints bounded line-width groups and viewport position; clicking navigates to the corresponding source line.

The presentation timer schedules only visible outline/minimap work. Show events rebuild once from current state, while hidden SnapshotDock panels retain data without rebuilding trees. The minimap is generated for the active view and a shared references provider feeds the existing References shell. Background process and document ownership continue independently of visibility.


**Documentation:**

- [Qt QWidget visibility](https://doc.qt.io/archives/qt-5.15/qwidget.html)
- [Qt QTimer](https://doc.qt.io/archives/qt-5.15/qtimer.html)
- [Qt QPainter](https://doc.qt.io/archives/qt-5.15/qpainter.html)
- [Qt paint events](https://doc.qt.io/archives/qt-5.15/qwidget.html#paintEvent)

### Topic code


#### Create file: `side_bar_widgets/document_minimap.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `document_minimap.py`. Create the file and paste the complete contents starting at line 1.

```python
"""A lightweight line-shape minimap with click-to-navigate and deferred hidden work."""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QWidget


class DocumentMinimap(QWidget):
    """Render line lengths and the visible viewport without another editor lexer."""
    navigate = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize bounded geometry samples and an explicit paused state."""
        super().__init__(parent)
        self.setMinimumWidth(100)
        self.widths, self.total, self.first, self.visible = (), 1, 0, 1
        self.paused = False

    def set_source(self, source, first=0, visible=1):
        """Reduce text into at most 1,000 line groups and update the viewport."""
        lines = source.splitlines() or ['']
        self.total = len(lines)
        stride = max(1, (self.total + 999) // 1000)
        self.widths = tuple(max(len(line.expandtabs(4)) for line in lines[i:i + stride])
                            for i in range(0, self.total, stride))
        self.first, self.visible, self.paused = first, visible, False
        self.update()

    def set_paused(self):
        """Discard old document geometry when the active tab exceeds its work budget."""
        self.widths, self.paused = (), True
        self.update()

    def paintEvent(self, event):
        """Paint compact line silhouettes and a translucent viewport rectangle."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#262a33'))
        if self.paused:
            painter.setPen(QColor('#dcdfe4'))
            painter.drawText(self.rect(), Qt.AlignCenter | Qt.TextWordWrap, 'Minimap paused for large file')
            return
        step = self.height() / max(1, len(self.widths))
        painter.setPen(QColor('#969ba7'))
        for row, width in enumerate(self.widths):
            y = int(row * step)
            painter.drawLine(4, y, min(self.width() - 4, 4 + width), y)
        y = int(self.first / self.total * self.height())
        height = max(4, int(self.visible / self.total * self.height()))
        painter.fillRect(0, y, self.width(), height, QColor(97, 175, 239, 60))

    def mousePressEvent(self, event):
        """Navigate proportionally to a clicked source line."""
        if event.button() == Qt.LeftButton and not self.paused:
            self.navigate.emit(min(self.total - 1, max(0, int(event.pos().y() / max(1, self.height()) * self.total))))
        else:
            super().mousePressEvent(event)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `DocumentMinimap` | Render line lengths and the visible viewport without another editor lexer. |
| `DocumentMinimap.__init__` | Initialize bounded geometry samples and an explicit paused state. |
| `DocumentMinimap.set_source` | Reduce text into at most 1,000 line groups and update the viewport. |
| `DocumentMinimap.set_paused` | Discard old document geometry when the active tab exceeds its work budget. |
| `DocumentMinimap.paintEvent` | Paint compact line silhouettes and a translucent viewport rectangle. |
| `DocumentMinimap.mousePressEvent` | Navigate proportionally to a clicked source line. |


### Topic implementation

**Required first:** Topic 6, Topic 20, Topic 28.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.document_minimap import DocumentMinimap
```



#### Add methods to `main.py` — `MainWindow`

Add only this topic’s methods to the existing MainWindow class. Insert the following **after the complete `MainWindow._show_update_dialog` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_visible_panels(self):
        """Schedule presentation work only for panels the user can currently see."""
        self.minimap_dock = QDockWidget("Minimap", self)
        self.minimap_dock.setObjectName("MinimapDock")
        self.minimap = DocumentMinimap(self.minimap_dock)
        self.minimap_dock.setWidget(self.minimap)
        self.addDockWidget(Qt.RightDockWidgetArea, self.minimap_dock)
        self.minimap_dock.hide()
        self.minimap.navigate.connect(self._jump_heading)
        self._presentation_timer = QTimer(self)
        self._presentation_timer.setSingleShot(True)
        self._presentation_timer.setInterval(160)
        self._presentation_timer.timeout.connect(self._refresh_optional_panels)
        self.minimap_dock.visibilityChanged.connect(lambda shown: self._refresh_optional_panels())
        self.outline_frame.installEventFilter(self)
        self.preview.installEventFilter(self)
        menu = self.menuBar().addMenu("Optional panels")
        menu.addAction(self.minimap_dock.toggleViewAction())
        menu.addAction("Find references", self._guide_find_references)

    def eventFilter(self, watched, event):
        """Refresh a newly shown presentation once while preserving normal Qt event handling."""
        if event.type() == QEvent.Show:
            if watched is self.outline_frame:
                QTimer.singleShot(0, self._refresh_optional_panels)
            elif watched is self.preview:
                QTimer.singleShot(0, self.render_preview)
        return super().eventFilter(watched, event)

    def _refresh_optional_panels(self):
        """Compute visible snapshots only; hidden data owners keep their state."""
        editor = self.current_editor()
        if self.outline_frame.isVisible():
            self._update_outline()
        if not self.minimap_dock.isVisible():
            return
        if editor is None:
            self.minimap.set_source("")
        elif editor.length() >= 2_000_000 and not getattr(editor, "_large_file_override", False):
            self.minimap.set_paused()
        else:
            self.minimap.set_source(editor.text(), editor.firstVisibleLine(),
                                    editor.SendScintilla(editor.SCI_LINESONSCREEN))

    def _guide_find_references(self):
        """Run project reference search on the current Python tab's shared provider."""
        editor = self.current_editor()
        if not isinstance(editor, PythonEditor):
            return
        self.references.show()
        self.references.set_rows((), "Searching references…")
        if editor.length() > 2_000_000 and not getattr(editor, "_large_file_override", False):
            self.references.set_rows((), "Analysis paused; use the per-tab large-file override")
            return
        line, column = editor.getCursorPosition()
        editor.references_finder.find_references(line + 1, column, editor.text(), editor.path)

    def _guide_references_ready(self, editor, generation, rows):
        """Reject an inactive source tab and retain current reference navigation rows."""
        if editor is not self.current_editor() or generation != editor.references_finder.generation:
            return
        self.references.set_rows([(name, path, line, column) for path, line, column, name in rows],
                                 "No references found")
```



#### Edit `main.py` — `MainWindow.__init__`

Initialize this topic after the window widgets exist and before settings/session restoration. Keep any other topic initialization calls below it.

Inside this method, find exactly:

```python
        self.init_ui()
```

Replace only that block with:

```python
        self.init_ui()
        self._install_visible_panels()
```



#### Insert at the start of `main.py` — `MainWindow._update_outline`

Defer both Python and Markdown outline building while the panel is hidden. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if not self.outline_frame.isVisible():
            return
```



#### `MainWindow.render_preview`

Keep Topic 26’s `if not self.preview.isVisible(): return` guard. If implementing this topic without Topic 26, add that guard at the start of `render_preview`, immediately after its docstring.


#### Insert at the start of `main.py` — `MainWindow._connect_editor`

Connect presentation scheduling and reference-result snapshots once per editor. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        editor.textChanged.connect(self._presentation_timer.start)
        editor.verticalScrollBar().valueChanged.connect(lambda value: self._presentation_timer.start())
        if isinstance(editor, PythonEditor):
            editor.references_finder.references_found.connect(
                lambda generation, rows, ed=editor: self._guide_references_ready(ed, generation, rows))
            editor.references_finder.references_empty.connect(
                lambda generation, ed=editor: self._guide_references_ready(ed, generation, []))
            editor.references_finder.error.connect(
                lambda generation, error, ed=editor: self.references.set_rows((), error)
                if ed is self.current_editor() else None)
```



#### Insert at the start of `main.py` — `MainWindow._on_current_editor_changed`

Rebuild newly focused visible panels after focus signals settle. Insert the following immediately after this method’s docstring (or immediately after its `def` line if it has no docstring), before its first existing statement. Keep any earlier topic hooks below the new insertion.

```python
        if hasattr(self, "_presentation_timer"):
            self._presentation_timer.start()
```



#### Edit `main.py` — `MainWindow.closeEvent`

Stop presentation scheduling after accepted close prompts. Without Topic 23, insert the timer stop before the original terminal stop instead.

Inside this method, find exactly:

```python
        if self.terminal is not None:
            self.terminal.stop()
```

Replace only that block with:

```python
        self._presentation_timer.stop()
        if self.terminal is not None:
            self.terminal.stop()
```



**Use this topic:** Run `python main.py` from the repository root. Hide and show Outline or Minimap and use Optional panels → Find references in Python. Showing a panel refreshes its latest snapshot.
