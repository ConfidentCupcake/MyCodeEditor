# Provider-owned squiggles using the editor's existing diagnostic colors
from PyQt5 import sip
from PyQt5.QtGui import QColor
from ruff_implementation.diagnostics_model import DiagnosticSeverity


class DiagnosticLayer:
    """Define per-view styles and paint shared-document ranges for one provider.
    
    Basedpyright owns indicator 24/25/26. Spelling owns indicator 28. Ruff keeps
    20-23. These are indicator IDs, not folding-marker IDs. This class changes
    no lexer style or syntax colour and isntalls no second hover/action handler.
    """
    
    def __init__(self, editor, provider: str) -> None:
        """Configure only this provider's styles on one live QScintilla view."""
        self.editor = editor
        self.indicators = ({DiagnosticSeverity.ERROR: 24, DiagnosticSeverity.WARNING: 25, DiagnosticSeverity.INFORMATION: 26} if provider == "basedpyright" else {severity: 28 for severity in DiagnosticSeverity})
        colors =  {DiagnosticSeverity.ERROR: "#ff5c57", DiagnosticSeverity.WARNING: "#ffbd2e", DiagnosticSeverity.INFORMATION: "#55aaff"}
        
        for severity, indicator in self.indicators.items():
            editor.indicatorDefine(editor.SquiggleIndicator, indicator)
            editor.setIndicatorForegroundColor(QColor(colors[severity] if provider == "basedpyright" else "#55aaff"), indicator)
            
    
    def clear(self) -> None:
        """Clear this provider's shared bytes ranges without touching other ID's"""
        editor = self.editor
        for indicator in set(self.indicators.values()):
            editor.SendScintilla(editor.SCI_SETINDICATORCURRENT, indicator)
            editor.SendScintilla(editor.SCI_INDICATORCLEARRANGE, 0, editor.length())
    
    
    def render(self, rows) -> None:
        """Replace one successful snapshot; an empty list removes old squiggles."""
        self.clear()
        editor = self.editor
        for row in rows:
            a, b = row.source_range.start, row.source_range.end
            start = editor.positionFromLineIndex(a.line, a.column)
            end = editor.positionFromLineIndex(b.line, b.column)
            if end <= start:
                continue # Keep point diagnostic in Problems; do not invent a byte ranges
            editor.SendScintilla(editor.SCI_SETINDICATORCURRENT, self.indicators[row.severity])
            editor.SendScintilla(editor.SCI_INDICATORFILLRANGE, start, end - start)


def configure_document(document, provider: str) -> None:
    """Give newly created split views the provider's styles without repainting text."""
    for view in list(document.views):
        if sip.isdeleted(view):
            continue
        layers = getattr(view, "_diagnostic_layers", None)
        if layers is None:
            layers = view._diagnostic_layers = {}
        if provider not in layers:
            layers[provider] = DiagnosticLayer(view, provider)


def paint_document(document, provider: str, rows) -> None:
    """Configure every live view, then mutate shared ranges through one owner."""
    configure_document(document, provider)
    owner = document.analysis_owner
    if owner is not None and not sip.isdeleted(owner):
        owner._diagnostic_layers[provider].render(rows)