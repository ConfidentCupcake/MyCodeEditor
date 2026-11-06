from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any


class DiagnosticSeverity(IntEnum):
    """Define application-level severity ordering independently of provider numeric values."""
    INFORMATION: int = 1
    WARNING: int = 2
    ERROR: int = 3
    
    
@dataclass
class Position:
    """Zero-based line and Python-character column."""
    line: int
    column: int
    

@dataclass
class SourceRange:
    """Store a zero-based half-open range using Python-character columns."""
    start: Position
    end: Position
    

@dataclass
class Diagnostic:
    """Carry provider-neutral diagnostic data while retainen an opaque provider payload for actions."""
    provider: str
    uri: str
    path: Path | None
    source_range: SourceRange
    severity: DiagnosticSeverity
    code: str
    message: str
    revision: int | None = None
    provider_data: Any = field(default=None, compare=False, repr=False)
    
