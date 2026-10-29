# Validated icon access for existing bundled SVG assets.

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
        icon.addFile(str(selected), mode=QIcon.Normal, state=QIcon.on)
    return icon
    
    
    