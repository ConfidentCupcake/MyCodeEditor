# MarkdownEditor — feature implementation guide

This guide targets the **current GitHub repository directly**, without requiring the previous guide. All paths are relative to the repository root. Existing-file line numbers refer to commit `17f08584813a91fc5a5450590130c7292a46de37`; after edits move lines, the named method and its next-definition boundary are the authoritative placement instructions.

Create the feature files in Topics 1–10, keep the existing Git implementation in Topic 11, then apply **Application integration** once. Shared save, close, rename, and session methods are printed as combined replacements so one feature does not overwrite another.

The required source folders already exist: `code_inteligence/`, `code_settings/`, `ruff_implementation/`, `side_bar_widgets/`, `python_editor/`, and `markdown_editor/`. Keep the actual spelling **`code_inteligence`**. The attached course's proposed `commands/`, `diagnostics/`, `documents/`, `snippets/`, `folding/`, and `editor_widgets/` packages are mapped into these existing folders. Do not create those additional top-level packages or add package markers.

**Create file** means paste the complete block into the new file. **Replace method** means delete the complete old definition, including decorators, and paste the supplied definition at the same indentation. **Add method** means add it once inside the stated class. No entire existing repository file needs deletion; replacements and the old Ruff context-menu placeholder are identified below.

## Topics

