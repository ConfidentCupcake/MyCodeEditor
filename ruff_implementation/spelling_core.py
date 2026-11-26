# Snapshot-only English/German spelling; this module never accesses Qt widgets.
from __future__ import annotations

import builtins
import io
import keyword
import re
import tokenize
from concurrent.futures import CancelledError
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

WORD = re.compile(r"[^\W\d_]+", re.UNICODE)
INLINE_CODE = re.compile(r"`[^`\n]*`")
IGNORED = frozenset(word.casefold() for word in [*keyword.kwlist, *dir(builtins)])



@dataclass(frozen=True)
class SpellingResult:
    """Immutable findings plus whether tokenization completed and the cap was hit."""
    findings: tuple[tuple[int, int, int, str], ...]
    complete: bool = True
    limited: bool = False


@lru_cache(maxsize=1)
def dictionary():
    """Load both bundled dictionaries once, on the serialized worker thread.

    Import lazily so pure range tests can inject a vocabulary without requiring
    the package. Membership checks never generate expensive correction candidates.
    """
    from spellchecker import SpellChecker
    return SpellChecker(language=["en", "de"], distance=1)
    

def pieces(text: str):
    """Yield (start, end, word) for snake/camel/acronym parts in original text.
    
    Underscore and digits separate WORD matches. A lower->upper transition or 
    the last capital before lowercase starts a camel part: HTTPServer becomes 
    HTTP + Server. Offsets are Python characters, never encoded byte counts.
    """
    for match in WORD.finditer(text):
        word = match.group()
        cuts = [0]
        for index in range(1, len(word)):
            current, previous = word[index], word[index - 1]
            next_lower = index + 1 < len(word) and word[index + 1].islower()
            if current.isupper() and (previous.islower() or (previous.isupper() and next_lower)):
                cuts.append(index)
        cuts.append(len(word))
        for start, end in zip(cuts, cuts[1:]):
            yield match.start() + start, match.start() + end, word[start:end]


def regions(source: str, markdown: bool):
    """Yield source-position natural-language regions, retaining original offsets.
    
    Markdown stays unchanged. For Python, check comments, docstrings and sentence-
    like string literals. Skip identifiers, bytes, raw literals, and single-word/
    configuration values. Avoid interpreting f-string expressions.
    """
    if markdown:
        for line, text in enumerate(source.splitlines()):
            yield line, 0, text
        return
    
    fstring_middle = getattr(tokenize, "FSTRING_MIDDLE", - 1)
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            # Remove the comment marker, while keeping absolute columns correction.
            text = token.string[1:]
            offset = 1
            # Linter pragnas and encoding declarations aren't human prose.
            if text.lstrip().lower().startswith(("noqa", "type:", "pyright", "pylint:", "ruff:", "fmt:", "isort:", "coding:", "region", "endregion")):
                continue
        elif token.type == tokenize.STRING:
            opening = re.match(r"(?i:([rubf]*))(\"\"\"|'''|\"|')", token.string)
            if opening is None:
                continue
            prefix, quote = opening.group(1).lower(), opening.group(2)
            if "b:" in prefix or "r" in prefix:
                continue
            text = token.string[opening.end():-len(quote)]
            offset = opening.end()
            # A single quoted technical value is typically an identifier or 
            # configuration item, not text for spellchecking.
            if len(quote) == 1 and not any(char.isspace() for char in text):
                continue
        
        elif token.type == fstring_middle:
            text = token.string
            offset = 0
            if not any(char.isspace() for char in text):
                continue
            
        else:
            continue
        
        for extra, row in enumerate(text.splitlines()):
            base = token.start[1] + offset if extra == 0 else 0
            yield token.start[0] - 1 + extra, base, row
        

def _is_technical_atom(atom: str) -> bool:
    """Reject individual programming tokens within otherwise prose-like regions.

    The scanner does not try to infer whether a whole comment is code.
    Instead, skip obvious code atoms (filenames, escapes, identifiers, paths, Unicode/UTF
    notations, numertical constants and all-caps acronyms
    """
    value = atom.strip(',.:;!?()[]{}"\'')
    if not value:
        return True
    if any(char in value for char in "_./\\`<>=%@"):
        return True
    if any(char.isdigit() for char in value):
        return True
    if len(value) > 1 and value.isupper():
        return True
    if re.search(r"[a-z][A-Z]", value):
        return True
    if "-" in value:
        return True
    return False

def check_words(source: str, markdown: bool, allow=frozenset(), known=None, cancelled=None, limit: int = 500) -> SpellingResult:
    """Check an immutable snapshot and return exact character ranges."""
    if known is None:
        spell = dictionary()
        known = lambda word: bool(spell.known([word]))
    accepted = IGNORED | frozenset(word.casefold() for word in allow)
    decisions = {}
    results = []
    try:
        for line, base, text in regions(source, markdown):
            if cancelled is not None and cancelled.is_set():
                raise CancelledError()
            if text.casefold() in accepted:
                continue
            # Preserve offsets while masking inline `code spans` in Python prose.
            scanned = (INLINE_CODE.sub(lambda match: " " * len(match.group()), text)
                       if not markdown else text)
            # Process each whitespace-delimited atom once. In Python prose,
            # never report words extracted from obvious technical atoms.
            for atom_match in re.finditer(r"\S+", scanned):
                atom = atom_match.group()
                if not markdown and _is_technical_atom(atom):
                    continue
                for match in WORD.finditer(atom):
                    whole = match.group()
                    if whole.casefold() in accepted:
                        continue
                    for start, end, word in pieces(whole):
                        if cancelled is not None and cancelled.is_set():
                            raise CancelledError()
                        folded = word.casefold()
                        if len(word) < 2 or folded in accepted:
                            continue
                        if folded not in decisions:
                            decisions[folded] = bool(known(folded))
                        if not decisions[folded]:
                            column = base + atom_match.start() + match.start()
                            results.append((line, column + start, column + end, word))
                            if len(results) >= limit:
                                return SpellingResult(tuple(results), limited=True)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return SpellingResult(tuple(results), complete=False)
    return SpellingResult(tuple(results))


def scan(source: str, markdown: bool, root: Path, cancelled) -> SpellingResult:
    """Read the project allow-list in the worker, then inspect the supplied text.
    
    File errors propagate to the GUI as infrastructure messages. No editor,
    document or QObject is passed here. Reloading vocabulary does not require
    reconstructing the large bundled dictionaries.
    """
    if cancelled.is_set():
        raise CancelledError()
    path = Path(root) / ".markdowneditor-spelling.txt"
    allow = frozenset()
    if path.exists():
        allow = frozenset(line.strip().casefold() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#"))
    return check_words(source, markdown, allow=allow, cancelled=cancelled)
        