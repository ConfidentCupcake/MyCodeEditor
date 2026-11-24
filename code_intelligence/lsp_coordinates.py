"""Convert negotiated LSP offsets without accessing editor widgets."""


def lsp_to_character(text: str, column: int, encoding: str) -> int:
    """Map a nonnegative LSP column to a Python/QScintilla character index.

    text is one line without CR/LF. Columns inside a multibyte character or
    surrogate pair round down to the preceding complete character. Oversized
    columns clamp to the line length. Invalid types/encodings raise ValueError
    rather than accidentally treating UTF-16 units as UTF-8 bytes.
    """
    if type(column) is not int or column < 0:
        raise ValueError("LSP column must be a nonnegative integer")
    if encoding == "utf-8":
        return len(text.encode("utf-8")[:column].decode("utf-8", errors="ignore"))
    if encoding == "utf-16":
        return len(text.encode("utf-16-le")[:column * 2].decode("utf-16-le", errors="ignore"))
    if encoding == "utf-32":
        return min(column, len(text))
    raise ValueError(f"Unsupported LSP position encoding: {encoding}")