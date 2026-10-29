# MarkdownEditor — topic-by-topic implementation guide

Each topic is complete in this order: **Topic explanation → Topic code → Topic implementation**. Finish that topic’s integration before starting another. Each final “Use this topic” paragraph tells you how to open the feature in the running editor; there are no test files to create.

The target is the existing [ConfidentCupcake/MarkdownEditor repository](https://github.com/ConfidentCupcake/MarkdownEditor). Paths below are relative to its root. Keep the repository’s spelling `code_inteligence`. All referenced source folders already exist; no new top-level folders or packages are needed.

The integration lives directly in `MainWindow`, `PythonEditor`, `MarkdownEditor`, `SettingsDialog`, `RuffLspController` and `FileManager`, as applicable. Do not create `editor_extensions.py` or an `EditorExtensions` class.

## Implementation order

Topics **1, 2, 3, 4, 5, 6, 8, 9 and 10 can each be implemented against the current repository without the other topics**. Topic **7 requires Topic 6** because a disk change must update one document and all its views consistently. Topic **11 is already implemented** in the repository.

If you want every feature, use **1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11**. You can run the editor after each completed topic. The numeric order also keeps the shared save/rename/session replacements before file-watching additions. Do not reapply Topic 6’s replacements after Topic 7; those replacements precede the watcher additions.

For every edit, locate the named class and method, then use the exact code anchor shown. Method names remain usable after earlier additions shift line numbers. “Replace only that block” preserves the rest of the method, including changes from other topics. Add each import and initialization call once. When several topics add code after the same anchor, retain all previously added lines below the new block.

These instructions start from the repository code, not a local copy with the previous guide’s combined integration already applied. If you already installed that combined integration, first restore only its changes from your own version-control history while retaining unrelated work; deleting its coordinator alone would leave broken calls. No existing repository file needs deletion. Within each topic, obsolete methods/blocks to replace are identified explicitly.


| Topic | Prerequisite |
|---|---|
| [1. Command Registry and Command Palette](#topic-1) | None |
| [2. Caret and Selection Contrast](#topic-2) | None |
| [3. Provider-Neutral Diagnostics and Problems](#topic-3) | None |
| [4. Ruff Quick Fixes](#topic-4) | None |
| [5. Find All References](#topic-5) | None |
| [6. Shared Document State and Enhanced Tabs](#topic-6) | None |
| [7. External File and Directory Watching](#topic-7) | Topic 6 |
| [8. Snippets and Reusable Templates](#topic-8) | None |
| [9. Code Folding](#topic-9) | None |
| [10. Document Minimap](#topic-10) | None |
| [11. Git Branch Indicator and Commit Graph](#topic-11) | Already in repository |


<a id="topic-1"></a>
## 1. Command Registry and Command Palette

### Topic explanation

A command registry is a searchable collection of the editor’s existing menu actions. The palette lets you find and run those actions from the keyboard. It calls the same QAction that the menu uses, preserving its shortcut, enabled state and checked state.

Command stores the action and its searchable label. CommandRegistry walks the current menus; CommandPaletteDialog filters those records and triggers the chosen action. Refreshing discovery on every opening prevents removed Recent Files actions from being retained. Stable object names identify the existing static actions; menu-path IDs cover unnamed dynamic entries.


**Documentation used for this topic:**

- [`QAction` reference](https://doc.qt.io/archives/qt-5.15/qaction.html)
- [`QMenu`](https://doc.qt.io/archives/qt-5.15/qmenu.html)
- [`QDialog`](https://doc.qt.io/archives/qt-5.15/qdialog.html)
- [`QListWidget`](https://doc.qt.io/archives/qt-5.15/qlistwidget.html)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `code_inteligence/command_registry.py`

**Folder:** `code_inteligence/` already exists. **File:** `command_registry.py`. Paste the complete code below starting at line 1.

```python
from __future__ import annotations

from dataclasses import dataclass

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QMenu, QMenuBar


@dataclass(frozen=True)
class Command:
    """One stable application command backed by its existing QAction."""

    command_id: str
    label: str
    category: str
    action: QAction

    @property
    def searchable_text(self) -> str:
        """Combine category, current label and shortcut into case-insensitive searchable text."""
        return f"{self.category} {self.label} {self.action.shortcut().toString()}".casefold()


class CommandRegistry(QObject):
    """Own the commands shared by menus, shortcuts, and the palette."""

    def __init__(self, parent=None):
        """Create the command map without copying any QAction callbacks."""
        super().__init__(parent)
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Retain one command per stable identifier and reject accidental duplicate registration."""
        if command.command_id in self._commands:
            raise ValueError(f"Duplicate command id: {command.command_id}")
        self._commands[command.command_id] = command

    def commands(self) -> tuple[Command, ...]:
        """Return the current discovered commands as an immutable sequence."""
        return tuple(self._commands.values())

    def register_menu_bar(self, menu_bar: QMenuBar) -> None:
        """Traverse top-level menus and collect their executable leaf actions."""
        for top_action in menu_bar.actions():
            menu = top_action.menu()
            if menu is not None:
                self._register_menu(menu, self._clean(top_action.text()))

    def _register_menu(self, menu: QMenu, category: str) -> None:
        """Collect leaf actions without retaining invisible menu entries."""
        for action in menu.actions():
            submenu = action.menu()
            label = self._clean(action.text())
            if submenu is not None:
                self._register_menu(submenu, f"{category} / {label}")
                continue
            if action.isSeparator() or not action.isVisible() or not label:
                continue
            # objectName is the future stable-ID path. Existing actions do not
            # set one yet, so the normalized menu path is a migration fallback.
            command_id = action.objectName() or self._slug(f"{category}.{label}")
            if command_id not in self._commands:
                self.register(Command(command_id, label, category, action))

    @staticmethod
    def _clean(text: str) -> str:
        """Remove Qt mnemonic ampersands from a displayed menu label."""
        return text.replace("&", "").strip()

    @staticmethod
    def _slug(value: str) -> str:
        """Build a fallback identifier for legacy actions that have no explicit object name."""
        return ".".join(value.casefold().replace("/", " ").split())

    def refresh_menus(self, menu_bar):
        """Rebuild discovery so recent-file actions removed by Qt are never retained."""
        self._commands.clear()
        self.register_menu_bar(menu_bar)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Command` | One stable application command backed by its existing QAction. |
| `Command.searchable_text` | Combine category, current label and shortcut into case-insensitive searchable text. |
| `CommandRegistry` | Own the commands shared by menus, shortcuts, and the palette. |
| `CommandRegistry.__init__` | Create the command map without copying any QAction callbacks. |
| `CommandRegistry.register` | Retain one command per stable identifier and reject accidental duplicate registration. |
| `CommandRegistry.commands` | Return the current discovered commands as an immutable sequence. |
| `CommandRegistry.register_menu_bar` | Traverse top-level menus and collect their executable leaf actions. |
| `CommandRegistry._register_menu` | Collect leaf actions without retaining invisible menu entries. |
| `CommandRegistry._clean` | Remove Qt mnemonic ampersands from a displayed menu label. |
| `CommandRegistry._slug` | Build a fallback identifier for legacy actions that have no explicit object name. |
| `CommandRegistry.refresh_menus` | Rebuild discovery so recent-file actions removed by Qt are never retained. |


#### Create `code_inteligence/command_palette.py`

**Folder:** `code_inteligence/` already exists. **File:** `command_palette.py`. Paste the complete code below starting at line 1.

```python
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout

from code_inteligence.command_registry import Command, CommandRegistry


class CommandPaletteDialog(QDialog):
    """Keyboard-first filtered view over a CommandRegistry."""

    def __init__(self, registry: CommandRegistry, parent=None):
        """Build a search field and result list bound to the shared command registry."""
        super().__init__(parent, Qt.Popup)
        self.registry = registry
        self.setMinimumWidth(620)
        layout = QVBoxLayout(self)
        self.query = QLineEdit(self)
        self.query.setPlaceholderText("Type a command…")
        self.results = QListWidget(self)
        layout.addWidget(self.query)
        layout.addWidget(self.results)
        self.query.textChanged.connect(self._refill)
        self.query.returnPressed.connect(self._execute_current)
        self.results.itemActivated.connect(lambda _item: self._execute_current())

    def open_palette(self) -> None:
        """Refresh live menu actions, reset the query and focus the popup search field."""
        self.registry.refresh_menus(self.parent().menuBar())
        self.query.clear()
        self._refill("")
        self.show()
        self.raise_()
        self.query.setFocus()

    def _refill(self, query: str) -> None:
        """Filter by all query tokens while displaying current shortcuts and disabled state."""
        tokens = query.casefold().split()
        self.results.clear()
        for command in self.registry.commands():
            if all(token in command.searchable_text for token in tokens):
                shortcut = command.action.shortcut().toString()
                suffix = f"    {shortcut}" if shortcut else ""
                item = QListWidgetItem(f"{command.category}: {command.label}{suffix}")
                item.setData(Qt.UserRole, command)
                item.setFlags(item.flags() | Qt.ItemIsEnabled if command.action.isEnabled()
                              else item.flags() & ~Qt.ItemIsEnabled)
                self.results.addItem(item)
        if self.results.count():
            self.results.setCurrentRow(0)

    def _execute_current(self) -> None:
        """Close the popup and trigger the selected existing action only when enabled."""
        item = self.results.currentItem()
        command: Command | None = item.data(Qt.UserRole) if item else None
        if command is None or not command.action.isEnabled():
            return
        self.accept()
        command.action.trigger()

    def keyPressEvent(self, event) -> None:
        """Move through results with arrow keys and preserve normal dialog Escape behavior."""
        if event.key() in (Qt.Key_Down, Qt.Key_Up):
            delta = 1 if event.key() == Qt.Key_Down else -1
            count = self.results.count()
            if count:
                self.results.setCurrentRow((self.results.currentRow() + delta) % count)
            return
        super().keyPressEvent(event)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `CommandPaletteDialog` | Keyboard-first filtered view over a CommandRegistry. |
| `CommandPaletteDialog.__init__` | Build a search field and result list bound to the shared command registry. |
| `CommandPaletteDialog.open_palette` | Refresh live menu actions, reset the query and focus the popup search field. |
| `CommandPaletteDialog._refill` | Filter by all query tokens while displaying current shortcuts and disabled state. |
| `CommandPaletteDialog._execute_current` | Close the popup and trigger the selected existing action only when enabled. |
| `CommandPaletteDialog.keyPressEvent` | Move through results with arrow keys and preserve normal dialog Escape behavior. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.command_registry import CommandRegistry
from code_inteligence.command_palette import CommandPaletteDialog
```



#### Add methods to `main.py` — `MainWindow`

The menu and palette use the same QAction instances; no action callbacks are copied. Insert the following **after the complete `MainWindow.set_up_menu` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_command_palette(self):
        """Expose existing menu actions through one searchable command dialog."""
        self.command_registry = CommandRegistry(self)
        self.command_palette = CommandPaletteDialog(self.command_registry, self)
        menu = self.menuBar().addMenu("Commands")
        action = menu.addAction("Command Palette")
        action.setObjectName("workbench.command_palette")
        action.setShortcut("Ctrl+Shift+L")
        action.triggered.connect(self.command_palette.open_palette)
        # Discovery runs again when opened, so rebuilt Recent Files entries stay valid.
        self.command_registry.refresh_menus(self.menuBar())
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
        self._install_command_palette()
```



#### Edit `main.py` — `MainWindow.set_up_menu`

Assign IDs after all existing menu actions have been created. This changes no shortcuts or callbacks.

Inside this method, find exactly:

```python
        check_updates_action.triggered.connect(lambda: self.check_for_updates(manual=True))
```

Replace only that block with:

```python
        check_updates_action.triggered.connect(lambda: self.check_for_updates(manual=True))

        # Stable IDs survive translated or renamed menu labels.
        new_file.setObjectName("menu.new_file")
        open_file.setObjectName("menu.open_file")
        open_folder.setObjectName("menu.open_folder")
        save_file.setObjectName("menu.save_file")
        save_as.setObjectName("menu.save_as")
        save_all_action.setObjectName("menu.save_all_action")
        close_all_action.setObjectName("menu.close_all_action")
        undo_action.setObjectName("menu.undo_action")
        redo_action.setObjectName("menu.redo_action")
        cut_action.setObjectName("menu.cut_action")
        copy_action.setObjectName("menu.copy_action")
        paste_action.setObjectName("menu.paste_action")
        select_all_action.setObjectName("menu.select_all_action")
        delete_line_action.setObjectName("menu.delete_line_action")
        find_action.setObjectName("menu.find_action")
        replace_action.setObjectName("menu.replace_action")
        goto_action.setObjectName("menu.goto_action")
        toggle_comment_action.setObjectName("menu.toggle_comment_action")
        goto_definition_action.setObjectName("menu.goto_definition_action")
        run_file_action.setObjectName("menu.run_file_action")
        run_with_args_action.setObjectName("menu.run_with_args_action")
        run_selection_action.setObjectName("menu.run_selection_action")
        stop_action.setObjectName("menu.stop_action")
        interpreter_action.setObjectName("menu.interpreter_action")
        toggle_sidebar_action.setObjectName("menu.toggle_sidebar_action")
        toggle_preview_action.setObjectName("menu.toggle_preview_action")
        toggle_console_action.setObjectName("menu.toggle_console_action")
        toggle_terminal_action.setObjectName("menu.toggle_terminal_action")
        split_right_action.setObjectName("menu.split_right_action")
        unsplit_action.setObjectName("menu.unsplit_action")
        fullscreen_editor.setObjectName("menu.fullscreen_editor")
        starting_window_size.setObjectName("menu.starting_window_size")
        git_refresh_action.setObjectName("menu.git_refresh_action")
        toggle_git_history_action.setObjectName("menu.toggle_git_history_action")
        settings_action.setObjectName("menu.settings_action")
        hacker_action.setObjectName("menu.hacker_action")
        check_updates_action.setObjectName("menu.check_updates_action")
```



**Use this topic:** Run `python main.py` from the repository root. Press **Ctrl+Shift+L**, type a menu action such as “Save”, and press Enter. The palette uses the existing action’s enabled state.


<a id="topic-2"></a>
## 2. Caret and Selection Contrast

### Topic explanation

Caret and selection contrast controls let you choose the cursor width/color and the foreground/background of selected text. These preferences make the editing position and selected region easier to distinguish from the theme.

The contrast module reads and validates stored overrides, writes them only after Save, and applies them after the lexer’s theme colors. Reset removes the override so the active theme supplies the color again. SettingsDialog holds temporary choices until the existing settings workflow accepts them.


**Documentation used for this topic:**

- [`QsciScintilla` reference](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)
- [`QColor`](https://doc.qt.io/archives/qt-5.15/qcolor.html)
- [`QColorDialog`](https://doc.qt.io/archives/qt-5.15/qcolordialog.html)
- [`QSettings`](https://doc.qt.io/archives/qt-5.15/qsettings.html)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `code_settings/contrast.py`

**Folder:** `code_settings/` already exists. **File:** `contrast.py`. Paste the complete code below starting at line 1.

```python
from PyQt5.QtGui import QColor


def relative_luminance(color: QColor) -> float:
    """Return WCAG relative luminance for a valid sRGB QColor."""
    if not color.isValid():
        raise ValueError("A valid color is required")

    def linear(component: int) -> float:
        """Convert one eight-bit sRGB channel to linear light for luminance calculation."""
        value = component / 255.0
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(value) for value in (color.red(), color.green(), color.blue()))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: QColor, second: QColor) -> float:
    """Return the luminance contrast ratio, with the lighter color divided by the darker color."""
    lighter, darker = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


COLOR_KEYS = ("caret_color", "selection_foreground", "selection_background")


def read_preferences(settings):
    """Read optional overrides; missing colors inherit the active lexer theme."""
    return {"caret_width": settings.value("caret_width", 2, type=int),
            **{key: settings.value(key, type=str) if settings.contains(key) else None
               for key in COLOR_KEYS}}


def write_preferences(settings, values):
    """Persist width and remove reset color keys instead of saving invalid colors."""
    settings.setValue("caret_width", max(1, min(5, int(values.get("caret_width", 2)))))
    for key in COLOR_KEYS:
        value = values.get(key)
        if value and QColor(value).isValid():
            settings.setValue(key, value)
        else:
            settings.remove(key)


def apply_preferences(editor, values):
    """Apply overrides after the lexer has restored its own editor-wide theme."""
    lexer = editor.lexer()
    pairs = (("caret_color", "caret-color", "#f31122", editor.setCaretForegroundColor),
             ("selection_foreground", "selection-foreground", "#ffffff", editor.setSelectionForegroundColor),
             ("selection_background", "selection-background", "#264f78", editor.setSelectionBackgroundColor))
    for key, theme_key, fallback, setter in pairs:
        color = QColor(values.get(key) or "")
        if not color.isValid():
            color = lexer.editor_color(theme_key, fallback) if hasattr(lexer, "editor_color") else QColor(fallback)
        setter(color)
    editor.setCaretWidth(max(1, min(5, int(values.get("caret_width", 2)))))
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `relative_luminance` | Return WCAG relative luminance for a valid sRGB QColor. |
| `relative_luminance.linear` | Convert one eight-bit sRGB channel to linear light for luminance calculation. |
| `contrast_ratio` | Return the luminance contrast ratio, with the lighter color divided by the darker color. |
| `read_preferences` | Read optional overrides; missing colors inherit the active lexer theme. |
| `write_preferences` | Persist width and remove reset color keys instead of saving invalid colors. |
| `apply_preferences` | Apply overrides after the lexer has restored its own editor-wide theme. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_settings.contrast import read_preferences, write_preferences, apply_preferences
```



#### Edit `main.py` — `MainWindow._load_settings`

Merge the saved caret and selection values into the settings dictionary.

Inside this method, find exactly:

```python
            "highlight_line": self.settings.value("highlight_line", True, type=bool),
```

Replace only that block with:

```python
            "highlight_line": self.settings.value("highlight_line", True, type=bool),
            **read_preferences(self.settings),
```



#### Edit `main.py` — `MainWindow._save_settings`

Persist validated overrides only after the Settings dialog is accepted.

Inside this method, find exactly:

```python
        self.settings.sync()
```

Replace only that block with:

```python
        write_preferences(self.settings, new_settings)
        self.settings.sync()
```



#### Edit `main.py` — `MainWindow._apply_editor_settings`

Apply overrides after lexer/theme styling so the theme does not erase the chosen contrast.

Inside this method, find exactly:

```python
        editor.SendScintilla(4003, 0, -1)
```

Replace only that block with:

```python
        editor.SendScintilla(4003, 0, -1)
        # Apply explicit overrides after the theme has supplied its defaults.
        apply_preferences(editor, settings)
```



#### Replace `code_settings/settings_dialog.py` — `SettingsDialog._create_appearance_tab`

This replacement adds only the contrast controls and retains the current settings fields. Delete this method’s complete current definition, from `def _create_appearance_tab(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _create_appearance_tab(self) -> QWidget:
        """Build theme, paper, caret, selection and line-display controls using current preferences."""
        tab = QWidget()
        layout = self._style_form(QFormLayout(tab))

        self.theme_combo = QComboBox()
        themes_dir = Path(asset_path("themes"))

        # Enumerate immutable packaged themes. A user override keeps the same
        # filename and is resolved later by MainWindow._theme_path().
        if themes_dir.is_dir():
            for theme_file in sorted(themes_dir.glob("*.json")):
                self.theme_combo.addItem(theme_file.stem, theme_file.name)

        # Never save a null theme value, even if a damaged installation has no
        # theme data. The wheel smoke test below should catch that condition.
        if self.theme_combo.count() == 0:
            self.theme_combo.addItem("theme", "theme.json")

        current_theme = self.settings.get("theme") or "theme.json"
        index = self.theme_combo.findData(current_theme)
        # If the stored theme file was deleted, fall back to the first
        # entry instead of leaving the combo blank.
        if index < 0:
            index = 0
        self.theme_combo.setCurrentIndex(index)
        layout.addRow("Theme:", self.theme_combo)

        # Paper color picker: a QSettings override on top of the active
        # theme's paper (theme switches do NOT reset it; the swatch shows
        # the effective color and starts from the current value).
        paper_row = QHBoxLayout()
        self.paper_btn = QPushButton()
        self._paper_override = self.settings.get("paper_color") or None
        self._paper_color = QColor(
            self._paper_override
            or self.settings.get("theme_paper", "#1e1f22")
        )
        self._refresh_paper_swatch()
        self.paper_btn.clicked.connect(self._pick_paper_color)
        paper_row.addWidget(self.paper_btn)

        self.paper_reset_btn = QPushButton("Reset to theme")
        self.paper_reset_btn.setToolTip("Drop the override - the active\n"
                                        "theme's own paper-color is used.")
        self.paper_reset_btn.clicked.connect(self._reset_paper_color)
        paper_row.addWidget(self.paper_reset_btn)
        paper_row.addStretch()
        layout.addRow("Paper color:", paper_row)

        self.caret_width_spin = QSpinBox()
        self.caret_width_spin.setRange(1, 5)
        self.caret_width_spin.setValue(self.settings.get("caret_width", 2))
        layout.addRow("Caret width:", self.caret_width_spin)
        self._appearance_colors = {key: self.settings.get(key) for key in
                                   ("caret_color", "selection_foreground", "selection_background")}
        for key, label in (("caret_color", "Caret color:"),
                           ("selection_foreground", "Selection text:"),
                           ("selection_background", "Selection background:")):
            row = QHBoxLayout()
            button = QPushButton(self._appearance_colors[key] or "Use theme")
            reset = QPushButton("Reset to theme")
            button.clicked.connect(lambda _checked=False, k=key, b=button: self._pick_editor_color(k, b))
            reset.clicked.connect(lambda _checked=False, k=key, b=button: self._reset_editor_color(k, b))
            row.addWidget(button)
            row.addWidget(reset)
            layout.addRow(label, row)

        self.line_numbers_cb = QCheckBox("Show Line Numbers")
        self.line_numbers_cb.setChecked(self.settings.get("line_numbers", True))
        layout.addRow("", self.line_numbers_cb)
        
        self.highlight_line_cb = QCheckBox("Highlight Current Line")
        self.highlight_line_cb.setChecked(self.settings.get("highlight_line", True))
        layout.addRow("", self.highlight_line_cb)
        
        return tab
```



#### Replace `code_settings/settings_dialog.py` — `SettingsDialog.get_settings`

This replacement adds only the contrast controls and retains the current settings fields. Delete this method’s complete current definition, from `def get_settings(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def get_settings(self) -> dict:
        """Return the complete edited preference dictionary without writing before Save is accepted."""
        return {
            "font_family": self.font_combo.currentFont().family(),
            "font_size": self.font_size_spin.value(),
            "tab_width": self.tab_width_spin.value(),
            "word_wrap": self.word_warp_cb.isChecked(),
            "restore_tabs": self.restore_tabs_cb.isChecked(),
            "interpreter": self.interpreter_input.text().strip(),
            "ruff_save_mode": self.ruff_combo.currentData(),
            "theme": self.theme_combo.currentData() or "theme.json",
            "paper_color": self._paper_override,
            "line_numbers": self.line_numbers_cb.isChecked(),
            "highlight_line": self.highlight_line_cb.isChecked(),
            "caret_width": self.caret_width_spin.value(),
            **self._appearance_colors,
        }
```



#### Add methods to `code_settings/settings_dialog.py` — `SettingsDialog`

These callbacks edit the dialog’s pending color choices; Cancel leaves saved settings unchanged. Insert the following **after the complete `SettingsDialog.get_settings` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _pick_editor_color(self, key, button):
        """Store a valid color override only when the picker is accepted."""
        color = QColorDialog.getColor(QColor(self._appearance_colors[key] or "#ffffff"), self, "Editor color")
        if color.isValid():
            self._appearance_colors[key] = color.name()
            button.setText(color.name())

    def _reset_editor_color(self, key, button):
        """Remove a dialog-level override so Save restores active-theme inheritance."""
        self._appearance_colors[key] = None
        button.setText("Use theme")
```



**Use this topic:** Run `python main.py`, open **Settings → Appearance**, change caret width or selection colors, and save. Open a document and select text. Reset a color to return to the active theme.


<a id="topic-3"></a>
## 3. Provider-Neutral Diagnostics and Problems

### Topic explanation

Provider-neutral diagnostics represent problems independently of the tool that reported them. A Problems dock can therefore display Ruff issues now and accept another provider later without rewriting its UI.

Diagnostic records carry provider, URI, path, severity, source range, revision and the original provider payload. DiagnosticsManager replaces one provider/URI collection at a time. MainWindow adapts Ruff records and owns the dock. RuffLspController clears outdated rows on edits, relocation and shutdown. Navigation finds the live URI owner, so untitled files do not require a real disk path. The existing cat/XP behavior remains connected.


**Documentation used for this topic:**

- [`QDockWidget`](https://doc.qt.io/archives/qt-5.15/qdockwidget.html)
- [`QTreeWidget`](https://doc.qt.io/archives/qt-5.15/qtreewidget.html)
- [LSP Diagnostic specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic)
- [Qt model/view](https://doc.qt.io/archives/qt-5.15/model-view-programming.html)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `ruff_implementation/diagnostics_model.py`

**Folder:** `ruff_implementation/` already exists. **File:** `diagnostics_model.py`. Paste the complete code below starting at line 1.

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any


class DiagnosticSeverity(IntEnum):
    """Define application-level severity ordering independently of provider numeric values."""
    INFORMATION = 1
    WARNING = 2
    ERROR = 3


@dataclass(frozen=True, order=True)
class Position:
    """Zero-based line and Python-character column."""
    line: int
    column: int


@dataclass(frozen=True)
class SourceRange:
    """Store a zero-based half-open range using Python-character columns."""
    start: Position
    end: Position


@dataclass(frozen=True)
class Diagnostic:
    """Carry provider-neutral diagnostic data while retaining an opaque provider payload for actions."""
    provider: str
    uri: str
    path: Path | None
    source_range: SourceRange
    severity: DiagnosticSeverity
    code: str
    message: str
    revision: int | None = None
    provider_data: Any = field(default=None, compare=False, repr=False)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `DiagnosticSeverity` | Define application-level severity ordering independently of provider numeric values. |
| `Position` | Zero-based line and Python-character column. |
| `SourceRange` | Store a zero-based half-open range using Python-character columns. |
| `Diagnostic` | Carry provider-neutral diagnostic data while retaining an opaque provider payload for actions. |


#### Create `ruff_implementation/diagnostics_manager.py`

**Folder:** `ruff_implementation/` already exists. **File:** `diagnostics_manager.py`. Paste the complete code below starting at line 1.

```python
from PyQt5.QtCore import QObject, pyqtSignal

from ruff_implementation.diagnostics_model import Diagnostic


class DiagnosticsManager(QObject):
    """Store complete diagnostic snapshots by provider and document."""

    changed = pyqtSignal(list)

    def __init__(self, parent=None):
        """Create an empty provider/document snapshot map owned by the GUI thread."""
        super().__init__(parent)
        self._collections: dict[tuple[str, str], tuple[Diagnostic, ...]] = {}

    def replace(self, provider: str, uri: str, diagnostics: list[Diagnostic]) -> None:
        """Validate snapshot identity and replace or remove exactly one provider/document collection."""
        if any(item.provider != provider or item.uri != uri for item in diagnostics):
            raise ValueError("Diagnostic collection identity does not match its contents")
        key = (provider, uri)
        if diagnostics:
            self._collections[key] = tuple(diagnostics)
        else:
            self._collections.pop(key, None)
        self.changed.emit(self.all())

    def clear_document(self, uri: str) -> None:
        """Remove every provider collection belonging to one document URI."""
        self._collections = {key: value for key, value in self._collections.items()
                             if key[1] != uri}
        self.changed.emit(self.all())

    def clear_provider(self, provider: str) -> None:
        """Remove a provider after its environment or server instance changes."""
        self._collections = {key: value for key, value in self._collections.items()
                             if key[0] != provider}
        self.changed.emit(self.all())

    def all(self) -> list[Diagnostic]:
        """Return a deterministic severity/path/position ordering of all retained diagnostics."""
        values = [item for group in self._collections.values() for item in group]
        return sorted(values, key=lambda item: (
            -int(item.severity), str(item.path or ""),
            item.source_range.start.line, item.source_range.start.column,
        ))
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `DiagnosticsManager` | Store complete diagnostic snapshots by provider and document. |
| `DiagnosticsManager.__init__` | Create an empty provider/document snapshot map owned by the GUI thread. |
| `DiagnosticsManager.replace` | Validate snapshot identity and replace or remove exactly one provider/document collection. |
| `DiagnosticsManager.clear_document` | Remove every provider collection belonging to one document URI. |
| `DiagnosticsManager.clear_provider` | Remove a provider after its environment or server instance changes. |
| `DiagnosticsManager.all` | Return a deterministic severity/path/position ordering of all retained diagnostics. |


#### Create `side_bar_widgets/problems_panel.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `problems_panel.py`. Paste the complete code below starting at line 1.

```python
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from ruff_implementation.diagnostics_model import Diagnostic, DiagnosticSeverity


class ProblemsPanel(QTreeWidget):
    """Provider-neutral, navigable diagnostic list."""

    diagnosticActivated = pyqtSignal(object)

    def __init__(self, parent=None):
        """Configure six columns and connect row activation to diagnostic navigation."""
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHeaderLabels(("Severity", "File", "Line", "Column", "Code", "Message"))
        self.itemActivated.connect(self._activate)

    def set_diagnostics(self, diagnostics: list[Diagnostic]) -> None:
        """Replace displayed rows with a complete provider-neutral snapshot."""
        self.clear()
        labels = {
            DiagnosticSeverity.ERROR: "Error",
            DiagnosticSeverity.WARNING: "Warning",
            DiagnosticSeverity.INFORMATION: "Info",
        }
        for diagnostic in diagnostics:
            start = diagnostic.source_range.start
            row = QTreeWidgetItem((
                labels[diagnostic.severity],
                diagnostic.path.name if diagnostic.path else diagnostic.uri,
                str(start.line + 1), str(start.column + 1),
                diagnostic.code, diagnostic.message,
            ))
            row.setData(0, Qt.UserRole, diagnostic)
            self.addTopLevelItem(row)

    def _activate(self, item: QTreeWidgetItem, _column: int) -> None:
        """Emit the diagnostic stored on the activated row without parsing visible text."""
        diagnostic = item.data(0, Qt.UserRole)
        if diagnostic is not None:
            self.diagnosticActivated.emit(diagnostic)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `ProblemsPanel` | Provider-neutral, navigable diagnostic list. |
| `ProblemsPanel.__init__` | Configure six columns and connect row activation to diagnostic navigation. |
| `ProblemsPanel.set_diagnostics` | Replace displayed rows with a complete provider-neutral snapshot. |
| `ProblemsPanel._activate` | Emit the diagnostic stored on the activated row without parsing visible text. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from ruff_implementation.diagnostics_manager import DiagnosticsManager
from ruff_implementation.diagnostics_model import Diagnostic, DiagnosticSeverity, Position, SourceRange
from ruff_implementation.ruff_diagnostics_model import RuffSeverity
from side_bar_widgets.problems_panel import ProblemsPanel
```



#### Add methods to `main.py` — `MainWindow`

These methods belong directly to MainWindow. The Problems dock needs no command palette or shared document store. Insert the following **after the complete `MainWindow._on_ruff_diagnostics` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_problems(self):
        """Create the provider-neutral diagnostic store and its Problems dock."""
        self.diagnostics_manager = DiagnosticsManager(self)
        self.problems_panel = ProblemsPanel(self)
        self.problems_dock = QDockWidget("Problems", self)
        self.problems_dock.setObjectName("ProblemsDock")
        self.problems_dock.setWidget(self.problems_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.problems_dock)
        self.problems_dock.hide()
        self.diagnostics_manager.changed.connect(self.problems_panel.set_diagnostics)
        self.problems_panel.diagnosticActivated.connect(self._open_problem)
        menu = self.menuBar().addMenu("Diagnostics")
        menu.addAction(self.problems_dock.toggleViewAction())

    def _publish_problems(self, editor, rows):
        """Convert Ruff records into generic diagnostics without losing their raw payload."""
        controller = editor.ruff_lsp
        if controller is None or controller._closed:
            return
        levels = {RuffSeverity.ERROR: DiagnosticSeverity.ERROR,
                  RuffSeverity.WARNING: DiagnosticSeverity.WARNING,
                  RuffSeverity.INFO: DiagnosticSeverity.INFORMATION}
        path = Path(editor.path) if editor.path else None
        values = [Diagnostic("ruff", controller.uri, path,
                    SourceRange(Position(item.start.line, item.start.column),
                                Position(item.end.line, item.end.column)),
                    levels[item.severity], item.code, item.message, item.revision, item)
                  for item in rows]
        # Replace one provider/URI collection, retaining other providers' rows.
        self.diagnostics_manager.replace("ruff", controller.uri, values)

    def _open_problem(self, diagnostic):
        """Navigate to a live URI owner, including an unsaved Python document."""
        point = diagnostic.source_range.start
        for editor in self.tab_view.all_editors():
            controller = getattr(editor, "ruff_lsp", None)
            if controller is not None and controller.uri == diagnostic.uri:
                self.tab_view.focus_editor(editor)
                editor.setCursorPosition(point.line, point.column)
                return
        if diagnostic.path is not None:
            self._open_file_at_position(str(diagnostic.path), point.line, point.column)
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
        self._install_problems()
```



#### Edit `main.py` — `MainWindow._on_ruff_diagnostics`

Publish the generic rows and keep the existing cat/XP reactions below this insertion.

Inside this method, find exactly:

```python
        had_issues = getattr(editor, "_had_ruff_issues", False)
```

Replace only that block with:

```python
        if hasattr(self, "diagnostics_manager"):
            self._publish_problems(editor, diagnostics)
        had_issues = getattr(editor, "_had_ruff_issues", False)
```



#### Edit `main.py` — `MainWindow._restart_ruff`

Remove the old server’s rows before replacing its client.

Inside this method, find exactly:

```python
        old_client = self.ruff_lsp_client
```

Replace only that block with:

```python
        self.diagnostics_manager.clear_provider("ruff")
        old_client = self.ruff_lsp_client
```



#### Add methods to `ruff_implementation/ruff_lsp_controller.py` — `RuffLspController`

The existing controller owns the URI, so it can clear stale rows before rename, close, or another edit. The optional lookup is safe during editor construction. Insert the following **after the complete `RuffLspController.relocate` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _clear_problem_rows(self):
        """Remove this URI's Problems rows when its text or lifecycle changes."""
        manager = getattr(self.editor.window(), "diagnostics_manager", None)
        if manager is not None:
            manager.clear_document(self.uri)
```



#### Edit `ruff_implementation/ruff_lsp_controller.py` — `RuffLspController.relocate`

Clear the old URI while it still identifies the currently displayed rows.

Inside this method, find exactly:

```python
        old_uri = self._uri
```

Replace only that block with:

```python
        self._clear_problem_rows()
        old_uri = self._uri
```



#### Edit `ruff_implementation/ruff_lsp_controller.py` — `RuffLspController._on_text_changed`

Clear the old URI while it still identifies the currently displayed rows.

Inside this method, find exactly:

```python
        if self._closed:
```

Replace only that block with:

```python
        self._clear_problem_rows()
        if self._closed:
```



#### Edit `ruff_implementation/ruff_lsp_controller.py` — `RuffLspController.shutdown`

Clear the old URI while it still identifies the currently displayed rows.

Inside this method, find exactly:

```python
        if self._closed:
```

Replace only that block with:

```python
        self._clear_problem_rows()
        if self._closed:
```



#### Edit `main.py` — `MainWindow._dispose_editor`

Clear diagnostics before setParent(None) detaches the editor from MainWindow. The controller shutdown then remains safe when this topic is installed on its own.

Inside this method, find exactly:

```python
        if isinstance(editor, PythonEditor):
```

Replace only that block with:

```python
        # Clear rows while the editor still belongs to this MainWindow.
        controller = getattr(editor, "ruff_lsp", None)
        if controller is not None:
            controller._clear_problem_rows()
        if isinstance(editor, PythonEditor):
```



**Use this topic:** Run `python main.py`, open a Python file that produces Ruff diagnostics, and show **Diagnostics → Problems**. Activate a row to navigate to it. Editing the buffer clears outdated rows until fresh diagnostics arrive.


<a id="topic-4"></a>
## 4. Ruff Quick Fixes

### Topic explanation

A quick fix is an edit suggested by the language server for a diagnostic. Right-clicking a Ruff issue requests its available fixes and lets you choose one without rewriting the file manually.

RuffLspController captures the URI and document version, requests code actions asynchronously and offers only the returned choices. WorkspaceEditApplier validates every range before changing anything, converts negotiated LSP column units to Scintilla byte positions, and applies replacements from the end of the document as one undo operation. This implementation supports complete single-document text edits; it rejects cross-file edits, resource operations and unsupported command-only actions rather than partially applying them.


**Documentation used for this topic:**

- [Ruff editor settings](https://docs.astral.sh/ruff/editors/settings/#codeaction)
- [LSP Code Action](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_codeAction)
- [WorkspaceEdit](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#workspaceEdit)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `ruff_implementation/workspace_edit.py`

**Folder:** `ruff_implementation/` already exists. **File:** `workspace_edit.py`. Paste the complete code below starting at line 1.

```python
"""Validate complete single-document LSP edits before touching the buffer."""
from dataclasses import dataclass


class WorkspaceEditError(ValueError):
    """An action cannot be applied completely to the requested revision."""


@dataclass(frozen=True)
class EditorTextEdit:
    """One checked replacement using absolute UTF-8 byte positions."""
    start: int
    end: int
    text: str


class WorkspaceEditApplier:
    """Apply a single-document edit as one undo group after complete validation."""

    def __init__(self, controller):
        """Use the requesting Ruff controller's URI, version, and position encoding."""
        self.controller = controller

    def _position(self, point):
        """Reject out-of-range positions and split UTF-8/UTF-16 characters."""
        editor = self.controller.editor
        if not isinstance(point, dict):
            raise WorkspaceEditError("Malformed position")
        line, column = point.get("line"), point.get("character")
        if type(line) is not int or type(column) is not int or not 0 <= line < editor.lines() or column < 0:
            raise WorkspaceEditError("Position is outside the document")
        text = editor.text(line).rstrip("\r\n")
        encoding = self.controller.client.position_encoding
        codec = {"utf-8": "utf-8", "utf-16": "utf-16-le", "utf-32": "utf-32-le"}.get(encoding)
        if codec is None:
            raise WorkspaceEditError("Unsupported position encoding")
        raw = text.encode(codec)
        width = {"utf-8": 1, "utf-16": 2, "utf-32": 4}[encoding]
        stop = column * width
        if stop > len(raw):
            raise WorkspaceEditError("Column is outside the line")
        try:
            prefix = raw[:stop].decode(codec)
        except UnicodeError as error:
            raise WorkspaceEditError("Position splits a Unicode character") from error
        return editor.positionFromLineIndex(line, len(prefix))

    def apply(self, payload, uri, version):
        """Validate identity, version, ranges, annotations and overlap before mutation."""
        owner = self.controller
        editor = owner.editor
        if owner._closed or owner.uri != uri or owner.document_version != version:
            raise WorkspaceEditError("Document changed after this action was requested")
        if editor.isReadOnly() or not isinstance(payload, dict):
            raise WorkspaceEditError("Document is read-only or edit is malformed")
        if payload.get("changeAnnotations"):
            raise WorkspaceEditError("Annotated edits require a separate approval UI")
        if "changes" in payload and "documentChanges" in payload:
            raise WorkspaceEditError("Ambiguous workspace edit")
        if "changes" in payload:
            changes = payload["changes"]
            if not isinstance(changes, dict) or set(changes) != {uri}:
                raise WorkspaceEditError("Only complete single-document edits are supported")
            raw_edits = changes[uri]
        else:
            entries = payload.get("documentChanges")
            if not isinstance(entries, list) or len(entries) != 1:
                raise WorkspaceEditError("Only one text-document change is supported")
            entry = entries[0]
            if not isinstance(entry, dict) or "kind" in entry:
                raise WorkspaceEditError("File creation, rename and deletion are not supported")
            document = entry.get("textDocument", {})
            if document.get("uri") != uri or document.get("version") not in (None, version):
                raise WorkspaceEditError("Action refers to another document or revision")
            raw_edits = entry.get("edits")
        if not isinstance(raw_edits, list):
            raise WorkspaceEditError("Malformed edit list")
        edits = []
        for raw in raw_edits:
            if not isinstance(raw, dict) or not isinstance(raw.get("newText"), str) or "annotationId" in raw:
                raise WorkspaceEditError("Malformed or annotated text edit")
            value = raw.get("range", {})
            start, end = self._position(value.get("start")), self._position(value.get("end"))
            if end < start:
                raise WorkspaceEditError("Reversed edit range")
            edits.append(EditorTextEdit(start, end, raw["newText"]))
        edits.sort(key=lambda item: (item.start, item.end))
        previous = None
        for edit in edits:
            if previous is not None and (edit.start < previous.end or edit.start == previous.start):
                raise WorkspaceEditError("Overlapping or ambiguous edits")
            previous = edit
        # All checks happen first; descending byte positions survive later replacements.
        editor.beginUndoAction()
        try:
            for edit in reversed(edits):
                first = editor.lineIndexFromPosition(edit.start)
                last = editor.lineIndexFromPosition(edit.end)
                editor.setSelection(*first, *last)
                editor.replaceSelectedText(edit.text)
        finally:
            editor.endUndoAction()
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `WorkspaceEditError` | An action cannot be applied completely to the requested revision. |
| `EditorTextEdit` | One checked replacement using absolute UTF-8 byte positions. |
| `WorkspaceEditApplier` | Apply a single-document edit as one undo group after complete validation. |
| `WorkspaceEditApplier.__init__` | Use the requesting Ruff controller's URI, version, and position encoding. |
| `WorkspaceEditApplier._position` | Reject out-of-range positions and split UTF-8/UTF-16 characters. |
| `WorkspaceEditApplier.apply` | Validate identity, version, ranges, annotations and overlap before mutation. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `ruff_implementation/ruff_lsp_controller.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMenu, QMessageBox
from ruff_implementation.workspace_edit import WorkspaceEditApplier, WorkspaceEditError
```



#### Replace `ruff_implementation/ruff_lsp_controller.py` — `RuffLspController.context_menu`

Replace the old placeholder with asynchronous action retrieval and explicit action selection. Delete this method’s complete current definition, from `def context_menu(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def context_menu(self, event, view=None):
        """Display current Ruff quick fixes without retaining the temporary Qt event."""
        view = view or self.editor
        position = view.SendScintilla(view.SCI_POSITIONFROMPOINT, event.pos().x(), event.pos().y())
        if position < 0:
            return False
        line, _column = self.editor.lineIndexFromPosition(position)
        diagnostic = self.view.at_line(line)
        if diagnostic is None:
            return False
        point = QPoint(event.globalPos())
        def receive(actions, error, uri, revision):
            """Show returned action titles and apply only the explicitly selected item."""
            if error:
                QMessageBox.warning(self.editor, "Quick fixes", str(error))
                return
            menu = QMenu(self.editor)
            pairs = []
            for action in actions:
                if not isinstance(action, dict):
                    continue
                item = menu.addAction(str(action.get("title", "Quick fix")))
                item.setEnabled(not bool(action.get("disabled")))
                pairs.append((item, action))
            if not pairs:
                menu.addAction("No quick fix available").setEnabled(False)
            chosen = menu.exec_(point)
            for item, action in pairs:
                if chosen is item:
                    try:
                        self.apply_code_action(action, uri, revision)
                    except WorkspaceEditError as error:
                        QMessageBox.warning(self.editor, "Quick fixes", str(error))
                    break
        self.request_quick_fixes(diagnostic, receive)
        return True
```



#### Add methods to `ruff_implementation/ruff_lsp_controller.py` — `RuffLspController`

The request captures a URI/version pair; the applier rejects stale, cross-file or unsupported actions. Insert the following **after the complete `RuffLspController.context_menu` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def request_quick_fixes(self, diagnostic, callback):
        """Request actions with raw provider data and capture the exact document identity."""
        uri, revision, client = self.uri, self.document_version, self.client
        if self._closed or diagnostic.revision != revision or not client.is_ready:
            callback([], {"message": "Diagnostic is stale"}, uri, revision)
            return
        self.change_timer.stop()
        self._send_change()
        def receive(result, error):
            """Discard replies after closure, relocation, editing or server replacement."""
            if self._closed or client is not self.client or self.uri != uri or self.document_version != revision:
                return
            callback(result if isinstance(result, list) else [], error, uri, revision)
        client.request("textDocument/codeAction", {
            "textDocument": {"uri": uri}, "range": diagnostic.raw["range"],
            "context": {"diagnostics": [diagnostic.raw], "only": ["quickfix"], "triggerKind": 1}}, receive)

    def apply_code_action(self, action, uri, revision):
        """Apply a direct edit completely or report an unsupported action form."""
        if action.get("disabled") or action.get("command") or not isinstance(action.get("edit"), dict):
            raise WorkspaceEditError("This action needs an unsupported command or resolve step")
        WorkspaceEditApplier(self).apply(action["edit"], uri, revision)
```



#### Replace `python_editor/pythoneditor.py` — `PythonEditor.contextMenuEvent`

Offer Ruff fixes before documentation lookup. The optional document-store lookup also supports Topic 6 if installed; it requires no new import or prerequisite. Delete this method’s complete current definition, from `def contextMenuEvent(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def contextMenuEvent(self, event):
        """
        Request documentation for a right-clicked identifier.
        
        Blank space retains the existing diagnostic/editor context menu. 
        A keyboard menu request also keeps the normal context menu behavior.
        """
        from PyQt5.QtGui import QContextMenuEvent
        # A mirrored view routes fixes through the sole document synchronizer.
        controller = self.ruff_lsp
        store = getattr(self.window(), "documents", None)
        if controller is None and store is not None and self in store.documents:
            controller = getattr(store.document(self).analysis_owner, "ruff_lsp", None)
        if (controller is not None and event.reason() == QContextMenuEvent.Mouse
                and controller.context_menu(event, self)):
            event.accept()
            return

        if (self.is_python_file and not self._shutting_down and event.reason() == QContextMenuEvent.Mouse):
            target = self._documentation_target(event.pos())
            if target is not None:
                self._ruff_hover_timer.stop()
                self._dismiss_signature()
                self._documentation_global_pos = event.globalPos()
                line, column = target
                self.hover_helper.get_hover(
                    line, column, self.text(),
                    str(self.full_path) if self.full_path else None,
                )
                event.accept()
                return
        
        super().contextMenuEvent(event)
```



**Use this topic:** Run `python main.py`, open a Python file with a Ruff issue that has a fix, and right-click the issue. Choose a returned fix; the edit can be undone as one operation. The selected Python interpreter must already have Ruff available for the repository’s existing Ruff server.


<a id="topic-5"></a>
## 5. Find All References

### Topic explanation

Find All References locates semantic uses of the symbol under the caret in a Python project. Unlike text search, Jedi resolves the symbol rather than matching every occurrence of its spelling.

ReferencesFinder runs Jedi away from the GUI thread using the selected interpreter and workspace root. Generation tokens invalidate older requests; the editor also checks that its path has not changed. PythonEditor emits plain SourceLocation values, and MainWindow presents them in a dock. Results navigate through the existing file-opening method with zero-based line/column coordinates.


**Documentation used for this topic:**

- [`jedi.Script.get_references`](https://jedi.readthedocs.io/en/latest/docs/api.html#jedi.Script.get_references)
- [Jedi API](https://jedi.readthedocs.io/en/latest/docs/api.html)
- [`QThread`](https://doc.qt.io/archives/qt-5.15/qthread.html)
- [LSP references](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_references)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `code_inteligence/locations_panel.py`

**Folder:** `code_inteligence/` already exists. **File:** `locations_panel.py`. Paste the complete code below starting at line 1.

```python
from dataclasses import dataclass
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


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

    def __init__(self, parent=None):
        """Create the symbol/path/line/column view and connect row activation."""
        super().__init__(parent)
        self.setHeaderLabels(("Symbol", "File", "Line", "Column"))
        self.itemActivated.connect(self._activate)

    def set_locations(self, locations: list[SourceLocation]) -> None:
        """Sort and replace rows while retaining each original location as hidden item data."""
        self.clear()
        for location in sorted(locations, key=lambda x: (str(x.path), x.line, x.column)):
            row = QTreeWidgetItem((location.label, location.path.name,
                                   str(location.line + 1), str(location.column + 1)))
            row.setToolTip(1, str(location.path))
            row.setData(0, Qt.UserRole, location)
            self.addTopLevelItem(row)

    def _activate(self, item, _column) -> None:
        """Emit the source location attached to the activated row."""
        location = item.data(0, Qt.UserRole)
        if location:
            self.locationActivated.emit(location)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `SourceLocation` | Store a disk path and zero-based line/character column for navigation. |
| `LocationsPanel` | Display provider-independent reference locations and emit selected records. |
| `LocationsPanel.__init__` | Create the symbol/path/line/column view and connect row activation. |
| `LocationsPanel.set_locations` | Sort and replace rows while retaining each original location as hidden item data. |
| `LocationsPanel._activate` | Emit the source location attached to the activated row. |


#### Replace `code_inteligence/references_finder.py`

**Folder:** `code_inteligence/` already exists. **File:** `references_finder.py`. Paste the complete code below starting at line 1. Delete the old file contents first.

```python
from PyQt5.QtCore import QThread, pyqtSignal
from jedi import Script, Project, create_environment
import jedi
# The existing helpers run concurrently; disable Jedi's shared mutable fast parser.
jedi.settings.fast_parser = False


class ReferencesFinder(QThread):
    """Find references without blocking, replaying only the newest request."""

    references_found = pyqtSignal(int, list)
    references_empty = pyqtSignal(int)
    error = pyqtSignal(int, str)

    def __init__(self):
        """Initialize latest-request generations and replay pending work after the active thread finishes."""
        super().__init__(None)
        self._generation = 0
        self._request = None
        self._pending = None
        self._shutting_down = False
        self.finished.connect(self._start_pending)

    def find_references(self, line, column, code, file_path=None, workspace=None, interpreter=None):
        """Capture plain source, caret, project and interpreter values for the newest request."""
        if self._shutting_down:
            return None
        self._generation += 1
        request = (self._generation, line, column, code, file_path, workspace, interpreter)
        if self.isRunning():
            self._pending = request
        else:
            self._request = request
            self.start()
        return self._generation

    def _start_pending(self):
        """Start only the most recent queued request when the previous worker finishes."""
        if self._shutting_down or self._pending is None:
            return
        self._request, self._pending = self._pending, None
        self.start()

    def run(self):
        """Run semantic Jedi reference lookup off the GUI thread and emit plain locations or an error."""
        generation, line, column, code, file_path, workspace, interpreter = self._request
        try:
            names = Script(code=code, path=file_path, project=Project(workspace) if workspace else None,
                           environment=create_environment(interpreter, safe=False) if interpreter else None).get_references(
                line=line, column=column, include_builtins=False
            )
            if self._shutting_down:
                return
            references = [
                (str(name.module_path), name.line - 1, name.column, name.name)
                for name in names
                if name.module_path is not None
            ]
            if references:
                self.references_found.emit(generation, references)
            else:
                self.references_empty.emit(generation)
        except Exception as exc:
            if not self._shutting_down:
                self.error.emit(generation, str(exc))

    def shutdown(self):
        """Reject future/results requests; completion remains asynchronous."""
        self._shutting_down = True
        self._pending = None
        self.requestInterruption()

    def invalidate(self):
        """Reject in-flight results without forcibly terminating a running thread."""
        self._generation += 1
        self._pending = None

    @property
    def generation(self):
        """Expose the current GUI-side request generation for delivery checks."""
        return self._generation
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `ReferencesFinder` | Find references without blocking, replaying only the newest request. |
| `ReferencesFinder.__init__` | Initialize latest-request generations and replay pending work after the active thread finishes. |
| `ReferencesFinder.find_references` | Capture plain source, caret, project and interpreter values for the newest request. |
| `ReferencesFinder._start_pending` | Start only the most recent queued request when the previous worker finishes. |
| `ReferencesFinder.run` | Run semantic Jedi reference lookup off the GUI thread and emit plain locations or an error. |
| `ReferencesFinder.shutdown` | Reject future/results requests; completion remains asynchronous. |
| `ReferencesFinder.invalidate` | Reject in-flight results without forcibly terminating a running thread. |
| `ReferencesFinder.generation` | Expose the current GUI-side request generation for delivery checks. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `python_editor/pythoneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.references_finder import ReferencesFinder
from code_inteligence.locations_panel import SourceLocation
```



#### Add signals in `python_editor/pythoneditor.py`

Inside `class PythonEditor`, immediately before the existing `goto_definition_requested` declaration, insert:

```python
    referencesReady = pyqtSignal(list)
    referencesFailed = pyqtSignal(str)
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Construct and connect the reference worker at the end of editor initialization.

Inside this method, find exactly:

```python
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()
```

Replace only that block with:

```python
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()

        self.references_finder = ReferencesFinder()
        self.references_finder.references_found.connect(self._references_found)
        self.references_finder.references_empty.connect(lambda generation: self._references_found(generation, []))
        self.references_finder.error.connect(self._references_error)
        # A result computed from older buffer contents must never be displayed.
        self.textChanged.connect(self.references_finder.invalidate)
```



#### Replace `python_editor/pythoneditor.py` — `PythonEditor._cursorPositionChanged`

Include the references worker in cursor invalidation and the existing worker shutdown tracking. Delete this method’s complete current definition, from `def _cursorPositionChanged(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

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

Include the references worker in cursor invalidation and the existing worker shutdown tracking. Delete this method’s complete current definition, from `def _analysis_workers(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

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

Capture the current path as well as the worker generation so Save As cannot display results for the old file. Insert the following **after the complete `PythonEditor.closeEvent` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def find_all_references(self):
        """Find semantic references using the selected project's interpreter and root."""
        if self._shutting_down or not self.is_python_file:
            return
        window = self.window()
        self._reference_request_path = self.full_path
        line, column = self.getCursorPosition()
        self.references_finder.find_references(line + 1, column, self.text(),
            str(self.full_path) if self.full_path else None,
            str(window._workspace_root), window.python_runner.interpreter)

    def _references_found(self, generation, rows):
        """Publish plain navigation records only for the current live request."""
        if (generation == self.references_finder.generation and not self._shutting_down
                and self.full_path == getattr(self, "_reference_request_path", None)):
            self.referencesReady.emit([SourceLocation(Path(path), line, column, name)
                                       for path, line, column, name in rows])

    def _references_error(self, generation, message):
        """Report a current request failure to the owning window's visible status area."""
        if (generation == self.references_finder.generation and not self._shutting_down
                and self.full_path == getattr(self, "_reference_request_path", None)):
            self.referencesFailed.emit(message)
```



#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.locations_panel import LocationsPanel
```



#### Add methods to `main.py` — `MainWindow`

Keep result presentation and navigation in the existing window. Insert the following **after the complete `MainWindow._open_file_at_position` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_references(self):
        """Create the references dock and its independent menu command."""
        self.references_panel = LocationsPanel(self)
        self.references_dock = QDockWidget("References", self)
        self.references_dock.setObjectName("ReferencesDock")
        self.references_dock.setWidget(self.references_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.references_dock)
        self.references_dock.hide()
        self.references_panel.locationActivated.connect(self._open_reference)
        menu = self.menuBar().addMenu("References")
        action = menu.addAction("Find All References")
        action.setObjectName("edit.references")
        action.setShortcut("Shift+F12")
        action.triggered.connect(self._find_references)
        menu.addAction(self.references_dock.toggleViewAction())

    def _find_references(self):
        """Request semantic references only from the current Python editor."""
        editor = self.current_editor()
        if isinstance(editor, PythonEditor):
            self.references_panel.set_locations([])
            editor.find_all_references()

    def _show_references(self, editor, rows):
        """Show results only while their requesting view is still current."""
        if editor is self.current_editor():
            self.references_panel.set_locations(rows)
            self.references_dock.show()
            self.references_dock.raise_()

    def _open_reference(self, location):
        """Navigate to the result's zero-based line and character column."""
        self._open_file_at_position(str(location.path), location.line, location.column)
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
        self._install_references()
```



#### Edit `main.py` — `MainWindow._connect_editor`

Connect each newly created Python view to the result panel and status bar.

Inside this method, find exactly:

```python
            editor.goto_definition_requested.connect(self._open_file_at_position)
```

Replace only that block with:

```python
            editor.goto_definition_requested.connect(self._open_file_at_position)
            editor.referencesReady.connect(lambda rows, ed=editor: self._show_references(ed, rows))
            editor.referencesFailed.connect(lambda message: self.statusBar().showMessage(message, 6000))
```



#### Edit `main.py` — `MainWindow._restart_ruff`

Invalidate semantic results when the interpreter or workspace root changes.

Inside this method, find exactly:

```python
        old_client = self.ruff_lsp_client
```

Replace only that block with:

```python
        self.references_panel.set_locations([])
        for view in self.tab_view.all_editors():
            if isinstance(view, PythonEditor):
                view.references_finder.invalidate()
        old_client = self.ruff_lsp_client
```



**Use this topic:** Run `python main.py`, open a Python project, place the caret on a symbol and press **Shift+F12**. Activate a result to open its location. A Markdown view does not start a Jedi request.


<a id="topic-6"></a>
## 6. Shared Document State and Enhanced Tabs

### Topic explanation

Shared document state separates one file’s text and dirty state from the individual tabs that display it. Duplicate View Right shares a QsciDocument, including edits and undo history, while each view keeps its own caret, scroll position, pin and preview state.

DocumentStateStore maps views to shared metadata. DirtyViews adapts the existing dirty-set callers so save/close operations count a document once. MainWindow directly handles duplicate views, preview promotion, pinned tabs, reopen, search, sorting and session restoration. Only one Python view synchronizes a shared document with Ruff; closing that owner transfers synchronization to a surviving view. Reopen and session restore retain saved-file locations, not unsaved-buffer recovery snapshots.


**Documentation used for this topic:**

- [`QsciDocument`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciDocument.html)
- [`QTabBar`](https://doc.qt.io/archives/qt-5.15/qtabbar.html)
- [`weakref`](https://docs.python.org/3/library/weakref.html)
- [`QTabWidget`](https://doc.qt.io/archives/qt-5.15/qtabwidget.html)
- [MutableSet adapter](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `code_inteligence/document_state.py`

**Folder:** `code_inteligence/` already exists. **File:** `document_state.py`. Paste the complete code below starting at line 1.

```python
"""One document state shared by multiple views, with a legacy dirty-set adapter."""
from dataclasses import dataclass, field
from pathlib import Path
from weakref import WeakKeyDictionary, WeakSet
from collections.abc import MutableSet
from PyQt5.QtCore import QObject, pyqtSignal


@dataclass(eq=False)
class DocumentState:
    """Shared identity and flags; cursor, selection, and pin state remain per-view."""
    path: Path | None
    dirty: bool = False
    read_only: bool = False
    externally_changed: bool = False
    disk_digest: bytes | None = None
    revision: int = 0
    views: WeakSet = field(default_factory=WeakSet)
    analysis_owner: object = None


@dataclass
class TabState:
    """Placement-independent flags belonging to one editor view."""
    pinned: bool = False
    preview: bool = False


@dataclass(frozen=True)
class ClosedTab:
    """A disk-backed reopen record; unsaved text is not a reopen snapshot."""
    path: Path
    python_mode: bool
    line: int
    column: int


class DocumentStateStore(QObject):
    """Own document/view associations without retaining closed editor widgets."""
    stateChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        """Create separate shared-document and per-tab maps."""
        super().__init__(parent)
        self.documents = WeakKeyDictionary()
        self.tabs = WeakKeyDictionary()
        self.recently_closed = []

    def attach(self, view, path=None, document=None):
        """Attach a new view; share state only when explicitly sharing its QsciDocument."""
        if view in self.documents:
            return self.documents[view]
        document = document or DocumentState(Path(path) if path else None)
        document.views.add(view)
        if document.analysis_owner is None:
            document.analysis_owner = view
        self.documents[view] = document
        self.tabs[view] = TabState()
        return document

    def document(self, view):
        """Return the one shared state for an attached editor."""
        return self.documents[view]

    def tab(self, view):
        """Return flags belonging only to the requested view."""
        return self.tabs[view]

    def all(self):
        """Return each shared document once, preserving live view-map order."""
        return list(dict.fromkeys(self.documents.values()))

    def set_dirty(self, view, dirty):
        """Change shared dirty state and promote all edited previews to permanent tabs."""
        document = self.document(view)
        document.dirty = bool(dirty)
        if dirty:
            document.revision += 1
            for item in document.views:
                self.tab(item).preview = False
        self.stateChanged.emit(document)

    def detach(self, view):
        """Remove a view; the lifecycle coordinator transfers Ruff ownership first."""
        document = self.documents.pop(view, None)
        self.tabs.pop(view, None)
        if document is not None:
            document.views.discard(view)
            if document.analysis_owner is view:
                document.analysis_owner = next(iter(document.views), None)
        return document

    def remember_closed(self, view, python_mode):
        """Keep at most twenty disk-backed reopen locations, newest first."""
        document = self.document(view)
        if document.path is not None:
            line, column = view.getCursorPosition()
            self.recently_closed.insert(0, ClosedTab(document.path, python_mode, line, column))
            del self.recently_closed[20:]


class DirtyViews(MutableSet):
    """Adapt existing dirty-set callers to the store without a second source of truth."""

    def __init__(self, store):
        """Retain the shared state store used by all membership and mutation operations."""
        self.store = store

    def __contains__(self, view):
        """Report shared dirtiness for any attached view of the document."""
        return view in self.store.documents and self.store.document(view).dirty

    def __iter__(self):
        """Yield one representative per dirty document for save/close prompt loops."""
        return iter([doc.analysis_owner for doc in self.store.all() if doc.dirty])

    def __len__(self):
        """Count dirty documents rather than duplicate views."""
        return sum(doc.dirty for doc in self.store.all())

    def add(self, view):
        """Mark the attached document dirty through its central state owner."""
        self.store.set_dirty(view, True)

    def discard(self, view):
        """Clear dirtiness for every view after an explicit save or discard decision."""
        if view in self.store.documents:
            self.store.set_dirty(view, False)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `DocumentState` | Shared identity and flags; cursor, selection, and pin state remain per-view. |
| `TabState` | Placement-independent flags belonging to one editor view. |
| `ClosedTab` | A disk-backed reopen record; unsaved text is not a reopen snapshot. |
| `DocumentStateStore` | Own document/view associations without retaining closed editor widgets. |
| `DocumentStateStore.__init__` | Create separate shared-document and per-tab maps. |
| `DocumentStateStore.attach` | Attach a new view; share state only when explicitly sharing its QsciDocument. |
| `DocumentStateStore.document` | Return the one shared state for an attached editor. |
| `DocumentStateStore.tab` | Return flags belonging only to the requested view. |
| `DocumentStateStore.all` | Return each shared document once, preserving live view-map order. |
| `DocumentStateStore.set_dirty` | Change shared dirty state and promote all edited previews to permanent tabs. |
| `DocumentStateStore.detach` | Remove a view; the lifecycle coordinator transfers Ruff ownership first. |
| `DocumentStateStore.remember_closed` | Keep at most twenty disk-backed reopen locations, newest first. |
| `DirtyViews` | Adapt existing dirty-set callers to the store without a second source of truth. |
| `DirtyViews.__init__` | Retain the shared state store used by all membership and mutation operations. |
| `DirtyViews.__contains__` | Report shared dirtiness for any attached view of the document. |
| `DirtyViews.__iter__` | Yield one representative per dirty document for save/close prompt loops. |
| `DirtyViews.__len__` | Count dirty documents rather than duplicate views. |
| `DirtyViews.add` | Mark the attached document dirty through its central state owner. |
| `DirtyViews.discard` | Clear dirtiness for every view after an explicit save or discard decision. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.document_state import DocumentStateStore, DirtyViews
from ruff_implementation.ruff_lsp_controller import RuffLspController
```



#### Edit `main.py` — `MainWindow.__init__`

Create the shared document store before UI construction. DirtyViews preserves the existing dirty-set interface while counting each document once.

Inside this method, find exactly:

```python
        self._dirty_editors = set()
```

Replace only that block with:

```python
        self.documents = DocumentStateStore(self)
        self._dirty_editors = DirtyViews(self.documents)
```



#### Add methods to `main.py` — `MainWindow`

Add the document lifecycle and tab commands directly to MainWindow. The optional references-worker invalidation supports Topic 5 without requiring it. Insert the following **after the complete `MainWindow.mark_editor_clean` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_document_tabs(self):
        """Connect document state to tab titles and expose tab-management commands."""
        self.documents.stateChanged.connect(self._refresh_document_titles)
        menu = self.menuBar().addMenu("Tabs")
        reopen = menu.addAction("Reopen Closed Tab")
        reopen.setObjectName("tabs.reopen")
        reopen.setShortcut("Ctrl+Shift+T")
        reopen.triggered.connect(self._reopen_tab)
        search = menu.addAction("Search Open Tabs")
        search.setObjectName("tabs.search")
        search.triggered.connect(self._search_tabs)
        sort = menu.addAction("Sort Active Group")
        sort.setObjectName("tabs.sort")
        sort.triggered.connect(self._sort_tabs)
        duplicate = menu.addAction("Duplicate View Right")
        duplicate.setObjectName("tabs.duplicate")
        duplicate.triggered.connect(lambda: self._duplicate_view(self.current_editor()))

    def _attach_document_view(self, editor):
        """Attach an editor to shared metadata before connecting its editing signals."""
        document = self.documents.attach(editor, getattr(editor, "path", None))
        document.disk_digest = getattr(editor, "_disk_digest", document.disk_digest)
        if document.path is not None:
            document.read_only = not os.access(document.path, os.W_OK)
            editor.setReadOnly(document.read_only)
        self._refresh_document_titles(document)

    def _refresh_document_titles(self, document):
        """Derive every view's tab title from shared state and per-view pin/preview flags."""
        for view in list(document.views):
            tab = self.documents.tab(view)
            name = document.path.name if document.path else "Untitled"
            title = ("● " if document.dirty else "") + name
            title += " [pinned]" if tab.pinned else " [preview]" if tab.preview else ""
            title += " [RO]" if document.read_only else ""
            title += " [external]" if document.externally_changed else ""
            self.tab_view.set_editor_title(view, title)
            self.tab_view.set_editor_tooltip(view, str(document.path or "Untitled"))

    def _retarget_document(self, editor, path):
        """Update every view's path and bytes metadata after a successful save or rename."""
        document = self.documents.document(editor)
        document.path = Path(path)
        document.disk_digest = getattr(editor, "_disk_digest", None)
        document.revision += 1
        document.read_only = not os.access(path, os.W_OK)
        for view in list(document.views):
            view.path = Path(path)
            view.full_path = Path(path).absolute()
            for name in ("_disk_digest", "_save_target", "_utf8_bom"):
                setattr(view, name, getattr(editor, name, None))
            view.setEolMode(editor.eolMode())
            view.setReadOnly(document.read_only)
            if isinstance(view, PythonEditor):
                view.auto_completer.file_path = str(view.full_path)
                if hasattr(view, "references_finder"):
                    view.references_finder.invalidate()
        owner = document.analysis_owner
        if isinstance(owner, PythonEditor) and owner.ruff_lsp:
            new_uri = Path(path).resolve().as_uri()
            if owner.ruff_lsp.uri != new_uri:
                owner.ruff_lsp.relocate(path)
        self._refresh_document_titles(document)

    def _clean_document(self, editor):
        """Commit shared clean metadata after save and update every view title."""
        document = self.documents.document(editor)
        document.dirty = False
        document.externally_changed = False
        document.disk_digest = getattr(editor, "_disk_digest", None)
        document.revision += 1
        for view in document.views:
            view._disk_digest = document.disk_digest
            view.setModified(False)
        self.documents.stateChanged.emit(document)

    def _duplicate_view(self, source, group=None):
        """Create an independent view over the same Scintilla document and state."""
        if source is None:
            return None
        document = self.documents.document(source)
        if isinstance(source, PythonEditor):
            view = PythonEditor(path=source.path, is_python_file=True, ruff_lsp_client=None)
        else:
            view = MarkdownEditor(path=source.path, is_python_file=False)
        # Share text and undo history; keep cursor/scroll state on each view.
        view.setDocument(source.document())
        for name in ("_utf8_bom", "_disk_digest", "_save_target"):
            setattr(view, name, getattr(source, name, None))
        view.setEolMode(source.eolMode())
        view.setReadOnly(document.read_only)
        self.documents.attach(view, document=document)
        self._apply_editor_settings(view, self._current_settings)
        self._connect_editor(view)
        if group is None:
            group = self.tab_view._create_group(after=self.tab_view.group_for_editor(source))
        self.tab_view.add_editor(view, "", group)
        view.setCursorPosition(*source.getCursorPosition())
        self._refresh_document_titles(document)
        return view

    def _detach_document_view(self, view, remember=False, transfer=True):
        """Detach a tab and transfer the sole Ruff synchronizer before retiring its owner."""
        if view not in self.documents.documents:
            return
        document = self.documents.document(view)
        if remember:
            self.documents.remember_closed(view, isinstance(view, PythonEditor))
        others = [item for item in document.views if item is not view]
        controller = getattr(view, "ruff_lsp", None)
        if controller is not None:
            controller.shutdown()
            view.ruff_lsp = None
        self.documents.detach(view)
        # Only one view owns Ruff synchronization for a shared document.
        if transfer and others and controller is not None:
            owner = others[0]
            document.analysis_owner = owner
            owner.ruff_lsp = RuffLspController(owner, self.ruff_lsp_client)
            owner.ruff_lsp.diagnostics_changed.connect(self._on_ruff_diagnostics)
            owner.ruff_lsp.sync_from_editor()

    def _prepare_preview(self, path, group):
        """Replace only an unpinned, clean preview in the requested group."""
        existing = self.tab_view.find_editor_by_path(path)
        if existing is not None:
            return
        for index in range(group.count()):
            view = group.widget(index)
            tab = self.documents.tab(view)
            if tab.preview and not tab.pinned and not self.documents.document(view).dirty:
                self.close_editor(view)
                break

    def _reopen_tab(self):
        """Reopen the latest available disk-backed location without restoring stale widgets."""
        while self.documents.recently_closed:
            item = self.documents.recently_closed.pop(0)
            if item.path.is_file():
                view = self.set_new_tab(item.path, is_python_file=item.python_mode)
                if view:
                    view.setCursorPosition(item.line, item.column)
                break

    def _search_tabs(self):
        """Select from distinct numbered entries even when filenames are duplicated."""
        views = self.tab_view.all_editors()
        labels = [f"{index + 1}: {view.path or 'Untitled'}" for index, view in enumerate(views)]
        if labels:
            selected, accepted = QInputDialog.getItem(self, "Open tabs", "Tab", labels, 0, True)
            if accepted and selected in labels:
                self.tab_view.focus_editor(views[labels.index(selected)])

    def _sort_tabs(self):
        """Reorder the active group's existing tabs, with pinned tabs first."""
        group = self.tab_view.active_group()
        desired = sorted([group.widget(i) for i in range(group.count())],
                         key=lambda view: (not self.documents.tab(view).pinned, str(view.path or '').casefold()))
        for index, view in enumerate(desired):
            group.tabBar().moveTab(group.indexOf(view), index)
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
        self._install_document_tabs()
```



#### Edit `main.py` — `MainWindow._connect_editor`

Attach shared state before textChanged can mark the editor dirty. Keep Topic 5’s optional reference-signal connections further down this method.

Inside this method, find exactly:

```python
        editor.textChanged.connect(lambda ed=editor: self._on_editor_text_changed(ed))
```

Replace only that block with:

```python
        self._attach_document_view(editor)
        editor.textChanged.connect(lambda ed=editor: self._on_editor_text_changed(ed))
```



#### Edit `main.py` — `MainWindow._on_editor_text_changed`

Remove the old single-view title update; it would overwrite pin/preview labels and leave duplicate views inconsistent.

Inside this method, find exactly:

```python
        path = getattr(editor, "path", None)
        base_title = path.name if path is not None else "Untitled"
        self.tab_view.set_editor_title(editor, f"● {base_title}")
```

Replace only that block with:

```python
        # DirtyViews emits stateChanged, which refreshes every view title.
```



#### Replace `main.py` — `MainWindow.mark_editor_clean`

Clean all views of the document after one successful save. Delete this method’s complete current definition, from `def mark_editor_clean(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def mark_editor_clean(self, editor):
        """Mark the shared document clean after a successful save and refresh file colors."""
        if editor is not None:
            self._clean_document(editor)
            if editor.path is not None:
                self.file_manager.check_git_status()
```



#### Replace `main.py` — `MainWindow.set_new_tab`

Add the preview parameter and promote reused previews when opened permanently. Delete this method’s complete current definition, from `def set_new_tab(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def set_new_tab(
            self,
            path: Path,
            is_new_file=False,
            target_group=None,
            is_python_file=None,
            preview=False,
    ):
        """Open one UTF-8 document without corrupting or duplicating it.

        Binary probing, symlink resolution, byte reading, and strict decoding
        are one I/O transaction. Every expected filesystem/encoding failure is
        converted to a user-visible dialog instead of escaping a Qt slot.
        """
        path = Path(path) if path is not None else None
        if is_new_file:
            return self.new_file(target_group=target_group)
        if path is None or not path.is_file():
            return None

        existing = self.tab_view.find_editor_by_path(path)
        if existing is not None:
            if not preview:
                self.documents.tab(existing).preview = False
                self._refresh_document_titles(self.documents.document(existing))
            self.tab_view.focus_editor(existing)
            return existing
        if preview:
            self._prepare_preview(path, target_group or self.tab_view.active_group())
            if target_group not in self.tab_view.groups():
                target_group = None

        try:
            if self.is_binary(path):
                self.statusBar().showMessage("Cannot open binary file", 2_000)
                return None

            # Keep the logical path on the tab, but read/write the target when
            # the logical path is a symlink so saving does not replace the link.
            target = save_target(path)
            raw = target.read_bytes()
            has_bom = raw.startswith(UTF8_BOM)
            text = raw.decode("utf-8-sig")
        except (OSError, UnicodeDecodeError) as error:
            QMessageBox.critical(self, "Open File", f"Could not open '{path}':\n{error}")
            return None

        editor = self.get_editor(path=path, is_python_file=is_python_file)
        editor._utf8_bom = has_bom
        editor._disk_digest = hashlib.sha256(raw).digest()
        editor._save_target = target

        # Preserve the dominant existing EOL convention rather than converting
        # the entire file merely because it was opened and saved.
        crlf_count = raw.count(b"\r\n")
        lf_count = raw.count(b"\n") - crlf_count
        cr_count = raw.count(b"\r") - crlf_count
        if crlf_count >= max(lf_count, cr_count) and crlf_count:
            editor.setEolMode(QsciScintilla.EolWindows)
        elif cr_count > max(crlf_count, lf_count):
            editor.setEolMode(QsciScintilla.EolMac)
        else:
            editor.setEolMode(QsciScintilla.EolUnix)

        editor.setTextSafely(text)
        self._connect_editor(editor)
        self.tab_view.add_editor(editor, path.name, target_group)
        self.documents.tab(editor).preview = preview
        self._refresh_document_titles(self.documents.document(editor))
        self.tab_view.set_editor_tooltip(editor, str(path.absolute()))

        self.current_file = path
        self._add_to_recent_files(str(path))
        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.outline_tree.clear()
        return editor
```



#### Replace `main.py` — `MainWindow.close_editor`

Respect pinning and prompt only when closing the final dirty view. Delete this method’s complete current definition, from `def close_editor(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def close_editor(self, editor):
        """Close unpinned views; prompt once only when the final view is dirty."""
        if editor is None or editor not in self.documents.documents:
            return True
        if self.documents.tab(editor).pinned:
            return True
        document = self.documents.document(editor)
        if document.dirty and len(document.views) == 1:
            self.tab_view.focus_editor(editor)
            name = document.path.name if document.path else "Untitled"
            answer = QMessageBox.question(self, "Unsaved Changes", f"Save changes to '{name}'?",
                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            if answer == QMessageBox.Cancel:
                return False
            if answer == QMessageBox.Save:
                if not self.save_file():
                    return False
                # Save As may replace all views with another editor class.
                editor = self.current_editor()
        self._detach_document_view(editor, remember=True)
        self.tab_view.remove_editor(editor)
        self._dispose_editor(editor)
        self.render_preview()
        return True
```



#### Replace `main.py` — `MainWindow.on_file_rename`

Retarget all views together; editor-mode changes must convert every view. Delete this method’s complete current definition, from `def on_file_rename(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def on_file_rename(self, old_path, new_path, is_directory=False):
        """Retarget each shared document once after a successful file-manager rename."""
        old_path, new_path = Path(old_path).absolute(), Path(new_path).absolute()
        for document in list(self.documents.all()):
            if document.path is None:
                continue
            current = document.path.absolute()
            if current == old_path:
                destination = new_path
            elif is_directory and current.is_relative_to(old_path):
                destination = new_path / current.relative_to(old_path)
            else:
                continue
            editor = document.analysis_owner
            editor._save_target = save_target(destination)
            self._retarget_document(editor, destination)
            wanted = PythonEditor if is_python_path(destination) else MarkdownEditor
            editor = self._convert_editor(editor, wanted)
            if editor is self.current_editor():
                self.current_file = destination
```



#### Replace `main.py` — `MainWindow.can_close_editors_for_path`

Ask once per document before a file-manager operation. Delete this method’s complete current definition, from `def can_close_editors_for_path(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def can_close_editors_for_path(self, target_path, is_directory=False):
        """Gather one save/discard decision per document before a file-manager operation."""
        seen = set()
        for editor in self.editors_for_path(target_path, is_directory):
            document = self.documents.document(editor)
            if document in seen or not document.dirty:
                continue
            seen.add(document)
            self.tab_view.focus_editor(editor)
            name = document.path.name if document.path else "Untitled"
            answer = QMessageBox.question(self, "Unsaved Changes", f"Save changes to '{name}'?",
                      QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save)
            if answer == QMessageBox.Cancel or (answer == QMessageBox.Save and not self.save_file()):
                return False
        return True
```



#### Replace `main.py` — `MainWindow.close_editors_for_path`

Close all affected views after the file-manager operation is confirmed. Delete this method’s complete current definition, from `def close_editors_for_path(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def close_editors_for_path(self, target_path, is_directory=False, prompt=True):
        """Close every view covered by a confirmed file-manager operation."""
        editors = self.editors_for_path(target_path, is_directory)
        if prompt and not self.can_close_editors_for_path(target_path, is_directory):
            return False
        # A save prompt can convert a view or move it to another path.
        editors = self.editors_for_path(target_path, is_directory)
        for editor in editors:
            self._detach_document_view(editor, transfer=False)
            self.tab_view.remove_editor(editor)
            self._dispose_editor(editor)
        return True
```



#### Replace `main.py` — `MainWindow.save_as`

Treat duplicate views as one file owner and preserve the existing save/format workflow. Delete this method’s complete current definition, from `def save_as(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def save_as(self):
        """Save to a user-confirmed path and update the tab's editor type.

        The native file dialog owns the intentional overwrite confirmation.
        The source tab's disk digest belongs to its old path and must never be
        compared with bytes at the new destination.
        """
        editor = self.current_editor()
        if editor is None:
            return False

        file_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save As",
            os.getcwd(),
        )
        if not file_path:
            self.statusBar().showMessage("Cancelled", 2_000)
            return False

        path = Path(file_path)
        owner = self.tab_view.find_editor_by_path(path)
        if owner is not None and self.documents.document(owner) is not self.documents.document(editor):
            QMessageBox.warning(self, "Save As", "That file is already open in another tab.")
            self.tab_view.focus_editor(owner)
            return False

        # The dialog confirmed replacement. Do not compare the destination to
        # the digest of the tab's previous path.
        if not self._save_editor_to_path(editor, path, check_external_change=False):
            return False

        editor.path = path
        editor.full_path = path.absolute()
        self.current_file = path
        self.tab_view.set_editor_tooltip(editor, str(editor.full_path))

        desired_class = PythonEditor if is_python_path(path) else MarkdownEditor
        converted = not isinstance(editor, desired_class)
        if converted:
            editor = self._convert_editor(editor, desired_class)

        if isinstance(editor, PythonEditor):
            # A newly converted PythonEditor was constructed with ``path`` and
            # already owns the correct URI. Only an existing Python editor must
            # migrate its old Ruff URI after Python-to-Python Save As.
            if not converted and editor.ruff_lsp is not None and editor.ruff_lsp.uri != path.resolve().as_uri():
                editor.ruff_lsp.relocate(path)
            editor.auto_completer.file_path = str(editor.full_path)

        self.mark_editor_clean(editor)
        self._add_to_recent_files(str(path))
        self.statusBar().showMessage(f"Saved {path.name}", 2_000)
        return True
```



#### Replace `main.py` — `MainWindow._convert_editor`

Replace all views of a document together and retain one Ruff owner. Delete this method’s complete current definition, from `def _convert_editor(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _convert_editor(self, old, EditorClass):
        """Convert every view of a document while preserving shared text and undo state."""
        if old is None or isinstance(old, EditorClass):
            return old
        document = self.documents.document(old)
        previous_views = list(document.views)
        source_document = old.document()
        owner = document.analysis_owner
        if isinstance(owner, PythonEditor) and owner.ruff_lsp is not None:
            owner.ruff_lsp.shutdown()
            owner.ruff_lsp = None
        current = self.current_editor()
        replacements = {}
        for index, view in enumerate(previous_views):
            group = self.tab_view.group_for_editor(view)
            position = group.indexOf(view)
            tab = self.documents.tab(view)
            if EditorClass is PythonEditor:
                new = PythonEditor(path=document.path, is_python_file=True,
                                   ruff_lsp_client=self.ruff_lsp_client if index == 0 else None)
            else:
                new = MarkdownEditor(path=document.path, is_python_file=False)
            new.setDocument(source_document)
            for name in ("_utf8_bom", "_disk_digest", "_save_target"):
                setattr(new, name, getattr(view, name, None))
            new.setEolMode(view.eolMode())
            new.setReadOnly(document.read_only)
            self.documents.attach(new, document=document)
            self.documents.tabs[new] = tab
            if index == 0:
                document.analysis_owner = new
            self._apply_editor_settings(new, self._current_settings)
            self._connect_editor(new)
            self.tab_view.add_editor(new, "", group)
            group.tabBar().moveTab(group.indexOf(new), position)
            new.setCursorPosition(*view.getCursorPosition())
            if view.hasSelectedText():
                new.setSelection(*view.getSelection())
            new.setFirstVisibleLine(view.firstVisibleLine())
            replacements[view] = new
        for view in previous_views:
            self.documents.detach(view)
            self.tab_view.remove_editor(view)
            self._dispose_editor(view)
        primary = document.analysis_owner
        if isinstance(primary, PythonEditor) and primary.ruff_lsp:
            primary.ruff_lsp.sync_from_editor()
        self._refresh_document_titles(document)
        if current in replacements:
            self.tab_view.focus_editor(replacements[current])
        return replacements[old]
```



#### Replace `main.py` — `MainWindow.save_session`

Store per-view placement, caret, scroll and pin state for saved files. Delete this method’s complete current definition, from `def save_session(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def save_session(self):
        """Persist one file identity with multiple independently positioned view records."""
        if not self.settings.value("restore_tabs", True, type=bool):
            return
        groups = list(self.tab_view.groups())
        views = self.tab_view.all_editors()
        records = []
        active = None
        for view in views:
            document = self.documents.document(view)
            if document.path is None:
                continue
            if view is self.current_editor():
                active = len(records)
            line, column = view.getCursorPosition()
            records.append({"path": str(document.path.absolute()), "python": isinstance(view, PythonEditor),
                            "group": groups.index(self.tab_view.group_for_editor(view)),
                            "line": line, "column": column, "scroll": view.firstVisibleLine(),
                            "pinned": self.documents.tab(view).pinned})
        self.settings.setValue("session", json.dumps({"tabs": records, "active_view": active,
                                                      "python_mode": self.python_editor_active}))
```



#### Replace `main.py` — `MainWindow._restore_session`

Restore a shared buffer once, then recreate its duplicate views. Delete this method’s complete current definition, from `def _restore_session(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _restore_session(self):
        """Restore saved files and duplicate views while retaining one Ruff owner per file."""
        if not self.settings.value("restore_tabs", True, type=bool):
            return
        try:
            session = json.loads(self.settings.value("session", "{}", type=str))
            if not isinstance(session, dict):
                return
            records = session.get("tabs", [])
            if not isinstance(records, list) or len(records) > 100:
                return
        except (ValueError, TypeError):
            return
        opened = {}
        active = None
        for index, item in enumerate(records):
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                continue
            group_number = item.get("group", 0)
            if type(group_number) is not int or not 0 <= group_number < 20:
                continue
            path = Path(item["path"])
            if not path.is_file():
                continue
            while len(self.tab_view.groups()) <= group_number:
                self.tab_view._create_group()
            group = self.tab_view.groups()[group_number]
            key = path.resolve()
            if key in opened:
                view = self._duplicate_view(opened[key], group)
            else:
                view = self.set_new_tab(path, target_group=group, is_python_file=bool(item.get("python", is_python_path(path))))
                if view is not None:
                    opened[key] = view
            if view is None:
                continue
            self.documents.tab(view).pinned = item.get("pinned") is True
            line, column, scroll = (item.get(name, 0) for name in ("line", "column", "scroll"))
            if all(type(value) is int and value >= 0 for value in (line, column, scroll)):
                view.setCursorPosition(min(line, view.lines() - 1), column)
                view.setFirstVisibleLine(scroll)
            self._refresh_document_titles(self.documents.document(view))
            if session.get("active_view") == index or session.get("active") == str(path):
                active = view
        self.python_editor_active = session.get("python_mode") is True
        if active is not None:
            self.tab_view.focus_editor(active)
```



#### Replace `main.py` — `MainWindow._show_tab_context_menu`

Use the clicked tab group for pin, close-right, duplicate and path actions. Delete this method’s complete current definition, from `def _show_tab_context_menu(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def _show_tab_context_menu(self, group, position):
        """Use the clicked group for pin, close-right, path and duplicate operations."""
        bar = group.tabBar()
        index = bar.tabAt(bar.mapFrom(group, position))
        if index < 0:
            return
        view = group.widget(index)
        tab = self.documents.tab(view)
        menu = QMenu(self)
        pin = menu.addAction("Unpin" if tab.pinned else "Pin")
        close = menu.addAction("Close")
        close.setEnabled(not tab.pinned)
        others = menu.addAction("Close Others")
        right = menu.addAction("Close to the Right")
        duplicate = menu.addAction("Duplicate View Right")
        copy = menu.addAction("Copy Path")
        reveal = menu.addAction("Reveal in File Manager")
        selected = menu.exec_(group.mapToGlobal(position))
        if selected is pin:
            tab.pinned, tab.preview = not tab.pinned, False
            self._refresh_document_titles(self.documents.document(view))
        elif selected is close:
            self.close_editor(view)
        elif selected in (others, right):
            targets = self.tab_view.all_editors() if selected is others else [group.widget(i) for i in range(index + 1, group.count())]
            for target in list(targets):
                if target is not view and not self.documents.tab(target).pinned:
                    if self.close_editor(target) is False:
                        break
        elif selected is duplicate:
            self._duplicate_view(view)
        elif selected is copy:
            self._copy_tab_path(view)
        elif selected is reveal:
            self._reveal_tab_in_file_manager(view)
```



#### Edit `main.py` — `MainWindow._dispose_editor`

Detach document ownership before retiring a widget; keep the existing asynchronous worker retirement.

Inside this method, find exactly:

```python
        if isinstance(editor, PythonEditor):
```

Replace only that block with:

```python
        self._detach_document_view(editor, transfer=not getattr(self, "_close_prompts_complete", False))
        if isinstance(editor, PythonEditor):
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

Propagate the successful path and disk digest before marking the shared document clean.

Inside this method, find exactly:

```python
        self.mark_editor_clean(editor)
```

Replace only that block with:

```python
        self._retarget_document(editor, logical_path)
        self.mark_editor_clean(editor)
```



#### Edit `main.py` — `MainWindow.closeEvent`

Ask once per dirty document when closing the application, even when several views share it.

Inside this method, find exactly:

```python
            for editor in list(self.tab_view.all_editors()):
                if editor not in self._dirty_editors:
                    continue
```

Replace only that block with:

```python
            # DirtyViews yields one representative per dirty document.
            for editor in list(self._dirty_editors):
```



#### Edit `side_bar_widgets/file_manager.py` — `FileManager.__init__`

Keep single-click preview opening separate from double-click permanent opening.

Inside this method, find exactly:

```python
        self.clicked.connect(self.tree_view_clicked)
```

Replace only that block with:

```python
        self.clicked.connect(self.tree_view_clicked)
        self.doubleClicked.connect(self._open_permanent)
```



#### Replace `side_bar_widgets/file_manager.py` — `FileManager.tree_view_clicked`

Single clicks create replaceable previews. Delete this method’s complete current definition, from `def tree_view_clicked(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def tree_view_clicked(self, index: QModelIndex):
        """Open a file as a replaceable clean preview; leave directory navigation to the tree."""
        path = self.model.filePath(index)
        p = Path(path)
        if p.is_file():
            self.set_new_tab(p, preview=True)
```



#### Add methods to `side_bar_widgets/file_manager.py` — `FileManager`

Double clicks promote the existing preview instead of duplicating its document. Insert the following **after the complete `FileManager.tree_view_clicked` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _open_permanent(self, index):
        """Promote a double-clicked file to a permanent tab using the existing open workflow."""
        path = Path(self.model.filePath(index))
        if path.is_file():
            self.set_new_tab(path, preview=False)
```



**Use this topic:** Run `python main.py`, open a file and choose **Tabs → Duplicate View Right**. Edits appear in both views; caret and scroll remain independent. The tab context menu provides Pin and close actions. A file-tree single click opens a preview; editing or double-clicking makes it permanent.


<a id="topic-7"></a>
## 7. External File and Directory Watching

### Topic explanation

File watching detects when another program modifies, replaces, deletes or recreates an open file. A clean buffer can reload from disk; a dirty buffer keeps its contents and asks what to do before overwriting external changes.

FileWatchService watches logical files and their parent directories, rearms watches after atomic replacement, and reads snapshots in background workers. MainWindow accepts a snapshot only if its captured document revision and disk digest still match. The same bytes supply both the hash and reloaded text. Compare opens a side-by-side dialog; reload, overwrite and cancel are separate choices. This watches open documents and refreshes the existing Git service; it is not a recursive watcher for every workspace file.


**Documentation used for this topic:**

- [`QFileSystemWatcher`](https://doc.qt.io/archives/qt-5.15/qfilesystemwatcher.html)
- [`QFileInfo`](https://doc.qt.io/archives/qt-5.15/qfileinfo.html)
- [`os.stat`](https://docs.python.org/3/library/os.html#os.stat)
- [`QTimer`](https://doc.qt.io/archives/qt-5.15/qtimer.html)
- [`pathlib`](https://docs.python.org/3/library/pathlib.html)
- [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor)
- [Hashing](https://docs.python.org/3/library/hashlib.html)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `code_inteligence/file_watch_service.py`

**Folder:** `code_inteligence/` already exists. **File:** `file_watch_service.py`. Paste the complete code below starting at line 1.

```python
"""Coalesce file hints, rearm atomic replacements, and read disk snapshots off-thread."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
from PyQt5.QtCore import QObject, QFileSystemWatcher, QTimer, Qt, pyqtSignal


class FileWatchService(QObject):
    """Watch explicit files and parents; deliver immutable disk data on the GUI thread."""
    hints = pyqtSignal(list)
    result = pyqtSignal(object, object, object, object, object)
    _ready = pyqtSignal(object, object, object)

    def __init__(self, parent=None):
        """Create one reader pool and a burst-coalescing timer with owned lifetime."""
        super().__init__(parent)
        self.watcher = QFileSystemWatcher(self)
        self.files, self.pending, self.futures = set(), set(), set()
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="file-watch")
        self.closed = False
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self._flush)
        self.watcher.fileChanged.connect(self._hint)
        self.watcher.directoryChanged.connect(self._hint)
        self._ready.connect(self._receive, Qt.QueuedConnection)

    def watch_file(self, path):
        """Track the logical path plus its resolved target and both parent folders."""
        logical = Path(path).absolute()
        self.files.update((logical, logical.resolve()))
        for item in (logical, logical.resolve()):
            if str(item.parent) not in self.watcher.directories():
                self.watcher.addPath(str(item.parent))
            if item.is_file() and str(item) not in self.watcher.files():
                self.watcher.addPath(str(item))

    def retain(self, paths):
        """Drop watches not used by any open document, preserving shared parents."""
        wanted = set()
        for path in paths:
            logical = Path(path).absolute()
            wanted.update((logical, logical.resolve()))
        for raw in self.watcher.files():
            if Path(raw) not in wanted:
                self.watcher.removePath(raw)
        parents = {str(p.parent) for p in wanted}
        for raw in self.watcher.directories():
            if raw not in parents:
                self.watcher.removePath(raw)
        self.files = wanted
        for path in wanted:
            self.watch_file(path)

    def _hint(self, raw):
        """Collect affected known files; directory events also catch file recreation."""
        path = Path(raw)
        self.pending.update(p for p in self.files if p == path or p.parent == path)
        self.timer.start()

    def _flush(self):
        """Rearm lost file watches and ask the owner for current document tokens."""
        paths, self.pending = sorted(self.pending), set()
        for path in paths:
            if path.is_file() and str(path) not in self.watcher.files():
                self.watcher.addPath(str(path))
        if paths:
            self.hints.emit(paths)

    @staticmethod
    def _read(path):
        """Read and hash the same byte snapshot, returning failures as data."""
        try:
            raw = path.read_bytes()
            return raw, hashlib.sha256(raw).digest(), None
        except OSError as error:
            return None, None, str(error)

    def probe(self, path, token):
        """Capture a revision token without letting worker code touch any widget."""
        if self.closed:
            return
        path = Path(path)
        future = self.pool.submit(self._read, path)
        self.futures.add(future)
        future.add_done_callback(lambda done: self._ready.emit(path, token, done))

    def _receive(self, path, token, future):
        """Drain worker ownership and deliver completed snapshots unless closing."""
        self.futures.discard(future)
        if not self.closed and not future.cancelled():
            raw, digest, error = future.result()
            self.result.emit(path, token, raw, digest, error)

    def shutdown(self):
        """Stop hints and pending reads without destroying running worker ownership."""
        self.closed = True
        self.timer.stop()
        self.pool.shutdown(wait=False, cancel_futures=True)

    def is_running(self):
        """Keep MainWindow alive until all queued completion signals are drained."""
        return bool(self.futures)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `FileWatchService` | Watch explicit files and parents; deliver immutable disk data on the GUI thread. |
| `FileWatchService.__init__` | Create one reader pool and a burst-coalescing timer with owned lifetime. |
| `FileWatchService.watch_file` | Track the logical path plus its resolved target and both parent folders. |
| `FileWatchService.retain` | Drop watches not used by any open document, preserving shared parents. |
| `FileWatchService._hint` | Collect affected known files; directory events also catch file recreation. |
| `FileWatchService._flush` | Rearm lost file watches and ask the owner for current document tokens. |
| `FileWatchService._read` | Read and hash the same byte snapshot, returning failures as data. |
| `FileWatchService.probe` | Capture a revision token without letting worker code touch any widget. |
| `FileWatchService._receive` | Drain worker ownership and deliver completed snapshots unless closing. |
| `FileWatchService.shutdown` | Stop hints and pending reads without destroying running worker ownership. |
| `FileWatchService.is_running` | Keep MainWindow alive until all queued completion signals are drained. |


#### Create `side_bar_widgets/comparison_dialog.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `comparison_dialog.py`. Paste the complete code below starting at line 1.

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

**Required first:** Topic 6. No other topic is required.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.file_watch_service import FileWatchService
```



#### Add methods to `main.py` — `MainWindow`

These methods compare a captured revision/digest against the live document before replacing text. Optional snippet cleanup runs only when Topic 8 is present. Insert the following **after the complete `MainWindow._save_editor_to_path` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_file_watching(self):
        """Watch saved document paths and receive immutable disk snapshots on the GUI thread."""
        self.file_watcher = FileWatchService(self)
        self.file_watcher.hints.connect(self._on_disk_hints)
        self.file_watcher.result.connect(self._on_disk_result)
        # This also covers any documents already attached before installation.
        self.file_watcher.retain([doc.path for doc in self.documents.all() if doc.path])

    def _on_disk_hints(self, paths):
        """Read affected documents with revision tokens and refresh the existing Git service."""
        for document in self.documents.all():
            if document.path and any(p.resolve() == document.path.resolve() for p in paths):
                self.file_watcher.probe(document.path, (document, document.revision, document.disk_digest))
        self._refresh_git_state()

    def _on_disk_result(self, path, token, raw, digest, error):
        """Ignore obsolete snapshots; reload clean documents and flag dirty/deleted ones."""
        document, revision, expected = token
        if document not in self.documents.all() or document.revision != revision or document.disk_digest != expected:
            return
        if digest == document.disk_digest and error is None:
            return  # Delayed notification from our own successful atomic save.
        if error or document.dirty:
            document.externally_changed = True
            self.documents.stateChanged.emit(document)
            return
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeError:
            document.externally_changed = True
            self.documents.stateChanged.emit(document)
            return
        views = list(document.views)
        positions = {view: (view.getCursorPosition(), view.firstVisibleLine()) for view in views}
        for view in views:
            view._loading_text = True
            if hasattr(view, "snippets"):
                view.snippets.cancel()
        owner = document.analysis_owner
        try:
            owner.setText(text)
            for view in views:
                view._utf8_bom = raw.startswith(b"\xef\xbb\xbf")
                view._disk_digest = digest
                view.setEolMode(QsciScintilla.EolWindows if b"\r\n" in raw else QsciScintilla.EolMac if b"\r" in raw else QsciScintilla.EolUnix)
                cursor, scroll = positions[view]
                view.setCursorPosition(*cursor)
                view.setFirstVisibleLine(scroll)
        finally:
            for view in views:
                view._loading_text = False
        if isinstance(owner, PythonEditor) and owner.ruff_lsp:
            owner.ruff_lsp.sync_from_editor()
        self._clean_document(owner)

    def _resolve_external(self, editor, raw):
        """Require an explicit overwrite, reload, compare or cancel decision before saving."""
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeError as error:
            QMessageBox.warning(self, "External change", str(error))
            return False
        box = QMessageBox(self)
        box.setWindowTitle("File changed on disk")
        box.setText("The file contains changes made outside the editor.")
        reload = box.addButton("Reload disk", QMessageBox.AcceptRole)
        keep = box.addButton("Overwrite with editor", QMessageBox.DestructiveRole)
        compare = box.addButton("Compare", QMessageBox.ActionRole)
        box.addButton(QMessageBox.Cancel)
        box.exec_()
        chosen = box.clickedButton()
        if chosen is keep:
            return True
        if chosen is compare:
            from side_bar_widgets.comparison_dialog import ComparisonDialog
            ComparisonDialog(editor.text(), text, "Editor versus disk", self,
                             accept_text="Close comparison").exec_()
        elif chosen is reload:
            document = self.documents.document(editor)
            views = list(document.views)
            for view in views:
                view._loading_text = True
                if hasattr(view, "snippets"):
                    view.snippets.cancel()
            try:
                editor.setText(text)
                for view in views:
                    view._utf8_bom = raw.startswith(b"\xef\xbb\xbf")
                    view._disk_digest = hashlib.sha256(raw).digest()
                    view.setEolMode(QsciScintilla.EolWindows if b"\r\n" in raw else QsciScintilla.EolMac if b"\r" in raw else QsciScintilla.EolUnix)
            finally:
                for view in views:
                    view._loading_text = False
            self._clean_document(editor)
            owner = document.analysis_owner
            if isinstance(owner, PythonEditor) and owner.ruff_lsp:
                owner.ruff_lsp.sync_from_editor()
        return False
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
        self._install_file_watching()
```



#### Edit `main.py` — `MainWindow._attach_document_view`

Begin watching every saved file when its first or duplicate view is attached.

Inside this method, find exactly:

```python
            editor.setReadOnly(document.read_only)
```

Replace only that block with:

```python
            editor.setReadOnly(document.read_only)
            self.file_watcher.watch_file(document.path)
```



#### Edit `main.py` — `MainWindow._retarget_document`

Update watched logical paths after Save As or rename.

Inside this method, find exactly:

```python
        self._refresh_document_titles(document)
```

Replace only that block with:

```python
        self.file_watcher.retain([doc.path for doc in self.documents.all() if doc.path])
        self._refresh_document_titles(document)
```



#### Edit `main.py` — `MainWindow._detach_document_view`

Release obsolete watches after document closure.

Inside this method, find exactly:

```python
            owner.ruff_lsp.sync_from_editor()
```

Replace only that block with:

```python
            owner.ruff_lsp.sync_from_editor()
        self.file_watcher.retain([doc.path for doc in self.documents.all() if doc.path])
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

Hash the same bytes that the conflict dialog will display; avoid reading two different disk versions.

Inside this method, find exactly:

```python
                actual = disk_digest(target)
```

Replace only that block with:

```python
                external_bytes = target.read_bytes()
                actual = hashlib.sha256(external_bytes).digest()
```



#### Edit `main.py` — `MainWindow._save_editor_to_path`

Replace the old yes/cancel prompt with explicit reload, overwrite, compare and cancel actions.

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
                if not self._resolve_external(editor, external_bytes):
                    return False
```



#### Edit `main.py` — `MainWindow._background_work_running`

Keep the application alive until pending disk reads have drained.

Inside this method, find exactly:

```python
        git_worker = getattr(
```

Replace only that block with:

```python
        if self.file_watcher.is_running():
            return True
        git_worker = getattr(
```



#### Edit `main.py` — `MainWindow.closeEvent`

Stop watcher work before the existing background-shutdown wait loop.

Inside this method, find exactly:

```python
        self.terminal.stop()
```

Replace only that block with:

```python
        self.file_watcher.shutdown()
        self.terminal.stop()
```



**Use this topic:** Run `python main.py` after Topic 6. Open a saved file and modify it using another program. Clean buffers reload; dirty buffers show an external-change marker. Save a dirty buffer to choose reload, overwrite, compare or cancel.


<a id="topic-8"></a>
## 8. Snippets and Reusable Templates

### Topic explanation

A snippet inserts reusable text with numbered editable placeholders. A template creates a new document of the appropriate language and inserts a snippet into it. Tab and Shift+Tab move between placeholders; Escape ends snippet navigation.

The parser turns the supported placeholder syntax into plain text plus ranges. SnippetController tracks those ranges in the editor and cancels navigation when edits invalidate them. SnippetCatalog provides the built-in Python and Markdown examples. MainWindow exposes insertion and template actions, and enables insertion only for the active language and a writable editor.


**Documentation used for this topic:**

- [`QsciScintilla`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)
- [`QKeyEvent`](https://doc.qt.io/archives/qt-5.15/qkeyevent.html)
- [`QStandardPaths`](https://doc.qt.io/archives/qt-5.15/qstandardpaths.html)
- [`json`](https://docs.python.org/3/library/json.html)
- [Scintilla modification notifications](https://www.scintilla.org/ScintillaDoc.html#SCN_MODIFIED)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `code_inteligence/snippet_parser.py`

**Folder:** `code_inteligence/` already exists. **File:** `snippet_parser.py`. Paste the complete code below starting at line 1.

```python
"""Parse the supported `${number:default}` snippet syntax."""

from dataclasses import dataclass
import re


_PLACEHOLDER = re.compile(r"\$\{([0-9]+):([^}]*)\}")


@dataclass(frozen=True)
class Placeholder:
    """One editable half-open character range in rendered snippet text."""

    number: int
    start: int
    end: int


@dataclass(frozen=True)
class ParsedSnippet:
    """Marker-free insertion text and its ordered placeholder ranges."""

    text: str
    placeholders: tuple[Placeholder, ...]


def parse_snippet(source: str) -> ParsedSnippet:
    """Remove markers and calculate spans against the resulting Unicode text."""
    chunks: list[str] = []
    placeholders: list[Placeholder] = []
    rendered_length = 0
    source_end = 0

    for match in _PLACEHOLDER.finditer(source):
        literal = source[source_end:match.start()]
        default = match.group(2)
        chunks.extend((literal, default))
        rendered_length += len(literal)
        start = rendered_length
        rendered_length += len(default)
        placeholders.append(Placeholder(int(match.group(1)), start, rendered_length))
        source_end = match.end()

    chunks.append(source[source_end:])
    placeholders.sort(key=lambda item: (item.number == 0, item.number, item.start))
    return ParsedSnippet("".join(chunks), tuple(placeholders))
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Placeholder` | One editable half-open character range in rendered snippet text. |
| `ParsedSnippet` | Marker-free insertion text and its ordered placeholder ranges. |
| `parse_snippet` | Remove markers and calculate spans against the resulting Unicode text. |


#### Create `code_inteligence/snippet_controller.py`

**Folder:** `code_inteligence/` already exists. **File:** `snippet_controller.py`. Paste the complete code below starting at line 1.

```python
"""Maintain snippet fields in absolute UTF-8 byte coordinates."""
from PyQt5.QtCore import QObject
from code_inteligence.snippet_parser import Placeholder, parse_snippet


class SnippetController(QObject):
    """Navigate supported fields and cancel on edits outside the active field."""

    def __init__(self, editor):
        """Observe modification positions rather than guessing from total text length."""
        super().__init__(editor)
        self.editor = editor
        self.spans = []
        self.index = -1
        self.inserting = False
        editor.SCN_MODIFIED.connect(self._modified)

    @property
    def active(self):
        """Return whether a field is currently available for Tab navigation."""
        return 0 <= self.index < len(self.spans)

    def cancel(self):
        """Forget navigation ranges while retaining all inserted text."""
        self.spans = []
        self.index = -1

    def insert(self, source):
        """Replace the selection once and convert character fields to byte ranges."""
        if self.editor.isReadOnly():
            return
        parsed = parse_snippet(source)
        editor = self.editor
        start = min(editor.SendScintilla(editor.SCI_GETANCHOR), editor.SendScintilla(editor.SCI_GETCURRENTPOS))
        self.cancel()
        self.inserting = True
        editor.beginUndoAction()
        try:
            editor.replaceSelectedText(parsed.text)
        finally:
            editor.endUndoAction()
            self.inserting = False
        self.spans = [Placeholder(field.number, start + len(parsed.text[:field.start].encode("utf-8")),
                                  start + len(parsed.text[:field.end].encode("utf-8")))
                      for field in parsed.placeholders]
        self.index = 0 if self.spans else -1
        self._select_active()

    def _modified(self, position, kind, text, length, *unused):
        """Update fields by actual edit position; reject edits outside the active field."""
        if self.inserting or not self.active or not (kind & 3):
            return
        field = self.spans[self.index]
        deleted = length if kind & 2 else 0
        if position < field.start or position + deleted > field.end:
            self.cancel()
            return
        delta = -length if kind & 2 else length
        old_end = field.end
        self.spans[self.index] = Placeholder(field.number, field.start, field.end + delta)
        # Numeric navigation order is not spatial order: compare byte positions.
        for index, other in enumerate(self.spans):
            if index != self.index and other.start >= old_end:
                self.spans[index] = Placeholder(other.number, other.start + delta, other.end + delta)

    def handle_tab(self, backwards=False):
        """Move to the previous/next field, or finish after the final field."""
        if not self.active:
            return False
        self.index += -1 if backwards else 1
        if not self.active:
            self.cancel()
        else:
            self._select_active()
        return True

    def _select_active(self):
        """Select the active byte span through QScintilla's Unicode-aware conversion."""
        if self.active:
            field = self.spans[self.index]
            self.editor.setSelection(*self.editor.lineIndexFromPosition(field.start),
                                     *self.editor.lineIndexFromPosition(field.end))
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `SnippetController` | Navigate supported fields and cancel on edits outside the active field. |
| `SnippetController.__init__` | Observe modification positions rather than guessing from total text length. |
| `SnippetController.active` | Return whether a field is currently available for Tab navigation. |
| `SnippetController.cancel` | Forget navigation ranges while retaining all inserted text. |
| `SnippetController.insert` | Replace the selection once and convert character fields to byte ranges. |
| `SnippetController._modified` | Update fields by actual edit position; reject edits outside the active field. |
| `SnippetController.handle_tab` | Move to the previous/next field, or finish after the final field. |
| `SnippetController._select_active` | Select the active byte span through QScintilla's Unicode-aware conversion. |


#### Create `code_inteligence/snippet_catalog.py`

**Folder:** `code_inteligence/` already exists. **File:** `snippet_catalog.py`. Paste the complete code below starting at line 1.

```python
"""Small built-in catalog; later merge a validated user JSON file into it."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Snippet:
    """Named insertion available to the palette and editor menu."""

    identifier: str
    title: str
    languages: tuple[str, ...]
    body: str


class SnippetCatalog:
    """Query immutable snippets by editor language."""

    def __init__(self) -> None:
        """Create immutable built-in Markdown and Python snippets with numbered fields."""
        self._items = (
            Snippet("markdown.link", "Markdown: Link", ("markdown",), "[${1:label}](${2:url})"),
            Snippet("markdown.image", "Markdown: Image", ("markdown",),
                    "![${1:alt text}](${2:image path})"),
            Snippet("markdown.table", "Markdown: Table", ("markdown",),
                    "| ${1:Column A} | ${2:Column B} |\n| --- | --- |\n| ${3:value} | ${4:value} |"),
            Snippet("markdown.frontmatter", "Markdown: Front Matter", ("markdown",),
                    "---\ntitle: ${1:title}\ndate: ${2:date}\n---\n\n${0:body}"),
            Snippet("markdown.fence", "Markdown: Fenced Code", ("markdown",),
                    "\u0060\u0060\u0060 ${1:language}\n${0:code}\n\u0060\u0060\u0060"),
            Snippet("markdown.admonition", "Markdown: Admonition", ("markdown",),
                    "> [!${1:NOTE}]\n> ${0:text}"),
            Snippet("python.function", "Python: Function", ("python",),
                    "def ${1:name}(${2:arguments}):\n    \"\"\"${3:summary}\"\"\"\n    ${0:pass}"),
            Snippet("python.class", "Python: Class", ("python",),
                    "class ${1:Name}:\n    \"\"\"${2:Summary}.\"\"\"\n\n    ${0:pass}"),
            Snippet("python.docstring", "Python: Docstring", ("python",),
                    "\"\"\"${1:Summary}.\n\n${2:Details}\n\"\"\""),
            Snippet("python.main", "Python: Main Guard", ("python",),
                    "if __name__ == \"__main__\":\n    ${0:main()}"),
        )

    def for_language(self, language: str) -> tuple[Snippet, ...]:
        """Return snippets whose declared language matches exactly."""
        return tuple(item for item in self._items if language in item.languages)

    def all(self):
        """Expose the immutable built-in catalog to menus without private-field access."""
        return self._items
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `Snippet` | Named insertion available to the palette and editor menu. |
| `SnippetCatalog` | Query immutable snippets by editor language. |
| `SnippetCatalog.__init__` | Create immutable built-in Markdown and Python snippets with numbered fields. |
| `SnippetCatalog.for_language` | Return snippets whose declared language matches exactly. |
| `SnippetCatalog.all` | Expose the immutable built-in catalog to menus without private-field access. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `main.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.snippet_catalog import SnippetCatalog
```



#### Imports in `markdown_editor/markdowneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.snippet_controller import SnippetController
```



#### Edit `markdown_editor/markdowneditor.py` — `MarkdownEditor.__init__`

Create the per-view snippet controller after the existing editor settings.

Inside this method, find exactly:

```python
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)
```

Replace only that block with:

```python
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)

        self.snippets = SnippetController(self)
```



#### Replace `markdown_editor/markdowneditor.py` — `MarkdownEditor.keyPressEvent`

Handle Tab, Shift+Tab and Escape for an active snippet before the existing key behavior. Delete this method’s complete current definition, from `def keyPressEvent(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Consume active snippet navigation keys, then preserve existing completion and editing behavior."""
        if event.key() == Qt.Key_Tab and self.snippets.handle_tab(False):
            return
        if event.key() == Qt.Key_Backtab and self.snippets.handle_tab(True):
            return
        if event.key() == Qt.Key_Escape and self.snippets.active:
            self.snippets.cancel()
            return
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Space:
            self.autoCompleteFromAll()
        else:
            return super().keyPressEvent(event)
```



#### Edit `markdown_editor/markdowneditor.py` — `MarkdownEditor.shutdown`

Cancel placeholder navigation before the view is retired.

Inside this method, find exactly:

```python
        self._shutting_down = True
```

Replace only that block with:

```python
        self.snippets.cancel()
        self._shutting_down = True
```



#### Imports in `python_editor/pythoneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.snippet_controller import SnippetController
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Create the per-view snippet controller after the existing editor settings.

Inside this method, find exactly:

```python
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()
```

Replace only that block with:

```python
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()

        self.snippets = SnippetController(self)
```



#### Replace `python_editor/pythoneditor.py` — `PythonEditor.keyPressEvent`

Handle Tab, Shift+Tab and Escape for an active snippet before the existing key behavior. Delete this method’s complete current definition, from `def keyPressEvent(` to immediately before the next method at the same indentation. Paste this replacement at the same class indentation. Preserve all other methods.

```python
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle editor shortcuts, indentation, and signature scheduling."""
        # Do this before early returns for completion acceptance/indentation.
        if event.key() == Qt.Key_Tab and self.snippets.handle_tab(False):
            return
        if event.key() == Qt.Key_Backtab and self.snippets.handle_tab(True):
            return
        if event.key() == Qt.Key_Escape and self.snippets.active:
            self.snippets.cancel()
            return
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
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.shutdown`

Cancel placeholder navigation before the view is retired.

Inside this method, find exactly:

```python
        if self._shutting_down:
```

Replace only that block with:

```python
        self.snippets.cancel()
        if self._shutting_down:
```



#### Add methods to `main.py` — `MainWindow`

The insert actions use the current view; templates create a new editor of the required language. Insert the following **after the complete `MainWindow.new_file` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_snippets(self):
        """Expose language-aware snippet insertion and new-document templates."""
        self.snippet_catalog = SnippetCatalog()
        self.snippet_actions = []
        menu = self.menuBar().addMenu("Snippets")
        insert_menu = menu.addMenu("Insert Snippet")
        template_menu = menu.addMenu("New From Template")
        for snippet in self.snippet_catalog.all():
            action = insert_menu.addAction(snippet.title)
            action.setObjectName("snippet." + snippet.identifier)
            # Bind the current item now; a bare loop variable would use the last item.
            action.triggered.connect(lambda checked=False, item=snippet: self._insert_snippet(item))
            self.snippet_actions.append((action, snippet))
            template = template_menu.addAction(snippet.title)
            template.setObjectName("template." + snippet.identifier)
            template.triggered.connect(lambda checked=False, item=snippet: self._insert_snippet(item, new=True))
        self._update_snippet_actions(self.current_editor())

    def _insert_snippet(self, snippet, new=False):
        """Insert into the active editor or create an unsaved template of the right type."""
        if new:
            previous = self.python_editor_active
            self.python_editor_active = "python" in snippet.languages
            try:
                editor = self.new_file()
            finally:
                self.python_editor_active = previous
        else:
            editor = self.current_editor()
        language = "python" if isinstance(editor, PythonEditor) else "markdown"
        if editor is not None and language in snippet.languages:
            editor.snippets.insert(snippet.body)

    def _update_snippet_actions(self, editor):
        """Update language-specific command enablement for the selected view."""
        language = "python" if isinstance(editor, PythonEditor) else "markdown"
        for action, snippet in self.snippet_actions:
            action.setEnabled(editor is not None and not editor.isReadOnly() and language in snippet.languages)
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
        self._install_snippets()
```



#### Edit `main.py` — `MainWindow._on_current_editor_changed`

Update the menu for the current language while remaining safe during initial UI construction.

Inside this method, find exactly:

```python
        if editor is None:
```

Replace only that block with:

```python
        if hasattr(self, "snippet_actions"):
            self._update_snippet_actions(editor)
        if editor is None:
```



**Use this topic:** Run `python main.py` and use **Snippets → Insert Snippet** in a matching Python or Markdown editor. Tab and Shift+Tab navigate placeholders. **Snippets → New From Template** creates a new unsaved document.


<a id="topic-9"></a>
## 9. Code Folding

### Topic explanation

Code folding collapses structured regions so you can focus on the surrounding document. Python uses indentation-aware fold regions; Markdown uses headings and fenced blocks.

The pure fold model calculates depth and header flags. FoldingController debounces text changes and writes the resulting levels into QScintilla. MainWindow’s commands operate on the active view. Fold All and Unfold All explicitly check each header’s expanded state instead of misusing foldAll’s children flag. A lexer/theme replacement invalidates cached fold metadata so it is reapplied.


**Documentation used for this topic:**

- [Folding](https://www.scintilla.org/ScintillaDoc.html#Folding)
- [`setFolding()`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)
- [`tokenize`](https://docs.python.org/3/library/tokenize.html)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `code_inteligence/fold_model.py`

**Folder:** `code_inteligence/` already exists. **File:** `fold_model.py`. Paste the complete code below starting at line 1.

```python
"""Pure fold-level models for incomplete Python and Markdown documents."""

from dataclasses import dataclass
from io import StringIO
import re
import tokenize


_PYTHON_HEADER = re.compile(
    r"^(?:async\s+def|def|class|if|elif|else|for|while|try|except|finally|with|match|case)\b.*:\s*(?:#.*)?$"
)
_ATX_HEADING = re.compile(r"^(#{1,6})\s+")
_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
_LIST_ITEM = re.compile(r"^(\s*)(?:[-+*]|[0-9]+[.)])\s+")
_BLOCKQUOTE = re.compile(r"^\s*((?:>\s*)+)")


@dataclass(frozen=True)
class FoldLine:
    """Fold depth and whether a line opens a collapsible region."""

    depth: int
    header: bool = False


def _indent_columns(line: str) -> int:
    """Expand leading tabs to Python-compatible eight-column boundaries."""
    width = 0
    for character in line:
        if character == " ":
            width += 1
        elif character == "\t":
            width += 8 - width % 8
        else:
            break
    return width


def python_fold_lines(text: str) -> list[FoldLine]:
    """Infer resilient indentation folds without requiring valid Python syntax."""
    lines = text.splitlines() or [""]
    significant = [index for index, line in enumerate(lines) if line.strip()]
    next_significant = {
        current: following for current, following in zip(significant, significant[1:])
    }
    indents = [_indent_columns(line) for line in lines]
    indentation_stack = [0]
    result: list[FoldLine] = []

    for index, line in enumerate(lines):
        if line.strip():
            indent = indents[index]
            while len(indentation_stack) > 1 and indent < indentation_stack[-1]:
                indentation_stack.pop()
            if indent > indentation_stack[-1]:
                indentation_stack.append(indent)
            depth = len(indentation_stack) - 1
        else:
            depth = result[-1].depth if result else 0

        following = next_significant.get(index)
        stripped = line.strip()
        header = bool(
            following is not None
            and indents[following] > indents[index]
            and _PYTHON_HEADER.match(stripped)
        )
        result.append(FoldLine(depth, header))
    # A complete multiline string is a useful fold even when indentation does
    # not change. Tokenization may fail for temporarily incomplete source, so
    # preserve the resilient indentation result when it does.
    try:
        for token in tokenize.generate_tokens(StringIO(text).readline):
            start = token.start[0] - 1
            end = token.end[0] - 1
            if token.type != tokenize.STRING or start >= end:
                continue
            base_depth = result[start].depth
            result[start] = FoldLine(base_depth, True)
            for line_number in range(start + 1, min(end + 1, len(result))):
                current = result[line_number]
                result[line_number] = FoldLine(
                    max(current.depth, base_depth + 1), current.header
                )
    except (tokenize.TokenError, IndentationError):
        pass
    return result


def markdown_fold_lines(text: str) -> list[FoldLine]:
    """Calculate heading hierarchy and fenced-block folds for Markdown."""
    lines = text.splitlines() or [""]
    heading_stack: list[int] = []
    active_fence: str | None = None
    fence_depth = 0
    previous_list_level = 0
    previous_quote_depth = 0
    fence_length = 0
    result: list[FoldLine] = []
    following = [""] * len(lines)
    next_text = ""
    for number in range(len(lines) - 1, -1, -1):
        following[number] = next_text
        if lines[number].strip():
            next_text = lines[number]

    def next_significant(index: int) -> str:
        """Return the precomputed next nonblank line in constant time."""
        return following[index]

    for index, line in enumerate(lines):
        fence_match = _FENCE.match(line)
        if active_fence is not None:
            is_close = bool(fence_match and fence_match.group(1)[0] == active_fence
                            and len(fence_match.group(1)) >= fence_length
                            and not line[fence_match.end():].strip())
            result.append(FoldLine(fence_depth + (0 if is_close else 1), False))
            if is_close:
                active_fence = None
            continue

        heading = _ATX_HEADING.match(line)
        if heading:
            rank = len(heading.group(1))
            while heading_stack and heading_stack[-1] >= rank:
                heading_stack.pop()
            depth = len(heading_stack)
            heading_stack.append(rank)
            result.append(FoldLine(depth, True))
            previous_list_level = 0
            previous_quote_depth = 0
            continue

        depth = len(heading_stack)
        if fence_match:
            active_fence = fence_match.group(1)[0]
            fence_length = len(fence_match.group(1))
            fence_depth = depth
            result.append(FoldLine(depth, True))
            previous_list_level = 0
            previous_quote_depth = 0
            continue

        quote = _BLOCKQUOTE.match(line)
        if quote:
            quote_depth = quote.group(1).count(">")
            starts_nested_block = quote_depth > previous_quote_depth
            following_quote = _BLOCKQUOTE.match(next_significant(index))
            following_depth = following_quote.group(1).count(">") if following_quote else 0
            quote_level = quote_depth - 1 if starts_nested_block else quote_depth
            result.append(FoldLine(
                depth + quote_level,
                starts_nested_block and following_depth >= quote_depth,
            ))
            previous_quote_depth = quote_depth
            previous_list_level = 0
            continue

        list_item = _LIST_ITEM.match(line)
        if list_item:
            # Two indentation columns form one visual nesting level here. This
            # is an editor policy, not part of the CommonMark specification.
            list_level = len(list_item.group(1).expandtabs(2)) // 2 + 1
            starts_nested_list = list_level > previous_list_level
            following_item = _LIST_ITEM.match(next_significant(index))
            following_level = (
                len(following_item.group(1).expandtabs(2)) // 2 + 1
                if following_item else 0
            )
            result.append(FoldLine(
                depth + (list_level - 1 if starts_nested_list else list_level),
                starts_nested_list and following_level >= list_level,
            ))
            previous_list_level = list_level
            previous_quote_depth = 0
            continue

        result.append(FoldLine(depth, False))
        if not line.strip():
            previous_list_level = 0
            previous_quote_depth = 0
    return result
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `FoldLine` | Fold depth and whether a line opens a collapsible region. |
| `_indent_columns` | Expand leading tabs to Python-compatible eight-column boundaries. |
| `python_fold_lines` | Infer resilient indentation folds without requiring valid Python syntax. |
| `markdown_fold_lines` | Calculate heading hierarchy and fenced-block folds for Markdown. |
| `markdown_fold_lines.next_significant` | Return the precomputed next nonblank line in constant time. |


#### Create `code_inteligence/folding_controller.py`

**Folder:** `code_inteligence/` already exists. **File:** `folding_controller.py`. Paste the complete code below starting at line 1.

```python
"""Debounce and apply pure fold models to QScintilla."""

import hashlib

from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QObject, QTimer

from code_inteligence.fold_model import markdown_fold_lines, python_fold_lines


SCI_SETFOLDLEVEL = 2222
SC_FOLDLEVELBASE = 0x400
SC_FOLDLEVELHEADERFLAG = 0x2000


class FoldingController(QObject):
    """Own folding configuration and incremental scheduling for one editor."""

    def __init__(self, editor, language: str, margin: int = 2) -> None:
        """Configure the folding margin and debounce model recalculation after text changes."""
        super().__init__(editor)
        self.editor = editor
        self.language = language
        self._last_digest = b""
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(180)
        self._timer.timeout.connect(self.recalculate)
        self.editor.setFolding(QsciScintilla.BoxedTreeFoldStyle, margin)
        self.editor.textChanged.connect(self.schedule)
        self.schedule()

    def schedule(self) -> None:
        """Restart the short quiet-period timer after an edit."""
        self._timer.start()

    def recalculate(self) -> None:
        """Compute and publish fold metadata when document text changed."""
        text = self.editor.text()
        digest = hashlib.blake2b(text.encode("utf-8"), digest_size=16).digest()
        if digest == self._last_digest:
            return
        self._last_digest = digest
        model = python_fold_lines(text) if self.language == "python" else markdown_fold_lines(text)
        for line_number in range(self.editor.lines()):
            item = model[line_number] if line_number < len(model) else type(model[0])(0)
            level = SC_FOLDLEVELBASE + item.depth
            if item.header:
                level |= SC_FOLDLEVELHEADERFLAG
            self.editor.SendScintilla(SCI_SETFOLDLEVEL, line_number, level)

    def set_all(self, expanded):
        """Set all fold headers explicitly; do not interpret foldAll's children flag as state."""
        self.recalculate()
        for line in range(self.editor.lines()):
            level = self.editor.SendScintilla(self.editor.SCI_GETFOLDLEVEL, line)
            if level & SC_FOLDLEVELHEADERFLAG:
                current = bool(self.editor.SendScintilla(self.editor.SCI_GETFOLDEXPANDED, line))
                if current != expanded:
                    self.editor.foldLine(line)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `FoldingController` | Own folding configuration and incremental scheduling for one editor. |
| `FoldingController.__init__` | Configure the folding margin and debounce model recalculation after text changes. |
| `FoldingController.schedule` | Restart the short quiet-period timer after an edit. |
| `FoldingController.recalculate` | Compute and publish fold metadata when document text changed. |
| `FoldingController.set_all` | Set all fold headers explicitly; do not interpret foldAll's children flag as state. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `markdown_editor/markdowneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.folding_controller import FoldingController
```



#### Edit `markdown_editor/markdowneditor.py` — `MarkdownEditor.__init__`

Attach folding after the existing lexer and editor setup.

Inside this method, find exactly:

```python
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)
```

Replace only that block with:

```python
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)

        self.folding_controller = FoldingController(self, "markdown")
```



#### Edit `markdown_editor/markdowneditor.py` — `MarkdownEditor.shutdown`

Stop pending fold calculations before the view is retired.

Inside this method, find exactly:

```python
        self._shutting_down = True
```

Replace only that block with:

```python
        self.folding_controller._timer.stop()
        self._shutting_down = True
```



#### Imports in `python_editor/pythoneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from code_inteligence.folding_controller import FoldingController
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Attach folding after the existing lexer and editor setup.

Inside this method, find exactly:

```python
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()
```

Replace only that block with:

```python
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()

        self.folding_controller = FoldingController(self, "python")
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.shutdown`

Stop pending fold calculations before the view is retired.

Inside this method, find exactly:

```python
        if self._shutting_down:
```

Replace only that block with:

```python
        self.folding_controller._timer.stop()
        if self._shutting_down:
```



#### Add methods to `main.py` — `MainWindow`

Each QAction invokes the current editor’s folding controller. Insert the following **after the complete `MainWindow.set_up_menu` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_folding(self):
        """Add explicit fold commands without requiring a command palette."""
        menu = self.menuBar().addMenu("Folding")
        toggle = menu.addAction("Toggle Fold")
        toggle.setObjectName("view.fold.toggle")
        toggle.setShortcut("Ctrl+Shift+[")
        toggle.triggered.connect(self._toggle_fold)
        collapse = menu.addAction("Fold All")
        collapse.setObjectName("view.fold.all")
        collapse.triggered.connect(lambda: self._fold_all(False))
        expand = menu.addAction("Unfold All")
        expand.setObjectName("view.fold.none")
        expand.triggered.connect(lambda: self._fold_all(True))

    def _toggle_fold(self):
        """Toggle the active line using QScintilla's foldLine slot."""
        editor = self.current_editor()
        if editor is not None:
            editor.folding_controller.recalculate()
            editor.foldLine(editor.getCursorPosition()[0])

    def _fold_all(self, expanded):
        """Set every fold header to a specific expanded/collapsed state."""
        editor = self.current_editor()
        if editor is not None:
            editor.folding_controller.set_all(expanded)
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
        self._install_folding()
```



#### Edit `main.py` — `MainWindow._apply_editor_settings`

Force fold metadata to be rebuilt after a theme/lexer replacement.

Inside this method, find exactly:

```python
        editor.SendScintilla(4003, 0, -1)
```

Replace only that block with:

```python
        editor.SendScintilla(4003, 0, -1)
        # Reapplying a lexer can replace fold levels even when text is unchanged.
        editor.folding_controller._last_digest = b""
        editor.folding_controller.schedule()
```



**Use this topic:** Run `python main.py`, open structured Python or Markdown text, then use the folding margin or the **Folding** menu. **Ctrl+Shift+[** toggles the caret line’s fold.


<a id="topic-10"></a>
## 10. Document Minimap

### Topic explanation

A document minimap is a compact overview beside the editor. It shows where the visible text sits within the whole document and lets you navigate by clicking or dragging the overview.

EditorMinimap belongs to one editor view, caches a reduced image of the document and highlights that view’s visible region. It translates mouse positions back to document lines. MainWindow owns the persisted visibility preference and supplies colors from the active lexer. Each duplicate view therefore has its own viewport indicator even when its text is shared.


**Documentation used for this topic:**

- [`QWidget`](https://doc.qt.io/archives/qt-5.15/qwidget.html)
- [`QPainter`](https://doc.qt.io/archives/qt-5.15/qpainter.html)
- [`SCI_LINESONSCREEN`](https://www.scintilla.org/ScintillaDoc.html#SCI_LINESONSCREEN)
- [`QsciScintilla`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)


### Topic code

Create or replace only the files listed here. The following implementation section connects this code to the existing editor.


#### Create `side_bar_widgets/editor_minimap.py`

**Folder:** `side_bar_widgets/` already exists. **File:** `editor_minimap.py`. Paste the complete code below starting at line 1.

```python
"""A bounded-cost document overview attached to one QScintilla editor."""

from PyQt5.QtCore import QEvent, QPoint, QRectF, Qt, QTimer
from PyQt5.QtGui import QColor, QMouseEvent, QPainter, QPen
from PyQt5.QtWidgets import QWidget


SCI_LINESONSCREEN = 2370
SCI_SETMARGINRIGHT = 2157


class EditorMinimap(QWidget):
    """Paint line-length strokes and navigate the observed editor."""

    def __init__(self, editor, width: int = 96) -> None:
        """Attach resize/scroll/edit signals and initialize one bounded-width navigation overlay."""
        super().__init__(editor)
        self.editor = editor
        self._map_width = max(48, min(width, 220))
        self._line_lengths: list[int] = []
        self._dirty = True
        self._dragging = False
        self._background = QColor("#1e1e1e")
        self._foreground = QColor("#858585")
        self._viewport = QColor(120, 150, 190, 75)

        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.editor.installEventFilter(self)
        self.editor.verticalScrollBar().valueChanged.connect(self.update)

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(180)
        self._refresh_timer.timeout.connect(self._rebuild_cache)
        self.editor.textChanged.connect(self.schedule_refresh)
        self._update_geometry()
        self.schedule_refresh()
        self.show()

    def set_colors(self, background: QColor, foreground: QColor,
                   viewport: QColor) -> None:
        """Apply validated theme-derived colors and repaint."""
        self._background = QColor(background)
        self._foreground = QColor(foreground)
        self._viewport = QColor(viewport)
        self.update()

    def set_map_visible(self, visible: bool) -> None:
        """Show or hide the overview and reserve matching editor space."""
        self.setVisible(visible)
        reserved = self._map_width if visible else 0
        self.editor.SendScintilla(SCI_SETMARGINRIGHT, 0, reserved)

    def schedule_refresh(self) -> None:
        """Coalesce fast typing into one cache rebuild."""
        self._dirty = True
        if self.isVisible():
            self._refresh_timer.start()

    def eventFilter(self, watched, event) -> bool:
        """Keep the overlay aligned when its editor is resized."""
        if watched is self.editor and event.type() == QEvent.Resize:
            self._update_geometry()
        return super().eventFilter(watched, event)

    def paintEvent(self, _event) -> None:
        """Render at most one representative source stroke per pixel row."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._background)
        total = max(1, len(self._line_lengths))
        height = max(1, self.height())
        stride = max(1, (total + height - 1) // height)
        painter.setPen(QPen(self._foreground, 1))

        for start in range(0, total, stride):
            bucket = self._line_lengths[start:start + stride]
            length = max(bucket, default=0)
            y = min(height - 1, int(start * height / total))
            stroke = min(self._map_width - 8, max(1, int(length * 0.7)))
            painter.drawLine(4, y, 4 + stroke, y)

        display_first = max(0, self.editor.firstVisibleLine())
        first = max(0, self.editor.SendScintilla(self.editor.SCI_DOCLINEFROMVISIBLE, display_first))
        display_count = max(1, int(self.editor.SendScintilla(SCI_LINESONSCREEN)))
        last = self.editor.SendScintilla(self.editor.SCI_DOCLINEFROMVISIBLE, display_first + display_count)
        visible = max(1, last - first) if last >= 0 else total - first
        top = first * height / total
        viewport_height = max(2.0, visible * height / total)
        painter.fillRect(QRectF(0, top, self.width(), viewport_height), self._viewport)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Begin navigation on a left-button press."""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._navigate(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Continuously navigate while the left button remains pressed."""
        if self._dragging:
            self._navigate(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Finish a minimap drag."""
        if event.button() == Qt.LeftButton:
            self._dragging = False

    def _rebuild_cache(self) -> None:
        """Rebuild one visible snapshot and cap stroke lengths to useful values."""
        if not self.isVisible():
            return
        self._dirty = False
        # Cap measured length because strokes wider than the widget are useless.
        self._line_lengths = [min(120, len(self.editor.text(line).rstrip("\r\n")))
                              for line in range(self.editor.lines())]
        self.update()

    def _navigate(self, point: QPoint) -> None:
        """Map a pointer row to a document line and reveal its corresponding display position."""
        total = max(1, self.editor.lines())
        target = min(total - 1, max(0, int(point.y() * total / max(1, self.height()))))
        visible = max(1, int(self.editor.SendScintilla(SCI_LINESONSCREEN)))
        self.editor.ensureLineVisible(target)
        display = self.editor.SendScintilla(self.editor.SCI_VISIBLEFROMDOCLINE, target)
        self.editor.setFirstVisibleLine(max(0, display - visible // 2))

    def _update_geometry(self) -> None:
        """Position the per-view overlay and reserve its width beside the editor text."""
        self.setGeometry(max(0, self.editor.width() - self._map_width),
                         0, self._map_width, self.editor.height())
        if self.isVisible():
            self.editor.SendScintilla(SCI_SETMARGINRIGHT, 0, self._map_width)

    def showEvent(self, event):
        """Refresh deferred content when a hidden view becomes visible."""
        if self._dirty:
            self._refresh_timer.start()
        super().showEvent(event)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `EditorMinimap` | Paint line-length strokes and navigate the observed editor. |
| `EditorMinimap.__init__` | Attach resize/scroll/edit signals and initialize one bounded-width navigation overlay. |
| `EditorMinimap.set_colors` | Apply validated theme-derived colors and repaint. |
| `EditorMinimap.set_map_visible` | Show or hide the overview and reserve matching editor space. |
| `EditorMinimap.schedule_refresh` | Coalesce fast typing into one cache rebuild. |
| `EditorMinimap.eventFilter` | Keep the overlay aligned when its editor is resized. |
| `EditorMinimap.paintEvent` | Render at most one representative source stroke per pixel row. |
| `EditorMinimap.mousePressEvent` | Begin navigation on a left-button press. |
| `EditorMinimap.mouseMoveEvent` | Continuously navigate while the left button remains pressed. |
| `EditorMinimap.mouseReleaseEvent` | Finish a minimap drag. |
| `EditorMinimap._rebuild_cache` | Rebuild one visible snapshot and cap stroke lengths to useful values. |
| `EditorMinimap._navigate` | Map a pointer row to a document line and reveal its corresponding display position. |
| `EditorMinimap._update_geometry` | Position the per-view overlay and reserve its width beside the editor text. |
| `EditorMinimap.showEvent` | Refresh deferred content when a hidden view becomes visible. |


### Topic implementation

No other topic is required. The additions below preserve already installed earlier topics.


#### Imports in `markdown_editor/markdowneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.editor_minimap import EditorMinimap
```



#### Edit `markdown_editor/markdowneditor.py` — `MarkdownEditor.__init__`

Create the overlay after the editor’s existing viewport setup.

Inside this method, find exactly:

```python
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)
```

Replace only that block with:

```python
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)

        self.minimap = EditorMinimap(self)
        self.minimap.set_map_visible(False)
```



#### Edit `markdown_editor/markdowneditor.py` — `MarkdownEditor.shutdown`

Stop overview refresh work before retiring the view.

Inside this method, find exactly:

```python
        self._shutting_down = True
```

Replace only that block with:

```python
        self.minimap._refresh_timer.stop()
        self._shutting_down = True
```



#### Imports in `python_editor/pythoneditor.py`

Add these imports to the existing import section, after any `from __future__` imports. Keep the existing imports.

```python
from side_bar_widgets.editor_minimap import EditorMinimap
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.__init__`

Create the overlay after the editor’s existing viewport setup.

Inside this method, find exactly:

```python
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()
```

Replace only that block with:

```python
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()

        self.minimap = EditorMinimap(self)
        self.minimap.set_map_visible(False)
```



#### Edit `python_editor/pythoneditor.py` — `PythonEditor.shutdown`

Stop overview refresh work before retiring the view.

Inside this method, find exactly:

```python
        if self._shutting_down:
```

Replace only that block with:

```python
        self.minimap._refresh_timer.stop()
        if self._shutting_down:
```



#### Add methods to `main.py` — `MainWindow`

MainWindow owns the preference and menu action; each editor owns only its own overlay. Insert the following **after the complete `MainWindow._apply_editor_settings` method**, before the next existing method. Keep the shown four-space class indentation.

```python
    def _install_minimap(self):
        """Create a persisted visibility command for each editor's own minimap."""
        menu = self.menuBar().addMenu("Minimap")
        self.minimap_action = menu.addAction("Show Minimap")
        self.minimap_action.setObjectName("view.minimap")
        self.minimap_action.setCheckable(True)
        self.minimap_action.setChecked(self.settings.value("editor/show_minimap", False, type=bool))
        self.minimap_action.toggled.connect(self._toggle_minimap)

    def _apply_minimap(self, editor):
        """Use real lexer theme accessors after settings replace the lexer."""
        lexer = editor.lexer()
        background = lexer.editor_color("paper-color", "#1e1f22") if hasattr(lexer, "editor_color") else QColor("#1e1f22")
        foreground = lexer.color(0) if lexer else QColor("#858585")
        editor.minimap.set_colors(background, foreground, QColor(120, 150, 190, 75))
        editor.minimap.set_map_visible(self.settings.value("editor/show_minimap", False, type=bool))

    def _toggle_minimap(self, visible):
        """Persist visibility and update each view's independently owned overview."""
        self.settings.setValue("editor/show_minimap", bool(visible))
        for editor in self.tab_view.all_editors():
            self._apply_minimap(editor)
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
        self._install_minimap()
```



#### Edit `main.py` — `MainWindow._apply_editor_settings`

Update minimap colors after the replacement lexer is installed.

Inside this method, find exactly:

```python
        editor.SendScintilla(4003, 0, -1)
```

Replace only that block with:

```python
        editor.SendScintilla(4003, 0, -1)
        self._apply_minimap(editor)
```



#### Edit `main.py` — `MainWindow._connect_editor`

Apply the persisted visibility to every newly connected editor view.

Inside this method, find exactly:

```python
        editor.textChanged.connect(lambda ed=editor: self._on_editor_text_changed(ed))
```

Replace only that block with:

```python
        self._apply_minimap(editor)
        editor.textChanged.connect(lambda ed=editor: self._on_editor_text_changed(ed))
```



**Use this topic:** Run `python main.py`, open a document and enable **Minimap → Show Minimap**. Clicking or dragging the overview moves the current view. The visibility choice persists.


<a id="topic-11"></a>
## 11. Git Branch Indicator and Commit Graph

### Topic explanation

The Git branch indicator shows the current repository identity, including detached or unborn states. The commit graph displays parent relationships and decorations so you can inspect history without leaving the editor.

This topic already exists in the current repository. The history model parses Git records, GitService obtains snapshots asynchronously, and CommitGraphPanel lays out and displays the graph. MainWindow uses one snapshot to update both the branch label and graph. Keep the existing implementation and signal connections; the code below is a reference to what is already installed, not a second implementation to paste.


**Documentation used for this topic:**

- [`git log`](https://git-scm.com/docs/git-log)
- [pretty formats](https://git-scm.com/docs/pretty-formats)
- [`git symbolic-ref`](https://git-scm.com/docs/git-symbolic-ref)
- [`git rev-parse`](https://git-scm.com/docs/git-rev-parse)
- [`subprocess`](https://docs.python.org/3/library/subprocess.html)
- [`QThread`](https://doc.qt.io/archives/qt-5.15/qthread.html)
- [`QTreeWidget`](https://doc.qt.io/archives/qt-5.15/qtreewidget.html)


### Topic code

The following files are already present. **Keep them**; the complete code is included for explanation.


#### Keep `git_implementation/history.py`

**Folder:** `git_implementation/` already exists. **File:** `history.py`. Keep its existing contents; do not paste a duplicate copy.

```python
"""Pure Git history values, parser and compact topological lane layout."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitCommit:
    """One immutable commit returned by the selected repository."""

    sha: str
    parents: tuple[str, ...]
    author: str
    authored_at: str
    decorations: str
    subject: str


@dataclass(frozen=True)
class GitSnapshot:
    """Branch/HEAD identity and a topologically ordered history page."""

    root: Path
    branch: str | None
    head_short: str
    commits: tuple[GitCommit, ...]


@dataclass
class GraphRow:
    """A commit plus a compact text representaion of its active lanes."""

    commit: GitCommit
    lane: int
    lane_count: int
    graph_text: str
    color_index: int = 0
    incoming: tuple[tuple[int, int], ...] = ()
    outgoing: tuple[tuple[int, int, int], ...] = ()


def parse_log(output: str) -> tuple[GitCommit, ...]:
    """Parse the record/unit-separated output produced by GitHistoryWorker.

    Args:
        output: Text whose records start with ``\x1e`` and whose six fields
            are separated by ``\x1f``.

    Returns:
        Immutable commits in the order provided by ``git log``.

    Raises:
        ValueError: If a record is missing fields or its object ID.
    """
    commits: list[GitCommit] = []
    for raw_record in output.split("\x1e"):
        record = raw_record.strip("\r\n")
        if not record:
            continue

        fields = record.split("\x1f", 5)
        if len(fields) != 6:
            raise ValueError("Malformed git log record")

        sha, parents, author, authored_at, decorations, subject = fields
        if not sha:
            raise ValueError("Git log record has no object id")

        commits.append(
            GitCommit(
                sha=sha,
                # A merge commit can have two or more parents, so the model's
                # field is deliberately plural.
                parents=tuple(parent for parent in parents.split() if parent),
                author=author,
                authored_at=authored_at,
                decorations=decorations,
                subject=subject,
            )
        )

    return tuple(commits)


def layout_graph(commits: tuple[GitCommit, ...]) -> tuple[GraphRow, ...]:
    """Assign stable columns and mark merges for a compact graph view."""
    active: list[str] = []
    colors: dict[str, int] = {}
    next_color = 0
    rows: list[GraphRow] = []

    for commit in commits:
        # The previous row's bottom lanes are this row's incoming lanes.
        incoming = tuple((i, colors[sha]) for i, sha in enumerate(active))
        if commit.sha not in active:
            active.append(commit.sha)
            colors[commit.sha] = next_color
            next_color += 1

        lane = active.index(commit.sha)
        node_color = colors[commit.sha]
        before = list(active)
        before_count = len(active)
        glyphs = ["| " for _ in active]
        glyphs[lane] = "● "
        suffix = "┬" if len(commit.parents) > 1 else ("╵" if not commit.parents else "")
        active.pop(lane)
        for number, parent in enumerate(commit.parents):
            if parent not in active:
                active.insert(min(lane + number, len(active)), parent)
                # Continue the first-parent line; side parents get another color.
                colors[parent] = node_color if number == 0 else next_color
                if number:
                    next_color += 1

        outgoing = [
            (i, active.index(sha), colors[sha]) for i, sha in enumerate(before) if sha != commit.sha
        ]
        outgoing.extend(
            (lane, active.index(parent), colors[parent]) for parent in dict.fromkeys(commit.parents)
        )
        rows.append(
            GraphRow(
                commit,
                lane,
                max(before_count, len(active)),
                "".join(glyphs) + suffix,
                node_color,
                incoming,
                tuple(outgoing),
            )
        )

        # Bound corrupt or adversarial history even though normal graphs are
        # far smaller than this limit.
        if len(active) > 256:
            raise ValueError("Commit graph exceeds the supported lane count")

    return tuple(rows)
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `GitCommit` | One immutable commit returned by the selected repository. |
| `GitSnapshot` | Branch/HEAD identity and a topologically ordered history page. |
| `GraphRow` | A commit plus a compact text representaion of its active lanes. |
| `parse_log` | Parse the record/unit-separated output produced by GitHistoryWorker. |
| `layout_graph` | Assign stable columns and mark merges for a compact graph view. |


#### Keep `git_implementation/git_service.py`

**Folder:** `git_implementation/` already exists. **File:** `git_service.py`. Keep its existing contents; do not paste a duplicate copy.

```python
"""Asynchronously retrieve bounded Git history without invoking a shell."""

from pathlib import Path
import subprocess
import time

from PyQt5.QtCore import QObject, QThread, pyqtSignal

from git_implementation.history import GitSnapshot, parse_log


class GitHistoryWorker(QThread):
    """Fetch one immutable Git snapshot outside the GUI thread."""

    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, folder: Path, limit: int = 500, parent=None) -> None:
        """Store one bounded history request without starting the thread."""
        super().__init__(parent)
        self.folder = Path(folder)
        self.limit = max(1, min(int(limit), 5000))

    def run(self) -> None:
        """Resolve repository root, identity, and bounded commit history."""
        try:
            root = self._git("rev-parse", "--show-toplevel").strip()
            if not root:
                raise RuntimeError("The selected folder is not a Git repository")

            repository = Path(root).resolve()
            branch_result = self._run(
                repository,
                "symbolic-ref",
                "--short",
                "--quiet",
                "HEAD",
            )
            branch = (
                branch_result.stdout.strip()
                if branch_result.returncode == 0
                else None
            )

            head_result = self._run(repository, "rev-parse", "--short", "HEAD")
            head = (
                head_result.stdout.strip()
                if head_result.returncode == 0
                else ""
            )

            log_result = self._run(
                repository,
                "log",
                "--all",
                "--topo-order",
                "--date-order",
                f"--max-count={self.limit}",
                "--format=%x1e%H%x1f%P%x1f%an%x1f%aI%x1f%D%x1f%s",
            )
            if log_result.returncode == 0:
                commits = parse_log(log_result.stdout)
            elif not head:
                # A repository with no first commit is valid.
                commits = ()
            else:
                raise RuntimeError(log_result.stderr.strip() or "Git log failed")

            self.succeeded.emit(
                GitSnapshot(repository, branch, head, commits)
            )
        except (
            OSError,
            subprocess.TimeoutExpired,
            RuntimeError,
            ValueError,
        ) as error:
            self.failed.emit(str(error))

    def _run(
        self,
        cwd: Path,
        *arguments: str,
    ) -> subprocess.CompletedProcess[str]:
        """Run Git with a timeout that remains responsive to cancellation.

        ``subprocess.run()`` cannot observe ``requestInterruption()`` while it
        waits. Short ``communicate()`` timeouts let shutdown terminate a Git
        child before Qt destroys the worker thread.
        """
        command = ["git", *arguments]
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 15

        while True:
            if self.isInterruptionRequested():
                process.terminate()
                try:
                    process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                raise InterruptedError("Git history refresh was cancelled")

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.kill()
                stdout, stderr = process.communicate()
                raise subprocess.TimeoutExpired(
                    command,
                    15,
                    output=stdout,
                    stderr=stderr,
                )

            try:
                stdout, stderr = process.communicate(
                    timeout=min(0.1, remaining)
                )
            except subprocess.TimeoutExpired:
                continue

            return subprocess.CompletedProcess(
                command,
                process.returncode,
                stdout,
                stderr,
            )

    def _git(self, *arguments: str) -> str:
        """Run a checked Git command in the user-selected folder."""
        return self._git_at(self.folder, *arguments)

    def _git_at(self, cwd: Path, *arguments: str) -> str:
        """Return stdout for a successful Git command in ``cwd``."""
        completed = self._run(cwd, *arguments)
        if completed.returncode != 0:
            message = completed.stderr.strip() or "Git command failed"
            raise RuntimeError(message)
        return completed.stdout


class GitService(QObject):
    """Publish only the newest asynchronous history request."""

    snapshotReady = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        """Initialize generation tracking and active-worker ownership."""
        super().__init__(parent)
        self._generation = 0
        self._workers: set[GitHistoryWorker] = set()
        self._shutting_down = False

    def refresh(self, folder: Path) -> None:
        """Start a bounded refresh and invalidate every older result."""
        if self._shutting_down:
            return

        self._generation += 1
        generation = self._generation

        # Old results are already rejected by generation. Interrupting the old
        # work also prevents repeated timer ticks from accumulating processes.
        for existing in tuple(self._workers):
            existing.requestInterruption()

        worker = GitHistoryWorker(folder, parent=self)
        self._workers.add(worker)
        worker.succeeded.connect(
            lambda snapshot, value=generation: self._publish(value, snapshot)
        )
        worker.failed.connect(
            lambda message, value=generation: self._publish_error(value, message)
        )
        worker.finished.connect(
            lambda current=worker: self._workers.discard(current)
        )
        worker.finished.connect(worker.deleteLater)
        worker.start()

    def _publish(self, generation: int, snapshot: GitSnapshot) -> None:
        """Publish a snapshot only when it belongs to the newest request."""
        if generation == self._generation:
            self.snapshotReady.emit(snapshot)

    def _publish_error(self, generation: int, message: str) -> None:
        """Publish an error only when it belongs to the newest request."""
        if generation == self._generation:
            self.failed.emit(message)

    def is_running(self) -> bool:
        """Return whether a history worker still owns a Git subprocess."""
        return any(worker.isRunning() for worker in self._workers)

    def shutdown(self) -> None:
        """Cancel active history work and suppress every stale result."""
        self._shutting_down = True
        self._generation += 1
        for worker in tuple(self._workers):
            worker.requestInterruption()
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `GitHistoryWorker` | Fetch one immutable Git snapshot outside the GUI thread. |
| `GitHistoryWorker.__init__` | Store one bounded history request without starting the thread. |
| `GitHistoryWorker.run` | Resolve repository root, identity, and bounded commit history. |
| `GitHistoryWorker._run` | Run Git with a timeout that remains responsive to cancellation. |
| `GitHistoryWorker._git` | Run a checked Git command in the user-selected folder. |
| `GitHistoryWorker._git_at` | Return stdout for a successful Git command in ``cwd``. |
| `GitService` | Publish only the newest asynchronous history request. |
| `GitService.__init__` | Initialize generation tracking and active-worker ownership. |
| `GitService.refresh` | Start a bounded refresh and invalidate every older result. |
| `GitService._publish` | Publish a snapshot only when it belongs to the newest request. |
| `GitService._publish_error` | Publish an error only when it belongs to the newest request. |
| `GitService.is_running` | Return whether a history worker still owns a Git subprocess. |
| `GitService.shutdown` | Cancel active history work and suppress every stale result. |


#### Keep `git_ui/commit_graph.py`

**Folder:** `git_ui/` already exists. **File:** `commit_graph.py`. Keep its existing contents; do not paste a duplicate copy.

```python
"""Editor-themed history with painted ancestry and safe reference labels."""

import json
from datetime import datetime
from html import escape

from PyQt5.QtCore import QPointF, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPalette, QPen, QTextDocument
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QHeaderView,
    QMenu,
    QPlainTextEdit,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from git_implementation.history import GitSnapshot, layout_graph

ROW_ROLE = Qt.UserRole + 1
REF_ROLE = Qt.UserRole + 2
LANE_WIDTH = 22


class HistoryDelegate(QStyledItemDelegate):
    """Paint graph segments and escaped, colored reference labels."""

    def __init__(self, panel):
        """Retain the panel's live palette without duplicating theme state."""
        super().__init__(panel)
        self.panel = panel

    def sizeHint(self, option, index):
        """Give nodes and labels space at any font size."""
        size = super().sizeHint(option, index)
        size.setHeight(max(32, option.fontMetrics.height() + 12))
        return size

    def paint(self, painter, option, index):
        """Draw standard selection first, then graph or reference content."""
        if index.column() not in (0, 2):
            return super().paint(painter, option, index)
        styled = QStyleOptionViewItem(option)
        self.initStyleOption(styled, index)
        styled.text = ""
        self.panel.style().drawControl(QStyle.CE_ItemViewItem, styled, painter, self.panel)
        painter.save()
        painter.setClipRect(option.rect)
        if index.column() == 0:
            row = index.data(ROW_ROLE)
            if row is not None:
                self._paint_graph(painter, option.rect, row)
        else:
            self._paint_refs(painter, option, index)
        painter.restore()

    def _paint_graph(self, painter, rect, row):
        """Connect row boundaries using model-supplied parent edges."""
        painter.setRenderHint(QPainter.Antialiasing)
        middle = rect.top() + rect.height() / 2
        left = rect.left() + 16
        for lane, color in row.incoming:
            painter.setPen(QPen(self.panel.lane_color(color), 2))
            x = left + lane * LANE_WIDTH
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, middle))
        for start, end, color in row.outgoing:
            painter.setPen(QPen(self.panel.lane_color(color), 2))
            x1, x2 = left + start * LANE_WIDTH, left + end * LANE_WIDTH
            path = QPainterPath(QPointF(x1, middle))
            bottom = rect.top() + rect.height()
            path.cubicTo(x1, bottom - 4, x2, middle + 4, x2, bottom)
            painter.drawPath(path)
        center = QPointF(left + row.lane * LANE_WIDTH, middle)
        painter.setBrush(self.panel.lane_color(row.color_index))
        painter.setPen(QPen(QColor(self.panel.background), 2))
        painter.drawEllipse(center, 5, 5)
        if "HEAD" in row.commit.decorations:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(self.panel.lane_color(row.color_index), 1))
            painter.drawEllipse(center, 8, 8)

    def _paint_refs(self, painter, option, index):
        """Render escaped labels so Git text cannot become active HTML."""
        row = index.sibling(index.row(), 0).data(ROW_ROLE)
        if row is None:
            return
        badges = []
        for ref in index.data(REF_ROLE) or ():
            color = self.panel.lane_color(3 if ref.startswith("tag: ") else row.color_index).name()
            badges.append(f'<span style="color:{color}; font-weight:600">[{escape(ref)}]</span>')
        doc = QTextDocument()
        doc.setDefaultFont(option.font)
        doc.setDocumentMargin(0)
        doc.setHtml(" &nbsp; ".join(badges))
        painter.translate(
            option.rect.left() + 7,
            option.rect.top() + (option.rect.height() - doc.size().height()) / 2,
        )
        doc.drawContents(painter)


class CommitGraphPanel(QTreeWidget):
    """Display readable history without changing repository state."""

    commitActivated = pyqtSignal(str)

    def __init__(self, parent=None):
        """Configure columns, selection, delegates, and read-only actions."""
        super().__init__(parent)
        self.setObjectName("GitHistoryTree")
        self._snapshot = None
        self._rows = {}
        self.setColumnCount(6)
        self.setHeaderLabels(
            ("Graph", "Commit message", "Branches / tags", "Commit", "Author", "Date")
        )
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setSortingEnabled(False)  # Sorting would falsify ancestry.
        self.setHorizontalScrollMode(QTreeWidget.ScrollPerPixel)
        self.setItemDelegate(HistoryDelegate(self))
        self.header().setStretchLastSection(False)
        self.header().setMinimumSectionSize(60)
        for column, width in enumerate((90, 330, 240, 100, 155, 155)):
            self.header().setSectionResizeMode(column, QHeaderView.Interactive)
            self.setColumnWidth(column, width)
        self.itemActivated.connect(self._activate)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)
        self.apply_theme()

    def sizeHint(self):
        """Request useful initial dock space for commit summaries."""
        return QSize(1100, 340)

    def resizeEvent(self, event):
        """Keep summaries readable in narrow docks; scroll other columns."""
        super().resizeEvent(event)
        occupied = sum(self.columnWidth(i) for i in (0, 2, 3, 4, 5))
        self.setColumnWidth(1, max(330, self.viewport().width() - occupied))

    def lane_color(self, number):
        """Return a repeatable color for an ancestry line, not a row number."""
        return QColor(self._lane_colors[number % len(self._lane_colors)])

    def apply_theme(self, theme_path=None):
        """Read the editor's theme file with safe dark-theme fallbacks."""
        theme = {}
        if theme_path:
            try:
                with open(theme_path, encoding="utf-8") as stream:
                    theme = json.load(stream).get("theme", {})
            except (OSError, ValueError, AttributeError):
                theme = {}
        if not isinstance(theme, dict):
            theme = {}
        editor = theme.get("editor", {})
        editor = editor if isinstance(editor, dict) else {}
        paper = editor.get("paper-color", "#1e1f22")
        background = QColor(paper if isinstance(paper, str) else "#1e1f22")
        if not background.isValid():
            background = QColor("#1e1f22")
        dark = background.lightness() < 128
        self.background = background.name()
        foreground = "#bcbec4" if dark else "#24292f"
        surface = background.lighter(125).name() if dark else background.darker(105).name()
        selection = "#35465d" if dark else "#d6e8ff"
        border = "#393b40" if dark else "#c8cdd3"
        self._lane_colors = (
            ("#82aaff", "#c792ea", "#66d9a8", "#ecc48d", "#f78c9c", "#89ddff")
            if dark
            else ("#185abc", "#753ab7", "#197347", "#8c5900", "#b32243", "#006a80")
        )
        font_settings = editor.get("font", {})
        font_settings = font_settings if isinstance(font_settings, dict) else {}
        try:
            size = max(9, min(20, int(font_settings.get("font-size", 11))))
        except (ValueError, TypeError):
            size = 11
        self.setFont(QFont(str(font_settings.get("family", "monospace")), size))
        # Measure fixed metadata columns at the selected font size, not at the
        # system default. Otherwise even an eight-character SHA gets ellipsized.
        metrics = self.fontMetrics()
        self.setColumnWidth(2, max(280, metrics.horizontalAdvance("feature/git-history") + 40))
        self.setColumnWidth(3, metrics.horizontalAdvance("01234567") + 30)
        self.setColumnWidth(4, metrics.horizontalAdvance("David Schubba") + 30)
        self.setColumnWidth(5, metrics.horizontalAdvance("2026-09-16 12:48") + 30)
        palette = self.palette()
        palette.setColor(QPalette.Base, background)
        palette.setColor(QPalette.Text, QColor(foreground))
        self.setPalette(palette)
        self.setStyleSheet(f"""
            QTreeWidget#GitHistoryTree {{ background:{self.background}; color:{foreground};
                alternate-background-color:{surface}; border:0; outline:0; }}
            QTreeWidget#GitHistoryTree::item {{ padding:0 7px; border:0; }}
            QTreeWidget#GitHistoryTree::item:selected {{ background:{selection}; color:{foreground}; }}
            QHeaderView::section {{ background:{surface}; color:{foreground};
                padding:9px 8px; border:0; border-bottom:1px solid {border}; }}
            QScrollBar {{ background:{self.background}; width:12px; height:12px; }}
            QScrollBar::handle {{ background:{border}; border-radius:4px; min-height:24px; min-width:24px; }}
            QMenu {{ background:{surface}; color:{foreground}; }}
        """)
        self.viewport().update()

    def set_snapshot(self, snapshot: GitSnapshot):
        """Replace history atomically and retain selection during refreshes."""
        if snapshot == self._snapshot:
            return
        rows = layout_graph(snapshot.commits)  # Validate before clearing old data.
        current = self.currentItem()
        same_root = self._snapshot is not None and self._snapshot.root == snapshot.root
        selected = current.data(0, Qt.UserRole) if current and same_root else None
        scroll = self.verticalScrollBar().value() if same_root else 0
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            self._snapshot = snapshot
            self._rows = {row.commit.sha: row for row in rows}
            for row in rows:
                commit = row.commit
                try:
                    date = datetime.fromisoformat(commit.authored_at).strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    date = commit.authored_at
                refs = tuple(filter(None, commit.decorations.split(", ")))
                item = QTreeWidgetItem(
                    ("", commit.subject, "  ".join(refs), commit.sha[:8], commit.author, date)
                )
                item.setData(0, Qt.UserRole, commit.sha)
                item.setData(0, ROW_ROLE, row)
                item.setData(2, REF_ROLE, refs)
                for column, value in enumerate(
                    (
                        commit.sha,
                        commit.subject,
                        commit.decorations,
                        commit.sha,
                        commit.author,
                        commit.authored_at,
                    )
                ):
                    item.setToolTip(column, "<qt>" + escape(value) + "</qt>")
                self.addTopLevelItem(item)
                if commit.sha == selected:
                    self.setCurrentItem(item)
            lanes = max((row.lane_count for row in rows), default=1)
            self.setColumnWidth(0, max(75, 32 + lanes * LANE_WIDTH))
            # Recompute scrollbar limits before restoring the previous position.
            self.doItemsLayout()
            self.verticalScrollBar().setValue(scroll)
        finally:
            self.setUpdatesEnabled(True)

    def clear(self):
        """Invalidate cached history when the repository disappears."""
        self._snapshot = None
        self._rows = {}
        super().clear()

    def _activate(self, item, _column):
        """Emit the SHA and display non-mutating details on activation."""
        sha = item.data(0, Qt.UserRole)
        if sha:
            self.commitActivated.emit(str(sha))
            self._show_details(str(sha))

    def _show_details(self, sha):
        """Show snapshot metadata without executing repository commands."""
        row = self._rows.get(sha)
        if row is None:
            return
        commit = row.commit
        dialog = QDialog(self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.setWindowTitle("Commit details")
        dialog.resize(720, 330)
        layout = QVBoxLayout(dialog)
        text = QPlainTextEdit(dialog)
        text.setReadOnly(True)
        text.setFont(self.font())
        text.setStyleSheet(
            f"background:{self.background};color:{self.palette().color(QPalette.Text).name()};"
        )
        text.setPlainText(
            f"Commit: {sha}\nAuthor: {commit.author}\nDate: {commit.authored_at}\n"
            f"Refs: {commit.decorations or '(none)'}\n"
            f"Parents: {', '.join(commit.parents) or '(root commit)'}\n\n{commit.subject}"
        )
        layout.addWidget(text)
        dialog.show()

    def _context_menu(self, position):
        """Offer copy and inspect actions, never checkout or discard."""
        item = self.itemAt(position)
        if item is None:
            return
        sha = item.data(0, Qt.UserRole)
        menu = QMenu(self)
        menu.addAction("Copy commit SHA", lambda: QApplication.clipboard().setText(sha))
        menu.addAction(
            "Copy commit message", lambda: QApplication.clipboard().setText(item.text(1))
        )
        menu.addAction("Commit details", lambda: self._show_details(sha))
        menu.exec_(self.viewport().mapToGlobal(position))
```


**Code explanation:**

| Class, function or method | Responsibility |
|---|---|
| `HistoryDelegate` | Paint graph segments and escaped, colored reference labels. |
| `HistoryDelegate.__init__` | Retain the panel's live palette without duplicating theme state. |
| `HistoryDelegate.sizeHint` | Give nodes and labels space at any font size. |
| `HistoryDelegate.paint` | Draw standard selection first, then graph or reference content. |
| `HistoryDelegate._paint_graph` | Connect row boundaries using model-supplied parent edges. |
| `HistoryDelegate._paint_refs` | Render escaped labels so Git text cannot become active HTML. |
| `CommitGraphPanel` | Display readable history without changing repository state. |
| `CommitGraphPanel.__init__` | Configure columns, selection, delegates, and read-only actions. |
| `CommitGraphPanel.sizeHint` | Request useful initial dock space for commit summaries. |
| `CommitGraphPanel.resizeEvent` | Keep summaries readable in narrow docks; scroll other columns. |
| `CommitGraphPanel.lane_color` | Return a repeatable color for an ancestry line, not a row number. |
| `CommitGraphPanel.apply_theme` | Read the editor's theme file with safe dark-theme fallbacks. |
| `CommitGraphPanel.set_snapshot` | Replace history atomically and retain selection during refreshes. |
| `CommitGraphPanel.clear` | Invalidate cached history when the repository disappears. |
| `CommitGraphPanel._activate` | Emit the SHA and display non-mutating details on activation. |
| `CommitGraphPanel._show_details` | Show snapshot metadata without executing repository commands. |
| `CommitGraphPanel._context_menu` | Offer copy and inspect actions, never checkout or discard. |


### Topic implementation

This feature already runs in the repository. Create no folders or files, delete no code, and add no duplicate connections.


The existing integration is in `main.py`, inside `MainWindow`:

| Location | Existing connection to keep |
|---|---|
| Imports | `GitService` and `CommitGraphPanel` imports |
| End of `init_ui`, after `_arm_cat_timers()` | Creates `git_service`, the branch label, the graph widget and the named `GitHistoryDock`; connects `snapshotReady` and `failed`; requests the initial refresh |
| `_on_git_snapshot` | Updates the branch label and graph from the same snapshot |
| `_on_git_failure` | Clears stale repository information |
| `_refresh_git_state` and `_refresh_git_history` | Refresh file colors and history for the current file-manager root |
| `set_up_menu` | Existing View-menu action shows Git History |
| `_background_work_running` and `closeEvent` | Retain and shut down the asynchronous Git service |

The existing snapshot and refresh methods are shown below to explain the integration. **Keep their single existing definitions; do not append another copy.**


```python
    def _on_git_snapshot(self, snapshot) -> None:
        """Update branch identity and graph from the same Git snapshot."""
        identity = snapshot.branch or (
            f"detached@{snapshot.head_short}" if snapshot.head_short else "unborn"
        )
        self.git_branch_label.setText(f"Git: {identity}")
        self.git_branch_label.setToolTip(str(snapshot.root))
        self.git_graph.set_snapshot(snapshot)
```

```python
    def _on_git_failure(self, message: str) -> None:
        """Clear stale repository identity without interrupting editing."""
        self.git_branch_label.setText("No Git repository")
        self.git_branch_label.setToolTip(message)
        
        # Do not call git_branch_label.clear(); that erases the message just set.
        self.git_graph.clear()
```

```python
    def _refresh_git_state(self) -> None:
        """
        Refresh file colors and history for the current project root.
        
        The file-tree status checker and history service are seperate asynchronous
        components. One coordinator prevents manus, timers, and folder changes
        from refreshing only half of the Git UI.
        """
        file_manager = getattr(self, "file_manager", None)
        if file_manager is None:
            return
        
        file_manager.check_git_status()
        if hasattr(self, "git_service"):
            self._refresh_git_history()
```

```python
    def _refresh_git_history(self) -> None:
        """Request history for the current FileManager root, if one is open."""
        folder = self.file_manager.current_folder
        if folder:
            self.git_service.refresh(Path(folder))
```


**Use this topic:** Run `python main.py` and open a folder inside a Git repository. Use the existing Git History action in the View menu. The status bar and graph use the selected folder’s repository; Git must be available to the existing GitService.
