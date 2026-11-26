import sys
from pathlib import Path

from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QKeyEvent

from code_intelligence.snippet_controller import SnippetController
from code_intelligence.folding_controller import FoldingController
from markdown_editor.markdowncustomlexer import MarkdownCustomLexer
from side_bar_widgets.editor_minimap import EditorMinimap
 

class MarkdownEditor(QsciScintilla):
    focused = pyqtSignal(object)
    def __init__(self, parent=None, path: Path=None, is_python_file: bool=False):
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
        # Correctly matched brackets
        self.setMatchedBraceForegroundColor(QColor("#FFFFFF"))
        self.setMatchedBraceBackgroundColor(QColor("#6040A0"))
        # Unmatched brackets
        self.setUnmatchedBraceForegroundColor(QColor("#FFFFFF"))
        self.setUnmatchedBraceForegroundColor(QColor("#8B2028"))
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
        self.minimap = EditorMinimap(self)
        self.folding_controller = FoldingController(self, "markdown")
        self.snippets = SnippetController(self)

    def _apply_theme_editor_style(self):
        """
        Push the theme's editor-section styling onto this widget.

        Mirrors PythonEditor._apply_theme_editor_style — called at the end
        of __init__ and again by main.py's _apply_editor_settings() after
        a lexer swap (fresh lexers reset the style table, which would
        otherwise wipe the margin colors / gutter-turns-white bug).

        Everything is read THROUGH the lexer so the theme file stays the
        single source of truth for editor-wide styling.
        """
        lexer = self.md_lexer
        f = lexer.editor_font()
        self.setFont(f)
        self.setMarginsFont(f)
        self.setPaper(lexer.defaultPaper())
        self.setCaretForegroundColor(
            lexer.editor_color("caret-color", "#f31122"))
        self.setCaretLineBackgroundColor(
            lexer.editor_color("caret-line-background", "#3d424d"))
        self.setMarginsForegroundColor(
            lexer.editor_color("margin-foreground", "#ff888888"))
        self.setMarginsBackgroundColor(
            lexer.editor_color("margin-background", "#1e1f22"))
        self.setMatchedBraceForegroundColor(QColor("#FFFFFF"))
        self.setMatchedBraceBackgroundColor(QColor("#6040A0"))
        self.setUnmatchedBraceBackgroundColor(QColor("#FFFFFF"))
        self.setUnmatchedBraceForegroundColor(QColor("#8B2028"))

    # No need to assign any function to handle key press, this overloads the function from base class
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Consume active snippet navigation keys, then preserve existing completion and editing behavior."""
        if event.key() == Qt.Key.Key_Tab and self.snippets.handle_tab(False):
            return
        if event.key() == Qt.Key.Key_Backtab and self.snippets.handle_tab(True):
            return
        if event.key() == Qt.Key.Key_Escape and self.snippets.active:
            self.snippets.cancel()
            return
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Space:
            self.autoCompleteFromAll()
        else:
            return super().keyPressEvent(event)
            
    def setTextSafely(self, text:str):
        self._loading_text = True
        invalidate = getattr(getattr(self, "md_lexer", None), "_invalidate_source", None)
        if invalidate is not None:
            invalidate()
        previous_blocked = self.blockSignals(True)
        try:
            self.setText(text)
            self.setModified(False)
        finally:
            # A load suppresses textChanged, so refresh the lexer explicitly.
            # Repeat after setText in case styling was requested during the load.
            if invalidate is not None:
                invalidate()
            self.blockSignals(previous_blocked)
            self._loading_text = False
        self.recolor()
            
        self.folding_controller.schedule()
        self.minimap.schedule_refresh()
            
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focused.emit(self)
        
    def shutdown(self):
        self.minimap.shutdown()
        self.folding_controller._timer.stop()
        self.snippets.cancel()
        self._shutting_down = True
