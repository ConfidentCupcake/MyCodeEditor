# Pure version correlation and strict UTF-16 diagnostic conversation.
from __future__ import annotations
from collections.abc import Callable
from typing import Any

from ruff_implementation.diagnostics_model import Diagnostic, DiagnosticSeverity, Position, SourceRange


class TypeVersions:
    """Assign unique wire revisions independently of a buffer's local counter.
    
    A close and reopened file can reuse its URI and local revision. A fresh
    wire number prevents the earlier file's delayed reply matching that state.
    This object belongs to the GUI thread; reset never rewinds its counter.
    """
    
    def __init__(self) -> None:
        """Start en empty ledger; the first issued wire version will be one."""
        self.next_version = 0
        self.sent: dict[str, tuple[Any, int, int]] = {}
        
    def issue(self, uri: str, owner: Any, local_revision: int) -> int:
        """Record an outgoing snapshot and return its increasing LSP version."""
        self.next_version += 1
        self.sent[uri] = (owner, local_revision, self.next_version)
        return self.next_version
    
    def is_sent(self, uri: str, owner: Any, local_revision: int) -> bool:
        """Whether this exact owner/revision already has a submitted snapshot."""
        value = self.sent.get(uri)
        return value is not None and value[0] is owner and value[1] == local_revision
    
    def accepts(self, uri: str, owner: Any, local_revision: int, wire_revision: Any) -> bool:
        """Require explicit integer version equality and the current owner."""
        return (type(wire_revision) is int and self.is_sent(uri, owner, local_revision) and self.sent[uri][2] == wire_revision)
    
    def forget(self, uri:str) -> None:
        """Retire one document without reusing its previous wire version."""
        self.sent.pop(uri, None)
        
    
    def reset(self) -> None:
        """Retire all sent identities after a process restart, keeping monotonicity."""
        self.sent.clear()
        

def utf16_position(raw: Any, line_count: int, line_text: Callable[[int], str]) -> Position:
    """Convert a validated LSP point into a Python-character column.
    
    line_text is called only for the affected line. Reject negative/out-of-line
    coordinates and offsets inside surrogate pairs. Never clamp a malformed 
    position onto unrelated source text. ValueError means reject the snapshot.
    """
    if not isinstance(raw, dict):
        raise ValueError("Position must be an object")
    line, units = raw.get("line"), raw.get("character")
    if type(line) is not int or type(units) is not int or not 0 <= line < line_count or units < 0:
        raise ValueError("Invalid line or UTF-16 column")
    text = line_text(line).rstrip("\r\n")
    encoded = text.encode("utf-16-le")
    if units * 2 > len(encoded):
        raise ValueError("Column exceeds line")
    try:
        prefix = encoded[:units * 2].decode("utf-16-le")
    except UnicodeDecodeError as error:
        raise ValueError("Column splits a surrogate pair") from error
    return Position(line, len(prefix))

def convert_types(rows: Any, uri: str, path: Any, revision: int, line_count: int, line_text: Callable[[int], str]) -> list[Diagnostic]:
    """Convert a complete snapshot or reject it before any GUI publication.
    
    Input ranges use UTF-16; application rages use Python characters. Severity
    numbers are explicitly mapped because LSP's ordering differs from ours.
    The raw payload is retained for later inspection, not automatic code actions.
    """
    if not isinstance(rows, list):
        raise ValueError("Diagnostic must be a list")
    result = []
    cache: dict[int, str] = {}
    
    def cached_line(line: int) -> str:
        """Reach each referenced widget line at most once for this snapshot."""
        if line not in cache:
            cache[line] = line_text(line)
        return cache[line]
    
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("message"), str):
            raise ValueError("Invalid diagnostic message")
        span = row.get("range")
        if not isinstance(span, dict):
            raise ValueError("Invalid diagnostic range")
        start = utf16_position(span.get("start"), line_count, cached_line)
        end = utf16_position(span.get("end"), line_count, cached_line)
        if (end.line, end.column) < (start.line, start.column):
            raise ValueError("Reversed diagnostic range")
        severity = row.get("severity", 3)
        if type(severity) is not int or severity not in (1, 2, 3, 4):
            raise ValueError("Invalid diagnostic severity")
        
        result.append(Diagnostic("basedpyright", uri, path, SourceRange(start, end),
            {1: DiagnosticSeverity.ERROR, 2: DiagnosticSeverity.WARNING,
             3: DiagnosticSeverity.INFORMATION, 4: DiagnosticSeverity.INFORMATION}[severity],
            str(row.get("code", "type")), row["message"], revision, row))
    return result
       
        
        
        
    
    
    