| Topic | Implementation |
|---:|---|
| 1 | [Command Registry and Command Palette](#topic-1) |
| 2 | [Caret and Selection Contrast](#topic-2) |
| 3 | [Provider-Neutral Diagnostics and Problems](#topic-3) |
| 4 | [Ruff Quick Fixes](#topic-4) |
| 5 | [Find All References](#topic-5) |
| 6 | [Shared Document State and Enhanced Tabs](#topic-6) |
| 7 | [External File and Directory Watching](#topic-7) |
| 8 | [Snippets and Reusable Templates](#topic-8) |
| 9 | [Code Folding](#topic-9) |
| 10 | [Document Minimap](#topic-10) |
| 11 | [Git Branch Indicator and Commit Graph](#topic-11) |

<a id="topic-1"></a>
## 1. Command Registry and Command Palette

### What the feature does

A command is an existing QAction with a stable identity. The registry lets the menu and palette execute the same action, so shortcuts, check state, and disabled state remain consistent. Ctrl+Shift+L opens the palette; all search words must match its category, label, or shortcut.

### How the code works

The registry walks current menus whenever the palette opens. This is important because the recent-files menu replaces its QAction objects. Existing menu actions receive object names in set_up_menu; the new Editor Tools actions receive explicit IDs. The popup holds current Command records in Qt.UserRole and calls action.trigger(), rather than duplicating MainWindow callbacks.

### Official documentation

- [`QAction` reference](https://doc.qt.io/archives/qt-5.15/qaction.html)
- [`QMenu`](https://doc.qt.io/archives/qt-5.15/qmenu.html)
- [`QAction`](https://doc.qt.io/archives/qt-5.15/qaction.html)
- [`QDialog`](https://doc.qt.io/archives/qt-5.15/qdialog.html)
- [`QListWidget`](https://doc.qt.io/archives/qt-5.15/qlistwidget.html)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `main.py` | [`MainWindow.set_up_menu`](#method-main-py-mainwindow-set-up-menu) — baseline lines 777–1050 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-code-inteligence-command-registry-py"></a>
### CREATE FILE — `code_inteligence/command_registry.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `command_registry.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
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

<a id="file-code-inteligence-command-palette-py"></a>
### CREATE FILE — `code_inteligence/command_palette.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `command_palette.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `CommandPaletteDialog` | Keyboard-first filtered view over a CommandRegistry. |
| `CommandPaletteDialog.__init__` | Build a search field and result list bound to the shared command registry. |
| `CommandPaletteDialog.open_palette` | Refresh live menu actions, reset the query and focus the popup search field. |
| `CommandPaletteDialog._refill` | Filter by all query tokens while displaying current shortcuts and disabled state. |
| `CommandPaletteDialog._execute_current` | Close the popup and trigger the selected existing action only when enabled. |
| `CommandPaletteDialog.keyPressEvent` | Move through results with arrow keys and preserve normal dialog Escape behavior. |

<a id="topic-2"></a>
## 2. Caret and Selection Contrast

### What the feature does

Caret width and color, selection text, and selection background are editable appearance preferences. A missing color override means inherit the active lexer theme; Reset to theme removes the saved override. Colors are applied after a lexer/theme replacement, which otherwise restores its own editor-wide styling.

### How the code works

read_preferences, the Appearance tab, write_preferences, and apply_preferences form one read/edit/save/apply path. The color-button callbacks capture their own keys so each row edits the intended setting. The luminance helpers make contrast calculations available without mixing them into settings persistence. This implementation controls the active selection through the existing QScintilla APIs; it does not introduce an unsupported inactive-selection message.

### Official documentation

- [`QsciScintilla` reference](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)
- [`QColor`](https://doc.qt.io/archives/qt-5.15/qcolor.html)
- [`QColorDialog`](https://doc.qt.io/archives/qt-5.15/qcolordialog.html)
- [`QSettings`](https://doc.qt.io/archives/qt-5.15/qsettings.html)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `main.py` | [`MainWindow._load_settings`](#method-main-py-mainwindow-load-settings) — baseline lines 1399–1438 |
| `main.py` | [`MainWindow._save_settings`](#method-main-py-mainwindow-save-settings) — baseline lines 1440–1468 |
| `main.py` | [`MainWindow._apply_editor_settings`](#method-main-py-mainwindow-apply-editor-settings) — baseline lines 1664–1738 |
| `code_settings/settings_dialog.py` | [`SettingsDialog._create_appearance_tab`](#method-code-settings-settings-dialog-py-settingsdialog-create-appearance-tab) — baseline lines 314–371 |
| `code_settings/settings_dialog.py` | [`SettingsDialog.get_settings`](#method-code-settings-settings-dialog-py-settingsdialog-get-settings) — baseline lines 405–418 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-code-settings-contrast-py"></a>
### CREATE FILE — `code_settings/contrast.py`

**Folder:** `code_settings/` already exists; do not create another package. **Create file:** `contrast.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `relative_luminance` | Return WCAG relative luminance for a valid sRGB QColor. |
| `contrast_ratio` | Return the luminance contrast ratio, with the lighter color divided by the darker color. |
| `read_preferences` | Read optional overrides; missing colors inherit the active lexer theme. |
| `write_preferences` | Persist width and remove reset color keys instead of saving invalid colors. |
| `apply_preferences` | Apply overrides after the lexer has restored its own editor-wide theme. |

<a id="topic-3"></a>
## 3. Provider-Neutral Diagnostics and Problems

### What the feature does

The Problems panel aggregates diagnostic snapshots independently of Ruff's internal model. Each row retains provider, document URI, path, severity, source range, revision, and the original provider payload. Display coordinates are one-based; navigation uses zero-based line and character columns.

### How the code works

DiagnosticsManager owns data keyed by provider and URI. EditorExtensions.publish_diagnostics is the Ruff adapter; ProblemsPanel only displays generic Diagnostic values. The adapter preserves the existing cat/XP behavior in MainWindow. Editing clears stale rows, server replacement clears the provider, and closing or relocating a document removes its old URI collection. Untitled rows navigate to their live owner instead of requiring a disk path.

### Official documentation

- [`QDockWidget`](https://doc.qt.io/archives/qt-5.15/qdockwidget.html)
- [`QTreeWidget`](https://doc.qt.io/archives/qt-5.15/qtreewidget.html)
- [LSP Diagnostic specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic)
- [Qt model/view](https://doc.qt.io/archives/qt-5.15/model-view-programming.html)
- [LSP Diagnostic](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `main.py` | [`MainWindow._on_ruff_diagnostics`](#method-main-py-mainwindow-on-ruff-diagnostics) — baseline lines 722–738 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-ruff-implementation-diagnostics-model-py"></a>
### CREATE FILE — `ruff_implementation/diagnostics_model.py`

**Folder:** `ruff_implementation/` already exists; do not create another package. **Create file:** `diagnostics_model.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `DiagnosticSeverity` | Define application-level severity ordering independently of provider numeric values. |
| `Position` | Zero-based line and Python-character column. |
| `SourceRange` | Store a zero-based half-open range using Python-character columns. |
| `Diagnostic` | Carry provider-neutral diagnostic data while retaining an opaque provider payload for actions. |

<a id="file-ruff-implementation-diagnostics-manager-py"></a>
### CREATE FILE — `ruff_implementation/diagnostics_manager.py`

**Folder:** `ruff_implementation/` already exists; do not create another package. **Create file:** `diagnostics_manager.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `DiagnosticsManager` | Store complete diagnostic snapshots by provider and document. |
| `DiagnosticsManager.__init__` | Create an empty provider/document snapshot map owned by the GUI thread. |
| `DiagnosticsManager.replace` | Validate snapshot identity and replace or remove exactly one provider/document collection. |
| `DiagnosticsManager.clear_document` | Remove every provider collection belonging to one document URI. |
| `DiagnosticsManager.clear_provider` | Remove a provider after its environment or server instance changes. |
| `DiagnosticsManager.all` | Return a deterministic severity/path/position ordering of all retained diagnostics. |

<a id="file-side-bar-widgets-problems-panel-py"></a>
### CREATE FILE — `side_bar_widgets/problems_panel.py`

**Folder:** `side_bar_widgets/` already exists; do not create another package. **Create file:** `problems_panel.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `ProblemsPanel` | Provider-neutral, navigable diagnostic list. |
| `ProblemsPanel.__init__` | Configure six columns and connect row activation to diagnostic navigation. |
| `ProblemsPanel.set_diagnostics` | Replace displayed rows with a complete provider-neutral snapshot. |
| `ProblemsPanel._activate` | Emit the diagnostic stored on the activated row without parsing visible text. |

<a id="topic-4"></a>
## 4. Ruff Quick Fixes

### What the feature does

Right-clicking a current Ruff diagnostic requests textDocument/codeAction through the existing asynchronous language server client. Selecting a supported direct-edit action applies one undoable batch. The request carries Ruff's original diagnostic data and the exact document URI/version.

### How the code works

WorkspaceEditApplier validates the whole action before mutation: identity, revision, resource-operation policy, position encoding, character boundaries, line limits, and nonoverlap. It handles changes and one versioned text-document entry in documentChanges. Valid replacements run from the end of the buffer backward, preserving earlier positions. Command/resolve, annotated, multi-file, and resource-operation actions are rejected visibly as complete units. Mirrored views use their shared document's sole Ruff controller, and stale replies are discarded after edits, closure, relocation, or interpreter replacement.

### Official documentation

- [Ruff editor settings](https://docs.astral.sh/ruff/editors/settings/#codeaction)
- [LSP Code Action](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_codeAction)
- [WorkspaceEdit](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#workspaceEdit)
- [Ruff code-action settings](https://docs.astral.sh/ruff/editors/settings/#codeaction)
- [LSP WorkspaceEdit](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#workspaceEdit)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `ruff_implementation/ruff_lsp_controller.py` | [`RuffLspController.context_menu`](#method-ruff-implementation-ruff-lsp-controller-py-rufflspcontroller-context-menu) — baseline lines 255–258 |
| `ruff_implementation/ruff_lsp_controller.py` | [`RuffLspController.request_quick_fixes`](#method-ruff-implementation-ruff-lsp-controller-py-rufflspcontroller-request-quick-fixes) — new method; insertion boundary below |
| `ruff_implementation/ruff_lsp_controller.py` | [`RuffLspController.apply_code_action`](#method-ruff-implementation-ruff-lsp-controller-py-rufflspcontroller-apply-code-action) — new method; insertion boundary below |
| `python_editor/pythoneditor.py` | [`PythonEditor.contextMenuEvent`](#method-python-editor-pythoneditor-py-pythoneditor-contextmenuevent) — baseline lines 254–280 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-ruff-implementation-workspace-edit-py"></a>
### CREATE FILE — `ruff_implementation/workspace_edit.py`

**Folder:** `ruff_implementation/` already exists; do not create another package. **Create file:** `workspace_edit.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `WorkspaceEditError` | An action cannot be applied completely to the requested revision. |
| `EditorTextEdit` | One checked replacement using absolute UTF-8 byte positions. |
| `WorkspaceEditApplier` | Apply a single-document edit as one undo group after complete validation. |
| `WorkspaceEditApplier.__init__` | Use the requesting Ruff controller's URI, version, and position encoding. |
| `WorkspaceEditApplier._position` | Reject out-of-range positions and split UTF-8/UTF-16 characters. |
| `WorkspaceEditApplier.apply` | Validate identity, version, ranges, annotations and overlap before mutation. |

<a id="topic-5"></a>
## 5. Find All References

### What the feature does

Shift+F12 performs semantic Jedi reference lookup for the symbol at the active Python caret. Results show symbol, path, line, and column and navigate through MainWindow's existing open-file method. The selected workspace and Python interpreter are passed to Jedi.

### How the code works

ReferencesFinder retains the existing latest-request worker pattern, with a generation increment on edits/cursor/environment changes. It returns plain tuples, which PythonEditor converts to SourceLocation values on the GUI thread. The worker joins _analysis_workers so a closed tab stays alive until its worker exits. Jedi's shared mutable fast parser is disabled because the repository's separate analysis helpers can run concurrently. A result is shown only while its source view is current.

### Official documentation

- [`jedi.Script.get_references`](https://jedi.readthedocs.io/en/latest/docs/api.html#jedi.Script.get_references)
- [Jedi API](https://jedi.readthedocs.io/en/latest/docs/api.html)
- [`QThread`](https://doc.qt.io/archives/qt-5.15/qthread.html)
- [LSP references](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_references)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `python_editor/pythoneditor.py` | [`PythonEditor.find_all_references`](#method-python-editor-pythoneditor-py-pythoneditor-find-all-references) — new method; insertion boundary below |
| `python_editor/pythoneditor.py` | [`PythonEditor._analysis_workers`](#method-python-editor-pythoneditor-py-pythoneditor-analysis-workers) — baseline lines 568–576 |
| `main.py` | [`MainWindow._restart_ruff`](#method-main-py-mainwindow-restart-ruff) — baseline lines 740–769 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-code-inteligence-locations-panel-py"></a>
### CREATE FILE — `code_inteligence/locations_panel.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `locations_panel.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `SourceLocation` | Store a disk path and zero-based line/character column for navigation. |
| `LocationsPanel` | Display provider-independent reference locations and emit selected records. |
| `LocationsPanel.__init__` | Create the symbol/path/line/column view and connect row activation. |
| `LocationsPanel.set_locations` | Sort and replace rows while retaining each original location as hidden item data. |
| `LocationsPanel._activate` | Emit the source location attached to the activated row. |

<a id="file-code-inteligence-references-finder-py"></a>
### REPLACE FILE — `code_inteligence/references_finder.py`

**Folder:** `code_inteligence/` already exists. **File:** `references_finder.py`. **Placement:** replace the whole file, baseline lines 1–64, including imports. Delete the previous contents rather than keeping duplicate definitions.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `ReferencesFinder` | Find references without blocking, replaying only the newest request. |
| `ReferencesFinder.__init__` | Initialize latest-request generations and replay pending work after the active thread finishes. |
| `ReferencesFinder.find_references` | Capture plain source, caret, project and interpreter values for the newest request. |
| `ReferencesFinder._start_pending` | Start only the most recent queued request when the previous worker finishes. |
| `ReferencesFinder.run` | Run semantic Jedi reference lookup off the GUI thread and emit plain locations or an error. |
| `ReferencesFinder.shutdown` | Reject future/results requests; completion remains asynchronous. |
| `ReferencesFinder.invalidate` | Reject in-flight results without forcibly terminating a running thread. |
| `ReferencesFinder.generation` | Expose the current GUI-side request generation for delivery checks. |

<a id="topic-6"></a>
## 6. Shared Document State and Enhanced Tabs

### What the feature does

A document owns text identity, dirty/read-only/external flags, and its disk digest. Each view owns cursor, selection, scroll, pin, and preview state. Duplicate View Right shares the QsciDocument while retaining independent view placement. Pinning protects ordinary close actions; single-click file-tree previews become permanent when edited or double-clicked.

### How the code works

DocumentStateStore is the source of truth. DirtyViews preserves the existing _dirty_editors interface without retaining a second dirty set: membership checks all views and iteration yields one representative per dirty document. Close prompts occur only on the final view, saves clean every view, Save As and rename retarget every view, and editor-mode conversion replaces all views together. Closing the Ruff owner explicitly closes its synchronizer and opens one on a surviving view. Session records restore duplicate views, positions, and pins. Reopen stores disk paths only, with a twenty-entry bound; it is not an unsaved-buffer recovery feature.

### Official documentation

- [`QsciDocument`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciDocument.html)
- [`QTabBar`](https://doc.qt.io/archives/qt-5.15/qtabbar.html)
- [`weakref`](https://docs.python.org/3/library/weakref.html)
- [`QTabWidget`](https://doc.qt.io/archives/qt-5.15/qtabwidget.html)
- [MutableSet adapter](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `main.py` | [`MainWindow.__init__`](#method-main-py-mainwindow-init) — baseline lines 142–235 |
| `main.py` | [`MainWindow._connect_editor`](#method-main-py-mainwindow-connect-editor) — baseline lines 686–706 |
| `main.py` | [`MainWindow.set_new_tab`](#method-main-py-mainwindow-set-new-tab) — baseline lines 1749–1816 |
| `main.py` | [`MainWindow.close_editor`](#method-main-py-mainwindow-close-editor) — baseline lines 2155–2185 |
| `main.py` | [`MainWindow._dispose_editor`](#method-main-py-mainwindow-dispose-editor) — baseline lines 2187–2198 |
| `main.py` | [`MainWindow._save_editor_to_path`](#method-main-py-mainwindow-save-editor-to-path) — baseline lines 2510–2589 |
| `main.py` | [`MainWindow.save_as`](#method-main-py-mainwindow-save-as) — baseline lines 2619–2672 |
| `main.py` | [`MainWindow.on_file_rename`](#method-main-py-mainwindow-on-file-rename) — baseline lines 2207–2257 |
| `main.py` | [`MainWindow._convert_editor`](#method-main-py-mainwindow-convert-editor) — baseline lines 2836–2900 |
| `main.py` | [`MainWindow.save_session`](#method-main-py-mainwindow-save-session) — baseline lines 3208–3261 |
| `main.py` | [`MainWindow._restore_session`](#method-main-py-mainwindow-restore-session) — baseline lines 3263–3344 |
| `main.py` | [`MainWindow.closeEvent`](#method-main-py-mainwindow-closeevent) — baseline lines 3153–3206 |
| `side_bar_widgets/file_manager.py` | [`FileManager.tree_view_clicked`](#method-side-bar-widgets-file-manager-py-filemanager-tree-view-clicked) — baseline lines 112–116 |
| `side_bar_widgets/file_manager.py` | [`FileManager._open_permanent`](#method-side-bar-widgets-file-manager-py-filemanager-open-permanent) — new method; insertion boundary below |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-code-inteligence-document-state-py"></a>
### CREATE FILE — `code_inteligence/document_state.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `document_state.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
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

<a id="topic-7"></a>
## 7. External File and Directory Watching

### What the feature does

File and parent-directory watches detect edits, atomic replacement, deletion, and recreation of open files. Burst events trigger background reads that hash the same bytes returned to the window. A clean document can reload; a dirty document receives an external-change marker and an explicit reload/overwrite/compare/cancel choice when saved.

### How the code works

FileWatchService retains watched logical paths and symlink targets, rearms file watches after replacements, and sends immutable read results through a queued Qt signal. Each request captures the document revision and accepted disk digest; obsolete results cannot overwrite a newer save or edit. Matching digests suppress delayed notifications from the editor's own atomic saves. Existing filesystem-model updates and periodic/manual Git refresh remain in place; document watches are not treated as complete coverage of every path in a repository.

### Official documentation

- [`QFileSystemWatcher`](https://doc.qt.io/archives/qt-5.15/qfilesystemwatcher.html)
- [`QFileInfo`](https://doc.qt.io/archives/qt-5.15/qfileinfo.html)
- [`os.stat`](https://docs.python.org/3/library/os.html#os.stat)
- [`QTimer`](https://doc.qt.io/archives/qt-5.15/qtimer.html)
- [`pathlib`](https://docs.python.org/3/library/pathlib.html)
- [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor)
- [Hashing](https://docs.python.org/3/library/hashlib.html)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `main.py` | [`MainWindow._save_editor_to_path`](#method-main-py-mainwindow-save-editor-to-path) — baseline lines 2510–2589 |
| `main.py` | [`MainWindow._background_work_running`](#method-main-py-mainwindow-background-work-running) — baseline lines 3101–3144 |
| `main.py` | [`MainWindow.closeEvent`](#method-main-py-mainwindow-closeevent) — baseline lines 3153–3206 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-code-inteligence-file-watch-service-py"></a>
### CREATE FILE — `code_inteligence/file_watch_service.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `file_watch_service.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
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

<a id="file-side-bar-widgets-comparison-dialog-py"></a>
### CREATE FILE — `side_bar_widgets/comparison_dialog.py`

**Folder:** `side_bar_widgets/` already exists; do not create another package. **Create file:** `comparison_dialog.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `ComparisonDialog` | Show two snapshots with line highlights and synchronized scrolling. |
| `ComparisonDialog.__init__` | Build read-only panes; acceptance never writes a file by itself. |
| `ComparisonDialog._scroll` | Map proportional scroll positions without feedback recursion. |
| `ComparisonDialog._highlight` | Color changed source lines, leaving both snapshots immutable. |

<a id="topic-8"></a>
## 8. Snippets and Reusable Templates

### What the feature does

The built-in catalog provides Python and Markdown snippets. Insert Snippet uses the active document; New From Template opens the same starter in an unsaved document of the appropriate language. Supported fields use ${number:default}; numeric order controls navigation, with field zero last. Tab and Shift+Tab move between fields, and Escape ends navigation.

### How the code works

The parser calculates ranges in the marker-free Unicode string. SnippetController converts those ranges to absolute UTF-8 byte positions before inserting one undoable edit. SCN_MODIFIED supplies actual edit positions, allowing field ranges to move by spatial position even when numeric field order differs. An edit outside the active field cancels navigation. Repeated numbers are independent fields; mirroring, choices, nested marker syntax, and user JSON catalogs are not added implicitly. Original editor key handling remains after the snippet checks.

### Official documentation

- [`QsciScintilla`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)
- [`QsciScintilla` class reference](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)
- [`QKeyEvent`](https://doc.qt.io/archives/qt-5.15/qkeyevent.html)
- [`QStandardPaths`](https://doc.qt.io/archives/qt-5.15/qstandardpaths.html)
- [`json`](https://docs.python.org/3/library/json.html)
- [Scintilla modification notifications](https://www.scintilla.org/ScintillaDoc.html#SCN_MODIFIED)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `python_editor/pythoneditor.py` | [`PythonEditor.__init__`](#method-python-editor-pythoneditor-py-pythoneditor-init) — baseline lines 37–179 |
| `python_editor/pythoneditor.py` | [`PythonEditor.keyPressEvent`](#method-python-editor-pythoneditor-py-pythoneditor-keypressevent) — baseline lines 402–459 |
| `markdown_editor/markdowneditor.py` | [`MarkdownEditor.__init__`](#method-markdown-editor-markdowneditor-py-markdowneditor-init) — baseline lines 13–61 |
| `markdown_editor/markdowneditor.py` | [`MarkdownEditor.keyPressEvent`](#method-markdown-editor-markdowneditor-py-markdowneditor-keypressevent) — baseline lines 90–94 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-code-inteligence-snippet-parser-py"></a>
### CREATE FILE — `code_inteligence/snippet_parser.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `snippet_parser.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `Placeholder` | One editable half-open character range in rendered snippet text. |
| `ParsedSnippet` | Marker-free insertion text and its ordered placeholder ranges. |
| `parse_snippet` | Remove markers and calculate spans against the resulting Unicode text. |

<a id="file-code-inteligence-snippet-controller-py"></a>
### CREATE FILE — `code_inteligence/snippet_controller.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `snippet_controller.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `SnippetController` | Navigate supported fields and cancel on edits outside the active field. |
| `SnippetController.__init__` | Observe modification positions rather than guessing from total text length. |
| `SnippetController.active` | Return whether a field is currently available for Tab navigation. |
| `SnippetController.cancel` | Forget navigation ranges while retaining all inserted text. |
| `SnippetController.insert` | Replace the selection once and convert character fields to byte ranges. |
| `SnippetController._modified` | Update fields by actual edit position; reject edits outside the active field. |
| `SnippetController.handle_tab` | Move to the previous/next field, or finish after the final field. |
| `SnippetController._select_active` | Select the active byte span through QScintilla's Unicode-aware conversion. |

<a id="file-code-inteligence-snippet-catalog-py"></a>
### CREATE FILE — `code_inteligence/snippet_catalog.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `snippet_catalog.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `Snippet` | Named insertion available to the palette and editor menu. |
| `SnippetCatalog` | Query immutable snippets by editor language. |
| `SnippetCatalog.__init__` | Create immutable built-in Markdown and Python snippets with numbered fields. |
| `SnippetCatalog.for_language` | Return snippets whose declared language matches exactly. |
| `SnippetCatalog.all` | Expose the immutable built-in catalog to menus without private-field access. |

<a id="topic-9"></a>
## 9. Code Folding

### What the feature does

Folding adds collapsible Python indentation blocks and complete multiline strings, plus Markdown heading sections, fences, lists, and quoted blocks. It is an editing-oriented fold model that can keep working while source is incomplete. The margin and Toggle Fold/Fold All/Unfold All commands operate on existing editor views.

### How the code works

FoldLine separates pure depth/header calculation from Scintilla messages. FoldingController debounces updates and publishes fold metadata only when source changes. Markdown lookahead is precomputed, and a closing fence must match the delimiter and minimum opening length. Python indentation is resilient rather than a complete grammar parser; temporary syntax errors retain that model when tokenization cannot finish. The commands use foldLine and explicit expanded flags; QScintilla.foldAll's Boolean parameter is not used as a false-means-unfold switch.

### Official documentation

- [Folding](https://www.scintilla.org/ScintillaDoc.html#Folding)
- [`setFolding()`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)
- [`QsciScintilla`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)
- [`tokenize`](https://docs.python.org/3/library/tokenize.html)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `python_editor/pythoneditor.py` | [`PythonEditor.__init__`](#method-python-editor-pythoneditor-py-pythoneditor-init) — baseline lines 37–179 |
| `markdown_editor/markdowneditor.py` | [`MarkdownEditor.__init__`](#method-markdown-editor-markdowneditor-py-markdowneditor-init) — baseline lines 13–61 |
| `main.py` | [`MainWindow._apply_editor_settings`](#method-main-py-mainwindow-apply-editor-settings) — baseline lines 1664–1738 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-code-inteligence-fold-model-py"></a>
### CREATE FILE — `code_inteligence/fold_model.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `fold_model.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `FoldLine` | Fold depth and whether a line opens a collapsible region. |
| `_indent_columns` | Expand leading tabs to Python-compatible eight-column boundaries. |
| `python_fold_lines` | Infer resilient indentation folds without requiring valid Python syntax. |
| `markdown_fold_lines` | Calculate heading hierarchy and fenced-block folds for Markdown. |

<a id="file-code-inteligence-folding-controller-py"></a>
### CREATE FILE — `code_inteligence/folding_controller.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `folding_controller.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `FoldingController` | Own folding configuration and incremental scheduling for one editor. |
| `FoldingController.__init__` | Configure the folding margin and debounce model recalculation after text changes. |
| `FoldingController.schedule` | Restart the short quiet-period timer after an edit. |
| `FoldingController.recalculate` | Compute and publish fold metadata when document text changed. |
| `FoldingController.set_all` | Set all fold headers explicitly; do not interpret foldAll's children flag as state. |

<a id="topic-10"></a>
## 10. Document Minimap

### What the feature does

Each editor view has its own optional overview, enabled through Editor Tools → Show Minimap. It draws bounded-width line strokes and a viewport rectangle. Clicking or dragging moves the observed editor without changing its text. Duplicate views share text but retain independent minimap viewport positions.

### How the code works

The widget caches line lengths after edits, defers rebuilding while hidden, and paints at most approximately one representative stroke per pixel row. QScintilla display-line/document-line conversion keeps navigation useful around folded or wrapped text. ensureLineVisible reveals a clicked target before scrolling. Theme values come from the actual lexer accessors; there is no invented MainWindow.theme dictionary. The overlay reserves its width with SCI_SETMARGINRIGHT and releases that space when hidden.

### Official documentation

- [`QWidget`](https://doc.qt.io/archives/qt-5.15/qwidget.html)
- [`QPainter`](https://doc.qt.io/archives/qt-5.15/qpainter.html)
- [`SCI_LINESONSCREEN`](https://www.scintilla.org/ScintillaDoc.html#SCI_LINESONSCREEN)
- [`QsciScintilla`](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciScintilla.html)

### Existing-file connections

| File | Definition and placement |
|---|---|
| `python_editor/pythoneditor.py` | [`PythonEditor.__init__`](#method-python-editor-pythoneditor-py-pythoneditor-init) — baseline lines 37–179 |
| `markdown_editor/markdowneditor.py` | [`MarkdownEditor.__init__`](#method-markdown-editor-markdowneditor-py-markdowneditor-init) — baseline lines 13–61 |
| `main.py` | [`MainWindow._apply_editor_settings`](#method-main-py-mainwindow-apply-editor-settings) — baseline lines 1664–1738 |

The feature files below are complete. Their shared window connections are implemented by [EditorExtensions](#file-code-inteligence-editor-extensions-py) and the linked combined method replacements in [Application integration](#application-integration).

<a id="file-side-bar-widgets-editor-minimap-py"></a>
### CREATE FILE — `side_bar_widgets/editor_minimap.py`

**Folder:** `side_bar_widgets/` already exists; do not create another package. **Create file:** `editor_minimap.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
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

<a id="topic-11"></a>
## 11. Git Branch Indicator and Commit Graph

### What the feature does

The current repository already implements this topic. Keep its GitService, immutable history models, graph layout, themed commit graph, status label, and refresh actions. Adding the older course's alternative service would duplicate workers and conflict with the current UI.

### How the code works

GitHistoryWorker obtains root, branch/detached identity, and bounded parent-aware history off the GUI thread. GitService owns latest-request delivery and shutdown. parse_log validates structured records; layout_graph turns parent relationships into lanes and edges; CommitGraphPanel draws those records and opens commit details. MainWindow refreshes file colors and history together. The watcher added in Topic 7 invokes that existing coordinator.

### Official documentation

- [`git log`](https://git-scm.com/docs/git-log)
- [pretty formats](https://git-scm.com/docs/pretty-formats)
- [`git symbolic-ref`](https://git-scm.com/docs/git-symbolic-ref)
- [`git rev-parse`](https://git-scm.com/docs/git-rev-parse)
- [`subprocess`](https://docs.python.org/3/library/subprocess.html)
- [`QThread`](https://doc.qt.io/archives/qt-5.15/qthread.html)
- [`QTreeWidget`](https://doc.qt.io/archives/qt-5.15/qtreewidget.html)

### Keep the current Git files

No Git file or folder needs creating or deleting. Keep the following current files; the new watcher calls `MainWindow._refresh_git_state()` rather than creating another Git service.

<a id="file-git-implementation-history-py"></a>
### KEEP FILE — `git_implementation/history.py`

**Folder/file:** `git_implementation/history.py` already exists. **Action:** keep its current contents. The complete existing implementation is shown here to explain how this topic works; do not add a second copy or install the older course alternative.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `GitCommit` | One immutable commit returned by the selected repository. |
| `GitSnapshot` | Branch/HEAD identity and a topologically ordered history page. |
| `GraphRow` | A commit plus a compact text representaion of its active lanes. |
| `parse_log` | Parse the record/unit-separated output produced by GitHistoryWorker. |
| `layout_graph` | Assign stable columns and mark merges for a compact graph view. |

<a id="file-git-implementation-git-service-py"></a>
### KEEP FILE — `git_implementation/git_service.py`

**Folder/file:** `git_implementation/git_service.py` already exists. **Action:** keep its current contents. The complete existing implementation is shown here to explain how this topic works; do not add a second copy or install the older course alternative.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
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

<a id="file-git-ui-commit-graph-py"></a>
### KEEP FILE — `git_ui/commit_graph.py`

**Folder/file:** `git_ui/commit_graph.py` already exists. **Action:** keep its current contents. The complete existing implementation is shown here to explain how this topic works; do not add a second copy or install the older course alternative.

````python
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
````

**Code explanation**

| Class, function, or method | Responsibility |
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

### Existing branch-label and refresh connections

Keep these methods in `main.py`. They are already connected by `MainWindow.init_ui()` and the existing menu/timer setup. The code is shown for explanation, not as an additional definition.

**Existing location:** `main.py`, `MainWindow._on_git_snapshot`, baseline lines 384–391.

````python
    def _on_git_snapshot(self, snapshot) -> None:
        """Update branch identity and graph from the same Git snapshot."""
        identity = snapshot.branch or (
            f"detached@{snapshot.head_short}" if snapshot.head_short else "unborn"
        )
        self.git_branch_label.setText(f"Git: {identity}")
        self.git_branch_label.setToolTip(str(snapshot.root))
        self.git_graph.set_snapshot(snapshot)
````

**Existing location:** `main.py`, `MainWindow._refresh_git_state`, baseline lines 413–427.

````python
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
````

**Existing location:** `main.py`, `MainWindow._refresh_git_history`, baseline lines 429–433.

````python
    def _refresh_git_history(self) -> None:
        """Request history for the current FileManager root, if one is open."""
        folder = self.file_manager.current_folder
        if folder:
            self.git_service.refresh(Path(folder))
````

<a id="application-integration"></a>
## Application integration

Create the shared coordinator below, then apply the existing-file edits in the order shown. It uses the existing `MainWindow`, `MultiTabView`, editor classes, Ruff client, and Git service. It does not create another application window or replace existing subprocess protocols.

The document store is initialized before UI construction. The coordinator is initialized after `init_ui()` and before settings/session restoration. This ensures its docks, actions, and file watcher exist before restored editors publish events.

<a id="file-code-inteligence-editor-extensions-py"></a>
### CREATE FILE — `code_inteligence/editor_extensions.py`

**Folder:** `code_inteligence/` already exists; do not create another package. **Create file:** `editor_extensions.py`. **Placement:** line 1 of the new file. Paste the following complete contents, including imports.

````python
"""Connect course features to the repository's existing MainWindow workflows."""
import hashlib
import json
import os
from pathlib import Path
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAction, QDockWidget, QInputDialog, QMenu, QMessageBox
from PyQt5.Qsci import QsciScintilla
from code_inteligence.command_registry import CommandRegistry
from code_inteligence.command_palette import CommandPaletteDialog
from code_inteligence.locations_panel import LocationsPanel
from code_inteligence.file_watch_service import FileWatchService
from code_inteligence.snippet_catalog import SnippetCatalog
from ruff_implementation.diagnostics_manager import DiagnosticsManager
from ruff_implementation.diagnostics_model import Diagnostic, DiagnosticSeverity, Position, SourceRange
from ruff_implementation.ruff_diagnostics_model import RuffSeverity
from ruff_implementation.ruff_lsp_controller import RuffLspController
from side_bar_widgets.problems_panel import ProblemsPanel
from python_editor.pythoneditor import PythonEditor
from markdown_editor.markdowneditor import MarkdownEditor


class EditorExtensions(QObject):
    """Coordinate actions, diagnostics, shared views, and asynchronous file snapshots."""

    def __init__(self, window):
        """Install features after the base UI exists and before restoring session tabs."""
        super().__init__(window)
        self.window = window
        self.store = window.documents
        self.store.stateChanged.connect(self.refresh_titles)
        self.diagnostics = DiagnosticsManager(window)
        self.problems = ProblemsPanel(window)
        self.problems_dock = self._dock("Problems", "ProblemsDock", self.problems)
        self.diagnostics.changed.connect(self.problems.set_diagnostics)
        self.problems.diagnosticActivated.connect(self.open_problem)
        self.references = LocationsPanel(window)
        self.references_dock = self._dock("References", "ReferencesDock", self.references)
        self.references.locationActivated.connect(self.open_reference)
        self.watcher = FileWatchService(window)
        self.watcher.hints.connect(self.disk_hints)
        self.watcher.result.connect(self.disk_result)
        self.catalog = SnippetCatalog()
        self.registry = CommandRegistry(window)
        self.palette = CommandPaletteDialog(self.registry, window)
        self._install_menu()
        self.registry.refresh_menus(window.menuBar())

    def _dock(self, title, name, widget):
        """Create one named dock compatible with QMainWindow layout persistence."""
        dock = QDockWidget(title, self.window)
        dock.setObjectName(name)
        dock.setWidget(widget)
        self.window.addDockWidget(Qt.BottomDockWidgetArea, dock)
        dock.hide()
        return dock

    def _action(self, menu, identifier, title, callback, shortcut=None):
        """Create one QAction shared by the menu and dynamically refreshed palette."""
        action = menu.addAction(title)
        action.setObjectName(identifier)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(lambda _checked=False: callback())
        return action

    def _install_menu(self):
        """Expose course commands without rebuilding any existing menu callbacks."""
        menu = self.window.menuBar().addMenu("Editor Tools")
        self._action(menu, "workbench.command_palette", "Command Palette", self.palette.open_palette, "Ctrl+Shift+L")
        menu.addAction(self.problems_dock.toggleViewAction())
        menu.addAction(self.references_dock.toggleViewAction())
        self._action(menu, "edit.references", "Find All References", self.find_references, "Shift+F12")
        self._action(menu, "tabs.reopen", "Reopen Closed Tab", self.reopen, "Ctrl+Shift+T")
        self._action(menu, "tabs.search", "Search Open Tabs", self.search_tabs)
        self._action(menu, "tabs.sort", "Sort Active Group", self.sort_tabs)
        self._action(menu, "tabs.duplicate", "Duplicate View Right", lambda: self.duplicate(self.window.current_editor()))
        self._action(menu, "view.fold.toggle", "Toggle Fold", self.toggle_fold, "Ctrl+Shift+[")
        self._action(menu, "view.fold.all", "Fold All", lambda: self.fold_all(False))
        self._action(menu, "view.fold.none", "Unfold All", lambda: self.fold_all(True))
        self.minimap_action = menu.addAction("Show Minimap")
        self.minimap_action.setObjectName("view.minimap")
        self.minimap_action.setCheckable(True)
        self.minimap_action.setChecked(self.window.settings.value("editor/show_minimap", False, type=bool))
        self.minimap_action.toggled.connect(self.toggle_minimap)
        self.snippet_actions = []
        snippets = menu.addMenu("Insert Snippet")
        templates = menu.addMenu("New From Template")
        for snippet in self.catalog.all():
            action = self._action(snippets, "snippet." + snippet.identifier, snippet.title,
                                  lambda item=snippet: self.insert_snippet(item))
            self.snippet_actions.append((action, snippet))
            self._action(templates, "template." + snippet.identifier, snippet.title,
                         lambda item=snippet: self.insert_snippet(item, new=True))
        self.current_changed(None)

    def attach(self, editor):
        """Initialize shared metadata and connect view-specific feature signals once."""
        document = self.store.attach(editor, getattr(editor, "path", None))
        document.disk_digest = getattr(editor, "_disk_digest", document.disk_digest)
        if document.path is not None:
            document.read_only = not os.access(document.path, os.W_OK)
            editor.setReadOnly(document.read_only)
            self.watcher.watch_file(document.path)
        if isinstance(editor, PythonEditor):
            editor.referencesReady.connect(lambda rows, ed=editor: self.show_references(ed, rows))
            editor.referencesFailed.connect(lambda message: self.window.statusBar().showMessage(message, 6000))
        self.apply_minimap(editor)
        self.refresh_titles(document)

    def refresh_titles(self, document):
        """Derive every view's tab title from shared state and per-view pin/preview flags."""
        for view in list(document.views):
            tab = self.store.tab(view)
            name = document.path.name if document.path else "Untitled"
            title = ("● " if document.dirty else "") + name
            title += " [pinned]" if tab.pinned else " [preview]" if tab.preview else ""
            title += " [RO]" if document.read_only else ""
            title += " [external]" if document.externally_changed else ""
            self.window.tab_view.set_editor_title(view, title)
            self.window.tab_view.set_editor_tooltip(view, str(document.path or "Untitled"))

    def current_changed(self, editor):
        """Update language-specific command enablement for the selected view."""
        language = "python" if isinstance(editor, PythonEditor) else "markdown"
        for action, snippet in self.snippet_actions:
            action.setEnabled(editor is not None and not editor.isReadOnly() and language in snippet.languages)

    def apply_minimap(self, editor):
        """Use real lexer theme accessors after settings replace the lexer."""
        lexer = editor.lexer()
        background = lexer.editor_color("paper-color", "#1e1f22") if hasattr(lexer, "editor_color") else QColor("#1e1f22")
        foreground = lexer.color(0) if lexer else QColor("#858585")
        editor.minimap.set_colors(background, foreground, QColor(120, 150, 190, 75))
        editor.minimap.set_map_visible(self.window.settings.value("editor/show_minimap", False, type=bool))

    def toggle_minimap(self, visible):
        """Persist visibility and update each view's independently owned overview."""
        self.window.settings.setValue("editor/show_minimap", bool(visible))
        for editor in self.window.tab_view.all_editors():
            self.apply_minimap(editor)

    def toggle_fold(self):
        """Toggle the active line using QScintilla's foldLine slot."""
        editor = self.window.current_editor()
        if editor is not None:
            editor.folding_controller.recalculate()
            editor.foldLine(editor.getCursorPosition()[0])

    def fold_all(self, expanded):
        """Set every fold header to a specific expanded/collapsed state."""
        editor = self.window.current_editor()
        if editor is not None:
            editor.folding_controller.set_all(expanded)

    def insert_snippet(self, snippet, new=False):
        """Insert into the active editor or create an unsaved template of the right type."""
        if new:
            previous = self.window.python_editor_active
            self.window.python_editor_active = "python" in snippet.languages
            try:
                editor = self.window.new_file()
            finally:
                self.window.python_editor_active = previous
        else:
            editor = self.window.current_editor()
        language = "python" if isinstance(editor, PythonEditor) else "markdown"
        if editor is not None and language in snippet.languages:
            editor.snippets.insert(snippet.body)

    def find_references(self):
        """Request references from the active Python view without constructing an editor."""
        editor = self.window.current_editor()
        if isinstance(editor, PythonEditor):
            editor.find_all_references()

    def show_references(self, editor, rows):
        """Reject a result belonging to a now-inactive source view."""
        if editor is self.window.current_editor():
            self.references.set_locations(rows)
            self.references_dock.show()
            self.references_dock.raise_()

    def open_reference(self, location):
        """Navigate using zero-based semantic-provider coordinates."""
        self.window._open_file_at_position(str(location.path), location.line, location.column)

    def publish_diagnostics(self, editor, rows):
        """Adapt Ruff diagnostics at one boundary; preserve raw provider payloads."""
        owner = editor.ruff_lsp
        if owner is None or owner._closed:
            return
        levels = {RuffSeverity.ERROR: DiagnosticSeverity.ERROR,
                  RuffSeverity.WARNING: DiagnosticSeverity.WARNING, RuffSeverity.INFO: DiagnosticSeverity.INFORMATION}
        path = Path(editor.path) if editor.path else None
        values = [Diagnostic("ruff", owner.uri, path,
                    SourceRange(Position(item.start.line, item.start.column), Position(item.end.line, item.end.column)),
                    levels[item.severity], item.code, item.message, item.revision, item) for item in rows]
        self.diagnostics.replace("ruff", owner.uri, values)

    def open_problem(self, diagnostic):
        """Navigate saved files or find the live owner of an untitled diagnostic URI."""
        for doc in self.store.all():
            owner = doc.analysis_owner
            controller = getattr(owner, "ruff_lsp", None)
            if controller and controller.uri == diagnostic.uri:
                self.window.tab_view.focus_editor(owner)
                point = diagnostic.source_range.start
                owner.setCursorPosition(point.line, point.column)
                return
        if diagnostic.path:
            point = diagnostic.source_range.start
            self.window._open_file_at_position(str(diagnostic.path), point.line, point.column)

    def retarget(self, editor, path):
        """Update every view's path and bytes metadata after a successful save or rename."""
        document = self.store.document(editor)
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
                view.references_finder.invalidate()
        owner = document.analysis_owner
        if isinstance(owner, PythonEditor) and owner.ruff_lsp:
            new_uri = Path(path).resolve().as_uri()
            if owner.ruff_lsp.uri != new_uri:
                self.diagnostics.clear_document(owner.ruff_lsp.uri)
                owner.ruff_lsp.relocate(path)
        self.watcher.retain([doc.path for doc in self.store.all() if doc.path])
        self.refresh_titles(document)

    def clean(self, editor):
        """Commit shared clean metadata after save and update every view title."""
        document = self.store.document(editor)
        document.dirty = False
        document.externally_changed = False
        document.disk_digest = getattr(editor, "_disk_digest", None)
        document.revision += 1
        for view in document.views:
            view._disk_digest = document.disk_digest
            view.setModified(False)
        self.store.stateChanged.emit(document)

    def duplicate(self, source, group=None):
        """Create an independent view over the same Scintilla document and state."""
        if source is None:
            return None
        document = self.store.document(source)
        if isinstance(source, PythonEditor):
            view = PythonEditor(path=source.path, is_python_file=True, ruff_lsp_client=None)
        else:
            view = MarkdownEditor(path=source.path, is_python_file=False)
        view.setDocument(source.document())
        for name in ("_utf8_bom", "_disk_digest", "_save_target"):
            setattr(view, name, getattr(source, name, None))
        view.setEolMode(source.eolMode())
        view.setReadOnly(document.read_only)
        self.store.attach(view, document=document)
        self.window._apply_editor_settings(view, self.window._current_settings)
        self.window._connect_editor(view)
        if group is None:
            group = self.window.tab_view._create_group(after=self.window.tab_view.group_for_editor(source))
        self.window.tab_view.add_editor(view, "", group)
        view.setCursorPosition(*source.getCursorPosition())
        self.refresh_titles(document)
        return view

    def detach(self, view, remember=False, transfer=True):
        """Detach a tab and transfer the sole Ruff synchronizer before retiring its owner."""
        if view not in self.store.documents:
            return
        document = self.store.document(view)
        if remember:
            self.store.remember_closed(view, isinstance(view, PythonEditor))
        others = [item for item in document.views if item is not view]
        controller = getattr(view, "ruff_lsp", None)
        if controller is not None:
            self.diagnostics.clear_document(controller.uri)
            controller.shutdown()
            view.ruff_lsp = None
        self.store.detach(view)
        if transfer and others and controller is not None:
            owner = others[0]
            document.analysis_owner = owner
            owner.ruff_lsp = RuffLspController(owner, self.window.ruff_lsp_client)
            owner.ruff_lsp.diagnostics_changed.connect(self.window._on_ruff_diagnostics)
            owner.ruff_lsp.sync_from_editor()
        self.watcher.retain([doc.path for doc in self.store.all() if doc.path])

    def prepare_preview(self, path, group):
        """Replace only an unpinned, clean preview in the requested group."""
        existing = self.window.tab_view.find_editor_by_path(path)
        if existing is not None:
            return
        for index in range(group.count()):
            view = group.widget(index)
            tab = self.store.tab(view)
            if tab.preview and not tab.pinned and not self.store.document(view).dirty:
                self.window.close_editor(view)
                break

    def reopen(self):
        """Reopen the latest available disk-backed location without restoring stale widgets."""
        while self.store.recently_closed:
            item = self.store.recently_closed.pop(0)
            if item.path.is_file():
                view = self.window.set_new_tab(item.path, is_python_file=item.python_mode)
                if view:
                    view.setCursorPosition(item.line, item.column)
                break

    def search_tabs(self):
        """Select from distinct numbered entries even when filenames are duplicated."""
        views = self.window.tab_view.all_editors()
        labels = [f"{index + 1}: {view.path or 'Untitled'}" for index, view in enumerate(views)]
        if labels:
            selected, accepted = QInputDialog.getItem(self.window, "Open tabs", "Tab", labels, 0, True)
            if accepted and selected in labels:
                self.window.tab_view.focus_editor(views[labels.index(selected)])

    def sort_tabs(self):
        """Reorder the active group's existing tabs, with pinned tabs first."""
        group = self.window.tab_view.active_group()
        desired = sorted([group.widget(i) for i in range(group.count())],
                         key=lambda view: (not self.store.tab(view).pinned, str(view.path or '').casefold()))
        for index, view in enumerate(desired):
            group.tabBar().moveTab(group.indexOf(view), index)

    def tab_menu(self, group, position):
        """Use the clicked group for pin, close-right, path and duplicate operations."""
        bar = group.tabBar()
        index = bar.tabAt(bar.mapFrom(group, position))
        if index < 0:
            return
        view = group.widget(index)
        tab = self.store.tab(view)
        menu = QMenu(self.window)
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
            self.refresh_titles(self.store.document(view))
        elif selected is close:
            self.window.close_editor(view)
        elif selected in (others, right):
            targets = self.window.tab_view.all_editors() if selected is others else [group.widget(i) for i in range(index + 1, group.count())]
            for target in list(targets):
                if target is not view and not self.store.tab(target).pinned:
                    if self.window.close_editor(target) is False:
                        break
        elif selected is duplicate:
            self.duplicate(view)
        elif selected is copy:
            self.window._copy_tab_path(view)
        elif selected is reveal:
            self.window._reveal_tab_in_file_manager(view)

    def disk_hints(self, paths):
        """Read affected documents with revision tokens and refresh the existing Git service."""
        for document in self.store.all():
            if document.path and any(p.resolve() == document.path.resolve() for p in paths):
                self.watcher.probe(document.path, (document, document.revision, document.disk_digest))
        self.window._refresh_git_state()

    def disk_result(self, path, token, raw, digest, error):
        """Ignore obsolete snapshots; reload clean documents and flag dirty/deleted ones."""
        document, revision, expected = token
        if document not in self.store.all() or document.revision != revision or document.disk_digest != expected:
            return
        if digest == document.disk_digest and error is None:
            return  # Delayed notification from our own successful atomic save.
        if error or document.dirty:
            document.externally_changed = True
            self.store.stateChanged.emit(document)
            return
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeError:
            document.externally_changed = True
            self.store.stateChanged.emit(document)
            return
        views = list(document.views)
        positions = {view: (view.getCursorPosition(), view.firstVisibleLine()) for view in views}
        for view in views:
            view._loading_text = True
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
        self.clean(owner)

    def shutdown(self):
        """Stop filesystem work; MainWindow retains ownership until completion drains."""
        self.watcher.shutdown()

    def resolve_external(self, editor, raw):
        """Require an explicit overwrite, reload, compare or cancel decision before saving."""
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeError as error:
            QMessageBox.warning(self.window, "External change", str(error))
            return False
        box = QMessageBox(self.window)
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
            ComparisonDialog(editor.text(), text, "Editor versus disk", self.window,
                             accept_text="Close comparison").exec_()
        elif chosen is reload:
            document = self.store.document(editor)
            views = list(document.views)
            for view in views:
                view._loading_text = True
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
            self.clean(editor)
            owner = document.analysis_owner
            if isinstance(owner, PythonEditor) and owner.ruff_lsp:
                owner.ruff_lsp.sync_from_editor()
        return False
````

**Code explanation**

| Class, function, or method | Responsibility |
|---|---|
| `EditorExtensions` | Coordinate actions, diagnostics, shared views, and asynchronous file snapshots. |
| `EditorExtensions.__init__` | Install features after the base UI exists and before restoring session tabs. |
| `EditorExtensions._dock` | Create one named dock compatible with QMainWindow layout persistence. |
| `EditorExtensions._action` | Create one QAction shared by the menu and dynamically refreshed palette. |
| `EditorExtensions._install_menu` | Expose course commands without rebuilding any existing menu callbacks. |
| `EditorExtensions.attach` | Initialize shared metadata and connect view-specific feature signals once. |
| `EditorExtensions.refresh_titles` | Derive every view's tab title from shared state and per-view pin/preview flags. |
| `EditorExtensions.current_changed` | Update language-specific command enablement for the selected view. |
| `EditorExtensions.apply_minimap` | Use real lexer theme accessors after settings replace the lexer. |
| `EditorExtensions.toggle_minimap` | Persist visibility and update each view's independently owned overview. |
| `EditorExtensions.toggle_fold` | Toggle the active line using QScintilla's foldLine slot. |
| `EditorExtensions.fold_all` | Set every fold header to a specific expanded/collapsed state. |
| `EditorExtensions.insert_snippet` | Insert into the active editor or create an unsaved template of the right type. |
| `EditorExtensions.find_references` | Request references from the active Python view without constructing an editor. |
| `EditorExtensions.show_references` | Reject a result belonging to a now-inactive source view. |
| `EditorExtensions.open_reference` | Navigate using zero-based semantic-provider coordinates. |
| `EditorExtensions.publish_diagnostics` | Adapt Ruff diagnostics at one boundary; preserve raw provider payloads. |
| `EditorExtensions.open_problem` | Navigate saved files or find the live owner of an untitled diagnostic URI. |
| `EditorExtensions.retarget` | Update every view's path and bytes metadata after a successful save or rename. |
| `EditorExtensions.clean` | Commit shared clean metadata after save and update every view title. |
| `EditorExtensions.duplicate` | Create an independent view over the same Scintilla document and state. |
| `EditorExtensions.detach` | Detach a tab and transfer the sole Ruff synchronizer before retiring its owner. |
| `EditorExtensions.prepare_preview` | Replace only an unpinned, clean preview in the requested group. |
| `EditorExtensions.reopen` | Reopen the latest available disk-backed location without restoring stale widgets. |
| `EditorExtensions.search_tabs` | Select from distinct numbered entries even when filenames are duplicated. |
| `EditorExtensions.sort_tabs` | Reorder the active group's existing tabs, with pinned tabs first. |
| `EditorExtensions.tab_menu` | Use the clicked group for pin, close-right, path and duplicate operations. |
| `EditorExtensions.disk_hints` | Read affected documents with revision tokens and refresh the existing Git service. |
| `EditorExtensions.disk_result` | Ignore obsolete snapshots; reload clean documents and flag dirty/deleted ones. |
| `EditorExtensions.shutdown` | Stop filesystem work; MainWindow retains ownership until completion drains. |
| `EditorExtensions.resolve_external` | Require an explicit overwrite, reload, compare or cancel decision before saving. |

<a id="integrate-main-py"></a>
## Edit `main.py`

### Add imports

At module scope in `main.py`, insert these imports **immediately after** `from markdowneditor_assets import asset_path` (baseline ending line 42), before the next existing statement. Do not duplicate them.

````python
from code_inteligence.document_state import DocumentStateStore, DirtyViews
from code_inteligence.editor_extensions import EditorExtensions
from code_settings.contrast import read_preferences, write_preferences, apply_preferences
````

### Add the `MainWindow` class docstring

Immediately after the `class MainWindow(...):` header (baseline line 120), before its first attribute or method, insert:

````python
    """Own the existing editor window and coordinate shared document lifecycle with feature services."""
````

<a id="method-main-py-mainwindow-init"></a>
### REPLACE `MainWindow.__init__`

**File:** `main.py`. **Baseline lines:** 142–235. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `init_ui` definition.

````python
    def __init__(self):
        """Construct existing services, shared document state and feature connections before session restoration."""
        super().__init__()
        self.update_check_finished.connect(self._show_update_check_result)
        self.documents = DocumentStateStore(self)
        self._dirty_editors = DirtyViews(self.documents)
        self.python_runner = PythonRunner(self)
        self.settings = QSettings("CodeEditor", "CodeEditor")
        self._hacker = self.settings.value("theme", "theme.json", type=str) == "hacker.json"
        self._pre_hacker_theme = "theme.json"
        # Load the saved recent files list, default to empty list
        self.recent_files = self.settings.value("recent_files", [], type=list)
        self.ruff_save_mode = self.settings.value("ruff_save_mode", "safe_format", type=str)
        self.update_available.connect(self._show_update_dialog)
        # retirement statement of all the Python workers
        self._retired_editors = set()


        # Detect if running as a bundled exe
        if hasattr(sys, "_MEIPASS"):
            # Running as PyInstaller exe — sys.executable is the editor itself.
            # Try to find a real Python installation on the system.
            import shutil

            found_python = shutil.which("python") or shutil.which("python3")
            if found_python:
                self.python_runner.set_interpreter(found_python)
            else:
                # No Python found — load from settings or let user pick
                saved = self._load_interpreter()
                if saved != sys.executable:
                    self.python_runner.set_interpreter(saved)
                else:
                    # Prompt user to select a Python interpreter
                    QMessageBox.warning(
                        self,
                        "Python Interpreter Required",
                        "No Python installation found.\n"
                        "Please select your Python interpreter (python.exe).",
                    )
                    self.choose_interpreter()
        else:
            # Running from source — sys.executable is the real Python
            self.python_runner.set_interpreter(self._load_interpreter())

        # The initial file-manager root is cwd for source/wheel launches and
        # home for the bundled executable. Ruff must use the same project view.
        initial_folder = Path.home() if hasattr(sys, "_MEIPASS") else Path.cwd()
        self._workspace_root = self._discover_workspace_root(initial_folder)

        self.ruff_lsp_client = RuffLspClient(
            python_executable=self.python_runner.interpreter,
            workspace_root=self._workspace_root,
            parent=self,
        )
        self.ruff_lsp_client.server_error.connect(self._on_ruff_lsp_error)
        self.ruff_lsp_client.start()

        self.console = None  # will be created in set_up_console_dock
        self.terminal = None
        self.python_editor_active = False
        self.current_file = None
        self.md = markdown.Markdown(
            extensions=[
                "extra",
                "codehilite",
                "toc",
                "sane_lists",
                "nl2br",
                "admonition",
                "smarty",
                "meta",
            ]
        )
        self._preview_css = """
           body { font-family: sans-serif; max-width: 800px; margin: 2em auto 0;
                  padding: 0 1em 4em; background:#1e1f22; color:#dcdfe4; }
           h1,h2 { border-bottom:1px solid #444; padding-bottom:.3em; }
           code { background:#1e1f22; padding:2px 5px; border-radius:3px; }
           pre { background:#1e1f22; padding:1em; border-radius:6px; overflow-x:auto; }
           """
        self.init_ui()
        self.extensions = EditorExtensions(self)

        if hasattr(sys, "_MEIPASS"):
            # We're running as a bundled exe
            import os

            home = os.path.expanduser("~")
            self.file_manager.model.setRootPath(home)
            self.file_manager.setRootIndex(self.file_manager.model.index(home))
        # Reopen the tabs from the previous sessions (no-op when
        # the feature is disabled or nothing was saved)
        self._apply_settings(self._load_settings())
        if self._hacker:
            self._set_scanlines_visible(True)
        self._restore_session()
````

**Code explanation:** Construct existing services, shared document state and feature connections before session restoration.

<a id="method-main-py-mainwindow-on-editor-text-changed"></a>
### REPLACE `MainWindow._on_editor_text_changed`

**File:** `main.py`. **Baseline lines:** 578–591. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `mark_editor_clean` definition.

````python
    def _on_editor_text_changed(self, editor):
        """Mark the specific editor that emitted textChanged as dirty."""
        if editor is None:
            return
        if getattr(editor, "_loading_text", False):
            return
        self._dirty_editors.add(editor)
        owner = self.documents.document(editor).analysis_owner
        controller = getattr(owner, "ruff_lsp", None)
        if controller is not None:
            self.extensions.diagnostics.clear_document(controller.uri)
        if editor is self.current_editor():
            self.update_word_count()
            if isinstance(editor, MarkdownEditor):
                self._debounce.start()
````

**Code explanation:** Mark the specific editor that emitted textChanged as dirty.

<a id="method-main-py-mainwindow-mark-editor-clean"></a>
### REPLACE `MainWindow.mark_editor_clean`

**File:** `main.py`. **Baseline lines:** 593–603. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `update_cursor_position` definition.

````python
    def mark_editor_clean(self, editor):
        """Mark the shared document clean after a successful save and refresh file colors."""
        if editor is not None:
            self.extensions.clean(editor)
            if editor.path is not None:
                self.file_manager.check_git_status()
````

**Code explanation:** Mark the shared document clean after a successful save and refresh file colors.

<a id="method-main-py-mainwindow-connect-editor"></a>
### REPLACE `MainWindow._connect_editor`

**File:** `main.py`. **Baseline lines:** 686–706. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_cat_unbox` definition.

````python
    def _connect_editor(self, editor):
        """Connect all MainWindow signals required by an editor."""
        self.documents.attach(editor, getattr(editor, "path", None))
        self.extensions.attach(editor)
        editor.textChanged.connect(lambda ed=editor: self._on_editor_text_changed(ed))
        editor.textChanged.connect(self._debounce.start)
        editor.textChanged.connect(self._outline_debounce.start)
        editor.textChanged.connect(self.update_word_count)
        editor.textChanged.connect(self._on_typing_xp)
        editor.textChanged.connect(lambda: self.power.attach_editor(editor))
        editor.textChanged.connect(self._arm_cat_timers)
        editor.textChanged.connect(self._cat_unbox)
        editor.cursorPositionChanged.connect(
            lambda line, column, ed=editor: self._on_editor_cursor_changed(ed, line, column)
        )
        editor.cursorPositionChanged.connect(lambda line, column, ed=editor: self.sync_scroll(ed))
        editor.verticalScrollBar().valueChanged.connect(
            lambda value, ed=editor: self.sync_scroll(ed)
        )
        if isinstance(editor, PythonEditor):
            editor.goto_definition_requested.connect(self._open_file_at_position)
            if editor.ruff_lsp is not None:
                editor.ruff_lsp.diagnostics_changed.connect(self._on_ruff_diagnostics)
````

**Code explanation:** Connect all MainWindow signals required by an editor.

<a id="method-main-py-mainwindow-on-ruff-diagnostics"></a>
### REPLACE `MainWindow._on_ruff_diagnostics`

**File:** `main.py`. **Baseline lines:** 722–738. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_restart_ruff` definition.

````python
    def _on_ruff_diagnostics(self, editor, diagnostics: list):
        """React only when this editor enters or leaves an issue state.

        State belongs to each editor because two tabs can have independent
        diagnostics. The term ``issues`` deliberately includes Ruff warnings,
        errors, and informational diagnostics, matching the previous UI intent.
        """
        if hasattr(self, "extensions"):
            self.extensions.publish_diagnostics(editor, diagnostics)
        had_issues = getattr(editor, "_had_ruff_issues", False)
        has_issues = bool(diagnostics)

        if has_issues and not had_issues:
            self.cat.set_state("alert", 2_000)
        elif had_issues and not has_issues:
            self.cat.add_xp(5)
            self.cat.set_state("stretch", 1_500)

        editor._had_ruff_issues = has_issues
````

**Code explanation:** React only when this editor enters or leaves an issue state. State belongs to each editor because two tabs can have independent diagnostics. The term ``issues`` deliberately includes Ruff warnings, errors, and informational diagnostics, matching the previous UI intent.

<a id="method-main-py-mainwindow-restart-ruff"></a>
### REPLACE `MainWindow._restart_ruff`

**File:** `main.py`. **Baseline lines:** 740–769. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_on_editor_cursor_changed` definition.

````python
    def _restart_ruff(
            self,
            python_executable: str | None = None,
            workspace_root: Path | None = None,
    ):
        """Replace the shared Ruff server after interpreter/workspace changes.

        Every open Python controller is reconnected to the new shared client.
        The old client then performs its asynchronous LSP shutdown. No editor
        owns a separate Ruff process.
        """
        executable = python_executable or self.python_runner.interpreter
        root = Path(workspace_root or self._workspace_root).resolve()
        self._workspace_root = root

        if hasattr(self, "extensions"):
            self.extensions.diagnostics.clear_provider("ruff")
            self.extensions.references.set_locations([])
            for view in self.tab_view.all_editors():
                if isinstance(view, PythonEditor):
                    view.references_finder.invalidate()
        old_client = self.ruff_lsp_client
        client = RuffLspClient(
            python_executable=executable,
            workspace_root=root,
            parent=self,
        )
        client.server_error.connect(self._on_ruff_lsp_error)
        self.ruff_lsp_client = client

        for editor in self.tab_view.all_editors():
            if isinstance(editor, PythonEditor) and editor.ruff_lsp is not None:
                editor.ruff_lsp.set_client(client)

        old_client.shutdown()
        client.start()
````

**Code explanation:** Replace the shared Ruff server after interpreter/workspace changes. Every open Python controller is reconnected to the new shared client. The old client then performs its asynchronous LSP shutdown. No editor owns a separate Ruff process.

<a id="method-main-py-mainwindow-set-up-menu"></a>
### REPLACE `MainWindow.set_up_menu`

**File:** `main.py`. **Baseline lines:** 777–1050. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `split_current_editor_right` definition.

````python
    def set_up_menu(self):
        """Create existing menu actions and assign stable IDs for palette discovery."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        new_file = file_menu.addAction("New")
        new_file.setObjectName("menu.new_file")
        new_file.setShortcut("Ctrl+N")
        new_file.setShortcutContext(Qt.ApplicationShortcut)
        new_file.triggered.connect(self.new_file)

        open_file = file_menu.addAction("Open File")
        open_file.setObjectName("menu.open_file")
        open_file.setShortcut("Ctrl+O")
        open_file.setShortcutContext(Qt.ApplicationShortcut)
        open_file.triggered.connect(self.open_file)

        # Open Recent submenu
        # addMenu returns a QMenu object. We store it as an instance
        # variable so we can rebuild it when the recent files list changes.
        self.recent_menu = file_menu.addMenu("Open Recent")
        self._update_recent_menu()

        open_folder = file_menu.addAction("Open Folder")
        open_folder.setObjectName("menu.open_folder")
        open_folder.setShortcut("Ctrl+K")
        open_folder.setShortcutContext(Qt.ApplicationShortcut)
        open_folder.triggered.connect(self.open_folder)

        file_menu.addSeparator()
        save_file = file_menu.addAction("Save")
        save_file.setObjectName("menu.save_file")
        save_file.setShortcut("Ctrl+S")
        save_file.setShortcutContext(Qt.ApplicationShortcut)
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save As")
        save_as.setObjectName("menu.save_as")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.setShortcutContext(Qt.ApplicationShortcut)
        save_as.triggered.connect(self.save_as)

        save_all_action = file_menu.addAction("Save All")
        save_all_action.setObjectName("menu.save_all_action")
        save_all_action.setShortcut("Ctrl+Shift+A")
        save_all_action.setShortcutContext(Qt.ApplicationShortcut)
        save_all_action.triggered.connect(self.save_all)

        close_all_action = file_menu.addAction("Close All")
        close_all_action.setObjectName("menu.close_all_action")
        close_all_action.setShortcut("Ctrl+Shift+W")
        close_all_action.setShortcutContext(Qt.ApplicationShortcut)
        close_all_action.triggered.connect(self._close_all_tabs)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        undo_action = edit_menu.addAction("Undo")
        undo_action.setObjectName("menu.undo_action")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setShortcutContext(Qt.ApplicationShortcut)
        undo_action.triggered.connect(self.undo)

        redo_action = edit_menu.addAction("Redo")
        redo_action.setObjectName("menu.redo_action")
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.setShortcutContext(Qt.ApplicationShortcut)
        redo_action.triggered.connect(self.redo)

        edit_menu.addSeparator()

        cut_action = edit_menu.addAction("Cut")
        cut_action.setObjectName("menu.cut_action")
        cut_action.setShortcut("Ctrl+X")
        cut_action.setShortcutContext(Qt.ApplicationShortcut)
        cut_action.triggered.connect(self.cut)

        copy_action = edit_menu.addAction("Copy")
        copy_action.setObjectName("menu.copy_action")
        copy_action.setShortcut("Ctrl+C")
        copy_action.setShortcutContext(Qt.ApplicationShortcut)
        copy_action.triggered.connect(self.copy)

        paste_action = edit_menu.addAction("Paste")
        paste_action.setObjectName("menu.paste_action")
        paste_action.setShortcut("Ctrl+V")
        paste_action.setShortcutContext(Qt.ApplicationShortcut)
        paste_action.triggered.connect(self.paste)

        edit_menu.addSeparator()

        select_all_action = edit_menu.addAction("Select All")
        select_all_action.setObjectName("menu.select_all_action")
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setShortcutContext(Qt.ApplicationShortcut)
        select_all_action.triggered.connect(self.select_all)

        delete_line_action = edit_menu.addAction("Delete Line")
        delete_line_action.setObjectName("menu.delete_line_action")
        delete_line_action.setShortcut("Ctrl+Shift+K")
        delete_line_action.setShortcutContext(Qt.ApplicationShortcut)
        delete_line_action.triggered.connect(self.delete_line)

        edit_menu.addSeparator()

        find_action = edit_menu.addAction("Find")
        find_action.setObjectName("menu.find_action")
        find_action.setShortcut("Ctrl+F")
        find_action.setShortcutContext(Qt.ApplicationShortcut)
        find_action.triggered.connect(self.show_find_bar)

        replace_action = edit_menu.addAction("Replace")
        replace_action.setObjectName("menu.replace_action")
        replace_action.setShortcut("Ctrl+H")
        replace_action.setShortcutContext(Qt.ApplicationShortcut)
        replace_action.triggered.connect(self.show_replace_bar)

        edit_menu.addSeparator()

        goto_action = edit_menu.addAction("Go to Line")
        goto_action.setObjectName("menu.goto_action")
        goto_action.setShortcut("Ctrl+G")
        goto_action.setShortcutContext(Qt.ApplicationShortcut)
        goto_action.triggered.connect(self.goto_line)

        edit_menu.addSeparator()

        toggle_comment_action = edit_menu.addAction("Toggle Comment")
        toggle_comment_action.setObjectName("menu.toggle_comment_action")
        toggle_comment_action.setShortcut("Ctrl+1")
        toggle_comment_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_comment_action.triggered.connect(self.toggle_comment)

        edit_menu.addSeparator()
        goto_definition_action = edit_menu.addAction("Go to Definition")
        goto_definition_action.setObjectName("menu.goto_definition_action")
        goto_definition_action.setShortcut("F12")
        goto_definition_action.setShortcutContext(Qt.ApplicationShortcut)
        goto_definition_action.triggered.connect(self._trigger_goto_definition)

        # Mode menu
        mode_menu = menu_bar.addMenu("Mode")

        # change to Python-Editor
        self.python_editor_action = mode_menu.addAction("Python Editor")
        self.python_editor_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        self.python_editor_action.setShortcutContext(Qt.ApplicationShortcut)
        self.python_editor_action.triggered.connect(self.change_editor_python)

        # change to Markdown-Editor
        self.markdown_editor_action = mode_menu.addAction("Markdown Editor")
        self.markdown_editor_action.setShortcut(QKeySequence("Ctrl+Shift+M"))
        self.markdown_editor_action.setShortcutContext(Qt.ApplicationShortcut)
        self.markdown_editor_action.triggered.connect(self.change_editor_markdown)

        run_menu = self.menuBar().addMenu("Run")

        run_file_action = run_menu.addAction("Run File")
        run_file_action.setObjectName("menu.run_file_action")
        run_file_action.setShortcut("F5")
        run_file_action.setShortcutContext(Qt.ApplicationShortcut)
        run_file_action.triggered.connect(self.run_current_file)

        run_with_args_action = run_menu.addAction("Run with Arguments")
        run_with_args_action.setObjectName("menu.run_with_args_action")
        run_with_args_action.setShortcut("Shift+F5")
        run_with_args_action.setShortcutContext(Qt.ApplicationShortcut)
        run_with_args_action.triggered.connect(self.run_with_arguments)

        run_selection_action = run_menu.addAction("Run Selection")
        run_selection_action.setObjectName("menu.run_selection_action")
        run_selection_action.setShortcut("Ctrl+Return")
        run_selection_action.setShortcutContext(Qt.ApplicationShortcut)
        run_selection_action.triggered.connect(self.run_selection)

        stop_action = run_menu.addAction("Stop")
        stop_action.setObjectName("menu.stop_action")
        stop_action.setShortcut("F6")
        stop_action.setShortcutContext(Qt.ApplicationShortcut)
        stop_action.triggered.connect(self.python_runner.stop)

        run_menu.addSeparator()

        interpreter_action = run_menu.addAction("Choose Interpreter...")
        interpreter_action.setObjectName("menu.interpreter_action")
        interpreter_action.triggered.connect(self.choose_interpreter)

        # Viewmenu for toggling the Sidebar

        view_menu = self.menuBar().addMenu("View")

        toggle_sidebar_action = view_menu.addAction("Toggle Sidebar")
        toggle_sidebar_action.setObjectName("menu.toggle_sidebar_action")
        toggle_sidebar_action.setShortcut("Ctrl+B")
        toggle_sidebar_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)

        toggle_preview_action = view_menu.addAction("Toggle Preview")
        toggle_preview_action.setObjectName("menu.toggle_preview_action")
        toggle_preview_action.setShortcut("Ctrl+J")
        toggle_preview_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_preview_action.triggered.connect(self.toggle_preview)

        toggle_console_action = view_menu.addAction("Toggle Console")
        toggle_console_action.setObjectName("menu.toggle_console_action")
        toggle_console_action.setShortcut("Ctrl+Shift+-")
        toggle_console_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_console_action.triggered.connect(self.toggle_console)

        toggle_terminal_action = view_menu.addAction("Toggle Terminal")
        toggle_terminal_action.setObjectName("menu.toggle_terminal_action")
        toggle_terminal_action.setShortcut("Ctrl+Shift+]")
        toggle_terminal_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_terminal_action.triggered.connect(self.toggle_terminal)

        view_menu.addSeparator()

        split_right_action = view_menu.addAction("Split Right")
        split_right_action.setObjectName("menu.split_right_action")
        split_right_action.setShortcut("Ctrl+Alt+Right")
        split_right_action.setShortcutContext(Qt.ApplicationShortcut)
        split_right_action.triggered.connect(self.split_current_editor_right)

        unsplit_action = view_menu.addAction("Unsplit")
        unsplit_action.setObjectName("menu.unsplit_action")
        unsplit_action.setShortcut("Ctrl+Alt+Left")
        unsplit_action.setShortcutContext(Qt.ApplicationShortcut)
        unsplit_action.triggered.connect(self.unsplit_active_group)

        view_menu.addSeparator()

        fullscreen_editor = view_menu.addAction("Fullscreen")
        fullscreen_editor.setObjectName("menu.fullscreen_editor")
        fullscreen_editor.setShortcut("F11")
        fullscreen_editor.setShortcutContext(Qt.ApplicationShortcut)
        fullscreen_editor.triggered.connect(self._show_full_screen)

        starting_window_size = view_menu.addAction("Startup Window Size")
        starting_window_size.setObjectName("menu.starting_window_size")
        starting_window_size.setShortcut("Shift+F11")
        starting_window_size.setShortcutContext(Qt.ApplicationShortcut)
        starting_window_size.triggered.connect(self._startup_window_size)

        view_menu.addSeparator()

        git_refresh_action = view_menu.addAction("Refresh Git Status")
        git_refresh_action.setObjectName("menu.git_refresh_action")
        git_refresh_action.setShortcut("Ctrl+Shift+G")
        git_refresh_action.setShortcutContext(Qt.ApplicationShortcut)
        git_refresh_action.triggered.connect(self._refresh_git_state)
        
        toggle_git_history_action = view_menu.addAction("Toggle Git History")
        toggle_git_history_action.setObjectName("menu.toggle_git_history_action")
        toggle_git_history_action.setShortcut("Ctrl+Alt+G")
        toggle_git_history_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_git_history_action.triggered.connect(self._toggle_git_history)

        settings_action = view_menu.addAction("Settings")
        settings_action.setObjectName("menu.settings_action")
        settings_action.setShortcut("Ctrl+Alt+S")
        settings_action.setShortcutContext(Qt.ApplicationShortcut)
        settings_action.triggered.connect(self.open_settings)

        hacker_action = view_menu.addAction("Hacker-Mode")
        hacker_action.setObjectName("menu.hacker_action")
        hacker_action.setShortcut("Ctrl+Shift+H")
        hacker_action.setShortcutContext(Qt.ApplicationShortcut)
        hacker_action.setCheckable(True)
        hacker_action.setChecked(self._hacker)
        hacker_action.toggled.connect(self.set_hacker_mode)
        self.hacker_action = hacker_action

        # B1/C7: Power Mode dropdown — master switch plus one toggle per
        # effect. All four states persist in QSettings (power_mode,
        # power_particles, power_shake, power_glow) like ruff_save_mode.
        # The handlers guard on self.power because the menu is built
        # before the controller is created in init_ui().
        power_menu = view_menu.addMenu("Power Mode")

        self.power_mode_action = power_menu.addAction("Enabled")
        self.power_mode_action.setCheckable(True)
        self.power_mode_action.setChecked(self.settings.value("power_mode", True, type=bool))
        self.power_mode_action.setShortcut("Ctrl+Shift+X")
        self.power_mode_action.setShortcutContext(Qt.ApplicationShortcut)
        self.power_mode_action.toggled.connect(self._toggle_power_mode)

        power_menu.addSeparator()

        self.power_particles_action = power_menu.addAction("Particles")
        self.power_particles_action.setCheckable(True)
        self.power_particles_action.setChecked(
            self.settings.value("power_particles", True, type=bool)
        )
        self.power_particles_action.toggled.connect(self._toggle_power_particles)

        self.power_shake_action = power_menu.addAction("Screen Shake")
        self.power_shake_action.setCheckable(True)
        self.power_shake_action.setChecked(self.settings.value("power_shake", True, type=bool))
        self.power_shake_action.toggled.connect(self._toggle_power_shake)

        self.power_glow_action = power_menu.addAction("Combo Glow")
        self.power_glow_action.setCheckable(True)
        self.power_glow_action.setChecked(self.settings.value("power_glow", True, type=bool))
        self.power_glow_action.toggled.connect(self._toggle_power_glow)

        help_menu = menu_bar.addMenu("Help")

        check_updates_action = help_menu.addAction("Check for Updates")
        check_updates_action.setObjectName("menu.check_updates_action")
        check_updates_action.triggered.connect(lambda: self.check_for_updates(manual=True))
````

**Code explanation:** Create existing menu actions and assign stable IDs for palette discovery.

<a id="method-main-py-mainwindow-load-settings"></a>
### REPLACE `MainWindow._load_settings`

**File:** `main.py`. **Baseline lines:** 1399–1438. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_save_settings` definition.

````python
    def _load_settings(self) -> dict:
        """
        Load all user preferences from the platform-native QSettings store.
        """

        # --- QSettings side --- #
        # .value(key, default, type=) coerces the stored values: QSettings serialises booleans/ints as strings
        # on some platforms, and the type= argument converts them back safely.
        #
        # THEME-MANAGED values: font family/size and the paper color are NOT
        # stored in QSettings anymore — the active theme.json is their single
        # source of truth (read here, written by _write_theme_editor()).
        theme_editor = self._read_theme_editor()

        return {
            "interpreter": self.settings.value(
                "interpreter", self.python_runner.interpreter, type=str
            ),
            # BUGFIX: read/write key mismatch - this read "ruff_safe_mode"
            # while _save_settings() writes "ruff_save_mode", so the saved
            # Ruff mode never survived a restart.
            "ruff_save_mode": self.settings.value("ruff_save_mode", "safe_format", type=str),
            "font_family": theme_editor.get("font_family", "JetBrains Mono"),
            "font_size": theme_editor.get("font_size", 13),
            # paper: QSettings override (color picker) wins over the theme;
            # theme_paper is the theme's OWN value, so the dialog's
            # "Reset to theme" button can drop the override.
            "paper_color": (
                self.settings.value("paper_color", type=str)
                if self.settings.contains("paper_color")
                else None
            ),
            "theme_paper": theme_editor.get("paper_color", "#1e1f22"),
            "tab_width": self.settings.value("tab_width", 4, type=int),
            "word_wrap": self.settings.value("word_wrap", False, type=bool),
            "restore_tabs": self.settings.value("restore_tabs", True, type=bool),
            "theme": self.settings.value("theme", "theme.json", type=str),
            "line_numbers": self.settings.value("line_numbers", True, type=bool),
            "highlight_line": self.settings.value("highlight_line", True, type=bool),
            **read_preferences(self.settings),
        }
````

**Code explanation:** Load all user preferences from the platform-native QSettings store.

<a id="method-main-py-mainwindow-save-settings"></a>
### REPLACE `MainWindow._save_settings`

**File:** `main.py`. **Baseline lines:** 1440–1468. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `open_settings` definition.

````python
    def _save_settings(self, new_settings: dict):
        """Persist an edited settings dictionary to QSettings.
        Called only after the user clicked Save in the dialog.

        Parameters
        ----------
        new_settings : dict
            The dictionary returned by SettingsDialog.get_settings().
        """
        self.settings.setValue("interpreter", new_settings["interpreter"])

        # --- QSettings -------------------------------------------------- #
        # NOTE: font_family / font_size are NOT QSettings keys anymore —
        # they live in the active theme.json (see _write_theme_editor()).
        for key in (
            "ruff_save_mode",
            "tab_width",
            "word_wrap",
            "restore_tabs",
            "theme",
            "line_numbers",
            "highlight_line",
        ):
            self.settings.setValue(key, new_settings[key])
        if new_settings.get("paper_color") is None:
            self.settings.remove("paper_color")
        else:
            self.settings.setValue("paper_color", new_settings["paper_color"])
        write_preferences(self.settings, new_settings)
        self.settings.sync()
````

**Code explanation:** Persist an edited settings dictionary to QSettings. Called only after the user clicked Save in the dialog. Parameters ---------- new_settings : dict The dictionary returned by SettingsDialog.get_settings().

<a id="method-main-py-mainwindow-apply-editor-settings"></a>
### REPLACE `MainWindow._apply_editor_settings`

**File:** `main.py`. **Baseline lines:** 1664–1738. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `is_binary` definition.

````python
    def _apply_editor_settings(self, editor, settings: dict):
        """
        Apply font/wrap/margin/theme settings to ONE editor.

        Split out of _apply_settings() so newly opened tabs (get_editor)
        can receive the same look without duplicating this code.
        """
        from PyQt5.Qsci import QsciScintilla

        from markdown_editor.markdowncustomlexer import MarkdownCustomLexer
        from markdown_editor.markdowneditor import MarkdownEditor
        from python_editor.custompythonlexer import PyCustomLexer
        from python_editor.pythoneditor import PythonEditor

        # THEME-MANAGED STYLING: font family/size and the paper color now
        # come from the theme's editor section (the Settings dialog writes
        # them there — see _write_theme_editor). The lexers apply them to
        # every style themselves; main.py no longer fights the lexer with
        # editor-level font overrides. That fight is exactly why the old
        # code "worked" for Markdown (setFont on ALL styles) but was
        # invisible on Python (setDefaultFont only touched style 0).

        # Paper override from the Settings color picker (QSettings key,
        # wins over the theme's own paper until reset to default).
        paper = QColor(settings["paper_color"]) if settings.get("paper_color") else None

        # QsciScintilla.WrapWord soft-wraps at the right edge;
        # WrapNone keeps the horizontal scrollbar behaviour.
        wrap = QsciScintilla.WrapWord if settings["word_wrap"] else QsciScintilla.WrapNone

        editor.setTabWidth(settings["tab_width"])
        editor.setWrapMode(wrap)
        editor.setCaretLineVisible(settings["highlight_line"])

        # Margin 0 is the line-number gutter. Width "0000" fits a
        # 4-digit line count; width 0 collapses it entirely.
        if settings["line_numbers"]:
            editor.setMarginWidth(0, "0000")
        else:
            editor.setMarginWidth(0, 0)

        # Recreate the lexer so a theme switch (or font change written
        # into the theme) takes effect now. A QScintilla can only host
        # ONE lexer at a time; the old one is replaced on the C++ side
        # by setLexer().
        theme_path = self._theme_path(settings.get("theme"))
        if isinstance(editor, MarkdownEditor):
            editor.md_lexer = MarkdownCustomLexer(editor, theme=theme_path, paper=paper)
            editor.setLexer(editor.md_lexer)
            # Re-push the theme's editor-wide look (font, margins, caret,
            # paper). The editor's own method handles the reset-a-lexer-
            # wipes-margin-colors problem in exactly one place.
            editor._apply_theme_editor_style()
        elif isinstance(editor, PythonEditor):
            editor.py_lexer = PyCustomLexer(editor, theme=theme_path, paper=paper)
            editor.setLexer(editor.py_lexer)
            editor._apply_theme_editor_style()

            # QsciAPIs is bound to the lexer instance it was created with,
            # so reattach a fresh one to the new lexer. The AutoCompleter
            # thread repopulates the word list as soon as the user types.
            from PyQt5.Qsci import QsciAPIs

            if getattr(editor, "_api", None) is not None:
                editor._api = QsciAPIs(editor.py_lexer)
                editor.auto_completer.api = editor._api

        # BUGFIX (phantom strings after theme switches): setLexer() does NOT
        # reliably restyle the whole document - old style bytes from the
        # PREVIOUS lexer/theme survive in the buffer, so text typed after
        # switching themes inherits stale styles (everything after the caret
        # rendered as neon-green "strings" until a docstring quote "closed"
        # the phantom string). SCI_COLOURISE (4003) with (0, -1) forces the
        # NEW lexer to restyle the entire document right now.
        editor.SendScintilla(4003, 0, -1)
        apply_preferences(editor, settings)
        if hasattr(self, "extensions"):
            self.extensions.apply_minimap(editor)
        editor.folding_controller._last_digest = b""
        editor.folding_controller.schedule()
````

**Code explanation:** Apply font/wrap/margin/theme settings to ONE editor. Split out of _apply_settings() so newly opened tabs (get_editor) can receive the same look without duplicating this code.

<a id="method-main-py-mainwindow-set-new-tab"></a>
### REPLACE `MainWindow.set_new_tab`

**File:** `main.py`. **Baseline lines:** 1749–1816. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `get_frame` definition.

````python
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
                self.extensions.refresh_titles(self.documents.document(existing))
            self.tab_view.focus_editor(existing)
            return existing
        if preview:
            self.extensions.prepare_preview(path, target_group or self.tab_view.active_group())
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
        self.extensions.refresh_titles(self.documents.document(editor))
        self.tab_view.set_editor_tooltip(editor, str(path.absolute()))

        self.current_file = path
        self._add_to_recent_files(str(path))
        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.outline_tree.clear()
        return editor
````

**Code explanation:** Open one UTF-8 document without corrupting or duplicating it. Binary probing, symlink resolution, byte reading, and strict decoding are one I/O transaction. Every expected filesystem/encoding failure is converted to a user-visible dialog instead of escaping a Qt slot.

<a id="method-main-py-mainwindow-show-tab-context-menu"></a>
### REPLACE `MainWindow._show_tab_context_menu`

**File:** `main.py`. **Baseline lines:** 2030–2069. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_close_other_tabs` definition.

````python
    def _show_tab_context_menu(self, group, pos):
        """Delegate tab actions using the clicked group rather than the active group."""
        self.extensions.tab_menu(group, pos)
````

**Code explanation:** Delegate tab actions using the clicked group rather than the active group.

<a id="method-main-py-mainwindow-close-editor"></a>
### REPLACE `MainWindow.close_editor`

**File:** `main.py`. **Baseline lines:** 2155–2185. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_dispose_editor` definition.

````python
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
        self.extensions.detach(editor, remember=True)
        self.tab_view.remove_editor(editor)
        self._dispose_editor(editor)
        self.render_preview()
        return True
````

**Code explanation:** Close unpinned views; prompt once only when the final view is dirty.

<a id="method-main-py-mainwindow-dispose-editor"></a>
### REPLACE `MainWindow._dispose_editor`

**File:** `main.py`. **Baseline lines:** 2187–2198. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_finalize_retired_editor` definition.

````python
    def _dispose_editor(self, editor):
        """Delete now, or retain a Python editor until its workers finish."""
        self.extensions.detach(editor, transfer=not getattr(self, "_close_prompts_complete", False))
        if isinstance(editor, PythonEditor):
            self._retired_editors.add(editor)
            editor.setParent(None)
            editor.shutdown_complete.connect(self._finalize_retired_editor)
            editor.shutdown()
            editor._check_shutdown_complete()
            return 
        editor.shutdown()
        editor.setParent(None)
        editor.deleteLater()
````

**Code explanation:** Delete now, or retain a Python editor until its workers finish.

<a id="method-main-py-mainwindow-on-file-rename"></a>
### REPLACE `MainWindow.on_file_rename`

**File:** `main.py`. **Baseline lines:** 2207–2257. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `editors_for_path` definition.

````python
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
            self.extensions.retarget(editor, destination)
            wanted = PythonEditor if is_python_path(destination) else MarkdownEditor
            editor = self._convert_editor(editor, wanted)
            if editor is self.current_editor():
                self.current_file = destination
````

**Code explanation:** Retarget each shared document once after a successful file-manager rename.

<a id="method-main-py-mainwindow-can-close-editors-for-path"></a>
### REPLACE `MainWindow.can_close_editors_for_path`

**File:** `main.py`. **Baseline lines:** 2276–2294. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `close_editors_for_path` definition.

````python
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
````

**Code explanation:** Gather one save/discard decision per document before a file-manager operation.

<a id="method-main-py-mainwindow-close-editors-for-path"></a>
### REPLACE `MainWindow.close_editors_for_path`

**File:** `main.py`. **Baseline lines:** 2296–2304. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `show_hide_tab` definition.

````python
    def close_editors_for_path(self, target_path, is_directory=False, prompt=True):
        """Close every view covered by a confirmed file-manager operation."""
        editors = self.editors_for_path(target_path, is_directory)
        if prompt and not self.can_close_editors_for_path(target_path, is_directory):
            return False
        for editor in editors:
            self.extensions.detach(editor, transfer=False)
            self.tab_view.remove_editor(editor)
            self._dispose_editor(editor)
        return True
````

**Code explanation:** Close every view covered by a confirmed file-manager operation.

<a id="method-main-py-mainwindow-save-editor-to-path"></a>
### REPLACE `MainWindow._save_editor_to_path`

**File:** `main.py`. **Baseline lines:** 2510–2589. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `save_file` definition.

````python
    def _save_editor_to_path(
        self,
        editor,
        path: Path,
        *,
        check_external_change: bool = True,
    ) -> bool:
        """Format and atomically save without losing links or newer disk data."""
        logical_path = Path(path)
        try:
            target = save_target(logical_path)
        except OSError as error:
            QMessageBox.critical(self, "Save File", f"Broken symbolic link:\n{error}")
            return False

        if check_external_change and target.exists():
            expected = getattr(editor, "_disk_digest", None)
            try:
                external_bytes = target.read_bytes()
                actual = hashlib.sha256(external_bytes).digest()
            except OSError as error:
                QMessageBox.critical(self, "Save File", str(error))
                return False
            if expected is not None and actual != expected:
                if not self.extensions.resolve_external(editor, external_bytes):
                    return False

        original = editor.text()
        try:
            formatted = self._run_ruff_before_save(logical_path, original)
        except (OSError, subprocess.SubprocessError, RuntimeError) as error:
            reply = QMessageBox.warning(
                self,
                "Ruff on save",
                f"Ruff could not process this file:\n{error}\n\nSave without Ruff?",
                QMessageBox.Save | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply != QMessageBox.Save:
                return False
            formatted = original

        temporary = None
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self._encode_editor_text(editor, formatted)
            with tempfile.NamedTemporaryFile(
                dir=target.parent,
                prefix=f".{target.name}.",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if target.exists():
                os.chmod(temporary, target.stat().st_mode)
            os.replace(temporary, target)
            temporary = None
        except OSError as error:
            QMessageBox.critical(self, "Save File", f"Could not save '{logical_path}':\n{error}")
            return False
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        if formatted != original:
            # Retain the pre-format text as one Undo step after the save.
            self._apply_formatted_text(editor, formatted)
        editor._save_target = target
        editor._disk_digest = hashlib.sha256(data).digest()
        self.extensions.retarget(editor, logical_path)
        self.mark_editor_clean(editor)
        return True
````

**Code explanation:** Format and atomically save without losing links or newer disk data.

<a id="method-main-py-mainwindow-save-as"></a>
### REPLACE `MainWindow.save_as`

**File:** `main.py`. **Baseline lines:** 2619–2672. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_terminal_view_has_focus` definition.

````python
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
````

**Code explanation:** Save to a user-confirmed path and update the tab's editor type. The native file dialog owns the intentional overwrite confirmation. The source tab's disk digest belongs to its old path and must never be compared with bytes at the new destination.

<a id="method-main-py-mainwindow-on-current-editor-changed"></a>
### REPLACE `MainWindow._on_current_editor_changed`

**File:** `main.py`. **Baseline lines:** 2740–2763. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `change_editor_python` definition.

````python
    def _on_current_editor_changed(self, editor):
        """Refresh MainWindow state when focus moved between editors."""
        if hasattr(self, "extensions"):
            self.extensions.current_changed(editor)
        if editor is None:
            self.current_file = None
            self.cursor_pos_label.setText("")
            self.word_count_label.setText("")
            return

        self.current_file = getattr(editor, "path", None)

        line, column = editor.getCursorPosition()
        self.update_cursor_position(line, column)
        self.update_word_count()

        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.outline_tree.clear()

        if isinstance(editor, MarkdownEditor):
            self.preview.show()
            self.render_preview()
        else:
            self.preview.hide()
````

**Code explanation:** Refresh MainWindow state when focus moved between editors.

<a id="method-main-py-mainwindow-convert-editor"></a>
### REPLACE `MainWindow._convert_editor`

**File:** `main.py`. **Baseline lines:** 2836–2900. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_swap_editor` definition.

````python
    def _convert_editor(self, old, EditorClass):
        """Convert every view of a document while preserving shared text and undo state."""
        if old is None or isinstance(old, EditorClass):
            return old
        document = self.documents.document(old)
        previous_views = list(document.views)
        source_document = old.document()
        owner = document.analysis_owner
        if isinstance(owner, PythonEditor) and owner.ruff_lsp is not None:
            self.extensions.diagnostics.clear_document(owner.ruff_lsp.uri)
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
        self.extensions.refresh_titles(document)
        if current in replacements:
            self.tab_view.focus_editor(replacements[current])
        return replacements[old]
````

**Code explanation:** Convert every view of a document while preserving shared text and undo state.

<a id="method-main-py-mainwindow-background-work-running"></a>
### REPLACE `MainWindow._background_work_running`

**File:** `main.py`. **Baseline lines:** 3101–3144. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_finish_pending_close` definition.

````python
    def _background_work_running(self) -> bool:
        """Return whether an asynchronous component is still shutting down.

        Returns:
            True while an editor retirement, Git scan, project search, Python
            run, Ruff process, or terminal PTY worker remains active.

        The method is polled by `_finish_pending_close()` through QTimer. It
        must only inspect state and must never block the GUI thread.
        """
        if self.extensions.watcher.is_running():
            return True
        git_worker = getattr(
            getattr(self, "file_manager", None),
            "git_checker",
            None,
        )
        search_worker = getattr(self, "search_worker", None)
        runner = getattr(self, "python_runner", None)
        ruff = getattr(self, "ruff_lsp_client", None)
        terminal = getattr(self, "terminal", None)
        git_service = getattr(self, "git_service", None)
        

        return bool(
            # Retired editors remain here until their workers are disposed.
            self._retired_editors

            # QThread-based background services use isRunning().
            or (git_worker is not None and git_worker.isRunning())
            or (search_worker is not None and search_worker.isRunning())
            or (git_service is not None and git_service.is_running())

            # PythonRunner exposes its own public running-state method.
            or (runner is not None and runner.is_running())

            # Ruff still uses QProcess, so its existing state check remains.
            or (
                ruff is not None
                and ruff.process.state() != QProcess.NotRunning
            )

            # The PTY terminal no longer owns a QProcess. Ask its public API
            # whether the _PtySession worker is still running.
            or (terminal is not None and terminal.is_running())
        )
````

**Code explanation:** Return whether an asynchronous component is still shutting down. Returns: True while an editor retirement, Git scan, project search, Python run, Ruff process, or terminal PTY worker remains active. The method is polled by `_finish_pending_close()` through QTimer. It must only inspect state and must never block the GUI thread.

<a id="method-main-py-mainwindow-closeevent"></a>
### REPLACE `MainWindow.closeEvent`

**File:** `main.py`. **Baseline lines:** 3153–3206. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `save_session` definition.

````python
    def closeEvent(self, event):
        """Prompt once per dirty document, persist views, and wait for owned background work before exit."""
        if getattr(self, "_close_ready", False):
            event.accept()
            return super().closeEvent(event)

        if not getattr(self, "_close_prompts_complete", False):
            for editor in list(self._dirty_editors):
                self.tab_view.focus_editor(editor)
                path = getattr(editor, "path", None)
                name = Path(path).name if path is not None else "Untitled"
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"Save changes to '{name}'?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save,
                )
                if reply == QMessageBox.Cancel:
                    event.ignore()
                    return
                if reply == QMessageBox.Save and not self.save_file():
                    event.ignore()
                    return
            self._close_prompts_complete = True
            self.save_session()

        for editor in list(self.tab_view.all_editors()):
            self.tab_view.remove_editor(editor)
            self._dispose_editor(editor)

        self.extensions.shutdown()
        self.terminal.stop()
        if hasattr(self.python_runner, "shutdown"):
            self.python_runner.shutdown()
        else:
            # Compatibility until Fix 5 replaces PythonRunner.
            self.python_runner.stop()
        self.ruff_lsp_client.shutdown()
        if hasattr(self.search_worker, "shutdown"):
            self.search_worker.shutdown()
        self.settings.setValue("recent_files", self.recent_files)
        
        self.file_manager.git_checker.shutdown()
        self.git_service.shutdown()

        if self._background_work_running():
            event.ignore()
            QTimer.singleShot(100, self._finish_pending_close)
            return

        self._close_ready = True
        event.accept()
        super().closeEvent(event)
````

**Code explanation:** Prompt once per dirty document, persist views, and wait for owned background work before exit.

<a id="method-main-py-mainwindow-save-session"></a>
### REPLACE `MainWindow.save_session`

**File:** `main.py`. **Baseline lines:** 3208–3261. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_restore_session` definition.

````python
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
````

**Code explanation:** Persist one file identity with multiple independently positioned view records.

<a id="method-main-py-mainwindow-restore-session"></a>
### REPLACE `MainWindow._restore_session`

**File:** `main.py`. **Baseline lines:** 3263–3344. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `check_for_updates` definition.

````python
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
                view = self.extensions.duplicate(opened[key], group)
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
            self.extensions.refresh_titles(self.documents.document(view))
            if session.get("active_view") == index or session.get("active") == str(path):
                active = view
        self.python_editor_active = session.get("python_mode") is True
        if active is not None:
            self.tab_view.focus_editor(active)
````

**Code explanation:** Restore saved files and duplicate views while retaining one Ruff owner per file.

<a id="integrate-code-settings-settings-dialog-py"></a>
## Edit `code_settings/settings_dialog.py`

<a id="method-code-settings-settings-dialog-py-settingsdialog-create-appearance-tab"></a>
### REPLACE `SettingsDialog._create_appearance_tab`

**File:** `code_settings/settings_dialog.py`. **Baseline lines:** 314–371. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_browse_interpreter` definition.

````python
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
````

**Code explanation:** Build theme, paper, caret, selection and line-display controls using current preferences.

<a id="method-code-settings-settings-dialog-py-settingsdialog-get-settings"></a>
### REPLACE `SettingsDialog.get_settings`

**File:** `code_settings/settings_dialog.py`. **Baseline lines:** 405–418. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop at the end of the named definition; retain the surrounding class/module.

````python
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
````

**Code explanation:** Return the complete edited preference dictionary without writing before Save is accepted.

<a id="method-code-settings-settings-dialog-py-settingsdialog-pick-editor-color"></a>
### ADD `SettingsDialog._pick_editor_color`

**File:** `code_settings/settings_dialog.py`. **Owner:** `SettingsDialog`. Insert inside the class **after `get_settings`** (baseline ending line 418), before the class ends. Add new methods in the order shown; retain four-space method indentation.

````python
    def _pick_editor_color(self, key, button):
        """Store a valid color override only when the picker is accepted."""
        color = QColorDialog.getColor(QColor(self._appearance_colors[key] or "#ffffff"), self, "Editor color")
        if color.isValid():
            self._appearance_colors[key] = color.name()
            button.setText(color.name())
````

**Code explanation:** Store a valid color override only when the picker is accepted.

<a id="method-code-settings-settings-dialog-py-settingsdialog-reset-editor-color"></a>
### ADD `SettingsDialog._reset_editor_color`

**File:** `code_settings/settings_dialog.py`. **Owner:** `SettingsDialog`. Insert inside the class **after `get_settings`** (baseline ending line 418), before the class ends. Add new methods in the order shown; retain four-space method indentation.

````python
    def _reset_editor_color(self, key, button):
        """Remove a dialog-level override so Save restores active-theme inheritance."""
        self._appearance_colors[key] = None
        button.setText("Use theme")
````

**Code explanation:** Remove a dialog-level override so Save restores active-theme inheritance.

<a id="integrate-markdown-editor-markdowneditor-py"></a>
## Edit `markdown_editor/markdowneditor.py`

### Add imports

At module scope in `markdown_editor/markdowneditor.py`, insert these imports **immediately after** `from markdown_editor.markdowncustomlexer import MarkdownCustomLexer` (baseline ending line 8), before the next existing statement. Do not duplicate them.

````python
from code_inteligence.snippet_controller import SnippetController
from code_inteligence.folding_controller import FoldingController
from side_bar_widgets.editor_minimap import EditorMinimap
````

### Add the `MarkdownEditor` class docstring

Immediately after the `class MarkdownEditor(...):` header (baseline line 11), before its first attribute or method, insert:

````python
    """Edit Markdown with existing syntax behavior plus snippets, folding and a per-view minimap."""
````

<a id="method-markdown-editor-markdowneditor-py-markdowneditor-init"></a>
### REPLACE `MarkdownEditor.__init__`

**File:** `markdown_editor/markdowneditor.py`. **Baseline lines:** 13–61. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_apply_theme_editor_style` definition.

````python
    def __init__(self, parent=None, path: Path=None, is_python_file: bool=False):
        """Configure the Markdown lexer and existing editing options, then attach view-level helpers."""
        super(MarkdownEditor, self).__init__(parent)
        self.path = path
        self._loading_text = False
        self._shutting_down = False
        self.full_path = self.path.absolute() if self.path else None
        self.is_python_file = is_python_file
        # encoding
        self.setUtf8(True)
        # NOTE: no editor-level font anymore — the theme (via the lexer)
        # owns family, size, colors and paper. _apply_theme_editor_style()
        # below pulls the editor-wide look from the lexer after it loads
        # the theme. JetBrains Mono 13 is only the pre-lexer fallback.

        # brace matching
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # indentation
        self.setIndentationGuides(True)
        self.setTabWidth(2)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)

        self.setEolMode(QsciScintilla.EolUnix if sys.platform != "win32" else QsciScintilla.EolWindows)
        self.setEolVisibility(False)

        # autocomplete
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # caret (fallbacks; the theme's editor section replaces them via
        # _apply_theme_editor_style once the lexer is attached)
        self.setCaretForegroundColor(QColor('#f31122'))  # sets text caret color
        self.setCaretLineVisible(True)  # enables the background color of the caret line
        self.setCaretWidth(2)  # sets the caret with
        self.setCaretLineBackgroundColor(QColor('#3d424d')) # changes the background color of the caret line

        # set lexer — it loads themes/theme.json itself and derives every
        # font/color/paper from it (single source of truth)
        self.md_lexer = MarkdownCustomLexer(self)
        self.setLexer(self.md_lexer)
        self._apply_theme_editor_style()

        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)

        self.snippets = SnippetController(self)
        self.folding_controller = FoldingController(self, "markdown")
        self.minimap = EditorMinimap(self)
        self.minimap.set_map_visible(False)
````

**Code explanation:** Configure the Markdown lexer and existing editing options, then attach view-level helpers.

<a id="method-markdown-editor-markdowneditor-py-markdowneditor-keypressevent"></a>
### REPLACE `MarkdownEditor.keyPressEvent`

**File:** `markdown_editor/markdowneditor.py`. **Baseline lines:** 90–94. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `setTextSafely` definition.

````python
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
````

**Code explanation:** Consume active snippet navigation keys, then preserve existing completion and editing behavior.

<a id="method-markdown-editor-markdowneditor-py-markdowneditor-shutdown"></a>
### REPLACE `MarkdownEditor.shutdown`

**File:** `markdown_editor/markdowneditor.py`. **Baseline lines:** 110–111. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop at the end of the named definition; retain the surrounding class/module.

````python
    def shutdown(self):
        """Stop view timers and snippet navigation before the editor is retired."""
        self.folding_controller._timer.stop()
        self.minimap._refresh_timer.stop()
        self.snippets.cancel()
        self._shutting_down = True
````

**Code explanation:** Stop view timers and snippet navigation before the editor is retired.

<a id="integrate-python-editor-pythoneditor-py"></a>
## Edit `python_editor/pythoneditor.py`

### Add imports

At module scope in `python_editor/pythoneditor.py`, insert these imports **immediately after** `from ruff_implementation.ruff_lsp_controller import RuffLspController` (baseline ending line 20), before the next existing statement. Do not duplicate them.

````python
from code_inteligence.snippet_controller import SnippetController
from code_inteligence.folding_controller import FoldingController
from side_bar_widgets.editor_minimap import EditorMinimap
from code_inteligence.references_finder import ReferencesFinder
from code_inteligence.locations_panel import SourceLocation
````

### Add the `PythonEditor` class docstring

Immediately after the `class PythonEditor(...):` header (baseline line 32), before its first attribute or method, insert:

````python
    """Edit Python with existing Ruff and Jedi services plus snippet, fold, minimap and reference support."""
````

### Add `PythonEditor` class attributes

Inside `PythonEditor`, insert these four-space-indented declarations **before** its first existing class statement at baseline line 33. Keep the existing declarations below them.

````python
    referencesReady = pyqtSignal(list)
    referencesFailed = pyqtSignal(str)
````

<a id="method-python-editor-pythoneditor-py-pythoneditor-init"></a>
### REPLACE `PythonEditor.__init__`

**File:** `python_editor/pythoneditor.py`. **Baseline lines:** 37–179. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_apply_theme_editor_style` definition.

````python
    def __init__(self, parent=None, path: Path = None, is_python_file: bool = True, ruff_lsp_client = None):
        """Initialize the existing Python editor and attach references, snippets, folding and a minimap."""
        super().__init__(parent)
        
        # Store the absolute logical file path. Ruff LSP uses it to form the stable
        # document UEI sent in didOpen/didChanged notifications.
        
        self.path = path
        self.full_path = self.path.absolute() if self.path else None
        self.is_python_file = is_python_file
        self.ruff_lsp = None
        self._manual_completion_generation = None

        self._ruff_hover_active = False
        self._loading_text = False
        self._shutting_down = False
        self._autocomplete_timer = QTimer(self)
        self._autocomplete_timer.setSingleShot(True)
        self._autocomplete_timer.setInterval(300)
        self._autocomplete_timer.timeout.connect(self._trigger_autocomplete)

        self._pending_line = 0
        self._pending_index = 0
        self.cursorPositionChanged.connect(self._cursorPositionChanged)

        self.setUtf8(True)

        # NOTE: no editor-level font anymore. The theme (via the lexer)
        # owns family, size, colors and paper — one source of truth.
        # The lexer is created below; helpers on it (editor_font(),
        # editor_color()) supply the margins/popup/caret values.

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setIndentationGuides(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)
        self.setEolMode(
            QsciScintilla.EolUnix if sys.platform != "win32" else QsciScintilla.EolWindows
        )
        self.setEolVisibility(False)

        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # Caret styling defaults; replaced by theme values once the lexer
        # exists (see _apply_theme_editor_style below + _apply_editor_settings
        # in main.py after a lexer swap). Kept as safe fallbacks so the
        # widget is never unstyled before a theme loads.
        self.setCaretForegroundColor(QColor("#f31122"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#3d424d"))
        self.setCaretWidth(2)

        if self.is_python_file:
            if ruff_lsp_client is not None:
                self.ruff_lsp = RuffLspController(editor=self, client=ruff_lsp_client, parent=self)


            self._ruff_hover_timer = QTimer(self)
            self._ruff_hover_timer.setSingleShot(True)
            self._ruff_hover_timer.setInterval(150)
            self._ruff_hover_timer.timeout.connect(self._trigger_ruff_hover)
            
            # An owned timer can be stopped when Space/Enter dismisses help.
            self._signature_timer = QTimer(self)
            self._signature_timer.setSingleShot(True)
            self._signature_timer.setInterval(50)
            self._signature_timer.timeout.connect(self._trigger_signature_help)
            self.signature_helper = SignatureHelper()
            self.signature_helper.signature_ready.connect(self._on_signature_ready)
            self.signature_helper.signature_empty.connect(self._on_signature_empty)

            self.hover_helper = HoverHelper()
            self.hover_helper.hover_info_ready.connect(self._on_hover_ready)
            self.hover_helper.hover_info_empty.connect(self._on_hover_empty)

            # DocumentationPopup ows only the UI. HoverHelper still performs
            # Jedi analysis is its worker thread and emits plain text results.
            # Create one popup for this editor tab. Passing self as parent means
            # Qt cleans it up automatically when this PythonEditor is destroyed.
            # The lexer loads the theme itself — font, colors and paper all
            # come from themes/theme.json (or the theme chosen in Settings).
            # Created FIRST so everything below can read its theme helpers.
            self.py_lexer = PyCustomLexer(self)

            self.documentation_popup = DocumentationPopup(self)
            self.documentation_popup.dismissed.connect(self._cancel_documentation)
            self._documentation_global_pos = None
            # Popup font follows the theme's global editor font (the old
            # self.window_font is gone — the lexer owns fonts now).
            self.documentation_popup.set_documentation_font(
                self.py_lexer.editor_font())

            self.setMouseTracking(True)

            self._apply_theme_editor_style()

            self._api = QsciAPIs(self.py_lexer)
            self.auto_completer = AutoCompleter(
                str(self.full_path) if self.full_path else None, self._api
            )
            self.auto_completer.completions_ready.connect(self._apply_completions)
            self.auto_completer.error.connect(self._handle_completion_error)

            self.setLexer(self.py_lexer)
        else:
            # No lexer in this mode yet (tab not converted): neutral defaults.
            # Once a lexer attaches, _apply_theme_editor_style takes over.
            self.setPaper(QColor("#1e1f22"))
            self.setColor(QColor("#abb2bf"))

        self.definition_finder = DefinitionFinder()
        self.definition_finder.definition_found.connect(self._on_definition_found)
        self.definition_finder.definition_not_found.connect(self._on_definition_not_found)
        self.definition_finder.error.connect(self._on_definition_error)

        # Margin 0: source-code line numbers.
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")

        # Margin 1: Ruff error, warning, information and quick-fix symbols.
        self.setMarginType(1, QsciScintilla.SymbolMargin)
        self.setMarginWidth(1, "000")

        ruff_marker_mask = (
            (1 << RuffDiagnosticView.ERROR_MARKER)
            | (1 << RuffDiagnosticView.WARNING_MARKER)
            | (1 << RuffDiagnosticView.INFO_MARKER)
            | (1 << RuffDiagnosticView.FIX_MARKER)
        )
        self.setMarginMarkerMask(1, ruff_marker_mask)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)

        # Final theme application (font, margins, caret, paper) — AFTER all
        # margin setup so nothing overrides it. The old hardcoded
        # setMarginsForegroundColor/BackgroundColor/setMarginsFont lines
        # that used to live here are replaced by this one theme-driven call.
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()

        self.references_finder = ReferencesFinder()
        self.references_finder.references_found.connect(self._references_found)
        self.references_finder.references_empty.connect(lambda generation: self._references_found(generation, []))
        self.references_finder.error.connect(self._references_error)
        self.textChanged.connect(self.references_finder.invalidate)
        self.snippets = SnippetController(self)
        self.folding_controller = FoldingController(self, "python")
        self.minimap = EditorMinimap(self)
        self.minimap.set_map_visible(False)
````

**Code explanation:** Initialize the existing Python editor and attach references, snippets, folding and a minimap.

<a id="method-python-editor-pythoneditor-py-pythoneditor-contextmenuevent"></a>
### REPLACE `PythonEditor.contextMenuEvent`

**File:** `python_editor/pythoneditor.py`. **Baseline lines:** 254–280. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_on_hover_ready` definition.

````python
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
````

**Code explanation:** Request documentation for a right-clicked identifier. Blank space retains the existing diagnostic/editor context menu. A keyboard menu request also keeps the normal context menu behavior.

<a id="method-python-editor-pythoneditor-py-pythoneditor-keypressevent"></a>
### REPLACE `PythonEditor.keyPressEvent`

**File:** `python_editor/pythoneditor.py`. **Baseline lines:** 402–459. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_dismiss_signature` definition.

````python
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
````

**Code explanation:** Handle editor shortcuts, indentation, and signature scheduling.

<a id="method-python-editor-pythoneditor-py-pythoneditor-cursorpositionchanged"></a>
### REPLACE `PythonEditor._cursorPositionChanged`

**File:** `python_editor/pythoneditor.py`. **Baseline lines:** 528–542. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_trigger_autocomplete` definition.

````python
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
````

**Code explanation:** Called when the cursor moves. Starts a debounce timer instead of immediately running Jedi analysis.

<a id="method-python-editor-pythoneditor-py-pythoneditor-analysis-workers"></a>
### REPLACE `PythonEditor._analysis_workers`

**File:** `python_editor/pythoneditor.py`. **Baseline lines:** 568–576. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `shutdown` definition.

````python
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
````

**Code explanation:** Return every per-editor QThread that must outlive the tab.

<a id="method-python-editor-pythoneditor-py-pythoneditor-shutdown"></a>
### REPLACE `PythonEditor.shutdown`

**File:** `python_editor/pythoneditor.py`. **Baseline lines:** 578–603. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `_check_shutdown_complete` definition.

````python
    def shutdown(self):
        """Stop producing results annd emit when all workers naturally finish."""
        self.folding_controller._timer.stop()
        self.minimap._refresh_timer.stop()
        self.snippets.cancel()
        if self._shutting_down:
            return
        self._shutting_down = True
        self._loading_text = True
        self._autocomplete_timer.stop()
        if self.is_python_file:
            self.documentation_popup.dismiss()
            self._dismiss_signature()
        for timer_name in ("_signature_timer", "_ruff_hover_timer"):
            timer = getattr(self, timer_name, None)
            if timer is not None:
                timer.stop()
        
        if self.ruff_lsp is not None:
            self.ruff_lsp.shutdown()
            
        workers = self._analysis_workers()
        for worker in workers:
            worker.shutdown()
            try:
                worker.finished.connect(self._check_shutdown_complete)
            except TypeError:
                pass
        self._check_shutdown_complete()
````

**Code explanation:** Stop producing results annd emit when all workers naturally finish.

<a id="method-python-editor-pythoneditor-py-pythoneditor-find-all-references"></a>
### ADD `PythonEditor.find_all_references`

**File:** `python_editor/pythoneditor.py`. **Owner:** `PythonEditor`. Insert inside the class **after `closeEvent`** (baseline ending line 612), before the class ends. Add new methods in the order shown; retain four-space method indentation.

````python
    def find_all_references(self):
        """Find semantic references using the selected project's interpreter and root."""
        if self._shutting_down or not self.is_python_file:
            return
        window = self.window()
        line, column = self.getCursorPosition()
        self.references_finder.find_references(line + 1, column, self.text(),
            str(self.full_path) if self.full_path else None,
            str(window._workspace_root), window.python_runner.interpreter)
````

**Code explanation:** Find semantic references using the selected project's interpreter and root.

<a id="method-python-editor-pythoneditor-py-pythoneditor-references-found"></a>
### ADD `PythonEditor._references_found`

**File:** `python_editor/pythoneditor.py`. **Owner:** `PythonEditor`. Insert inside the class **after `closeEvent`** (baseline ending line 612), before the class ends. Add new methods in the order shown; retain four-space method indentation.

````python
    def _references_found(self, generation, rows):
        """Publish plain navigation records only for the current live request."""
        if generation == self.references_finder.generation and not self._shutting_down:
            self.referencesReady.emit([SourceLocation(Path(path), line, column, name)
                                       for path, line, column, name in rows])
````

**Code explanation:** Publish plain navigation records only for the current live request.

<a id="method-python-editor-pythoneditor-py-pythoneditor-references-error"></a>
### ADD `PythonEditor._references_error`

**File:** `python_editor/pythoneditor.py`. **Owner:** `PythonEditor`. Insert inside the class **after `closeEvent`** (baseline ending line 612), before the class ends. Add new methods in the order shown; retain four-space method indentation.

````python
    def _references_error(self, generation, message):
        """Report a current request failure to the owning window's visible status area."""
        if generation == self.references_finder.generation and not self._shutting_down:
            self.referencesFailed.emit(message)
````

**Code explanation:** Report a current request failure to the owning window's visible status area.

<a id="integrate-ruff-implementation-ruff-lsp-controller-py"></a>
## Edit `ruff_implementation/ruff_lsp_controller.py`

### Replace import

Replace `ruff_implementation/ruff_lsp_controller.py` baseline lines 8–8, the complete `from PyQt5.QtCore import QObject, QTimer, pyqtSignal` statement, with:

````python
from PyQt5.QtCore import QObject, QTimer, QPoint, pyqtSignal
````

### Replace import

Replace `ruff_implementation/ruff_lsp_controller.py` baseline lines 9–9, the complete `from PyQt5.QtWidgets import QToolTip` statement, with:

````python
from PyQt5.QtWidgets import QToolTip, QMenu, QMessageBox
````

### Add imports

At module scope in `ruff_implementation/ruff_lsp_controller.py`, insert these imports **immediately after** `from ruff_implementation.ruff_diagnostics_view import RuffDiagnosticView` (baseline ending line 12), before the next existing statement. Do not duplicate them.

````python
from ruff_implementation.workspace_edit import WorkspaceEditApplier, WorkspaceEditError
````

<a id="method-ruff-implementation-ruff-lsp-controller-py-rufflspcontroller-context-menu"></a>
### REPLACE `RuffLspController.context_menu`

**File:** `ruff_implementation/ruff_lsp_controller.py`. **Baseline lines:** 255–258. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `shutdown` definition.

````python
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
````

**Code explanation:** Display current Ruff quick fixes without retaining the temporary Qt event.

<a id="method-ruff-implementation-ruff-lsp-controller-py-rufflspcontroller-request-quick-fixes"></a>
### ADD `RuffLspController.request_quick_fixes`

**File:** `ruff_implementation/ruff_lsp_controller.py`. **Owner:** `RuffLspController`. Insert inside the class **after `shutdown`** (baseline ending line 276), before the class ends. Add new methods in the order shown; retain four-space method indentation.

````python
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
````

**Code explanation:** Request actions with raw provider data and capture the exact document identity.

<a id="method-ruff-implementation-ruff-lsp-controller-py-rufflspcontroller-apply-code-action"></a>
### ADD `RuffLspController.apply_code_action`

**File:** `ruff_implementation/ruff_lsp_controller.py`. **Owner:** `RuffLspController`. Insert inside the class **after `shutdown`** (baseline ending line 276), before the class ends. Add new methods in the order shown; retain four-space method indentation.

````python
    def apply_code_action(self, action, uri, revision):
        """Apply a direct edit completely or report an unsupported action form."""
        if action.get("disabled") or action.get("command") or not isinstance(action.get("edit"), dict):
            raise WorkspaceEditError("This action needs an unsupported command or resolve step")
        WorkspaceEditApplier(self).apply(action["edit"], uri, revision)
````

**Code explanation:** Apply a direct edit completely or report an unsupported action form.

<a id="integrate-side-bar-widgets-file-manager-py"></a>
## Edit `side_bar_widgets/file_manager.py`

### Add the `FileManager` class docstring

Immediately after the `class FileManager(...):` header (baseline line 20), before its first attribute or method, insert:

````python
    """Display the filesystem with existing management actions and distinct preview/permanent opens."""
````

<a id="method-side-bar-widgets-file-manager-py-filemanager-init"></a>
### REPLACE `FileManager.__init__`

**File:** `side_bar_widgets/file_manager.py`. **Baseline lines:** 21–76. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `check_git_status` definition.

````python
    def __init__(self, set_new_tab, main_window, parent=None):
        """Configure the existing file tree and wire single-click previews and double-click permanent opens."""
        super(FileManager, self).__init__(None)

        self.set_new_tab = set_new_tab
        self.main_window = main_window
        
        self._rename_old_path = None
        self._rename_is_directory = False
        self.is_renaming = False
        self.current_edit_index = None

        self.manager_font = QFont("sans-serif", 13)

        self.model = GitAwareFileSystemModel(self)
        self.model.setRootPath(os.getcwd())
        # File system filters
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.Drives)
        self.model.setReadOnly(False)
        self.setFocusPolicy(Qt.NoFocus)

        self.setFont(self.manager_font)
        self.setModel(self.model)
        self.setRootIndex(self.model.index(os.getcwd()))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)

        # add text menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # hank
        self.clicked.connect(self.tree_view_clicked)
        self.doubleClicked.connect(self._open_permanent)
        self.setIndentation(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Hiding other columns except for name
        self.setHeaderHidden(True)
        self.setColumnHidden(1,True)
        self.setColumnHidden(2,True)
        self.setColumnHidden(3,True)

        # enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)

        # enable file name editing
        # renaming
        self.itemDelegate().closeEditor.connect(self._on_closeEditor)
        
        from python_editor.git_integration import GitStatusChecker
        self.git_checker = GitStatusChecker()
        self.git_checker.status_ready.connect(self._on_git_status)
        self.git_statuses = {}
````

**Code explanation:** Configure the existing file tree and wire single-click previews and double-click permanent opens.

<a id="method-side-bar-widgets-file-manager-py-filemanager-tree-view-clicked"></a>
### REPLACE `FileManager.tree_view_clicked`

**File:** `side_bar_widgets/file_manager.py`. **Baseline lines:** 112–116. Delete the complete existing definition, including any decorator, and paste the replacement at the same indentation. Stop before the following `dragEnterEvent` definition.

````python
    def tree_view_clicked(self, index: QModelIndex):
        """Open a file as a replaceable clean preview; leave directory navigation to the tree."""
        path = self.model.filePath(index)
        p = Path(path)
        if p.is_file():
            self.set_new_tab(p, preview=True)
````

**Code explanation:** Open a file as a replaceable clean preview; leave directory navigation to the tree.

<a id="method-side-bar-widgets-file-manager-py-filemanager-open-permanent"></a>
### ADD `FileManager._open_permanent`

**File:** `side_bar_widgets/file_manager.py`. **Owner:** `FileManager`. Insert inside the class **after `current_folder`** (baseline ending line 445), before the class ends. Add new methods in the order shown; retain four-space method indentation.

````python
    def _open_permanent(self, index):
        """Promote a double-clicked file to a permanent tab using the existing open workflow."""
        path = Path(self.model.filePath(index))
        if path.is_file():
            self.set_new_tab(path, preview=False)
````

**Code explanation:** Promote a double-clicked file to a permanent tab using the existing open workflow.

## What to remove or retain

- Replace the listed existing methods completely. Do not keep both the original and replacement definitions.
- The old `self._dirty_editors = set()` initialization is replaced by the `DirtyViews` adapter. Keep existing callers of that interface; their state now comes from `DocumentStateStore`.
- Replace `RuffLspController.context_menu()`'s old unconditional `return False` placeholder with the asynchronous quick-fix implementation.
- Replace the old references worker file with the complete version in Topic 5. The editor owns that worker through `_analysis_workers()` during closure.
- Keep the original completion, indentation, documentation popup, and editor key behavior after the snippet checks in the combined `keyPressEvent()` replacements.
- Keep the existing Git service, history model, commit graph, file-color worker, and periodic/manual refresh. Do not add the attached course's second Git implementation.
- Do not delete any whole existing source file or add the course's proposed top-level feature packages. All new source files are placed in existing package folders above.

## Start the editor

Once all feature files and combined replacements are in place, launch from the repository root:

```bash
python main.py
```

The new actions are grouped under **Editor Tools**. Caret and selection settings are in the existing **Settings → Appearance** dialog. File-tree single-click opens a preview; double-click or a normal Open action makes it permanent. Right-click a tab for pinning, close-to-right, and duplicate-view actions.

