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
    