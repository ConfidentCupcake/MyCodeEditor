# MarkdownEditor — complete implementation guide

**Repository:** [ConfidentCupcake/MarkdownEditor](https://github.com/ConfidentCupcake/MarkdownEditor)  
**Required baseline:** [`17f08584813a91fc5a5450590130c7292a46de37`](https://github.com/ConfidentCupcake/MarkdownEditor/tree/17f08584813a91fc5a5450590130c7292a46de37)  
**Guide date:** 5 October 2026  
**Content source:** `MarkdownEditor_COURSE_EXERCISES_AND_IMPLEMENTATION_2026-10-03.md`  
**Structure reference:** `MarkdownEditor_DETAILED_IMPLEMENTATION_GUIDE_2026-09-11.md`

## Purpose and rules

This guide completes the 30 topics in the course and restructures them into the detailed template's implementation sequence: explain the feature, identify files and locations, provide complete code, explain the code, and verify the behavior. It retains 60 exercises with closed solution dropdowns. The September template's older baseline and bug fixes are not copied onto this repository; all existing-file locations below refer to the pinned October course baseline.

Every implementation path is relative to the repository root. Baseline line numbers are navigation aids: after edits shift them, the named class/method and its next-definition boundary are authoritative. **Replace** means remove the complete old definition and paste the replacement at the same indentation. **Create** means use the entire supplied file. Shared lifecycle methods are consolidated in Final integration and applied once.

Exercise answers are learning copies. Install each complete file and each integration replacement once; do not paste an exercise answer on top of the full implementation. Every supplied class, method, and function has a docstring; inline comments explain important ownership, validation, concurrency, and byte-position decisions.

### Before editing

Use your existing clone. Confirm its current commit and working-tree state before starting a feature branch:

```bash
git status --short
git rev-parse HEAD
git switch -c feature/complete-editor-guide
```

The expected commit is the required baseline above. If your checkout has additional changes, reconcile the named methods against those changes before applying replacements; baseline line ranges must not be used to overwrite unrelated work. Keep your existing working changes intact.

### Folders

The implementation uses existing `code_inteligence/`, `code_settings/`, `markdown_editor/`, `markdowneditor_assets/`, `python_editor/`, `side_bar_widgets/`, and `tests/`. Keep the repository's actual spelling **`code_inteligence`**. No new source folder or package marker is required. Recovery/history/run-profile directories are created at runtime under the application data directory; do not create them inside the repository.

### Installation order

| Order | Work | Location |
|---:|---|---|
| 1 | Create/replace feature modules | Topics 01–30 below; finish all modules before launching |
| 2 | Add imports, class docstrings, constants, and combined existing methods | Final integration |
| 3 | Add the complete controller once | Final integration, after MainWindow and before main() |
| 4 | Update both scanner backends and build the optional native extension | Native lexer integration |
| 5 | Create the three test modules and run checks | Test installation |
| 6 | Exercise visible desktop behavior | Per-topic checks and final acceptance checklist |

### Completed gaps in the original course

| Earlier gap | Implementation supplied here |
|---|---|
| Checkpoint model only | Production Python/Cython scanner snapshots and lexer integration |
| Scheduler limited to workspace symbols | All five existing Jedi providers plus references, rename, and symbols use one queue |
| Test output without a collected-test model | pytest hook bridge, exact node IDs, selection, rerun-failed, results, and independent process |
| Missing Problems/references/minimap UI | Snapshot docks and bounded clickable minimap |
| Basic compare/history flow | Side-by-side comparison, retained-version browser, accepted drafts, three-way merges |
| Incomplete welcome/layout/authoring flows | Recent projects, templates, built-in presets, image/heading links, parser-backed anchors |
| Partial lazy creation | Deferred terminal/console bodies and lazy Tests/run-output docks |
| Unconnected new commands | Combined QAction shortcut registry and usable focus escape binding |

## Topic index

| Topic | Feature | Exercises |
|---:|---|---|
| 01 | [Unified design system](#topic-01) | A: implementation; B: regression |
| 02 | [Consistent SVG icons](#topic-02) | A: implementation; B: regression |
| 03 | [Breadcrumb navigation](#topic-03) | A: implementation; B: regression |
| 04 | [Compact and comfortable layouts](#topic-04) | A: implementation; B: regression |
| 05 | [Improved status bar](#topic-05) | A: implementation; B: regression |
| 06 | [Polished empty states](#topic-06) | A: implementation; B: regression |
| 07 | [Welcome screen](#topic-07) | A: implementation; B: regression |
| 08 | [Focus mode](#topic-08) | A: implementation; B: regression |
| 09 | [Workspace layout presets](#topic-09) | A: implementation; B: regression |
| 10 | [Automatic recovery](#topic-10) | A: implementation; B: regression |
| 11 | [Local file history](#topic-11) | A: implementation; B: regression |
| 12 | [External-change comparison](#topic-12) | A: implementation; B: regression |
| 13 | [Compare/diff editor](#topic-13) | A: implementation; B: regression |
| 14 | [Rename symbol with preview](#topic-14) | A: implementation; B: regression |
| 15 | [Workspace symbol search](#topic-15) | A: implementation; B: regression |
| 16 | [Test runner panel](#topic-16) | A: implementation; B: regression |
| 17 | [Run configurations](#topic-17) | A: implementation; B: regression |
| 18 | [Configurable keyboard shortcuts](#topic-18) | A: implementation; B: regression |
| 19 | [Smarter pair handling](#topic-19) | A: implementation; B: regression |
| 20 | [Outline and navigation](#topic-20) | A: implementation; B: regression |
| 21 | [Authoring tools](#topic-21) | A: implementation; B: regression |
| 22 | [Performance diagnostics mode](#topic-22) | A: implementation; B: regression |
| 23 | [Lazy initialization](#topic-23) | A: implementation; B: regression |
| 24 | [Background file hashing](#topic-24) | A: implementation; B: regression |
| 25 | [Incremental syntax highlighting](#topic-25) | A: implementation; B: regression |
| 26 | [Smarter Markdown preview updates](#topic-26) | A: implementation; B: regression |
| 27 | [Large-file mode](#topic-27) | A: implementation; B: regression |
| 28 | [Shared analysis scheduling](#topic-28) | A: implementation; B: regression |
| 29 | [Bounded result caching](#topic-29) | A: implementation; B: regression |
| 30 | [Pause hidden-panel work](#topic-30) | A: implementation; B: regression |

---

<a id="topic-01"></a>
## Topic 01 — Unified design system

### 1. Topic and resulting behavior

One semantic palette gives menus, tabs, buttons, and dock headers consistent colors. Generated QSS supplies the shared widget rules; syntax tokens and terminal ANSI colors keep their existing theme owners.

### 2. Official documentation and code walkthrough

Change density twice. The window rebuilds from its captured base stylesheet, so rules do not accumulate. Follow PALETTE → theme_qss → MainWindow.apply_design_density.

- [Qt 5 style sheets](https://doc.qt.io/archives/qt-5.15/stylesheet.html)
- [Qt 5 style sheet reference](https://doc.qt.io/archives/qt-5.15/stylesheet-reference.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_settings/design_system.py` | [`PALETTE`](#file-code-settings-design-system-py) |
| `code_settings/design_system.py` | [`theme_qss`](#file-code-settings-design-system-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `theme_qss` in `code_settings/design_system.py`. **Contract:** Generate one scoped widget stylesheet from shared semantic tokens. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_settings/design_system.py`. **Placement:** the complete `theme_qss` definition in its named owner. The [installation block](#file-code-settings-design-system-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** Change density twice. The window rebuilds from its captured base stylesheet, so rules do not accumulate. Follow PALETTE → theme_qss → MainWindow.apply_design_density. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_01_design_tokens` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Reject an unknown preference before emitting invalid stylesheet data.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_01_design_tokens():
    """Reject an unknown preference before emitting invalid stylesheet data."""
    assert 'padding: 7px' in theme_qss('comfortable')
    assert '#61afef' in theme_qss('comfortable')
    with pytest.raises(ValueError):
        theme_qss('tiny')
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_01_design_tokens"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-settings-design-system-py"></a>
#### CREATE FILE — `code_settings/design_system.py`

**Folder:** `code_settings/` already exists. Create **only** `design_system.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Shared interface colors and density rules.

### 7. Acceptance check

Switch density repeatedly and inspect selected tabs, dock titles, disabled buttons, and focus borders.

---

<a id="topic-02"></a>
## Topic 02 — Consistent SVG icons

### 1. Topic and resulting behavior

A single icon provider resolves the existing packaged SVG assets and supplies normal/active states. Sidebar controls become keyboard-accessible QToolButtons with a real checked state.

### 2. Official documentation and code walkthrough

themed_icon combines asset_path with QIcon states. MainWindow.get_sidebar_label creates each button; _set_sidebar_icon changes the checked state instead of constructing an unrelated image path.

- [Qt QIcon states](https://doc.qt.io/archives/qt-5.15/qicon.html)
- [Qt QToolButton](https://doc.qt.io/archives/qt-5.15/qtoolbutton.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `markdowneditor_assets/icon_provider.py` | [`themed_icon`](#file-markdowneditor-assets-icon-provider-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `themed_icon` in `markdowneditor_assets/icon_provider.py`. **Contract:** Load existing 24px SVG icons with actual disabled/selected Qt states. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `markdowneditor_assets/icon_provider.py`. **Placement:** the complete `themed_icon` definition in its named owner. The [installation block](#file-markdowneditor-assets-icon-provider-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** themed_icon combines asset_path with QIcon states. MainWindow.get_sidebar_label creates each button; _set_sidebar_icon changes the checked state instead of constructing an unrelated image path. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_02_icon_assets` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Use the actual shipped assets and reject names outside the sidebar.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_02_icon_assets(app):
    """Use the actual shipped assets and reject names outside the sidebar."""
    assert not themed_icon('terminal').isNull()
    with pytest.raises(ValueError):
        themed_icon('../terminal')
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_02_icon_assets"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-markdowneditor-assets-icon-provider-py"></a>
#### CREATE FILE — `markdowneditor_assets/icon_provider.py`

**Folder:** `markdowneditor_assets/` already exists. Create **only** `icon_provider.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** State-aware icons from the existing SVG assets.

### 7. Acceptance check

Open each sidebar panel using both keyboard and mouse; check that its active icon follows the selected panel.

---

<a id="topic-03"></a>
## Topic 03 — Breadcrumb navigation

### 1. Topic and resulting behavior

Breadcrumbs show the active document and its containing Python class/function. Symbol extraction uses Python AST ranges, so a method belongs to its containing class rather than to the most recently encountered name.

### 2. Official documentation and code walkthrough

python_symbols records source ranges; symbol_at selects the innermost enclosing symbol. cursor_changed refreshes the breadcrumb and _jump converts navigation into editor coordinates.

- [Python AST locations](https://docs.python.org/3/library/ast.html)
- [Qt layouts](https://doc.qt.io/archives/qt-5.15/qhboxlayout.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/symbol_index.py` | [`Symbol`](#file-code-inteligence-symbol-index-py) |
| `code_inteligence/symbol_index.py` | [`python_symbols`](#file-code-inteligence-symbol-index-py) |
| `code_inteligence/symbol_index.py` | [`symbol_at`](#file-code-inteligence-symbol-index-py) |
| `side_bar_widgets/breadcrumb.py` | [`Breadcrumb`](#file-side-bar-widgets-breadcrumb-py) |
| `main.py` | [`EditorFeatureController.cursor_changed`](#controller) |
| `main.py` | [`EditorFeatureController._jump`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `symbol_at` in `code_inteligence/symbol_index.py`. **Contract:** Return the enclosing symbol chain for a zero-based source line. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/symbol_index.py`. **Placement:** the complete `symbol_at` definition in its named owner. The [installation block](#file-code-inteligence-symbol-index-py) gives the exact file or baseline placement. This answer is already included there.

````python
def symbol_at(symbols: list[Symbol], line: int) -> list[Symbol]:
    """Return the enclosing symbol chain for a zero-based source line."""
    # AST end_lineno prevents a method breadcrumb leaking into the next class.
    eligible = [item for item in symbols if item.line <= line <= item.end_line]
    return sorted(eligible, key=lambda item: (item.line, -item.end_line))
````

**Why this works:** python_symbols records source ranges; symbol_at selects the innermost enclosing symbol. cursor_changed refreshes the breadcrumb and _jump converts navigation into editor coordinates. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_03_breadcrumb_scope` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Only the enclosing class and method contribute symbol buttons.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_03_breadcrumb_scope(app, tmp_path):
    """Only the enclosing class and method contribute symbol buttons."""
    source = 'class A:\n    def run(self):\n        return 1\nclass B:\n    pass\n'
    symbols = python_symbols(tmp_path / 'a.py', source)
    assert [s.name for s in symbol_at(symbols, 2)] == ['A', 'run']
    assert [s.name for s in symbol_at(symbols, 4)] == ['B']
    destinations = []
    bar = Breadcrumb(lambda row, col: destinations.append((row, col)))
    bar.show_location(tmp_path, tmp_path / 'a.py', source, 2, True)
    bar.row.itemAt(3).widget().click()
    assert destinations == [(1, 4)]
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_03_breadcrumb_scope"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-symbol-index-py"></a>
#### CREATE FILE — `code_inteligence/symbol_index.py`

**Folder:** `code_inteligence/` already exists. Create **only** `symbol_index.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Python source symbols and bounded workspace indexing.

<a id="file-side-bar-widgets-breadcrumb-py"></a>
#### CREATE FILE — `side_bar_widgets/breadcrumb.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `breadcrumb.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Clickable document and symbol navigation.

### 7. Acceptance check

Move between two methods and outside the class. Activate breadcrumb segments and confirm the correct line receives the caret.

---

<a id="topic-04"></a>
## Topic 04 — Compact and comfortable layouts

### 1. Topic and resulting behavior

Compact and comfortable modes change shared padding and sidebar geometry while preserving document text, selections, and syntax colors. QSettings retains the selected mode.

### 2. Official documentation and code walkthrough

The two menu actions pass explicit density values. apply_design_density validates the preference, regenerates QSS from the original base, and updates the existing sidebar buttons.

- [Qt style sheets](https://doc.qt.io/archives/qt-5.15/stylesheet.html)
- [Qt QSettings](https://doc.qt.io/archives/qt-5.15/qsettings.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_settings/design_system.py` | [`theme_qss`](#file-code-settings-design-system-py) |
| `main.py` | [`EditorFeatureController._install_menu`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `theme_qss` in `code_settings/design_system.py`. **Contract:** Generate one scoped widget stylesheet from shared semantic tokens. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_settings/design_system.py`. **Placement:** the complete `theme_qss` definition in its named owner. The [installation block](#file-code-settings-design-system-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** The two menu actions pass explicit density values. apply_design_density validates the preference, regenerates QSS from the original base, and updates the existing sidebar buttons. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_04_density_roundtrip` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Regenerating the same profile is stable and does not append rules.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_04_density_roundtrip():
    """Regenerating the same profile is stable and does not append rules."""
    comfortable = theme_qss('comfortable')
    assert 'padding: 3px' in theme_qss('compact')
    assert theme_qss('comfortable') == comfortable
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_04_density_roundtrip"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

This topic shares the complete modules linked in the file table. Apply those files once, then its controller/MainWindow connections in Final integration.

### 7. Acceptance check

Switch both ways, restart the editor, and check that the chosen density persists.

---

<a id="topic-05"></a>
## Topic 05 — Improved status bar

### 1. Topic and resulting behavior

The status bar exposes UTF-8/BOM, line endings, indentation, interpreter, and process activity beside the existing cursor and Git labels. Clickable values also accept keyboard activation.

### 2. Official documentation and code walkthrough

StatusItem delegates activation to one callback. Encoding and EOL changes mark serialization dirty; current_changed reads the selected editor so values do not leak from another tab. Process activity is a short status indication, not a multi-job dashboard.

- [Qt status bar](https://doc.qt.io/archives/qt-5.15/qstatusbar.html)
- [QScintilla overview](https://www.riverbankcomputing.com/software/qscintilla/intro)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `side_bar_widgets/status_item.py` | [`StatusItem`](#file-side-bar-widgets-status-item-py) |
| `main.py` | [`EditorFeatureController._install_status`](#controller) |
| `main.py` | [`EditorFeatureController.choose_encoding`](#controller) |
| `main.py` | [`EditorFeatureController.choose_line_ending`](#controller) |
| `main.py` | [`EditorFeatureController.choose_indentation`](#controller) |
| `main.py` | [`EditorFeatureController.current_changed`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `EditorFeatureController.choose_encoding` in `main.py`. **Contract:** Choose the UTF-8 BOM bit used by the existing atomic save path. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `main.py`. **Placement:** the complete `EditorFeatureController.choose_encoding` definition in its named owner. The [installation block](#controller) gives the exact file or baseline placement. This answer is already included there.

````python
    def choose_encoding(self) -> None:
        """Choose the UTF-8 BOM bit used by the existing atomic save path."""
        from PyQt5.QtWidgets import QInputDialog
        editor = self.window.current_editor()
        if editor is None:
            return
        choice, ok = QInputDialog.getItem(self.window, "Encoding", "Save as",
                                          ["UTF-8", "UTF-8 BOM"],
                                          1 if getattr(editor, "_utf8_bom", False) else 0, False)
        if ok:
            editor._utf8_bom = choice == "UTF-8 BOM"
            self.window._on_editor_text_changed(editor)
            self.current_changed(editor)
````

**Why this works:** StatusItem delegates activation to one callback. Encoding and EOL changes mark serialization dirty; current_changed reads the selected editor so values do not leak from another tab. Process activity is a short status indication, not a multi-job dashboard. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_05_status_keyboard` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Keyboard activation invokes the same setting as a pointer click.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_05_status_keyboard(app):
    """Keyboard activation invokes the same setting as a pointer click."""
    called = []
    item = StatusItem('UTF-8', lambda: called.append('encoding'))
    QTest.keyClick(item, Qt.Key_Return)
    QTest.mouseClick(item, Qt.LeftButton)
    assert called == ['encoding', 'encoding']
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_05_status_keyboard"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-side-bar-widgets-status-item-py"></a>
#### CREATE FILE — `side_bar_widgets/status_item.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `status_item.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Keyboard-accessible status bar settings.

### 7. Acceptance check

Use Tab and Enter on the settings values. Save a BOM/CRLF file and inspect its bytes; switch between Python and Markdown tabs.

---

<a id="topic-06"></a>
## Topic 06 — Polished empty states

### 1. Topic and resulting behavior

Empty panels display an explanation and an appropriate action instead of an unexplained blank area. Problems and References keep a latest snapshot and reveal an empty message when there are no rows.

### 2. Official documentation and code walkthrough

EmptyState is a reusable message/action widget. SnapshotDock owns a stack of a label and a tree, stores immutable row tuples, and rebuilds only when visible.

- [Qt stacked widgets](https://doc.qt.io/archives/qt-5.15/qstackedwidget.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `side_bar_widgets/empty_state.py` | [`EmptyState`](#file-side-bar-widgets-empty-state-py) |
| `side_bar_widgets/snapshot_dock.py` | [`SnapshotDock`](#file-side-bar-widgets-snapshot-dock-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `EmptyState` in `side_bar_widgets/empty_state.py`. **Contract:** Explain why a panel has no rows and provide a relevant next action. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `side_bar_widgets/empty_state.py`. **Placement:** the complete `EmptyState` definition in its named owner. The [installation block](#file-side-bar-widgets-empty-state-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** EmptyState is a reusable message/action widget. SnapshotDock owns a stack of a label and a tree, stores immutable row tuples, and rebuilds only when visible. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_06_empty_action` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** An empty-panel action is connected to a callable operation.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_06_empty_action(app):
    """An empty-panel action is connected to a callable operation."""
    called = []
    panel = EmptyState('No results', 'Open a project', 'Open', lambda: called.append(True))
    from PyQt5.QtWidgets import QPushButton
    panel.findChild(QPushButton).click()
    assert called == [True]
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_06_empty_action"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-side-bar-widgets-empty-state-py"></a>
#### CREATE FILE — `side_bar_widgets/empty_state.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `empty_state.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** A reusable explanation and action for an empty panel.

<a id="file-side-bar-widgets-snapshot-dock-py"></a>
#### CREATE FILE — `side_bar_widgets/snapshot_dock.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `snapshot_dock.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Deferred presentation for Problems and References while retaining latest data.

### 7. Acceptance check

Show an empty Problems panel, then generate a Ruff diagnostic and resolve it. The panel must return to its empty message.

---

<a id="topic-07"></a>
## Topic 07 — Welcome screen

### 1. Topic and resulting behavior

The welcome screen offers recent files, recent projects, Open actions, and built-in Python/Markdown/README templates. It appears when the tab collection is empty and opens templates as unsaved drafts.

### 2. Official documentation and code walkthrough

Welcome.refresh rebuilds recent items from current settings. create_template selects known starter text; open_draft uses the existing new-file lifecycle without assigning an overwrite destination.

- [Qt main-window center](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)
- [Qt stacked widgets](https://doc.qt.io/archives/qt-5.15/qstackedwidget.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `side_bar_widgets/welcome_screen.py` | [`Welcome`](#file-side-bar-widgets-welcome-screen-py) |
| `main.py` | [`EditorFeatureController._install_center`](#controller) |
| `main.py` | [`EditorFeatureController.show_empty`](#controller) |
| `main.py` | [`EditorFeatureController.create_template`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `EditorFeatureController.show_empty` in `main.py`. **Contract:** Show Welcome only when every split tab group is empty. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `main.py`. **Placement:** the complete `EditorFeatureController.show_empty` definition in its named owner. The [installation block](#controller) gives the exact file or baseline placement. This answer is already included there.

````python
    def show_empty(self) -> None:
        """Show Welcome only when every split tab group is empty."""
        empty = not list(self.window.tab_view.all_editors())
        if empty:
            self.welcome.refresh(self.window.recent_files, self.window.settings.value("recent_projects", [], type=list))
        self.stack.setCurrentWidget(self.welcome if empty else self.stack.widget(0))
        self.breadcrumb.setVisible(not empty)
````

**Why this works:** Welcome.refresh rebuilds recent items from current settings. create_template selects known starter text; open_draft uses the existing new-file lifecycle without assigning an overwrite destination. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_07_welcome_recent_file` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Recent-file buttons retain their own path rather than the loop's last path.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_07_welcome_recent_file(app, tmp_path):
    """Recent-file buttons retain their own path rather than the loop's last path."""
    opened = []
    page = Welcome([str(tmp_path / 'first.md'), str(tmp_path / 'second.md')],
                   lambda path=None: opened.append(path), lambda: None)
    from PyQt5.QtWidgets import QPushButton
    buttons = page.findChildren(QPushButton)
    buttons[2].click()
    buttons[3].click()
    assert opened == [tmp_path / 'first.md', tmp_path / 'second.md']
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_07_welcome_recent_file"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-side-bar-widgets-welcome-screen-py"></a>
#### CREATE FILE — `side_bar_widgets/welcome_screen.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `welcome_screen.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Recent files, recent projects and starter templates on the empty-workspace page.

### 7. Acceptance check

Close all tabs; reopen a recent project and create each template. Verify that creating a template never replaces an existing file.

---

<a id="topic-08"></a>
## Topic 08 — Focus mode

### 1. Topic and resulting behavior

Focus mode snapshots the current docks, splitter, sidebar, side panel, and menu visibility, then hides distractions. Exiting restores that snapshot rather than applying a canned arrangement.

### 2. Official documentation and code walkthrough

Layouts.focus stores state once. The registered view.focus QAction has an application shortcut, Ctrl+Shift+F11 by default, so it remains reachable while menus are hidden.

- [Qt saveState/restoreState](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)
- [Qt shortcuts](https://doc.qt.io/archives/qt-5.15/qshortcut.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_settings/workspace_layouts.py` | [`Layouts.focus`](#file-code-settings-workspace-layouts-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `Layouts.focus` in `code_settings/workspace_layouts.py`. **Contract:** Temporarily hide side panels and docks without overwriting a preset. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_settings/workspace_layouts.py`. **Placement:** the complete `Layouts.focus` definition in its named owner. The [installation block](#file-code-settings-workspace-layouts-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** Layouts.focus stores state once. The registered view.focus QAction has an application shortcut, Ctrl+Shift+F11 by default, so it remains reachable while menus are hidden. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_08_focus_restore` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Leaving focus restores the visible dock and consumes its snapshot.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_08_focus_restore(layout_window):
    """Leaving focus restores the visible dock and consumes its snapshot."""
    state = Layouts(layout_window)
    state.focus(True)
    assert layout_window.console_dock.isHidden()
    state.focus(False)
    assert not layout_window.console_dock.isHidden()
    assert state.before_focus is None
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_08_focus_restore"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-settings-workspace-layouts-py"></a>
#### CREATE FILE — `code_settings/workspace_layouts.py`

**Folder:** `code_settings/` already exists. Create **only** `workspace_layouts.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Named layout snapshots and reversible focus mode.

### 7. Acceptance check

Arrange multiple docks, enter focus mode, then use the shortcut to leave it. Check exact visibility and splitter restoration.

---

<a id="topic-09"></a>
## Topic 09 — Workspace layout presets

### 1. Topic and resulting behavior

Python Coding, Markdown Writing, and Git Review work immediately as built-in layouts. Named saved layouts retain QMainWindow state, geometry, splitter sizes, and central-panel visibility.

### 2. Official documentation and code walkthrough

Layouts.restore validates serialized values and rolls back when restoration fails. If a built-in name has no saved override, _builtin applies its documented arrangement. Stable dock object names are required.

- [Qt main-window state](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)
- [Qt settings](https://doc.qt.io/archives/qt-5.15/qsettings.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_settings/workspace_layouts.py` | [`Layouts`](#file-code-settings-workspace-layouts-py) |
| `main.py` | [`EditorFeatureController.save_layout`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `Layouts.restore` in `code_settings/workspace_layouts.py`. **Contract:** Restore saved geometry atomically, or apply one of three built-in layouts. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_settings/workspace_layouts.py`. **Placement:** the complete `Layouts.restore` definition in its named owner. The [installation block](#file-code-settings-workspace-layouts-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** Layouts.restore validates serialized values and rolls back when restoration fails. If a built-in name has no saved override, _builtin applies its documented arrangement. Stable dock object names are required. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_09_saved_layout` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** A missing preset preserves state; a named preset restores dock visibility.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_09_saved_layout(layout_window):
    """A missing preset preserves state; a named preset restores dock visibility."""
    state = Layouts(layout_window)
    assert not state.restore('Missing')
    state.save('Python Coding')
    layout_window.console_dock.hide()
    assert state.restore('Python Coding')
    assert not layout_window.console_dock.isHidden()
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_09_saved_layout"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

This topic shares the complete modules linked in the file table. Apply those files once, then its controller/MainWindow connections in Final integration.

### 7. Acceptance check

Try all three presets before saving anything. Save a custom name, move docks, and restore it. Corrupt a test settings value and verify failure does not leave a half-restored layout.

---

<a id="topic-10"></a>
## Topic 10 — Automatic recovery

### 1. Topic and resulting behavior

Automatic recovery saves dirty document snapshots to application data every five seconds. Recovery records retain identity and logical path, and reopening creates a draft so disk files are not silently overwritten.

### 2. Official documentation and code walkthrough

atomic_bytes writes beside the destination and replaces it atomically. RecoveryStore stores the snapshot and metadata; controller attach/flush/restore/discard hooks follow the existing document lifecycle.

- [Python tempfile](https://docs.python.org/3/library/tempfile.html)
- [Qt application data paths](https://doc.qt.io/archives/qt-5.15/qstandardpaths.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/document_recovery.py` | [`atomic_bytes`](#file-code-inteligence-document-recovery-py) |
| `code_inteligence/document_recovery.py` | [`RecoveryStore`](#file-code-inteligence-document-recovery-py) |
| `main.py` | [`EditorFeatureController.attach`](#controller) |
| `main.py` | [`EditorFeatureController.flush_recovery`](#controller) |
| `main.py` | [`EditorFeatureController.restore_recovery`](#controller) |
| `main.py` | [`EditorFeatureController.discarded`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `RecoveryStore` in `code_inteligence/document_recovery.py`. **Contract:** Keep dirty buffers apart from normal saved-tab session metadata. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/document_recovery.py`. **Placement:** the complete `RecoveryStore` definition in its named owner. The [installation block](#file-code-inteligence-document-recovery-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** atomic_bytes writes beside the destination and replaces it atomically. RecoveryStore stores the snapshot and metadata; controller attach/flush/restore/discard hooks follow the existing document lifecycle. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_10_recovery_copy` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** A recovery snapshot never overwrites the associated saved document.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_10_recovery_copy(tmp_path):
    """A recovery snapshot never overwrites the associated saved document."""
    document = tmp_path / 'saved.md'
    document.write_text('disk', encoding='utf-8')
    store = RecoveryStore(tmp_path / 'recovery')
    store.write('stable-id', document, 'unsaved 😀')
    assert store.pending()[0]['text'] == 'unsaved 😀'
    assert document.read_text(encoding='utf-8') == 'disk'
    store.forget('stable-id')
    assert store.pending() == []
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_10_recovery_copy"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-document-recovery-py"></a>
#### CREATE FILE — `code_inteligence/document_recovery.py`

**Folder:** `code_inteligence/` already exists. Create **only** `document_recovery.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Atomic dirty-buffer snapshots separate from saved-file sessions.

### 7. Acceptance check

Edit a saved file and an untitled tab, wait for a snapshot, and restart after a forced exit in a disposable workspace. Restore and explicitly save the drafts.

---

<a id="topic-11"></a>
## Topic 11 — Local file history

### 1. Topic and resulting behavior

Local history retains earlier saved file bytes with bounded per-file retention. The history browser lists retained timestamps and sizes, lets you compare any selected version, and opens an accepted version as a new draft.

### 2. Official documentation and code walkthrough

VersionStore keys storage by resolved path and prunes older entries. saved records previous disk bytes; HistoryDialog returns a selected snapshot; browse_history feeds ComparisonDialog.

- [Python pathlib](https://docs.python.org/3/library/pathlib.html)
- [Python os.replace](https://docs.python.org/3/library/os.html#os.replace)
- [Qt list widgets](https://doc.qt.io/archives/qt-5.15/qlistwidget.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/local_history.py` | [`VersionStore`](#file-code-inteligence-local-history-py) |
| `main.py` | [`EditorFeatureController.saved`](#controller) |
| `main.py` | [`EditorFeatureController.browse_history`](#controller) |
| `side_bar_widgets/history_dialog.py` | [`HistoryDialog`](#file-side-bar-widgets-history-dialog-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `VersionStore` in `code_inteligence/local_history.py`. **Contract:** Bounded content-addressed history outside the working tree. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/local_history.py`. **Placement:** the complete `VersionStore` definition in its named owner. The [installation block](#file-code-inteligence-local-history-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** VersionStore keys storage by resolved path and prunes older entries. saved records previous disk bytes; HistoryDialog returns a selected snapshot; browse_history feeds ComparisonDialog. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_11_history_retention` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** History bounds versions for one path and retains the newest predecessor.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_11_history_retention(tmp_path):
    """History bounds versions for one path and retains the newest predecessor."""
    history = VersionStore(tmp_path / 'history', keep=2)
    document = tmp_path / 'saved.md'
    for value in (b'one', b'two', b'three'):
        history.record(document, value)
    versions = history.versions(document)
    assert len(versions) == 2
    assert versions[0].read_bytes() == b'three'
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_11_history_retention"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-local-history-py"></a>
#### CREATE FILE — `code_inteligence/local_history.py`

**Folder:** `code_inteligence/` already exists. Create **only** `local_history.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Bounded predecessor snapshots of successfully saved documents.

<a id="file-side-bar-widgets-history-dialog-py"></a>
#### CREATE FILE — `side_bar_widgets/history_dialog.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `history_dialog.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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
````

**File responsibility:** Browse every retained local version without overwriting a document.

### 7. Acceptance check

Save three distinct versions, select the oldest retained version, compare, and open its draft. Confirm the working file remains at the latest saved revision.

---

<a id="topic-12"></a>
## Topic 12 — External-change comparison

### 1. Topic and resulting behavior

External edits are detected through filesystem hints followed by background content hashing. Saving a changed file offers reload, keep-buffer, or a three-way merge draft based on the last known disk text.

### 2. Official documentation and code walkthrough

The editor retains _disk_text as the common ancestor. three_way combines nonoverlapping line edits and marks overlapping alternatives. A merge opens a new tab; the user reviews conflicts before choosing where to save.

- [Python hashlib](https://docs.python.org/3/library/hashlib.html)
- [Qt message boxes](https://doc.qt.io/archives/qt-5.15/qmessagebox.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/text_comparison.py` | [`three_way`](#file-code-inteligence-text-comparison-py) |
| `main.py` | [`EditorFeatureController.external_conflict`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `EditorFeatureController.external_conflict` in `main.py`. **Contract:** Offer reload, keep, or an explicit conflict-marker merge draft. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `main.py`. **Placement:** the complete `EditorFeatureController.external_conflict` definition in its named owner. The [installation block](#controller) gives the exact file or baseline placement. This answer is already included there.

````python
    def external_conflict(self, editor, raw: bytes) -> str:
        """Offer reload, keep, or an explicit conflict-marker merge draft."""
        disk = raw.decode("utf-8-sig")
        dialog = QMessageBox(self.window)
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
            self.window.mark_editor_clean(editor)
            return "cancel-save"
        if chosen is keep:
            return "overwrite"
        if chosen is merge:
            # Without a stored common ancestor, never claim a clean merge.
            result, _conflict = three_way(getattr(editor, "_disk_text", ""), editor.text(), disk)
            previous_mode = self.window.python_editor_active
            self.window.python_editor_active = isinstance(editor, PythonEditor)
            try:
                draft = self.window.new_file()
            finally:
                self.window.python_editor_active = previous_mode
            draft.setText(result)
        return "cancel-save"
````

**Why this works:** The editor retains _disk_text as the common ancestor. three_way combines nonoverlapping line edits and marks overlapping alternatives. A merge opens a new tab; the user reviews conflicts before choosing where to save. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_12_conflict_preserves_both` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** A divergent edit is visible; trivial agreement needs no conflict markers.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_12_conflict_preserves_both():
    """A divergent edit is visible; trivial agreement needs no conflict markers."""
    assert three_way('base', 'same', 'same') == ('same', False)
    merged, conflict = three_way('base', 'editor text', 'disk text')
    assert conflict
    assert 'editor text' in merged and 'disk text' in merged
    assert '<<<<<<< EDITOR' in merged
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_12_conflict_preserves_both"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-text-comparison-py"></a>
#### CREATE FILE — `code_inteligence/text_comparison.py`

**Folder:** `code_inteligence/` already exists. Create **only** `text_comparison.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Read-only text differences and explicit merge drafts.

### 7. Acceptance check

Change different lines in the editor and on disk, then merge. Repeat with the same line and confirm both alternatives appear inside conflict markers.

---

<a id="topic-13"></a>
## Topic 13 — Compare/diff editor

### 1. Topic and resulting behavior

Read-only side-by-side comparison supports buffer versus disk, two selected files, Git HEAD versus buffer, and historical versions. Changed lines are highlighted and scroll positions are synchronized proportionally.

### 2. Official documentation and code walkthrough

ComparisonDialog owns two read-only panes. compare returns explicit acceptance; callers open the right-hand side as a draft. Rename uses the same review surface with an Apply rename button and its separate revision checks.

- [Python difflib](https://docs.python.org/3/library/difflib.html)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)
- [Qt plain-text editor](https://doc.qt.io/archives/qt-5.15/qplaintextedit.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/text_comparison.py` | [`unified_diff`](#file-code-inteligence-text-comparison-py) |
| `main.py` | [`EditorFeatureController.compare`](#controller) |
| `main.py` | [`EditorFeatureController.compare_disk`](#controller) |
| `main.py` | [`EditorFeatureController.compare_files`](#controller) |
| `main.py` | [`EditorFeatureController.compare_git_head`](#controller) |
| `side_bar_widgets/comparison_dialog.py` | [`ComparisonDialog`](#file-side-bar-widgets-comparison-dialog-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `unified_diff` in `code_inteligence/text_comparison.py`. **Contract:** Return a readable diff with stable source labels. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/text_comparison.py`. **Placement:** the complete `unified_diff` definition in its named owner. The [installation block](#file-code-inteligence-text-comparison-py) gives the exact file or baseline placement. This answer is already included there.

````python
def unified_diff(before: str, after: str, left: str, right: str) -> str:
    """Return a readable diff with stable source labels."""
    return "".join(difflib.unified_diff(before.splitlines(keepends=True),
                                        after.splitlines(keepends=True),
                                        fromfile=left, tofile=right))
````

**Why this works:** ComparisonDialog owns two read-only panes. compare returns explicit acceptance; callers open the right-hand side as a draft. Rename uses the same review surface with an Apply rename button and its separate revision checks. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_13_comparison_read_only` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** A diff labels both snapshots and returns no output for equal content.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_13_comparison_read_only():
    """A diff labels both snapshots and returns no output for equal content."""
    before, after = 'one\n', 'two\n'
    result = unified_diff(before, after, 'disk', 'buffer')
    assert '--- disk' in result and '+++ buffer' in result
    assert '-one' in result and '+two' in result
    assert unified_diff(before, before, 'disk', 'buffer') == ''
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_13_comparison_read_only"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-side-bar-widgets-comparison-dialog-py"></a>
#### CREATE FILE — `side_bar_widgets/comparison_dialog.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `comparison_dialog.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Side-by-side immutable comparisons used by history, disk and rename previews.

### 7. Acceptance check

Compare unequal-length files, scroll both panes, cancel, then choose Open draft. Verify the right-hand text opens in a separate unsaved tab.

---

<a id="topic-14"></a>
## Topic 14 — Rename symbol with preview

### 1. Topic and resulting behavior

Python rename runs Jedi in the shared analysis queue, previews every affected file, and applies only an explicitly accepted, still-current plan. Identifier validation rejects keywords; writes preserve source encoding, BOM, line endings, and permission mode.

### 2. Official documentation and code walkthrough

plan_rename captures original bytes and rejects file moves/outside-workspace targets. _rename_ready rejects dirty buffers before and after review. apply_rename rechecks every file before writing and attempts rollback on an I/O failure.

- [Jedi rename API](https://jedi.readthedocs.io/en/latest/docs/api.html)
- [Jedi refactoring objects](https://jedi.readthedocs.io/en/latest/docs/api-classes.html)
- [Python encoding detection](https://docs.python.org/3/library/tokenize.html#tokenize.detect_encoding)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/symbol_rename.py` | [`FileEdit`](#file-code-inteligence-symbol-rename-py) |
| `code_inteligence/symbol_rename.py` | [`plan_rename`](#file-code-inteligence-symbol-rename-py) |
| `code_inteligence/symbol_rename.py` | [`rename_preview`](#file-code-inteligence-symbol-rename-py) |
| `code_inteligence/symbol_rename.py` | [`apply_rename`](#file-code-inteligence-symbol-rename-py) |
| `main.py` | [`EditorFeatureController.rename_symbol`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `apply_rename` in `code_inteligence/symbol_rename.py`. **Contract:** Check every original revision before applying the approved edit set. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/symbol_rename.py`. **Placement:** the complete `apply_rename` definition in its named owner. The [installation block](#file-code-inteligence-symbol-rename-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** plan_rename captures original bytes and rejects file moves/outside-workspace targets. _rename_ready rejects dirty buffers before and after review. apply_rename rechecks every file before writing and attempts rollback on an I/O failure. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_14_jedi_rename_and_stale_preview` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Use real Jedi semantics, then reject a disk edit made after preview.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_14_jedi_rename_and_stale_preview(tmp_path):
    """Use real Jedi semantics, then reject a disk edit made after preview."""
    document = tmp_path / 'example.py'
    source = 'def old_name():\n    return 1\n\nold_name()\n'
    document.write_text(source, encoding='utf-8')
    edits = plan_rename(tmp_path, document, source, 0, 5, 'new_name')
    assert b'new_name()' in edits[0].after
    document.write_text(source + '# external change\n', encoding='utf-8')
    with pytest.raises(RuntimeError):
        apply_rename(edits)
    assert document.read_text(encoding='utf-8').endswith('# external change\n')
    document.write_text(source, encoding='utf-8')
    apply_rename(edits)
    assert 'old_name' not in document.read_text(encoding='utf-8')
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_14_jedi_rename_and_stale_preview"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-symbol-rename-py"></a>
#### CREATE FILE — `code_inteligence/symbol_rename.py`

**Folder:** `code_inteligence/` already exists. Create **only** `symbol_rename.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Preview and revision-checked application of Jedi rename edits.

### 7. Acceptance check

Rename a cross-file symbol. Change a target after generating its preview and confirm Apply refuses the stale plan. Test a UTF-8 BOM/CRLF file.

---

<a id="topic-15"></a>
## Topic 15 — Workspace symbol search

### 1. Topic and resulting behavior

Workspace search scans Python definitions under the actual workspace root, skips excluded directories, tolerates invalid files, and navigates to a selected definition.

### 2. Official documentation and code walkthrough

workspace_symbols returns plain immutable symbol records. The controller submits the scan with interpreter/workspace identity to the same owned analysis queue used by Python providers.

- [Python AST](https://docs.python.org/3/library/ast.html)
- [Python os.walk](https://docs.python.org/3/library/os.html#os.walk)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/symbol_index.py` | [`workspace_symbols`](#file-code-inteligence-symbol-index-py) |
| `code_inteligence/analysis_cache.py` | [`RequestKey`](#file-code-inteligence-analysis-cache-py) |
| `main.py` | [`EditorFeatureController.find_symbol`](#controller) |
| `main.py` | [`EditorFeatureController._analysis_ready`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `workspace_symbols` in `code_inteligence/symbol_index.py`. **Contract:** Build a bounded index, skipping virtualenvs and unreadable files. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/symbol_index.py`. **Placement:** the complete `workspace_symbols` definition in its named owner. The [installation block](#file-code-inteligence-symbol-index-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** workspace_symbols returns plain immutable symbol records. The controller submits the scan with interpreter/workspace identity to the same owned analysis queue used by Python providers. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_15_workspace_tolerates_broken_file` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** One invalid file must not hide definitions from other Python files.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_15_workspace_tolerates_broken_file(tmp_path):
    """One invalid file must not hide definitions from other Python files."""
    (tmp_path / 'bad.py').write_text('def broken(', encoding='utf-8')
    (tmp_path / 'good.py').write_text('class Present:\n    pass\n', encoding='utf-8')
    assert [item.name for item in workspace_symbols(tmp_path)] == ['Present']
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_15_workspace_tolerates_broken_file"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

This topic shares the complete modules linked in the file table. Apply those files once, then its controller/MainWindow connections in Final integration.

### 7. Acceptance check

Search a project containing one malformed Python file; valid definitions should remain searchable and open at their declaration lines.

---

<a id="topic-16"></a>
## Topic 16 — Test runner panel

### 1. Topic and resulting behavior

The Tests dock collects exact pytest node IDs, groups them by file, runs the workspace or selected cases, retains failed IDs for rerun, shows structured results and text output, and offers Stop. It owns a process separate from Run File and run profiles.

### 2. Official documentation and code walkthrough

pytest_bridge emits JSONL through pytest hooks to a private event file. TestSession incrementally reads whole records, including parameter IDs and setup/call/teardown outcomes. Switching environments stops the old session and rejects its pending structured records.

- [Qt QProcess](https://doc.qt.io/archives/qt-5.15/qprocess.html)
- [pytest usage](https://docs.pytest.org/en/stable/how-to/usage.html)
- [pytest hooks and reports](https://docs.pytest.org/en/stable/reference/reference.html)
- [Writing pytest plugins](https://docs.pytest.org/en/stable/how-to/writing_plugins.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `python_editor/test_panel.py` | [`OutputView`](#file-python-editor-test-panel-py) |
| `python_editor/test_panel.py` | [`TestDock`](#file-python-editor-test-panel-py) |
| `python_editor/run_configurations.py` | [`ProcessPanel`](#file-python-editor-run-configurations-py) |
| `main.py` | [`EditorFeatureController.run_tests`](#controller) |
| `main.py` | [`EditorFeatureController._make_tests`](#controller) |
| `python_editor/test_session.py` | [`TestSession`](#file-python-editor-test-session-py) |
| `python_editor/pytest_bridge.py` | [`Reporter`](#file-python-editor-pytest-bridge-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `TestSession.start` in `python_editor/test_session.py`. **Contract:** Run exact node IDs, or collect them, without converting them to shell text. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `python_editor/test_session.py`. **Placement:** the complete `TestSession.start` definition in its named owner. The [installation block](#file-python-editor-test-session-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** pytest_bridge emits JSONL through pytest hooks to a private event file. TestSession incrementally reads whole records, including parameter IDs and setup/call/teardown outcomes. Switching environments stops the old session and rejects its pending structured records. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_16_process_streams_utf8` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Run a real child process through QProcess and receive its final output.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_16_process_streams_utf8(app, tmp_path):
    """Run a real child process through QProcess and receive its final output."""
    script = tmp_path / 'child.py'
    script.write_text('print("ready 😀")\n', encoding='utf-8')
    runner = ProcessPanel()
    output, exits = [], []
    runner.output.connect(output.append)
    runner.finished.connect(exits.append)
    runner.run(RunConfig('test', sys.executable, str(script), str(tmp_path), [],
                         {'PYTHONIOENCODING': 'utf-8'}))
    wait_until(app, lambda: bool(exits))
    assert exits == [0]
    assert 'ready 😀' in ''.join(output)
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_16_process_streams_utf8"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-python-editor-test-panel-py"></a>
#### CREATE FILE — `python_editor/test_panel.py`

**Folder:** `python_editor/` already exists. Create **only** `test_panel.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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
````

**File responsibility:** A separate test-output dock with traceback navigation.

<a id="file-python-editor-test-session-py"></a>
#### CREATE FILE — `python_editor/test_session.py`

**Folder:** `python_editor/` already exists. Create **only** `test_session.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Separate pytest process and incremental structured-event reader.

<a id="file-python-editor-pytest-bridge-py"></a>
#### CREATE FILE — `python_editor/pytest_bridge.py`

**Folder:** `python_editor/` already exists. Create **only** `pytest_bridge.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Run pytest in its selected interpreter and write structured events separately.

### 7. Acceptance check

Collect parameterized cases, run one failing case, rerun failed, then stop a long test. Trigger an import error and check collection-error reporting.

---

<a id="topic-17"></a>
## Topic 17 — Run configurations

### 1. Topic and resulting behavior

Named run configurations persist explicit interpreter, script, working directory, argument list, and environment overrides. A separate lazily created output dock displays streamed output, exit status, and Stop.

### 2. Official documentation and code walkthrough

RunConfigDialog parses JSON argument/environment fields. ProcessPanel validates fields, passes an argument vector directly to QProcess, and handles failed startup. Stop terminates then uses a generation-guarded delayed kill.

- [Qt process environment](https://doc.qt.io/archives/qt-5.15/qprocessenvironment.html)
- [Python JSON](https://docs.python.org/3/library/json.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `python_editor/run_configurations.py` | [`RunConfig`](#file-python-editor-run-configurations-py) |
| `python_editor/run_configurations.py` | [`load_configs`](#file-python-editor-run-configurations-py) |
| `python_editor/run_configurations.py` | [`save_configs`](#file-python-editor-run-configurations-py) |
| `python_editor/run_configurations.py` | [`RunConfigDialog`](#file-python-editor-run-configurations-py) |
| `main.py` | [`EditorFeatureController.run_configuration`](#controller) |
| `python_editor/run_output.py` | [`RunOutputDock`](#file-python-editor-run-output-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `RunConfigDialog.value` in `python_editor/run_configurations.py`. **Contract:** Parse arguments and environment, raising before any process starts. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `python_editor/run_configurations.py`. **Placement:** the complete `RunConfigDialog.value` definition in its named owner. The [installation block](#file-python-editor-run-configurations-py) gives the exact file or baseline placement. This answer is already included there.

````python
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

**Why this works:** RunConfigDialog parses JSON argument/environment fields. ProcessPanel validates fields, passes an argument vector directly to QProcess, and handles failed startup. Stop terminates then uses a generation-guarded delayed kill. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_17_run_dialog_validates_data` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Arguments stay a list; environment values must be strings.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_17_run_dialog_validates_data(app, tmp_path):
    """Arguments stay a list; environment values must be strings."""
    config = RunConfig('example', sys.executable, 'a.py', str(tmp_path), ['two words'], {})
    dialog = RunConfigDialog(config)
    assert dialog.value().arguments == ['two words']
    dialog.fields['env'].setText('{"COUNT": 3}')
    with pytest.raises(ValueError):
        dialog.value()
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_17_run_dialog_validates_data"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-python-editor-run-configurations-py"></a>
#### CREATE FILE — `python_editor/run_configurations.py`

**Folder:** `python_editor/` already exists. Create **only** `run_configurations.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Named process settings and argument-vector execution.

<a id="file-python-editor-run-output-py"></a>
#### CREATE FILE — `python_editor/run_output.py`

**Folder:** `python_editor/` already exists. Create **only** `run_output.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

    def completed(self, code):
        """Display the exit status and disable Stop after process completion."""
        self.append(f"\nProcess exited with code {code}\n")
        self.stop.setEnabled(False)
````

**File responsibility:** Lazy, read-only output for named run configurations.

### 7. Acceptance check

Run a script whose path contains spaces with a Unicode argument and an environment override. Check output, exit code, invalid configuration rejection, and Stop.

---

<a id="topic-18"></a>
## Topic 18 — Configurable keyboard shortcuts

### 1. Topic and resulting behavior

The shortcut editor lists stable command IDs and changes the existing QAction bindings. Core editor actions and new feature actions share one registry, including the focus-mode escape action.

### 2. Official documentation and code walkthrough

Shortcuts.bind validates the complete requested map before changing any QAction. ShortcutDialog offers an editable command selector with completion and stores overrides in QSettings.

- [Qt QAction](https://doc.qt.io/archives/qt-5.15/qaction.html)
- [Qt QKeySequence](https://doc.qt.io/archives/qt-5.15/qkeysequence.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_settings/keyboard_shortcuts.py` | [`Shortcuts`](#file-code-settings-keyboard-shortcuts-py) |
| `code_settings/keyboard_shortcuts.py` | [`ShortcutDialog`](#file-code-settings-keyboard-shortcuts-py) |
| `main.py` | [`EditorFeatureController.edit_shortcuts`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `Shortcuts.bind` in `code_settings/keyboard_shortcuts.py`. **Contract:** Validate every binding before mutating any action. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_settings/keyboard_shortcuts.py`. **Placement:** the complete `Shortcuts.bind` definition in its named owner. The [installation block](#file-code-settings-keyboard-shortcuts-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** Shortcuts.bind validates the complete requested map before changing any QAction. ShortcutDialog offers an editable command selector with completion and stores overrides in QSettings. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_18_shortcut_conflict_is_atomic` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Reject duplicates before changing either original QAction shortcut.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_18_shortcut_conflict_is_atomic(app, tmp_path):
    """Reject duplicates before changing either original QAction shortcut."""
    settings = QSettings(str(tmp_path / 'keys.ini'), QSettings.IniFormat)
    save, open_file = QAction('Save'), QAction('Open')
    save.setShortcut('Ctrl+S')
    open_file.setShortcut('Ctrl+O')
    with pytest.raises(ValueError):
        Shortcuts(settings).bind({'save': save, 'open': open_file}, {'open': 'Ctrl+S'})
    assert open_file.shortcut().toString() == 'Ctrl+O'
    assert save.shortcut().toString() == 'Ctrl+S'
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_18_shortcut_conflict_is_atomic"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-settings-keyboard-shortcuts-py"></a>
#### CREATE FILE — `code_settings/keyboard_shortcuts.py`

**Folder:** `code_settings/` already exists. Create **only** `keyboard_shortcuts.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Shortcut validation and editing for existing QAction objects.

### 7. Acceptance check

Assign a new binding, restart, and invoke it. Attempt a collision with Save and confirm neither action changes.

---

<a id="topic-19"></a>
## Topic 19 — Smarter pair handling

### 1. Topic and resulting behavior

Pair handling wraps selections, inserts matching delimiters, skips an existing closer, and deletes an empty pair as one undo action. Context guards avoid unwanted quote insertion inside Python strings/comments, escaped quotes, and apostrophes in words.

### 2. Official documentation and code walkthrough

The helpers convert QScintilla UTF-8 positions carefully. pairing_allowed uses the production Python scanner for context; each editor calls the helpers before its normal key behavior.

- [QScintilla overview](https://www.riverbankcomputing.com/software/qscintilla/intro)
- [Python Unicode encodings](https://docs.python.org/3/howto/unicode.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/pair_handling.py` | [`PAIRS`](#file-code-inteligence-pair-handling-py) |
| `code_inteligence/pair_handling.py` | [`pair_key`](#file-code-inteligence-pair-handling-py) |
| `code_inteligence/pair_handling.py` | [`empty_pair_backspace`](#file-code-inteligence-pair-handling-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `empty_pair_backspace` in `code_inteligence/pair_handling.py`. **Contract:** Delete both adjacent pair characters on Backspace, keeping one undo. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/pair_handling.py`. **Placement:** the complete `empty_pair_backspace` definition in its named owner. The [installation block](#file-code-inteligence-pair-handling-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** The helpers convert QScintilla UTF-8 positions carefully. pairing_allowed uses the production Python scanner for context; each editor calls the helpers before its normal key behavior. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_19_pairs_after_unicode` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Use real QScintilla indices after an emoji, then undo a paired deletion.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_19_pairs_after_unicode(app):
    """Use real QScintilla indices after an emoji, then undo a paired deletion."""
    editor = QsciScintilla()
    editor.setUtf8(True)
    editor.setText('😀')
    editor.setCursorPosition(0, 1)
    assert pair_key(editor, '(')
    assert editor.text() == '😀()'
    assert empty_pair_backspace(editor)
    assert editor.text() == '😀'
    editor.undo()
    assert editor.text() == '😀()'
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_19_pairs_after_unicode"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-pair-handling-py"></a>
#### CREATE FILE — `code_inteligence/pair_handling.py`

**Folder:** `code_inteligence/` already exists. Create **only** `pair_handling.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Undoable bracket and quote handling shared by both editors.

### 7. Acceptance check

Type pairs after emoji and non-ASCII text. Test selections, backspace, comments, string escapes, and undo.

---

<a id="topic-20"></a>
## Topic 20 — Outline and navigation

### 1. Topic and resulting behavior

Python scope navigation and Markdown outline navigation use source-aware records. Markdown headings follow the actual Python-Markdown dialect, including setext headings and duplicate anchors such as setup_1. TOC and heading links reuse those records.

### 2. Official documentation and code walkthrough

document_model marks an analysis copy, removes markers before TOC assigns IDs, and collects final heading anchors after parsing. MarkdownOutline navigates by source line; the sanitized preview preserves heading id attributes.

- [Python regular expressions](https://docs.python.org/3/library/re.html)
- [Qt tree widget](https://doc.qt.io/archives/qt-5.15/qtreewidget.html)
- [Python-Markdown TOC and IDs](https://python-markdown.github.io/extensions/toc/)
- [Python-Markdown extension API](https://python-markdown.github.io/extensions/api/)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `markdown_editor/heading_navigation.py` | [`Heading`](#file-markdown-editor-document-model-py) |
| `markdown_editor/heading_navigation.py` | [`markdown_headings`](#file-markdown-editor-heading-navigation-py) |
| `side_bar_widgets/markdown_outline.py` | [`MarkdownOutline`](#file-side-bar-widgets-markdown-outline-py) |
| `markdown_editor/heading_navigation.py` | [`heading_link`](#file-markdown-editor-heading-navigation-py) |
| `markdown_editor/heading_navigation.py` | [`toc`](#file-markdown-editor-heading-navigation-py) |
| `main.py` | [`EditorFeatureController.insert_toc`](#controller) |
| `markdown_editor/document_model.py` | [`parse_headings`](#file-markdown-editor-document-model-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `markdown_headings` in `markdown_editor/heading_navigation.py`. **Contract:** Return real rendered ATX/setext headings with zero-based source positions. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `markdown_editor/heading_navigation.py`. **Placement:** the complete `markdown_headings` definition in its named owner. The [installation block](#file-markdown-editor-heading-navigation-py) gives the exact file or baseline placement. This answer is already included there.

````python
def markdown_headings(text: str) -> list[Heading]:
    """Return real rendered ATX/setext headings with zero-based source positions."""
    return parse_headings(text)
````

**Why this works:** document_model marks an analysis copy, removes markers before TOC assigns IDs, and collects final heading anchors after parsing. MarkdownOutline navigates by source line; the sanitized preview preserves heading id attributes. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_20_markdown_fences_and_duplicates` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Code fences suppress headings and repeated titles get distinct anchors.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_20_markdown_fences_and_duplicates():
    """Code fences suppress headings and repeated titles get distinct anchors."""
    source = '# Setup\n```python\n# hidden\n```\n# Setup\n'
    assert [item.slug for item in markdown_headings(source)] == ['setup', 'setup_1']
    assert '(#setup_1)' in toc(source)
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_20_markdown_fences_and_duplicates"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-markdown-editor-document-model-py"></a>
#### CREATE FILE — `markdown_editor/document_model.py`

**Folder:** `markdown_editor/` already exists. Create **only** `document_model.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Use the application's actual Python-Markdown dialect for headings and links.

<a id="file-markdown-editor-heading-navigation-py"></a>
#### CREATE FILE — `markdown_editor/heading_navigation.py`

**Folder:** `markdown_editor/` already exists. Create **only** `heading_navigation.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Heading navigation and TOCs using the same anchors as the actual preview.

<a id="file-side-bar-widgets-markdown-outline-py"></a>
#### CREATE FILE — `side_bar_widgets/markdown_outline.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `markdown_outline.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** A heading tree beside the existing Python outline.

### 7. Acceptance check

Test duplicate headings, setext headings, fenced examples, and inline formatting. Compare generated links with the actual preview anchors.

---

<a id="topic-21"></a>
## Topic 21 — Authoring tools

### 1. Topic and resulting behavior

Markdown authoring adds validated table rows, relative links, image links, heading links, and a local-link check. Link checking inspects rendered destinations, so reference-style links follow the same parser as preview.

### 2. Official documentation and code walkthrough

table escapes cell content; relative_link URL-encodes relative paths; broken_local_links distinguishes external URLs from filesystem paths and validates fragments in linked Markdown documents. Ambiguous reference destinations are reported by URL without inventing a source line.

- [Python urllib.parse](https://docs.python.org/3/library/urllib.parse.html)
- [Python os.path](https://docs.python.org/3/library/os.path.html)
- [Python-Markdown reference](https://python-markdown.github.io/reference/)
- [HTMLParser](https://docs.python.org/3/library/html.parser.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `markdown_editor/authoring_tools.py` | [`table`](#file-markdown-editor-authoring-tools-py) |
| `markdown_editor/authoring_tools.py` | [`relative_link`](#file-markdown-editor-authoring-tools-py) |
| `markdown_editor/authoring_tools.py` | [`broken_local_links`](#file-markdown-editor-authoring-tools-py) |
| `main.py` | [`EditorFeatureController.insert_table`](#controller) |
| `main.py` | [`EditorFeatureController.insert_link`](#controller) |
| `main.py` | [`EditorFeatureController.check_links`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `relative_link` in `markdown_editor/authoring_tools.py`. **Contract:** Create a portable, URL-escaped Markdown link relative to a document. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `markdown_editor/authoring_tools.py`. **Placement:** the complete `relative_link` definition in its named owner. The [installation block](#file-markdown-editor-authoring-tools-py) gives the exact file or baseline placement. This answer is already included there.

````python
def relative_link(document: Path, target: Path, *, image: bool = False, alt: str = "") -> str:
    """Create a portable, URL-escaped Markdown link relative to a document."""
    from urllib.parse import quote
    # Markdown moves with the document; cwd may be another folder entirely.
    relative = os.path.relpath(target.resolve(), document.resolve().parent)
    url = quote(Path(relative).as_posix(), safe="/.-_~")
    label = (alt or target.stem).replace("[", r"\[").replace("]", r"\]")
    return f"{'!' if image else ''}[{label}]({url})"
````

**Why this works:** table escapes cell content; relative_link URL-encodes relative paths; broken_local_links distinguishes external URLs from filesystem paths and validates fragments in linked Markdown documents. Ambiguous reference destinations are reported by URL without inventing a source line. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_21_table_and_relative_link` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Escaped pipes keep table columns stable and spaces survive URL encoding.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_21_table_and_relative_link(tmp_path):
    """Escaped pipes keep table columns stable and spaces survive URL encoding."""
    assert r'a\|b' in table([['a|b'], ['cell']])
    with pytest.raises(ValueError):
        table([['one'], ['one', 'two']])
    image = tmp_path / 'screen shot.png'
    image.write_bytes(b'example')
    source = tmp_path / 'note.md'
    link = relative_link(source, image, image=True)
    assert 'screen%20shot.png' in link
    assert broken_local_links(source, link) == []
    assert broken_local_links(source, '[empty]()') == []
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_21_table_and_relative_link"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-markdown-editor-authoring-tools-py"></a>
#### CREATE FILE — `markdown_editor/authoring_tools.py`

**Folder:** `markdown_editor/` already exists. Create **only** `authoring_tools.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Markdown table and relative-link helpers.

### 7. Acceptance check

Insert a table containing pipe characters and link to a filename with spaces. Check a reference-style link and a missing Markdown fragment.

---

<a id="topic-22"></a>
## Topic 22 — Performance diagnostics mode

### 1. Topic and resulting behavior

Performance diagnostics are opt-in and store bounded in-memory samples for startup, preview conversion/delivery, lexer work, and shared analysis requests. The timings view summarizes count and durations without recording source text.

### 2. Official documentation and code walkthrough

Timings.observe discards samples when disabled and uses a capped deque when enabled. Analysis timing includes time waiting in the single worker queue; preview delivery timing is the JavaScript callback latency, not a GPU paint measurement.

- [Python time.perf_counter](https://docs.python.org/3/library/time.html#time.perf_counter)
- [Qt QWebEnginePage](https://doc.qt.io/archives/qt-5.15/qwebenginepage.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_settings/performance_diagnostics.py` | [`Timings`](#file-code-settings-performance-diagnostics-py) |
| `main.py` | [`EditorFeatureController.show_timings`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `Timings.observe` in `code_settings/performance_diagnostics.py`. **Contract:** Record elapsed milliseconds for startup, preview and analysis. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_settings/performance_diagnostics.py`. **Placement:** the complete `Timings.observe` definition in its named owner. The [installation block](#file-code-settings-performance-diagnostics-py) gives the exact file or baseline placement. This answer is already included there.

````python
    def observe(self, name: str, elapsed: float) -> None:
        """Record elapsed milliseconds for startup, preview and analysis."""
        if not self.enabled:
            return
        # perf_counter() reports seconds; users inspect milliseconds here.
        values = self.samples.setdefault(name, [])
        values.append(elapsed * 1000)
        del values[:-self.limit]
````

**Why this works:** Timings.observe discards samples when disabled and uses a capped deque when enabled. Analysis timing includes time waiting in the single worker queue; preview delivery timing is the JavaScript callback latency, not a GPU paint measurement. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_22_timing_bound` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** The latest two samples determine a summary after the older slow sample expires.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_22_timing_bound():
    """The latest two samples determine a summary after the older slow sample expires."""
    timings = Timings(limit=2)
    for seconds in (0.100, 0.003, 0.005):
        timings.observe('preview', seconds)
    assert timings.summary()['preview'] == (2, 5.0)
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_22_timing_bound"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-settings-performance-diagnostics-py"></a>
#### CREATE FILE — `code_settings/performance_diagnostics.py`

**Folder:** `code_settings/` already exists. Create **only** `performance_diagnostics.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Bounded elapsed-time samples for measured operations.

### 7. Acceptance check

Enable diagnostics, edit Python and Markdown, then inspect the sample groups. Disable it and confirm counts stop growing.

---

<a id="topic-23"></a>
## Topic 23 — Lazy initialization

### 1. Topic and resulting behavior

Tests, run-profile output, terminal, and console bodies are created on first use. Terminal and console retain cheap named dock shells so layout restoration still has stable dock identities.

### 2. Official documentation and code walkthrough

LazyWidget memoizes a factory result. DeferredDock.ensure creates the body exactly once; showEvent invokes ensure before display. The existing Ruff client still starts with MainWindow; this chapter defers the listed widgets and terminal process.

- [Qt dock widgets](https://doc.qt.io/archives/qt-5.15/qdockwidget.html)
- [Qt main-window restoreDockWidget](https://doc.qt.io/archives/qt-5.15/qmainwindow.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `side_bar_widgets/lazy_panel.py` | [`LazyWidget`](#file-side-bar-widgets-lazy-panel-py) |
| `main.py` | [`EditorFeatureController._make_tests`](#controller) |
| `side_bar_widgets/deferred_dock.py` | [`DeferredDock`](#file-side-bar-widgets-deferred-dock-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `LazyWidget` in `side_bar_widgets/lazy_panel.py`. **Contract:** Build an optional panel once, on first open, then reuse it. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `side_bar_widgets/lazy_panel.py`. **Placement:** the complete `LazyWidget` definition in its named owner. The [installation block](#file-side-bar-widgets-lazy-panel-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** LazyWidget memoizes a factory result. DeferredDock.ensure creates the body exactly once; showEvent invokes ensure before display. The existing Ruff client still starts with MainWindow; this chapter defers the listed widgets and terminal process. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_23_lazy_factory_once` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Repeated panel access returns the same object and calls its factory once.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_23_lazy_factory_once():
    """Repeated panel access returns the same object and calls its factory once."""
    calls = []
    def create():
        """Count actual construction before returning a distinct object."""
        calls.append(1)
        return object()
    panel = LazyWidget(create)
    first = panel.get()
    assert panel.get() is first
    assert calls == [1]
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_23_lazy_factory_once"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-side-bar-widgets-lazy-panel-py"></a>
#### CREATE FILE — `side_bar_widgets/lazy_panel.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `lazy_panel.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Construct an optional panel once when requested.

<a id="file-side-bar-widgets-deferred-dock-py"></a>
#### CREATE FILE — `side_bar_widgets/deferred_dock.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `deferred_dock.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Construct expensive terminal/console widgets only when their dock first shows.

### 7. Acceptance check

Start with a fresh settings profile and no session tabs. Confirm terminal/console bodies are absent until opened, then reuse the same bodies on later hide/show cycles.

---

<a id="topic-24"></a>
## Topic 24 — Background file hashing

### 1. Topic and resulting behavior

File-change hints enqueue byte hashing outside the GUI thread. Results carry file path, editor identity, and revision, so closing a tab or changing its path cannot apply an obsolete digest to another document.

### 2. Official documentation and code walkthrough

FileHashQueue deduplicates ownership and delivers through Qt signals. The controller reattaches watches after atomic replacements and sets a comparison hint only when the digest differs from the last accepted disk revision.

- [Qt QFileSystemWatcher](https://doc.qt.io/archives/qt-5.15/qfilesystemwatcher.html)
- [Python futures](https://docs.python.org/3/library/concurrent.futures.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/file_hash_queue.py` | [`FileHashQueue`](#file-code-inteligence-file-hash-queue-py) |
| `main.py` | [`EditorFeatureController._track_file`](#controller) |
| `main.py` | [`EditorFeatureController._directory_changed`](#controller) |
| `main.py` | [`EditorFeatureController._file_changed`](#controller) |
| `main.py` | [`EditorFeatureController._hash_ready`](#controller) |
| `main.py` | [`EditorFeatureController.retire`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `FileHashQueue._on_done` in `code_inteligence/file_hash_queue.py`. **Contract:** Discard a result after edit, rename, Save As or tab closure. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/file_hash_queue.py`. **Placement:** the complete `FileHashQueue._on_done` definition in its named owner. The [installation block](#file-code-inteligence-file-hash-queue-py) gives the exact file or baseline placement. This answer is already included there.

````python
    def _on_done(self, identity, request, digest, future) -> None:
        """Discard a result after edit, rename, Save As or tab closure."""
        self.futures.discard(future)
        if self.pending.get(identity) == request and isinstance(digest, bytes):
            self.changed.emit(identity, request, digest)
````

**Why this works:** FileHashQueue deduplicates ownership and delivers through Qt signals. The controller reattaches watches after atomic replacements and sets a comparison hint only when the digest differs from the last accepted disk revision. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_24_hash_generation` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** A stale result drains from shutdown tracking without being published.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_24_hash_generation(app, tmp_path):
    """A stale result drains from shutdown tracking without being published."""
    worker = FileHashQueue()
    received = []
    worker.changed.connect(lambda *result: received.append(result))
    path = (tmp_path / 'a.md').resolve()
    worker.pending['editor'] = (path, 2)
    old = Future()
    worker.futures.add(old)
    worker._on_done('editor', (path, 1), b'old', old)
    assert not worker.futures and not received
    current = Future()
    worker.futures.add(current)
    digest = hashlib.sha256(b'current').digest()
    worker._on_done('editor', (path, 2), digest, current)
    assert received == [('editor', (path, 2), digest)]
    worker.shutdown()
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_24_hash_generation"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-file-hash-queue-py"></a>
#### CREATE FILE — `code_inteligence/file_hash_queue.py`

**Folder:** `code_inteligence/` already exists. Create **only** `file_hash_queue.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Background file hashing with identity and generation checks.

### 7. Acceptance check

Replace a watched file atomically and close or edit its tab while hashing runs. Obsolete results must be ignored.

---

<a id="topic-25"></a>
## Topic 25 — Incremental syntax highlighting

### 1. Topic and resulting behavior

Incremental syntax-state scanning is enabled in the production Python lexer and the native Cython scanner. Sparse checkpoints retain every scanner-local value needed to resume; edits invalidate affected prefixes before reuse.

### 2. Official documentation and code walkthrough

LexerCheckpoints rewinds lookahead boundaries and keeps bounded sparse snapshots. Both scanners expose the same optional snapshot/checkpoints contract. STATE_API=2 rejects an old native binary; styleText uses the cache before styling and records timings.

- [QScintilla introduction](https://www.riverbankcomputing.com/software/qscintilla/intro)
- [Scintilla lexing](https://www.scintilla.org/ScintillaDoc.html)
- [Cython compilation](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html)
- [QScintilla custom lexer](https://www.riverbankcomputing.com/static/Docs/QScintilla/classQsciLexerCustom.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `python_editor/lexer_checkpoints.py` | [`LexerCheckpoints`](#file-python-editor-lexer-checkpoints-py) |
| `python_editor/custompythonlexer.py` | [`_py_compute_state`](#integration-python-editor-custompythonlexer-py) |
| `python_editor/custompythonlexer.py` | [`PyCustomLexer.styleText`](#integration-python-editor-custompythonlexer-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `LexerCheckpoints.invalidate` in `python_editor/lexer_checkpoints.py`. **Contract:** Discard states at/after the changed line and three-byte lookahead. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `python_editor/lexer_checkpoints.py`. **Placement:** the complete `LexerCheckpoints.invalidate` definition in its named owner. The [installation block](#file-python-editor-lexer-checkpoints-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** LexerCheckpoints rewinds lookahead boundaries and keeps bounded sparse snapshots. Both scanners expose the same optional snapshot/checkpoints contract. STATE_API=2 rejects an old native binary; styleText uses the cache before styling and records timings. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_25_checkpoint_invalidates_prefix` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** An edit near the start invalidates production snapshots farther downstream.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_25_checkpoint_invalidates_prefix():
    """An edit near the start invalidates production snapshots farther downstream."""
    from python_editor.custompythonlexer import _py_compute_state
    cache = LexerCheckpoints(verify=True)
    old = (b"value = 1\n" * 2000)
    cache.state_before(old, len(old), _py_compute_state)
    assert len(cache.states) > 1
    new = bytes([39, 39, 39]) + old
    cache.invalidate(new)
    assert cache.states == {0: None}
    assert cache.state_before(new, len(new), _py_compute_state) == _py_compute_state(new, len(new))
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_25_checkpoint_invalidates_prefix"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-python-editor-lexer-checkpoints-py"></a>
#### CREATE FILE — `python_editor/lexer_checkpoints.py`

**Folder:** `python_editor/` already exists. Create **only** `lexer_checkpoints.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

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

**File responsibility:** Sparse complete scanner snapshots used by production Python and Cython lexers.

<a id="file-python-editor-setup-py"></a>
#### REPLACE FILE — `python_editor/setup.py`

**Folder:** `python_editor/` already exists. **Placement:** replace the entire existing `setup.py` (baseline lines 1–36), including imports. Keep this single version.

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

**File responsibility:** Build the optional packaged Cython lexer from the repository root.

### 7. Acceptance check

Build the native extension and run the checkpoint equivalence test. It compares arbitrary styling ranges and edits against full scans for both backends.

---

<a id="topic-26"></a>
## Topic 26 — Smarter Markdown preview updates

### 1. Topic and resulting behavior

Markdown preview edits are debounced and hashed for the active document. Hidden previews and large files skip optional conversion; showing preview explicitly renders current content. Repeated JavaScript updates use a local function scope.

### 2. Official documentation and code walkthrough

PreviewSchedule keeps only the latest editor and digest. render_preview sanitizes rendered HTML, updates the loaded shell through a JSON-encoded payload, and preserves scroll position.

- [Qt QTimer](https://doc.qt.io/archives/qt-5.15/qtimer.html)
- [Python hashlib](https://docs.python.org/3/library/hashlib.html)
- [Bleach sanitizer](https://bleach.readthedocs.io/en/latest/clean.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `markdown_editor/preview_scheduler.py` | [`PreviewSchedule`](#file-markdown-editor-preview-scheduler-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `PreviewSchedule.flush` in `markdown_editor/preview_scheduler.py`. **Contract:** Render only if the visible editor's source actually changed. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `markdown_editor/preview_scheduler.py`. **Placement:** the complete `PreviewSchedule.flush` definition in its named owner. The [installation block](#file-markdown-editor-preview-scheduler-py) gives the exact file or baseline placement. This answer is already included there.

````python
    def flush(self) -> None:
        """Render only if the visible editor's source actually changed."""
        editor = self.editor
        if editor is None or editor is not self.parent().current_editor():
            return
        preview = getattr(self.parent(), "preview", None)
        if preview is not None and not preview.isVisible():
            return
        if editor.length() > 2_000_000 and not getattr(editor, "_large_file_override", False):
            return
        # The digest includes the document body; the cache key also includes
        # editor identity so equal text in two tabs does not confuse ownership.
        digest = hashlib.sha256(editor.text().encode("utf-8")).digest()
        key = (id(editor), digest)
        if self.last != key:
            self.render()
            self.last = key
````

**Why this works:** PreviewSchedule keeps only the latest editor and digest. render_preview sanitizes rendered HTML, updates the loaded shell through a JSON-encoded payload, and preserves scroll position. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_26_preview_active_tab` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Render a changed active buffer once and ignore a now-background buffer.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_26_preview_active_tab(app):
    """Render a changed active buffer once and ignore a now-background buffer."""
    owner = QWidget()
    editor = QsciScintilla()
    editor.setText('first')
    owner.current_editor = lambda: editor
    rendered = []
    schedule = PreviewSchedule(lambda: rendered.append(editor.text()), owner)
    schedule.editor = editor
    schedule.flush()
    schedule.flush()
    assert rendered == ['first']
    owner.current_editor = lambda: None
    editor.setText('second')
    schedule.flush()
    assert rendered == ['first']
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_26_preview_active_tab"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-markdown-editor-preview-scheduler-py"></a>
#### CREATE FILE — `markdown_editor/preview_scheduler.py`

**Folder:** `markdown_editor/` already exists. Create **only** `preview_scheduler.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
        if editor.length() > 2_000_000 and not getattr(editor, "_large_file_override", False):
            return
        # The digest includes the document body; the cache key also includes
        # editor identity so equal text in two tabs does not confuse ownership.
        digest = hashlib.sha256(editor.text().encode("utf-8")).digest()
        key = (id(editor), digest)
        if self.last != key:
            self.render()
            self.last = key
````

**File responsibility:** Coalesce Markdown preview changes for the active document.

### 7. Acceptance check

Type rapidly, switch tabs before the timer fires, hide/show preview, and render repeatedly. Confirm the active document appears and scroll is retained.

---

<a id="topic-27"></a>
## Topic 27 — Large-file mode

### 1. Topic and resulting behavior

Large-file mode measures current UTF-8 byte length, including growth during editing. It pauses optional analysis/presentation work above two million bytes while editing and saving remain available; a per-tab override explicitly re-enables optional features.

### 2. Official documentation and code walkthrough

file_size_mode expresses the boundary. The controller refreshes policy when text or tabs change, clears optional completion state when necessary, and applies the same threshold to outline/minimap/preview/provider work.

- [QScintilla introduction](https://www.riverbankcomputing.com/software/qscintilla/intro)
- [Python bytes](https://docs.python.org/3/library/stdtypes.html#bytes)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_settings/large_file_policy.py` | [`file_size_mode`](#file-code-settings-large-file-policy-py) |
| `code_settings/large_file_policy.py` | [`should_update_panel`](#file-code-settings-large-file-policy-py) |
| `main.py` | [`EditorFeatureController.toggle_large_file`](#controller) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `file_size_mode` in `code_settings/large_file_policy.py`. **Contract:** Decide whether optional preview, minimap and analysis should pause. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_settings/large_file_policy.py`. **Placement:** the complete `file_size_mode` definition in its named owner. The [installation block](#file-code-settings-large-file-policy-py) gives the exact file or baseline placement. This answer is already included there.

````python
def file_size_mode(size: int, *, threshold: int = 2_000_000) -> bool:
    """Decide whether optional preview, minimap and analysis should pause."""
    # Saving, dirty tracking and recovery are outside this optional budget.
    return size >= threshold
````

**Why this works:** file_size_mode expresses the boundary. The controller refreshes policy when text or tabs change, clears optional completion state when necessary, and applies the same threshold to outline/minimap/preview/provider work. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_27_large_file_boundary` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Apply a byte threshold at the boundary without platform-dependent file I/O.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_27_large_file_boundary():
    """Apply a byte threshold at the boundary without platform-dependent file I/O."""
    assert not file_size_mode(9, threshold=10)
    assert file_size_mode(10, threshold=10)
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_27_large_file_boundary"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-settings-large-file-policy-py"></a>
#### CREATE FILE — `code_settings/large_file_policy.py`

**Folder:** `code_settings/` already exists. Create **only** `large_file_policy.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Decide whether optional presentation work fits the document budget.

### 7. Acceptance check

Open just-below and just-above boundary files, grow a small buffer past the threshold, then use the override and switch tabs.

---

<a id="topic-28"></a>
## Topic 28 — Shared analysis scheduling

### 1. Topic and resulting behavior

One application-owned worker serializes Jedi completion, signatures, documentation, definitions, references, rename, and workspace scans. Request lanes are separated by document and kind; closing a tab invalidates its deliveries while the queue retains running-worker ownership.

### 2. Official documentation and code walkthrough

AnalysisProvider snapshots plain source/context before submission. AnalysisQueue cancels superseded pending work and checks serials on GUI-thread delivery. Each adapter translates plain results into the existing provider signals, preserving the editor shutdown contract.

- [Python futures](https://docs.python.org/3/library/concurrent.futures.html)
- [Jedi API](https://jedi.readthedocs.io/en/latest/docs/api.html)
- [Jedi Script and environment API](https://jedi.readthedocs.io/en/latest/docs/api.html)
- [Qt connection types](https://doc.qt.io/archives/qt-5.15/qt.html#ConnectionType-enum)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/analysis_cache.py` | [`RequestKey`](#file-code-inteligence-analysis-cache-py) |
| `code_inteligence/analysis_scheduler.py` | [`AnalysisQueue`](#file-code-inteligence-analysis-scheduler-py) |
| `code_inteligence/analysis_provider.py` | [`AnalysisProvider`](#file-code-inteligence-analysis-provider-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `AnalysisQueue._receive` in `code_inteligence/analysis_scheduler.py`. **Contract:** Drain futures and reject stale serials even when keys are identical. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/analysis_scheduler.py`. **Placement:** the complete `AnalysisQueue._receive` definition in its named owner. The [installation block](#file-code-inteligence-analysis-scheduler-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
            if not isinstance(value, Exception):
                self.cache.put(key, value)  # Transient failures must not poison the cache.
            self.ready.emit(key, value)
        if not self.futures:
            self.idle.emit()
````

**Why this works:** AnalysisProvider snapshots plain source/context before submission. AnalysisQueue cancels superseded pending work and checks serials on GUI-thread delivery. Each adapter translates plain results into the existing provider signals, preserving the editor shutdown contract. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_28_latest_analysis_wins` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Run real worker jobs while rejecting the obsolete result on Qt delivery.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_28_latest_analysis_wins(app):
    """Run real worker jobs while rejecting the obsolete result on Qt delivery."""
    queue = AnalysisQueue()
    release = Event()
    results = []
    queue.ready.connect(lambda key, value: results.append((key, value)))
    old = RequestKey('a.py', 1, sys.executable, '/project', 'symbols')
    new = RequestKey('a.py', 2, sys.executable, '/project', 'symbols')
    def first():
        """Block the old work so a newer request supersedes it deterministically."""
        assert release.wait(2)
        return 'old'
    queue.submit(old, first)
    queue.submit(new, lambda: 'new')
    release.set()
    wait_until(app, lambda: not queue.is_running())
    assert results == [(new, 'new')]
    queue.shutdown()
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_28_latest_analysis_wins"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-analysis-scheduler-py"></a>
#### CREATE FILE — `code_inteligence/analysis_scheduler.py`

**Folder:** `code_inteligence/` already exists. Create **only** `analysis_scheduler.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
"""One application-owned worker queue for all Jedi providers and workspace scans."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, Future
from time import perf_counter
from PyQt5.QtCore import QCoreApplication, QObject, Qt, pyqtSignal
from code_inteligence.analysis_cache import LRU, RequestKey


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
        self.cache, self.futures = LRU(), set()
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
        if key in self.cache.values:
            future = Future()
            future.set_result(self.cache.get(key))
            self.futures.add(future)
            self._deliver.emit(key, future, serial, 0.0)
            return
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
            if not isinstance(value, Exception):
                self.cache.put(key, value)  # Transient failures must not poison the cache.
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
        self.cache.values.clear()
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

**File responsibility:** One application-owned worker queue for all Jedi providers and workspace scans.

<a id="file-code-inteligence-analysis-provider-py"></a>
#### CREATE FILE — `code_inteligence/analysis_provider.py`

**Folder:** `code_inteligence/` already exists. Create **only** `analysis_provider.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Immutable Jedi requests and adapters preserving existing editor signals.

<a id="file-code-inteligence-autocompleter-py"></a>
#### REPLACE FILE — `code_inteligence/autocompleter.py`

**Folder:** `code_inteligence/` already exists. **Placement:** replace the entire existing `autocompleter.py` (baseline lines 1–70), including imports. Keep this single version.

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

**File responsibility:** Shared-queue adapter for autocompleter.

<a id="file-code-inteligence-signature-helper-py"></a>
#### REPLACE FILE — `code_inteligence/signature_helper.py`

**Folder:** `code_inteligence/` already exists. **Placement:** replace the entire existing `signature_helper.py` (baseline lines 1–70), including imports. Keep this single version.

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

**File responsibility:** Shared-queue adapter for signature helper.

<a id="file-code-inteligence-hover-helper-py"></a>
#### REPLACE FILE — `code_inteligence/hover_helper.py`

**Folder:** `code_inteligence/` already exists. **Placement:** replace the entire existing `hover_helper.py` (baseline lines 1–75), including imports. Keep this single version.

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

**File responsibility:** Shared-queue adapter for hover helper.

<a id="file-code-inteligence-definition-finder-py"></a>
#### REPLACE FILE — `code_inteligence/definition_finder.py`

**Folder:** `code_inteligence/` already exists. **Placement:** replace the entire existing `definition_finder.py` (baseline lines 1–68), including imports. Keep this single version.

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

**File responsibility:** Shared-queue adapter for definition finder.

<a id="file-code-inteligence-references-finder-py"></a>
#### REPLACE FILE — `code_inteligence/references_finder.py`

**Folder:** `code_inteligence/` already exists. **Placement:** replace the entire existing `references_finder.py` (baseline lines 1–64), including imports. Keep this single version.

````python
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
````

**File responsibility:** Shared-queue adapter for references finder.

### 7. Acceptance check

Request analysis in two tabs, edit one, change interpreter/workspace, and close a requesting tab. Only current live-tab results should be displayed.

---

<a id="topic-29"></a>
## Topic 29 — Bounded result caching

### 1. Topic and resulting behavior

A bounded LRU retains successful exact-key analysis results. Keys include document identity, path, source digest, caret, request kind, workspace, and interpreter. Errors are not cached; environment changes clear retained results.

### 2. Official documentation and code walkthrough

LRU moves hits to the newest position and evicts oldest entries. The queue delivers cache hits asynchronously, preserving the same generation checks and signal order as worker results.

- [Python OrderedDict](https://docs.python.org/3/library/collections.html#collections.OrderedDict)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_inteligence/analysis_cache.py` | [`LRU`](#file-code-inteligence-analysis-cache-py) |
| `code_inteligence/analysis_cache.py` | [`RequestKey`](#file-code-inteligence-analysis-cache-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `LRU` in `code_inteligence/analysis_cache.py`. **Contract:** A small revision-aware cache whose keys include environment identity. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `code_inteligence/analysis_cache.py`. **Placement:** the complete `LRU` definition in its named owner. The [installation block](#file-code-inteligence-analysis-cache-py) gives the exact file or baseline placement. This answer is already included there.

````python
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
````

**Why this works:** LRU moves hits to the newest position and evicts oldest entries. The queue delivers cache hits asynchronously, preserving the same generation checks and signal order as worker results. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_29_cache_eviction` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Reading A promotes it; inserting C then removes older untouched B.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_29_cache_eviction():
    """Reading A promotes it; inserting C then removes older untouched B."""
    cache = LRU(size=2)
    cache.put('A', 1)
    cache.put('B', 2)
    assert cache.get('A') == 1
    cache.put('C', 3)
    assert cache.get('B') is None
    assert cache.get('A') == 1
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_29_cache_eviction"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-code-inteligence-analysis-cache-py"></a>
#### CREATE FILE — `code_inteligence/analysis_cache.py`

**Folder:** `code_inteligence/` already exists. Create **only** `analysis_cache.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** Revision and environment keyed bounded result storage.

### 7. Acceptance check

Fill a small cache, touch an older entry, and insert another. Verify true least-recently-used eviction and no cross-tab/environment reuse.

---

<a id="topic-30"></a>
## Topic 30 — Pause hidden-panel work

### 1. Topic and resulting behavior

Problems, References, Markdown outline, and a lightweight clickable minimap defer presentation rebuilding while hidden. The minimap paints bounded line-width groups and viewport position; clicking navigates to the corresponding source line.

### 2. Official documentation and code walkthrough

SnapshotDock retains the latest rows and a dirty flag. The controller coalesces active-document presentation updates; showing a dock refreshes current state. Large-file mode replaces minimap work with a paused message.

- [Qt QWidget visibility](https://doc.qt.io/archives/qt-5.15/qwidget.html)
- [Qt QTimer](https://doc.qt.io/archives/qt-5.15/qtimer.html)
- [Qt QPainter](https://doc.qt.io/archives/qt-5.15/qpainter.html)
- [Qt paint events](https://doc.qt.io/archives/qt-5.15/qwidget.html#paintEvent)

Read the named API pages alongside the implementation below. Qt links describe the Qt 5 APIs wrapped by PyQt5; use the Python syntax printed in this guide.

### 3. Files and integration locations

| File | Definition / installation link |
|---|---|
| `code_settings/large_file_policy.py` | [`should_update_panel`](#file-code-settings-large-file-policy-py) |
| `main.py` | [`EditorFeatureController.current_changed`](#controller) |
| `side_bar_widgets/snapshot_dock.py` | [`SnapshotDock`](#file-side-bar-widgets-snapshot-dock-py) |
| `side_bar_widgets/document_minimap.py` | [`DocumentMinimap`](#file-side-bar-widgets-document-minimap-py) |

The full-file blocks identify the folder and line-1 placement. The linked Final integration blocks give pinned baseline lines and named replacement boundaries for existing methods.

### 4. Exercise A — implement the behavior

Implement `SnapshotDock.set_rows` in `side_bar_widgets/snapshot_dock.py`. **Contract:** Retain immutable (description, path, line, column) rows without hidden repaint. Use the imports and supporting types from the complete file. Explain the state transition described in the walkthrough before viewing the answer.

<details>
<summary>Solution A — complete definition, placement, and explanation</summary>

**File:** `side_bar_widgets/snapshot_dock.py`. **Placement:** the complete `SnapshotDock.set_rows` definition in its named owner. The [installation block](#file-side-bar-widgets-snapshot-dock-py) gives the exact file or baseline placement. This answer is already included there.

````python
    def set_rows(self, rows, empty='No results'):
        """Retain immutable (description, path, line, column) rows without hidden repaint."""
        self.rows = tuple(tuple(row) for row in rows)
        self.empty.setText(empty)
        self.dirty = True
        self.refresh()
````

**Why this works:** SnapshotDock retains the latest rows and a dirty flag. The controller coalesces active-document presentation updates; showing a dock refreshes current state. Large-file mode replaces minimap work with a paused message. The docstring states the method contract; comments beside the state changes explain the important safeguards.

</details>

### 5. Exercise B — prove the behavior

Write `test_30_hidden_panel_guard` in `tests/test_feature_exercises.py` using the imports and fixtures from [Test installation](#test-installation). **Required result:** Visibility prevents optional work even for a small editable document.

<details>
<summary>Solution B — executable regression test</summary>

````python
def test_30_hidden_panel_guard(app):
    """Visibility prevents optional work even for a small editable document."""
    panel = QWidget()
    editor = QsciScintilla()
    editor.setText('small')
    panel.hide()
    assert not should_update_panel(panel, editor)
    panel.show()
    assert should_update_panel(panel, editor)
    panel.close()
````

**Placement:** module scope in the complete test file; this test is already included there. Run it from the repository root:

````bash
python -m pytest -q tests/test_feature_exercises.py -k "test_30_hidden_panel_guard"
````

The assertions exercise the documented result or rejection path. Supplemental production integration regressions appear in `tests/test_completed_features.py`.

</details>

### 6. Full implementation

<a id="file-side-bar-widgets-document-minimap-py"></a>
#### CREATE FILE — `side_bar_widgets/document_minimap.py`

**Folder:** `side_bar_widgets/` already exists. Create **only** `document_minimap.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
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
````

**File responsibility:** A lightweight line-shape minimap with click-to-navigate and deferred hidden work.

### 7. Acceptance check

Edit while panels are hidden, then reveal them. Check that only the latest document state appears and minimap navigation follows the selected tab.

---

<a id="final-integration"></a>
## Final integration — combine existing-file changes once

All new modules must exist before importing the editor. The following sections complete the connection to the actual repository. They intentionally consolidate shared save, close, tab, preview, and analysis methods. Do not apply earlier course replacements after these replacements.

The table below is a quick navigation map. Each detailed replacement includes its full code and authoritative named boundary.

**`main.py`**

| Definition | Baseline lines |
|---|---|
| `MainWindow.__init__` | 142–235 |
| `MainWindow.init_ui` | 237–382 |
| `MainWindow._on_git_snapshot` | 384–391 |
| `MainWindow._on_git_failure` | 405–411 |
| `MainWindow._update_outline` | 454–457 |
| `MainWindow._on_editor_text_changed` | 578–591 |
| `MainWindow.set_up_console_dock` | 614–640 |
| `MainWindow._set_sidebar_icon` | 642–647 |
| `MainWindow.get_sidebar_label` | 649–658 |
| `MainWindow._connect_editor` | 686–706 |
| `MainWindow._on_ruff_diagnostics` | 722–738 |
| `MainWindow._restart_ruff` | 740–769 |
| `MainWindow._on_editor_cursor_changed` | 771–775 |
| `MainWindow.set_up_menu` | 777–1050 |
| `MainWindow.toggle_preview` | 1286–1296 |
| `MainWindow._apply_settings` | 1507–1530 |
| `MainWindow.set_new_tab` | 1749–1816 |
| `MainWindow.set_up_body` | 1837–2015 |
| `MainWindow.close_editor` | 2155–2185 |
| `MainWindow._dispose_editor` | 2187–2198 |
| `MainWindow.show_hide_tab` | 2306–2370 |
| `MainWindow.new_file` | 2374–2384 |
| `MainWindow.open_folder` | 2405–2431 |
| `MainWindow._save_editor_to_path` | 2510–2589 |
| `MainWindow.save_as` | 2619–2672 |
| `MainWindow._on_current_editor_changed` | 2740–2763 |
| `MainWindow.render_preview` | 2797–2809 |
| `MainWindow._convert_editor` | 2836–2900 |
| `MainWindow._background_work_running` | 3101–3144 |
| `MainWindow.closeEvent` | 3153–3206 |

**`python_editor/pythoneditor.py`**

| Definition | Baseline lines |
|---|---|
| `PythonEditor.__init__` | 37–179 |
| `PythonEditor.keyPressEvent` | 402–459 |
| `PythonEditor._cursorPositionChanged` | 528–542 |
| `PythonEditor._analysis_workers` | 568–576 |

**`markdown_editor/markdowneditor.py`**

| Definition | Baseline lines |
|---|---|
| `MarkdownEditor.keyPressEvent` | 90–94 |

**`python_editor/custompythonlexer.py`**

| Definition | Baseline lines |
|---|---|
| `_py_compute_state` | 113–299 |
| `PyCustomLexer.styleText` | 1131–1172 |

<a id="integration-main-py"></a>
### Integrate `main.py`

#### Imports and module-level state

**Insert after** `from markdowneditor_assets import asset_path` (baseline line 42), at module scope, before the next existing statement. Do not duplicate imports already added.

````python
import time
import uuid
from code_inteligence.analysis_cache import RequestKey
from code_inteligence.analysis_scheduler import shared_analysis
from code_inteligence.document_recovery import RecoveryStore
from code_inteligence.file_hash_queue import FileHashQueue
from code_inteligence.local_history import VersionStore
from code_inteligence.symbol_index import workspace_symbols
from code_inteligence.symbol_rename import apply_rename, plan_rename, rename_preview
from code_inteligence.text_comparison import three_way, unified_diff
from code_settings.keyboard_shortcuts import ShortcutDialog
from code_settings.performance_diagnostics import Timings
from code_settings.workspace_layouts import Layouts
from markdown_editor.authoring_tools import broken_local_links, relative_link, table
from markdown_editor.heading_navigation import toc
from markdown_editor.preview_scheduler import PreviewSchedule
from python_editor.run_configurations import ProcessPanel, RunConfig, RunConfigDialog, load_configs, save_configs
from python_editor.test_panel import TestDock
from side_bar_widgets.breadcrumb import Breadcrumb
from side_bar_widgets.lazy_panel import LazyWidget
from side_bar_widgets.markdown_outline import MarkdownOutline
from side_bar_widgets.status_item import StatusItem
from side_bar_widgets.welcome_screen import Welcome
````

**Replace the entire `MARKDOWN_ALLOWED_ATTRIBUTES` assignment**, baseline lines 59–65, immediately before `MARKDOWN_ALLOWED_PROTOCOLS`. Heading IDs must survive sanitization for heading links.

````python
MARKDOWN_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "th": ["align"],
    "td": ["align"],
    **{f"h{level}": ["id"] for level in range(1, 7)},
}
````

**Class docstring:** immediately after `class MainWindow(...):` (baseline line 120), before its first attribute or method, insert at four-space indentation:

````python
    """Own the editor window, document lifecycle, existing services, and feature controller."""
````

#### REPLACE `MainWindow.__init__`

**File:** `main.py`. **Baseline:** lines 142–235. Replace the entire named definition, including any decorator. Stop before `init_ui` and keep that following definition.

````python
    def __init__(self):
        """Construct source services, UI, feature bridge and restored drafts."""
        super().__init__()
        self._startup_started = time.perf_counter()
        self.update_check_finished.connect(self._show_update_check_result)
        self._dirty_editors = set()
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
        # The bridge needs the body, menus, status bar and docks created by
        # init_ui. Construct it before session restore reopens any editors.
        self.features = EditorFeatureController(self)

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
        # Saved paths and unsaved text have different lifetimes. Recovery
        # prompts after normal tabs return so drafts never overwrite files.
        self.features.restore_recovery()
        self.features.timings.observe("startup", time.perf_counter() - self._startup_started)
````

**Responsibility:** Construct source services, UI, feature bridge and restored drafts.

#### REPLACE `MainWindow.init_ui`

**File:** `main.py`. **Baseline:** lines 237–382. Replace the entire named definition, including any decorator. Stop before `_on_git_snapshot` and keep that following definition.

````python
    def init_ui(self):
        """Create base menus, docks, editors and the fixed Markdown preview."""
        self.setWindowTitle("Code Editor")
        self.setWindowIcon(QIcon(resource_path("icons/app-icon-256.png")))
        self.resize(self.WIDTH, self.HEIGHT)
        self.window_font = QFont("sans-serif")
        self.window_font.setPointSize(13)
        self.setFont(self.window_font)

        qss_path = resource_path("css/style.qss")
        print(f"QSS path: {qss_path}")
        print(f"QSS exists: {os.path.exists(qss_path)}")
        try:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError as e:
            print(f"STYLESHEET ERROR: {e}")
            # Fallback: apply basic dark styling inline
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1f22; color: #d3d3d3; }
                QMenuBar { background-color: #2d2d2d; color: floralwhite; }
                QTabWidget { background-color: #1e1f22; color: #d3d3d3; }
            """)

        self._outline_debounce = QTimer(self)
        self._outline_debounce.setSingleShot(True)
        self._outline_debounce.setInterval(500)
        # BUGFIX: was connected to its own start() -> restarted itself forever
        self._outline_debounce.timeout.connect(self._update_outline)

        self.set_up_menu()
        self.set_up_body()

        self._git_refresh_timer = QTimer(self)
        self._git_refresh_timer.setInterval(15000)
        self._git_refresh_timer.timeout.connect(self._refresh_git_state)
        self._git_refresh_timer.start()

        # Find/Replace bar. Hidden by default
        self.find_bar = FindReplaceBar(show_replace=False, parent=self)
        self.find_bar.hide()

        # Connect the find bar's signals to our search methods
        self.find_bar.find_next_requested.connect(self._do_find_next)
        self.find_bar.find_prev_requested.connect(self._do_find_prev)
        self.find_bar.replace_requested.connect(self._do_replace)
        self.find_bar.replace_all_requested.connect(self._do_replace_all)

        self.set_up_console_dock()

        self._preview_ready = False
        self.preview.loadFinished.connect(self._on_preview_loaded)
        base = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{self._preview_css}</style></head><body><div id="content"></div></body></html>"""
        self.preview.setHtml(base)
        self.statusBar().setFont(self.window_font)
        self.statusBar().setStyleSheet("""
                color: #CCCCCC;
        """)
        self.statusBar().showMessage(f"Interpreter: {self.python_runner.interpreter}")
        self.cursor_pos_label = QLabel("Ln 1, Col 1")
        self.cursor_pos_label.setStyleSheet("color: #888; padding: 0 10px;")
        self.statusBar().addPermanentWidget(self.cursor_pos_label)

        # --- Cozy Mode: the status bar cat ---------------------------------------------------------- #
        self.cat = CatController(self)
        self.statusBar().addPermanentWidget(self.cat)

        from cozy.neko import NekoChaser

        self.neko = NekoChaser(self)
        self.neko.start()

        # C2: level-ups plat rhe Dance frames and announce themselves
        self.cat.level_up.connect(
            lambda lvl, title: self.statusBar().showMessage(
                f"Cat leveled up: {title} (level {lvl})", 3000
            )
        )

        # C1: pet milestones (achievement logic lives in the handler, NOT in the lambda
        # keep lambdas dump, they cannot be extended
        self.cat.petted.connect(self._on_cat_petted)

        from cozy.power_mode import PowerModeController

        # Honor the saved Power Mode states from the View menu dropdown.
        self.power = PowerModeController(
            self,
            enabled=self.power_mode_action.isChecked(),
            shake_intensity=1,
            particles_on=self.power_particles_action.isChecked(),
            shake_on=self.power_shake_action.isChecked(),
            glow_enabled=self.power_glow_action.isChecked(),
        )

        self.python_runner.process_started.connect(self._on_run_started)
        self.python_runner.process_finished.connect(self._on_run_finished)

        # Word count label - shows "Words: X | Chars: Y"
        self.word_count_label = QLabel("Words: 0 | Chars: 0")
        self.word_count_label.setStyleSheet("color: #888; padding: 0 10px;")
        self.statusBar().addPermanentWidget(self.word_count_label)

        self.show()

        QTimer.singleShot(2000, lambda: self.check_for_updates(manual=False))

        # --- idle choreography: sleepy -> box -> sleep ------------------ #
        # Escalation ladder: 60 s idle = yawn; 3 min = deep sleep; 10 min =
        # the cat moves into a box (and pops back out when you return).
        # Timers re-arm on activity via _connect_editor's textChanged below.
        self._cat_sleepy_timer = QTimer(self)
        self._cat_sleepy_timer.setSingleShot(True)
        self._cat_sleepy_timer.timeout.connect(lambda: self.cat.set_state("sleepy", 120000))

        self._cat_sleep_timer = QTimer(self)
        self._cat_sleep_timer.setSingleShot(True)
        self._cat_sleep_timer.timeout.connect(lambda: self.cat.set_state("sleep", 300000))

        self._cat_box_timer = QTimer(self)
        self._cat_box_timer.setSingleShot(True)
        self._cat_box_timer.timeout.connect(self._cat_moves_into_box)

        self._arm_cat_timers()

        self.git_service = GitService(self)
        self.git_branch_label = QLabel("No Git repository", self)
        self.statusBar().addPermanentWidget(self.git_branch_label)

        self.git_graph = CommitGraphPanel(self)
        self.git_graph_dock = QDockWidget("Git History", self)
        self.git_graph_dock.setObjectName("GitHistoryDock")
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
        self._apply_git_history_theme(self._active_theme_path())
        self.addDockWidget(Qt.BottomDockWidgetArea, self.git_graph_dock)
        self.git_graph_dock.hide()

        self.git_service.snapshotReady.connect(self._on_git_snapshot)
        self.git_service.failed.connect(self._on_git_failure)
        # GitService is created after the body and menus, so startup refresh belongs
        # here, after all widgets and signals connections exists.
        self._refresh_git_state()
````

**Responsibility:** Create base menus, docks, editors and the fixed Markdown preview.

#### REPLACE `MainWindow._on_git_snapshot`

**File:** `main.py`. **Baseline:** lines 384–391. Replace the entire named definition, including any decorator. Stop before `_apply_git_history_theme` and keep that following definition.

````python
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
````

**Responsibility:** Update branch identity and graph from the same Git snapshot.

#### REPLACE `MainWindow._on_git_failure`

**File:** `main.py`. **Baseline:** lines 405–411. Replace the entire named definition, including any decorator. Stop before `_refresh_git_state` and keep that following definition.

````python
    def _on_git_failure(self, message: str) -> None:
        """Clear stale repository identity without interrupting editing."""
        self.git_branch_label.setText("No Git repository")
        self.git_branch_label.setToolTip(message)
        
        # Do not call git_branch_label.clear(); that erases the message just set.
        self.git_graph.clear()
        self.git_empty.title_label.setText("No Git repository")
        self.git_empty.hint_label.setText(message)
        self.git_pages.setCurrentWidget(self.git_empty)
````

**Responsibility:** Clear stale repository identity without interrupting editing.

#### REPLACE `MainWindow._update_outline`

**File:** `main.py`. **Baseline:** lines 454–457. Replace the entire named definition, including any decorator. Stop before `update_word_count` and keep that following definition.

````python
    def _update_outline(self):
        """Rebuild the visible outline once after edits, deferring hidden work."""
        if not self.outline_frame.isVisible():
            self._outline_needs_refresh = True
            return
        self._outline_needs_refresh = False
        editor = self.current_editor()
        if isinstance(editor, PythonEditor):
            if (getattr(editor, "_large_file_mode", False)
                    and not getattr(editor, "_large_file_override", False)):
                self.outline_tree.clear()
                return
            self.outline_tree.update_outline(editor.text())
````

**Responsibility:** Rebuild the visible outline once after edits, deferring hidden work.

#### REPLACE `MainWindow._on_editor_text_changed`

**File:** `main.py`. **Baseline:** lines 578–591. Replace the entire named definition, including any decorator. Stop before `mark_editor_clean` and keep that following definition.

````python
    def _on_editor_text_changed(self, editor):
        """Mark the specific editor that emitted textChanged as dirty."""
        if editor is None:
            return
        if getattr(editor, "_loading_text", False):
            return
        self._dirty_editors.add(editor)
        editor._large_file_mode = editor.length() > 2_000_000
        editor._revision = getattr(editor, "_revision", 0) + 1
        path = getattr(editor, "path", None)
        base_title = path.name if path is not None else "Untitled"
        self.tab_view.set_editor_title(editor, f"● {base_title}")
        if editor is self.current_editor():
            self.update_word_count()
````

**Responsibility:** Mark the specific editor that emitted textChanged as dirty.

#### REPLACE `MainWindow.set_up_console_dock`

**File:** `main.py`. **Baseline:** lines 614–640. Replace the entire named definition, including any decorator. Stop before `_set_sidebar_icon` and keep that following definition.

````python
    def set_up_console_dock(self):
        """Create stable lazy Console/Terminal dock shells for layout restoration."""
        from side_bar_widgets.deferred_dock import DeferredDock
        self.console_dock = DeferredDock("Python Console", "ConsoleDock", self._make_console, self)
        self.terminal_dock = DeferredDock("Terminal", "TerminalDock", self._make_terminal, self)
        for name, dock in (("console", self.console_dock), ("terminal", self.terminal_dock)):
            self.addDockWidget(Qt.BottomDockWidgetArea, dock)
            dock.hide()
            dock.visibilityChanged.connect(lambda visible, n=name: self._set_sidebar_icon(n, visible))
````

**Responsibility:** Create stable lazy Console/Terminal dock shells for layout restoration.

#### REPLACE `MainWindow._set_sidebar_icon`

**File:** `main.py`. **Baseline:** lines 642–647. Replace the entire named definition, including any decorator. Stop before `get_sidebar_label` and keep that following definition.

````python
    def _set_sidebar_icon(self, name: str, active: bool):
        """Reflect a tool's actual visibility using the existing icon variants."""
        button = self.sidebar_labels.get(name)
        if button is not None:
            button.setChecked(active)
````

**Responsibility:** Reflect a tool's actual visibility using the existing icon variants.

#### REPLACE `MainWindow.get_sidebar_label`

**File:** `main.py`. **Baseline:** lines 649–658. Replace the entire named definition, including any decorator. Stop before `get_editor` and keep that following definition.

````python
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
````

**Responsibility:** Create a keyboard-operable 24px SVG sidebar action. The path argument remains for compatibility with set_up_body; the semantic icon name selects the packaged SVG and its active variant.

#### REPLACE `MainWindow._connect_editor`

**File:** `main.py`. **Baseline:** lines 686–706. Replace the entire named definition, including any decorator. Stop before `_cat_unbox` and keep that following definition.

````python
    def _connect_editor(self, editor):
        """Connect all MainWindow signals required by an editor."""
        editor.textChanged.connect(lambda ed=editor: self._on_editor_text_changed(ed))
        # EditorFeatureController.attach connects Markdown changes to PreviewSchedule;
        # avoid a second unconditional timer for every Python keystroke.
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
        if hasattr(self, "features"):
            self.features.attach(editor)
````

**Responsibility:** Connect all MainWindow signals required by an editor.

#### REPLACE `MainWindow._on_ruff_diagnostics`

**File:** `main.py`. **Baseline:** lines 722–738. Replace the entire named definition, including any decorator. Stop before `_restart_ruff` and keep that following definition.

````python
    def _on_ruff_diagnostics(self, editor, diagnostics: list):
        """React only when this editor enters or leaves an issue state.

        State belongs to each editor because two tabs can have independent
        diagnostics. The term ``issues`` deliberately includes Ruff warnings,
        errors, and informational diagnostics, matching the previous UI intent.
        """
        had_issues = getattr(editor, "_had_ruff_issues", False)
        has_issues = bool(diagnostics)

        if has_issues and not had_issues:
            self.cat.set_state("alert", 2_000)
        elif had_issues and not has_issues:
            self.cat.add_xp(5)
            self.cat.set_state("stretch", 1_500)

        editor._had_ruff_issues = has_issues
        if hasattr(self, "features"):
            self.features.diagnostics_changed(editor, diagnostics)
````

**Responsibility:** React only when this editor enters or leaves an issue state. State belongs to each editor because two tabs can have independent diagnostics. The term ``issues`` deliberately includes Ruff warnings, errors, and informational diagnostics, matching the previous UI intent.

#### REPLACE `MainWindow._restart_ruff`

**File:** `main.py`. **Baseline:** lines 740–769. Replace the entire named definition, including any decorator. Stop before `_on_editor_cursor_changed` and keep that following definition.

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
        if hasattr(self, "features"):
            self.features.environment_changed()

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

**Responsibility:** Replace the shared Ruff server after interpreter/workspace changes. Every open Python controller is reconnected to the new shared client. The old client then performs its asynchronous LSP shutdown. No editor owns a separate Ruff process.

#### REPLACE `MainWindow._on_editor_cursor_changed`

**File:** `main.py`. **Baseline:** lines 771–775. Replace the entire named definition, including any decorator. Stop before `set_up_menu` and keep that following definition.

````python
    def _on_editor_cursor_changed(self, editor, line: int, column: int):
        """Update the status bar only for the focused editor."""
        if editor is not self.current_editor():
            return
        self.update_cursor_position(line, column)
        if hasattr(self, "features"):
            self.features.cursor_changed(editor)
````

**Responsibility:** Update the status bar only for the focused editor.

#### REPLACE `MainWindow.set_up_menu`

**File:** `main.py`. **Baseline:** lines 777–1050. Replace the entire named definition, including any decorator. Stop before `split_current_editor_right` and keep that following definition.

````python
    def set_up_menu(self):
        """Register the existing editor actions and persistent shortcut IDs."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        new_file = file_menu.addAction("New")
        new_file.setShortcut("Ctrl+N")
        new_file.setShortcutContext(Qt.ApplicationShortcut)
        new_file.triggered.connect(self.new_file)

        open_file = file_menu.addAction("Open File")
        open_file.setShortcut("Ctrl+O")
        open_file.setShortcutContext(Qt.ApplicationShortcut)
        open_file.triggered.connect(self.open_file)

        # Open Recent submenu
        # addMenu returns a QMenu object. We store it as an instance
        # variable so we can rebuild it when the recent files list changes.
        self.recent_menu = file_menu.addMenu("Open Recent")
        self._update_recent_menu()

        open_folder = file_menu.addAction("Open Folder")
        open_folder.setShortcut("Ctrl+K")
        open_folder.setShortcutContext(Qt.ApplicationShortcut)
        open_folder.triggered.connect(self.open_folder)

        file_menu.addSeparator()
        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.setShortcutContext(Qt.ApplicationShortcut)
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save As")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.setShortcutContext(Qt.ApplicationShortcut)
        save_as.triggered.connect(self.save_as)

        save_all_action = file_menu.addAction("Save All")
        save_all_action.setShortcut("Ctrl+Shift+A")
        save_all_action.setShortcutContext(Qt.ApplicationShortcut)
        save_all_action.triggered.connect(self.save_all)

        close_all_action = file_menu.addAction("Close All")
        close_all_action.setShortcut("Ctrl+Shift+W")
        close_all_action.setShortcutContext(Qt.ApplicationShortcut)
        close_all_action.triggered.connect(self._close_all_tabs)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        undo_action = edit_menu.addAction("Undo")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setShortcutContext(Qt.ApplicationShortcut)
        undo_action.triggered.connect(self.undo)

        redo_action = edit_menu.addAction("Redo")
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.setShortcutContext(Qt.ApplicationShortcut)
        redo_action.triggered.connect(self.redo)

        edit_menu.addSeparator()

        cut_action = edit_menu.addAction("Cut")
        cut_action.setShortcut("Ctrl+X")
        cut_action.setShortcutContext(Qt.ApplicationShortcut)
        cut_action.triggered.connect(self.cut)

        copy_action = edit_menu.addAction("Copy")
        copy_action.setShortcut("Ctrl+C")
        copy_action.setShortcutContext(Qt.ApplicationShortcut)
        copy_action.triggered.connect(self.copy)

        paste_action = edit_menu.addAction("Paste")
        paste_action.setShortcut("Ctrl+V")
        paste_action.setShortcutContext(Qt.ApplicationShortcut)
        paste_action.triggered.connect(self.paste)

        edit_menu.addSeparator()

        select_all_action = edit_menu.addAction("Select All")
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setShortcutContext(Qt.ApplicationShortcut)
        select_all_action.triggered.connect(self.select_all)

        delete_line_action = edit_menu.addAction("Delete Line")
        delete_line_action.setShortcut("Ctrl+Shift+K")
        delete_line_action.setShortcutContext(Qt.ApplicationShortcut)
        delete_line_action.triggered.connect(self.delete_line)

        edit_menu.addSeparator()

        find_action = edit_menu.addAction("Find")
        find_action.setShortcut("Ctrl+F")
        find_action.setShortcutContext(Qt.ApplicationShortcut)
        find_action.triggered.connect(self.show_find_bar)

        replace_action = edit_menu.addAction("Replace")
        replace_action.setShortcut("Ctrl+H")
        replace_action.setShortcutContext(Qt.ApplicationShortcut)
        replace_action.triggered.connect(self.show_replace_bar)

        edit_menu.addSeparator()

        goto_action = edit_menu.addAction("Go to Line")
        goto_action.setShortcut("Ctrl+G")
        goto_action.setShortcutContext(Qt.ApplicationShortcut)
        goto_action.triggered.connect(self.goto_line)

        edit_menu.addSeparator()

        toggle_comment_action = edit_menu.addAction("Toggle Comment")
        toggle_comment_action.setShortcut("Ctrl+1")
        toggle_comment_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_comment_action.triggered.connect(self.toggle_comment)

        edit_menu.addSeparator()
        goto_definition_action = edit_menu.addAction("Go to Definition")
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
        run_file_action.setShortcut("F5")
        run_file_action.setShortcutContext(Qt.ApplicationShortcut)
        run_file_action.triggered.connect(self.run_current_file)

        run_with_args_action = run_menu.addAction("Run with Arguments")
        run_with_args_action.setShortcut("Shift+F5")
        run_with_args_action.setShortcutContext(Qt.ApplicationShortcut)
        run_with_args_action.triggered.connect(self.run_with_arguments)

        run_selection_action = run_menu.addAction("Run Selection")
        run_selection_action.setShortcut("Ctrl+Return")
        run_selection_action.setShortcutContext(Qt.ApplicationShortcut)
        run_selection_action.triggered.connect(self.run_selection)

        stop_action = run_menu.addAction("Stop")
        stop_action.setShortcut("F6")
        stop_action.setShortcutContext(Qt.ApplicationShortcut)
        stop_action.triggered.connect(self.python_runner.stop)

        run_menu.addSeparator()

        interpreter_action = run_menu.addAction("Choose Interpreter...")
        interpreter_action.triggered.connect(self.choose_interpreter)

        # Viewmenu for toggling the Sidebar

        view_menu = self.menuBar().addMenu("View")

        toggle_sidebar_action = view_menu.addAction("Toggle Sidebar")
        toggle_sidebar_action.setShortcut("Ctrl+B")
        toggle_sidebar_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)

        toggle_preview_action = view_menu.addAction("Toggle Preview")
        toggle_preview_action.setShortcut("Ctrl+J")
        toggle_preview_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_preview_action.triggered.connect(self.toggle_preview)

        toggle_console_action = view_menu.addAction("Toggle Console")
        toggle_console_action.setShortcut("Ctrl+Shift+-")
        toggle_console_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_console_action.triggered.connect(self.toggle_console)

        toggle_terminal_action = view_menu.addAction("Toggle Terminal")
        toggle_terminal_action.setShortcut("Ctrl+Shift+]")
        toggle_terminal_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_terminal_action.triggered.connect(self.toggle_terminal)

        view_menu.addSeparator()

        split_right_action = view_menu.addAction("Split Right")
        split_right_action.setShortcut("Ctrl+Alt+Right")
        split_right_action.setShortcutContext(Qt.ApplicationShortcut)
        split_right_action.triggered.connect(self.split_current_editor_right)

        unsplit_action = view_menu.addAction("Unsplit")
        unsplit_action.setShortcut("Ctrl+Alt+Left")
        unsplit_action.setShortcutContext(Qt.ApplicationShortcut)
        unsplit_action.triggered.connect(self.unsplit_active_group)

        view_menu.addSeparator()

        fullscreen_editor = view_menu.addAction("Fullscreen")
        fullscreen_editor.setShortcut("F11")
        fullscreen_editor.setShortcutContext(Qt.ApplicationShortcut)
        fullscreen_editor.triggered.connect(self._show_full_screen)

        starting_window_size = view_menu.addAction("Startup Window Size")
        starting_window_size.setShortcut("Shift+F11")
        starting_window_size.setShortcutContext(Qt.ApplicationShortcut)
        starting_window_size.triggered.connect(self._startup_window_size)

        view_menu.addSeparator()

        git_refresh_action = view_menu.addAction("Refresh Git Status")
        git_refresh_action.setShortcut("Ctrl+Shift+G")
        git_refresh_action.setShortcutContext(Qt.ApplicationShortcut)
        git_refresh_action.triggered.connect(self._refresh_git_state)
        
        toggle_git_history_action = view_menu.addAction("Toggle Git History")
        toggle_git_history_action.setShortcut("Ctrl+Alt+G")
        toggle_git_history_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_git_history_action.triggered.connect(self._toggle_git_history)

        settings_action = view_menu.addAction("Settings")
        settings_action.setShortcut("Ctrl+Alt+S")
        settings_action.setShortcutContext(Qt.ApplicationShortcut)
        settings_action.triggered.connect(self.open_settings)

        hacker_action = view_menu.addAction("Hacker-Mode")
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
        check_updates_action.triggered.connect(lambda: self.check_for_updates(manual=True))

        # Stable IDs are independent of the displayed action text and survive
        # renaming a menu or translating its label. Reuse these exact QActions.
        self.command_actions = {
            "file.open": open_file,
            "file.save": save_file,
            "file.save_as": save_as,
            "file.save_all": save_all_action,
            "edit.undo": undo_action,
            "edit.redo": redo_action,
            "edit.find": find_action,
            "edit.replace": replace_action,
            "edit.goto_line": goto_action,
            "run.file": run_file_action,
            "run.stop": stop_action,
            "view.sidebar": toggle_sidebar_action,
            "view.terminal": toggle_terminal_action,
            "view.console": toggle_console_action,
        }
        try:
            from code_settings.keyboard_shortcuts import Shortcuts
            overrides = json.loads(self.settings.value("shortcuts", "{}", type=str))
            Shortcuts(self.settings).bind(self.command_actions, overrides)
        except (TypeError, ValueError) as error:
            self.statusBar().showMessage(f"Invalid shortcut settings: {error}", 5000)
````

**Responsibility:** Register the existing editor actions and persistent shortcut IDs.

#### REPLACE `MainWindow.toggle_preview`

**File:** `main.py`. **Baseline:** lines 1286–1296. Replace the entire named definition, including any decorator. Stop before `toggle_console` and keep that following definition.

````python
    def toggle_preview(self):
        """Hide/Show the Markdown preview panel."""
        currently_visible = self.preview.isVisible()
        self.preview.setVisible(not currently_visible)

        if currently_visible:
            # Hiding preview: give all space to sidebar + editor
            self.hs_split.setSizes([250, 850, 0])
        else:
            # Showing preview: restore even split
            self.hs_split.setSizes([250, 575, 575])
            self.render_preview()
````

**Responsibility:** Hide/Show the Markdown preview panel.

#### REPLACE `MainWindow._apply_settings`

**File:** `main.py`. **Baseline:** lines 1507–1530. Replace the entire named definition, including any decorator. Stop before `set_hacker_mode` and keep that following definition.

````python
    def _apply_settings(self, settings: dict):
        """
        Push a settings dictionary onto every open editor.

        MultiTabView.all_editors() yields the editors of ALL tab groups
        (both halves of a split view), so one loop covers everything.
        The settings are also cached on self so new tabs opened later
        can inherit them via _apply_editor_settings().
        """
        self._current_settings = settings

        # The dock is created after startup settings; later changes retheme it.
        if hasattr(self, "git_graph"):
            self._apply_git_history_theme(self._theme_path(settings.get("theme")))

        for editor in self.tab_view.all_editors():
            self._apply_editor_settings(editor, settings)

        if settings["interpreter"]:
            previous = self.python_runner.interpreter
            self.python_runner.set_interpreter(settings["interpreter"])
            self.statusBar().showMessage(f"Interpreter: {self.python_runner.interpreter}", 3000)
            if previous != settings["interpreter"] and hasattr(self, "ruff_lsp_client"):
                self._restart_ruff(settings["interpreter"])

        if hasattr(self, "features"):
            # Regenerate once from the base stylesheet after a theme/settings
            # change. Appending to the current style duplicates old rules.
            self.apply_design_density(
                self.settings.value("ui_density", "comfortable", type=str))
````

**Responsibility:** Push a settings dictionary onto every open editor. MultiTabView.all_editors() yields the editors of ALL tab groups (both halves of a split view), so one loop covers everything. The settings are also cached on self so new tabs opened later can inherit them via _apply_editor_settings().

#### REPLACE `MainWindow.set_new_tab`

**File:** `main.py`. **Baseline:** lines 1749–1816. Replace the entire named definition, including any decorator. Stop before `get_frame` and keep that following definition.

````python
    def set_new_tab(
            self,
            path: Path,
            is_new_file=False,
            target_group=None,
            is_python_file=None,
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
            self.tab_view.focus_editor(existing)
            return existing

        try:
            if self.is_binary(path):
                self.statusBar().showMessage("Cannot open binary file", 2_000)
                return None

            # Keep the logical path on the tab, but read/write the target when
            # the logical path is a symlink so saving does not replace the link.
            target = save_target(path)
            raw = target.read_bytes()
            from code_settings.large_file_policy import file_size_mode
            large_file = file_size_mode(len(raw))
            has_bom = raw.startswith(UTF8_BOM)
            text = raw.decode("utf-8-sig")
        except (OSError, UnicodeDecodeError) as error:
            QMessageBox.critical(self, "Open File", f"Could not open '{path}':\n{error}")
            return None

        editor = self.get_editor(path=path, is_python_file=is_python_file)
        # Optional analysis/preview can pause on this tab; saving never does.
        editor._large_file_mode = large_file
        editor._large_file_override = False
        editor._utf8_bom = has_bom
        editor._disk_digest = hashlib.sha256(raw).digest()
        editor._disk_text = text
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
        if hasattr(self, "features"):
            self.features.show_empty()
        self.tab_view.set_editor_tooltip(editor, str(path.absolute()))

        self.current_file = path
        self._add_to_recent_files(str(path))
        if isinstance(editor, PythonEditor):
            self._update_outline()
        else:
            self.outline_tree.clear()
        return editor
````

**Responsibility:** Open one UTF-8 document without corrupting or duplicating it. Binary probing, symlink resolution, byte reading, and strict decoding are one I/O transaction. Every expected filesystem/encoding failure is converted to a user-visible dialog instead of escaping a Qt slot.

#### REPLACE `MainWindow.set_up_body`

**File:** `main.py`. **Baseline:** lines 1837–2015. Replace the entire named definition, including any decorator. Stop before `_goto_symbol` and keep that following definition.

````python
    def set_up_body(self):
        """Build the editor layout and sidebar navigation/action icons."""
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.Shape.NoFrame)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body_frame.setLayout(body)

        self.tab_view = MultiTabView(self)
        self.tab_view.setContentsMargins(0, 0, 0, 0)
        self.tab_view.currentEditorChanged.connect(self._on_current_editor_changed)
        self.tab_view.closeEditorRequested.connect(self.close_editor)
        # BUGFIX: the tab context menu was never wired up - connect it here.
        self.tab_view.tabContextMenuRequested.connect(self._show_tab_context_menu)

        # editor_container = QWidget()
        # editor_layout = QStackedWidget(editor_container)

        self.preview = QWebEngineView()

        # --- Setup for the Sidebar
        self.side_bar = QFrame()
        self.side_bar.setFrameShape(QFrame.Shape.StyledPanel)
        self.side_bar.setFrameShadow(QFrame.Shadow.Plain)
        self.side_bar.setStyleSheet(f"""
            background-color: {"#1e1f22"};
        """)

        side_bar_layout = QVBoxLayout()
        side_bar_layout.setContentsMargins(5, 15, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        # --- Setup for labels
        self.sidebar_labels = {}

        folder_label = self.get_sidebar_label(resource_path("icons/folder-active.svg"), "folder")
        self.sidebar_labels["folder"] = folder_label
        side_bar_layout.addWidget(folder_label)

        search_label = self.get_sidebar_label(resource_path("icons/search.svg"), "search")
        self.sidebar_labels["search"] = search_label
        side_bar_layout.addWidget(search_label)
        self.side_bar.setLayout(side_bar_layout)

        outline_label = self.get_sidebar_label(resource_path("icons/outline.svg"), "outline")
        self.sidebar_labels["outline"] = outline_label
        side_bar_layout.addWidget(outline_label)

        terminal_label = self.get_sidebar_label(resource_path("icons/terminal.svg"), "terminal")
        self.sidebar_labels["terminal"] = terminal_label
        side_bar_layout.addWidget(terminal_label)
        
        # Reuse the existing assets; these are actions, not side-panel pages.
        for name in ("console", "settings"):
            label = self.get_sidebar_label(resource_path(f"icons/{name}.svg"), name)
            self.sidebar_labels[name] = label
            side_bar_layout.addWidget(label)

        self.outline_tree = CodeOutlineTree()
        self.outline_tree.symbol_clicked.connect(self._goto_symbol)

        self.outline_frame = self.get_frame()
        outline_layout = QVBoxLayout()
        outline_layout.setContentsMargins(0, 0, 0, 0)
        outline_layout.setSpacing(0)

        outline_label = QLabel("Outline")
        outline_label.setStyleSheet("color: #636d83; padding: 4px 8px; font-size: 12px;")
        outline_layout.addWidget(outline_label)
        outline_layout.addWidget(self.outline_tree)
        self.outline_frame.setLayout(outline_layout)

        # split view
        self.hs_split = QSplitter(Qt.Orientation.Horizontal)

        # --- Frame and layout to hold the tree view (FILE MANAGER)
        self.file_manager_frame = self.get_frame()

        self.file_manager_layout = QVBoxLayout()
        self.file_manager_layout.setContentsMargins(0, 0, 0, 0)
        self.file_manager_layout.setSpacing(0)
        self.file_manager = FileManager(
            set_new_tab=self.set_new_tab,
            main_window=self,
            parent=self,
        )

        # setup layout
        self.file_manager_layout.addWidget(self.file_manager)
        self.file_manager_frame.setLayout(self.file_manager_layout)

        # search manager
        self.search_frame = self.get_frame()

        search_layout = QVBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_layout.setContentsMargins(0, 10, 0, 0)
        search_layout.setSpacing(0)

        search_input = QLineEdit()
        search_input.setPlaceholderText("Search")
        search_input.setFont(self.window_font)

        self.search_checkbox = QCheckBox("Include hidden module folders")
        self.search_regex_checkbox = QCheckBox("Regex")
        self.search_case_checkbox = QCheckBox("Case sensitive")
        for checkbox in (
            self.search_checkbox,
            self.search_regex_checkbox,
            self.search_case_checkbox,
        ):
            checkbox.setFont(self.window_font)

        self.search_worker = SearchWorker()
        self.search_worker.results_ready.connect(self.search_finished)
        self.search_worker.search_error.connect(self.search_failed)

        def request_search():
            self.search_worker.update(
                search_input.text(),
                self.file_manager.model.rootPath(),
                self.search_checkbox.isChecked(),
                self.search_regex_checkbox.isChecked(),
                self.search_case_checkbox.isChecked(),
            )

        search_input.textChanged.connect(lambda _text: request_search())
        self.search_checkbox.toggled.connect(lambda _on: request_search())
        self.search_regex_checkbox.toggled.connect(lambda _on: request_search())
        self.search_case_checkbox.toggled.connect(lambda _on: request_search())

        self.search_list_view = QListWidget()
        self.search_list_view.setFont(QFont("sans-serif", 13))
        self.search_list_view.setStyleSheet("""
        QListWidget {
            background-color: #21252b;
            border-radius: 5px;
            border: 1px solid #D3D3D3;
            padding: 5px;
            color: #D3D3D3;
        }
        """)

        self.search_list_view.itemClicked.connect(self.search_list_view_clicked)

        search_layout.addWidget(self.search_checkbox)
        search_layout.addWidget(self.search_regex_checkbox)
        search_layout.addWidget(self.search_case_checkbox)
        search_layout.addWidget(search_input)
        search_layout.addSpacerItem(QSpacerItem(5, 5, QSizePolicy.Minimum, QSizePolicy.Minimum))

        search_layout.addWidget(self.search_list_view)
        self.search_frame.setLayout(search_layout)

        # --- Side panel: QStackedWidget so only one panel is visible at a time ---
        self.side_panel = QStackedWidget()
        self.side_panel.setMinimumWidth(280)  # was 200 — too narrow
        self.side_panel.setMaximumWidth(450)  # was 400 — give more room
        self.side_panel.addWidget(self.file_manager_frame)
        self.side_panel.addWidget(self.search_frame)
        self.side_panel.addWidget(self.outline_frame)

        body.addWidget(self.side_bar)
        self.hs_split.addWidget(self.side_panel)
        self.hs_split.addWidget(self.tab_view)
        self.hs_split.addWidget(self.preview)
        self.hs_split.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hs_split.setSizes([300, 550, 550])
        body.addWidget(self.hs_split)
        body_frame.setLayout(body)

        self.setCentralWidget(body_frame)
````

**Responsibility:** Build the editor layout and sidebar navigation/action icons.

#### REPLACE `MainWindow.close_editor`

**File:** `main.py`. **Baseline:** lines 2155–2185. Replace the entire named definition, including any decorator. Stop before `_dispose_editor` and keep that following definition.

````python
    def close_editor(self, editor):
        """Resolve unsaved changes and retire one tab's owned workers."""
        if editor is None:
            return

        if editor in self._dirty_editors:
            path = getattr(editor, "path", None)
            name = path.name if path is not None else "Untitled"

            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save Changes to '{name}'?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if reply == QMessageBox.Cancel:
                return False

            if reply == QMessageBox.Save:
                self.tab_view.focus_editor(editor)
                if not self.save_file():
                    return False
            elif reply == QMessageBox.Discard and hasattr(self, "features"):
                # Only an explicit discard may destroy the unsaved snapshot.
                self.features.discarded(editor)

        self._dirty_editors.discard(editor)
        self.tab_view.remove_editor(editor)
        if hasattr(self, "features"):
            QTimer.singleShot(0, self.features.show_empty)
        
        self._dispose_editor(editor)

        self.render_preview()
        return True
````

**Responsibility:** Resolve unsaved changes and retire one tab's owned workers.

#### REPLACE `MainWindow._dispose_editor`

**File:** `main.py`. **Baseline:** lines 2187–2198. Replace the entire named definition, including any decorator. Stop before `_finalize_retired_editor` and keep that following definition.

````python
    def _dispose_editor(self, editor):
        """Delete now, or retain a Python editor until its workers finish."""
        if hasattr(self, "features"):
            self.features.retire(editor)
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

**Responsibility:** Delete now, or retain a Python editor until its workers finish.

#### REPLACE `MainWindow.show_hide_tab`

**File:** `main.py`. **Baseline:** lines 2306–2370. Replace the entire named definition, including any decorator. Stop before `tree_view_context_menu` and keep that following definition.

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
                self.terminal_dock.ensure().output.setFocus()
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
            if hasattr(self, "features"):
                self.features.refresh_presentations()

        for name in ("folder", "search", "outline"):
            self._set_sidebar_icon(name, name == type_)
        # Restore splitter sizes if the side panel was hidden (width 0)
        sizes = self.hs_split.sizes()
        if sizes and sizes[0] == 0:
            self.hs_split.setSizes([300, 550, 550])
````

**Responsibility:** Dispatch left-clicks to tool actions or the three sidebar pages.

#### REPLACE `MainWindow.new_file`

**File:** `main.py`. **Baseline:** lines 2374–2384. Replace the entire named definition, including any decorator. Stop before `open_file` and keep that following definition.

````python
    def new_file(self, target_group=None):
        """Create an untitled editor in the active group."""

        editor = self.get_editor()
        self._connect_editor(editor)

        self.tab_view.add_editor(editor, "Untitled", target_group)
        if hasattr(self, "features"):
            self.features.show_empty()
        self.current_file = None
        self.statusBar().showMessage("Created new file", 3000)

        return editor
````

**Responsibility:** Create an untitled editor in the active group.

#### REPLACE `MainWindow.open_folder`

**File:** `main.py`. **Baseline:** lines 2405–2431. Replace the entire named definition, including any decorator. Stop before `_run_ruff_before_save` and keep that following definition.

````python
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
        if hasattr(self, "features"):
            self.features.show_empty()
        self.statusBar().showMessage(f"Opened {selected}", 2000)
````

**Responsibility:** Open a chosen/recent project and retarget live services without forcing a PTY.

#### REPLACE `MainWindow._save_editor_to_path`

**File:** `main.py`. **Baseline:** lines 2510–2589. Replace the entire named definition, including any decorator. Stop before `save_file` and keep that following definition.

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
                actual = disk_digest(target)
            except OSError as error:
                QMessageBox.critical(self, "Save File", str(error))
                return False
            if expected is not None and actual != expected:
                try:
                    disk_bytes = target.read_bytes()
                    disk_bytes.decode("utf-8-sig")
                except (OSError, UnicodeError) as error:
                    QMessageBox.warning(self, "External change", str(error))
                    return False
                # Keep is the only decision that proceeds with this save.
                if self.features.external_conflict(editor, disk_bytes) != "overwrite":
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
            # Snapshot the current disk version; history is recorded only
            # after the main atomic replacement has succeeded.
            previous_bytes = target.read_bytes() if target.exists() else None
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
        editor._disk_text = data.decode("utf-8-sig")
        self.mark_editor_clean(editor)
        if hasattr(self, "features"):
            self.features.saved(editor, logical_path, previous_bytes)
        return True
````

**Responsibility:** Format and atomically save without losing links or newer disk data.

#### REPLACE `MainWindow.save_as`

**File:** `main.py`. **Baseline:** lines 2619–2672. Replace the entire named definition, including any decorator. Stop before `_terminal_view_has_focus` and keep that following definition.

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
        if owner is not None and owner is not editor:
            QMessageBox.warning(self, "Save As", "That file is already open in another tab.")
            self.tab_view.focus_editor(owner)
            return False

        # The dialog confirmed replacement. Do not compare the destination to
        # the digest of the tab's previous path.
        if not self._save_editor_to_path(editor, path, check_external_change=False):
            return False

        editor.path = path
        editor.full_path = path.absolute()
        editor._revision = getattr(editor, "_revision", 0) + 1
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
            if not converted and editor.ruff_lsp is not None:
                editor.ruff_lsp.relocate(path)
            editor.auto_completer.file_path = str(editor.full_path)

        self.mark_editor_clean(editor)
        self._add_to_recent_files(str(path))
        if hasattr(self, "features"):
            self.features.current_changed(self.current_editor())
        self.statusBar().showMessage(f"Saved {path.name}", 2_000)
        return True
````

**Responsibility:** Save to a user-confirmed path and update the tab's editor type. The native file dialog owns the intentional overwrite confirmation. The source tab's disk digest belongs to its old path and must never be compared with bytes at the new destination.

#### REPLACE `MainWindow._on_current_editor_changed`

**File:** `main.py`. **Baseline:** lines 2740–2763. Replace the entire named definition, including any decorator. Stop before `change_editor_python` and keep that following definition.

````python
    def _on_current_editor_changed(self, editor):
        """Refresh MainWindow state when focus moved between editors."""
        if editor is None:
            self.current_file = None
            self.cursor_pos_label.setText("")
            self.word_count_label.setText("")
            if hasattr(self, "features"):
                self.features.current_changed(None)
            return

        self.current_file = getattr(editor, "path", None)

        line, column = editor.getCursorPosition()
        self.update_cursor_position(line, column)
        self.update_word_count()

        if isinstance(editor, PythonEditor):
            self._update_outline()
        else:
            self.outline_tree.clear()

        if isinstance(editor, MarkdownEditor):
            self.preview.show()
            self.render_preview()
        else:
            self.preview.hide()

        if hasattr(self, "features"):
            self.features.current_changed(editor)
````

**Responsibility:** Refresh MainWindow state when focus moved between editors.

#### REPLACE `MainWindow.render_preview`

**File:** `main.py`. **Baseline:** lines 2797–2809. Replace the entire named definition, including any decorator. Stop before `_on_preview_loaded` and keep that following definition.

````python
    def render_preview(self):
        """Render only sanitized Markdown into the already loaded shell."""
        editor = self.current_editor()

        if not isinstance(editor, MarkdownEditor) or not self._preview_ready:
            return
        if not self.preview.isVisible():
            return
        if (editor.length() > 2_000_000
                and not getattr(editor, "_large_file_override", False)):
            return

        started = time.perf_counter()
        safe_body = self._render_markdown_safely(editor.text())
        if hasattr(self, "features"):
            self.features.timings.observe("preview.convert", time.perf_counter() - started)
        # json.dumps creats a valid JavaScript string literal. Never interpolate
        # document text directly into JavaScript source.
        payload = json.dumps(safe_body)
        script = (
            "(() => { const previous = window.scrollY;"
            f'document.getElementById("content").innerHTML = {payload};'
            "window.scrollTo(0, previous); })();"
        )
        web_started = time.perf_counter()
        self.preview.page().runJavaScript(
            script,
            lambda _result: (
                self.features.timings.observe(
                    "preview.webengine", time.perf_counter() - web_started
                ) if hasattr(self, "features") else None
            ),
        )
````

**Responsibility:** Render only sanitized Markdown into the already loaded shell.

#### REPLACE `MainWindow._convert_editor`

**File:** `main.py`. **Baseline:** lines 2836–2900. Replace the entire named definition, including any decorator. Stop before `_swap_editor` and keep that following definition.

````python
    def _convert_editor(self, old, EditorClass):
        """Replace one tab's editor class without leaking the old instance.

        Document/path/display state is copied to the new editor. Dirty-set
        migration is conditional, but retirement of the old widget is always
        required because clean Python editors also own workers and LSP signals.
        """
        if old is None or isinstance(old, EditorClass):
            return old
        group = self.tab_view.group_for_editor(old)
        if group is None:
            return None

        index = group.indexOf(old)
        was_current = old is self.current_editor()
        previous_current = group.currentWidget()
        title = group.tabText(index)
        tooltip = group.tabToolTip(index)
        icon = group.tabIcon(index)
        text = old.text()
        path = getattr(old, "path", None)
        was_dirty = old in self._dirty_editors
        line, column = old.getCursorPosition()
        selection = old.getSelection()
        first_visible = old.firstVisibleLine()

        new_editor = self.get_editor(path=path, is_python_file=(EditorClass is PythonEditor))
        new_editor.setTextSafely(text)
        new_editor._disk_text = getattr(old, "_disk_text", "")
        new_editor._utf8_bom = getattr(old, "_utf8_bom", False)
        new_editor._disk_digest = getattr(old, "_disk_digest", None)
        new_editor._save_target = getattr(old, "_save_target", path)
        new_editor._large_file_mode = getattr(old, "_large_file_mode", False)
        new_editor._large_file_override = getattr(old, "_large_file_override", False)
        new_editor._revision = getattr(old, "_revision", 0)
        new_editor.setEolMode(old.eolMode())
        self._connect_editor(new_editor)
        # Conversion changes widget class, not document/recovery identity.
        new_editor._recovery_id = old._recovery_id

        # Direct insertion must reproduce MultiTabView.add_editor's focus
        # wiring because this operation replaces an existing tab in-place.
        new_editor.installEventFilter(self.tab_view)
        if hasattr(new_editor, "focused"):
            new_editor.focused.connect(self.tab_view._on_editor_focused)

        group.blockSignals(True)
        group.removeTab(index)
        group.insertTab(index, new_editor, icon, title)
        group.setTabToolTip(index, tooltip)
        if was_current:
            group.setCurrentIndex(index)
        elif previous_current is not None and previous_current is not old:
            group.setCurrentWidget(previous_current)
        group.blockSignals(False)

        if was_dirty:
            self._dirty_editors.discard(old)
            self._dirty_editors.add(new_editor)

        # Always shut down and retire the removed editor. Keeping this outside
        # the dirty branch fixes the clean-conversion worker/widget leak.
        self._dispose_editor(old)

        new_editor.setCursorPosition(line, column)
        if selection[0] >= 0:
            new_editor.setSelection(*selection)
        new_editor.setFirstVisibleLine(first_visible)
        if was_current:
            self.tab_view.focus_editor(new_editor)
        return new_editor
````

**Responsibility:** Replace one tab's editor class without leaking the old instance. Document/path/display state is copied to the new editor. Dirty-set migration is conditional, but retirement of the old widget is always required because clean Python editors also own workers and LSP signals.

#### REPLACE `MainWindow._background_work_running`

**File:** `main.py`. **Baseline:** lines 3101–3144. Replace the entire named definition, including any decorator. Stop before `_finish_pending_close` and keep that following definition.

````python
    def _background_work_running(self) -> bool:
        """Return whether an asynchronous component is still shutting down.

        Returns:
            True while an editor retirement, Git scan, project search, Python
            run, Ruff process, or terminal PTY worker remains active.

        The method is polled by `_finish_pending_close()` through QTimer. It
        must only inspect state and must never block the GUI thread.
        """
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
        features = getattr(self, "features", None)
        

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
            # A QObject with queued worker results stays alive until its
            # own GUI-thread receive slot drains every completion.
            or (features is not None and features.analysis.is_running())
            or (features is not None and features.hashes.is_running())
            or (features is not None and features.test_session.is_running())
            or (
                features is not None
                and features.runner.process.state() != QProcess.NotRunning
            )
        )
````

**Responsibility:** Return whether an asynchronous component is still shutting down. Returns:     True while an editor retirement, Git scan, project search, Python     run, Ruff process, or terminal PTY worker remains active. The method is polled by `_finish_pending_close()` through QTimer. It must only inspect state and must never block the GUI thread.

#### REPLACE `MainWindow.closeEvent`

**File:** `main.py`. **Baseline:** lines 3153–3206. Replace the entire named definition, including any decorator. Stop before `save_session` and keep that following definition.

````python
    def closeEvent(self, event):
        """Prompt once, stop services, and defer final close until workers exit."""
        if getattr(self, "_close_ready", False):
            event.accept()
            return super().closeEvent(event)

        if not getattr(self, "_close_prompts_complete", False):
            for editor in list(self.tab_view.all_editors()):
                if editor not in self._dirty_editors:
                    continue
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
                if reply == QMessageBox.Discard:
                    self.features.discarded(editor)
                    self._dirty_editors.discard(editor)
            self._close_prompts_complete = True
            self.save_session()

        # Stop snapshots only after every Save/Discard/Cancel decision settled.
        self.features.shutdown()
        self.features.runner.stop()
        self.features.test_session.stop()

        for editor in list(self.tab_view.all_editors()):
            self.tab_view.remove_editor(editor)
            self._dispose_editor(editor)

        if self.terminal is not None:
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

**Responsibility:** Prompt once, stop services, and defer final close until workers exit.

#### ADD methods to `MainWindow`

**File:** `main.py`. Insert the following methods **inside `MainWindow`, after `_show_update_dialog`** (baseline ending line 3422), before the class ends. Preserve four-space method indentation. Each method is new; add it once.

````python
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
````

<a id="integration-python-editor-pythoneditor-py"></a>
### Integrate `python_editor/pythoneditor.py`

#### Imports and module-level state

**Insert after** `from code_inteligence.indentation_helper import indentation_for_new_line` (baseline line 17), at module scope, before the next existing statement. Do not duplicate imports already added.

````python
from code_inteligence.references_finder import ReferencesFinder
from code_inteligence.pair_handling import pair_key, empty_pair_backspace
````

**Class docstring:** immediately after `class PythonEditor(...):` (baseline line 32), before its first attribute or method, insert at four-space indentation:

````python
    """Edit Python with byte-correct input, shared analysis providers, and Ruff diagnostics."""
````

#### REPLACE `PythonEditor.__init__`

**File:** `python_editor/pythoneditor.py`. **Baseline:** lines 37–179. Replace the entire named definition, including any decorator. Stop before `_apply_theme_editor_style` and keep that following definition.

````python
    def __init__(self, parent=None, path: Path = None, is_python_file: bool = True, ruff_lsp_client = None):
        """Configure editing behavior and connect providers to this document identity."""
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
            self.signature_helper = SignatureHelper(self)
            self.signature_helper.signature_ready.connect(self._on_signature_ready)
            self.signature_helper.signature_empty.connect(self._on_signature_empty)

            self.hover_helper = HoverHelper(self)
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
                str(self.full_path) if self.full_path else None, self._api, self
            )
            self.auto_completer.completions_ready.connect(self._apply_completions)
            self.auto_completer.error.connect(self._handle_completion_error)

            self.setLexer(self.py_lexer)
        else:
            # No lexer in this mode yet (tab not converted): neutral defaults.
            # Once a lexer attaches, _apply_theme_editor_style takes over.
            self.setPaper(QColor("#1e1f22"))
            self.setColor(QColor("#abb2bf"))

        self.references_finder = ReferencesFinder(self)
        self.definition_finder = DefinitionFinder(self)
        self.definition_finder.definition_found.connect(self._on_definition_found)
        self.definition_finder.definition_not_found.connect(self._on_definition_not_found)
        self.definition_finder.error.connect(self._on_definition_error)
        self.textChanged.connect(self._invalidate_analysis)

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
````

**Responsibility:** Configure editing behavior and connect providers to this document identity.

#### REPLACE `PythonEditor.keyPressEvent`

**File:** `python_editor/pythoneditor.py`. **Baseline:** lines 402–459. Replace the entire named definition, including any decorator. Stop before `_dismiss_signature` and keep that following definition.

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
````

**Responsibility:** Handle editor shortcuts, indentation, and signature scheduling.

#### REPLACE `PythonEditor._cursorPositionChanged`

**File:** `python_editor/pythoneditor.py`. **Baseline:** lines 528–542. Replace the entire named definition, including any decorator. Stop before `_trigger_autocomplete` and keep that following definition.

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

**Responsibility:** Called when the cursor moves. Starts a debounce timer instead of immediately running Jedi analysis.

#### REPLACE `PythonEditor._analysis_workers`

**File:** `python_editor/pythoneditor.py`. **Baseline:** lines 568–576. Replace the entire named definition, including any decorator. Stop before `shutdown` and keep that following definition.

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

**Responsibility:** Return every per-editor QThread that must outlive the tab.

#### ADD methods to `PythonEditor`

**File:** `python_editor/pythoneditor.py`. Insert the following methods **inside `PythonEditor`, after `closeEvent`** (baseline ending line 612), before the class ends. Preserve four-space method indentation. Each method is new; add it once.

````python
    def _invalidate_analysis(self):
        """Invalidate every provider after edits, including stationary-caret changes."""
        for provider in self._analysis_workers():
            provider.invalidate()
        if self.length() > 2_000_000 and not getattr(self, "_large_file_override", False):
            self._autocomplete_timer.stop()
            if hasattr(self, "_api"):
                self._api.clear()
````

<a id="integration-markdown-editor-markdowneditor-py"></a>
### Integrate `markdown_editor/markdowneditor.py`

#### Imports and module-level state

**Insert after** `from markdown_editor.markdowncustomlexer import MarkdownCustomLexer` (baseline line 8), at module scope, before the next existing statement. Do not duplicate imports already added.

````python
from code_inteligence.pair_handling import pair_key, empty_pair_backspace
````

**Class docstring:** immediately after `class MarkdownEditor(...):` (baseline line 11), before its first attribute or method, insert at four-space indentation:

````python
    """Edit Markdown with matching pairs, themed syntax, and document lifecycle signals."""
````

#### REPLACE `MarkdownEditor.keyPressEvent`

**File:** `markdown_editor/markdowneditor.py`. **Baseline:** lines 90–94. Replace the entire named definition, including any decorator. Stop before `setTextSafely` and keep that following definition.

````python
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
````

**Responsibility:** Insert smart pairs while preserving the existing Ctrl+Space action.

<a id="integration-python-editor-custompythonlexer-py"></a>
### Integrate `python_editor/custompythonlexer.py`

#### Imports and module-level state

**Insert after** `from markdowneditor_assets import asset_path` (baseline line 12), at module scope, before the next existing statement. Do not duplicate imports already added.

````python
from python_editor.lexer_checkpoints import LexerCheckpoints
````

**Replace the native-import `try/except` block**, baseline lines 14–19, before `_resource_path`. The API version check falls back safely when an old extension remains installed.

````python
try:
    from python_editor.lexer_fast import style_chunk as _cython_style
    from python_editor.lexer_fast import compute_state_before as _cython_state
    from python_editor.lexer_fast import STATE_API
    _HAS_CYTHON = STATE_API == 2
except ImportError:
    _HAS_CYTHON = False
````

**Class docstring:** immediately after `class PyCustomLexer(...):` (baseline line 1096), before its first attribute or method, insert at four-space indentation:

````python
    """Style Python with matching native/fallback scanners and incremental state checkpoints."""
````

#### REPLACE `_py_compute_state`

**File:** `python_editor/custompythonlexer.py`. **Baseline:** lines 113–299. Replace the entire named definition, including any decorator. Stop before `_py_style_chunk` and keep that following definition.

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

**Responsibility:** Scan from byte 0 to target_pos and return the packed lexer state. ``snapshot`` restores all scanner locals at a safe line boundary. Optional ``checkpoints`` receives complete snapshots; packed style bits alone omit bracket and pending-definition state and must never be used to resume.

#### REPLACE `PyCustomLexer.styleText`

**File:** `python_editor/custompythonlexer.py`. **Baseline:** lines 1131–1172. Replace the entire named definition, including any decorator. Stop at the end of this definition; retain the surrounding class/module.

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
        features = getattr(self.editor.window(), "features", None)
        if features is not None:
            features.timings.observe("python-lexing", perf_counter() - began)
````

**Responsibility:** Style byte ranges using invalidated, complete prefix-state checkpoints. Both scanners expose the same resume protocol. Styling token generation remains unchanged; only the repeated prefix-state scan is shortened.

<a id="controller"></a>
### ADD `EditorFeatureController` to `main.py`

**Folder/file:** existing repository-root `main.py`; do not create a separate controller file. **Placement:** module scope, after the complete `MainWindow` class and immediately before `def main() -> int:`. The baseline `main()` anchor is given below. Paste the complete class once, with no extra indentation. `MainWindow.__init__` creates it after the base UI exists and before session restoration.

This class connects the feature modules to the existing window, owns timers and shared service adapters, and keeps document lifecycle decisions in the original MainWindow methods. Its docstrings explain every method; its comments explain the revision, write, and lifetime checks.

**Baseline insertion anchor:** `main.py` line 3424, immediately before `def main() -> int:`.

````python
class EditorFeatureController:
    """Wire shared services to MainWindow without replacing its ownership model."""

    def __init__(self, window):
        """Create user-data storage and optional panels after the base UI exists."""
        self.window = window
        root = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        self.recovery = RecoveryStore(root / "recovery")
        self.history = VersionStore(root / "history")
        self.timings = Timings(enabled=window.settings.value("performance_diagnostics", False, type=bool))
        self.layouts = Layouts(window)
        self.runner = ProcessPanel(window)
        self.run_output = LazyWidget(self._make_run_output)
        self.analysis = shared_analysis()
        self.analysis.measured.connect(self.timings.observe)
        self.analysis.ready.connect(self._analysis_ready)
        self.hashes = FileHashQueue(window)
        self.hashes.changed.connect(self._hash_ready)
        self.file_watcher = QFileSystemWatcher(window)
        self.file_watcher.fileChanged.connect(self._file_changed)
        self.file_watcher.directoryChanged.connect(self._directory_changed)
        self._watched_editors = {}
        self.tests = LazyWidget(self._make_tests)
        from python_editor.test_session import TestSession
        self.test_session = TestSession(window)
        self.preview = PreviewSchedule(window.render_preview, window)
        self.breadcrumb = Breadcrumb(self._jump, window)
        self._install_center()
        self.md_outline = MarkdownOutline(window)
        self.md_outline.activated_line.connect(lambda row: self._jump(row, 0))
        window.outline_frame.layout().addWidget(self.md_outline)
        self.md_outline.hide()
        self._install_status()
        self._install_menu()
        self._install_panels()
        from code_settings.keyboard_shortcuts import Shortcuts
        try:
            overrides = json.loads(window.settings.value("shortcuts", "{}", type=str))
            Shortcuts(window.settings).bind(window.command_actions, overrides)
        except (TypeError, ValueError) as error:
            window.statusBar().showMessage(f"Invalid shortcut settings: {error}", 5000)
        self._recovery_timer = QTimer(window)
        self._recovery_timer.setInterval(5000)
        self._recovery_timer.timeout.connect(self.flush_recovery)
        self._recovery_timer.start()
        window.apply_design_density(
            window.settings.value("ui_density", "comfortable", type=str))
        self.show_empty()

    def _install_center(self) -> None:
        """Wrap the existing central widget; do not rebuild tab groups."""
        window = self.window
        original = window.takeCentralWidget()
        self.stack = QStackedWidget(window)
        self.stack.addWidget(original)
        self.welcome = Welcome(window.recent_files,
                               lambda path=None: window.open_recent_file(str(path)) if path else window.open_file(),
                               lambda path=None: window.open_folder(path), window,
                               projects=window.settings.value("recent_projects", [], type=list),
                               create_template=self.create_template)
        self.stack.addWidget(self.welcome)
        wrapper = QWidget(window)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.breadcrumb)
        layout.addWidget(self.stack)
        window.setCentralWidget(wrapper)

    def _install_status(self) -> None:
        """Add metadata beside the existing Ln/Col, cat and Git labels."""
        window = self.window
        self.encoding = StatusItem("UTF-8", self.choose_encoding, window)
        self.line_ending = StatusItem("LF", self.choose_line_ending, window)
        self.indent = StatusItem("Spaces: 4", self.choose_indentation, window)
        self.interpreter = StatusItem("Python", window.choose_interpreter, window)
        self.activity = QLabel("Idle", window)
        for item in (self.encoding, self.line_ending, self.indent, self.interpreter,
                     self.activity):
            window.statusBar().addPermanentWidget(item)
        self.runner.output.connect(lambda _text: self.activity.setText("Running"))
        self.runner.finished.connect(lambda _code: self.activity.setText("Idle"))
        window.python_runner.process_started.connect(lambda: self.activity.setText("Running Python"))
        window.python_runner.process_finished.connect(lambda _code: self.activity.setText("Idle"))

    def choose_encoding(self) -> None:
        """Choose the UTF-8 BOM bit used by the existing atomic save path."""
        from PyQt5.QtWidgets import QInputDialog
        editor = self.window.current_editor()
        if editor is None:
            return
        choice, ok = QInputDialog.getItem(self.window, "Encoding", "Save as",
                                          ["UTF-8", "UTF-8 BOM"],
                                          1 if getattr(editor, "_utf8_bom", False) else 0, False)
        if ok:
            editor._utf8_bom = choice == "UTF-8 BOM"
            self.window._on_editor_text_changed(editor)
            self.current_changed(editor)

    def choose_line_ending(self) -> None:
        """Set a QScintilla EOL mode and mark byte serialization as dirty."""
        from PyQt5.Qsci import QsciScintilla
        from PyQt5.QtWidgets import QInputDialog
        editor = self.window.current_editor()
        if editor is None:
            return
        value, ok = QInputDialog.getItem(self.window, "Line endings", "Choose",
                                         ["LF", "CRLF", "CR"], 0, False)
        if ok:
            modes = {"LF": QsciScintilla.EolUnix,
                     "CRLF": QsciScintilla.EolWindows,
                     "CR": QsciScintilla.EolMac}
            editor.setEolMode(modes[value])
            self.window._on_editor_text_changed(editor)
            self.current_changed(editor)

    def choose_indentation(self) -> None:
        """Select tabs or space width for the active editor only."""
        from PyQt5.QtWidgets import QInputDialog
        editor = self.window.current_editor()
        if editor is None:
            return
        value, ok = QInputDialog.getItem(self.window, "Indentation", "Choose",
                                         ["Tabs: 4", "Spaces: 2", "Spaces: 4", "Spaces: 8"],
                                         2, False)
        if ok:
            editor.setIndentationsUseTabs(value.startswith("Tabs"))
            editor.setTabWidth(int(value[-1]))
            self.current_changed(editor)

    def _install_menu(self) -> None:
        """Install only new actions; reuse existing File/View menu actions."""
        window = self.window
        menu = window.menuBar().addMenu("Workspace Extras")
        density_menu = menu.addMenu("Density")
        for density in ("compact", "comfortable"):
            action = density_menu.addAction(density.title())
            window.command_actions["view.density." + density] = action
            action.triggered.connect(lambda _checked=False, d=density:
                                     window.apply_design_density(d))
        command_ids = iter(("view.focus", "layout.python", "layout.markdown", "layout.git",
                            "layout.save", "search.symbols", "edit.rename", "tests.run",
                            "run.configuration", "settings.shortcuts", "compare.disk",
                            "compare.files", "compare.git", "history.browse", "markdown.table",
                            "markdown.link", "markdown.check_links"))
        for label, callback in (("Focus mode", lambda: self.layouts.focus(
                                   self.layouts.before_focus is None)),
                                ("Python Coding layout", lambda: self.layouts.restore("Python Coding")),
                                ("Markdown Writing layout", lambda: self.layouts.restore("Markdown Writing")),
                                ("Git Review layout", lambda: self.layouts.restore("Git Review")),
                                ("Save current layout", self.save_layout),
                                ("Workspace symbols", self.find_symbol),
                                ("Rename symbol", self.rename_symbol),
                                ("Run workspace tests", self.run_tests),
                                ("Run configuration", self.run_configuration),
                                ("Keyboard shortcuts", self.edit_shortcuts),
                                ("Compare buffer with disk", self.compare_disk),
                                ("Compare two files", self.compare_files),
                                ("Compare buffer with Git HEAD", self.compare_git_head),
                                ("Browse local history", self.browse_history),
                                ("Insert Markdown table", self.insert_table),
                                ("Insert relative link", self.insert_link),
                                ("Check local links", self.check_links)):
            action = menu.addAction(label)
            action.triggered.connect(lambda _checked=False, fn=callback: fn())
            command = next(command_ids)
            window.command_actions[command] = action
            window.addAction(action)  # Keep actions reachable when focus mode hides menus.
            if command == "view.focus":
                action.setShortcut("Ctrl+Shift+F11")
                action.setShortcutContext(Qt.ApplicationShortcut)
        window.command_actions["markdown.image"] = menu.addAction("Insert image", lambda: self.insert_link(image=True))
        window.command_actions["markdown.heading_link"] = menu.addAction("Insert heading link", self.insert_heading_link)
        window.command_actions["markdown.toc"] = menu.addAction("Insert table of contents", self.insert_toc)
        window.command_actions["view.large_file_override"] = menu.addAction("Override large-file mode for current tab",
                       self.toggle_large_file)
        mode = menu.addAction("Enable performance diagnostics")
        window.command_actions["diagnostics.enabled"] = mode
        mode.setCheckable(True)
        mode.setChecked(self.timings.enabled)
        mode.toggled.connect(self.set_diagnostics_enabled)
        window.command_actions["diagnostics.show"] = menu.addAction("Performance timings", self.show_timings)

    def attach(self, editor) -> None:
        """Assign a recovery identity once and schedule preview for Markdown edits."""
        if not hasattr(editor, "_recovery_id"):
            editor._recovery_id = str(uuid.uuid4())
        self._watched_editors[id(editor)] = editor
        self._track_file(editor)
        if isinstance(editor, PythonEditor):
            editor.references_finder.references_found.connect(lambda generation, rows, ed=editor: self.references_ready(ed, generation, rows))
            editor.references_finder.references_empty.connect(lambda generation, ed=editor: self.references_ready(ed, generation, []))
            editor.references_finder.error.connect(lambda generation, error, ed=editor: self.references.set_rows((), error) if ed is self.window.current_editor() else None)
        editor.textChanged.connect(self._presentation_timer.start)
        if not hasattr(editor, "_disk_text"):
            editor._disk_text = editor.text()
        if isinstance(editor, MarkdownEditor):
            editor.textChanged.connect(lambda ed=editor: self.preview.changed(ed)
                                       if ed is self.window.current_editor() else None)


    def _track_file(self, editor) -> None:
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

    def _directory_changed(self, folder: str) -> None:
        """Reattach file watches after an external atomic rename/save."""
        for editor in tuple(self._watched_editors.values()):
            target = getattr(editor, "_save_target", None)
            if target is None or str(Path(target).resolve().parent) != folder:
                continue
            filename = str(Path(target).resolve())
            if Path(filename).is_file() and filename not in self.file_watcher.files():
                self.file_watcher.addPath(filename)
                self._file_changed(filename)

    def _file_changed(self, filename: str) -> None:
        """Send a watcher hint to the worker without reading bytes on the GUI."""
        target = Path(filename).resolve()
        for identity, editor in tuple(self._watched_editors.items()):
            if (getattr(editor, "_save_target", None) is not None
                    and Path(editor._save_target).resolve() == target):
                self.hashes.check(target, identity, getattr(editor, "_revision", 0))
        # QSaveFile/os.replace commonly removes a file watcher registration.
        if target.is_file() and filename not in self.file_watcher.files():
            self.file_watcher.addPath(filename)

    def _hash_ready(self, identity, request, digest: bytes) -> None:
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
            if editor is self.window.current_editor():
                self.window.statusBar().showMessage("File changed on disk; compare before saving", 6000)

    def retire(self, editor) -> None:
        """Invalidate completed and pending results for a disposed editor."""
        identity = id(editor)
        self._watched_editors.pop(identity, None)
        self.problem_rows.pop(identity, None)
        self.problems.set_rows([row for rows in self.problem_rows.values() for row in rows], "No reported problems")
        self.hashes.forget(identity)
        target = getattr(editor, "_save_target", None)
        if target is None:
            return
        filename = str(Path(target).resolve())
        if filename in self.file_watcher.files() and not any(
            getattr(other, "_save_target", None) is not None
            and Path(other._save_target).resolve() == Path(filename)
            for other in self._watched_editors.values()
        ):
            self.file_watcher.removePath(filename)
        folder = str(Path(filename).parent)
        if folder in self.file_watcher.directories() and not any(
            getattr(other, "_save_target", None) is not None
            and str(Path(other._save_target).resolve().parent) == folder
            for other in self._watched_editors.values()
        ):
            self.file_watcher.removePath(folder)

    def current_changed(self, editor) -> None:
        """Update welcome, metadata and breadcrumb after tab focus changes."""
        self.show_empty()
        if editor is None:
            for label in (self.encoding, self.line_ending, self.indent):
                label.setText("")
            return
        self.encoding.setText("UTF-8 BOM" if getattr(editor, "_utf8_bom", False) else "UTF-8")
        self.line_ending.setText({0: "CRLF", 1: "CR", 2: "LF"}.get(editor.eolMode(), "LF"))
        self.indent.setText(("Tabs" if editor.indentationsUseTabs() else "Spaces") +
                            f": {editor.tabWidth()}")
        self.interpreter.setText(Path(self.window.python_runner.interpreter).name)
        self.md_outline.setVisible(isinstance(editor, MarkdownEditor))
        self.window.outline_tree.setVisible(isinstance(editor, PythonEditor))
        if isinstance(editor, MarkdownEditor) and self.md_outline.isVisible() and (
                not getattr(editor, "_large_file_mode", False)
                or getattr(editor, "_large_file_override", False)):
            self.md_outline.refresh(editor.text())
        elif isinstance(editor, MarkdownEditor):
            self.md_outline.clear()  # Never show another tab's stale headings.
        self.cursor_changed(editor)
        self.refresh_presentations()

    def cursor_changed(self, editor) -> None:
        """Render a location only for the active tab to avoid stale callbacks."""
        if editor is not self.window.current_editor():
            return
        line, _column = editor.getCursorPosition()
        large = (getattr(editor, "_large_file_mode", False)
                 and not getattr(editor, "_large_file_override", False))
        self.breadcrumb.show_location(self.window._workspace_root,
                                      getattr(editor, "path", None),
                                      "" if large else editor.text(),
                                      line, isinstance(editor, PythonEditor))

    def toggle_large_file(self) -> None:
        """Permit optional analysis/preview on the current large tab only."""
        editor = self.window.current_editor()
        if editor is None or not getattr(editor, "_large_file_mode", False):
            return
        editor._large_file_override = not getattr(editor, "_large_file_override", False)
        self.current_changed(editor)
        if isinstance(editor, PythonEditor):
            self.window._update_outline()
        if editor._large_file_override and isinstance(editor, MarkdownEditor):
            self.window.render_preview()

    def show_timings(self) -> None:
        """Present bounded performance samples without path or source data."""
        values = self.timings.summary()
        detail = "\n".join(f"{name}: {count} samples, max {slow:.1f} ms"
                           for name, (count, slow) in sorted(values.items()))
        QMessageBox.information(self.window, "Performance timings",
                                detail or "No samples yet")

    def _jump(self, line: int, column: int) -> None:
        """Navigate inside the focused document using QScintilla coordinates."""
        editor = self.window.current_editor()
        if editor is not None:
            editor.setCursorPosition(line, column)
            editor.ensureLineVisible(line)
            editor.setFocus()

    def show_empty(self) -> None:
        """Show Welcome only when every split tab group is empty."""
        empty = not list(self.window.tab_view.all_editors())
        if empty:
            self.welcome.refresh(self.window.recent_files, self.window.settings.value("recent_projects", [], type=list))
        self.stack.setCurrentWidget(self.welcome if empty else self.stack.widget(0))
        self.breadcrumb.setVisible(not empty)

    def flush_recovery(self) -> None:
        """Snapshot dirty buffers every five seconds without touching disk files."""
        for editor in self.window.tab_view.all_editors():
            if editor in self.window._dirty_editors:
                try:
                    self.recovery.write(editor._recovery_id, getattr(editor, "path", None),
                                        editor.text(), isinstance(editor, PythonEditor))
                except (OSError, ValueError) as error:
                    # A periodic Qt slot must report an I/O failure rather
                    # than unwind into Qt's event loop.
                    self.window.statusBar().showMessage(f"Recovery unavailable: {error}", 5000)

    def restore_recovery(self) -> None:
        """Ask before restoring snapshots; never overwrite a newer disk file."""
        for item in self.recovery.pending():
            if QMessageBox.question(self.window, "Recover buffer",
                                    f"Restore unsaved content from {item['path'] or 'Untitled'}?",
                                    QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                continue
            previous_mode = self.window.python_editor_active
            self.window.python_editor_active = bool(item.get("python"))
            try:
                editor = self.window.new_file()
            finally:
                self.window.python_editor_active = previous_mode
            editor.setText(item["text"])
            editor._recovery_id = item["id"]
            # Keep a recovered copy untitled until the user chooses Save As.

    def saved(self, editor, path: Path, old_bytes: bytes | None) -> None:
        """Store pre-save bytes after a successful save and clear recovery."""
        try:
            if old_bytes is not None:
                self.history.record(Path(path), old_bytes)
        except OSError as error:
            # The document is already on disk. A history failure cannot undo
            # that successful save or make its dirty indicator truthful again.
            self.window.statusBar().showMessage(f"History unavailable: {error}", 5000)
        finally:
            try:
                self.recovery.forget(editor._recovery_id)
            except OSError as error:
                self.window.statusBar().showMessage(f"Recovery cleanup failed: {error}", 5000)
        editor._external_changed = False
        self._track_file(editor)
        if editor is self.window.current_editor():
            self.current_changed(editor)

    def discarded(self, editor) -> None:
        """Remove a recovery snapshot only for an explicit user discard."""
        self.recovery.forget(editor._recovery_id)
        QTimer.singleShot(0, self.show_empty)

    def compare(self, before, after, title):
        """Return explicit approval from a side-by-side, read-only comparison."""
        from side_bar_widgets.comparison_dialog import ComparisonDialog
        label = "Apply rename" if title == "Review rename" else "Open draft"
        return ComparisonDialog(before, after, title, self.window,
                                accept_text=label).exec_() == QDialog.Accepted

    def compare_disk(self) -> None:
        """Compare current UTF-8 buffer to the actual symlink-safe disk target."""
        editor = self.window.current_editor()
        if editor is None or getattr(editor, "path", None) is None:
            return
        try:
            # set_new_tab/_save_editor_to_path already resolved a symlink-safe
            # target, so importing main as a second module is unnecessary.
            target = Path(getattr(editor, "_save_target", editor.path))
            disk = target.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self.window, "Compare", str(error))
            return
        if self.compare(editor.text(), disk, "Buffer versus disk"):
            self.open_draft(disk, isinstance(editor, PythonEditor))

    def compare_files(self) -> None:
        """Compare two UTF-8 files and optionally open the right-hand text as a draft."""
        from PyQt5.QtWidgets import QFileDialog
        selected = []
        for caption in ("First file", "Second file"):
            filename, _filter = QFileDialog.getOpenFileName(self.window, caption)
            if not filename:
                return
            selected.append(Path(filename))
        try:
            left, right = (path.read_text(encoding="utf-8-sig") for path in selected)
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self.window, "Compare files", str(error))
            return
        if self.compare(left, right, "Two files"):
            self.open_draft(right, is_python_path(selected[1]))

    def compare_git_head(self) -> None:
        """Compare the unsaved buffer with this file's Git HEAD bytes."""
        import subprocess
        editor = self.window.current_editor()
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
            QMessageBox.warning(self.window, "Git comparison", str(error))
            return
        if self.compare(before, editor.text(), "Git HEAD versus buffer"):
            self.open_draft(editor.text(), isinstance(editor, PythonEditor))

    def external_conflict(self, editor, raw: bytes) -> str:
        """Offer reload, keep, or an explicit conflict-marker merge draft."""
        disk = raw.decode("utf-8-sig")
        dialog = QMessageBox(self.window)
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
            self.window.mark_editor_clean(editor)
            return "cancel-save"
        if chosen is keep:
            return "overwrite"
        if chosen is merge:
            # Without a stored common ancestor, never claim a clean merge.
            result, _conflict = three_way(getattr(editor, "_disk_text", ""), editor.text(), disk)
            previous_mode = self.window.python_editor_active
            self.window.python_editor_active = isinstance(editor, PythonEditor)
            try:
                draft = self.window.new_file()
            finally:
                self.window.python_editor_active = previous_mode
            draft.setText(result)
        return "cancel-save"

    def browse_history(self):
        """Choose any retained version, compare it and open an explicitly accepted draft."""
        from side_bar_widgets.history_dialog import HistoryDialog
        editor = self.window.current_editor()
        if editor is None or not getattr(editor, "path", None):
            return
        dialog = HistoryDialog(self.history.versions(Path(editor.path)), self.window)
        if dialog.exec_() != QDialog.Accepted or dialog.selected_path() is None:
            return
        try:
            old = dialog.selected_path().read_text(encoding="utf-8-sig")
            if self.compare(editor.text(), old, "Compare selected local version"):
                self.open_draft(old, isinstance(editor, PythonEditor))
        except (OSError, UnicodeError) as error:
            QMessageBox.warning(self.window, "Local history", str(error))

    def save_layout(self) -> None:
        """Capture the current layout under a reusable preset name."""
        from PyQt5.QtWidgets import QInputDialog
        name, accepted = QInputDialog.getText(self.window, "Save layout", "Name")
        if accepted and name.strip():
            self.layouts.save(name.strip())

    def find_symbol(self) -> None:
        """Submit a bounded AST index on a worker, never in the click handler."""
        from PyQt5.QtWidgets import QInputDialog
        query, accepted = QInputDialog.getText(self.window, "Workspace symbols", "Name")
        if not accepted:
            return
        self._symbol_query = query
        root = self.window._workspace_root
        # Workspace files may change without an editor event. Use a fresh
        # generation for each explicit search rather than reusing stale cache.
        key = RequestKey("", time.monotonic_ns(), self.window.python_runner.interpreter,
                         str(root), "workspace-symbols")
        self.analysis.submit(key, lambda: workspace_symbols(root))

    def _analysis_ready(self, key, value) -> None:
        """Reject a result after the active workspace or interpreter changes."""
        if key.kind == "rename":
            self._rename_ready(key, value)
            return
        if key.kind != "workspace-symbols" or key.workspace != str(self.window._workspace_root):
            return
        if key.interpreter != self.window.python_runner.interpreter:
            return
        if isinstance(value, Exception):
            QMessageBox.warning(self.window, "Symbols", str(value))
            return
        from PyQt5.QtWidgets import QInputDialog
        query = self._symbol_query
        results = [s for s in value if query.casefold() in s.name.casefold()][:100]
        labels = [f"{s.name} — {s.path.relative_to(self.window._workspace_root)}:{s.line + 1}"
                  for s in results]
        if not labels:
            QMessageBox.information(self.window, "Symbols", "No matching symbols")
            return
        picked, ok = QInputDialog.getItem(self.window, "Symbols", "Definition", labels, 0, False)
        if ok:
            item = results[labels.index(picked)]
            self.window._open_file_at_position(str(item.path), item.line, item.column)

    def rename_symbol(self):
        """Submit semantic rename planning off-thread and review its exact result later."""
        editor = self.window.current_editor()
        if not isinstance(editor, PythonEditor) or not editor.path:
            return
        if self.window._dirty_editors:
            QMessageBox.warning(self.window, "Rename", "Save all modified tabs first")
            return
        name, accepted = QInputDialog.getText(self.window, "Rename symbol", "New name")
        if not accepted:
            return
        line, column = editor.getCursorPosition()
        root, path, source = self.window._workspace_root, Path(editor.path), editor.text()
        interpreter = self.window.python_runner.interpreter
        key = RequestKey(str(path), time.monotonic_ns(), interpreter, str(root), "rename")
        self.analysis.submit(key, lambda: plan_rename(root, path, source, line, column, name, interpreter))

    def run_tests(self, targets=None, collect=False):
        """Run workspace, selected node IDs, or collection in a separate pytest process."""
        try:
            dock = self.tests.get()
            dock.show()
            dock.output.clear()
            dock.state.setText("Collecting…" if collect else "Running…")
            if collect:
                dock.set_context(self.window._workspace_root, self.window.python_runner.interpreter)
            self.test_session.start(self.window.python_runner.interpreter,
                                    self.window._workspace_root, targets or (), collect=collect)
        except (OSError, ValueError, RuntimeError) as error:
            QMessageBox.warning(self.window, "Tests", str(error))

    def _make_tests(self):
        """Create the collected-test tree and connect its dedicated runner once."""
        dock = TestDock(self.window._workspace_root, self.window)
        if not self.window.restoreDockWidget(dock):
            self.window.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.test_session.output.connect(dock.append)
        self.test_session.finished.connect(dock.completed)
        self.test_session.event_ready.connect(dock.on_event)
        dock.run_requested.connect(self.run_tests)
        dock.collect_requested.connect(lambda: self.run_tests(collect=True))
        dock.targets_requested.connect(lambda targets: self.run_tests(targets))
        dock.stop_requested.connect(self.test_session.stop)
        dock.navigate.connect(lambda path, line: self.window._open_file_at_position(path, line, 0))
        return dock

    def run_configuration(self) -> None:
        """Edit one persistent launch profile and run it after validation."""
        from PyQt5.QtWidgets import QInputDialog
        location = self.recovery.directory.parent / "run-configs.json"
        try:
            configs = load_configs(location)
        except (ValueError, TypeError, OSError) as error:
            QMessageBox.warning(self.window, "Run configurations", str(error))
            return
        if configs:
            labels = [c.name for c in configs]
            chosen, ok = QInputDialog.getItem(self.window, "Run configurations",
                                              "Select", labels + ["New…"], 0, False)
            if not ok:
                return
            current = configs[labels.index(chosen)] if chosen != "New…" else None
        else:
            current = None
        config = current or RunConfig("New", self.window.python_runner.interpreter,
                                      "", str(self.window._workspace_root), [], {})
        dialog = RunConfigDialog(config, self.window)
        if dialog.exec_() != QDialog.Accepted:
            return
        try:
            result = dialog.value()
            configs = [c for c in configs if c.name != result.name] + [result]
            save_configs(location, configs)
            self.run_output.get().show()
            self.run_output.get().begin(result.name)
            self.runner.run(result)
        except (OSError, ValueError, TypeError, RuntimeError) as error:
            QMessageBox.warning(self.window, "Run configuration", str(error))

    def edit_shortcuts(self) -> None:
        """Edit stable command IDs bound to the original menu QActions."""
        dialog = ShortcutDialog(self.window.command_actions,
                                self.window.settings, self.window)
        dialog.exec_()

    def insert_table(self):
        """Validate user-entered JSON rows before inserting a table as one undo step."""
        editor = self.window.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        value, accepted = QInputDialog.getMultiLineText(self.window, "Insert table", "Rows as JSON; first row is the header", '[["Column A", "Column B"], ["", ""]]')
        if not accepted:
            return
        try:
            rows = json.loads(value)
            if not isinstance(rows, list) or any(not isinstance(row, list) or
                    any(not isinstance(cell, str) for cell in row) for row in rows):
                raise ValueError("Use a JSON list of rows containing strings")
            content = table(rows)
        except (ValueError, TypeError) as error:
            QMessageBox.warning(self.window, "Table", str(error))
            return
        editor.beginUndoAction()
        try:
            editor.insert(content)
        finally:
            editor.endUndoAction()

    def insert_link(self, image=False) -> None:
        """Pick a local target and write a relative, escaped Markdown URL."""
        from PyQt5.QtWidgets import QFileDialog
        editor = self.window.current_editor()
        if not isinstance(editor, MarkdownEditor) or not editor.path:
            return
        value, _filter = QFileDialog.getOpenFileName(self.window, "Link target",
                                                    str(Path(editor.path).parent))
        if value:
            editor.insert(relative_link(Path(editor.path), Path(value), image=image))

    def check_links(self) -> None:
        """Summarize broken local paths without treating URLs as files."""
        editor = self.window.current_editor()
        if not isinstance(editor, MarkdownEditor) or not editor.path:
            return
        bad = broken_local_links(Path(editor.path), editor.text())
        QMessageBox.information(self.window, "Local links",
                                "\n".join(link for _line, link in bad[:20])
                                if bad else "All checked local links exist")

    def insert_toc(self) -> None:
        """Insert a generated heading index at the current Markdown caret."""
        editor = self.window.current_editor()
        if isinstance(editor, MarkdownEditor):
            editor.insert(toc(editor.text()) + "\n")

    def shutdown(self) -> None:
        """Stop feature timers and workers after the close prompts resolve."""
        self._recovery_timer.stop()
        self._presentation_timer.stop()
        self.preview.timer.stop()
        self.flush_recovery()
        if self.file_watcher.files():
            self.file_watcher.removePaths(self.file_watcher.files())
        if self.file_watcher.directories():
            self.file_watcher.removePaths(self.file_watcher.directories())
        self.analysis.shutdown()
        self.hashes.shutdown()

    def environment_changed(self):
        """Invalidate shared results and tab providers after project/environment changes."""
        self.analysis.invalidate_all()
        self.test_session.invalidate()
        for editor in self.window.tab_view.all_editors():
            if isinstance(editor, PythonEditor):
                for provider in editor._analysis_workers():
                    provider.invalidate()
        if self.tests.value is not None:
            self.tests.value.set_context(self.window._workspace_root,
                                            self.window.python_runner.interpreter)
        self.current_changed(self.window.current_editor())

    def create_template(self, name):
        """Open a selected starter as an unsaved document of the correct editor type."""
        from side_bar_widgets.welcome_screen import TEMPLATES
        python, source = TEMPLATES[name]
        self.open_draft(source, python)

    def open_draft(self, source, python=False):
        """Create editable draft text without assigning an overwrite destination."""
        previous = self.window.python_editor_active
        self.window.python_editor_active = python
        try:
            editor = self.window.new_file()
            editor.setText(source)
            return editor
        finally:
            self.window.python_editor_active = previous

    def insert_heading_link(self):
        """Offer rendered headings and insert a correctly escaped local anchor link."""
        from markdown_editor.heading_navigation import markdown_headings, heading_link
        editor = self.window.current_editor()
        if not isinstance(editor, MarkdownEditor):
            return
        headings = markdown_headings(editor.text())
        if not headings:
            return
        labels = [f"{h.title} (line {h.line + 1})" for h in headings]
        choice, accepted = QInputDialog.getItem(self.window, "Heading link", "Heading", labels, 0, False)
        if accepted:
            editor.insert(heading_link(editor.text(), headings[labels.index(choice)].line))

    def _install_panels(self):
        """Create cheap Problems/References/Minimap shells and connect navigation once."""
        from side_bar_widgets.snapshot_dock import SnapshotDock
        from side_bar_widgets.document_minimap import DocumentMinimap
        self.problem_rows = {}
        self.problems = SnapshotDock("Problems", "ProblemsDock", self.window)
        self.references = SnapshotDock("References", "ReferencesDock", self.window)
        self.minimap_dock = QDockWidget("Minimap", self.window)
        self.minimap_dock.setObjectName("MinimapDock")
        self.minimap = DocumentMinimap(self.minimap_dock)
        self.minimap_dock.setWidget(self.minimap)
        for dock in (self.problems, self.references, self.minimap_dock):
            self.window.addDockWidget(Qt.RightDockWidgetArea, dock)
            dock.hide()
        self.problems.navigate.connect(self.window._open_file_at_position)
        self.references.navigate.connect(self.window._open_file_at_position)
        self.minimap.navigate.connect(lambda line: self._jump(line, 0))
        self.minimap_dock.visibilityChanged.connect(lambda _shown: self.refresh_presentations())
        self._presentation_timer = QTimer(self.window)
        self._presentation_timer.setSingleShot(True)
        self._presentation_timer.setInterval(160)
        self._presentation_timer.timeout.connect(self.refresh_presentations)
        menu = self.window.menuBar().addMenu("Analysis panels")
        for dock in (self.problems, self.references, self.minimap_dock):
            action = dock.toggleViewAction()
            menu.addAction(action)
            self.window.command_actions["view." + dock.objectName()] = action
        self.window.command_actions["search.references"] = menu.addAction("Find references", self.find_references)

    def refresh_presentations(self):
        """Rebuild visible optional panels once using the current document snapshot."""
        editor = self.window.current_editor()
        if editor is None:
            self.md_outline.clear()
            self.minimap.set_source("")
            return
        large = editor.length() > 2_000_000 and not getattr(editor, "_large_file_override", False)
        if self.md_outline.isVisible():
            if large:
                self.md_outline.clear()
            elif isinstance(editor, MarkdownEditor):
                self.md_outline.refresh(editor.text())
        if self.minimap_dock.isVisible():
            if large:
                self.minimap.set_paused()
            else:
                self.minimap.set_source(editor.text(), editor.firstVisibleLine(),
                                        editor.SendScintilla(editor.SCI_LINESONSCREEN))

    def find_references(self):
        """Run project reference search on the current Python tab's shared provider."""
        editor = self.window.current_editor()
        if not isinstance(editor, PythonEditor):
            return
        self.references.show()
        self.references.set_rows((), "Searching references…")
        if editor.length() > 2_000_000 and not getattr(editor, "_large_file_override", False):
            self.references.set_rows((), "Analysis paused; use the per-tab large-file override")
            return
        line, column = editor.getCursorPosition()
        editor.references_finder.find_references(line + 1, column, editor.text(), editor.path)

    def references_ready(self, editor, generation, rows):
        """Reject an inactive source tab and retain current reference navigation rows."""
        if editor is not self.window.current_editor() or generation != editor.references_finder.generation:
            return
        self.references.set_rows([(name, path, line, column) for path, line, column, name in rows],
                                 "No references found")

    def diagnostics_changed(self, editor, diagnostics):
        """Retain current Ruff data while deferring hidden Problems tree rebuilding."""
        path = str(getattr(editor, "path", None) or "")
        self.problem_rows[id(editor)] = [(f"{d.code}: {d.message}", path, d.start.line, d.start.column)
                                        for d in diagnostics if path]
        self.problems.set_rows([row for rows in self.problem_rows.values() for row in rows],
                               "No reported problems in open saved Python files")

    def _rename_ready(self, key, edits):
        """Review a current rename plan and revalidate every affected file on Apply."""
        if key.workspace != str(self.window._workspace_root) or key.interpreter != self.window.python_runner.interpreter:
            return
        if isinstance(edits, Exception):
            QMessageBox.warning(self.window, "Rename", str(edits))
            return
        if self.window._dirty_editors:
            QMessageBox.warning(self.window, "Rename", "A buffer changed while the plan was calculated; save and retry")
            return
        if not edits or not self.compare("", rename_preview(edits), "Review rename"):
            return
        try:
            if self.window._dirty_editors:
                raise RuntimeError("An open buffer changed during review; save and retry")
            apply_rename(edits)
            for edit in edits:
                try:
                    self.history.record(edit.path, edit.before)
                except OSError as error:
                    # A backup error must not prevent refreshing already-written files.
                    self.window.statusBar().showMessage(f"History copy failed: {error}", 6000)
            affected = {edit.path for edit in edits}
            for view in self.window.tab_view.all_editors():
                if getattr(view, "path", None) and Path(view.path).resolve() in affected:
                    raw = Path(view.path).read_bytes()
                    view.setTextSafely(raw.decode("utf-8-sig"))
                    view._disk_text = raw.decode("utf-8-sig")
                    view._utf8_bom = raw.startswith(UTF8_BOM)
                    view._disk_digest = hashlib.sha256(raw).digest()
                    if isinstance(view, PythonEditor) and view.ruff_lsp is not None:
                        view.ruff_lsp.sync_from_editor()
                    self.window.mark_editor_clean(view)
            self.analysis.invalidate_all()
        except (OSError, UnicodeError, ValueError, RuntimeError) as error:
            QMessageBox.warning(self.window, "Rename", str(error))

    def set_diagnostics_enabled(self, enabled):
        """Persist opt-in in-memory timings; source text and file paths are never recorded."""
        self.timings.enabled = enabled
        self.window.settings.setValue("performance_diagnostics", enabled)

    def _make_run_output(self):
        """Create a distinct named-profile output dock and connect its Stop action once."""
        from python_editor.run_output import RunOutputDock
        dock = RunOutputDock(self.window)
        self.window.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.runner.output.connect(dock.append)
        self.runner.finished.connect(dock.completed)
        dock.stop_requested.connect(self.runner.stop)
        return dock
````

<a id="native-lexer-integration"></a>
### Native lexer integration — `python_editor/lexer_fast.pyx`

The Python fallback and Cython scanner use the same snapshot tuple. Update the source before rebuilding; keeping an old binary is safe because the Python import checks `STATE_API`, but the old binary will not receive the optimization.

**File:** existing `python_editor/lexer_fast.pyx`. **Placement:** replace the complete `compute_state_before` definition, immediately after `_skip_string` and before `def style_chunk`. Insert `STATE_API = 2` immediately before the replacement function, at module scope. Retain `style_chunk` and all other Cython helpers unchanged.

**Baseline replacement region:** lines 171–405; the next `def style_chunk` is the stopping boundary.

````cython
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

The complete replacement `python_editor/setup.py` appears in Topic 25. Run the build **from the repository root**, not from inside `python_editor/`:

```bash
python -m pip install -e ".[test]"
python -m pip install "Cython>=3,<4"
python python_editor/setup.py build_ext --inplace
python -c "from python_editor import lexer_fast; print(lexer_fast.STATE_API)"
```

The last command must print `2`. The build regenerates the C source and platform-specific extension; do not paste generated C or commit a machine-specific `.so`/`.pyd` as portable source. A compiler compatible with the selected Python installation is required. For the pure-Python fallback, the editor remains usable without building the extension; the native-specific regression is skipped until the extension is available.

The repository already declares the runtime dependencies used here. Pytest must also be installed in the interpreter selected for running tests, which may differ from the interpreter launching the editor. No shell quoting is applied to run-profile argument entries: enter a JSON list such as `["--name", "Ada Lovelace"]`, not one combined command string.

<a id="test-installation"></a>
## Test installation and verification

Create the following files in the existing `tests/` directory. All exercise B answers are included in the first file with their imports and fixtures. The third file covers the previously missing production connections: native/fallback checkpoint equivalence, real Jedi queue results, structured pytest collection/selection, metadata-preserving rename, parser-backed links, and deferred panels.

These tests are additions; retain the repository's existing tests.

<a id="file-tests-test-feature-exercises-py"></a>
#### CREATE FILE — `tests/test_feature_exercises.py`

**Folder:** `tests/` already exists. Create **only** `test_feature_exercises.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
"""Executable answers to the course's second exercise in each topic.

Run from the repository root with pytest. Qt tests use real widgets; the
offscreen platform lets Linux CI run them without a visible desktop.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import hashlib
import sys
import time
from concurrent.futures import Future
from pathlib import Path
from threading import Event

import pytest
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QAction, QDockWidget, QMainWindow, QSplitter, QWidget
from PyQt5.Qsci import QsciScintilla

from code_settings.design_system import theme_qss
from markdowneditor_assets.icon_provider import themed_icon
from code_inteligence.symbol_index import python_symbols, symbol_at, workspace_symbols
from side_bar_widgets.breadcrumb import Breadcrumb
from side_bar_widgets.status_item import StatusItem
from side_bar_widgets.empty_state import EmptyState
from side_bar_widgets.welcome_screen import Welcome
from code_settings.workspace_layouts import Layouts
from code_inteligence.document_recovery import RecoveryStore
from code_inteligence.local_history import VersionStore
from code_inteligence.text_comparison import three_way, unified_diff
from code_inteligence.symbol_rename import plan_rename, apply_rename
from python_editor.run_configurations import ProcessPanel, RunConfig, RunConfigDialog
from code_settings.keyboard_shortcuts import Shortcuts
from code_inteligence.pair_handling import pair_key, empty_pair_backspace
from markdown_editor.heading_navigation import markdown_headings, toc
from markdown_editor.authoring_tools import table, relative_link, broken_local_links
from code_settings.performance_diagnostics import Timings
from side_bar_widgets.lazy_panel import LazyWidget
from code_inteligence.file_hash_queue import FileHashQueue
from python_editor.lexer_checkpoints import LexerCheckpoints
from markdown_editor.preview_scheduler import PreviewSchedule
from code_settings.large_file_policy import file_size_mode, should_update_panel
from code_inteligence.analysis_scheduler import AnalysisQueue
from code_inteligence.analysis_cache import LRU, RequestKey


@pytest.fixture(scope='session')
def app():
    """Retain one QApplication throughout all real Qt widget tests."""
    application = QApplication.instance() or QApplication([])
    yield application


def wait_until(app, condition, timeout=3.0):
    """Process Qt delivery while waiting for one bounded asynchronous result."""
    deadline = time.monotonic() + timeout
    while not condition() and time.monotonic() < deadline:
        app.processEvents()
        QTest.qWait(5)
    assert condition(), 'Timed out waiting for the expected Qt result'


@pytest.fixture
def layout_window(app, tmp_path):
    """Build the real Qt objects required by Layouts without starting services."""
    window = QMainWindow()
    window.settings = QSettings(str(tmp_path / 'layout.ini'), QSettings.IniFormat)
    window.hs_split = QSplitter(window)
    window.side_bar, window.side_panel = QWidget(), QWidget()
    window.hs_split.addWidget(window.side_bar)
    window.hs_split.addWidget(window.side_panel)
    window.hs_split.addWidget(QWidget())
    window.setCentralWidget(window.hs_split)
    window.console_dock = QDockWidget('Console', window)
    window.console_dock.setObjectName('ConsoleDock')
    window.addDockWidget(Qt.BottomDockWidgetArea, window.console_dock)
    window.resize(900, 500)
    window.show()
    app.processEvents()
    yield window
    window.close()


def test_01_design_tokens():
    """Reject an unknown preference before emitting invalid stylesheet data."""
    assert 'padding: 7px' in theme_qss('comfortable')
    assert '#61afef' in theme_qss('comfortable')
    with pytest.raises(ValueError):
        theme_qss('tiny')


def test_02_icon_assets(app):
    """Use the actual shipped assets and reject names outside the sidebar."""
    assert not themed_icon('terminal').isNull()
    with pytest.raises(ValueError):
        themed_icon('../terminal')


def test_03_breadcrumb_scope(app, tmp_path):
    """Only the enclosing class and method contribute symbol buttons."""
    source = 'class A:\n    def run(self):\n        return 1\nclass B:\n    pass\n'
    symbols = python_symbols(tmp_path / 'a.py', source)
    assert [s.name for s in symbol_at(symbols, 2)] == ['A', 'run']
    assert [s.name for s in symbol_at(symbols, 4)] == ['B']
    destinations = []
    bar = Breadcrumb(lambda row, col: destinations.append((row, col)))
    bar.show_location(tmp_path, tmp_path / 'a.py', source, 2, True)
    bar.row.itemAt(3).widget().click()
    assert destinations == [(1, 4)]


def test_04_density_roundtrip():
    """Regenerating the same profile is stable and does not append rules."""
    comfortable = theme_qss('comfortable')
    assert 'padding: 3px' in theme_qss('compact')
    assert theme_qss('comfortable') == comfortable


def test_05_status_keyboard(app):
    """Keyboard activation invokes the same setting as a pointer click."""
    called = []
    item = StatusItem('UTF-8', lambda: called.append('encoding'))
    QTest.keyClick(item, Qt.Key_Return)
    QTest.mouseClick(item, Qt.LeftButton)
    assert called == ['encoding', 'encoding']


def test_06_empty_action(app):
    """An empty-panel action is connected to a callable operation."""
    called = []
    panel = EmptyState('No results', 'Open a project', 'Open', lambda: called.append(True))
    from PyQt5.QtWidgets import QPushButton
    panel.findChild(QPushButton).click()
    assert called == [True]


def test_07_welcome_recent_file(app, tmp_path):
    """Recent-file buttons retain their own path rather than the loop's last path."""
    opened = []
    page = Welcome([str(tmp_path / 'first.md'), str(tmp_path / 'second.md')],
                   lambda path=None: opened.append(path), lambda: None)
    from PyQt5.QtWidgets import QPushButton
    buttons = page.findChildren(QPushButton)
    buttons[2].click()
    buttons[3].click()
    assert opened == [tmp_path / 'first.md', tmp_path / 'second.md']


def test_08_focus_restore(layout_window):
    """Leaving focus restores the visible dock and consumes its snapshot."""
    state = Layouts(layout_window)
    state.focus(True)
    assert layout_window.console_dock.isHidden()
    state.focus(False)
    assert not layout_window.console_dock.isHidden()
    assert state.before_focus is None


def test_09_saved_layout(layout_window):
    """A missing preset preserves state; a named preset restores dock visibility."""
    state = Layouts(layout_window)
    assert not state.restore('Missing')
    state.save('Python Coding')
    layout_window.console_dock.hide()
    assert state.restore('Python Coding')
    assert not layout_window.console_dock.isHidden()


def test_10_recovery_copy(tmp_path):
    """A recovery snapshot never overwrites the associated saved document."""
    document = tmp_path / 'saved.md'
    document.write_text('disk', encoding='utf-8')
    store = RecoveryStore(tmp_path / 'recovery')
    store.write('stable-id', document, 'unsaved 😀')
    assert store.pending()[0]['text'] == 'unsaved 😀'
    assert document.read_text(encoding='utf-8') == 'disk'
    store.forget('stable-id')
    assert store.pending() == []


def test_11_history_retention(tmp_path):
    """History bounds versions for one path and retains the newest predecessor."""
    history = VersionStore(tmp_path / 'history', keep=2)
    document = tmp_path / 'saved.md'
    for value in (b'one', b'two', b'three'):
        history.record(document, value)
    versions = history.versions(document)
    assert len(versions) == 2
    assert versions[0].read_bytes() == b'three'


def test_12_conflict_preserves_both():
    """A divergent edit is visible; trivial agreement needs no conflict markers."""
    assert three_way('base', 'same', 'same') == ('same', False)
    merged, conflict = three_way('base', 'editor text', 'disk text')
    assert conflict
    assert 'editor text' in merged and 'disk text' in merged
    assert '<<<<<<< EDITOR' in merged


def test_13_comparison_read_only():
    """A diff labels both snapshots and returns no output for equal content."""
    before, after = 'one\n', 'two\n'
    result = unified_diff(before, after, 'disk', 'buffer')
    assert '--- disk' in result and '+++ buffer' in result
    assert '-one' in result and '+two' in result
    assert unified_diff(before, before, 'disk', 'buffer') == ''


def test_14_jedi_rename_and_stale_preview(tmp_path):
    """Use real Jedi semantics, then reject a disk edit made after preview."""
    document = tmp_path / 'example.py'
    source = 'def old_name():\n    return 1\n\nold_name()\n'
    document.write_text(source, encoding='utf-8')
    edits = plan_rename(tmp_path, document, source, 0, 5, 'new_name')
    assert b'new_name()' in edits[0].after
    document.write_text(source + '# external change\n', encoding='utf-8')
    with pytest.raises(RuntimeError):
        apply_rename(edits)
    assert document.read_text(encoding='utf-8').endswith('# external change\n')
    document.write_text(source, encoding='utf-8')
    apply_rename(edits)
    assert 'old_name' not in document.read_text(encoding='utf-8')


def test_15_workspace_tolerates_broken_file(tmp_path):
    """One invalid file must not hide definitions from other Python files."""
    (tmp_path / 'bad.py').write_text('def broken(', encoding='utf-8')
    (tmp_path / 'good.py').write_text('class Present:\n    pass\n', encoding='utf-8')
    assert [item.name for item in workspace_symbols(tmp_path)] == ['Present']


def test_16_process_streams_utf8(app, tmp_path):
    """Run a real child process through QProcess and receive its final output."""
    script = tmp_path / 'child.py'
    script.write_text('print("ready 😀")\n', encoding='utf-8')
    runner = ProcessPanel()
    output, exits = [], []
    runner.output.connect(output.append)
    runner.finished.connect(exits.append)
    runner.run(RunConfig('test', sys.executable, str(script), str(tmp_path), [],
                         {'PYTHONIOENCODING': 'utf-8'}))
    wait_until(app, lambda: bool(exits))
    assert exits == [0]
    assert 'ready 😀' in ''.join(output)


def test_17_run_dialog_validates_data(app, tmp_path):
    """Arguments stay a list; environment values must be strings."""
    config = RunConfig('example', sys.executable, 'a.py', str(tmp_path), ['two words'], {})
    dialog = RunConfigDialog(config)
    assert dialog.value().arguments == ['two words']
    dialog.fields['env'].setText('{"COUNT": 3}')
    with pytest.raises(ValueError):
        dialog.value()


def test_18_shortcut_conflict_is_atomic(app, tmp_path):
    """Reject duplicates before changing either original QAction shortcut."""
    settings = QSettings(str(tmp_path / 'keys.ini'), QSettings.IniFormat)
    save, open_file = QAction('Save'), QAction('Open')
    save.setShortcut('Ctrl+S')
    open_file.setShortcut('Ctrl+O')
    with pytest.raises(ValueError):
        Shortcuts(settings).bind({'save': save, 'open': open_file}, {'open': 'Ctrl+S'})
    assert open_file.shortcut().toString() == 'Ctrl+O'
    assert save.shortcut().toString() == 'Ctrl+S'


def test_19_pairs_after_unicode(app):
    """Use real QScintilla indices after an emoji, then undo a paired deletion."""
    editor = QsciScintilla()
    editor.setUtf8(True)
    editor.setText('😀')
    editor.setCursorPosition(0, 1)
    assert pair_key(editor, '(')
    assert editor.text() == '😀()'
    assert empty_pair_backspace(editor)
    assert editor.text() == '😀'
    editor.undo()
    assert editor.text() == '😀()'


def test_20_markdown_fences_and_duplicates():
    """Code fences suppress headings and repeated titles get distinct anchors."""
    source = '# Setup\n```python\n# hidden\n```\n# Setup\n'
    assert [item.slug for item in markdown_headings(source)] == ['setup', 'setup_1']
    assert '(#setup_1)' in toc(source)


def test_21_table_and_relative_link(tmp_path):
    """Escaped pipes keep table columns stable and spaces survive URL encoding."""
    assert r'a\|b' in table([['a|b'], ['cell']])
    with pytest.raises(ValueError):
        table([['one'], ['one', 'two']])
    image = tmp_path / 'screen shot.png'
    image.write_bytes(b'example')
    source = tmp_path / 'note.md'
    link = relative_link(source, image, image=True)
    assert 'screen%20shot.png' in link
    assert broken_local_links(source, link) == []
    assert broken_local_links(source, '[empty]()') == []


def test_22_timing_bound():
    """The latest two samples determine a summary after the older slow sample expires."""
    timings = Timings(limit=2)
    for seconds in (0.100, 0.003, 0.005):
        timings.observe('preview', seconds)
    assert timings.summary()['preview'] == (2, 5.0)


def test_23_lazy_factory_once():
    """Repeated panel access returns the same object and calls its factory once."""
    calls = []
    def create():
        """Count actual construction before returning a distinct object."""
        calls.append(1)
        return object()
    panel = LazyWidget(create)
    first = panel.get()
    assert panel.get() is first
    assert calls == [1]


def test_24_hash_generation(app, tmp_path):
    """A stale result drains from shutdown tracking without being published."""
    worker = FileHashQueue()
    received = []
    worker.changed.connect(lambda *result: received.append(result))
    path = (tmp_path / 'a.md').resolve()
    worker.pending['editor'] = (path, 2)
    old = Future()
    worker.futures.add(old)
    worker._on_done('editor', (path, 1), b'old', old)
    assert not worker.futures and not received
    current = Future()
    worker.futures.add(current)
    digest = hashlib.sha256(b'current').digest()
    worker._on_done('editor', (path, 2), digest, current)
    assert received == [('editor', (path, 2), digest)]
    worker.shutdown()


def test_25_checkpoint_invalidates_prefix():
    """An edit near the start invalidates production snapshots farther downstream."""
    from python_editor.custompythonlexer import _py_compute_state
    cache = LexerCheckpoints(verify=True)
    old = (b"value = 1\n" * 2000)
    cache.state_before(old, len(old), _py_compute_state)
    assert len(cache.states) > 1
    new = bytes([39, 39, 39]) + old
    cache.invalidate(new)
    assert cache.states == {0: None}
    assert cache.state_before(new, len(new), _py_compute_state) == _py_compute_state(new, len(new))


def test_26_preview_active_tab(app):
    """Render a changed active buffer once and ignore a now-background buffer."""
    owner = QWidget()
    editor = QsciScintilla()
    editor.setText('first')
    owner.current_editor = lambda: editor
    rendered = []
    schedule = PreviewSchedule(lambda: rendered.append(editor.text()), owner)
    schedule.editor = editor
    schedule.flush()
    schedule.flush()
    assert rendered == ['first']
    owner.current_editor = lambda: None
    editor.setText('second')
    schedule.flush()
    assert rendered == ['first']


def test_27_large_file_boundary():
    """Apply a byte threshold at the boundary without platform-dependent file I/O."""
    assert not file_size_mode(9, threshold=10)
    assert file_size_mode(10, threshold=10)


def test_28_latest_analysis_wins(app):
    """Run real worker jobs while rejecting the obsolete result on Qt delivery."""
    queue = AnalysisQueue()
    release = Event()
    results = []
    queue.ready.connect(lambda key, value: results.append((key, value)))
    old = RequestKey('a.py', 1, sys.executable, '/project', 'symbols')
    new = RequestKey('a.py', 2, sys.executable, '/project', 'symbols')
    def first():
        """Block the old work so a newer request supersedes it deterministically."""
        assert release.wait(2)
        return 'old'
    queue.submit(old, first)
    queue.submit(new, lambda: 'new')
    release.set()
    wait_until(app, lambda: not queue.is_running())
    assert results == [(new, 'new')]
    queue.shutdown()


def test_29_cache_eviction():
    """Reading A promotes it; inserting C then removes older untouched B."""
    cache = LRU(size=2)
    cache.put('A', 1)
    cache.put('B', 2)
    assert cache.get('A') == 1
    cache.put('C', 3)
    assert cache.get('B') is None
    assert cache.get('A') == 1


def test_30_hidden_panel_guard(app):
    """Visibility prevents optional work even for a small editable document."""
    panel = QWidget()
    editor = QsciScintilla()
    editor.setText('small')
    panel.hide()
    assert not should_update_panel(panel, editor)
    panel.show()
    assert should_update_panel(panel, editor)
    panel.close()
````

**File responsibility:** Executable answers to the course's second exercise in each topic.

Run from the repository root with pytest. Qt tests use real widgets; the
offscreen platform lets Linux CI run them without a visible desktop.

<a id="file-tests-test-feature-models-py"></a>
#### CREATE FILE — `tests/test_feature_models.py`

**Folder:** `tests/` already exists. Create **only** `test_feature_models.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
"""Pure regression checks for the course's state and parser boundaries."""
from pathlib import Path
from tempfile import TemporaryDirectory

from code_inteligence.document_recovery import RecoveryStore
from code_inteligence.local_history import VersionStore
from code_inteligence.document_recovery import atomic_bytes
from markdown_editor.authoring_tools import broken_local_links
from markdown_editor.heading_navigation import markdown_headings
from code_inteligence.symbol_index import python_symbols
from markdown_editor.authoring_tools import relative_link
from code_inteligence.symbol_index import symbol_at
from markdown_editor.authoring_tools import table
from code_inteligence.text_comparison import three_way
from python_editor.lexer_checkpoints import LexerCheckpoints


def test_symbol_containment():
    """A method breadcrumb ends with its AST block, not the next class."""
    code = "class A:\n    def run(self):\n        return 1\nclass B:\n    pass\n"
    items = python_symbols(Path("a.py"), code)
    assert [s.name for s in symbol_at(items, 2)] == ["A", "run"]
    assert [s.name for s in symbol_at(items, 4)] == ["B"]


def test_markdown_headings_and_table():
    """Fenced headings are ignored and repeated slugs become unique."""
    headings = markdown_headings("# Setup\n```python\n# Not heading\n```\n# Setup")
    assert [h.slug for h in headings] == ["setup", "setup_1"]
    assert r"\|" in table([["a|b"], ["x"]])


def test_links_and_merge():
    """Local paths round-trip; divergent edits produce visible conflicts."""
    with TemporaryDirectory() as folder:
        root = Path(folder)
        source, image = root / "doc.md", root / "image name.png"
        image.write_bytes(b"png")
        link = relative_link(source, image, image=True, alt="screen")
        assert "image%20name.png" in link
        assert broken_local_links(source, link) == []
    text, conflict = three_way("base", "editor", "disk")
    assert conflict and "editor" in text and "disk" in text


def test_recovery_history_atomic():
    """Unsaved drafts and saved predecessors remain separate on disk."""
    with TemporaryDirectory() as folder:
        root = Path(folder)
        path = root / "test.py"
        atomic_bytes(path, b"before")
        history = VersionStore(root / "history", keep=2)
        history.record(path, path.read_bytes())
        atomic_bytes(path, b"after")
        recovery = RecoveryStore(root / "recovery")
        recovery.write("id-1", path, "dirty draft", python=True)
        assert history.versions(path)[0].read_bytes() == b"before"
        assert recovery.pending()[0]["text"] == "dirty draft"
        recovery.forget("id-1")
        assert not recovery.pending()


def test_checkpoint_invalidation():
    """Resumed scanner state matches a full scan after insertion and deletion."""
    from python_editor.custompythonlexer import _py_compute_state
    cache = LexerCheckpoints(verify=True)
    original = b"def f():\n    return 1\n" * 800
    for source in (original, original.replace(b"return 1", b"return 'value'", 1), original[:5000]):
        assert cache.state_before(source, len(source), _py_compute_state) == _py_compute_state(source, len(source))
````

**File responsibility:** Pure regression checks for the course's state and parser boundaries.

<a id="file-tests-test-completed-features-py"></a>
#### CREATE FILE — `tests/test_completed_features.py`

**Folder:** `tests/` already exists. Create **only** `test_completed_features.py` there. **Placement:** line 1 of the new file; set its entire contents to the following block. No new package directory or `__init__.py` is needed.

````python
"""Regression tests for production integrations missing from the source course."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import random
import sys
from time import monotonic, sleep
import pytest
from PyQt5.QtWidgets import QApplication
from python_editor.custompythonlexer import _py_compute_state, _py_style_chunk
from python_editor.lexer_checkpoints import LexerCheckpoints

@pytest.fixture(scope='module')
def app():
    """Keep one application alive while worker signals are delivered."""
    return QApplication.instance() or QApplication([])


def wait(app, predicate):
    """Pump Qt with a deadline so worker failures cannot hang the suite."""
    deadline = monotonic() + 15
    while not predicate() and monotonic() < deadline:
        app.processEvents()
        sleep(.002)
    assert predicate()


@pytest.mark.parametrize('backend', ['python', 'cython'])
def test_production_checkpoint_equivalence(backend):
    """Compare scanners and emitted styles across noncontiguous ranges and edits."""
    if backend == 'cython':
        native = pytest.importorskip('python_editor.lexer_fast')
        scan, style = native.compute_state_before, native.style_chunk
    else:
        scan, style = _py_compute_state, _py_style_chunk
    sample = '''class C:
    def method(self, x=(1,
                        2)):
        """A docstring with \\ paths and a ' quote."""
        text = f"prefix {dict(a='nested')} tail"
        return x  # comment
'''
    data = (sample * 120 + "text = '''unterminated\n" * 3).encode()
    cache = LexerCheckpoints(verify=True)
    randomizer = random.Random(42)
    for source in (data, data.replace(b'class C:', b'class Longer:', 1),
                   data.replace(b'docstring', b'\nchanged', 1), data[:-10], data):
        for target in [len(source), 0, *[randomizer.randrange(len(source)) for _ in range(40)]]:
            optimized = cache.state_before(source, target, scan)
            expected = scan(source, target)
            assert optimized == expected
            end = min(len(source), target + 139)
            assert style(source, target, end, optimized, set(), set(), set()) == style(
                source, target, end, expected, set(), set(), set())
    assert len(cache.states) > 1


def test_nonoverlapping_three_way_merge():
    """Merge separate edits and preserve both alternatives on overlapping edits."""
    from code_inteligence.text_comparison import three_way
    assert three_way('a\nb\nc\n', 'A\nb\nc\n', 'a\nb\nC\n') == ('A\nb\nC\n', False)
    merged, conflict = three_way('a\n', 'x\n', 'y\n')
    assert conflict and '<<<<<<< EDITOR' in merged and '>>>>>>> DISK' in merged


def test_shared_provider_results(app, tmp_path):
    """Execute all migrated provider kinds through real Jedi and the shared queue."""
    from code_inteligence.analysis_provider import evaluate
    from code_inteligence.analysis_cache import RequestKey
    from code_inteligence.analysis_scheduler import AnalysisQueue
    path = tmp_path / 'sample.py'
    source = 'def greet(value):\n    """Greeting documentation."""\n    return value\n\ngreet(1)\n'
    path.write_text(source)
    queue = AnalysisQueue()
    values = {}
    queue.ready.connect(lambda key, value: values.__setitem__(key.kind, value))
    positions = {'completion': (5, 3), 'signature': (5, 6), 'documentation': (5, 2),
                 'definition': (5, 2), 'references': (5, 2)}
    for kind, (line, column) in positions.items():
        key = RequestKey(str(path), 1, sys.executable, str(tmp_path), kind, 'doc', line, column)
        queue.submit(key, lambda k=key: evaluate(k, source))
    wait(app, lambda: len(values) == 5 and not queue.is_running())
    assert not any(isinstance(value, Exception) for value in values.values()), values
    assert 'greet' in values['completion']
    assert 'greet(value)' in values['signature']
    assert 'Greeting documentation' in values['documentation']
    assert values['definition'][1] == 1
    assert len(values['references']) >= 2
    queue.shutdown()


def test_structured_pytest_selection_and_failure(app, tmp_path):
    """Collect exact parameter IDs and rerun only the failed item in a real child."""
    from python_editor.test_session import TestSession
    test = tmp_path / 'test_nodes.py'
    test.write_text('import pytest\n@pytest.mark.parametrize("value", [0, 1])\ndef test_value(value):\n    assert value == 0\n')
    session = TestSession()
    events, exits = [], []
    session.event_ready.connect(events.append)
    session.finished.connect(exits.append)
    session.start(sys.executable, tmp_path, collect=True)
    wait(app, lambda: bool(exits))
    nodes = [e['nodeid'] for e in events if e['event'] == 'collected']
    assert nodes == ['test_nodes.py::test_value[0]', 'test_nodes.py::test_value[1]']
    events.clear(); exits.clear()
    session.start(sys.executable, tmp_path, [nodes[1]])
    wait(app, lambda: bool(exits))
    failures = [e['nodeid'] for e in events if e['event'] == 'result' and e['outcome'] == 'failed']
    assert failures == [nodes[1]] and exits == [1]
    events.clear(); exits.clear()
    session.start(sys.executable, tmp_path, collect=True)
    session.invalidate()
    wait(app, lambda: bool(exits))
    assert events == []


def test_rename_preserves_bom_crlf_and_mode(tmp_path):
    """Rename a Python identifier without changing UTF-8 BOM, CRLF, or mode bits."""
    from code_inteligence.symbol_rename import plan_rename, apply_rename
    path = tmp_path / 'sample.py'
    original = b'\xef\xbb\xbfvalue = 1\r\nprint(value)\r\n'
    path.write_bytes(original)
    path.chmod(0o640)
    edits = plan_rename(tmp_path, path, original.decode('utf-8-sig'), 0, 2, 'answer')
    apply_rename(edits)
    assert path.read_bytes() == b'\xef\xbb\xbfanswer = 1\r\nprint(answer)\r\n'
    assert path.stat().st_mode & 0o777 == 0o640


def test_markdown_grammar_and_reference_links(tmp_path):
    """Use actual Markdown parsing for heading IDs, fences, setext, and references."""
    from markdown_editor.document_model import parse_headings, rendered_links
    from markdown_editor.authoring_tools import broken_local_links
    source = '# Setup\n\n# Setup\n\nTitle\n=====\n\n```python\n# Hidden\n```\n\n[asset][a]\n\n[a]: target.md#setup\n'
    rows = parse_headings(source)
    assert [(r.title, r.slug) for r in rows] == [('Setup', 'setup'), ('Setup', 'setup_1'), ('Title', 'title')]
    assert rendered_links(source) == ['target.md#setup']
    path = tmp_path / 'note.md'
    (tmp_path / 'target.md').write_text('# Setup\n')
    assert broken_local_links(path, source) == []
    assert broken_local_links(path, '[bad](target.md#absent)')


def test_deferred_dock_and_hidden_rows(app):
    """Keep hidden presentation changes cheap, then display only the latest snapshot."""
    from PyQt5.QtWidgets import QMainWindow, QLabel
    from PyQt5.QtCore import Qt
    from side_bar_widgets.deferred_dock import DeferredDock
    from side_bar_widgets.snapshot_dock import SnapshotDock
    window = QMainWindow()
    calls = []
    dock = DeferredDock('Deferred', 'Deferred', lambda: calls.append(1) or QLabel('Ready'), window)
    window.addDockWidget(Qt.RightDockWidgetArea, dock)
    dock.hide()
    assert calls == []
    assert dock.ensure() is dock.ensure() and calls == [1]
    rows = SnapshotDock('Rows', 'RowsDock', window)
    window.addDockWidget(Qt.LeftDockWidgetArea, rows)
    rows.hide()
    rows.set_rows([('First', 'a.py', 0, 0)], 'Empty')
    rows.set_rows([('Latest', 'b.py', 1, 0)], 'Empty')
    assert rows.tree.topLevelItemCount() == 0
    window.show(); rows.show(); app.processEvents()
    assert rows.tree.topLevelItemCount() == 1
    assert rows.tree.topLevelItem(0).text(0) == 'Latest'
    window.close()
````

**File responsibility:** Regression tests for production integrations missing from the source course.

### Commands

Run from the repository root after installing the modules and integration changes:

```bash
python -m pytest -q tests/test_feature_exercises.py tests/test_feature_models.py tests/test_completed_features.py
python main.py
```

For a headless Linux test run, set `QT_QPA_PLATFORM=offscreen` in the test environment. Use the normal desktop environment for the interactive acceptance checks.

### Evidence collected for this guide

- **43 tests passed** in the isolated implementation, including both the pure-Python and compiled Cython checkpoint-equivalence cases.
- The native extension compiled successfully with GCC and reported API version 2.
- A real PyQt5/QScintilla/MainWindow check exercised Markdown and Python templates, deferred bodies, Tests and run-output docks, density changes, focus escape, saved layouts, and clean asynchronous shutdown.
- Real Qt WebEngine loaded its preview shell in that check. Repeated rendering exposed a JavaScript top-level `const` redeclaration issue; the supplied `render_preview` fixes it by wrapping each update in a local function scope. That final scope-only correction was reviewed in the code, not subjected to another desktop run.

Tests ran with Python 3.12, PyQt5 5.15.11, QScintilla 2.14.1, Jedi 0.20.0, pytest 8.4.2, Python-Markdown 3.11, and Cython 3.3.0. This records the verification environment; it does not replace the repository's dependency ranges with new pins.

Windows terminal/PowerShell behavior, multi-monitor desktop geometry, and native packaging on other operating systems were not exercised here. The automated cases are evidence for their specific behaviors, not a claim that every UI path has been exhaustively tested.

### Final desktop acceptance checklist

1. Start the editor, reopen recent files/projects, create templates, and close every tab back to the welcome screen.
2. Switch density and layouts; verify sidebar icons and keyboard focus; enter and leave focus mode using its registered shortcut.
3. Save UTF-8/BOM and LF/CRLF files; compare disk changes; restore a recovery draft and a selected local-history draft.
4. Exercise cross-file rename and reject a stale preview; navigate symbols, definitions, references, Problems rows, outline entries, and the minimap.
5. Collect tests, run a parameterized selection, rerun failed, stop a run, and change workspace. Run a separate named profile and inspect its own output.
6. Verify links, duplicate heading anchors, images, tables, and repeated preview rendering. Hide panels while editing, then show current results.
7. Open a large file, test the per-tab override, enable/disable diagnostics, and close the application during pending analysis/process work.

### Behavior boundaries

Recovery is a periodic local snapshot and cannot recover edits made after its latest snapshot. Local history is bounded and is not a replacement for Git. Rename performs per-file atomic replacement with best-effort rollback; it is not a multi-file filesystem transaction, and another process can still write concurrently. The minimap is a navigation silhouette, not a second syntax-rendered editor. Local-link checking does not crawl network URLs. These boundaries describe the implemented behavior; none is an omitted integration step.

## Applying future repository changes

Keep the pinned baseline in review notes. When the upstream repository changes, rebase by named definitions and preserve any newer document-lifecycle fixes. Rebuild the native extension after modifying its snapshot contract. When adding a new command, register its QAction; when adding analysis, submit immutable work to the shared queue and include all relevant context in RequestKey; when adding an optional panel, separate retained data from visible presentation work.

