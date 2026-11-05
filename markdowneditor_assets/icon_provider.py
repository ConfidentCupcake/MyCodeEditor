"""State-aware SVG icons from the existing application asset package."""
from functools import lru_cache
from pathlib import Path
from PyQt5.QtGui import QIcon
from markdowneditor_assets import asset_path

ALLOWED = frozenset({'folder', 'search', 'outline', 'terminal', 'console', 'settings'})

@lru_cache(maxsize=6)
@lru_cache(maxsize=64)
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