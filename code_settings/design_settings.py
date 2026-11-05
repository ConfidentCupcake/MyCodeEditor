"""Shared interface colors; document syntax colors remain lexer-owned."""
from __future__ import annotations
from typing import Any
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

def theme_qss(density: str='comfortable', tokens: Any=None) -> Any:
    """Generate fresh QSS; callers append it to the original base exactly once."""
    if density not in {'compact', 'comfortable'}:
        raise ValueError(f'Unsupported density: {density}')
    t = tokens or DesignTokens()
    pad = 3 if density == 'compact' else 7
    # Scope panel backgrounds so Scintilla and terminal surfaces keep their themes.
    return f"""
    QWidget[designPanel="true"] {{ background: {t.surface}; color: {t.foreground}; }}
    QDialog, QDockWidget {{ background: {t.surface}; color: {t.foreground}; }}
    QLineEdit, QListWidget, QTreeWidget, QPlainTextEdit {{ background: {t.paper}; color: {t.foreground}; selection-background-color: {t.accent}; }}
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