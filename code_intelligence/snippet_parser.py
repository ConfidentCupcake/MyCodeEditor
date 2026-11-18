# Parse the supported '${number:default}' snippet syntax.

from __future__ import annotations

import re
from dataclasses import dataclass

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
    rendered_length: int = 0
    source_end: int = 0
    
    for match in _PLACEHOLDER.finditer(source):
        literal = source[source_end:match.start()]
        default = match.group(2)
        chunks.extend((literal, default))
        rendered_length += len(literal)
        start = rendered_length
        placeholders.append(Placeholder(int(match.group(1)), start, rendered_length))
        source_end = match.end()
        
    chunks.append(source[source_end:])
    placeholders.sort(key=lambda item: (item.number == 0, item.number, item.start))
    return ParsedSnippet("".join(chunks), tuple(placeholders))
    