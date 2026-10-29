# MarkdownEditor: diagnostics and highlighting implementation guide


This guide uses the source in [commit `b26bf8df9b6c`](https://github.com/ConfidentCupcake/MarkdownEditor/tree/b26bf8df9b6c99153a3591a258c368256c8d2590), the version pushed as “Something bad with Basedpyright”. All paths below are relative to that repository root. Line numbers refer to that source before edits; use the class/method name as the stable location after earlier edits shift lines.


Apply one topic completely, restart with `python main.py`, and check its result before continuing. Topics 1, 2 and 5 address separate causes. Topic 3 uses the Qt helpers from Topic 2. Topic 4 requires Topics 2 and 3 because diagnostic retention crosses the window, Ruff controller and basedpyright service. There is no `editor_extensions.py` or `EditorExtensions` class.


**What is and is not established:** the screenshot’s resumed string-colouring defect is reproduced and corrected in both lexer engines. The LSP framing/settings defects are reproduced and corrected. The menu/model/enum fixes remove many Qt-related findings. These are tested corrections, not a claim that the entire repository is free of errors. The final verification section identifies remaining findings and the Windows verification boundary.


## Topic 1 — Correct triple-quoted strings in incremental highlighting


### Explanation and documentation


The syntax lexer and language servers are separate systems. Ruff/basedpyright publish diagnostics; the custom lexer assigns token colors. In the pushed lexer, a triple-quoted string could close on the opposite quote character. The regular expression in `ruff_implementation/spelling_diagnostics.py` contains exactly that combination. When styling resumes at `@dataclass`, the old state scanner reports that the decorator is inside a string. Changing both the state scanner and string-run scanner fixes this reproduction.


Both implementations must change: `custompythonlexer.py` is the fallback and `lexer_fast.pyx` is the compiled implementation. Updating only the Python copy has no effect when an older native extension is imported. The private editor-reference rename also preserves the inherited Qt `editor()` method.


Documentation: [Python string literals](https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals), [Scintilla styling and byte positions](https://www.scintilla.org/ScintillaDoc.html#Styling), [Cython compilation](https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html).


### 1.1. `python_editor/custompythonlexer.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `except ImportError:` (original line 19).


```python
    _cython_style = None
    _cython_state = None
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 1.1.1 Existing method/function `_py_compute_state`

Only the opening quote character can terminate this triple-quoted string. The run scanner also stops only at that delimiter or a backslash; otherwise an opposite quote can both corrupt the resume state and prevent the scanner from advancing.


**Old version — original lines 114–300:**


```python
def _py_compute_state(text, target_pos):
    """Scan from byte 0 to target_pos and return the packed lexer state.
    `text` must be a bytes object; all positions/lengths are byte-based."""
    target_pos = min(target_pos, len(text))
    length = len(text)
    i = 0
    in_string = in_comment = triple_string = 0
    string_delim = ""
    in_fstring = escape_next = in_fexpr = fexpr_depth = is_docstring = 0
    bracket_depth = pending_def = pending_class = 0
    expect_docstring = at_class_body = 0

    while i < target_pos:
        c = text[i:i + 1].decode("latin-1")

        if in_fexpr:
            if c == "}":
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                i += 1
                continue
            if c == "{":
                fexpr_depth += 1
                i += 1
                continue
            if c in "frb" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") in "\"'":
                # decode to a 1-char string — bytes indexing gives an int here
                delim = text[i + 1:i + 2].decode("latin-1")
                i += 2
                if i + 1 < length and text[i:i + 1].decode("latin-1") == delim and text[i + 1:i + 2].decode("latin-1") == delim:
                    i += 2
                    i = _py_skip_string(text, i, target_pos, delim, True)
                else:
                    i = _py_skip_string(text, i, target_pos, delim, False)
                continue
            if c in "\"'":
                delim = c
                i += 1
                if i + 1 < length and text[i:i + 1].decode("latin-1") == delim and text[i + 1:i + 2].decode("latin-1") == delim:
                    i += 2
                    i = _py_skip_string(text, i, target_pos, delim, True)
                else:
                    i = _py_skip_string(text, i, target_pos, delim, False)
                continue
            i += 1
            continue

        if in_comment:
            if c in "\n\r":
                in_comment = 0
            i += 1
            continue

        if in_string:
            if escape_next:
                escape_next = 0
                i += 1
                continue
            if c == "\\":
                escape_next = 1
                i += 1
                continue
            if triple_string:
                if c in "\"'":
                    if i + 2 < length and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                        in_string = triple_string = string_delim = 0
                        in_fstring = is_docstring = 0
                        i += 3
                        continue
                    i += 1
                    continue
                if in_fstring and c == "{":
                    if i + 1 < length and text[i + 1:i + 2].decode("latin-1") == "{":
                        i += 2
                        continue
                    in_fexpr = 1
                    fexpr_depth = 1
                    i += 1
                    continue
                i += 1
                continue
            if c == string_delim:
                in_string = string_delim = in_fstring = is_docstring = 0
                i += 1
                continue
            if in_fstring and c == "{":
                if i + 1 < length and text[i + 1:i + 2].decode("latin-1") == "{":
                    i += 2
                    continue
                in_fexpr = 1
                fexpr_depth = 1
                i += 1
                continue
            i += 1
            continue

        # not in string/comment
        if c in "frb" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") in "\"'":
            next_c = text[i + 1:i + 2].decode("latin-1")
            if i + 3 < length and text[i + 2:i + 3].decode("latin-1") == next_c and text[i + 3:i + 4].decode("latin-1") == next_c:
                in_string = triple_string = 1
                string_delim = next_c
                in_fstring = 1 if c == "f" else 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 4
                continue
            in_string = 1
            triple_string = 0
            string_delim = next_c
            in_fstring = 1 if c == "f" else 0
            expect_docstring = 0
            i += 2
            continue

        if c in "\"'":
            if i + 2 < length and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                in_string = triple_string = 1
                string_delim = c
                in_fstring = 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 3
                continue
            in_string = 1
            triple_string = 0
            string_delim = c
            in_fstring = 0
            expect_docstring = 0
            i += 1
            continue

        if c == "#":
            in_comment = 1
            i += 1
            continue

        if c in "([{":
            bracket_depth += 1
            i += 1
            continue
        if c in ")]}":
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        if c == ":":
            if bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = pending_class = 0
            i += 1
            continue

        if c == "-" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") == ">":
            i += 2
            continue

        if c.isalpha() or c == "_":
            start = i
            i += 1
            while i < target_pos and (text[i:i + 1].decode("latin-1").isalnum() or text[i:i + 1].decode("latin-1") == "_"):
                i += 1
            word = text[start:i].decode("utf-8", errors="replace")
            if word == "def":
                pending_def = 1
                pending_class = 0
                at_class_body = 0
            elif word == "class":
                pending_class = 1
                pending_def = 0
                at_class_body = 0
            else:
                expect_docstring = 0
            continue

        i += 1

    return _py_pack_state(in_string, in_comment, triple_string, string_delim,
                          in_fstring, escape_next, in_fexpr, fexpr_depth,
                          is_docstring, expect_docstring, at_class_body)
```


**New version:**


```python
def _py_compute_state(text, target_pos):
    """Reconstruct lexical state at a byte offset before incremental styling.

    Args:
        text: Complete source encoded as UTF-8 bytes.
        target_pos: Byte offset at which styling will resume, clamped to EOF.

    Returns:
        Packed integer state describing strings, comments, f-string expressions
        and docstring context at that offset. A triple string closes only with
        three copies of its opening quote character; the other quote is data.
    """
    target_pos = min(target_pos, len(text))
    length = len(text)
    i = 0
    in_string = in_comment = triple_string = 0
    string_delim = ""
    in_fstring = escape_next = in_fexpr = fexpr_depth = is_docstring = 0
    bracket_depth = pending_def = pending_class = 0
    expect_docstring = at_class_body = 0

    while i < target_pos:
        c = text[i:i + 1].decode("latin-1")

        if in_fexpr:
            if c == "}":
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                i += 1
                continue
            if c == "{":
                fexpr_depth += 1
                i += 1
                continue
            if c in "frb" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") in "\"'":
                # decode to a 1-char string — bytes indexing gives an int here
                delim = text[i + 1:i + 2].decode("latin-1")
                i += 2
                if i + 1 < length and text[i:i + 1].decode("latin-1") == delim and text[i + 1:i + 2].decode("latin-1") == delim:
                    i += 2
                    i = _py_skip_string(text, i, target_pos, delim, True)
                else:
                    i = _py_skip_string(text, i, target_pos, delim, False)
                continue
            if c in "\"'":
                delim = c
                i += 1
                if i + 1 < length and text[i:i + 1].decode("latin-1") == delim and text[i + 1:i + 2].decode("latin-1") == delim:
                    i += 2
                    i = _py_skip_string(text, i, target_pos, delim, True)
                else:
                    i = _py_skip_string(text, i, target_pos, delim, False)
                continue
            i += 1
            continue

        if in_comment:
            if c in "\n\r":
                in_comment = 0
            i += 1
            continue

        if in_string:
            if escape_next:
                escape_next = 0
                i += 1
                continue
            if c == "\\":
                escape_next = 1
                i += 1
                continue
            if triple_string:
                # Only the opening quote kind can close this triple string.
                if c == string_delim:
                    if i + 2 < length and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                        in_string = triple_string = string_delim = 0
                        in_fstring = is_docstring = 0
                        i += 3
                        continue
                    i += 1
                    continue
                if in_fstring and c == "{":
                    if i + 1 < length and text[i + 1:i + 2].decode("latin-1") == "{":
                        i += 2
                        continue
                    in_fexpr = 1
                    fexpr_depth = 1
                    i += 1
                    continue
                i += 1
                continue
            if c == string_delim:
                in_string = string_delim = in_fstring = is_docstring = 0
                i += 1
                continue
            if in_fstring and c == "{":
                if i + 1 < length and text[i + 1:i + 2].decode("latin-1") == "{":
                    i += 2
                    continue
                in_fexpr = 1
                fexpr_depth = 1
                i += 1
                continue
            i += 1
            continue

        # not in string/comment
        if c in "frb" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") in "\"'":
            next_c = text[i + 1:i + 2].decode("latin-1")
            if i + 3 < length and text[i + 2:i + 3].decode("latin-1") == next_c and text[i + 3:i + 4].decode("latin-1") == next_c:
                in_string = triple_string = 1
                string_delim = next_c
                in_fstring = 1 if c == "f" else 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 4
                continue
            in_string = 1
            triple_string = 0
            string_delim = next_c
            in_fstring = 1 if c == "f" else 0
            expect_docstring = 0
            i += 2
            continue

        if c in "\"'":
            if i + 2 < length and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                in_string = triple_string = 1
                string_delim = c
                in_fstring = 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 3
                continue
            in_string = 1
            triple_string = 0
            string_delim = c
            in_fstring = 0
            expect_docstring = 0
            i += 1
            continue

        if c == "#":
            in_comment = 1
            i += 1
            continue

        if c in "([{":
            bracket_depth += 1
            i += 1
            continue
        if c in ")]}":
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        if c == ":":
            if bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = pending_class = 0
            i += 1
            continue

        if c == "-" and i + 1 < target_pos and text[i + 1:i + 2].decode("latin-1") == ">":
            i += 2
            continue

        if c.isalpha() or c == "_":
            start = i
            i += 1
            while i < target_pos and (text[i:i + 1].decode("latin-1").isalnum() or text[i:i + 1].decode("latin-1") == "_"):
                i += 1
            word = text[start:i].decode("utf-8", errors="replace")
            if word == "def":
                pending_def = 1
                pending_class = 0
                at_class_body = 0
            elif word == "class":
                pending_class = 1
                pending_def = 0
                at_class_body = 0
            else:
                expect_docstring = 0
            continue

        i += 1

    return _py_pack_state(in_string, in_comment, triple_string, string_delim,
                          in_fstring, escape_next, in_fexpr, fexpr_depth,
                          is_docstring, expect_docstring, at_class_body)
```


**Implementation:** inside `python_editor/custompythonlexer.py`, replace only `_py_compute_state`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 1.1.2 Existing method/function `_py_style_chunk`

Only the opening quote character can terminate this triple-quoted string. The run scanner also stops only at that delimiter or a backslash; otherwise an opposite quote can both corrupt the resume state and prevent the scanner from advancing.


**Old version — original lines 303–841:**


```python
def _py_style_chunk(text, start, end, prev_state, keywords, builtins, magic_methods):
    """Pure-Python twin of lexer_fast.style_chunk. Returns (final_state, [(len, style), ...])."""
    length = len(text)
    end = min(end, length)
    start = max(0, start)

    (in_string, in_comment, triple_string, string_delim,
     in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring,
     expect_docstring, at_class_body) = _py_unpack_state(prev_state)

    S_DEFAULT, S_KEYWORD, S_TYPES, S_STRING, S_KEYARGS, S_BRACKETS = 0, 1, 2, 3, 4, 5
    S_COMMENTS, S_CONSTANTS, S_FUNCTIONS, S_CLASSES, S_FUNCTION_DEF = 6, 7, 8, 9, 10
    S_DECORATOR, S_OPERATORS, S_MAGIC, S_NUMBERS, S_SELF, S_BUILTINS = 11, 12, 13, 14, 15, 16
    S_PARAMS, S_CLASSREF, S_IFIELD, S_IMETHOD, S_SFIELD, S_SMETHOD = 17, 18, 19, 20, 21, 22
    S_FCALL, S_LOCAL, S_COMMA, S_MODULE, S_DOCSTRING = 23, 24, 25, 26, 27

    results = []
    i = start

    after_def = after_class = after_dot = after_at = 0
    after_from = after_import = in_from_import = 0
    in_def_params = param_depth = at_type_pos = after_arrow = 0
    bracket_depth = pending_def = pending_class = 0
    at_arg_pos = False

    string_style = S_DOCSTRING if (in_string and is_docstring) else S_STRING

    while i < end:
        c = text[i:i + 1].decode("latin-1")

        # ---- comment ----
        if in_comment:
            token_start = i
            while i < end and text[i:i + 1].decode("latin-1") not in "\n\r":
                i += 1
            if i > token_start:
                results.append((i - token_start, S_COMMENTS))
            if i < end:
                in_comment = 0
                if text[i:i + 1].decode("latin-1") == "\r" and i + 1 < end and text[i + 1:i + 2].decode("latin-1") == "\n":
                    results.append((2, S_DEFAULT)); i += 2
                else:
                    results.append((1, S_DEFAULT)); i += 1
            continue

        # ---- f-string expression ----
        if in_fexpr:
            if c == "}":
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                    results.append((1, string_style))
                else:
                    results.append((1, S_BRACKETS))
                i += 1
                continue
            if c == "{":
                fexpr_depth += 1
                results.append((1, S_BRACKETS))
                i += 1
                continue
            if c in "frb" and i + 1 < end and text[i + 1:i + 2].decode("latin-1") in "\"'":
                token_start = i
                # CHUNK-SAFETY: only consume 4 bytes when all 4 are inside
                # THIS chunk (not `length` = the full document).
                if i + 3 < end and text[i + 2:i + 3].decode("latin-1") == text[i + 1:i + 2].decode("latin-1") and text[i + 3:i + 4].decode("latin-1") == text[i + 1:i + 2].decode("latin-1"):
                    results.append((4, S_STRING)); i += 4
                else:
                    results.append((2, S_STRING)); i += 2
                continue
            if c in "\"'":
                token_start = i
                i += 1
                while i < end:
                    if text[i:i + 1].decode("latin-1") == "\\":
                        # CHUNK-SAFETY: a backslash as the LAST chunk byte
                        # must not skip past `end` (would over-style by 1).
                        if i + 1 < end:
                            i += 2
                        else:
                            i += 1
                        continue
                    if text[i:i + 1].decode("latin-1") == c:
                        i += 1
                        break
                    if text[i:i + 1].decode("latin-1") in "\n\r":
                        break
                    i += 1
                results.append((i - token_start, S_STRING))
                continue
            if c == "#":
                token_start = i
                while i < end and text[i:i + 1].decode("latin-1") not in "\n\r":
                    i += 1
                results.append((i - token_start, S_COMMENTS))
                continue
            if c.isalpha() or c == "_":
                token_start = i
                while i < end and (
                    text[i:i + 1].decode("latin-1").isalnum()
                    or text[i:i + 1].decode("latin-1") in (".", "_")
                ):
                    i += 1
                token = text[token_start:i].decode("utf-8", errors="replace")
                followed_by_paren = i < end and text[i:i + 1].decode("latin-1") == "("
                if token in ("True", "False", "None"):
                    results.append((i - token_start, S_CONSTANTS))
                elif token in ("self", "cls"):
                    results.append((i - token_start, S_SELF))
                elif token in keywords:
                    results.append((i - token_start, S_KEYWORD))
                elif token in builtins:
                    results.append((i - token_start, S_BUILTINS))
                elif followed_by_paren:
                    results.append((i - token_start, S_FCALL))
                elif token[:1].isupper():
                    results.append((i - token_start, S_CLASSREF))
                else:
                    results.append((i - token_start, S_LOCAL))
                continue
            if c.isdigit():
                token_start = i
                while i < end and (
                    text[i:i + 1].decode("latin-1").isalnum()
                    or text[i:i + 1].decode("latin-1") in (".", "_")
                ):
                    i += 1

                results.append((i - token_start, S_NUMBERS))
                continue
            if c in "+-*/%=<>!&|^~":
                token_start = i
                i += 1
                if i < end and text[i:i + 1].decode("latin-1") in "+-*/%=<>!&|^~":
                    i += 1
                results.append((i - token_start, S_OPERATORS))
                continue
            if c in "(){}[]":
                results.append((1, S_BRACKETS))
                i += 1
                continue
            if c in " \t":
                token_start = i
                while i < end and text[i:i + 1].decode("latin-1") in " \t":
                    i += 1
                results.append((i - token_start, S_DEFAULT))
                continue
            if c in "\n\r":
                results.append((1, S_DEFAULT))
                i += 1
                continue
            results.append((1, S_DEFAULT))
            i += 1
            continue

        # ---- string ----
        if in_string:
            token_start = i
            if escape_next:
                i += 1
                escape_next = 0
                results.append((i - token_start, string_style))
                continue
            if c == "\\":
                i += 1
                escape_next = 1
                results.append((1, string_style))
                continue
            if triple_string:
                if c in "\"'":
                    # CHUNK-SAFETY: the closing '"""' may straddle the chunk
                    # end. Only consume 3 quote bytes when ALL of them are
                    # inside THIS chunk (i + 2 < end, NOT < length). Styling
                    # more bytes than the chunk contains corrupts
                    # Scintilla's style buffer and crashes the editor.
                    if i + 2 < end and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                        results.append((3, string_style))
                        i += 3
                        in_string = triple_string = string_delim = 0
                        in_fstring = is_docstring = 0
                        string_style = S_STRING
                        continue
                    results.append((1, string_style))
                    i += 1
                    continue
                if in_fstring and c == "{":
                    # CHUNK-SAFETY: '{{' needs both braces inside the chunk.
                    if i + 1 < end and text[i + 1:i + 2].decode("latin-1") == "{":
                        if i > token_start:
                            results.append((i - token_start, string_style))
                        results.append((2, string_style))
                        i += 2
                        continue
                    if i > token_start:
                        results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    in_fexpr = 1
                    fexpr_depth = 1
                    continue
                token_start = i
                while i < end:
                    c2 = text[i:i + 1].decode("latin-1")
                    if c2 in "\"'\\":
                        break
                    if in_fstring and c2 == "{":
                        break
                    i += 1
                if i > token_start:
                    results.append((i - token_start, string_style))
                continue

            # single-line string
            token_start = i
            while i < end:
                c2 = text[i:i + 1].decode("latin-1")
                if c2 == string_delim:
                    results.append((i - token_start + 1, string_style))
                    i += 1
                    in_string = string_delim = in_fstring = is_docstring = 0
                    string_style = S_STRING
                    break
                if c2 == "\\":
                    results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    escape_next = 1
                    break
                if in_fstring and c2 == "{":
                    # CHUNK-SAFETY: '{{' needs both braces inside the chunk.
                    if i + 1 < end and text[i + 1:i + 2].decode("latin-1") == "{":
                        if i > token_start:
                            results.append((i - token_start, string_style))
                        results.append((2, string_style))
                        i += 2
                        token_start = i
                        continue
                    if i > token_start:
                        results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    in_fexpr = 1
                    fexpr_depth = 1
                    break
                if c2 in "\n\r":
                    results.append((i - token_start, string_style))
                    in_string = string_delim = in_fstring = is_docstring = 0
                    string_style = S_STRING
                    break
                i += 1
            else:
                results.append((i - token_start, string_style))
            continue

        # ---- not in string or comment ----
        if c in " \t":
            token_start = i
            while i < end and text[i:i + 1].decode("latin-1") in " \t":
                i += 1
            results.append((i - token_start, S_DEFAULT))
            continue

        if c in "\n\r":
            if c == "\r" and i + 1 < end and text[i + 1:i + 2] == b"\n":
                results.append((2, S_DEFAULT)); i += 2
            else:
                results.append((1, S_DEFAULT)); i += 1
            if bracket_depth == 0:
                after_def = after_class = after_at = after_dot = 0
                after_from = after_import = in_from_import = 0
                at_arg_pos = False
                at_type_pos = after_arrow = 0
            continue

        if c in "frb" and i + 1 < end and text[i + 1:i + 2].decode("latin-1") in "\"'":
            # decode to a 1-char string — bytes indexing would give an int
            # here and break every comparison below.
            next_c = text[i + 1:i + 2].decode("latin-1")
            token_start = i
            # CHUNK-SAFETY: prefixed triple strings need all 4 bytes
            # inside THIS chunk, not just inside the document.
            if i + 3 < end and text[i + 2:i + 3].decode("latin-1") == next_c and text[i + 3:i + 4].decode("latin-1") == next_c:
                if expect_docstring:
                    string_style = S_DOCSTRING
                    is_docstring = 1
                else:
                    string_style = S_STRING
                results.append((4, string_style))
                i += 4
                in_string = triple_string = 1
                string_delim = next_c
                in_fstring = 1 if c == "f" else 0
            else:
                results.append((2, S_STRING))
                i += 2
                in_string = 1
                triple_string = 0
                string_delim = next_c
                in_fstring = 1 if c == "f" else 0
            expect_docstring = 0
            continue

        if c in "\"'":
            # CHUNK-SAFETY: the opening '"""' may straddle the chunk end.
            # Only consume 3 quote bytes when ALL of them are inside THIS
            # chunk; otherwise fall through to single-line-string handling
            # (the next chunk's state scan sees the full triple and styles
            # the remaining quotes correctly).
            if i + 2 < end and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                if expect_docstring:
                    string_style = S_DOCSTRING
                    is_docstring = 1
                else:
                    string_style = S_STRING
                results.append((3, string_style))
                i += 3
                in_string = triple_string = 1
                string_delim = c
                in_fstring = 0
            else:
                results.append((1, S_STRING))
                i += 1
                in_string = 1
                triple_string = 0
                string_delim = c
                in_fstring = 0
            expect_docstring = 0
            continue

        if c == "#":
            in_comment = 1
            token_start = i
            i += 1
            while i < end and text[i:i + 1].decode("latin-1") not in "\n\r":
                i += 1
            results.append((i - token_start, S_COMMENTS))
            continue

        if c == "@":
            results.append((1, S_DECORATOR))
            i += 1
            after_at = 1
            expect_docstring = 0
            at_arg_pos = False
            continue

        if c.isdigit():
            token_start = i
            while i < end and (text[i:i + 1].decode("latin-1").isalnum() or text[i:i + 1].decode("latin-1") == "."):
                i += 1
            results.append((i - token_start, S_NUMBERS))
            expect_docstring = 0
            at_arg_pos = False
            continue

        if c == ".":
            results.append((1, S_DEFAULT))
            i += 1
            if not (after_from or after_import):
                after_dot = 1
            at_arg_pos = False
            continue

        if c in "(){}[]":
            results.append((1, S_BRACKETS))
            if c in "([{":
                bracket_depth += 1
                if c == "(" and after_def:
                    in_def_params = 1
                    param_depth = 1
                    after_def = 0
                    at_type_pos = 0
                elif in_def_params:
                    param_depth += 1
                at_arg_pos = True
            else:
                if bracket_depth > 0:
                    bracket_depth -= 1
                if in_def_params:
                    param_depth -= 1
                    if param_depth <= 0:
                        in_def_params = 0
                        param_depth = 0
                        at_type_pos = 0
                at_arg_pos = False
            i += 1
            after_dot = 0
            continue

        if c in "+-*/%=<>!&|^~":
            token_start = i
            i += 1
            if i < end and text[i:i + 1].decode("latin-1") in "+-*/%=<>!&|^~":
                i += 1
            results.append((i - token_start, S_OPERATORS))
            expect_docstring = 0
            if text[token_start:token_start + 1].decode("latin-1") == "-" and token_start + 1 < end and text[token_start + 1:token_start + 2].decode("latin-1") == ">":
                if pending_def and bracket_depth == 0:
                    after_arrow = 1
            at_arg_pos = False
            continue

        if c == ",":
            results.append((1, S_COMMA))
            i += 1
            if in_def_params:
                at_type_pos = 0
            if not (after_import or in_from_import or after_from):
                pass
            at_arg_pos = True
            continue

        if c == ":":
            results.append((1, S_DEFAULT))
            if in_def_params and param_depth == 1:
                at_type_pos = 1
            elif bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = pending_class = 0
                after_arrow = 0
            i += 1
            at_arg_pos = False
            continue

        if c == ";":
            results.append((1, S_DEFAULT))
            i += 1
            expect_docstring = after_from = after_import = in_from_import = 0
            at_arg_pos = False
            continue

        # ---- identifier ----
        if c.isalpha() or c == "_":
            token_start = i
            while i < end and (text[i:i + 1].decode("latin-1").isalnum() or text[i:i + 1].decode("latin-1") == "_"):
                i += 1
            token = text[token_start:i].decode("utf-8", errors="replace")

            followed_by_paren = i < end and text[i:i + 1].decode("latin-1") == "("
            followed_by_eq = (i < end and text[i:i + 1].decode("latin-1") == "=" and
                              (i + 1 >= end or text[i + 1:i + 2].decode("latin-1") != "="))
            _j = i
            while _j < end and text[_j:_j + 1].decode("latin-1") in " \t":
                _j += 1
            followed_by_assign = (_j < end and text[_j:_j + 1].decode("latin-1") == "=" and
                                  (_j + 1 >= end or text[_j + 1:_j + 2].decode("latin-1") != "="))

            if token not in ("def", "class"):
                expect_docstring = 0

            # --- decision tree (mirrors lexer_fast.pyx / PyCharm) ---
            if after_at:
                results.append((i - token_start, S_DECORATOR))
                after_at = 0
            elif token in ("self", "cls"):
                results.append((i - token_start, S_SELF))
            elif token in ("True", "False", "None"):
                results.append((i - token_start, S_CONSTANTS))
            elif token == "def":
                results.append((i - token_start, S_KEYWORD))
                after_def = pending_def = 1
                pending_class = at_class_body = 0
            elif token == "class":
                results.append((i - token_start, S_KEYWORD))
                after_class = pending_class = 1
                pending_def = 0
            elif token == "import":
                results.append((i - token_start, S_KEYWORD))
                if after_from:
                    after_from = 0
                    in_from_import = 1
                else:
                    after_import = 1
            elif token == "from":
                results.append((i - token_start, S_KEYWORD))
                after_from = 1
            elif token == "as":
                results.append((i - token_start, S_KEYWORD))
                after_import = in_from_import = 0
            elif token in keywords:
                results.append((i - token_start, S_KEYWORD))
            elif after_def:
                if token in magic_methods:
                    results.append((i - token_start, S_MAGIC))
                else:
                    results.append((i - token_start, S_FUNCTION_DEF))
            elif after_class:
                results.append((i - token_start, S_CLASSES))
                after_class = 0
            elif after_dot:
                if followed_by_paren:
                    results.append((i - token_start, S_IMETHOD))
                else:
                    results.append((i - token_start, S_IFIELD))
                after_dot = 0
            elif in_def_params and param_depth == 1:
                if at_type_pos:
                    results.append((i - token_start, S_TYPES))
                else:
                    results.append((i - token_start, S_PARAMS))
            elif after_arrow:
                results.append((i - token_start, S_TYPES))
            elif after_from or after_import:
                results.append((i - token_start, S_MODULE))
            elif in_from_import:
                if token[:1].isupper():
                    results.append((i - token_start, S_CLASSREF))
                else:
                    results.append((i - token_start, S_MODULE))
            elif at_arg_pos and followed_by_eq and not in_def_params:
                results.append((i - token_start, S_KEYARGS))
            elif at_class_body and followed_by_assign:
                results.append((i - token_start, S_IFIELD))
            elif token in builtins:
                results.append((i - token_start, S_BUILTINS))
            elif followed_by_paren:
                results.append((i - token_start, S_FCALL))
            elif token.startswith("__") and token.endswith("__") and len(token) > 4:
                results.append((i - token_start, S_BUILTINS))
            elif token[:1].isupper():
                results.append((i - token_start, S_CLASSREF))
            else:
                results.append((i - token_start, S_LOCAL))

            at_arg_pos = False
            continue

        results.append((1, S_DEFAULT))
        i += 1
        at_arg_pos = False

    final_state = _py_pack_state(in_string, in_comment, triple_string,
                                 string_delim, in_fstring, escape_next,
                                 in_fexpr, fexpr_depth, is_docstring,
                                 expect_docstring, at_class_body)
    return (final_state, results)
```


**New version:**


```python
def _py_style_chunk(text, start, end, prev_state, keywords, builtins, magic_methods):
    """Tokenize one byte interval using the state reconstructed at its start.

    Args:
        text: Complete UTF-8 source buffer.
        start: First byte to style.
        end: Exclusive final byte, clamped to the source length.
        prev_state: Packed state from the corresponding state scanner.
        keywords: Python keyword names used by the theme's keyword style.
        builtins: Builtin and module names receiving the builtin style.
        magic_methods: Special method names receiving their dedicated style.

    Returns:
        A pair containing the final packed state and ordered (byte count, style
        ID) runs. Counts are bytes, matching QScintilla's styling API. Triple
        string runs stop at their own delimiter or an escape, not the other
        quote character; that also guarantees progress across embedded quotes.
    """
    length = len(text)
    end = min(end, length)
    start = max(0, start)

    (in_string, in_comment, triple_string, string_delim,
     in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring,
     expect_docstring, at_class_body) = _py_unpack_state(prev_state)

    S_DEFAULT, S_KEYWORD, S_TYPES, S_STRING, S_KEYARGS, S_BRACKETS = 0, 1, 2, 3, 4, 5
    S_COMMENTS, S_CONSTANTS, S_FUNCTIONS, S_CLASSES, S_FUNCTION_DEF = 6, 7, 8, 9, 10
    S_DECORATOR, S_OPERATORS, S_MAGIC, S_NUMBERS, S_SELF, S_BUILTINS = 11, 12, 13, 14, 15, 16
    S_PARAMS, S_CLASSREF, S_IFIELD, S_IMETHOD, S_SFIELD, S_SMETHOD = 17, 18, 19, 20, 21, 22
    S_FCALL, S_LOCAL, S_COMMA, S_MODULE, S_DOCSTRING = 23, 24, 25, 26, 27

    results = []
    i = start

    after_def = after_class = after_dot = after_at = 0
    after_from = after_import = in_from_import = 0
    in_def_params = param_depth = at_type_pos = after_arrow = 0
    bracket_depth = pending_def = pending_class = 0
    at_arg_pos = False

    string_style = S_DOCSTRING if (in_string and is_docstring) else S_STRING

    while i < end:
        c = text[i:i + 1].decode("latin-1")

        # ---- comment ----
        if in_comment:
            token_start = i
            while i < end and text[i:i + 1].decode("latin-1") not in "\n\r":
                i += 1
            if i > token_start:
                results.append((i - token_start, S_COMMENTS))
            if i < end:
                in_comment = 0
                if text[i:i + 1].decode("latin-1") == "\r" and i + 1 < end and text[i + 1:i + 2].decode("latin-1") == "\n":
                    results.append((2, S_DEFAULT)); i += 2
                else:
                    results.append((1, S_DEFAULT)); i += 1
            continue

        # ---- f-string expression ----
        if in_fexpr:
            if c == "}":
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                    results.append((1, string_style))
                else:
                    results.append((1, S_BRACKETS))
                i += 1
                continue
            if c == "{":
                fexpr_depth += 1
                results.append((1, S_BRACKETS))
                i += 1
                continue
            if c in "frb" and i + 1 < end and text[i + 1:i + 2].decode("latin-1") in "\"'":
                token_start = i
                # CHUNK-SAFETY: only consume 4 bytes when all 4 are inside
                # THIS chunk (not `length` = the full document).
                if i + 3 < end and text[i + 2:i + 3].decode("latin-1") == text[i + 1:i + 2].decode("latin-1") and text[i + 3:i + 4].decode("latin-1") == text[i + 1:i + 2].decode("latin-1"):
                    results.append((4, S_STRING)); i += 4
                else:
                    results.append((2, S_STRING)); i += 2
                continue
            if c in "\"'":
                token_start = i
                i += 1
                while i < end:
                    if text[i:i + 1].decode("latin-1") == "\\":
                        # CHUNK-SAFETY: a backslash as the LAST chunk byte
                        # must not skip past `end` (would over-style by 1).
                        if i + 1 < end:
                            i += 2
                        else:
                            i += 1
                        continue
                    if text[i:i + 1].decode("latin-1") == c:
                        i += 1
                        break
                    if text[i:i + 1].decode("latin-1") in "\n\r":
                        break
                    i += 1
                results.append((i - token_start, S_STRING))
                continue
            if c == "#":
                token_start = i
                while i < end and text[i:i + 1].decode("latin-1") not in "\n\r":
                    i += 1
                results.append((i - token_start, S_COMMENTS))
                continue
            if c.isalpha() or c == "_":
                token_start = i
                while i < end and (
                    text[i:i + 1].decode("latin-1").isalnum()
                    or text[i:i + 1].decode("latin-1") in (".", "_")
                ):
                    i += 1
                token = text[token_start:i].decode("utf-8", errors="replace")
                followed_by_paren = i < end and text[i:i + 1].decode("latin-1") == "("
                if token in ("True", "False", "None"):
                    results.append((i - token_start, S_CONSTANTS))
                elif token in ("self", "cls"):
                    results.append((i - token_start, S_SELF))
                elif token in keywords:
                    results.append((i - token_start, S_KEYWORD))
                elif token in builtins:
                    results.append((i - token_start, S_BUILTINS))
                elif followed_by_paren:
                    results.append((i - token_start, S_FCALL))
                elif token[:1].isupper():
                    results.append((i - token_start, S_CLASSREF))
                else:
                    results.append((i - token_start, S_LOCAL))
                continue
            if c.isdigit():
                token_start = i
                while i < end and (
                    text[i:i + 1].decode("latin-1").isalnum()
                    or text[i:i + 1].decode("latin-1") in (".", "_")
                ):
                    i += 1

                results.append((i - token_start, S_NUMBERS))
                continue
            if c in "+-*/%=<>!&|^~":
                token_start = i
                i += 1
                if i < end and text[i:i + 1].decode("latin-1") in "+-*/%=<>!&|^~":
                    i += 1
                results.append((i - token_start, S_OPERATORS))
                continue
            if c in "(){}[]":
                results.append((1, S_BRACKETS))
                i += 1
                continue
            if c in " \t":
                token_start = i
                while i < end and text[i:i + 1].decode("latin-1") in " \t":
                    i += 1
                results.append((i - token_start, S_DEFAULT))
                continue
            if c in "\n\r":
                results.append((1, S_DEFAULT))
                i += 1
                continue
            results.append((1, S_DEFAULT))
            i += 1
            continue

        # ---- string ----
        if in_string:
            token_start = i
            if escape_next:
                i += 1
                escape_next = 0
                results.append((i - token_start, string_style))
                continue
            if c == "\\":
                i += 1
                escape_next = 1
                results.append((1, string_style))
                continue
            if triple_string:
                # Only the opening quote kind can close this triple string.
                if c == string_delim:
                    # CHUNK-SAFETY: the closing '"""' may straddle the chunk
                    # end. Only consume 3 quote bytes when ALL of them are
                    # inside THIS chunk (i + 2 < end, NOT < length). Styling
                    # more bytes than the chunk contains corrupts
                    # Scintilla's style buffer and crashes the editor.
                    if i + 2 < end and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                        results.append((3, string_style))
                        i += 3
                        in_string = triple_string = string_delim = 0
                        in_fstring = is_docstring = 0
                        string_style = S_STRING
                        continue
                    results.append((1, string_style))
                    i += 1
                    continue
                if in_fstring and c == "{":
                    # CHUNK-SAFETY: '{{' needs both braces inside the chunk.
                    if i + 1 < end and text[i + 1:i + 2].decode("latin-1") == "{":
                        if i > token_start:
                            results.append((i - token_start, string_style))
                        results.append((2, string_style))
                        i += 2
                        continue
                    if i > token_start:
                        results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    in_fexpr = 1
                    fexpr_depth = 1
                    continue
                token_start = i
                while i < end:
                    c2 = text[i:i + 1].decode("latin-1")
                    if c2 == string_delim or c2 == "\\":
                        break
                    if in_fstring and c2 == "{":
                        break
                    i += 1
                if i > token_start:
                    results.append((i - token_start, string_style))
                continue

            # single-line string
            token_start = i
            while i < end:
                c2 = text[i:i + 1].decode("latin-1")
                if c2 == string_delim:
                    results.append((i - token_start + 1, string_style))
                    i += 1
                    in_string = string_delim = in_fstring = is_docstring = 0
                    string_style = S_STRING
                    break
                if c2 == "\\":
                    results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    escape_next = 1
                    break
                if in_fstring and c2 == "{":
                    # CHUNK-SAFETY: '{{' needs both braces inside the chunk.
                    if i + 1 < end and text[i + 1:i + 2].decode("latin-1") == "{":
                        if i > token_start:
                            results.append((i - token_start, string_style))
                        results.append((2, string_style))
                        i += 2
                        token_start = i
                        continue
                    if i > token_start:
                        results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    in_fexpr = 1
                    fexpr_depth = 1
                    break
                if c2 in "\n\r":
                    results.append((i - token_start, string_style))
                    in_string = string_delim = in_fstring = is_docstring = 0
                    string_style = S_STRING
                    break
                i += 1
            else:
                results.append((i - token_start, string_style))
            continue

        # ---- not in string or comment ----
        if c in " \t":
            token_start = i
            while i < end and text[i:i + 1].decode("latin-1") in " \t":
                i += 1
            results.append((i - token_start, S_DEFAULT))
            continue

        if c in "\n\r":
            if c == "\r" and i + 1 < end and text[i + 1:i + 2] == b"\n":
                results.append((2, S_DEFAULT)); i += 2
            else:
                results.append((1, S_DEFAULT)); i += 1
            if bracket_depth == 0:
                after_def = after_class = after_at = after_dot = 0
                after_from = after_import = in_from_import = 0
                at_arg_pos = False
                at_type_pos = after_arrow = 0
            continue

        if c in "frb" and i + 1 < end and text[i + 1:i + 2].decode("latin-1") in "\"'":
            # decode to a 1-char string — bytes indexing would give an int
            # here and break every comparison below.
            next_c = text[i + 1:i + 2].decode("latin-1")
            token_start = i
            # CHUNK-SAFETY: prefixed triple strings need all 4 bytes
            # inside THIS chunk, not just inside the document.
            if i + 3 < end and text[i + 2:i + 3].decode("latin-1") == next_c and text[i + 3:i + 4].decode("latin-1") == next_c:
                if expect_docstring:
                    string_style = S_DOCSTRING
                    is_docstring = 1
                else:
                    string_style = S_STRING
                results.append((4, string_style))
                i += 4
                in_string = triple_string = 1
                string_delim = next_c
                in_fstring = 1 if c == "f" else 0
            else:
                results.append((2, S_STRING))
                i += 2
                in_string = 1
                triple_string = 0
                string_delim = next_c
                in_fstring = 1 if c == "f" else 0
            expect_docstring = 0
            continue

        if c in "\"'":
            # CHUNK-SAFETY: the opening '"""' may straddle the chunk end.
            # Only consume 3 quote bytes when ALL of them are inside THIS
            # chunk; otherwise fall through to single-line-string handling
            # (the next chunk's state scan sees the full triple and styles
            # the remaining quotes correctly).
            if i + 2 < end and text[i + 1:i + 2].decode("latin-1") == c and text[i + 2:i + 3].decode("latin-1") == c:
                if expect_docstring:
                    string_style = S_DOCSTRING
                    is_docstring = 1
                else:
                    string_style = S_STRING
                results.append((3, string_style))
                i += 3
                in_string = triple_string = 1
                string_delim = c
                in_fstring = 0
            else:
                results.append((1, S_STRING))
                i += 1
                in_string = 1
                triple_string = 0
                string_delim = c
                in_fstring = 0
            expect_docstring = 0
            continue

        if c == "#":
            in_comment = 1
            token_start = i
            i += 1
            while i < end and text[i:i + 1].decode("latin-1") not in "\n\r":
                i += 1
            results.append((i - token_start, S_COMMENTS))
            continue

        if c == "@":
            results.append((1, S_DECORATOR))
            i += 1
            after_at = 1
            expect_docstring = 0
            at_arg_pos = False
            continue

        if c.isdigit():
            token_start = i
            while i < end and (text[i:i + 1].decode("latin-1").isalnum() or text[i:i + 1].decode("latin-1") == "."):
                i += 1
            results.append((i - token_start, S_NUMBERS))
            expect_docstring = 0
            at_arg_pos = False
            continue

        if c == ".":
            results.append((1, S_DEFAULT))
            i += 1
            if not (after_from or after_import):
                after_dot = 1
            at_arg_pos = False
            continue

        if c in "(){}[]":
            results.append((1, S_BRACKETS))
            if c in "([{":
                bracket_depth += 1
                if c == "(" and after_def:
                    in_def_params = 1
                    param_depth = 1
                    after_def = 0
                    at_type_pos = 0
                elif in_def_params:
                    param_depth += 1
                at_arg_pos = True
            else:
                if bracket_depth > 0:
                    bracket_depth -= 1
                if in_def_params:
                    param_depth -= 1
                    if param_depth <= 0:
                        in_def_params = 0
                        param_depth = 0
                        at_type_pos = 0
                at_arg_pos = False
            i += 1
            after_dot = 0
            continue

        if c in "+-*/%=<>!&|^~":
            token_start = i
            i += 1
            if i < end and text[i:i + 1].decode("latin-1") in "+-*/%=<>!&|^~":
                i += 1
            results.append((i - token_start, S_OPERATORS))
            expect_docstring = 0
            if text[token_start:token_start + 1].decode("latin-1") == "-" and token_start + 1 < end and text[token_start + 1:token_start + 2].decode("latin-1") == ">":
                if pending_def and bracket_depth == 0:
                    after_arrow = 1
            at_arg_pos = False
            continue

        if c == ",":
            results.append((1, S_COMMA))
            i += 1
            if in_def_params:
                at_type_pos = 0
            if not (after_import or in_from_import or after_from):
                pass
            at_arg_pos = True
            continue

        if c == ":":
            results.append((1, S_DEFAULT))
            if in_def_params and param_depth == 1:
                at_type_pos = 1
            elif bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = pending_class = 0
                after_arrow = 0
            i += 1
            at_arg_pos = False
            continue

        if c == ";":
            results.append((1, S_DEFAULT))
            i += 1
            expect_docstring = after_from = after_import = in_from_import = 0
            at_arg_pos = False
            continue

        # ---- identifier ----
        if c.isalpha() or c == "_":
            token_start = i
            while i < end and (text[i:i + 1].decode("latin-1").isalnum() or text[i:i + 1].decode("latin-1") == "_"):
                i += 1
            token = text[token_start:i].decode("utf-8", errors="replace")

            followed_by_paren = i < end and text[i:i + 1].decode("latin-1") == "("
            followed_by_eq = (i < end and text[i:i + 1].decode("latin-1") == "=" and
                              (i + 1 >= end or text[i + 1:i + 2].decode("latin-1") != "="))
            _j = i
            while _j < end and text[_j:_j + 1].decode("latin-1") in " \t":
                _j += 1
            followed_by_assign = (_j < end and text[_j:_j + 1].decode("latin-1") == "=" and
                                  (_j + 1 >= end or text[_j + 1:_j + 2].decode("latin-1") != "="))

            if token not in ("def", "class"):
                expect_docstring = 0

            # --- decision tree (mirrors lexer_fast.pyx / PyCharm) ---
            if after_at:
                results.append((i - token_start, S_DECORATOR))
                after_at = 0
            elif token in ("self", "cls"):
                results.append((i - token_start, S_SELF))
            elif token in ("True", "False", "None"):
                results.append((i - token_start, S_CONSTANTS))
            elif token == "def":
                results.append((i - token_start, S_KEYWORD))
                after_def = pending_def = 1
                pending_class = at_class_body = 0
            elif token == "class":
                results.append((i - token_start, S_KEYWORD))
                after_class = pending_class = 1
                pending_def = 0
            elif token == "import":
                results.append((i - token_start, S_KEYWORD))
                if after_from:
                    after_from = 0
                    in_from_import = 1
                else:
                    after_import = 1
            elif token == "from":
                results.append((i - token_start, S_KEYWORD))
                after_from = 1
            elif token == "as":
                results.append((i - token_start, S_KEYWORD))
                after_import = in_from_import = 0
            elif token in keywords:
                results.append((i - token_start, S_KEYWORD))
            elif after_def:
                if token in magic_methods:
                    results.append((i - token_start, S_MAGIC))
                else:
                    results.append((i - token_start, S_FUNCTION_DEF))
            elif after_class:
                results.append((i - token_start, S_CLASSES))
                after_class = 0
            elif after_dot:
                if followed_by_paren:
                    results.append((i - token_start, S_IMETHOD))
                else:
                    results.append((i - token_start, S_IFIELD))
                after_dot = 0
            elif in_def_params and param_depth == 1:
                if at_type_pos:
                    results.append((i - token_start, S_TYPES))
                else:
                    results.append((i - token_start, S_PARAMS))
            elif after_arrow:
                results.append((i - token_start, S_TYPES))
            elif after_from or after_import:
                results.append((i - token_start, S_MODULE))
            elif in_from_import:
                if token[:1].isupper():
                    results.append((i - token_start, S_CLASSREF))
                else:
                    results.append((i - token_start, S_MODULE))
            elif at_arg_pos and followed_by_eq and not in_def_params:
                results.append((i - token_start, S_KEYARGS))
            elif at_class_body and followed_by_assign:
                results.append((i - token_start, S_IFIELD))
            elif token in builtins:
                results.append((i - token_start, S_BUILTINS))
            elif followed_by_paren:
                results.append((i - token_start, S_FCALL))
            elif token.startswith("__") and token.endswith("__") and len(token) > 4:
                results.append((i - token_start, S_BUILTINS))
            elif token[:1].isupper():
                results.append((i - token_start, S_CLASSREF))
            else:
                results.append((i - token_start, S_LOCAL))

            at_arg_pos = False
            continue

        results.append((1, S_DEFAULT))
        i += 1
        at_arg_pos = False

    final_state = _py_pack_state(in_string, in_comment, triple_string,
                                 string_delim, in_fstring, escape_next,
                                 in_fexpr, fexpr_depth, is_docstring,
                                 expect_docstring, at_class_body)
    return (final_state, results)
```


**Implementation:** inside `python_editor/custompythonlexer.py`, replace only `_py_style_chunk`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 1.1.3 Existing method/function `NeutronLexer.__init__`

The widget reference is stored in `_editor` so the inherited `QsciLexerCustom.editor()` method remains callable. The Python and Markdown lexers must use the same renamed reference.


**Old version — original lines 845–873:**


```python
    def __init__(self, language_name, editor, theme=None, paper=None):
        """
        Base lexer for both custom lexers.

        Font/styling model (single source of truth: the THEME):
          - family + size come from the theme's GLOBAL editor.font block
            (one place — the Settings dialog edits exactly that block)
          - per-style font blocks contribute ONLY font-weight and italic
          - per-style paper-color is optional; styles without one inherit
            the editor paper (which is also what the Settings color picker
            overrides at runtime)

        :param theme: absolute path to a theme .json; None -> themes/theme.json
        :param paper: QColor paper override from the Settings dialog
                     (None = use the theme's editor.paper-color)
        """
        super(NeutronLexer, self).__init__(editor)
        self.editor = editor
        self.language_name = language_name
        self.theme_json = None
        self.theme = theme or _resource_path(os.path.join("themes", "theme.json"))
        self.paper_override = paper          # QColor or None

        self.token_list = []
        self.keyword_list = []
        self.builtin_names = []

        self._init_theme_vars()
        self._init_theme()
```


**New version:**


```python
    def __init__(self, language_name, editor, theme=None, paper=None):
        """
        Base lexer for both custom lexers.

        Font/styling model (single source of truth: the THEME):
          - family + size come from the theme's GLOBAL editor.font block
            (one place — the Settings dialog edits exactly that block)
          - per-style font blocks contribute ONLY font-weight and italic
          - per-style paper-color is optional; styles without one inherit
            the editor paper (which is also what the Settings color picker
            overrides at runtime)

        :param theme: absolute path to a theme .json; None -> themes/theme.json
        :param paper: QColor paper override from the Settings dialog
                     (None = use the theme's editor.paper-color)
        """
        super(NeutronLexer, self).__init__(editor)
        # Preserve QsciLexerCustom.editor(), which is an inherited method.
        self._editor = editor
        self.language_name = language_name
        self.theme_json = {}
        self.theme = theme or _resource_path(os.path.join("themes", "theme.json"))
        self.paper_override = paper          # QColor or None

        self.token_list = []
        self.keyword_list = []
        self.builtin_names = []

        self._init_theme_vars()
        self._init_theme()
```


**Implementation:** inside `python_editor/custompythonlexer.py`, replace only `NeutronLexer.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 1.1.4 Existing method/function `NeutronLexer._init_theme_vars`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 881–934:**


```python
    def _init_theme_vars(self):
        self.DEFAULT = 0
        self.KEYWORD = 1
        self.TYPES = 2
        self.STRING = 3
        self.KEYARGS = 4
        self.BRACKETS = 5
        self.COMMENTS = 6
        self.CONSTANTS = 7
        self.FUNCTIONS = 8
        self.CLASSES = 9
        self.FUNCTION_DEF = 10
        self.DECORATOR = 11
        # --- Semantic styles (mirror PyCharm's Python color scheme) ---
        self.OPERATORS = 12
        self.MAGIC_METHODS = 13
        self.NUMBERS = 14
        self.SELF_CLS = 15
        self.BUILTINS = 16
        self.PARAMETERS = 17
        self.CLASS_REFERENCE = 18
        self.INSTANCE_FIELD = 19
        self.INSTANCE_METHOD = 20
        self.STATIC_FIELD = 21
        self.STATIC_METHOD = 22
        self.FUNCTION_CALL = 23
        self.LOCAL_VARIABLE = 24
        self.COMMA = 25
        self.MODULE_NAME = 26
        self.DOCSTRING = 27

        self.default_names = [
            "default", "keyword", "types", "string", "keyargs",
            "brackets", "comments", "constants", "functions",
            "classes", "function_def", "decorator",
            "operators", "magic_methods", "numbers",
            "self_cls", "builtins", "parameters",
            "class_reference", "instance_field", "instance_method",
            "static_field", "static_method", "function_call",
            "local_variable", "comma", "module_name", "docstring",
        ]

        self.font_weights = {
            "thin": QFont.Thin,
            "extralight": getattr(QFont, 'ExtraLight', QFont.Light),
            "light": QFont.Light,
            "normal": QFont.Normal,
            "medium": QFont.Medium,
            "demibold": QFont.DemiBold,
            "bold": QFont.Bold,
            "extrabold": getattr(QFont, 'ExtraBold', QFont.Bold),
            "black": QFont.Black,
        }
        self._prev_state = 0
```


**New version:**


```python
    def _init_theme_vars(self):
        """Initialize style identifiers, theme colors and per-style font settings.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self.DEFAULT = 0
        self.KEYWORD = 1
        self.TYPES = 2
        self.STRING = 3
        self.KEYARGS = 4
        self.BRACKETS = 5
        self.COMMENTS = 6
        self.CONSTANTS = 7
        self.FUNCTIONS = 8
        self.CLASSES = 9
        self.FUNCTION_DEF = 10
        self.DECORATOR = 11
        # --- Semantic styles (mirror PyCharm's Python color scheme) ---
        self.OPERATORS = 12
        self.MAGIC_METHODS = 13
        self.NUMBERS = 14
        self.SELF_CLS = 15
        self.BUILTINS = 16
        self.PARAMETERS = 17
        self.CLASS_REFERENCE = 18
        self.INSTANCE_FIELD = 19
        self.INSTANCE_METHOD = 20
        self.STATIC_FIELD = 21
        self.STATIC_METHOD = 22
        self.FUNCTION_CALL = 23
        self.LOCAL_VARIABLE = 24
        self.COMMA = 25
        self.MODULE_NAME = 26
        self.DOCSTRING = 27

        self.default_names = [
            "default", "keyword", "types", "string", "keyargs",
            "brackets", "comments", "constants", "functions",
            "classes", "function_def", "decorator",
            "operators", "magic_methods", "numbers",
            "self_cls", "builtins", "parameters",
            "class_reference", "instance_field", "instance_method",
            "static_field", "static_method", "function_call",
            "local_variable", "comma", "module_name", "docstring",
        ]

        self.font_weights = {
            "thin": QFont.Weight.Thin,
            "extralight": getattr(QFont, 'ExtraLight', QFont.Weight.Light),
            "light": QFont.Weight.Light,
            "normal": QFont.Weight.Normal,
            "medium": QFont.Weight.Medium,
            "demibold": QFont.Weight.DemiBold,
            "bold": QFont.Weight.Bold,
            "extrabold": getattr(QFont, 'ExtraBold', QFont.Weight.Bold),
            "black": QFont.Weight.Black,
        }
        self._prev_state = 0
```


**Implementation:** inside `python_editor/custompythonlexer.py`, replace only `NeutronLexer._init_theme_vars`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 1.1.5 Existing method/function `NeutronLexer._init_theme`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.

The widget reference is stored in `_editor` so the inherited `QsciLexerCustom.editor()` method remains callable. The Python and Markdown lexers must use the same renamed reference.


**Old version — original lines 936–995:**


```python
    def _init_theme(self):
        """
        Build the whole style table from the theme file.

        Lookup order per style:
          color        <- style block (required)
          paper-color  <- style block, else editor.paper-color,
                         else the `paper` override from Settings (wins over
                         everything when set)
          font         <- GLOBAL family+size (editor.font) combined with the
                         style's font-weight / italic only. Per-style family
                         and font-size are deliberately IGNORED so one font
                         choice in Settings really changes every style —
                         that inconsistency is exactly why PythonEditor
                         ignored the settings dialog before.
        """
        with open(self.theme, "r", encoding="utf-8") as f:
            self.theme_json = json.load(f)

        data = self.theme_json["theme"]

        # --- editor-wide defaults (the section the Settings dialog edits) -- #
        editor_section = data.get("editor", {})
        gfont = editor_section.get("font", {})
        self.editor_font_family = gfont.get("family", "JetBrains Mono")
        self.editor_font_size = int(gfont.get("font-size", 13))

        theme_paper = editor_section.get("paper-color", "#1e1f22")
        default_paper = (self.paper_override.name()
                         if self.paper_override else theme_paper)

        # The default style carries the editor-wide look; unstyled bytes
        # and the margins inherit from it.
        self.setDefaultColor(QColor(
            data["syntax"][0]["default"].get("color", "#bcbec4")
            if "default" in data["syntax"][0] else "#bcbec4"))
        self.setDefaultPaper(QColor(default_paper))

        colors = data["syntax"]
        for clr in colors:
            name = list(clr.keys())[0]
            if name not in self.default_names:
                # Styles of the OTHER language live in the same theme file
                # (one merged 62-style list) — skip silently, they are not
                # errors, just not ours.
                continue
            body = clr[name]

            if "color" in body:
                self.setColor(QColor(body["color"]), getattr(self, name.upper()))

            paper_hex = body.get("paper-color", default_paper)
            self.setPaper(QColor(paper_hex), getattr(self, name.upper()))

            f = body.get("font", {})
            weight = self.font_weights.get(f.get("font-weight", "normal"),
                                           QFont.Normal)
            fnt = QFont(self.editor_font_family, self.editor_font_size, weight)
            fnt.setItalic(bool(f.get("italic", False)))
            self.setFont(fnt, getattr(self, name.upper()))
```


**New version:**


```python
    def _init_theme(self):
        """
        Build the whole style table from the theme file.

        Lookup order per style:
          color        <- style block (required)
          paper-color  <- style block, else editor.paper-color,
                         else the `paper` override from Settings (wins over
                         everything when set)
          font         <- GLOBAL family+size (editor.font) combined with the
                         style's font-weight / italic only. Per-style family
                         and font-size are deliberately IGNORED so one font
                         choice in Settings really changes every style —
                         that inconsistency is exactly why PythonEditor
                         ignored the settings dialog before.
        """
        with open(self.theme, "r", encoding="utf-8") as f:
            self.theme_json = json.load(f)

        data = self.theme_json["theme"]

        # --- editor-wide defaults (the section the Settings dialog edits) -- #
        editor_section = data.get("editor", {})
        gfont = editor_section.get("font", {})
        self._editor_font_family = gfont.get("family", "JetBrains Mono")
        self._editor_font_size = int(gfont.get("font-size", 13))

        theme_paper = editor_section.get("paper-color", "#1e1f22")
        default_paper = (self.paper_override.name()
                         if self.paper_override else theme_paper)

        # The default style carries the editor-wide look; unstyled bytes
        # and the margins inherit from it.
        self.setDefaultColor(QColor(
            data["syntax"][0]["default"].get("color", "#bcbec4")
            if "default" in data["syntax"][0] else "#bcbec4"))
        self.setDefaultPaper(QColor(default_paper))

        colors = data["syntax"]
        for clr in colors:
            name = list(clr.keys())[0]
            if name not in self.default_names:
                # Styles of the OTHER language live in the same theme file
                # (one merged 62-style list) — skip silently, they are not
                # errors, just not ours.
                continue
            body = clr[name]

            if "color" in body:
                self.setColor(QColor(body["color"]), getattr(self, name.upper()))

            paper_hex = body.get("paper-color", default_paper)
            self.setPaper(QColor(paper_hex), getattr(self, name.upper()))

            f = body.get("font", {})
            weight = self.font_weights.get(f.get("font-weight", "normal"),
                                           QFont.Weight.Normal)
            fnt = QFont(self._editor_font_family, self._editor_font_size, weight)
            fnt.setItalic(bool(f.get("italic", False)))
            self.setFont(fnt, getattr(self, name.upper()))
```


**Implementation:** inside `python_editor/custompythonlexer.py`, replace only `NeutronLexer._init_theme`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 1.1.6 Existing method/function `NeutronLexer.editor_font`

The widget reference is stored in `_editor` so the inherited `QsciLexerCustom.editor()` method remains callable. The Python and Markdown lexers must use the same renamed reference.


**Old version — original lines 1000–1010:**


```python
    def editor_font(self) -> QFont:
        """
        The editor-wide font (family + size) from the theme's global
        editor.font block, with per-style weight/italic stripped — this is
        the font for margins, popups and anything editor-wide.

        Replaces the old editors' self.window_font. Falls back to
        JetBrains Mono 13 when the theme has no editor section.
        """
        f = QFont(self.editor_font_family, self.editor_font_size)
        return f
```


**New version:**


```python
    def editor_font(self) -> QFont:
        """
        The editor-wide font (family + size) from the theme's global
        editor.font block, with per-style weight/italic stripped — this is
        the font for margins, popups and anything editor-wide.

        Replaces the old editors' self.window_font. Falls back to
        JetBrains Mono 13 when the theme has no editor section.
        """
        f = QFont(self._editor_font_family, self._editor_font_size)
        return f
```


**Implementation:** inside `python_editor/custompythonlexer.py`, replace only `NeutronLexer.editor_font`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 1.1.7 Existing method/function `PyCustomLexer.styleText`

The widget reference is stored in `_editor` so the inherited `QsciLexerCustom.editor()` method remains callable. The Python and Markdown lexers must use the same renamed reference.


**Old version — original lines 1132–1173:**


```python
    def styleText(self, start: int, end: int) -> None:
        full_text = self.editor.text()
        text_bytes = full_text.encode('utf-8')

        start_char = self._byte_pos_to_char_index(full_text, start)
        end_char = self._byte_pos_to_char_index(full_text, end)

        start_byte = len(full_text[:start_char].encode('utf-8'))
        end_byte = len(full_text[:end_char].encode('utf-8'))

        # Compute the correct lexer state at start_byte by scanning from byte 0.
        # This is necessary because QScintilla may call styleText for
        # non-contiguous regions (e.g. when the user scrolls).
        if _HAS_CYTHON:
            prev_state = _cython_state(text_bytes, start_byte)
            final_state, styled_tokens = _cython_style(
                text_bytes,
                start_byte,
                end_byte,
                prev_state,
                self._keyword_set,
                self._builtin_set,
                self._magic_set,
            )
        else:
            # Pure-Python fallback - identical logic to lexer_fast.pyx
            prev_state = _py_compute_state(text_bytes, start_byte)
            final_state, styled_tokens = _py_style_chunk(
                text_bytes,
                start_byte,
                end_byte,
                prev_state,
                self._keyword_set,
                self._builtin_set,
                self._magic_set,
            )

        self.startStyling(start)
        for byte_len, style_id in styled_tokens:
            self.setStyling(byte_len, style_id)

        self._prev_state = final_state
```


**New version:**


```python
    def styleText(self, start: int, end: int) -> None:
        """Apply native or fallback style runs to QScintilla's requested range.

        Args:
            start: First UTF-8 byte requested by Scintilla.
            end: Exclusive final byte requested by Scintilla.

        Rescan context before the requested offset because Scintilla can resume
        in a different region after edits or scrolling. Both native functions
        must be available together; otherwise use the Python implementation.
        """
        full_text = self._editor.text()
        text_bytes = full_text.encode('utf-8')

        start_char = self._byte_pos_to_char_index(full_text, start)
        end_char = self._byte_pos_to_char_index(full_text, end)

        start_byte = len(full_text[:start_char].encode('utf-8'))
        end_byte = len(full_text[:end_char].encode('utf-8'))

        # Compute the correct lexer state at start_byte by scanning from byte 0.
        # This is necessary because QScintilla may call styleText for
        # non-contiguous regions (e.g. when the user scrolls).
        if _cython_style is not None and _cython_state is not None:
            prev_state = _cython_state(text_bytes, start_byte)
            final_state, styled_tokens = _cython_style(
                text_bytes,
                start_byte,
                end_byte,
                prev_state,
                self._keyword_set,
                self._builtin_set,
                self._magic_set,
            )
        else:
            # Pure-Python fallback - identical logic to lexer_fast.pyx
            prev_state = _py_compute_state(text_bytes, start_byte)
            final_state, styled_tokens = _py_style_chunk(
                text_bytes,
                start_byte,
                end_byte,
                prev_state,
                self._keyword_set,
                self._builtin_set,
                self._magic_set,
            )

        self.startStyling(start)
        for byte_len, style_id in styled_tokens:
            self.setStyling(byte_len, style_id)

        self._prev_state = final_state
```


**Implementation:** inside `python_editor/custompythonlexer.py`, replace only `PyCustomLexer.styleText`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 1.2. `python_editor/lexer_fast.pyx`


#### 1.2.1 Existing function `compute_state_before`

Only the opening quote character can terminate this triple-quoted string. The run scanner also stops only at that delimiter or a backslash; otherwise an opposite quote can both corrupt the resume state and prevent the scanner from advancing.


**Old function — original line 171:**


```cython
def compute_state_before(bytes text, int target_pos):
    cdef int length = len(text)
    if target_pos > length:
        target_pos = length

    cdef int i = 0
    cdef int start
    cdef unsigned char c
    cdef unsigned char next_c
    cdef int delim
    cdef int in_string = 0
    cdef int in_comment = 0
    cdef int triple_string = 0
    cdef int string_delim = 0
    cdef int in_fstring = 0
    cdef int escape_next = 0
    cdef int in_fexpr = 0
    cdef int fexpr_depth = 0
    cdef int is_docstring = 0

    cdef int bracket_depth = 0
    cdef int pending_def = 0
    cdef int pending_class = 0
    cdef int expect_docstring = 0
    cdef int at_class_body = 0

    while i < target_pos:
        c = text[i]

        # ---- inside f-string expression { ... } ----
        if in_fexpr:
            if c == 125:  # }
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                i += 1
                continue
            if c == 123:  # {
                fexpr_depth += 1
                i += 1
                continue
            # prefixed nested string
            if (c == 102 or c == 114 or c == 98) and i + 1 < target_pos:
                next_c = text[i + 1]
                if next_c == 34 or next_c == 39:
                    delim = next_c
                    i += 2
                    if i + 1 < length and text[i] == delim and text[i+1] == delim:
                        i += 2
                        _skip_string(text, target_pos, &i, delim, 1)
                    else:
                        _skip_string(text, target_pos, &i, delim, 0)
                    continue
            if c == 34 or c == 39:
                delim = c
                i += 1
                if i + 1 < length and text[i] == delim and text[i+1] == delim:
                    i += 2
                    _skip_string(text, target_pos, &i, delim, 1)
                else:
                    _skip_string(text, target_pos, &i, delim, 0)
                continue
            i += 1
            continue

        # ---- comment ----
        if in_comment:
            if c == 10 or c == 13:
                in_comment = 0
            i += 1
            continue

        # ---- inside string ----
        if in_string:
            if escape_next:
                escape_next = 0
                i += 1
                continue
            if c == 92:
                escape_next = 1
                i += 1
                continue
            if triple_string:
                if c == 34 or c == 39:
                    if i + 2 < length and text[i+1] == c and text[i+2] == c:
                        in_string = 0
                        triple_string = 0
                        string_delim = 0
                        in_fstring = 0
                        is_docstring = 0
                        i += 3
                        continue
                    i += 1
                    continue
                if in_fstring and c == 123:
                    if i + 1 < length and text[i+1] == 123:
                        i += 2
                        continue
                    in_fexpr = 1
                    fexpr_depth = 1
                    i += 1
                    continue
                i += 1
                continue
            # single-line string
            if c == string_delim:
                in_string = 0
                string_delim = 0
                in_fstring = 0
                is_docstring = 0
                i += 1
                continue
            if in_fstring and c == 123:
                if i + 1 < length and text[i+1] == 123:
                    i += 2
                    continue
                in_fexpr = 1
                fexpr_depth = 1
                i += 1
                continue
            i += 1
            continue

        # ---- not in string/comment ----

        # string prefix f/r/b
        if (c == 102 or c == 114 or c == 98) and i + 1 < target_pos:
            next_c = text[i + 1]
            if next_c == 34 or next_c == 39:
                if i + 3 < length and text[i+2] == next_c and text[i+3] == next_c:
                    in_string = 1
                    triple_string = 1
                    string_delim = next_c
                    in_fstring = 1 if (c == 102) else 0
                    if expect_docstring:
                        is_docstring = 1
                    expect_docstring = 0
                    i += 4
                    continue
                in_string = 1
                triple_string = 0
                string_delim = next_c
                in_fstring = 1 if (c == 102) else 0
                expect_docstring = 0
                i += 2
                continue

        # regular string
        if c == 34 or c == 39:
            if i + 2 < length and text[i+1] == c and text[i+2] == c:
                in_string = 1
                triple_string = 1
                string_delim = c
                in_fstring = 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 3
                continue
            in_string = 1
            triple_string = 0
            string_delim = c
            in_fstring = 0
            expect_docstring = 0
            i += 1
            continue

        # comment
        if c == 35:
            in_comment = 1
            i += 1
            continue

        # brackets
        if c == 40 or c == 91 or c == 123:
            bracket_depth += 1
            i += 1
            continue
        if c == 41 or c == 93 or c == 125:
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        # colon
        if c == 58:
            if bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = 0
                pending_class = 0
            i += 1
            continue

        # arrow ->
        if c == 45 and i + 1 < target_pos and text[i+1] == 62:
            i += 2
            continue

        # identifier
        if is_alpha(c):
            start = i
            i += 1
            while i < target_pos and is_alnum(text[i]):
                i += 1
            if text[start:i] == b"def":
                pending_def = 1
                pending_class = 0
                at_class_body = 0
            elif text[start:i] == b"class":
                pending_class = 1
                pending_def = 0
                at_class_body = 0
            else:
                expect_docstring = 0
            continue

        # newline (do NOT reset expect_docstring/pending_def here -
        # docstrings live on the line after the def/class header)
        if c == 10 or c == 13:
            i += 1
            continue

        i += 1

    return pack_state(in_string, in_comment, triple_string,
                      string_delim, in_fstring, escape_next,
                      in_fexpr, fexpr_depth, is_docstring,
                      expect_docstring, at_class_body)


# --- The full styler ---
```


**New function:**


```cython
def compute_state_before(bytes text, int target_pos):
    """Reconstruct lexical state at a byte offset before incremental styling.

    Args:
        text: Complete source encoded as UTF-8 bytes.
        target_pos: Byte offset at which styling will resume, clamped to EOF.

    Returns:
        Packed integer state describing strings, comments, f-string expressions
        and docstring context at that offset. A triple string closes only with
        three copies of its opening quote character; the other quote is data.
    """
    cdef int length = len(text)
    if target_pos > length:
        target_pos = length

    cdef int i = 0
    cdef int start
    cdef unsigned char c
    cdef unsigned char next_c
    cdef int delim
    cdef int in_string = 0
    cdef int in_comment = 0
    cdef int triple_string = 0
    cdef int string_delim = 0
    cdef int in_fstring = 0
    cdef int escape_next = 0
    cdef int in_fexpr = 0
    cdef int fexpr_depth = 0
    cdef int is_docstring = 0

    cdef int bracket_depth = 0
    cdef int pending_def = 0
    cdef int pending_class = 0
    cdef int expect_docstring = 0
    cdef int at_class_body = 0

    while i < target_pos:
        c = text[i]

        # ---- inside f-string expression { ... } ----
        if in_fexpr:
            if c == 125:  # }
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                i += 1
                continue
            if c == 123:  # {
                fexpr_depth += 1
                i += 1
                continue
            # prefixed nested string
            if (c == 102 or c == 114 or c == 98) and i + 1 < target_pos:
                next_c = text[i + 1]
                if next_c == 34 or next_c == 39:
                    delim = next_c
                    i += 2
                    if i + 1 < length and text[i] == delim and text[i+1] == delim:
                        i += 2
                        _skip_string(text, target_pos, &i, delim, 1)
                    else:
                        _skip_string(text, target_pos, &i, delim, 0)
                    continue
            if c == 34 or c == 39:
                delim = c
                i += 1
                if i + 1 < length and text[i] == delim and text[i+1] == delim:
                    i += 2
                    _skip_string(text, target_pos, &i, delim, 1)
                else:
                    _skip_string(text, target_pos, &i, delim, 0)
                continue
            i += 1
            continue

        # ---- comment ----
        if in_comment:
            if c == 10 or c == 13:
                in_comment = 0
            i += 1
            continue

        # ---- inside string ----
        if in_string:
            if escape_next:
                escape_next = 0
                i += 1
                continue
            if c == 92:
                escape_next = 1
                i += 1
                continue
            if triple_string:
                # Match the opening delimiter, not either possible quote.
                if c == string_delim:
                    if i + 2 < length and text[i+1] == c and text[i+2] == c:
                        in_string = 0
                        triple_string = 0
                        string_delim = 0
                        in_fstring = 0
                        is_docstring = 0
                        i += 3
                        continue
                    i += 1
                    continue
                if in_fstring and c == 123:
                    if i + 1 < length and text[i+1] == 123:
                        i += 2
                        continue
                    in_fexpr = 1
                    fexpr_depth = 1
                    i += 1
                    continue
                i += 1
                continue
            # single-line string
            if c == string_delim:
                in_string = 0
                string_delim = 0
                in_fstring = 0
                is_docstring = 0
                i += 1
                continue
            if in_fstring and c == 123:
                if i + 1 < length and text[i+1] == 123:
                    i += 2
                    continue
                in_fexpr = 1
                fexpr_depth = 1
                i += 1
                continue
            i += 1
            continue

        # ---- not in string/comment ----

        # string prefix f/r/b
        if (c == 102 or c == 114 or c == 98) and i + 1 < target_pos:
            next_c = text[i + 1]
            if next_c == 34 or next_c == 39:
                if i + 3 < length and text[i+2] == next_c and text[i+3] == next_c:
                    in_string = 1
                    triple_string = 1
                    string_delim = next_c
                    in_fstring = 1 if (c == 102) else 0
                    if expect_docstring:
                        is_docstring = 1
                    expect_docstring = 0
                    i += 4
                    continue
                in_string = 1
                triple_string = 0
                string_delim = next_c
                in_fstring = 1 if (c == 102) else 0
                expect_docstring = 0
                i += 2
                continue

        # regular string
        if c == 34 or c == 39:
            if i + 2 < length and text[i+1] == c and text[i+2] == c:
                in_string = 1
                triple_string = 1
                string_delim = c
                in_fstring = 0
                if expect_docstring:
                    is_docstring = 1
                expect_docstring = 0
                i += 3
                continue
            in_string = 1
            triple_string = 0
            string_delim = c
            in_fstring = 0
            expect_docstring = 0
            i += 1
            continue

        # comment
        if c == 35:
            in_comment = 1
            i += 1
            continue

        # brackets
        if c == 40 or c == 91 or c == 123:
            bracket_depth += 1
            i += 1
            continue
        if c == 41 or c == 93 or c == 125:
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        # colon
        if c == 58:
            if bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = 0
                pending_class = 0
            i += 1
            continue

        # arrow ->
        if c == 45 and i + 1 < target_pos and text[i+1] == 62:
            i += 2
            continue

        # identifier
        if is_alpha(c):
            start = i
            i += 1
            while i < target_pos and is_alnum(text[i]):
                i += 1
            if text[start:i] == b"def":
                pending_def = 1
                pending_class = 0
                at_class_body = 0
            elif text[start:i] == b"class":
                pending_class = 1
                pending_def = 0
                at_class_body = 0
            else:
                expect_docstring = 0
            continue

        # newline (do NOT reset expect_docstring/pending_def here -
        # docstrings live on the line after the def/class header)
        if c == 10 or c == 13:
            i += 1
            continue

        i += 1

    return pack_state(in_string, in_comment, triple_string,
                      string_delim, in_fstring, escape_next,
                      in_fexpr, fexpr_depth, is_docstring,
                      expect_docstring, at_class_body)


# --- The full styler ---
```


**Implementation:** replace this function from its `def compute_state_before(` line through the end of its body. Keep the preceding Cython helpers and style enum. Rebuild only after both functions have been changed.


#### 1.2.2 Existing function `style_chunk`

Only the opening quote character can terminate this triple-quoted string. The run scanner also stops only at that delimiter or a backslash; otherwise an opposite quote can both corrupt the resume state and prevent the scanner from advancing.


**Old function — original line 406:**


```cython
def style_chunk(bytes text, int start, int end, int prev_state,
                set keywords, set builtins, set magic_methods):
    cdef int length = len(text)
    if end > length:
        end = length
    if start < 0:
        start = 0

    cdef int in_string, in_comment, triple_string, string_delim
    cdef int in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring
    cdef int expect_docstring
    cdef int at_class_body
    (in_string, in_comment, triple_string, string_delim,
     in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring,
     expect_docstring, at_class_body) = unpack_state(prev_state)

    cdef list results = []
    cdef int i = start
    cdef int token_start
    cdef unsigned char c
    cdef bytes token_bytes
    cdef str token_str
    cdef unsigned char next_c
    cdef int string_style

    # Context tracking
    cdef int after_def = 0
    cdef int after_class = 0
    cdef int after_dot = 0
    cdef int after_at = 0
    cdef int in_def_params = 0
    cdef int param_depth = 0
    cdef int at_type_pos = 0
    cdef int after_arrow = 0
    cdef int bracket_depth = 0
    cdef int pending_def = 0
    cdef int pending_class = 0

    cdef int prev_id_type = 0
    cdef int dot_owner_type = 0

    cdef int after_from = 0
    cdef int after_import = 0
    cdef int in_from_import = 0
    cdef bint followed_by_paren
    cdef bint followed_by_eq
    cdef bint at_arg_pos = False
    cdef bint followed_by_assign
    cdef int _j

    if in_string and is_docstring:
        string_style = STYLE_DOCSTRING
    else:
        string_style = STYLE_STRING

    while i < end:
        c = text[i]

        # ============ COMMENT ============
        if in_comment:
            token_start = i
            while i < end and text[i] != 10 and text[i] != 13:
                i += 1
            if i > token_start:
                results.append((i - token_start, STYLE_COMMENTS))
            if i < end and (text[i] == 10 or text[i] == 13):
                in_comment = 0
                if text[i] == 13 and i + 1 < end and text[i+1] == 10:
                    results.append((2, STYLE_DEFAULT))
                    i += 2
                else:
                    results.append((1, STYLE_DEFAULT))
                    i += 1
            continue

        # ============ F-STRING EXPRESSION { ... } ============
        if in_fexpr:
            if c == 125:  # }
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                    results.append((1, string_style))
                else:
                    results.append((1, STYLE_BRACKETS))
                i += 1
                continue
            if c == 123:  # {
                fexpr_depth += 1
                results.append((1, STYLE_BRACKETS))
                i += 1
                continue
            if (c == 102 or c == 114 or c == 98) and i + 1 < end:
                next_c = text[i + 1]
                if next_c == 34 or next_c == 39:
                    token_start = i
                    # CHUNK-SAFETY: only consume 4 bytes when all 4 are
                    # inside THIS chunk (not `length` = full document).
                    if i + 3 < end and text[i+2] == next_c and text[i+3] == next_c:
                        results.append((4, STYLE_STRING))
                        i += 4
                    else:
                        results.append((2, STYLE_STRING))
                        i += 2
                    continue
            if c == 34 or c == 39:
                token_start = i
                i += 1
                while i < end:
                    if text[i] == 92:
                        # CHUNK-SAFETY: a backslash as the LAST byte of the
                        # chunk must not skip past `end` (would style one
                        # byte too many).
                        if i + 1 < end:
                            i += 2
                        else:
                            i += 1
                        continue
                    if text[i] == c:
                        i += 1
                        break
                    if text[i] == 10 or text[i] == 13:
                        break
                    i += 1
                results.append((i - token_start, STYLE_STRING))
                continue
            if c == 35:
                token_start = i
                while i < end and text[i] != 10 and text[i] != 13:
                    i += 1
                results.append((i - token_start, STYLE_COMMENTS))
                continue
            if is_alpha(c):
                token_start = i
                while i < end and is_alnum(text[i]):
                    i += 1
                token_bytes = text[token_start:i]
                token_str = token_bytes.decode('utf-8', errors='replace')
                followed_by_paren = (i < end and text[i] == 40)
                if token_str in ("True", "False", "None"):
                    results.append((i - token_start, STYLE_CONSTANTS))
                elif token_str in ("self", "cls"):
                    results.append((i - token_start, STYLE_SELF_CLS))
                elif token_str in keywords:
                    results.append((i - token_start, STYLE_KEYWORD))
                elif token_str in builtins:
                    results.append((i - token_start, STYLE_BUILTINS))
                elif followed_by_paren:
                    results.append((i - token_start, STYLE_FUNCTION_CALL))
                elif len(token_str) > 0 and token_str[0].isupper():
                    results.append((i - token_start, STYLE_CLASS_REFERENCE))
                else:
                    results.append((i - token_start, STYLE_LOCAL_VARIABLE))
                continue
            if is_digit(c):
                token_start = i
                while i < end and (is_alnum(text[i]) or text[i] == 46):
                    i += 1
                results.append((i - token_start, STYLE_NUMBERS))
                continue
            if is_operator(c):
                token_start = i
                i += 1
                if i < end and is_operator(text[i]):
                    i += 1
                results.append((i - token_start, STYLE_OPERATORS))
                continue
            if is_bracket(c):
                results.append((1, STYLE_BRACKETS))
                i += 1
                continue
            if is_space(c):
                token_start = i
                while i < end and is_space(text[i]):
                    i += 1
                results.append((i - token_start, STYLE_DEFAULT))
                continue
            if c == 10 or c == 13:
                results.append((1, STYLE_DEFAULT))
                i += 1
                continue
            results.append((1, STYLE_DEFAULT))
            i += 1
            continue

        # ============ STRING ============
        if in_string:
            token_start = i

            if escape_next:
                i += 1
                escape_next = 0
                results.append((i - token_start, string_style))
                continue

            if c == 92:
                i += 1
                escape_next = 1
                results.append((1, string_style))
                continue

            if triple_string:
                if c == 34 or c == 39:
                    # CHUNK-SAFETY: the closing '"""' may straddle the chunk
                    # end. Only consume 3 quote bytes when ALL of them are
                    # inside THIS chunk (i + 2 < end, NOT < length). Styling
                    # more bytes than the chunk contains corrupts
                    # Scintilla's style buffer and crashes the editor.
                    if i + 2 < end and text[i+1] == c and text[i+2] == c:
                        results.append((3, string_style))
                        i += 3
                        in_string = 0
                        triple_string = 0
                        string_delim = 0
                        in_fstring = 0
                        is_docstring = 0
                        string_style = STYLE_STRING
                        continue
                    results.append((1, string_style))
                    i += 1
                    continue
                if in_fstring and c == 123:
                    # CHUNK-SAFETY: '{{' needs both braces inside the chunk.
                    if i + 1 < end and text[i+1] == 123:
                        if i > token_start:
                            results.append((i - token_start, string_style))
                        results.append((2, string_style))
                        i += 2
                        continue
                    if i > token_start:
                        results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    in_fexpr = 1
                    fexpr_depth = 1
                    continue
                token_start = i
                while i < end:
                    c = text[i]
                    if c == 34 or c == 39 or c == 92:
                        break
                    if in_fstring and c == 123:
                        break
                    i += 1
                if i > token_start:
                    results.append((i - token_start, string_style))
                continue

            # single-line string
            token_start = i
            while i < end:
                c = text[i]
                if c == string_delim:
                    results.append((i - token_start + 1, string_style))
                    i += 1
                    in_string = 0
                    string_delim = 0
                    in_fstring = 0
                    is_docstring = 0
                    string_style = STYLE_STRING
                    break
                if c == 92:
                    results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    escape_next = 1
                    break
                if in_fstring and c == 123:
                    # CHUNK-SAFETY: '{{' needs both braces inside the chunk.
                    if i + 1 < end and text[i+1] == 123:
                        if i > token_start:
                            results.append((i - token_start, string_style))
                        results.append((2, string_style))
                        i += 2
                        token_start = i
                        continue
                    if i > token_start:
                        results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    in_fexpr = 1
                    fexpr_depth = 1
                    break
                if c == 10 or c == 13:
                    results.append((i - token_start, string_style))
                    in_string = 0
                    string_delim = 0
                    in_fstring = 0
                    is_docstring = 0
                    string_style = STYLE_STRING
                    break
                i += 1
            else:
                results.append((i - token_start, string_style))
            continue

        # ============ NOT IN STRING OR COMMENT ============

        # Whitespace (preserves at_arg_pos / at_type_pos)
        if is_space(c):
            token_start = i
            while i < end and is_space(text[i]):
                i += 1
            results.append((i - token_start, STYLE_DEFAULT))
            continue

        # Newline
        if c == 10 or c == 13:
            if c == 13 and i + 1 < end and text[i+1] == 10:
                results.append((2, STYLE_DEFAULT))
                i += 2
            else:
                results.append((1, STYLE_DEFAULT))
                i += 1
            if bracket_depth == 0:
                after_def = 0
                after_class = 0
                after_at = 0
                after_dot = 0
                prev_id_type = 0
                dot_owner_type = 0
                after_from = 0
                after_import = 0
                in_from_import = 0
                at_arg_pos = False
                at_type_pos = 0
                after_arrow = 0
            continue

        # String with prefix: f"...", r'...', b"..."
        if (c == 102 or c == 114 or c == 98) and i + 1 < end:
            next_c = text[i + 1]
            if next_c == 34 or next_c == 39:
                token_start = i
                # CHUNK-SAFETY: prefixed triple strings need all 4 bytes
                # inside THIS chunk, not just inside the document.
                if i + 3 < end and text[i+2] == next_c and text[i+3] == next_c:
                    if expect_docstring:
                        string_style = STYLE_DOCSTRING
                        is_docstring = 1
                    else:
                        string_style = STYLE_STRING
                    results.append((4, string_style))
                    i += 4
                    in_string = 1
                    triple_string = 1
                    string_delim = next_c
                    in_fstring = 1 if (c == 102) else 0
                else:
                    results.append((2, STYLE_STRING))
                    i += 2
                    in_string = 1
                    triple_string = 0
                    string_delim = next_c
                    in_fstring = 1 if (c == 102) else 0
                expect_docstring = 0
                prev_id_type = 0
                continue

        # Regular string
        if c == 34 or c == 39:
            # CHUNK-SAFETY: the opening '"""' may straddle the chunk end.
            # Only consume 3 quote bytes when ALL of them are inside THIS
            # chunk; otherwise fall through to single-line-string handling
            # (the next chunk's state scan sees the full triple and styles
            # the remaining quotes correctly).
            if i + 2 < end and text[i+1] == c and text[i+2] == c:
                if expect_docstring:
                    string_style = STYLE_DOCSTRING
                    is_docstring = 1
                else:
                    string_style = STYLE_STRING
                results.append((3, string_style))
                i += 3
                in_string = 1
                triple_string = 1
                string_delim = c
                in_fstring = 0
            else:
                results.append((1, STYLE_STRING))
                i += 1
                in_string = 1
                triple_string = 0
                string_delim = c
                in_fstring = 0
            expect_docstring = 0
            prev_id_type = 0
            continue

        # Comment
        if c == 35:
            in_comment = 1
            token_start = i
            i += 1
            while i < end and text[i] != 10 and text[i] != 13:
                i += 1
            results.append((i - token_start, STYLE_COMMENTS))
            prev_id_type = 0
            continue

        # Decorator
        if c == 64:
            results.append((1, STYLE_DECORATOR))
            i += 1
            after_at = 1
            expect_docstring = 0
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Number
        if is_digit(c):
            token_start = i
            while i < end and (is_alnum(text[i]) or text[i] == 46):
                i += 1
            results.append((i - token_start, STYLE_NUMBERS))
            expect_docstring = 0
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Dot
        if c == 46:
            results.append((1, STYLE_DEFAULT))
            i += 1
            if after_from or after_import:
                pass
            else:
                after_dot = 1
                dot_owner_type = prev_id_type
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Brackets
        if is_bracket(c):
            results.append((1, STYLE_BRACKETS))
            if c == 40 or c == 91 or c == 123:
                bracket_depth += 1
                if c == 40 and after_def:
                    in_def_params = 1
                    param_depth = 1
                    after_def = 0
                    at_type_pos = 0
                elif in_def_params:
                    param_depth += 1
                at_arg_pos = True
            elif c == 41 or c == 93 or c == 125:
                if bracket_depth > 0:
                    bracket_depth -= 1
                if in_def_params:
                    param_depth -= 1
                    if param_depth <= 0:
                        in_def_params = 0
                        param_depth = 0
                        at_type_pos = 0
                at_arg_pos = False
            i += 1
            after_dot = 0
            prev_id_type = 0
            continue

        # Operators
        if is_operator(c):
            token_start = i
            i += 1
            if i < end and is_operator(text[i]):
                i += 1
            results.append((i - token_start, STYLE_OPERATORS))
            expect_docstring = 0
            if text[token_start] == 45 and (token_start + 1 < end) and text[token_start+1] == 62:
                if pending_def and bracket_depth == 0:
                    after_arrow = 1
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Comma
        if c == 44:
            results.append((1, STYLE_COMMA))
            i += 1
            if in_def_params:
                at_type_pos = 0
            if not after_import and not in_from_import and not after_from:
                prev_id_type = 0
            at_arg_pos = True
            continue

        # Colon
        if c == 58:
            results.append((1, STYLE_DEFAULT))
            if in_def_params and param_depth == 1:
                at_type_pos = 1
            elif bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = 0
                pending_class = 0
                after_arrow = 0
            i += 1
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Semicolon
        if c == 59:
            results.append((1, STYLE_DEFAULT))
            i += 1
            expect_docstring = 0
            after_from = 0
            after_import = 0
            in_from_import = 0
            prev_id_type = 0
            at_arg_pos = False
            continue

        # ============ IDENTIFIER (word) ============
        if is_alpha(c):
            token_start = i
            while i < end and is_alnum(text[i]):
                i += 1

            token_bytes = text[token_start:i]
            token_str = token_bytes.decode('utf-8', errors='replace')

            followed_by_paren = (i < end and text[i] == 40)
            followed_by_eq = (i < end and text[i] == 61 and
                              (i + 1 >= end or text[i+1] != 61))
            _j = i
            while _j < end and (text[_j] == 32 or text[_j] == 9):
                _j += 1
            followed_by_assign = (_j < end and text[_j] == 61 and
                                  (_j + 1 >= end or text[_j+1] != 61))

            if not (token_str == "def" or token_str == "class"):
                expect_docstring = 0

            # --- Style decision tree (mirrors PyCharm's Python semantics) ---
            if after_at:
                results.append((i - token_start, STYLE_DECORATOR))
                after_at = 0
                prev_id_type = 0

            elif token_str in ("self", "cls"):
                results.append((i - token_start, STYLE_SELF_CLS))
                prev_id_type = 1

            elif token_str in ("True", "False", "None"):
                results.append((i - token_start, STYLE_CONSTANTS))
                prev_id_type = 0

            elif token_str == "def":
                results.append((i - token_start, STYLE_KEYWORD))
                after_def = 1
                pending_def = 1
                pending_class = 0
                at_class_body = 0
                prev_id_type = 0

            elif token_str == "class":
                results.append((i - token_start, STYLE_KEYWORD))
                after_class = 1
                pending_class = 1
                pending_def = 0
                prev_id_type = 0

            elif token_str == "import":
                results.append((i - token_start, STYLE_KEYWORD))
                if after_from:
                    after_from = 0
                    in_from_import = 1
                else:
                    after_import = 1
                prev_id_type = 0

            elif token_str == "from":
                results.append((i - token_start, STYLE_KEYWORD))
                after_from = 1
                prev_id_type = 0

            elif token_str == "as":
                results.append((i - token_start, STYLE_KEYWORD))
                after_import = 0
                in_from_import = 0
                prev_id_type = 0

            elif token_str in keywords:
                results.append((i - token_start, STYLE_KEYWORD))
                prev_id_type = 0

            elif after_def:
                # Method/function declaration name. Magic methods (dunders)
                # get their own magenta color in PyCharm.
                if token_str in magic_methods:
                    results.append((i - token_start, STYLE_MAGIC_METHODS))
                else:
                    results.append((i - token_start, STYLE_FUNCTION_DEF))
                prev_id_type = 3

            elif after_class:
                results.append((i - token_start, STYLE_CLASSES))
                after_class = 0
                prev_id_type = 2

            elif after_dot:
                # Anything CALLED after a dot is violet (method call),
                # anything merely referenced is grey (field).
                if followed_by_paren:
                    results.append((i - token_start, STYLE_INSTANCE_METHOD))
                else:
                    results.append((i - token_start, STYLE_INSTANCE_FIELD))
                after_dot = 0
                dot_owner_type = 0
                prev_id_type = 3

            elif in_def_params and param_depth == 1:
                if at_type_pos:
                    results.append((i - token_start, STYLE_TYPES))
                else:
                    results.append((i - token_start, STYLE_PARAMETERS))
                prev_id_type = 3

            elif after_arrow:
                results.append((i - token_start, STYLE_TYPES))
                prev_id_type = 2

            elif after_from:
                results.append((i - token_start, STYLE_MODULE_NAME))
                prev_id_type = 0

            elif after_import:
                results.append((i - token_start, STYLE_MODULE_NAME))
                prev_id_type = 0

            elif in_from_import:
                if len(token_str) > 0 and token_str[0].isupper():
                    results.append((i - token_start, STYLE_CLASS_REFERENCE))
                    prev_id_type = 2
                else:
                    results.append((i - token_start, STYLE_MODULE_NAME))
                    prev_id_type = 0

            elif (at_arg_pos and followed_by_eq and not in_def_params):
                results.append((i - token_start, STYLE_KEYARGS))
                prev_id_type = 3

            elif at_class_body and followed_by_assign:
                # class-body attribute assignment target -> grey (like PyCharm)
                results.append((i - token_start, STYLE_INSTANCE_FIELD))
                prev_id_type = 3

            elif token_str in builtins:
                # Builtins (super, print, str, os, ...) are grey in PyCharm,
                # even when called.
                results.append((i - token_start, STYLE_BUILTINS))
                prev_id_type = 3

            elif followed_by_paren:
                # A called identifier: function call / constructor call (violet).
                # Checked BEFORE the uppercase class-reference branch so that
                # QFont() / QLabel() render as calls, like in PyCharm.
                results.append((i - token_start, STYLE_FUNCTION_CALL))
                prev_id_type = 3

            elif (token_str.startswith("__") and token_str.endswith("__")
                    and len(token_str) > 4):
                # Dunder references (e.g. __file__, __name__) -> grey
                results.append((i - token_start, STYLE_BUILTINS))
                prev_id_type = 3

            elif len(token_str) > 0 and token_str[0].isupper():
                # Class reference at usage site -> grey (only the definition
                # site is colored soft red)
                results.append((i - token_start, STYLE_CLASS_REFERENCE))
                prev_id_type = 2

            else:
                results.append((i - token_start, STYLE_LOCAL_VARIABLE))
                prev_id_type = 3

            at_arg_pos = False
            continue

        # Unknown character
        results.append((1, STYLE_DEFAULT))
        i += 1
        prev_id_type = 0
        at_arg_pos = False

    cdef int final_state = pack_state(in_string, in_comment, triple_string,
                             string_delim, in_fstring, escape_next,
                             in_fexpr, fexpr_depth, is_docstring,
                             expect_docstring, at_class_body)
    return (final_state, results)
```


**New function:**


```cython
def style_chunk(bytes text, int start, int end, int prev_state,
                set keywords, set builtins, set magic_methods):
    """Tokenize one byte interval using the state reconstructed at its start.

    Args:
        text: Complete UTF-8 source buffer.
        start: First byte to style.
        end: Exclusive final byte, clamped to the source length.
        prev_state: Packed state from the corresponding state scanner.
        keywords: Python keyword names used by the theme's keyword style.
        builtins: Builtin and module names receiving the builtin style.
        magic_methods: Special method names receiving their dedicated style.

    Returns:
        A pair containing the final packed state and ordered (byte count, style
        ID) runs. Counts are bytes, matching QScintilla's styling API. Triple
        string runs stop at their own delimiter or an escape, not the other
        quote character; that also guarantees progress across embedded quotes.
    """
    cdef int length = len(text)
    if end > length:
        end = length
    if start < 0:
        start = 0

    cdef int in_string, in_comment, triple_string, string_delim
    cdef int in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring
    cdef int expect_docstring
    cdef int at_class_body
    (in_string, in_comment, triple_string, string_delim,
     in_fstring, escape_next, in_fexpr, fexpr_depth, is_docstring,
     expect_docstring, at_class_body) = unpack_state(prev_state)

    cdef list results = []
    cdef int i = start
    cdef int token_start
    cdef unsigned char c
    cdef bytes token_bytes
    cdef str token_str
    cdef unsigned char next_c
    cdef int string_style

    # Context tracking
    cdef int after_def = 0
    cdef int after_class = 0
    cdef int after_dot = 0
    cdef int after_at = 0
    cdef int in_def_params = 0
    cdef int param_depth = 0
    cdef int at_type_pos = 0
    cdef int after_arrow = 0
    cdef int bracket_depth = 0
    cdef int pending_def = 0
    cdef int pending_class = 0

    cdef int prev_id_type = 0
    cdef int dot_owner_type = 0

    cdef int after_from = 0
    cdef int after_import = 0
    cdef int in_from_import = 0
    cdef bint followed_by_paren
    cdef bint followed_by_eq
    cdef bint at_arg_pos = False
    cdef bint followed_by_assign
    cdef int _j

    if in_string and is_docstring:
        string_style = STYLE_DOCSTRING
    else:
        string_style = STYLE_STRING

    while i < end:
        c = text[i]

        # ============ COMMENT ============
        if in_comment:
            token_start = i
            while i < end and text[i] != 10 and text[i] != 13:
                i += 1
            if i > token_start:
                results.append((i - token_start, STYLE_COMMENTS))
            if i < end and (text[i] == 10 or text[i] == 13):
                in_comment = 0
                if text[i] == 13 and i + 1 < end and text[i+1] == 10:
                    results.append((2, STYLE_DEFAULT))
                    i += 2
                else:
                    results.append((1, STYLE_DEFAULT))
                    i += 1
            continue

        # ============ F-STRING EXPRESSION { ... } ============
        if in_fexpr:
            if c == 125:  # }
                fexpr_depth -= 1
                if fexpr_depth <= 0:
                    fexpr_depth = 0
                    in_fexpr = 0
                    results.append((1, string_style))
                else:
                    results.append((1, STYLE_BRACKETS))
                i += 1
                continue
            if c == 123:  # {
                fexpr_depth += 1
                results.append((1, STYLE_BRACKETS))
                i += 1
                continue
            if (c == 102 or c == 114 or c == 98) and i + 1 < end:
                next_c = text[i + 1]
                if next_c == 34 or next_c == 39:
                    token_start = i
                    # CHUNK-SAFETY: only consume 4 bytes when all 4 are
                    # inside THIS chunk (not `length` = full document).
                    if i + 3 < end and text[i+2] == next_c and text[i+3] == next_c:
                        results.append((4, STYLE_STRING))
                        i += 4
                    else:
                        results.append((2, STYLE_STRING))
                        i += 2
                    continue
            if c == 34 or c == 39:
                token_start = i
                i += 1
                while i < end:
                    if text[i] == 92:
                        # CHUNK-SAFETY: a backslash as the LAST byte of the
                        # chunk must not skip past `end` (would style one
                        # byte too many).
                        if i + 1 < end:
                            i += 2
                        else:
                            i += 1
                        continue
                    if text[i] == c:
                        i += 1
                        break
                    if text[i] == 10 or text[i] == 13:
                        break
                    i += 1
                results.append((i - token_start, STYLE_STRING))
                continue
            if c == 35:
                token_start = i
                while i < end and text[i] != 10 and text[i] != 13:
                    i += 1
                results.append((i - token_start, STYLE_COMMENTS))
                continue
            if is_alpha(c):
                token_start = i
                while i < end and is_alnum(text[i]):
                    i += 1
                token_bytes = text[token_start:i]
                token_str = token_bytes.decode('utf-8', errors='replace')
                followed_by_paren = (i < end and text[i] == 40)
                if token_str in ("True", "False", "None"):
                    results.append((i - token_start, STYLE_CONSTANTS))
                elif token_str in ("self", "cls"):
                    results.append((i - token_start, STYLE_SELF_CLS))
                elif token_str in keywords:
                    results.append((i - token_start, STYLE_KEYWORD))
                elif token_str in builtins:
                    results.append((i - token_start, STYLE_BUILTINS))
                elif followed_by_paren:
                    results.append((i - token_start, STYLE_FUNCTION_CALL))
                elif len(token_str) > 0 and token_str[0].isupper():
                    results.append((i - token_start, STYLE_CLASS_REFERENCE))
                else:
                    results.append((i - token_start, STYLE_LOCAL_VARIABLE))
                continue
            if is_digit(c):
                token_start = i
                while i < end and (is_alnum(text[i]) or text[i] == 46):
                    i += 1
                results.append((i - token_start, STYLE_NUMBERS))
                continue
            if is_operator(c):
                token_start = i
                i += 1
                if i < end and is_operator(text[i]):
                    i += 1
                results.append((i - token_start, STYLE_OPERATORS))
                continue
            if is_bracket(c):
                results.append((1, STYLE_BRACKETS))
                i += 1
                continue
            if is_space(c):
                token_start = i
                while i < end and is_space(text[i]):
                    i += 1
                results.append((i - token_start, STYLE_DEFAULT))
                continue
            if c == 10 or c == 13:
                results.append((1, STYLE_DEFAULT))
                i += 1
                continue
            results.append((1, STYLE_DEFAULT))
            i += 1
            continue

        # ============ STRING ============
        if in_string:
            token_start = i

            if escape_next:
                i += 1
                escape_next = 0
                results.append((i - token_start, string_style))
                continue

            if c == 92:
                i += 1
                escape_next = 1
                results.append((1, string_style))
                continue

            if triple_string:
                # Match the opening delimiter, not either possible quote.
                if c == string_delim:
                    # CHUNK-SAFETY: the closing '"""' may straddle the chunk
                    # end. Only consume 3 quote bytes when ALL of them are
                    # inside THIS chunk (i + 2 < end, NOT < length). Styling
                    # more bytes than the chunk contains corrupts
                    # Scintilla's style buffer and crashes the editor.
                    if i + 2 < end and text[i+1] == c and text[i+2] == c:
                        results.append((3, string_style))
                        i += 3
                        in_string = 0
                        triple_string = 0
                        string_delim = 0
                        in_fstring = 0
                        is_docstring = 0
                        string_style = STYLE_STRING
                        continue
                    results.append((1, string_style))
                    i += 1
                    continue
                if in_fstring and c == 123:
                    # CHUNK-SAFETY: '{{' needs both braces inside the chunk.
                    if i + 1 < end and text[i+1] == 123:
                        if i > token_start:
                            results.append((i - token_start, string_style))
                        results.append((2, string_style))
                        i += 2
                        continue
                    if i > token_start:
                        results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    in_fexpr = 1
                    fexpr_depth = 1
                    continue
                token_start = i
                while i < end:
                    c = text[i]
                    if c == string_delim or c == 92:
                        break
                    if in_fstring and c == 123:
                        break
                    i += 1
                if i > token_start:
                    results.append((i - token_start, string_style))
                continue

            # single-line string
            token_start = i
            while i < end:
                c = text[i]
                if c == string_delim:
                    results.append((i - token_start + 1, string_style))
                    i += 1
                    in_string = 0
                    string_delim = 0
                    in_fstring = 0
                    is_docstring = 0
                    string_style = STYLE_STRING
                    break
                if c == 92:
                    results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    escape_next = 1
                    break
                if in_fstring and c == 123:
                    # CHUNK-SAFETY: '{{' needs both braces inside the chunk.
                    if i + 1 < end and text[i+1] == 123:
                        if i > token_start:
                            results.append((i - token_start, string_style))
                        results.append((2, string_style))
                        i += 2
                        token_start = i
                        continue
                    if i > token_start:
                        results.append((i - token_start, string_style))
                    results.append((1, string_style))
                    i += 1
                    in_fexpr = 1
                    fexpr_depth = 1
                    break
                if c == 10 or c == 13:
                    results.append((i - token_start, string_style))
                    in_string = 0
                    string_delim = 0
                    in_fstring = 0
                    is_docstring = 0
                    string_style = STYLE_STRING
                    break
                i += 1
            else:
                results.append((i - token_start, string_style))
            continue

        # ============ NOT IN STRING OR COMMENT ============

        # Whitespace (preserves at_arg_pos / at_type_pos)
        if is_space(c):
            token_start = i
            while i < end and is_space(text[i]):
                i += 1
            results.append((i - token_start, STYLE_DEFAULT))
            continue

        # Newline
        if c == 10 or c == 13:
            if c == 13 and i + 1 < end and text[i+1] == 10:
                results.append((2, STYLE_DEFAULT))
                i += 2
            else:
                results.append((1, STYLE_DEFAULT))
                i += 1
            if bracket_depth == 0:
                after_def = 0
                after_class = 0
                after_at = 0
                after_dot = 0
                prev_id_type = 0
                dot_owner_type = 0
                after_from = 0
                after_import = 0
                in_from_import = 0
                at_arg_pos = False
                at_type_pos = 0
                after_arrow = 0
            continue

        # String with prefix: f"...", r'...', b"..."
        if (c == 102 or c == 114 or c == 98) and i + 1 < end:
            next_c = text[i + 1]
            if next_c == 34 or next_c == 39:
                token_start = i
                # CHUNK-SAFETY: prefixed triple strings need all 4 bytes
                # inside THIS chunk, not just inside the document.
                if i + 3 < end and text[i+2] == next_c and text[i+3] == next_c:
                    if expect_docstring:
                        string_style = STYLE_DOCSTRING
                        is_docstring = 1
                    else:
                        string_style = STYLE_STRING
                    results.append((4, string_style))
                    i += 4
                    in_string = 1
                    triple_string = 1
                    string_delim = next_c
                    in_fstring = 1 if (c == 102) else 0
                else:
                    results.append((2, STYLE_STRING))
                    i += 2
                    in_string = 1
                    triple_string = 0
                    string_delim = next_c
                    in_fstring = 1 if (c == 102) else 0
                expect_docstring = 0
                prev_id_type = 0
                continue

        # Regular string
        if c == 34 or c == 39:
            # CHUNK-SAFETY: the opening '"""' may straddle the chunk end.
            # Only consume 3 quote bytes when ALL of them are inside THIS
            # chunk; otherwise fall through to single-line-string handling
            # (the next chunk's state scan sees the full triple and styles
            # the remaining quotes correctly).
            if i + 2 < end and text[i+1] == c and text[i+2] == c:
                if expect_docstring:
                    string_style = STYLE_DOCSTRING
                    is_docstring = 1
                else:
                    string_style = STYLE_STRING
                results.append((3, string_style))
                i += 3
                in_string = 1
                triple_string = 1
                string_delim = c
                in_fstring = 0
            else:
                results.append((1, STYLE_STRING))
                i += 1
                in_string = 1
                triple_string = 0
                string_delim = c
                in_fstring = 0
            expect_docstring = 0
            prev_id_type = 0
            continue

        # Comment
        if c == 35:
            in_comment = 1
            token_start = i
            i += 1
            while i < end and text[i] != 10 and text[i] != 13:
                i += 1
            results.append((i - token_start, STYLE_COMMENTS))
            prev_id_type = 0
            continue

        # Decorator
        if c == 64:
            results.append((1, STYLE_DECORATOR))
            i += 1
            after_at = 1
            expect_docstring = 0
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Number
        if is_digit(c):
            token_start = i
            while i < end and (is_alnum(text[i]) or text[i] == 46):
                i += 1
            results.append((i - token_start, STYLE_NUMBERS))
            expect_docstring = 0
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Dot
        if c == 46:
            results.append((1, STYLE_DEFAULT))
            i += 1
            if after_from or after_import:
                pass
            else:
                after_dot = 1
                dot_owner_type = prev_id_type
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Brackets
        if is_bracket(c):
            results.append((1, STYLE_BRACKETS))
            if c == 40 or c == 91 or c == 123:
                bracket_depth += 1
                if c == 40 and after_def:
                    in_def_params = 1
                    param_depth = 1
                    after_def = 0
                    at_type_pos = 0
                elif in_def_params:
                    param_depth += 1
                at_arg_pos = True
            elif c == 41 or c == 93 or c == 125:
                if bracket_depth > 0:
                    bracket_depth -= 1
                if in_def_params:
                    param_depth -= 1
                    if param_depth <= 0:
                        in_def_params = 0
                        param_depth = 0
                        at_type_pos = 0
                at_arg_pos = False
            i += 1
            after_dot = 0
            prev_id_type = 0
            continue

        # Operators
        if is_operator(c):
            token_start = i
            i += 1
            if i < end and is_operator(text[i]):
                i += 1
            results.append((i - token_start, STYLE_OPERATORS))
            expect_docstring = 0
            if text[token_start] == 45 and (token_start + 1 < end) and text[token_start+1] == 62:
                if pending_def and bracket_depth == 0:
                    after_arrow = 1
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Comma
        if c == 44:
            results.append((1, STYLE_COMMA))
            i += 1
            if in_def_params:
                at_type_pos = 0
            if not after_import and not in_from_import and not after_from:
                prev_id_type = 0
            at_arg_pos = True
            continue

        # Colon
        if c == 58:
            results.append((1, STYLE_DEFAULT))
            if in_def_params and param_depth == 1:
                at_type_pos = 1
            elif bracket_depth == 0 and (pending_def or pending_class):
                expect_docstring = 1
                if pending_class:
                    at_class_body = 1
                pending_def = 0
                pending_class = 0
                after_arrow = 0
            i += 1
            prev_id_type = 0
            at_arg_pos = False
            continue

        # Semicolon
        if c == 59:
            results.append((1, STYLE_DEFAULT))
            i += 1
            expect_docstring = 0
            after_from = 0
            after_import = 0
            in_from_import = 0
            prev_id_type = 0
            at_arg_pos = False
            continue

        # ============ IDENTIFIER (word) ============
        if is_alpha(c):
            token_start = i
            while i < end and is_alnum(text[i]):
                i += 1

            token_bytes = text[token_start:i]
            token_str = token_bytes.decode('utf-8', errors='replace')

            followed_by_paren = (i < end and text[i] == 40)
            followed_by_eq = (i < end and text[i] == 61 and
                              (i + 1 >= end or text[i+1] != 61))
            _j = i
            while _j < end and (text[_j] == 32 or text[_j] == 9):
                _j += 1
            followed_by_assign = (_j < end and text[_j] == 61 and
                                  (_j + 1 >= end or text[_j+1] != 61))

            if not (token_str == "def" or token_str == "class"):
                expect_docstring = 0

            # --- Style decision tree (mirrors PyCharm's Python semantics) ---
            if after_at:
                results.append((i - token_start, STYLE_DECORATOR))
                after_at = 0
                prev_id_type = 0

            elif token_str in ("self", "cls"):
                results.append((i - token_start, STYLE_SELF_CLS))
                prev_id_type = 1

            elif token_str in ("True", "False", "None"):
                results.append((i - token_start, STYLE_CONSTANTS))
                prev_id_type = 0

            elif token_str == "def":
                results.append((i - token_start, STYLE_KEYWORD))
                after_def = 1
                pending_def = 1
                pending_class = 0
                at_class_body = 0
                prev_id_type = 0

            elif token_str == "class":
                results.append((i - token_start, STYLE_KEYWORD))
                after_class = 1
                pending_class = 1
                pending_def = 0
                prev_id_type = 0

            elif token_str == "import":
                results.append((i - token_start, STYLE_KEYWORD))
                if after_from:
                    after_from = 0
                    in_from_import = 1
                else:
                    after_import = 1
                prev_id_type = 0

            elif token_str == "from":
                results.append((i - token_start, STYLE_KEYWORD))
                after_from = 1
                prev_id_type = 0

            elif token_str == "as":
                results.append((i - token_start, STYLE_KEYWORD))
                after_import = 0
                in_from_import = 0
                prev_id_type = 0

            elif token_str in keywords:
                results.append((i - token_start, STYLE_KEYWORD))
                prev_id_type = 0

            elif after_def:
                # Method/function declaration name. Magic methods (dunders)
                # get their own magenta color in PyCharm.
                if token_str in magic_methods:
                    results.append((i - token_start, STYLE_MAGIC_METHODS))
                else:
                    results.append((i - token_start, STYLE_FUNCTION_DEF))
                prev_id_type = 3

            elif after_class:
                results.append((i - token_start, STYLE_CLASSES))
                after_class = 0
                prev_id_type = 2

            elif after_dot:
                # Anything CALLED after a dot is violet (method call),
                # anything merely referenced is grey (field).
                if followed_by_paren:
                    results.append((i - token_start, STYLE_INSTANCE_METHOD))
                else:
                    results.append((i - token_start, STYLE_INSTANCE_FIELD))
                after_dot = 0
                dot_owner_type = 0
                prev_id_type = 3

            elif in_def_params and param_depth == 1:
                if at_type_pos:
                    results.append((i - token_start, STYLE_TYPES))
                else:
                    results.append((i - token_start, STYLE_PARAMETERS))
                prev_id_type = 3

            elif after_arrow:
                results.append((i - token_start, STYLE_TYPES))
                prev_id_type = 2

            elif after_from:
                results.append((i - token_start, STYLE_MODULE_NAME))
                prev_id_type = 0

            elif after_import:
                results.append((i - token_start, STYLE_MODULE_NAME))
                prev_id_type = 0

            elif in_from_import:
                if len(token_str) > 0 and token_str[0].isupper():
                    results.append((i - token_start, STYLE_CLASS_REFERENCE))
                    prev_id_type = 2
                else:
                    results.append((i - token_start, STYLE_MODULE_NAME))
                    prev_id_type = 0

            elif (at_arg_pos and followed_by_eq and not in_def_params):
                results.append((i - token_start, STYLE_KEYARGS))
                prev_id_type = 3

            elif at_class_body and followed_by_assign:
                # class-body attribute assignment target -> grey (like PyCharm)
                results.append((i - token_start, STYLE_INSTANCE_FIELD))
                prev_id_type = 3

            elif token_str in builtins:
                # Builtins (super, print, str, os, ...) are grey in PyCharm,
                # even when called.
                results.append((i - token_start, STYLE_BUILTINS))
                prev_id_type = 3

            elif followed_by_paren:
                # A called identifier: function call / constructor call (violet).
                # Checked BEFORE the uppercase class-reference branch so that
                # QFont() / QLabel() render as calls, like in PyCharm.
                results.append((i - token_start, STYLE_FUNCTION_CALL))
                prev_id_type = 3

            elif (token_str.startswith("__") and token_str.endswith("__")
                    and len(token_str) > 4):
                # Dunder references (e.g. __file__, __name__) -> grey
                results.append((i - token_start, STYLE_BUILTINS))
                prev_id_type = 3

            elif len(token_str) > 0 and token_str[0].isupper():
                # Class reference at usage site -> grey (only the definition
                # site is colored soft red)
                results.append((i - token_start, STYLE_CLASS_REFERENCE))
                prev_id_type = 2

            else:
                results.append((i - token_start, STYLE_LOCAL_VARIABLE))
                prev_id_type = 3

            at_arg_pos = False
            continue

        # Unknown character
        results.append((1, STYLE_DEFAULT))
        i += 1
        prev_id_type = 0
        at_arg_pos = False

    cdef int final_state = pack_state(in_string, in_comment, triple_string,
                             string_delim, in_fstring, escape_next,
                             in_fexpr, fexpr_depth, is_docstring,
                             expect_docstring, at_class_body)
    return (final_state, results)
```


**Implementation:** replace this function from its `def style_chunk(` line through the end of its body. Keep the preceding Cython helpers and style enum. Rebuild only after both functions have been changed.


### 1.3. `markdown_editor/markdowncustomlexer.py`


#### 1.3.1 Existing method/function `MarkdownCustomLexer.__init__`

The widget reference is stored in `_editor` so the inherited `QsciLexerCustom.editor()` method remains callable. The Python and Markdown lexers must use the same renamed reference.


**Old version — original lines 9–26:**


```python
    def __init__(self, editor, theme=None, paper=None):
        """
        :param theme: absolute path to a theme .json; None -> default
        :param paper: QColor paper override from the Settings color picker;
                      None -> the theme's editor.paper-color
        """
        super(MarkdownCustomLexer, self).__init__("Markdown", editor,
                                                  theme=theme, paper=paper)

        # Fallback colors ONLY for themes without an editor section —
        # _init_theme's theme-driven styles win; these just guarantee
        # unstyled regions never flash white when a legacy theme is loaded.
        if not self.theme_json.get("theme", {}).get("editor"):
            self.setDefaultColor(QColor("#abb2bf"))
            self.setDefaultPaper(QColor("#1e1f22"))

        self.editor.setColor(self.defaultColor())
        self.editor.setPaper(self.defaultPaper())
```


**New version:**


```python
    def __init__(self, editor, theme=None, paper=None):
        """
        :param theme: absolute path to a theme .json; None -> default
        :param paper: QColor paper override from the Settings color picker;
                      None -> the theme's editor.paper-color
        """
        super(MarkdownCustomLexer, self).__init__("Markdown", editor,
                                                  theme=theme, paper=paper)

        # Fallback colors ONLY for themes without an editor section —
        # _init_theme's theme-driven styles win; these just guarantee
        # unstyled regions never flash white when a legacy theme is loaded.
        if not self.theme_json.get("theme", {}).get("editor"):
            self.setDefaultColor(QColor("#abb2bf"))
            self.setDefaultPaper(QColor("#1e1f22"))

        self._editor.setColor(self.defaultColor())
        self._editor.setPaper(self.defaultPaper())
```


**Implementation:** inside `markdown_editor/markdowncustomlexer.py`, replace only `MarkdownCustomLexer.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 1.3.2 Existing method/function `MarkdownCustomLexer._init_theme_vars`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 31–127:**


```python
    def _init_theme_vars(self):
        self.DEFAULT = 0

        self.HEADER = 1
        self.SETEXT_HEADER = 2
        self.HRULE = 3
        self.BLOCKQUOTE = 4
        self.LIST_MARKER = 5
        self.ORDERED_LIST_MARKER = 6
        self.TASK_MARKER = 7

        self.BOLD = 8
        self.ITALIC = 9
        self.BOLD_ITALIC = 10
        self.STRIKETHROUGH = 11

        self.INLINE_CODE = 12
        self.CODE_FENCE = 13
        self.CODE_BLOCK = 14
        self.CODE_LANGUAGE = 15

        self.LINK_TEXT = 16
        self.LINK_URL = 17
        self.LINK_TITLE = 18
        self.REFERENCE_ID = 19
        self.LINK_DEFINITION = 20
        self.AUTOLINK = 21
        self.IMAGE_MARKER = 22

        self.TABLE_PIPE = 23
        self.TABLE_SEPARATOR = 24
        self.TABLE_TEXT = 25

        self.HTML = 26
        self.ESCAPE = 27
        self.ENTITY = 28

        self.FOOTNOTE_MARKER = 29
        self.FOOTNOTE_TEXT = 30

        self.ALERT = 31
        self.MENTION = 32
        self.ISSUE_REF = 33
        self.EMOJI = 34

        self.COMMENTS = 35  # HTML comments <!-- ... -->

        self.default_names = [
            "default",
            "header",
            "setext_header",
            "hrule",
            "blockquote",
            "list_marker",
            "ordered_list_marker",
            "task_marker",
            "bold",
            "italic",
            "bold_italic",
            "strikethrough",
            "inline_code",
            "code_fence",
            "code_block",
            "code_language",
            "link_text",
            "link_url",
            "link_title",
            "reference_id",
            "link_definition",
            "autolink",
            "image_marker",
            "table_pipe",
            "table_separator",
            "table_text",
            "html",
            "escape",
            "entity",
            "footnote_marker",
            "footnote_text",
            "alert",
            "mention",
            "issue_ref",
            "emoji",
            "comments",
        ]

        self.font_weights = {
            "thin": QFont.Thin,
            "extralight": QFont.ExtraLight,
            "light": QFont.Light,
            "normal": QFont.Normal,
            "medium": QFont.Medium,
            "demibold": QFont.DemiBold,
            "bold": QFont.Bold,
            "extrabold": QFont.ExtraBold,
            "black": QFont.Black,
        }
```


**New version:**


```python
    def _init_theme_vars(self):
        """Initialize style identifiers, theme colors and per-style font settings.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self.DEFAULT = 0

        self.HEADER = 1
        self.SETEXT_HEADER = 2
        self.HRULE = 3
        self.BLOCKQUOTE = 4
        self.LIST_MARKER = 5
        self.ORDERED_LIST_MARKER = 6
        self.TASK_MARKER = 7

        self.BOLD = 8
        self.ITALIC = 9
        self.BOLD_ITALIC = 10
        self.STRIKETHROUGH = 11

        self.INLINE_CODE = 12
        self.CODE_FENCE = 13
        self.CODE_BLOCK = 14
        self.CODE_LANGUAGE = 15

        self.LINK_TEXT = 16
        self.LINK_URL = 17
        self.LINK_TITLE = 18
        self.REFERENCE_ID = 19
        self.LINK_DEFINITION = 20
        self.AUTOLINK = 21
        self.IMAGE_MARKER = 22

        self.TABLE_PIPE = 23
        self.TABLE_SEPARATOR = 24
        self.TABLE_TEXT = 25

        self.HTML = 26
        self.ESCAPE = 27
        self.ENTITY = 28

        self.FOOTNOTE_MARKER = 29
        self.FOOTNOTE_TEXT = 30

        self.ALERT = 31
        self.MENTION = 32
        self.ISSUE_REF = 33
        self.EMOJI = 34

        self.COMMENTS = 35  # HTML comments <!-- ... -->

        self.default_names = [
            "default",
            "header",
            "setext_header",
            "hrule",
            "blockquote",
            "list_marker",
            "ordered_list_marker",
            "task_marker",
            "bold",
            "italic",
            "bold_italic",
            "strikethrough",
            "inline_code",
            "code_fence",
            "code_block",
            "code_language",
            "link_text",
            "link_url",
            "link_title",
            "reference_id",
            "link_definition",
            "autolink",
            "image_marker",
            "table_pipe",
            "table_separator",
            "table_text",
            "html",
            "escape",
            "entity",
            "footnote_marker",
            "footnote_text",
            "alert",
            "mention",
            "issue_ref",
            "emoji",
            "comments",
        ]

        self.font_weights = {
            "thin": QFont.Weight.Thin,
            "extralight": QFont.Weight.ExtraLight,
            "light": QFont.Weight.Light,
            "normal": QFont.Weight.Normal,
            "medium": QFont.Weight.Medium,
            "demibold": QFont.Weight.DemiBold,
            "bold": QFont.Weight.Bold,
            "extrabold": QFont.Weight.ExtraBold,
            "black": QFont.Weight.Black,
        }
```


**Implementation:** inside `markdown_editor/markdowncustomlexer.py`, replace only `MarkdownCustomLexer._init_theme_vars`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 1.3.3 Existing method/function `MarkdownCustomLexer.styleText`

The widget reference is stored in `_editor` so the inherited `QsciLexerCustom.editor()` method remains callable. The Python and Markdown lexers must use the same renamed reference.


**Old version — original lines 340–359:**


```python
    def styleText(self, start: int, end: int) -> None:
        full_text = self.editor.text()
        start_char = self._byte_pos_to_char_index(full_text, start)
        end_char = self._byte_pos_to_char_index(full_text, end)
        in_fence, fence_char, fence_len, in_comment = self._state_before(full_text, start_char)
        partial_first = start_char > 0 and full_text[start_char - 1] != "\n"

        self.startStyling(start)
        lines = full_text[start_char:end_char].split("\n")
        for index, line in enumerate(lines):
            in_fence, fence_char, fence_len, in_comment = self._style_line_with_comments(
                line,
                in_fence,
                fence_char,
                fence_len,
                in_comment,
                force_inline=partial_first and index == 0,
            )
            if index != len(lines) - 1:
                self.setStyling(1, self.DEFAULT)
```


**New version:**


```python
    def styleText(self, start: int, end: int) -> None:
        """Apply Markdown token styles to the requested Scintilla byte range.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        full_text = self._editor.text()
        start_char = self._byte_pos_to_char_index(full_text, start)
        end_char = self._byte_pos_to_char_index(full_text, end)
        in_fence, fence_char, fence_len, in_comment = self._state_before(full_text, start_char)
        partial_first = start_char > 0 and full_text[start_char - 1] != "\n"

        self.startStyling(start)
        lines = full_text[start_char:end_char].split("\n")
        for index, line in enumerate(lines):
            in_fence, fence_char, fence_len, in_comment = self._style_line_with_comments(
                line,
                in_fence,
                fence_char,
                fence_len,
                in_comment,
                force_inline=partial_first and index == 0,
            )
            if index != len(lines) - 1:
                self.setStyling(1, self.DEFAULT)
```


**Implementation:** inside `markdown_editor/markdowncustomlexer.py`, replace only `MarkdownCustomLexer.styleText`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### Implement and check Topic 1


No new folder is needed. Change the three files above together. No existing source file is deleted. From the repository root, rebuild the extension using the same interpreter that launches the editor:


```powershell
python python_editor/setup.py build_ext --inplace
python -c "import lexer_fast; print(lexer_fast.__file__)"
python main.py
```


A Windows native build requires a working C compiler compatible with that Python installation. The build replaces its generated extension; do not edit generated `lexer_fast.c` by hand. If compilation is unavailable, disable the existing `lexer_fast` native extension you actually import and let the tested Python fallback run. Identify its exact location with the import command first; do not delete unrelated `.pyd` files. Restart the process after rebuilding.


Open `ruff_implementation/spelling_diagnostics.py`, move/edit above the decorator and scroll away/back. `@dataclass` must receive decorator style rather than string style. Triple double quotes inside a triple-single-quoted literal (and the converse) must remain string contents. This addresses the demonstrated delimiter bug; it is not a complete new Python parser.


## Topic 2 — Make Qt usage accurately describable by basedpyright


### Explanation and documentation


The error flood has several causes. The recommended profile reports extensive annotation-quality findings; those are not necessarily runtime failures. Separately, PyQt5’s bundled stubs use scoped enums and optional object returns. Your source also assigns `self.model` in a QTreeView subclass, hiding its inherited method. These require different fixes.


`require_qt` checks a result that this particular call site requires. It must not be used for an API where absence is normal. `qt_flags` constructs a concrete Qt flags object and isolates a generated-stub constructor gap. Scoped enum names refer to the same runtime values. `ClickableLabel` declares a signal instead of replacing an existing Qt method at runtime. The standard checking profile keeps undefined variables, missing attributes and unsafe optional access enabled.


Documentation: [basedpyright configuration and diagnostic profiles](https://docs.basedpyright.com/latest/configuration/config-files/), [QMenu action/menu creation](https://doc.qt.io/archives/qt-5.15/qmenu.html), [QMainWindow status bar](https://doc.qt.io/archives/qt-5.15/qmainwindow.html#statusBar), [QAbstractItemView model](https://doc.qt.io/archives/qt-5.15/qabstractitemview.html#model), [Python typing](https://docs.python.org/3/library/typing.html). The enum and overload corrections were also checked against the installed PyQt5 5.15.11 `.pyi` declarations and real widgets.


### 2.1. `code_inteligence/qt_helpers.py`


**New file.** Use the existing `code_inteligence/` folder. Create `qt_helpers.py` with the following complete contents. No existing file is replaced.


```python
"""Runtime-checked narrowing for Qt APIs whose bundled stubs allow None."""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def require_qt(value: T | None) -> T:
    """Return a Qt object required by the caller, or expose its failed creation.

    Args:
        value: Result of an API which this call site requires to return an object,
            such as QMenu.addAction(text) or QMainWindow.statusBar().

    Returns:
        The same object with its optional type narrowed for static analysis.

    Raises:
        RuntimeError: The required object is absent. Call sites where absence is
            normal must use an explicit guard instead of this helper.

    Unlike a cast or a disabled diagnostic rule, this check also validates the
    assumption at runtime. It does not construct, replace, or take ownership of
    the Qt object and does not change its signal connections.
    """
    if value is None:
        raise RuntimeError("A required Qt object was not created")
    return value


def qt_flags(flag_type: Callable[[Any], T], *values: int) -> T:
    """Construct a Qt flag wrapper from its integer-compatible enum members.

    Args:
        flag_type: Qt's concrete flags constructor, such as ``Qt.WindowFlags``.
        values: Members to combine with bitwise OR. Zero values produce an
            empty set of flags.

    Returns:
        An instance of ``flag_type`` suitable for the corresponding Qt setter.

    PyQt5 accepts an integer mask at runtime, but its generated constructor
    stubs omit that overload. Keep that binding boundary in one helper rather
    than disabling argument checks throughout the editor.
    """
    mask = 0
    for value in values:
        mask |= int(value)  # Preserve every selected bit, including zero flags.
    return flag_type(mask)
```


**Implementation:** save this file before editing its import sites below. Its classes/functions document their arguments, behavior and failure handling in their docstrings.


### 2.2. `code_inteligence/clickable_label.py`


**New file.** Use the existing `code_inteligence/` folder. Create `clickable_label.py` with the following complete contents. No existing file is replaced.


```python
"""A sidebar label with a declared click signal instead of a replaced method."""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QLabel


class ClickableLabel(QLabel):
    """Emit a mouse press for the sidebar's existing show/hide dispatcher.

    The inherited constructor and visual behavior remain those of QLabel.
    ``pressed`` carries the original event synchronously on the GUI thread;
    receivers must use it immediately rather than retaining the Qt event.
    """

    pressed = pyqtSignal(object)

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        """Forward a real press without assigning over a bound Qt method.

        Args:
            a0: Mouse event delivered by Qt. Its name and optional annotation
                match PyQt5's generated QLabel declaration. A missing event is
                ignored; Qt normally supplies a real QMouseEvent.

        This preserves the old sidebar callback's handling of every mouse
        button. The receiver decides which button should toggle its panel.
        """
        if a0 is not None:
            self.pressed.emit(a0)  # Same-thread delivery keeps the event valid.
```


**Implementation:** save this file before editing its import sites below. Its classes/functions document their arguments, behavior and failure handling in their docstrings.


### 2.3. `pyproject.toml`


**Change the existing `[tool.basedpyright]` section at the end of this file.** Ruff settings and project dependencies stay as they are.

**Old section:**


```toml
[tool.basedpyright]
# Broad checks, including warnings when types are too weak for reliable analysis.
typeCheckingMode = "recommended"

# These findings represent the unresolved/unsafe code cases requested here.
reportUndefinedVariable = "error"
reportAttributeAccessIssue = "error"
reportOptionalMemberAccess = "error"

# Generate code and environments are not editor application source.
```


**New section:**


```toml
[tool.basedpyright]
# Check everyday semantic errors without recommended-mode annotation warnings.
typeCheckingMode = "standard"

# These findings represent the unresolved/unsafe code cases requested here.
reportUndefinedVariable = "error"
reportAttributeAccessIssue = "error"
reportOptionalMemberAccess = "error"

# Generated code and environments are not editor application source.

exclude = ["resources_rc.py", "build", "dist", ".venv", "venv", "__pycache__"]
```


**Implementation:** replace only that section. `standard` reduces annotation-completeness policy noise. The three explicitly enabled semantic error rules remain active. Generated code/build outputs are excluded from direct project scanning; imported excluded modules can still be analyzed. No Qt stub package is added.


### 2.4. `main.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `import resources_rc  # noqa: F401 - register resources generated from icons/resources.qrc` (original line 26).


```python
from code_inteligence.clickable_label import ClickableLabel
```


**Implementation:** insert once at module/class indentation exactly as shown.


**Import/declaration addition 2:** insert immediately after `from side_bar_widgets.problems_panel import ProblemsPanel` (original line 55).


```python

from code_inteligence.qt_helpers import require_qt, qt_flags
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 2.4.1 Existing method/function `_excepthook`

Display an uncaught exception through the application error dialog. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 136–150:**


```python
def _excepthook(exc_type, exc, tb):
    try:
        log_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "crash_log.txt"
        if log_path.exists() and log_path.stat().st_size > 1024 * 1024:
            rotated = log_dir / "crash_log.1.txt"
            rotated.unlink(missing_ok=True)
            log_path.replace(rotated)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}]\n")
            traceback.print_exception(exc_type, exc, tb, file=f)
    except OSError:
        pass
    traceback.print_exception(exc_type, exc, tb)  # also as stderr
```


**New version:**


```python
def _excepthook(exc_type, exc, tb):
    """Display an uncaught exception through the application error dialog.

    Use the declared Qt enum scope and checked required objects so the
    installed PyQt5 stubs can describe the same values used at runtime.
    """
    try:
        log_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "crash_log.txt"
        if log_path.exists() and log_path.stat().st_size > 1024 * 1024:
            rotated = log_dir / "crash_log.1.txt"
            rotated.unlink(missing_ok=True)
            log_path.replace(rotated)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}]\n")
            traceback.print_exception(exc_type, exc, tb, file=f)
    except OSError:
        pass
    traceback.print_exception(exc_type, exc, tb)  # also as stderr
```


**Implementation:** inside `main.py`, replace only `_excepthook`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.2 Existing method/function `MainWindow.__init__`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 187–279:**


```python
    def __init__(self):
        super().__init__()
        self.update_check_finished.connect(self._show_update_check_result)
        self._dirty_editors = set()
        self.python_runner = PythonRunner(self)
        self.settings = QSettings("CodeEditor", "CodeEditor")
        self._hacker = self.settings.value("theme", "theme.json", type=str) == "hacker.json"
        self._pre_hacker_theme = "theme.json"
        # Load the saved recent files list, default to empty list
        self.recent_files = self.settings.value("recent_files", [], type=list)
        self.ruff_save_mode = self.settings.value("ruff_save_mode", "safe_format", type=str)
        self.update_available.connect(self._show_update_dialog)
        # retirement statement of all the Python workers
        self._retired_editors = set()
        # Detect if running as a bundled exe
        if hasattr(sys, "_MEIPASS"):
            # Running as PyInstaller exe — sys.executable is the editor itself.
            # Try to find a real Python installation on the system.
            import shutil
            found_python = shutil.which("python") or shutil.which("python3")
            if found_python:
                self.python_runner.set_interpreter(found_python)
            else:
                # No Python found — load from settings or let user pick
                saved = self._load_interpreter()
                if saved != sys.executable:
                    self.python_runner.set_interpreter(saved)
                else:
                    # Prompt user to select a Python interpreter
                    QMessageBox.warning(
                        self,
                        "Python Interpreter Required",
                        "No Python installation found.\n"
                        "Please select your Python interpreter (python.exe).",
                    )
                    self.choose_interpreter()
        else:
            # Running from source — sys.executable is the real Python
            self.python_runner.set_interpreter(self._load_interpreter())
        # The initial file-manager root is cwd for source/wheel launches and
        # home for the bundled executable. Ruff must use the same project view.
        initial_folder = Path.home() if hasattr(sys, "_MEIPASS") else Path.cwd()
        self._workspace_root = self._discover_workspace_root(initial_folder)
        self.ruff_lsp_client = RuffLspClient(
            python_executable=self.python_runner.interpreter,
            workspace_root=self._workspace_root,
            parent=self,
        )
        self.ruff_lsp_client.server_error.connect(self._on_ruff_lsp_error)
        self.ruff_lsp_client.start()

        self.console = None  # will be created in set_up_console_dock
        self.terminal = None

        self.python_editor_active = False
        self.current_file = None
        self.md = markdown.Markdown(
            extensions=[
                "extra",
                "codehilite",
                "toc",
                "sane_lists",
                "nl2br",
                "admonition",
                "smarty",
                "meta",
            ]
        )
        self._preview_css = """
           body { font-family: sans-serif; max-width: 800px; margin: 2em auto 0;
                  padding: 0 1em 4em; background:#1e1f22; color:#dcdfe4; }
           h1,h2 { border-bottom:1px solid #444; padding-bottom:.3em; }
           code { background:#1e1f22; padding:2px 5px; border-radius:3px; }
           pre { background:#1e1f22; padding:1em; border-radius:6px; overflow-x:auto; }
           """

        self.init_ui()
        self._install_command_palette()
        self._install_problems()
        self._install_type_diagnostics()

        if hasattr(sys, "_MEIPASS"):
            # We're running as a bundled exe
            import os
            home = os.path.expanduser("~")
            self.file_manager.model.setRootPath(home)
            self.file_manager.setRootIndex(self.file_manager.model.index(home))
        # Reopen the tabs from the previous sessions (no-op when
        # the feature is disabled or nothing was saved)
        self._apply_settings(self._load_settings())
        if self._hacker:
            self._set_scanlines_visible(True)
        self._restore_session()
```


**New version:**


```python
    def __init__(self):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__()
        self.update_check_finished.connect(self._show_update_check_result)
        self._dirty_editors = set()
        self.python_runner = PythonRunner(self)
        self.settings = QSettings("CodeEditor", "CodeEditor")
        self._hacker = self.settings.value("theme", "theme.json", type=str) == "hacker.json"
        self._pre_hacker_theme = "theme.json"
        # Load the saved recent files list, default to empty list
        self.recent_files = self.settings.value("recent_files", [], type=list)
        self.ruff_save_mode = self.settings.value("ruff_save_mode", "safe_format", type=str)
        self.update_available.connect(self._show_update_dialog)
        # retirement statement of all the Python workers
        self._retired_editors = set()
        # Detect if running as a bundled exe
        if hasattr(sys, "_MEIPASS"):
            # Running as PyInstaller exe — sys.executable is the editor itself.
            # Try to find a real Python installation on the system.
            import shutil
            found_python = shutil.which("python") or shutil.which("python3")
            if found_python:
                self.python_runner.set_interpreter(found_python)
            else:
                # No Python found — load from settings or let user pick
                saved = self._load_interpreter()
                if saved != sys.executable:
                    self.python_runner.set_interpreter(saved)
                else:
                    # Prompt user to select a Python interpreter
                    QMessageBox.warning(
                        self,
                        "Python Interpreter Required",
                        "No Python installation found.\n"
                        "Please select your Python interpreter (python.exe).",
                    )
                    self.choose_interpreter()
        else:
            # Running from source — sys.executable is the real Python
            self.python_runner.set_interpreter(self._load_interpreter())
        # The initial file-manager root is cwd for source/wheel launches and
        # home for the bundled executable. Ruff must use the same project view.
        initial_folder = Path.home() if hasattr(sys, "_MEIPASS") else Path.cwd()
        self._workspace_root = self._discover_workspace_root(initial_folder)
        self.ruff_lsp_client = RuffLspClient(
            python_executable=self.python_runner.interpreter,
            workspace_root=self._workspace_root,
            parent=self,
        )
        self.ruff_lsp_client.server_error.connect(self._on_ruff_lsp_error)
        self.ruff_lsp_client.start()

        self.console = None  # will be created in set_up_console_dock
        self.terminal = None

        self.python_editor_active = False
        self.current_file = None
        self.md = markdown.Markdown(
            extensions=[
                "extra",
                "codehilite",
                "toc",
                "sane_lists",
                "nl2br",
                "admonition",
                "smarty",
                "meta",
            ]
        )
        self._preview_css = """
           body { font-family: sans-serif; max-width: 800px; margin: 2em auto 0;
                  padding: 0 1em 4em; background:#1e1f22; color:#dcdfe4; }
           h1,h2 { border-bottom:1px solid #444; padding-bottom:.3em; }
           code { background:#1e1f22; padding:2px 5px; border-radius:3px; }
           pre { background:#1e1f22; padding:1em; border-radius:6px; overflow-x:auto; }
           """

        self.init_ui()
        self._install_command_palette()
        self._install_problems()
        self._install_type_diagnostics()

        if hasattr(sys, "_MEIPASS"):
            # We're running as a bundled exe
            import os
            home = os.path.expanduser("~")
            self.file_manager.fs_model.setRootPath(home)
            self.file_manager.setRootIndex(self.file_manager.fs_model.index(home))
        # Reopen the tabs from the previous sessions (no-op when
        # the feature is disabled or nothing was saved)
        self._apply_settings(self._load_settings())
        if self._hacker:
            self._set_scanlines_visible(True)
        self._restore_session()
```


**Implementation:** inside `main.py`, replace only `MainWindow.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.3 Existing method/function `MainWindow.init_ui`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 281–418:**


```python
    def init_ui(self):
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(100)
        self._debounce.timeout.connect(self.render_preview)
        self.setWindowTitle("Code Editor")
        self.setWindowIcon(QIcon(resource_path("icons/app-icon-256.png")))
        self.resize(self.WIDTH, self.HEIGHT)
        self.window_font = QFont("sans-serif")
        self.window_font.setPointSize(13)
        self.setFont(self.window_font)
        qss_path = resource_path("css/style.qss")
        print(f"QSS path: {qss_path}")
        print(f"QSS exists: {os.path.exists(qss_path)}")
        try:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError as e:
            print(f"STYLESHEET ERROR: {e}")
            # Fallback: apply basic dark styling inline
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1f22; color: #d3d3d3; }
                QMenuBar { background-color: #2d2d2d; color: floralwhite; }
                QTabWidget { background-color: #1e1f22; color: #d3d3d3; }
            """)

        self._outline_debounce = QTimer(self)
        self._outline_debounce.setSingleShot(True)
        self._outline_debounce.setInterval(500)

        # BUGFIX: was connected to its own start() -> restarted itself forever
        self._outline_debounce.timeout.connect(self._update_outline)
        self.set_up_menu()
        self.set_up_body()
        self._git_refresh_timer = QTimer(self)
        self._git_refresh_timer.setInterval(15000)
        self._git_refresh_timer.timeout.connect(self._refresh_git_state)
        self._git_refresh_timer.start()
        # Find/Replace bar. Hidden by default
        self.find_bar = FindReplaceBar(show_replace=False, parent=self)
        self.find_bar.hide()
        # Connect the find bar's signals to our search methods
        self.find_bar.find_next_requested.connect(self._do_find_next)
        self.find_bar.find_prev_requested.connect(self._do_find_prev)
        self.find_bar.replace_requested.connect(self._do_replace)
        self.find_bar.replace_all_requested.connect(self._do_replace_all)
        self.set_up_console_dock()

        self._preview_ready = False
        self.preview.loadFinished.connect(self._on_preview_loaded)
        base = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{self._preview_css}</style></head><body><div id="content"></div></body></html>"""
        self.preview.setHtml(base)
        self.statusBar().setFont(self.window_font)
        self.statusBar().setStyleSheet("""
                color: #CCCCCC;
        """)

        self.statusBar().showMessage(f"Interpreter: {self.python_runner.interpreter}")
        self.cursor_pos_label = QLabel("Ln 1, Col 1")
        self.cursor_pos_label.setStyleSheet("color: #888; padding: 0 10px;")
        self.statusBar().addPermanentWidget(self.cursor_pos_label)

        # --- Cozy Mode: the status bar cat ---------------------------------------------------------- #

        self.cat = CatController(self)
        self.statusBar().addPermanentWidget(self.cat)
        from cozy.neko import NekoChaser
        self.neko = NekoChaser(self)
        self.neko.start()

        # C2: level-ups plat rhe Dance frames and announce themselves

        self.cat.level_up.connect(
            lambda lvl, title: self.statusBar().showMessage(
                f"Cat leveled up: {title} (level {lvl})", 3000
            )
        )

        # C1: pet milestones (achievement logic lives in the handler, NOT in the lambda
        # keep lambdas dump, they cannot be extended
        self.cat.petted.connect(self._on_cat_petted)

        from cozy.power_mode import PowerModeController

        # Honor the saved Power Mode states from the View menu dropdown.

        self.power = PowerModeController(
            self,
            enabled=self.power_mode_action.isChecked(),
            shake_intensity=1,
            particles_on=self.power_particles_action.isChecked(),
            shake_on=self.power_shake_action.isChecked(),
            glow_enabled=self.power_glow_action.isChecked(),
        )
        self.python_runner.process_started.connect(self._on_run_started)
        self.python_runner.process_finished.connect(self._on_run_finished)

        # Word count label - shows "Words: X | Chars: Y"

        self.word_count_label = QLabel("Words: 0 | Chars: 0")
        self.word_count_label.setStyleSheet("color: #888; padding: 0 10px;")
        self.statusBar().addPermanentWidget(self.word_count_label)
        self.show()

        QTimer.singleShot(2000, lambda: self.check_for_updates(manual=False))
        # --- idle choreography: sleepy -> box -> sleep ------------------ #
        # Escalation ladder: 60 s idle = yawn; 3 min = deep sleep; 10 min =
        # the cat moves into a box (and pops back out when you return).
        # Timers re-arm on activity via _connect_editor's textChanged below.
        self._cat_sleepy_timer = QTimer(self)
        self._cat_sleepy_timer.setSingleShot(True)
        self._cat_sleepy_timer.timeout.connect(lambda: self.cat.set_state("sleepy", 120000))
        self._cat_sleep_timer = QTimer(self)
        self._cat_sleep_timer.setSingleShot(True)
        self._cat_sleep_timer.timeout.connect(lambda: self.cat.set_state("sleep", 300000))
        self._cat_box_timer = QTimer(self)
        self._cat_box_timer.setSingleShot(True)
        self._cat_box_timer.timeout.connect(self._cat_moves_into_box)
        self._arm_cat_timers()

        # Git Integration
        self.git_service = GitService(self)
        self.git_branch_label = QLabel("No Git repository", self)
        self.statusBar().addPermanentWidget(self.git_branch_label)
        self.git_graph = CommitGraphPanel(self)
        self.git_graph_dock = QDockWidget("Git History", self)
        self.git_graph_dock.setObjectName("GitHistoryDock")
        self.git_graph_dock.setWidget(self.git_graph)
        self._apply_git_history_theme(self._active_theme_path())
        self.addDockWidget(Qt.BottomDockWidgetArea, self.git_graph_dock)
        self.git_graph_dock.hide()
        self.git_service.snapshotReady.connect(self._on_git_snapshot)
        self.git_service.failed.connect(self._on_git_failure)

        # GitService is created after the body and menus, so startup refresh belongs
        # here, after all widgets and signals connections exists.

        self._refresh_git_state()
```


**New version:**


```python
    def init_ui(self):
        """Build the main window panels, menus, editor area and status controls.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(100)
        self._debounce.timeout.connect(self.render_preview)
        self.setWindowTitle("Code Editor")
        self.setWindowIcon(QIcon(resource_path("icons/app-icon-256.png")))
        self.resize(self.WIDTH, self.HEIGHT)
        self.window_font = QFont("sans-serif")
        self.window_font.setPointSize(13)
        self.setFont(self.window_font)
        qss_path = resource_path("css/style.qss")
        print(f"QSS path: {qss_path}")
        print(f"QSS exists: {os.path.exists(qss_path)}")
        try:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError as e:
            print(f"STYLESHEET ERROR: {e}")
            # Fallback: apply basic dark styling inline
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1f22; color: #d3d3d3; }
                QMenuBar { background-color: #2d2d2d; color: floralwhite; }
                QTabWidget { background-color: #1e1f22; color: #d3d3d3; }
            """)

        self._outline_debounce = QTimer(self)
        self._outline_debounce.setSingleShot(True)
        self._outline_debounce.setInterval(500)

        # BUGFIX: was connected to its own start() -> restarted itself forever
        self._outline_debounce.timeout.connect(self._update_outline)
        self.set_up_menu()
        self.set_up_body()
        self._git_refresh_timer = QTimer(self)
        self._git_refresh_timer.setInterval(15000)
        self._git_refresh_timer.timeout.connect(self._refresh_git_state)
        self._git_refresh_timer.start()
        # Find/Replace bar. Hidden by default
        self.find_bar = FindReplaceBar(show_replace=False, parent=self)
        self.find_bar.hide()
        # Connect the find bar's signals to our search methods
        self.find_bar.find_next_requested.connect(self._do_find_next)
        self.find_bar.find_prev_requested.connect(self._do_find_prev)
        self.find_bar.replace_requested.connect(self._do_replace)
        self.find_bar.replace_all_requested.connect(self._do_replace_all)
        self.set_up_console_dock()

        self._preview_ready = False
        self.preview.loadFinished.connect(self._on_preview_loaded)
        base = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{self._preview_css}</style></head><body><div id="content"></div></body></html>"""
        self.preview.setHtml(base)
        require_qt(self.statusBar()).setFont(self.window_font)
        require_qt(self.statusBar()).setStyleSheet("""
                color: #CCCCCC;
        """)

        require_qt(self.statusBar()).showMessage(f"Interpreter: {self.python_runner.interpreter}")
        self.cursor_pos_label = QLabel("Ln 1, Col 1")
        self.cursor_pos_label.setStyleSheet("color: #888; padding: 0 10px;")
        require_qt(self.statusBar()).addPermanentWidget(self.cursor_pos_label)

        # --- Cozy Mode: the status bar cat ---------------------------------------------------------- #

        self.cat = CatController(self)
        require_qt(self.statusBar()).addPermanentWidget(self.cat)
        from cozy.neko import NekoChaser
        self.neko = NekoChaser(self)
        self.neko.start()

        # C2: level-ups plat rhe Dance frames and announce themselves

        self.cat.level_up.connect(
            lambda lvl, title: require_qt(self.statusBar()).showMessage(
                f"Cat leveled up: {title} (level {lvl})", 3000
            )
        )

        # C1: pet milestones (achievement logic lives in the handler, NOT in the lambda
        # keep lambdas dump, they cannot be extended
        self.cat.petted.connect(self._on_cat_petted)

        from cozy.power_mode import PowerModeController

        # Honor the saved Power Mode states from the View menu dropdown.

        self.power = PowerModeController(
            self,
            enabled=self.power_mode_action.isChecked(),
            shake_intensity=1,
            particles_on=self.power_particles_action.isChecked(),
            shake_on=self.power_shake_action.isChecked(),
            glow_enabled=self.power_glow_action.isChecked(),
        )
        self.python_runner.process_started.connect(self._on_run_started)
        self.python_runner.process_finished.connect(self._on_run_finished)

        # Word count label - shows "Words: X | Chars: Y"

        self.word_count_label = QLabel("Words: 0 | Chars: 0")
        self.word_count_label.setStyleSheet("color: #888; padding: 0 10px;")
        require_qt(self.statusBar()).addPermanentWidget(self.word_count_label)
        self.show()

        QTimer.singleShot(2000, lambda: self.check_for_updates(manual=False))
        # --- idle choreography: sleepy -> box -> sleep ------------------ #
        # Escalation ladder: 60 s idle = yawn; 3 min = deep sleep; 10 min =
        # the cat moves into a box (and pops back out when you return).
        # Timers re-arm on activity via _connect_editor's textChanged below.
        self._cat_sleepy_timer = QTimer(self)
        self._cat_sleepy_timer.setSingleShot(True)
        self._cat_sleepy_timer.timeout.connect(lambda: self.cat.set_state("sleepy", 120000))
        self._cat_sleep_timer = QTimer(self)
        self._cat_sleep_timer.setSingleShot(True)
        self._cat_sleep_timer.timeout.connect(lambda: self.cat.set_state("sleep", 300000))
        self._cat_box_timer = QTimer(self)
        self._cat_box_timer.setSingleShot(True)
        self._cat_box_timer.timeout.connect(self._cat_moves_into_box)
        self._arm_cat_timers()

        # Git Integration
        self.git_service = GitService(self)
        self.git_branch_label = QLabel("No Git repository", self)
        require_qt(self.statusBar()).addPermanentWidget(self.git_branch_label)
        self.git_graph = CommitGraphPanel(self)
        self.git_graph_dock = QDockWidget("Git History", self)
        self.git_graph_dock.setObjectName("GitHistoryDock")
        self.git_graph_dock.setWidget(self.git_graph)
        self._apply_git_history_theme(self._active_theme_path())
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.git_graph_dock)
        self.git_graph_dock.hide()
        self.git_service.snapshotReady.connect(self._on_git_snapshot)
        self.git_service.failed.connect(self._on_git_failure)

        # GitService is created after the body and menus, so startup refresh belongs
        # here, after all widgets and signals connections exists.

        self._refresh_git_state()
```


**Implementation:** inside `main.py`, replace only `MainWindow.init_ui`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.4 Existing method/function `MainWindow._apply_git_history_theme`

Theme the history content, dock title, and current-branch indicator. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 429–439:**


```python
    def _apply_git_history_theme(self, theme_path) -> None:
        """Theme the history content, dock title, and current-branch indicator."""
        self.git_graph.apply_theme(theme_path)
        foreground = self.git_graph.palette().color(QPalette.Text).name()
        background = self.git_graph.background
        accent = self.git_graph.lane_color(0).name()
        self.git_graph_dock.setStyleSheet(
            f"QDockWidget#GitHistoryDock {{ color:{foreground}; }}"
            f"QDockWidget#GitHistoryDock::title {{ background:{background}; padding:6px; }}"
        )
        self.git_branch_label.setStyleSheet(f"color:{accent}; padding:0 8px; font-weight:600;")
```


**New version:**


```python
    def _apply_git_history_theme(self, theme_path) -> None:
        """Theme the history content, dock title, and current-branch indicator."""
        self.git_graph.apply_theme(theme_path)
        foreground = self.git_graph.palette().color(QPalette.ColorRole.Text).name()
        background = self.git_graph.background
        accent = self.git_graph.lane_color(0).name()
        self.git_graph_dock.setStyleSheet(
            f"QDockWidget#GitHistoryDock {{ color:{foreground}; }}"
            f"QDockWidget#GitHistoryDock::title {{ background:{background}; padding:6px; }}"
        )
        self.git_branch_label.setStyleSheet(f"color:{accent}; padding:0 8px; font-weight:600;")
```


**Implementation:** inside `main.py`, replace only `MainWindow._apply_git_history_theme`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.5 Existing method/function `MainWindow._on_cat_petted`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 510–522:**


```python
    def _on_cat_petted(self, total_pets: int):
        """
        C1: react to pet milestones.
        Fires on EVERY pet (the sigggnal carries the total), but the checks are
        exact matches so each milestone fires exactlz one. A >= check would re-triggggger
        on every pet past the treshold.

        :param total_pets: new lifetime pet count.
        """

        if total_pets == 1000:
            self.cat.set_party_hat(True)
            self.statusBar().showMessage("Achievement unlocked: Certified Cat Person", 5000)
```


**New version:**


```python
    def _on_cat_petted(self, total_pets: int):
        """
        C1: react to pet milestones.
        Fires on EVERY pet (the sigggnal carries the total), but the checks are
        exact matches so each milestone fires exactlz one. A >= check would re-triggggger
        on every pet past the treshold.

        :param total_pets: new lifetime pet count.
        """

        if total_pets == 1000:
            self.cat.set_party_hat(True)
            require_qt(self.statusBar()).showMessage("Achievement unlocked: Certified Cat Person", 5000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._on_cat_petted`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.6 Existing method/function `MainWindow._toggle_power_mode`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 551–568:**


```python
    def _toggle_power_mode(self, on: bool):
        """
        B1/C7: master switch for Power Mode (View -> Power Mode -> Enabled).
        Turning it off also clears any in-flight particles, stops the
        shake and the glow (the controller's set_enabled does that), so
        nothing keeps playing after the switch. The individual effect
        toggles stay as they were and take effect again when the master
        switch is back on. Persisted in QSettings so the next launch
        starts in the same mode.

        :param on: True = Power Mode enabled (subject to effect toggles)
        """

        power = getattr(self, "power", None)
        if power is not None:
            power.set_enabled(on)
        self.settings.setValue("power_mode", on)
        self.statusBar().showMessage("Power Mode ON" if on else "Power Mode OFF", 2000)
```


**New version:**


```python
    def _toggle_power_mode(self, on: bool):
        """
        B1/C7: master switch for Power Mode (View -> Power Mode -> Enabled).
        Turning it off also clears any in-flight particles, stops the
        shake and the glow (the controller's set_enabled does that), so
        nothing keeps playing after the switch. The individual effect
        toggles stay as they were and take effect again when the master
        switch is back on. Persisted in QSettings so the next launch
        starts in the same mode.

        :param on: True = Power Mode enabled (subject to effect toggles)
        """

        power = getattr(self, "power", None)
        if power is not None:
            power.set_enabled(on)
        self.settings.setValue("power_mode", on)
        require_qt(self.statusBar()).showMessage("Power Mode ON" if on else "Power Mode OFF", 2000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._toggle_power_mode`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.7 Existing method/function `MainWindow._toggle_power_particles`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 570–576:**


```python
    def _toggle_power_particles(self, on: bool):
        """B1: particles-only switch (View -> Power Mode -> Particles)."""
        power = getattr(self, "power", None)
        if power is not None:
            power.set_particles(on)
        self.settings.setValue("power_particles", on)
        self.statusBar().showMessage("Particles ON" if on else "Particles OFF", 2000)
```


**New version:**


```python
    def _toggle_power_particles(self, on: bool):
        """B1: particles-only switch (View -> Power Mode -> Particles)."""
        power = getattr(self, "power", None)
        if power is not None:
            power.set_particles(on)
        self.settings.setValue("power_particles", on)
        require_qt(self.statusBar()).showMessage("Particles ON" if on else "Particles OFF", 2000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._toggle_power_particles`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.8 Existing method/function `MainWindow._toggle_power_shake`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 578–584:**


```python
    def _toggle_power_shake(self, on: bool):
        """B1: screen-shake-only switch (View -> Power Mode -> Screen Shake)."""
        power = getattr(self, "power", None)
        if power is not None:
            power.set_shake_enabled(on)
        self.settings.setValue("power_shake", on)
        self.statusBar().showMessage("Screen Shake ON" if on else "Screen Shake OFF", 2000)
```


**New version:**


```python
    def _toggle_power_shake(self, on: bool):
        """B1: screen-shake-only switch (View -> Power Mode -> Screen Shake)."""
        power = getattr(self, "power", None)
        if power is not None:
            power.set_shake_enabled(on)
        self.settings.setValue("power_shake", on)
        require_qt(self.statusBar()).showMessage("Screen Shake ON" if on else "Screen Shake OFF", 2000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._toggle_power_shake`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.9 Existing method/function `MainWindow._toggle_power_glow`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 586–593:**


```python
    def _toggle_power_glow(self, on: bool):
        """C7: combo-glow-only switch (View -> Power Mode -> Combo Glow)."""
        power = getattr(self, "power", None)
        if power is not None:
            power.set_glow(on)

        self.settings.setValue("power_glow", on)
        self.statusBar().showMessage("Combo Glow ON" if on else "Combo Glow OFF", 2000)
```


**New version:**


```python
    def _toggle_power_glow(self, on: bool):
        """C7: combo-glow-only switch (View -> Power Mode -> Combo Glow)."""
        power = getattr(self, "power", None)
        if power is not None:
            power.set_glow(on)

        self.settings.setValue("power_glow", on)
        require_qt(self.statusBar()).showMessage("Combo Glow ON" if on else "Combo Glow OFF", 2000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._toggle_power_glow`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.10 Existing method/function `MainWindow.set_up_console_dock`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 645–674:**


```python
    def set_up_console_dock(self):
        """Create the bottom console panel."""
        self.console = ConsoleWidget(self.python_runner, self)
        self.console.run_btn.clicked.connect(self.run_current_file)
        dock = QDockWidget("Python Console", self)
        dock.setWidget(self.console)
        dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        dock.hide()
        self.console_dock = dock
        terminal_directory = (
            self._workspace_root
            if hasattr(sys, "_MEIPASS")
            else self.file_manager.current_folder or self._workspace_root
        )

        # Terminal (new)
        self.terminal = TerminalWidget(parent=self, working_directory=terminal_directory)
        t_dock = QDockWidget("Terminal", self)
        t_dock.setWidget(self.terminal)
        t_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.addDockWidget(Qt.BottomDockWidgetArea, t_dock)
        t_dock.hide()
        self.terminal_dock = t_dock

        # Menu shortcuts, Run, and the dock close button must update the icons too;
        dock.visibilityChanged.connect(lambda visible: self._set_sidebar_icon("console", visible))
        t_dock.visibilityChanged.connect(
            lambda visible: self._set_sidebar_icon("terminal", visible)
        )
```


**New version:**


```python
    def set_up_console_dock(self):
        """Create the bottom console panel."""
        self.console = ConsoleWidget(self.python_runner, self)
        self.console.run_btn.clicked.connect(self.run_current_file)
        dock = QDockWidget("Python Console", self)
        dock.setWidget(self.console)
        dock.setFeatures(qt_flags(QDockWidget.DockWidgetFeatures, QDockWidget.DockWidgetFeature.DockWidgetClosable, QDockWidget.DockWidgetFeature.DockWidgetMovable))
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        dock.hide()
        self.console_dock = dock
        terminal_directory = (
            self._workspace_root
            if hasattr(sys, "_MEIPASS")
            else self.file_manager.current_folder or self._workspace_root
        )

        # Terminal (new)
        self.terminal = TerminalWidget(parent=self, working_directory=terminal_directory)
        t_dock = QDockWidget("Terminal", self)
        t_dock.setWidget(self.terminal)
        t_dock.setFeatures(qt_flags(QDockWidget.DockWidgetFeatures, QDockWidget.DockWidgetFeature.DockWidgetClosable, QDockWidget.DockWidgetFeature.DockWidgetMovable))
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, t_dock)
        t_dock.hide()
        self.terminal_dock = t_dock

        # Menu shortcuts, Run, and the dock close button must update the icons too;
        dock.visibilityChanged.connect(lambda visible: self._set_sidebar_icon("console", visible))
        t_dock.visibilityChanged.connect(
            lambda visible: self._set_sidebar_icon("terminal", visible)
        )
```


**Implementation:** inside `main.py`, replace only `MainWindow.set_up_console_dock`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.11 Existing method/function `MainWindow.get_sidebar_label`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.

Use the declared click signal instead of assigning a lambda to QLabel.mousePressEvent. The existing sidebar dispatcher still receives the original event and panel name.


**Old version — original lines 685–694:**


```python
    def get_sidebar_label(self, path, name):
        """Create a named clickable sidebar icon using the shared dispatcher."""
        label = QLabel(self)
        label.setPixmap(QPixmap(path).scaled(QSize(25, 25)))
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setFont(self.window_font)
        label.setToolTip(name.title())
        label.setCursor(Qt.PointingHandCursor)
        label.mousePressEvent = lambda e: self.show_hide_tab(e, name)
        return label
```


**New version:**


```python
    def get_sidebar_label(self, path, name):
        """Create a named clickable sidebar icon using the shared dispatcher."""
        label = ClickableLabel(self)
        label.setPixmap(QPixmap(path).scaled(QSize(25, 25)))
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setFont(self.window_font)
        label.setToolTip(name.title())
        label.setCursor(Qt.CursorShape.PointingHandCursor)
        # Keep the QLabel method intact; connect the explicitly declared signal.
        label.pressed.connect(lambda event: self.show_hide_tab(event, name))
        return label
```


**Implementation:** inside `main.py`, replace only `MainWindow.get_sidebar_label`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.12 Existing method/function `MainWindow.get_editor`

The annotation now includes `None`, which the existing default and unsaved-document branch already accept. This makes the contract match the existing behavior.


**Old version — original lines 696–716:**


```python
    def get_editor(self, path: Path = None, is_python_file=None) -> QsciScintilla:
        """Create the correct editor using the shared extension policy."""
        if path is not None and is_python_file is None:
            path = Path(path)
            is_python_file = is_python_path(path)
        elif is_python_file is None:
            is_python_file = self.python_editor_active

        if is_python_file:
            editor = PythonEditor(
                path=path,
                is_python_file=True,
                ruff_lsp_client=self.ruff_lsp_client,
            )
        else:
            editor = MarkdownEditor(path=path, is_python_file=False)

        saved = getattr(self, "_current_settings", None)
        if saved:
            self._apply_editor_settings(editor, saved)
        return editor
```


**New version:**


```python
    def get_editor(self, path: Path | None = None, is_python_file=None) -> QsciScintilla:
        """Create the correct editor using the shared extension policy."""
        if path is not None and is_python_file is None:
            path = Path(path)
            is_python_file = is_python_path(path)
        elif is_python_file is None:
            is_python_file = self.python_editor_active

        if is_python_file:
            editor = PythonEditor(
                path=path,
                is_python_file=True,
                ruff_lsp_client=self.ruff_lsp_client,
            )
        else:
            editor = MarkdownEditor(path=path, is_python_file=False)

        saved = getattr(self, "_current_settings", None)
        if saved:
            self._apply_editor_settings(editor, saved)
        return editor
```


**Implementation:** inside `main.py`, replace only `MainWindow.get_editor`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.13 Existing method/function `MainWindow._connect_editor`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 722–747:**


```python
    def _connect_editor(self, editor):
        """Connect all MainWindow signals required by an editor."""
        editor.textChanged.connect(lambda ed=editor: self._on_editor_text_changed(ed))
        editor.textChanged.connect(self._debounce.start)
        editor.textChanged.connect(self._outline_debounce.start)
        editor.textChanged.connect(self.update_word_count)
        editor.textChanged.connect(self._on_typing_xp)
        editor.textChanged.connect(lambda: self.power.attach_editor(editor))
        editor.textChanged.connect(self._arm_cat_timers)
        editor.textChanged.connect(self._cat_unbox)
        editor.cursorPositionChanged.connect(
            lambda line, column, ed=editor: self._on_editor_cursor_changed(ed, line, column)
        )
        editor.cursorPositionChanged.connect(lambda line, column, ed=editor: self.sync_scroll(ed))
        editor.verticalScrollBar().valueChanged.connect(
            lambda value, ed=editor: self.sync_scroll(ed)
        )
        if isinstance(editor, PythonEditor):
            editor.goto_definition_requested.connect(self._open_file_at_position)
            if editor.ruff_lsp is not None:
                editor.ruff_lsp.diagnostics_changed.connect(self._on_ruff_diagnostics)
        if hasattr(self, "diagnostics_manager"):
            self._bind_diagnostic_editor(editor)
        if (isinstance(editor, PythonEditor) and editor.ruff_lsp is not None
                and hasattr(self, "type_diagnostics")):
            self.type_diagnostics.attach(editor.ruff_lsp)
```


**New version:**


```python
    def _connect_editor(self, editor):
        """Connect all MainWindow signals required by an editor."""
        editor.textChanged.connect(lambda ed=editor: self._on_editor_text_changed(ed))
        editor.textChanged.connect(self._debounce.start)
        editor.textChanged.connect(self._outline_debounce.start)
        editor.textChanged.connect(self.update_word_count)
        editor.textChanged.connect(self._on_typing_xp)
        editor.textChanged.connect(lambda: self.power.attach_editor(editor))
        editor.textChanged.connect(self._arm_cat_timers)
        editor.textChanged.connect(self._cat_unbox)
        editor.cursorPositionChanged.connect(
            lambda line, column, ed=editor: self._on_editor_cursor_changed(ed, line, column)
        )
        editor.cursorPositionChanged.connect(lambda line, column, ed=editor: self.sync_scroll(ed))
        require_qt(editor.verticalScrollBar()).valueChanged.connect(
            lambda value, ed=editor: self.sync_scroll(ed)
        )
        if isinstance(editor, PythonEditor):
            editor.goto_definition_requested.connect(self._open_file_at_position)
            if editor.ruff_lsp is not None:
                editor.ruff_lsp.diagnostics_changed.connect(self._on_ruff_diagnostics)
        if hasattr(self, "diagnostics_manager"):
            self._bind_diagnostic_editor(editor)
        if (isinstance(editor, PythonEditor) and editor.ruff_lsp is not None
                and hasattr(self, "type_diagnostics")):
            self.type_diagnostics.attach(editor.ruff_lsp)
```


**Implementation:** inside `main.py`, replace only `MainWindow._connect_editor`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.14 Existing method/function `MainWindow._on_ruff_lsp_error`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 758–761:**


```python
    def _on_ruff_lsp_error(self, message: str):
        """Expose Ruff LSP startup and protocol failures to the user."""
        print(f"Ruff LSP error {message}")
        self.statusBar().showMessage(message, 8000)
```


**New version:**


```python
    def _on_ruff_lsp_error(self, message: str):
        """Expose Ruff LSP startup and protocol failures to the user."""
        print(f"Ruff LSP error {message}")
        require_qt(self.statusBar()).showMessage(message, 8000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._on_ruff_lsp_error`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.15 New method/function `MainWindow._on_new_file_action`

Connect QAction signals to explicit None-returning adapters. The checked boolean is intentionally ignored; new_file/save_file/save_as retain their useful return values for direct callers.

**New code:**


```python
    def _on_new_file_action(self, checked: bool = False) -> None:
        """Open a new tab when QAction emits triggered(bool).

        Args:
            checked: QAction's checked state; unused for this non-checkable
                command. It must not become new_file's target-group argument.

        Discard the returned editor because a Qt signal slot returns no value.
        """
        self.new_file()
```


**Implementation:** add this method before `MainWindow.set_up_menu` in `main.py`. Keep it inside its named class where applicable. No old method is deleted.


#### 2.4.16 New method/function `MainWindow._on_save_file_action`

Save the active file and discard the command's success result. The replacement below includes the updated declaration and explanatory comments.

**New code:**


```python
    def _on_save_file_action(self, checked: bool = False) -> None:
        """Save the active file and discard the command's success result.

        Args:
            checked: Unused QAction checked state. Keeping it explicit matches
                the signal while the command keeps its useful bool return type.
        """
        self.save_file()
```


**Implementation:** add this method before `MainWindow.set_up_menu` in `main.py`. Keep it inside its named class where applicable. No old method is deleted.


#### 2.4.17 New method/function `MainWindow._on_save_as_action`

Connect QAction signals to explicit None-returning adapters. The checked boolean is intentionally ignored; new_file/save_file/save_as retain their useful return values for direct callers.

**New code:**


```python
    def _on_save_as_action(self, checked: bool = False) -> None:
        """Run Save As without returning its bool result to Qt.

        Args:
            checked: Unused QAction checked state. Signal callbacks return None,
                while direct callers of save_as can still use its bool result.
        """
        self.save_as()
```


**Implementation:** add this method before `MainWindow.set_up_menu` in `main.py`. Keep it inside its named class where applicable. No old method is deleted.


#### 2.4.18 Existing method/function `MainWindow.set_up_menu`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.

Connect QAction signals to explicit None-returning adapters. The checked boolean is intentionally ignored; new_file/save_file/save_as retain their useful return values for direct callers.


**Old version — original lines 821–1121:**


```python
    def set_up_menu(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        new_file = file_menu.addAction("New")
        new_file.setShortcut("Ctrl+N")
        new_file.setShortcutContext(Qt.ApplicationShortcut)
        new_file.triggered.connect(self.new_file)

        open_file = file_menu.addAction("Open File")
        open_file.setShortcut("Ctrl+O")
        open_file.setShortcutContext(Qt.ApplicationShortcut)
        open_file.triggered.connect(self.open_file)

        # Open Recent submenu
        # addMenu returns a QMenu object. We store it as an instance
        # variable so we can rebuild it when the recent files list changes.
        self.recent_menu = file_menu.addMenu("Open Recent")
        self._update_recent_menu()

        open_folder = file_menu.addAction("Open Folder")
        open_folder.setShortcut("Ctrl+K")
        open_folder.setShortcutContext(Qt.ApplicationShortcut)
        open_folder.triggered.connect(self.open_folder)

        file_menu.addSeparator()

        save_file = file_menu.addAction("Save")
        save_file.setShortcut("Ctrl+S")
        save_file.setShortcutContext(Qt.ApplicationShortcut)
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save As")
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.setShortcutContext(Qt.ApplicationShortcut)
        save_as.triggered.connect(self.save_as)

        save_all_action = file_menu.addAction("Save All")
        save_all_action.setShortcut("Ctrl+Shift+A")
        save_all_action.setShortcutContext(Qt.ApplicationShortcut)
        save_all_action.triggered.connect(self.save_all)

        close_all_action = file_menu.addAction("Close All")
        close_all_action.setShortcut("Ctrl+Shift+W")
        close_all_action.setShortcutContext(Qt.ApplicationShortcut)
        close_all_action.triggered.connect(self._close_all_tabs)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        undo_action = edit_menu.addAction("Undo")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setShortcutContext(Qt.ApplicationShortcut)
        undo_action.triggered.connect(self.undo)

        redo_action = edit_menu.addAction("Redo")
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.setShortcutContext(Qt.ApplicationShortcut)

        redo_action.triggered.connect(self.redo)

        edit_menu.addSeparator()

        cut_action = edit_menu.addAction("Cut")
        cut_action.setShortcut("Ctrl+X")
        cut_action.setShortcutContext(Qt.ApplicationShortcut)
        cut_action.triggered.connect(self.cut)

        copy_action = edit_menu.addAction("Copy")
        copy_action.setShortcut("Ctrl+C")
        copy_action.setShortcutContext(Qt.ApplicationShortcut)
        copy_action.triggered.connect(self.copy)

        paste_action = edit_menu.addAction("Paste")
        paste_action.setShortcut("Ctrl+V")
        paste_action.setShortcutContext(Qt.ApplicationShortcut)
        paste_action.triggered.connect(self.paste)

        edit_menu.addSeparator()

        select_all_action = edit_menu.addAction("Select All")
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setShortcutContext(Qt.ApplicationShortcut)
        select_all_action.triggered.connect(self.select_all)

        delete_line_action = edit_menu.addAction("Delete Line")
        delete_line_action.setShortcut("Ctrl+Shift+K")
        delete_line_action.setShortcutContext(Qt.ApplicationShortcut)
        delete_line_action.triggered.connect(self.delete_line)

        edit_menu.addSeparator()

        find_action = edit_menu.addAction("Find")
        find_action.setShortcut("Ctrl+F")
        find_action.setShortcutContext(Qt.ApplicationShortcut)
        find_action.triggered.connect(self.show_find_bar)

        replace_action = edit_menu.addAction("Replace")
        replace_action.setShortcut("Ctrl+H")
        replace_action.setShortcutContext(Qt.ApplicationShortcut)
        replace_action.triggered.connect(self.show_replace_bar)

        edit_menu.addSeparator()

        goto_action = edit_menu.addAction("Go to Line")
        goto_action.setShortcut("Ctrl+G")
        goto_action.setShortcutContext(Qt.ApplicationShortcut)
        goto_action.triggered.connect(self.goto_line)

        edit_menu.addSeparator()

        toggle_comment_action = edit_menu.addAction("Toggle Comment")
        toggle_comment_action.setShortcut("Ctrl+1")
        toggle_comment_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_comment_action.triggered.connect(self.toggle_comment)

        edit_menu.addSeparator()

        goto_definition_action = edit_menu.addAction("Go to Definition")
        goto_definition_action.setShortcut("F12")
        goto_definition_action.setShortcutContext(Qt.ApplicationShortcut)
        goto_definition_action.triggered.connect(self._trigger_goto_definition)

        # Mode menu
        mode_menu = menu_bar.addMenu("Mode")

        # change to Python-Editor
        self.python_editor_action = mode_menu.addAction("Python Editor")
        self.python_editor_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        self.python_editor_action.setShortcutContext(Qt.ApplicationShortcut)
        self.python_editor_action.triggered.connect(self.change_editor_python)

        # change to Markdown-Editor
        self.markdown_editor_action = mode_menu.addAction("Markdown Editor")
        self.markdown_editor_action.setShortcut(QKeySequence("Ctrl+Shift+M"))
        self.markdown_editor_action.setShortcutContext(Qt.ApplicationShortcut)
        self.markdown_editor_action.triggered.connect(self.change_editor_markdown)

        run_menu = self.menuBar().addMenu("Run")

        run_file_action = run_menu.addAction("Run File")
        run_file_action.setShortcut("F5")
        run_file_action.setShortcutContext(Qt.ApplicationShortcut)
        run_file_action.triggered.connect(self.run_current_file)

        run_with_args_action = run_menu.addAction("Run with Arguments")
        run_with_args_action.setShortcut("Shift+F5")
        run_with_args_action.setShortcutContext(Qt.ApplicationShortcut)
        run_with_args_action.triggered.connect(self.run_with_arguments)

        run_selection_action = run_menu.addAction("Run Selection")
        run_selection_action.setShortcut("Ctrl+Return")
        run_selection_action.setShortcutContext(Qt.ApplicationShortcut)
        run_selection_action.triggered.connect(self.run_selection)

        stop_action = run_menu.addAction("Stop")
        stop_action.setShortcut("F6")
        stop_action.setShortcutContext(Qt.ApplicationShortcut)
        stop_action.triggered.connect(self.python_runner.stop)

        run_menu.addSeparator()

        interpreter_action = run_menu.addAction("Choose Interpreter...")
        interpreter_action.triggered.connect(self.choose_interpreter)

        # Viewmenu for toggling the Sidebar
        view_menu = self.menuBar().addMenu("View")

        toggle_sidebar_action = view_menu.addAction("Toggle Sidebar")
        toggle_sidebar_action.setShortcut("Ctrl+B")
        toggle_sidebar_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)

        toggle_preview_action = view_menu.addAction("Toggle Preview")
        toggle_preview_action.setShortcut("Ctrl+J")
        toggle_preview_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_preview_action.triggered.connect(self.toggle_preview)

        toggle_console_action = view_menu.addAction("Toggle Console")
        toggle_console_action.setShortcut("Ctrl+Shift+-")
        toggle_console_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_console_action.triggered.connect(self.toggle_console)

        toggle_terminal_action = view_menu.addAction("Toggle Terminal")
        toggle_terminal_action.setShortcut("Ctrl+Shift+]")
        toggle_terminal_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_terminal_action.triggered.connect(self.toggle_terminal)

        view_menu.addSeparator()
        split_right_action = view_menu.addAction("Split Right")
        split_right_action.setShortcut("Ctrl+Alt+Right")
        split_right_action.setShortcutContext(Qt.ApplicationShortcut)
        split_right_action.triggered.connect(self.split_current_editor_right)

        unsplit_action = view_menu.addAction("Unsplit")
        unsplit_action.setShortcut("Ctrl+Alt+Left")
        unsplit_action.setShortcutContext(Qt.ApplicationShortcut)
        unsplit_action.triggered.connect(self.unsplit_active_group)

        view_menu.addSeparator()
        fullscreen_editor = view_menu.addAction("Fullscreen")
        fullscreen_editor.setShortcut("F11")
        fullscreen_editor.setShortcutContext(Qt.ApplicationShortcut)
        fullscreen_editor.triggered.connect(self._show_full_screen)
        starting_window_size = view_menu.addAction("Startup Window Size")
        starting_window_size.setShortcut("Shift+F11")
        starting_window_size.setShortcutContext(Qt.ApplicationShortcut)
        starting_window_size.triggered.connect(self._startup_window_size)

        view_menu.addSeparator()
        git_refresh_action = view_menu.addAction("Refresh Git Status")
        git_refresh_action.setShortcut("Ctrl+Shift+G")
        git_refresh_action.setShortcutContext(Qt.ApplicationShortcut)
        git_refresh_action.triggered.connect(self._refresh_git_state)
        toggle_git_history_action = view_menu.addAction("Toggle Git History")
        toggle_git_history_action.setShortcut("Ctrl+Alt+G")
        toggle_git_history_action.setShortcutContext(Qt.ApplicationShortcut)
        toggle_git_history_action.triggered.connect(self._toggle_git_history)
        settings_action = view_menu.addAction("Settings")
        settings_action.setShortcut("Ctrl+Alt+S")
        settings_action.setShortcutContext(Qt.ApplicationShortcut)
        settings_action.triggered.connect(self.open_settings)
        hacker_action = view_menu.addAction("Hacker-Mode")
        hacker_action.setShortcut("Ctrl+Shift+H")
        hacker_action.setShortcutContext(Qt.ApplicationShortcut)
        hacker_action.setCheckable(True)
        hacker_action.setChecked(self._hacker)
        hacker_action.toggled.connect(self.set_hacker_mode)
        self.hacker_action = hacker_action

        # B1/C7: Power Mode dropdown — master switch plus one toggle per
        # effect. All four states persist in QSettings (power_mode,
        # power_particles, power_shake, power_glow) like ruff_save_mode.
        # The handlers guard on self.power because the menu is built
        # before the controller is created in init_ui().
        power_menu = view_menu.addMenu("Power Mode")
        self.power_mode_action = power_menu.addAction("Enabled")
        self.power_mode_action.setCheckable(True)
        self.power_mode_action.setChecked(self.settings.value("power_mode", True, type=bool))
        self.power_mode_action.setShortcut("Ctrl+Shift+X")
        self.power_mode_action.setShortcutContext(Qt.ApplicationShortcut)
        self.power_mode_action.toggled.connect(self._toggle_power_mode)
        power_menu.addSeparator()
        self.power_particles_action = power_menu.addAction("Particles")
        self.power_particles_action.setCheckable(True)
        self.power_particles_action.setChecked(
            self.settings.value("power_particles", True, type=bool)
        )
        self.power_particles_action.toggled.connect(self._toggle_power_particles)
        self.power_shake_action = power_menu.addAction("Screen Shake")
        self.power_shake_action.setCheckable(True)
        self.power_shake_action.setChecked(self.settings.value("power_shake", True, type=bool))
        self.power_shake_action.toggled.connect(self._toggle_power_shake)
        self.power_glow_action = power_menu.addAction("Combo Glow")
        self.power_glow_action.setCheckable(True)
        self.power_glow_action.setChecked(self.settings.value("power_glow", True, type=bool))
        self.power_glow_action.toggled.connect(self._toggle_power_glow)
        help_menu = menu_bar.addMenu("Help")
        check_updates_action = help_menu.addAction("Check for Updates")
        check_updates_action.triggered.connect(lambda: self.check_for_updates(manual=True))

        # Setting Object names for all shortcut actions for the command_palette
        new_file.setObjectName("menu.new_file")
        open_file.setObjectName("menu.open_file")
        open_folder.setObjectName("menu.open_folder")
        save_file.setObjectName("menu.save_file")
        save_as.setObjectName("menu.save_as")
        save_all_action.setObjectName("menu.save_all_action")
        close_all_action.setObjectName("menu.close_all_action")
        undo_action.setObjectName("menu.undo_action")
        redo_action.setObjectName("menu.redo_action")
        cut_action.setObjectName("menu.cut_action")
        copy_action.setObjectName("menu.copy_action")
        paste_action.setObjectName("menu.paste_action")
        select_all_action.setObjectName("menu.select_all_action")
        delete_line_action.setObjectName("menu.delete_line_action")
        find_action.setObjectName("menu.find_action")
        replace_action.setObjectName("menu.replace_action")
        goto_action.setObjectName("menu.goto_action")
        toggle_comment_action.setObjectName("menu.toggle_comment_action")
        goto_definition_action.setObjectName("menu.goto_definition_action")
        run_file_action.setObjectName("menu.run_file_action")
        run_with_args_action.setObjectName("menu.run_with_args_action")
        run_selection_action.setObjectName("menu.run_selection_action")
        stop_action.setObjectName("menu.stop_action")
        interpreter_action.setObjectName("menu.interpreter_action")
        toggle_sidebar_action.setObjectName("menu.toggle_sidebar_action")
        toggle_preview_action.setObjectName("menu.toggle_preview_action")
        toggle_console_action.setObjectName("menu.toggle_console_action")
        toggle_terminal_action.setObjectName("menu.toggle_terminal_action")
        split_right_action.setObjectName("menu.split_right_action")
        unsplit_action.setObjectName("menu.unsplit_action")
        fullscreen_editor.setObjectName("menu.fullscreen_editor")
        starting_window_size.setObjectName("menu.starting_window_size")
        git_refresh_action.setObjectName("menu.git_refresh_action")
        toggle_git_history_action.setObjectName("menu.toggle_git_history_action")
        settings_action.setObjectName("menu.settings_action")
        hacker_action.setObjectName("menu.hacker_action")
        check_updates_action.setObjectName("menu.check_updates_action")
```


**New version:**


```python
    def set_up_menu(self):
        """Create the editor menus, actions and keyboard shortcuts.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        menu_bar = require_qt(self.menuBar())

        # File menu
        file_menu = require_qt(menu_bar.addMenu("File"))

        new_file = require_qt(file_menu.addAction("New"))
        new_file.setShortcut("Ctrl+N")
        new_file.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        new_file.triggered.connect(self._on_new_file_action)

        open_file = require_qt(file_menu.addAction("Open File"))
        open_file.setShortcut("Ctrl+O")
        open_file.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        open_file.triggered.connect(self.open_file)

        # Open Recent submenu
        # addMenu returns a QMenu object. We store it as an instance
        # variable so we can rebuild it when the recent files list changes.
        self.recent_menu = require_qt(file_menu.addMenu("Open Recent"))
        self._update_recent_menu()

        open_folder = require_qt(file_menu.addAction("Open Folder"))
        open_folder.setShortcut("Ctrl+K")
        open_folder.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        open_folder.triggered.connect(self.open_folder)

        file_menu.addSeparator()

        save_file = require_qt(file_menu.addAction("Save"))
        save_file.setShortcut("Ctrl+S")
        save_file.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        save_file.triggered.connect(self._on_save_file_action)

        save_as = require_qt(file_menu.addAction("Save As"))
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        save_as.triggered.connect(self._on_save_as_action)

        save_all_action = require_qt(file_menu.addAction("Save All"))
        save_all_action.setShortcut("Ctrl+Shift+A")
        save_all_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        save_all_action.triggered.connect(self.save_all)

        close_all_action = require_qt(file_menu.addAction("Close All"))
        close_all_action.setShortcut("Ctrl+Shift+W")
        close_all_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        close_all_action.triggered.connect(self._close_all_tabs)

        # Edit menu
        edit_menu = require_qt(menu_bar.addMenu("Edit"))

        undo_action = require_qt(edit_menu.addAction("Undo"))
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        undo_action.triggered.connect(self.undo)

        redo_action = require_qt(edit_menu.addAction("Redo"))
        redo_action.setShortcut("Ctrl+Shift+Z")
        redo_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)

        redo_action.triggered.connect(self.redo)

        edit_menu.addSeparator()

        cut_action = require_qt(edit_menu.addAction("Cut"))
        cut_action.setShortcut("Ctrl+X")
        cut_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        cut_action.triggered.connect(self.cut)

        copy_action = require_qt(edit_menu.addAction("Copy"))
        copy_action.setShortcut("Ctrl+C")
        copy_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        copy_action.triggered.connect(self.copy)

        paste_action = require_qt(edit_menu.addAction("Paste"))
        paste_action.setShortcut("Ctrl+V")
        paste_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        paste_action.triggered.connect(self.paste)

        edit_menu.addSeparator()

        select_all_action = require_qt(edit_menu.addAction("Select All"))
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        select_all_action.triggered.connect(self.select_all)

        delete_line_action = require_qt(edit_menu.addAction("Delete Line"))
        delete_line_action.setShortcut("Ctrl+Shift+K")
        delete_line_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        delete_line_action.triggered.connect(self.delete_line)

        edit_menu.addSeparator()

        find_action = require_qt(edit_menu.addAction("Find"))
        find_action.setShortcut("Ctrl+F")
        find_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        find_action.triggered.connect(self.show_find_bar)

        replace_action = require_qt(edit_menu.addAction("Replace"))
        replace_action.setShortcut("Ctrl+H")
        replace_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        replace_action.triggered.connect(self.show_replace_bar)

        edit_menu.addSeparator()

        goto_action = require_qt(edit_menu.addAction("Go to Line"))
        goto_action.setShortcut("Ctrl+G")
        goto_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        goto_action.triggered.connect(self.goto_line)

        edit_menu.addSeparator()

        toggle_comment_action = require_qt(edit_menu.addAction("Toggle Comment"))
        toggle_comment_action.setShortcut("Ctrl+1")
        toggle_comment_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        toggle_comment_action.triggered.connect(self.toggle_comment)

        edit_menu.addSeparator()

        goto_definition_action = require_qt(edit_menu.addAction("Go to Definition"))
        goto_definition_action.setShortcut("F12")
        goto_definition_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        goto_definition_action.triggered.connect(self._trigger_goto_definition)

        # Mode menu
        mode_menu = require_qt(menu_bar.addMenu("Mode"))

        # change to Python-Editor
        self.python_editor_action = require_qt(mode_menu.addAction("Python Editor"))
        self.python_editor_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        self.python_editor_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self.python_editor_action.triggered.connect(self.change_editor_python)

        # change to Markdown-Editor
        self.markdown_editor_action = require_qt(mode_menu.addAction("Markdown Editor"))
        self.markdown_editor_action.setShortcut(QKeySequence("Ctrl+Shift+M"))
        self.markdown_editor_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self.markdown_editor_action.triggered.connect(self.change_editor_markdown)

        run_menu = require_qt(require_qt(self.menuBar()).addMenu("Run"))

        run_file_action = require_qt(run_menu.addAction("Run File"))
        run_file_action.setShortcut("F5")
        run_file_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        run_file_action.triggered.connect(self.run_current_file)

        run_with_args_action = require_qt(run_menu.addAction("Run with Arguments"))
        run_with_args_action.setShortcut("Shift+F5")
        run_with_args_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        run_with_args_action.triggered.connect(self.run_with_arguments)

        run_selection_action = require_qt(run_menu.addAction("Run Selection"))
        run_selection_action.setShortcut("Ctrl+Return")
        run_selection_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        run_selection_action.triggered.connect(self.run_selection)

        stop_action = require_qt(run_menu.addAction("Stop"))
        stop_action.setShortcut("F6")
        stop_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        stop_action.triggered.connect(self.python_runner.stop)

        run_menu.addSeparator()

        interpreter_action = require_qt(run_menu.addAction("Choose Interpreter..."))
        interpreter_action.triggered.connect(self.choose_interpreter)

        # Viewmenu for toggling the Sidebar
        view_menu = require_qt(require_qt(self.menuBar()).addMenu("View"))

        toggle_sidebar_action = require_qt(view_menu.addAction("Toggle Sidebar"))
        toggle_sidebar_action.setShortcut("Ctrl+B")
        toggle_sidebar_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)

        toggle_preview_action = require_qt(view_menu.addAction("Toggle Preview"))
        toggle_preview_action.setShortcut("Ctrl+J")
        toggle_preview_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        toggle_preview_action.triggered.connect(self.toggle_preview)

        toggle_console_action = require_qt(view_menu.addAction("Toggle Console"))
        toggle_console_action.setShortcut("Ctrl+Shift+-")
        toggle_console_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        toggle_console_action.triggered.connect(self.toggle_console)

        toggle_terminal_action = require_qt(view_menu.addAction("Toggle Terminal"))
        toggle_terminal_action.setShortcut("Ctrl+Shift+]")
        toggle_terminal_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        toggle_terminal_action.triggered.connect(self.toggle_terminal)

        view_menu.addSeparator()
        split_right_action = require_qt(view_menu.addAction("Split Right"))
        split_right_action.setShortcut("Ctrl+Alt+Right")
        split_right_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        split_right_action.triggered.connect(self.split_current_editor_right)

        unsplit_action = require_qt(view_menu.addAction("Unsplit"))
        unsplit_action.setShortcut("Ctrl+Alt+Left")
        unsplit_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        unsplit_action.triggered.connect(self.unsplit_active_group)

        view_menu.addSeparator()
        fullscreen_editor = require_qt(view_menu.addAction("Fullscreen"))
        fullscreen_editor.setShortcut("F11")
        fullscreen_editor.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        fullscreen_editor.triggered.connect(self._show_full_screen)
        starting_window_size = require_qt(view_menu.addAction("Startup Window Size"))
        starting_window_size.setShortcut("Shift+F11")
        starting_window_size.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        starting_window_size.triggered.connect(self._startup_window_size)

        view_menu.addSeparator()
        git_refresh_action = require_qt(view_menu.addAction("Refresh Git Status"))
        git_refresh_action.setShortcut("Ctrl+Shift+G")
        git_refresh_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        git_refresh_action.triggered.connect(self._refresh_git_state)
        toggle_git_history_action = require_qt(view_menu.addAction("Toggle Git History"))
        toggle_git_history_action.setShortcut("Ctrl+Alt+G")
        toggle_git_history_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        toggle_git_history_action.triggered.connect(self._toggle_git_history)
        settings_action = require_qt(view_menu.addAction("Settings"))
        settings_action.setShortcut("Ctrl+Alt+S")
        settings_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        settings_action.triggered.connect(self.open_settings)
        hacker_action = require_qt(view_menu.addAction("Hacker-Mode"))
        hacker_action.setShortcut("Ctrl+Shift+H")
        hacker_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        hacker_action.setCheckable(True)
        hacker_action.setChecked(self._hacker)
        hacker_action.toggled.connect(self.set_hacker_mode)
        self.hacker_action = hacker_action

        # B1/C7: Power Mode dropdown — master switch plus one toggle per
        # effect. All four states persist in QSettings (power_mode,
        # power_particles, power_shake, power_glow) like ruff_save_mode.
        # The handlers guard on self.power because the menu is built
        # before the controller is created in init_ui().
        power_menu = require_qt(view_menu.addMenu("Power Mode"))
        self.power_mode_action = require_qt(power_menu.addAction("Enabled"))
        self.power_mode_action.setCheckable(True)
        self.power_mode_action.setChecked(self.settings.value("power_mode", True, type=bool))
        self.power_mode_action.setShortcut("Ctrl+Shift+X")
        self.power_mode_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self.power_mode_action.toggled.connect(self._toggle_power_mode)
        power_menu.addSeparator()
        self.power_particles_action = require_qt(power_menu.addAction("Particles"))
        self.power_particles_action.setCheckable(True)
        self.power_particles_action.setChecked(
            self.settings.value("power_particles", True, type=bool)
        )
        self.power_particles_action.toggled.connect(self._toggle_power_particles)
        self.power_shake_action = require_qt(power_menu.addAction("Screen Shake"))
        self.power_shake_action.setCheckable(True)
        self.power_shake_action.setChecked(self.settings.value("power_shake", True, type=bool))
        self.power_shake_action.toggled.connect(self._toggle_power_shake)
        self.power_glow_action = require_qt(power_menu.addAction("Combo Glow"))
        self.power_glow_action.setCheckable(True)
        self.power_glow_action.setChecked(self.settings.value("power_glow", True, type=bool))
        self.power_glow_action.toggled.connect(self._toggle_power_glow)
        help_menu = require_qt(menu_bar.addMenu("Help"))
        check_updates_action = require_qt(help_menu.addAction("Check for Updates"))
        check_updates_action.triggered.connect(lambda: self.check_for_updates(manual=True))

        # Setting Object names for all shortcut actions for the command_palette
        new_file.setObjectName("menu.new_file")
        open_file.setObjectName("menu.open_file")
        open_folder.setObjectName("menu.open_folder")
        save_file.setObjectName("menu.save_file")
        save_as.setObjectName("menu.save_as")
        save_all_action.setObjectName("menu.save_all_action")
        close_all_action.setObjectName("menu.close_all_action")
        undo_action.setObjectName("menu.undo_action")
        redo_action.setObjectName("menu.redo_action")
        cut_action.setObjectName("menu.cut_action")
        copy_action.setObjectName("menu.copy_action")
        paste_action.setObjectName("menu.paste_action")
        select_all_action.setObjectName("menu.select_all_action")
        delete_line_action.setObjectName("menu.delete_line_action")
        find_action.setObjectName("menu.find_action")
        replace_action.setObjectName("menu.replace_action")
        goto_action.setObjectName("menu.goto_action")
        toggle_comment_action.setObjectName("menu.toggle_comment_action")
        goto_definition_action.setObjectName("menu.goto_definition_action")
        run_file_action.setObjectName("menu.run_file_action")
        run_with_args_action.setObjectName("menu.run_with_args_action")
        run_selection_action.setObjectName("menu.run_selection_action")
        stop_action.setObjectName("menu.stop_action")
        interpreter_action.setObjectName("menu.interpreter_action")
        toggle_sidebar_action.setObjectName("menu.toggle_sidebar_action")
        toggle_preview_action.setObjectName("menu.toggle_preview_action")
        toggle_console_action.setObjectName("menu.toggle_console_action")
        toggle_terminal_action.setObjectName("menu.toggle_terminal_action")
        split_right_action.setObjectName("menu.split_right_action")
        unsplit_action.setObjectName("menu.unsplit_action")
        fullscreen_editor.setObjectName("menu.fullscreen_editor")
        starting_window_size.setObjectName("menu.starting_window_size")
        git_refresh_action.setObjectName("menu.git_refresh_action")
        toggle_git_history_action.setObjectName("menu.toggle_git_history_action")
        settings_action.setObjectName("menu.settings_action")
        hacker_action.setObjectName("menu.hacker_action")
        check_updates_action.setObjectName("menu.check_updates_action")
```


**Implementation:** inside `main.py`, replace only `MainWindow.set_up_menu`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.19 Existing method/function `MainWindow._install_command_palette`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1123–1134:**


```python
    def _install_command_palette(self):
        """Ecpose existing menu actions through one searchable command dialog."""
        self.command_regristry = CommandRegistry(self)
        self.command_palette = CommandPaletteDialog(self.command_regristry, self)
        menu = self.menuBar().addMenu("Commands")
        action = menu.addAction("Command Palette")
        action.setObjectName("workbench.command_palette")
        action.setShortcut("Ctrl+Alt+Y")
        action.triggered.connect(self.command_palette.open_palette)

        # Discovery runs again when opened, so rebuilt Recent Files entries stay valid.
        self.command_regristry.refresh_menus(self.menuBar())
```


**New version:**


```python
    def _install_command_palette(self):
        """Ecpose existing menu actions through one searchable command dialog."""
        self.command_regristry = CommandRegistry(self)
        self.command_palette = CommandPaletteDialog(self.command_regristry, self)
        menu = require_qt(require_qt(self.menuBar()).addMenu("Commands"))
        action = require_qt(menu.addAction("Command Palette"))
        action.setObjectName("workbench.command_palette")
        action.setShortcut("Ctrl+Alt+Y")
        action.triggered.connect(self.command_palette.open_palette)

        # Discovery runs again when opened, so rebuilt Recent Files entries stay valid.
        self.command_regristry.refresh_menus(require_qt(self.menuBar()))
```


**Implementation:** inside `main.py`, replace only `MainWindow._install_command_palette`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.20 Existing method/function `MainWindow.save_all`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1180–1202:**


```python
    def save_all(self):
        saved_count = 0
        original_editor = self.current_editor()

        for editor in list(self.tab_view.all_editors()):
            if editor not in self._dirty_editors:
                continue
            path = getattr(editor, "path", None)
            if path is None:
                self.tab_view.focus_editor(editor)
                if self.save_as():
                    saved_count += 1
                    continue
                break
            if self._save_editor_to_path(editor, Path(path)):
                saved_count += 1

        if original_editor is not None:
            self.tab_view.focus_editor(original_editor)
        self.statusBar().showMessage(
            f"Saved {saved_count} file(s)",
            3000,
        )
```


**New version:**


```python
    def save_all(self):
        """Save each open document through the existing save command.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        saved_count = 0
        original_editor = self.current_editor()

        for editor in list(self.tab_view.all_editors()):
            if editor not in self._dirty_editors:
                continue
            path = getattr(editor, "path", None)
            if path is None:
                self.tab_view.focus_editor(editor)
                if self.save_as():
                    saved_count += 1
                    continue
                break
            if self._save_editor_to_path(editor, Path(path)):
                saved_count += 1

        if original_editor is not None:
            self.tab_view.focus_editor(original_editor)
        require_qt(self.statusBar()).showMessage(
            f"Saved {saved_count} file(s)",
            3000,
        )
```


**Implementation:** inside `main.py`, replace only `MainWindow.save_all`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.21 Existing method/function `MainWindow._update_recent_menu`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1204–1216:**


```python
    def _update_recent_menu(self):
        """Rebuild the 'Open Recent' submenu from the recent_files list."""
        self.recent_menu.clear()

        if not self.recent_files:
            empty_action = self.recent_menu.addAction("(No recent files)")
            empty_action.setEnabled(False)
            return

        for path in self.recent_files:
            action = self.recent_menu.addAction(Path(path).name)
            action.setData(path)
            action.triggered.connect(lambda checked, p=path: self.open_recent_file(p))
```


**New version:**


```python
    def _update_recent_menu(self):
        """Rebuild the 'Open Recent' submenu from the recent_files list."""
        self.recent_menu.clear()

        if not self.recent_files:
            empty_action = require_qt(self.recent_menu.addAction("(No recent files)"))
            empty_action.setEnabled(False)
            return

        for path in self.recent_files:
            action = require_qt(self.recent_menu.addAction(Path(path).name))
            action.setData(path)
            action.triggered.connect(lambda checked, p=path: self.open_recent_file(p))
```


**Implementation:** inside `main.py`, replace only `MainWindow._update_recent_menu`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.22 Existing method/function `MainWindow._current_python_editor`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1407–1414:**


```python
    def _current_python_editor(self):
        """Return a runnable Python editor or show one consistent message."""
        editor = self.current_editor()
        if not isinstance(editor, PythonEditor):
            self.statusBar().showMessage("Run commands are available only for Python files", 3000)
            return None

        return editor
```


**New version:**


```python
    def _current_python_editor(self):
        """Return a runnable Python editor or show one consistent message."""
        editor = self.current_editor()
        if not isinstance(editor, PythonEditor):
            require_qt(self.statusBar()).showMessage("Run commands are available only for Python files", 3000)
            return None

        return editor
```


**Implementation:** inside `main.py`, replace only `MainWindow._current_python_editor`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.23 Existing method/function `MainWindow.run_with_arguments`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1416–1444:**


```python
    def run_with_arguments(self):
        editor = self._current_python_editor()
        if editor is None:
            return

        if editor.path is None:
            if not self.save_as():
                return
            editor = self.current_editor()
            if not isinstance(editor, PythonEditor) or editor.path is None:
                return
        elif not self.save_file():
            self.statusBar().showMessage("Run cancelled: save failed", 4000)
            return

        args, accepted = QInputDialog.getText(
            self,
            "Run with Arguments",
            "Command-line arguments",
            QLineEdit.Normal,
            "",
        )

        if not accepted:
            return

        self.console_dock.show()
        path = Path(editor.path)
        self.python_runner.run_file_with_args(path, args, cwd=path.parent)
```


**New version:**


```python
    def run_with_arguments(self):
        """Collect command-line arguments and run the selected Python file.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        editor = self._current_python_editor()
        if editor is None:
            return

        if editor.path is None:
            if not self.save_as():
                return
            editor = self.current_editor()
            if not isinstance(editor, PythonEditor) or editor.path is None:
                return
        elif not self.save_file():
            require_qt(self.statusBar()).showMessage("Run cancelled: save failed", 4000)
            return

        args, accepted = QInputDialog.getText(
            self,
            "Run with Arguments",
            "Command-line arguments",
            QLineEdit.EchoMode.Normal,
            "",
        )

        if not accepted:
            return

        self.console_dock.show()
        path = Path(editor.path)
        self.python_runner.run_file_with_args(path, args, cwd=path.parent)
```


**Implementation:** inside `main.py`, replace only `MainWindow.run_with_arguments`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.24 Existing method/function `MainWindow.run_current_file`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1446–1462:**


```python
    def run_current_file(self):
        editor = self._current_python_editor()
        if editor is None:
            return
        if editor.path is None:
            if not self.save_as():
                return
            editor = self.current_editor()
            if not isinstance(editor, PythonEditor) or editor.path is None:
                return
        elif not self.save_file():
            self.statusBar().showMessage("Run cancelled: save failed", 4000)
            return

        self.console_dock.show()
        path = Path(editor.path)
        self.python_runner.run_file(path, cwd=path.parent)
```


**New version:**


```python
    def run_current_file(self):
        """Start the current Python document using the configured runner.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        editor = self._current_python_editor()
        if editor is None:
            return
        if editor.path is None:
            if not self.save_as():
                return
            editor = self.current_editor()
            if not isinstance(editor, PythonEditor) or editor.path is None:
                return
        elif not self.save_file():
            require_qt(self.statusBar()).showMessage("Run cancelled: save failed", 4000)
            return

        self.console_dock.show()
        path = Path(editor.path)
        self.python_runner.run_file(path, cwd=path.parent)
```


**Implementation:** inside `main.py`, replace only `MainWindow.run_current_file`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.25 Existing method/function `MainWindow.choose_interpreter`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1477–1489:**


```python
    def choose_interpreter(self):
        """Let the user pick a Python executable."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose Python Interpreter", "", "Python Executable (python.exe);;All Files (*)"
        )
        if path:
            previous = self.python_runner.interpreter
            self.python_runner.set_interpreter(path)
            self.statusBar().showMessage(f"Python Interpreter: {path}", 3000)
            self._save_interpreter(path)

            if previous != path and hasattr(self, "ruff_lsp_client"):
                self._restart_ruff(path)
```


**New version:**


```python
    def choose_interpreter(self):
        """Let the user pick a Python executable."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose Python Interpreter", "", "Python Executable (python.exe);;All Files (*)"
        )
        if path:
            previous = self.python_runner.interpreter
            self.python_runner.set_interpreter(path)
            require_qt(self.statusBar()).showMessage(f"Python Interpreter: {path}", 3000)
            self._save_interpreter(path)

            if previous != path and hasattr(self, "ruff_lsp_client"):
                self._restart_ruff(path)
```


**Implementation:** inside `main.py`, replace only `MainWindow.choose_interpreter`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.26 Existing method/function `MainWindow.open_settings`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

Fix all four misspelled configuration keys and return a dictionary rather than a one-element tuple. Keep unknown-name, missing-attribute and optional-member checks at error severity. The standard checking profile is an explicit policy change, not proof that every previous warning was false.


**Old version — original lines 1577–1612:**


```python
    def open_settings(self):
        """
        Open the settings dialog and apply the result if Save was hit.

        Flow: build dialog from current values → exec_() blocks until the
        dialog closes → on Accepted, persist and apply. exec_() runs a
        nested event loop, so the main window keeps painting while the
        dialog is open, but no other user code in this method runs until
        the dialog is dismissed (standard modal behaviour).
        """

        # Local import: the dialog module is only needed here, and a
        # local import keeps startup time down and avoids a hard
        # dependency if settings_dialog.py is temporarily broken.
        from code_settings.settings_dialog import SettingsDialog

        dialog = SettingsDialog(self._load_settings(), self)

        if dialog.exec_() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            # Font changes are persisted INTO the active theme.json (its
            # editor.font block) — the theme is the single source of truth.
            # Everything else still goes through _save_settings/QSettings.
            if (new_settings["font_family"], new_settings["font_size"]) != (
                self._current_settings.get("font_family"),
                self._current_settings.get("font_size"),
            ):
                self._write_theme_editor(new_settings["font_family"], new_settings["font_size"])
            self._save_settings(new_settings)

            # ruff_save_mode is cached in __init__; keep the cache in
            # sync so _run_ruff_before_save() sees the new value
            # immediately (no restart needed).
            self.ruff_save_mode = new_settings["ruff_save_mode"]
            self._apply_settings(new_settings)
            self.statusBar().showMessage("Settings saved", 2000)
```


**New version:**


```python
    def open_settings(self):
        """
        Open the settings dialog and apply the result if Save was hit.

        Flow: build dialog from current values → exec_() blocks until the
        dialog closes → on Accepted, persist and apply. exec_() runs a
        nested event loop, so the main window keeps painting while the
        dialog is open, but no other user code in this method runs until
        the dialog is dismissed (standard modal behaviour).
        """

        # Local import: the dialog module is only needed here, and a
        # local import keeps startup time down and avoids a hard
        # dependency if settings_dialog.py is temporarily broken.
        from code_settings.settings_dialog import SettingsDialog

        dialog = SettingsDialog(self._load_settings(), self)

        if dialog.exec_() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            # Font changes are persisted INTO the active theme.json (its
            # editor.font block) — the theme is the single source of truth.
            # Everything else still goes through _save_settings/QSettings.
            if (new_settings["font_family"], new_settings["font_size"]) != (
                self._current_settings.get("font_family"),
                self._current_settings.get("font_size"),
            ):
                self._write_theme_editor(new_settings["font_family"], new_settings["font_size"])
            self._save_settings(new_settings)

            # ruff_save_mode is cached in __init__; keep the cache in
            # sync so _run_ruff_before_save() sees the new value
            # immediately (no restart needed).
            self.ruff_save_mode = new_settings["ruff_save_mode"]
            self._apply_settings(new_settings)
            require_qt(self.statusBar()).showMessage("Settings saved", 2000)
```


**Implementation:** inside `main.py`, replace only `MainWindow.open_settings`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.27 Existing method/function `MainWindow._apply_settings`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

Fix all four misspelled configuration keys and return a dictionary rather than a one-element tuple. Keep unknown-name, missing-attribute and optional-member checks at error severity. The standard checking profile is an explicit policy change, not proof that every previous warning was false.


**Old version — original lines 1614–1637:**


```python
    def _apply_settings(self, settings: dict):
        """
        Push a settings dictionary onto every open editor.

        MultiTabView.all_editors() yields the editors of ALL tab groups
        (both halves of a split view), so one loop covers everything.
        The settings are also cached on self so new tabs opened later
        can inherit them via _apply_editor_settings().
        """
        self._current_settings = settings

        # The dock is created after startup settings; later changes retheme it.
        if hasattr(self, "git_graph"):
            self._apply_git_history_theme(self._theme_path(settings.get("theme")))

        for editor in self.tab_view.all_editors():
            self._apply_editor_settings(editor, settings)

        if settings["interpreter"]:
            previous = self.python_runner.interpreter
            self.python_runner.set_interpreter(settings["interpreter"])
            self.statusBar().showMessage(f"Interpreter: {self.python_runner.interpreter}", 3000)
            if previous != settings["interpreter"] and hasattr(self, "ruff_lsp_client"):
                self._restart_ruff(settings["interpreter"])
```


**New version:**


```python
    def _apply_settings(self, settings: dict):
        """
        Push a settings dictionary onto every open editor.

        MultiTabView.all_editors() yields the editors of ALL tab groups
        (both halves of a split view), so one loop covers everything.
        The settings are also cached on self so new tabs opened later
        can inherit them via _apply_editor_settings().
        """
        self._current_settings = settings

        # The dock is created after startup settings; later changes retheme it.
        if hasattr(self, "git_graph"):
            self._apply_git_history_theme(self._theme_path(settings.get("theme")))

        for editor in self.tab_view.all_editors():
            self._apply_editor_settings(editor, settings)

        if settings["interpreter"]:
            previous = self.python_runner.interpreter
            self.python_runner.set_interpreter(settings["interpreter"])
            require_qt(self.statusBar()).showMessage(f"Interpreter: {self.python_runner.interpreter}", 3000)
            if previous != settings["interpreter"] and hasattr(self, "ruff_lsp_client"):
                self._restart_ruff(settings["interpreter"])
```


**Implementation:** inside `main.py`, replace only `MainWindow._apply_settings`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.28 Existing method/function `MainWindow.set_hacker_mode`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1639–1658:**


```python
    def set_hacker_mode(self, on: bool):
        """
        C17: the full bundle - CRT theme + sanlines in one switch.

        Reuses the settings machinery delliberately: theme switching, lexer recreation,
        thr margin color, fix and per-editor application were already built and debugged.
        Never write a second theme pipeline when one exists.

        :param on: True = hacker.json + scanlines; False = default theme
        """
        if on and not self._hacker:
            self._pre_hacker_theme = self.settings.value("theme", "theme.json", type=str)

        self._hacker = bool(on)
        self._set_scanlines_visible(self._hacker)
        settings = self._load_settings()
        settings["theme"] = "hacker.json" if self._hacker else self._pre_hacker_theme
        self._save_settings(settings)
        self._apply_settings(settings)
        self.statusBar().showMessage("HACK THE PLANET" if on else "Back to reality", 2500)
```


**New version:**


```python
    def set_hacker_mode(self, on: bool):
        """
        C17: the full bundle - CRT theme + sanlines in one switch.

        Reuses the settings machinery delliberately: theme switching, lexer recreation,
        thr margin color, fix and per-editor application were already built and debugged.
        Never write a second theme pipeline when one exists.

        :param on: True = hacker.json + scanlines; False = default theme
        """
        if on and not self._hacker:
            self._pre_hacker_theme = self.settings.value("theme", "theme.json", type=str)

        self._hacker = bool(on)
        self._set_scanlines_visible(self._hacker)
        settings = self._load_settings()
        settings["theme"] = "hacker.json" if self._hacker else self._pre_hacker_theme
        self._save_settings(settings)
        self._apply_settings(settings)
        require_qt(self.statusBar()).showMessage("HACK THE PLANET" if on else "Back to reality", 2500)
```


**Implementation:** inside `main.py`, replace only `MainWindow.set_hacker_mode`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.29 Existing method/function `MainWindow._write_theme_editor`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1709–1754:**


```python
    def _write_theme_editor(self, font_family: str, font_size: int) -> None:
        """
        Persist a font change INTO the active theme.json.

        This is the write side of the theme-as-source-of-truth model the
        user chose: the Settings dialog edits the theme file itself, so a
        font choice belongs to that theme and switching themes switches
        the font with it. Family and size are written to the GLOBAL
        editor.font block; per-style italic/weight in the syntax section
        are untouched.

        :param font_family: e.g. "JetBrains Mono"
        :param font_size: point size
        """

        source = self._active_theme_path()
        if not source:
            return

        theme_name = self.settings.value("theme", "theme.json", type=str)
        config_root = (
            Path(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)) / "themes"
        )
        config_root.mkdir(parents=True, exist_ok=True)
        path = config_root / theme_name
        if not path.exists():
            shutil.copy2(source, path)

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            editor = data.setdefault("theme", {}).setdefault("editor", {})
            editor.setdefault("font", {})
            editor["font"]["family"] = font_family
            editor["font"]["font-size"] = int(font_size)
            temporary = path.with_suffix(path.suffix + ".tmp")
            with open(temporary, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, path)

        except (OSError, json.JSONDecodeError) as e:
            if "temporary" in locals():
                temporary.unlink(missing_ok=True)
            self.statusBar().showMessage(f"Could not write theme: {e}", 4000)
```


**New version:**


```python
    def _write_theme_editor(self, font_family: str, font_size: int) -> None:
        """
        Persist a font change INTO the active theme.json.

        This is the write side of the theme-as-source-of-truth model the
        user chose: the Settings dialog edits the theme file itself, so a
        font choice belongs to that theme and switching themes switches
        the font with it. Family and size are written to the GLOBAL
        editor.font block; per-style italic/weight in the syntax section
        are untouched.

        :param font_family: e.g. "JetBrains Mono"
        :param font_size: point size
        """

        source = self._active_theme_path()
        if not source:
            return

        theme_name = self.settings.value("theme", "theme.json", type=str)
        config_root = (
            Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)) / "themes"
        )
        config_root.mkdir(parents=True, exist_ok=True)
        path = config_root / theme_name
        if not path.exists():
            shutil.copy2(source, path)

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            editor = data.setdefault("theme", {}).setdefault("editor", {})
            editor.setdefault("font", {})
            editor["font"]["family"] = font_family
            editor["font"]["font-size"] = int(font_size)
            temporary = path.with_suffix(path.suffix + ".tmp")
            with open(temporary, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, path)

        except (OSError, json.JSONDecodeError) as e:
            if "temporary" in locals():
                temporary.unlink(missing_ok=True)
            require_qt(self.statusBar()).showMessage(f"Could not write theme: {e}", 4000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._write_theme_editor`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.30 Existing method/function `MainWindow._theme_path`

Return a user override or packaged theme path. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 1756–1777:**


```python
    def _theme_path(self, theme_name):
        """
        Return a user override or packaged theme path.

        User-edited themes in the platform configuration directory take
        precedence. Otherwise the immutable JSON shipped in
        ``markdowneditor_assets/themes`` is used.
        """

        if not theme_name:
            return None

        user_candidate = (
            Path(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation))
            / "themes"
            / theme_name
        )

        if user_candidate.is_file():
            return str(user_candidate)
        packaged = Path(asset_path(f"themes/{theme_name}"))
        return str(packaged) if packaged.is_file() else None
```


**New version:**


```python
    def _theme_path(self, theme_name):
        """
        Return a user override or packaged theme path.

        User-edited themes in the platform configuration directory take
        precedence. Otherwise the immutable JSON shipped in
        ``markdowneditor_assets/themes`` is used.
        """

        if not theme_name:
            return None

        user_candidate = (
            Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation))
            / "themes"
            / theme_name
        )

        if user_candidate.is_file():
            return str(user_candidate)
        packaged = Path(asset_path(f"themes/{theme_name}"))
        return str(packaged) if packaged.is_file() else None
```


**Implementation:** inside `main.py`, replace only `MainWindow._theme_path`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.31 Existing method/function `MainWindow.set_new_tab`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1871–1940:**


```python
    def set_new_tab(
        self,
        path: Path,
        is_new_file=False,
        target_group=None,
        is_python_file=None,
    ):
        """Open one UTF-8 document without corrupting or duplicating it.
        Binary probing, symlink resolution, byte reading, and strict decoding
        are one I/O transaction. Every expected filesystem/encoding failure is
        converted to a user-visible dialog instead of escaping a Qt slot.
        """
        path = Path(path) if path is not None else None
        if is_new_file:
            return self.new_file(target_group=target_group)

        if path is None or not path.is_file():
            return None

        existing = self.tab_view.find_editor_by_path(path)
        if existing is not None:
            self.tab_view.focus_editor(existing)
            return existing
        try:
            if self.is_binary(path):
                self.statusBar().showMessage("Cannot open binary file", 2_000)
                return None

            # Keep the logical path on the tab, but read/write the target when
            # the logical path is a symlink so saving does not replace the link.
            target = save_target(path)
            raw = target.read_bytes()
            has_bom = raw.startswith(UTF8_BOM)
            text = raw.decode("utf-8-sig")

        except (OSError, UnicodeDecodeError) as error:
            QMessageBox.critical(self, "Open File", f"Could not open '{path}':\n{error}")
            return None

        editor = self.get_editor(path=path, is_python_file=is_python_file)
        editor._utf8_bom = has_bom
        editor._disk_digest = hashlib.sha256(raw).digest()
        editor._save_target = target

        # Preserve the dominant existing EOL convention rather than converting
        # the entire file merely because it was opened and saved.
        crlf_count = raw.count(b"\r\n")
        lf_count = raw.count(b"\n") - crlf_count
        cr_count = raw.count(b"\r") - crlf_count

        if crlf_count >= max(lf_count, cr_count) and crlf_count:
            editor.setEolMode(QsciScintilla.EolWindows)

        elif cr_count > max(crlf_count, lf_count):
            editor.setEolMode(QsciScintilla.EolMac)

        else:
            editor.setEolMode(QsciScintilla.EolUnix)

        editor.setTextSafely(text)
        self._connect_editor(editor)
        self.tab_view.add_editor(editor, path.name, target_group)
        self.tab_view.set_editor_tooltip(editor, str(path.absolute()))
        self.current_file = path
        self._add_to_recent_files(str(path))
        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.outline_tree.clear()
        return editor
```


**New version:**


```python
    def set_new_tab(
        self,
        path: Path,
        is_new_file=False,
        target_group=None,
        is_python_file=None,
    ):
        """Open one UTF-8 document without corrupting or duplicating it.
        Binary probing, symlink resolution, byte reading, and strict decoding
        are one I/O transaction. Every expected filesystem/encoding failure is
        converted to a user-visible dialog instead of escaping a Qt slot.
        """
        path = Path(path) if path is not None else None
        if is_new_file:
            return self.new_file(target_group=target_group)

        if path is None or not path.is_file():
            return None

        existing = self.tab_view.find_editor_by_path(path)
        if existing is not None:
            self.tab_view.focus_editor(existing)
            return existing
        try:
            if self.is_binary(path):
                require_qt(self.statusBar()).showMessage("Cannot open binary file", 2_000)
                return None

            # Keep the logical path on the tab, but read/write the target when
            # the logical path is a symlink so saving does not replace the link.
            target = save_target(path)
            raw = target.read_bytes()
            has_bom = raw.startswith(UTF8_BOM)
            text = raw.decode("utf-8-sig")

        except (OSError, UnicodeDecodeError) as error:
            QMessageBox.critical(self, "Open File", f"Could not open '{path}':\n{error}")
            return None

        editor = self.get_editor(path=path, is_python_file=is_python_file)
        editor._utf8_bom = has_bom
        editor._disk_digest = hashlib.sha256(raw).digest()
        editor._save_target = target

        # Preserve the dominant existing EOL convention rather than converting
        # the entire file merely because it was opened and saved.
        crlf_count = raw.count(b"\r\n")
        lf_count = raw.count(b"\n") - crlf_count
        cr_count = raw.count(b"\r") - crlf_count

        if crlf_count >= max(lf_count, cr_count) and crlf_count:
            editor.setEolMode(QsciScintilla.EolWindows)

        elif cr_count > max(crlf_count, lf_count):
            editor.setEolMode(QsciScintilla.EolMac)

        else:
            editor.setEolMode(QsciScintilla.EolUnix)

        editor.setTextSafely(text)
        self._connect_editor(editor)
        self.tab_view.add_editor(editor, path.name, target_group)
        self.tab_view.set_editor_tooltip(editor, str(path.absolute()))
        self.current_file = path
        self._add_to_recent_files(str(path))
        if isinstance(editor, PythonEditor):
            self.outline_tree.update_outline(editor.text())
        else:
            self.outline_tree.clear()
        return editor
```


**Implementation:** inside `main.py`, replace only `MainWindow.set_new_tab`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.32 Existing method/function `MainWindow.get_frame`

Return a borderless frame using the shared panel stylesheet. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 1942–1959:**


```python
    def get_frame(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame.setFrameShadow(QFrame.Plain)
        frame.setContentsMargins(0, 0, 0, 0)
        frame.setStyleSheet("""
            QFrame {
                background-color: #1e1f22;
                border-radius: 0px;
                border: none;
                padding: 5px;
                color: #D3D3D3;
            }
            QFrame::hover {
                color: white;
            }
        """)
        return frame
```


**New version:**


```python
    def get_frame(self) -> QFrame:
        """Return a borderless frame using the shared panel stylesheet.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.NoFrame)
        frame.setFrameShadow(QFrame.Shadow.Plain)
        frame.setContentsMargins(0, 0, 0, 0)
        frame.setStyleSheet("""
            QFrame {
                background-color: #1e1f22;
                border-radius: 0px;
                border: none;
                padding: 5px;
                color: #D3D3D3;
            }
            QFrame::hover {
                color: white;
            }
        """)
        return frame
```


**Implementation:** inside `main.py`, replace only `MainWindow.get_frame`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.33 Existing method/function `MainWindow.set_up_body`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 1961–2120:**


```python
    def set_up_body(self):
        """Build the editor layout and sidebar navigation/action icons."""
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.Shape.NoFrame)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body_frame.setLayout(body)
        self.tab_view = MultiTabView(self)
        self.tab_view.setContentsMargins(0, 0, 0, 0)
        self.tab_view.currentEditorChanged.connect(self._on_current_editor_changed)
        self.tab_view.closeEditorRequested.connect(self.close_editor)

        # BUGFIX: the tab context menu was never wired up - connect it here.
        self.tab_view.tabContextMenuRequested.connect(self._show_tab_context_menu)

        # editor_container = QWidget()
        # editor_layout = QStackedWidget(editor_container)
        self.preview = QWebEngineView()

        # --- Setup for the Sidebar
        self.side_bar = QFrame()
        self.side_bar.setFrameShape(QFrame.Shape.StyledPanel)
        self.side_bar.setFrameShadow(QFrame.Shadow.Plain)
        self.side_bar.setStyleSheet(f"""
            background-color: {"#1e1f22"};
        """)
        side_bar_layout = QVBoxLayout()
        side_bar_layout.setContentsMargins(5, 15, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        # --- Setup for labels
        self.sidebar_labels = {}
        folder_label = self.get_sidebar_label(resource_path("icons/folder-active.png"), "folder")
        self.sidebar_labels["folder"] = folder_label
        side_bar_layout.addWidget(folder_label)
        search_label = self.get_sidebar_label(resource_path("icons/search.png"), "search")
        self.sidebar_labels["search"] = search_label
        side_bar_layout.addWidget(search_label)
        self.side_bar.setLayout(side_bar_layout)
        outline_label = self.get_sidebar_label(resource_path("icons/outline.png"), "outline")
        self.sidebar_labels["outline"] = outline_label
        side_bar_layout.addWidget(outline_label)
        terminal_label = self.get_sidebar_label(resource_path("icons/terminal.png"), "terminal")
        self.sidebar_labels["terminal"] = terminal_label
        side_bar_layout.addWidget(terminal_label)

        # Reuse the existing assets; these are actions, not side-panel pages.

        for name in ("console", "settings"):
            label = self.get_sidebar_label(resource_path(f"icons/{name}.png"), name)
            self.sidebar_labels[name] = label
            side_bar_layout.addWidget(label)
        self.outline_tree = CodeOutlineTree()
        self.outline_tree.symbol_clicked.connect(self._goto_symbol)
        self.outline_frame = self.get_frame()
        outline_layout = QVBoxLayout()
        outline_layout.setContentsMargins(0, 0, 0, 0)
        outline_layout.setSpacing(0)
        outline_label = QLabel("Outline")
        outline_label.setStyleSheet("color: #636d83; padding: 4px 8px; font-size: 12px;")
        outline_layout.addWidget(outline_label)
        outline_layout.addWidget(self.outline_tree)
        self.outline_frame.setLayout(outline_layout)

        # split view
        self.hs_split = QSplitter(Qt.Orientation.Horizontal)

        # --- Frame and layout to hold the tree view (FILE MANAGER)
        self.file_manager_frame = self.get_frame()
        self.file_manager_layout = QVBoxLayout()
        self.file_manager_layout.setContentsMargins(0, 0, 0, 0)
        self.file_manager_layout.setSpacing(0)
        self.file_manager = FileManager(
            set_new_tab=self.set_new_tab,
            main_window=self,
            parent=self,
        )

        # setup layout
        self.file_manager_layout.addWidget(self.file_manager)
        self.file_manager_frame.setLayout(self.file_manager_layout)

        # search manager
        self.search_frame = self.get_frame()
        search_layout = QVBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_layout.setContentsMargins(0, 10, 0, 0)
        search_layout.setSpacing(0)
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search")
        search_input.setFont(self.window_font)
        self.search_checkbox = QCheckBox("Include hidden module folders")
        self.search_regex_checkbox = QCheckBox("Regex")
        self.search_case_checkbox = QCheckBox("Case sensitive")

        for checkbox in (
            self.search_checkbox,
            self.search_regex_checkbox,
            self.search_case_checkbox,
        ):
            checkbox.setFont(self.window_font)
        self.search_worker = SearchWorker()
        self.search_worker.results_ready.connect(self.search_finished)
        self.search_worker.search_error.connect(self.search_failed)

        def request_search():
            self.search_worker.update(
                search_input.text(),
                self.file_manager.model.rootPath(),
                self.search_checkbox.isChecked(),
                self.search_regex_checkbox.isChecked(),
                self.search_case_checkbox.isChecked(),
            )

        search_input.textChanged.connect(lambda _text: request_search())
        self.search_checkbox.toggled.connect(lambda _on: request_search())
        self.search_regex_checkbox.toggled.connect(lambda _on: request_search())
        self.search_case_checkbox.toggled.connect(lambda _on: request_search())
        self.search_list_view = QListWidget()
        self.search_list_view.setFont(QFont("sans-serif", 13))
        self.search_list_view.setStyleSheet("""
        QListWidget {
            background-color: #21252b;
            border-radius: 5px;
            border: 1px solid #D3D3D3;
            padding: 5px;
            color: #D3D3D3;
        }
        """)
        self.search_list_view.itemClicked.connect(self.search_list_view_clicked)
        search_layout.addWidget(self.search_checkbox)
        search_layout.addWidget(self.search_regex_checkbox)
        search_layout.addWidget(self.search_case_checkbox)
        search_layout.addWidget(search_input)
        search_layout.addSpacerItem(QSpacerItem(5, 5, QSizePolicy.Minimum, QSizePolicy.Minimum))
        search_layout.addWidget(self.search_list_view)
        self.search_frame.setLayout(search_layout)

        # --- Side panel: QStackedWidget so only one panel is visible at a time ---
        self.side_panel = QStackedWidget()
        self.side_panel.setMinimumWidth(280)  # was 200 — too narrow
        self.side_panel.setMaximumWidth(450)  # was 400 — give more room
        self.side_panel.addWidget(self.file_manager_frame)
        self.side_panel.addWidget(self.search_frame)
        self.side_panel.addWidget(self.outline_frame)
        body.addWidget(self.side_bar)
        self.hs_split.addWidget(self.side_panel)
        self.hs_split.addWidget(self.tab_view)
        self.hs_split.addWidget(self.preview)
        self.hs_split.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hs_split.setSizes([300, 550, 550])
        body.addWidget(self.hs_split)
        body_frame.setLayout(body)
        self.setCentralWidget(body_frame)
```


**New version:**


```python
    def set_up_body(self):
        """Build the editor layout and sidebar navigation/action icons."""
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.Shape.NoFrame)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body_frame.setLayout(body)
        self.tab_view = MultiTabView(self)
        self.tab_view.setContentsMargins(0, 0, 0, 0)
        self.tab_view.currentEditorChanged.connect(self._on_current_editor_changed)
        self.tab_view.closeEditorRequested.connect(self.close_editor)

        # BUGFIX: the tab context menu was never wired up - connect it here.
        self.tab_view.tabContextMenuRequested.connect(self._show_tab_context_menu)

        # editor_container = QWidget()
        # editor_layout = QStackedWidget(editor_container)
        self.preview = QWebEngineView()

        # --- Setup for the Sidebar
        self.side_bar = QFrame()
        self.side_bar.setFrameShape(QFrame.Shape.StyledPanel)
        self.side_bar.setFrameShadow(QFrame.Shadow.Plain)
        self.side_bar.setStyleSheet(f"""
            background-color: {"#1e1f22"};
        """)
        side_bar_layout = QVBoxLayout()
        side_bar_layout.setContentsMargins(5, 15, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(qt_flags(Qt.Alignment, Qt.AlignmentFlag.AlignTop, Qt.AlignmentFlag.AlignCenter))

        # --- Setup for labels
        self.sidebar_labels = {}
        folder_label = self.get_sidebar_label(resource_path("icons/folder-active.png"), "folder")
        self.sidebar_labels["folder"] = folder_label
        side_bar_layout.addWidget(folder_label)
        search_label = self.get_sidebar_label(resource_path("icons/search.png"), "search")
        self.sidebar_labels["search"] = search_label
        side_bar_layout.addWidget(search_label)
        self.side_bar.setLayout(side_bar_layout)
        outline_label = self.get_sidebar_label(resource_path("icons/outline.png"), "outline")
        self.sidebar_labels["outline"] = outline_label
        side_bar_layout.addWidget(outline_label)
        terminal_label = self.get_sidebar_label(resource_path("icons/terminal.png"), "terminal")
        self.sidebar_labels["terminal"] = terminal_label
        side_bar_layout.addWidget(terminal_label)

        # Reuse the existing assets; these are actions, not side-panel pages.

        for name in ("console", "settings"):
            label = self.get_sidebar_label(resource_path(f"icons/{name}.png"), name)
            self.sidebar_labels[name] = label
            side_bar_layout.addWidget(label)
        self.outline_tree = CodeOutlineTree()
        self.outline_tree.symbol_clicked.connect(self._goto_symbol)
        self.outline_frame = self.get_frame()
        outline_layout = QVBoxLayout()
        outline_layout.setContentsMargins(0, 0, 0, 0)
        outline_layout.setSpacing(0)
        outline_label = QLabel("Outline")
        outline_label.setStyleSheet("color: #636d83; padding: 4px 8px; font-size: 12px;")
        outline_layout.addWidget(outline_label)
        outline_layout.addWidget(self.outline_tree)
        self.outline_frame.setLayout(outline_layout)

        # split view
        self.hs_split = QSplitter(Qt.Orientation.Horizontal)

        # --- Frame and layout to hold the tree view (FILE MANAGER)
        self.file_manager_frame = self.get_frame()
        self.file_manager_layout = QVBoxLayout()
        self.file_manager_layout.setContentsMargins(0, 0, 0, 0)
        self.file_manager_layout.setSpacing(0)
        self.file_manager = FileManager(
            set_new_tab=self.set_new_tab,
            main_window=self,
            parent=self,
        )

        # setup layout
        self.file_manager_layout.addWidget(self.file_manager)
        self.file_manager_frame.setLayout(self.file_manager_layout)

        # search manager
        self.search_frame = self.get_frame()
        search_layout = QVBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_layout.setContentsMargins(0, 10, 0, 0)
        search_layout.setSpacing(0)
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search")
        search_input.setFont(self.window_font)
        self.search_checkbox = QCheckBox("Include hidden module folders")
        self.search_regex_checkbox = QCheckBox("Regex")
        self.search_case_checkbox = QCheckBox("Case sensitive")

        for checkbox in (
            self.search_checkbox,
            self.search_regex_checkbox,
            self.search_case_checkbox,
        ):
            checkbox.setFont(self.window_font)
        self.search_worker = SearchWorker()
        self.search_worker.results_ready.connect(self.search_finished)
        self.search_worker.search_error.connect(self.search_failed)

        def request_search():
            """Submit the query, filesystem root and search options to the worker.

            Read the root from fs_model. The inherited QTreeView.model() method
            remains callable and is no longer hidden by an instance attribute.
            """
            self.search_worker.update(
                search_input.text(),
                self.file_manager.fs_model.rootPath(),
                self.search_checkbox.isChecked(),
                self.search_regex_checkbox.isChecked(),
                self.search_case_checkbox.isChecked(),
            )

        search_input.textChanged.connect(lambda _text: request_search())
        self.search_checkbox.toggled.connect(lambda _on: request_search())
        self.search_regex_checkbox.toggled.connect(lambda _on: request_search())
        self.search_case_checkbox.toggled.connect(lambda _on: request_search())
        self.search_list_view = QListWidget()
        self.search_list_view.setFont(QFont("sans-serif", 13))
        self.search_list_view.setStyleSheet("""
        QListWidget {
            background-color: #21252b;
            border-radius: 5px;
            border: 1px solid #D3D3D3;
            padding: 5px;
            color: #D3D3D3;
        }
        """)
        self.search_list_view.itemClicked.connect(self.search_list_view_clicked)
        search_layout.addWidget(self.search_checkbox)
        search_layout.addWidget(self.search_regex_checkbox)
        search_layout.addWidget(self.search_case_checkbox)
        search_layout.addWidget(search_input)
        search_layout.addSpacerItem(QSpacerItem(5, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        search_layout.addWidget(self.search_list_view)
        self.search_frame.setLayout(search_layout)

        # --- Side panel: QStackedWidget so only one panel is visible at a time ---
        self.side_panel = QStackedWidget()
        self.side_panel.setMinimumWidth(280)  # was 200 — too narrow
        self.side_panel.setMaximumWidth(450)  # was 400 — give more room
        self.side_panel.addWidget(self.file_manager_frame)
        self.side_panel.addWidget(self.search_frame)
        self.side_panel.addWidget(self.outline_frame)
        body.addWidget(self.side_bar)
        self.hs_split.addWidget(self.side_panel)
        self.hs_split.addWidget(self.tab_view)
        self.hs_split.addWidget(self.preview)
        self.hs_split.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hs_split.setSizes([300, 550, 550])
        body.addWidget(self.hs_split)
        body_frame.setLayout(body)
        self.setCentralWidget(body_frame)
```


**Implementation:** inside `main.py`, replace only `MainWindow.set_up_body`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.34 Existing method/function `MainWindow._show_tab_context_menu`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2135–2173:**


```python
    def _show_tab_context_menu(self, group, pos: QPoint):
        """
        Show a context menu when the user right-clicks a tab.
        `group` is the QTabWidget (tab group) the click happened in,
        `pos` is the click position in that group's coordinates.
        """
        tab_bar = group.tabBar()

        # Convert the click position from QTabWidget coords to QTabBar coords
        bar_pos = tab_bar.mapFrom(group, pos)
        index = tab_bar.tabAt(bar_pos)

        if index < 0:
            # User clicked somewhere that's not a tab (e.g. the empty space after tabs)
            return

        editor = group.widget(index)
        if editor is None:
            return

        menu = QMenu(self)
        close_action = menu.addAction("Close")
        close_others_action = menu.addAction("Close Others")
        close_all_action = menu.addAction("Close All")
        menu.addSeparator()
        copy_path_action = menu.addAction("Copy Path")
        reveal_action = menu.addAction("Reveal in File Manager")
        action = menu.exec_(group.mapToGlobal(pos))

        if action == close_action:
            self.close_editor(editor)
        elif action == close_others_action:
            self._close_other_tabs(editor)
        elif action == close_all_action:
            self._close_all_tabs()
        elif action == copy_path_action:
            self._copy_tab_path(editor)
        elif action == reveal_action:
            self._reveal_tab_in_file_manager(editor)
```


**New version:**


```python
    def _show_tab_context_menu(self, group, pos: QPoint):
        """
        Show a context menu when the user right-clicks a tab.
        `group` is the QTabWidget (tab group) the click happened in,
        `pos` is the click position in that group's coordinates.
        """
        tab_bar = group.tabBar()

        # Convert the click position from QTabWidget coords to QTabBar coords
        bar_pos = tab_bar.mapFrom(group, pos)
        index = tab_bar.tabAt(bar_pos)

        if index < 0:
            # User clicked somewhere that's not a tab (e.g. the empty space after tabs)
            return

        editor = group.widget(index)
        if editor is None:
            return

        menu = QMenu(self)
        close_action = require_qt(menu.addAction("Close"))
        close_others_action = require_qt(menu.addAction("Close Others"))
        close_all_action = require_qt(menu.addAction("Close All"))
        menu.addSeparator()
        copy_path_action = require_qt(menu.addAction("Copy Path"))
        reveal_action = require_qt(menu.addAction("Reveal in File Manager"))
        action = menu.exec_(group.mapToGlobal(pos))

        if action == close_action:
            self.close_editor(editor)
        elif action == close_others_action:
            self._close_other_tabs(editor)
        elif action == close_all_action:
            self._close_all_tabs()
        elif action == copy_path_action:
            self._copy_tab_path(editor)
        elif action == reveal_action:
            self._reveal_tab_in_file_manager(editor)
```


**Implementation:** inside `main.py`, replace only `MainWindow._show_tab_context_menu`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.35 Existing method/function `MainWindow._copy_tab_path`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2190–2195:**


```python
    def _copy_tab_path(self, editor):
        """Copy the file path of the tab's editor to the clipboard."""
        path = getattr(editor, "path", None)
        if path is not None:
            QApplication.clipboard().setText(str(path))
            self.statusBar().showMessage(f"Copied: {path}", 2000)
```


**New version:**


```python
    def _copy_tab_path(self, editor):
        """Copy the file path of the tab's editor to the clipboard."""
        path = getattr(editor, "path", None)
        if path is not None:
            QApplication.clipboard().setText(str(path))
            require_qt(self.statusBar()).showMessage(f"Copied: {path}", 2000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._copy_tab_path`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.36 Existing method/function `MainWindow.set_cursor_pointer`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 2230–2231:**


```python
    def set_cursor_pointer(self, e):
        self.setCursor(Qt.PointingHandCursor)
```


**New version:**


```python
    def set_cursor_pointer(self, e):
        """Select the pointing-hand cursor when the control is entered.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self.setCursor(Qt.CursorShape.PointingHandCursor)
```


**Implementation:** inside `main.py`, replace only `MainWindow.set_cursor_pointer`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.37 Existing method/function `MainWindow.set_cursor_arrow`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 2233–2234:**


```python
    def set_cursor_arrow(self, e):
        self.setCursor(Qt.ArrowCursor)
```


**New version:**


```python
    def set_cursor_arrow(self, e):
        """Restore the arrow cursor when the control is left.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self.setCursor(Qt.CursorShape.ArrowCursor)
```


**Implementation:** inside `main.py`, replace only `MainWindow.set_cursor_arrow`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.38 Existing method/function `MainWindow.search_finished`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2236–2243:**


```python
    def search_finished(self, generation, items, truncated):
        if generation != self.search_worker.generation:
            return
        self.search_list_view.clear()
        for item in items:
            self.search_list_view.addItem(item)
        if truncated:
            self.statusBar().showMessage(f"Search limited to {len(items)} results", 4000)
```


**New version:**


```python
    def search_finished(self, generation, items, truncated):
        """Present completed project-search results in the search panel.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if generation != self.search_worker.generation:
            return
        self.search_list_view.clear()
        for item in items:
            self.search_list_view.addItem(item)
        if truncated:
            require_qt(self.statusBar()).showMessage(f"Search limited to {len(items)} results", 4000)
```


**Implementation:** inside `main.py`, replace only `MainWindow.search_finished`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.39 Existing method/function `MainWindow.search_failed`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2245–2248:**


```python
    def search_failed(self, generation, message):
        if generation == self.search_worker.generation:
            self.search_list_view.clear()
            self.statusBar().showMessage(f"Invalid search: {message}", 4000)
```


**New version:**


```python
    def search_failed(self, generation, message):
        """Report an asynchronous project-search failure in the status bar.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if generation == self.search_worker.generation:
            self.search_list_view.clear()
            require_qt(self.statusBar()).showMessage(f"Invalid search: {message}", 4000)
```


**Implementation:** inside `main.py`, replace only `MainWindow.search_failed`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.40 Existing method/function `MainWindow.close_editor`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.


**Old version — original lines 2259–2285:**


```python
    def close_editor(self, editor):
        if editor is None:
            return

        if editor in self._dirty_editors:
            path = getattr(editor, "path", None)
            name = path.name if path is not None else "Untitled"
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save Changes to '{name}'?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if reply == QMessageBox.Cancel:
                return False
            if reply == QMessageBox.Save:
                self.tab_view.focus_editor(editor)
                if not self.save_file():
                    return False

        self._dirty_editors.discard(editor)
        self.tab_view.remove_editor(editor)
        self._dispose_editor(editor)
        self.render_preview()
        return True
```


**New version:**


```python
    def close_editor(self, editor):
        """Close an editor through the existing unsaved-change and retirement flow.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if editor is None:
            return

        if editor in self._dirty_editors:
            path = getattr(editor, "path", None)
            name = path.name if path is not None else "Untitled"
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save Changes to '{name}'?",
                qt_flags(QMessageBox.StandardButtons, QMessageBox.StandardButton.Save, QMessageBox.StandardButton.Discard, QMessageBox.StandardButton.Cancel),
                QMessageBox.StandardButton.Save,
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return False
            if reply == QMessageBox.StandardButton.Save:
                self.tab_view.focus_editor(editor)
                if not self.save_file():
                    return False

        self._dirty_editors.discard(editor)
        self.tab_view.remove_editor(editor)
        self._dispose_editor(editor)
        self.render_preview()
        return True
```


**Implementation:** inside `main.py`, replace only `MainWindow.close_editor`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.41 Existing method/function `MainWindow.can_close_editors_for_path`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.


**Old version — original lines 2377–2397:**


```python
    def can_close_editors_for_path(self, target_path, is_directory=False):
        """Collect save/discard decisions without removing tabs."""

        for editor in self.editors_for_path(target_path, is_directory):
            if editor not in self._dirty_editors:
                continue
            self.tab_view.focus_editor(editor)
            name = Path(editor.path).name
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to '{name}'?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply == QMessageBox.Cancel:
                return False
            if reply == QMessageBox.Save and not self.save_file():
                return False

        return True
```


**New version:**


```python
    def can_close_editors_for_path(self, target_path, is_directory=False):
        """Collect save/discard decisions without removing tabs."""

        for editor in self.editors_for_path(target_path, is_directory):
            if editor not in self._dirty_editors:
                continue
            self.tab_view.focus_editor(editor)
            name = Path(editor.path).name
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Save changes to '{name}'?",
                qt_flags(QMessageBox.StandardButtons, QMessageBox.StandardButton.Save, QMessageBox.StandardButton.Discard, QMessageBox.StandardButton.Cancel),
                QMessageBox.StandardButton.Save,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return False
            if reply == QMessageBox.StandardButton.Save and not self.save_file():
                return False

        return True
```


**Implementation:** inside `main.py`, replace only `MainWindow.can_close_editors_for_path`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.42 Existing method/function `MainWindow.show_hide_tab`

Dispatch left-clicks to tool actions or the three sidebar pages. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 2409–2473:**


```python
    def show_hide_tab(self, e, type_):
        """Dispatch left-clicks to tool actions or the three sidebar pages."""
        if e.button() != Qt.LeftButton:
            return

        # Return before changing page icons: opening a dock is independen of
        # the currently selected Folder/Search/Outline page.
        if type_ in ("terminal", "console"):
            dock = self.terminal_dock if type_ == "terminal" else self.console_dock
            dock.show()
            dock.raise_()
            if type_ == "terminal":
                self.terminal.output.setFocus()
            return

        if type_ == "settings":
            self._set_sidebar_icon("settings", True)
            try:
                self.open_settings()
            finally:
                self._set_sidebar_icon("settings", False)
            return

        panels = {
            "folder": self.file_manager_frame,
            "search": self.search_frame,
            "outline": self.outline_frame,
        }

        # Update icon states. Reset all to gray, then set active to blue
        icon_map = {
            "folder": (resource_path("icons/folder.png"), resource_path("icons/folder-active.png")),
            "search": (resource_path("icons/search.png"), resource_path("icons/search-active.png")),
            "outline": (
                resource_path("icons/outline.png"),
                resource_path("icons/outline-active.png"),
            ),
        }

        # Reset all sidebar icons to inactive gray
        for name, (inactive, active) in icon_map.items():
            label = self.sidebar_labels.get(name)
            if label:
                label.setPixmap(QPixmap(inactive).scaled(QSize(25, 25)))

        target = panels.get(type_)
        if target is None:
            return

        # If the target panel is already showing, hide the side panel
        if self.side_panel.isVisible() and self.side_panel.currentWidget() is target:
            # Clicking the active panel hiddes is, resets to gray
            self.side_panel.hide()
            return

        # Otherwise, switch to the target panel and show it
        self.side_panel.setCurrentWidget(target)
        self.side_panel.show()
        label = self.sidebar_labels.get(type_)
        if label:
            label.setPixmap(QPixmap(icon_map[type_][1]).scaled(QSize(25, 25)))
        # Restore splitter sizes if the side panel was hidden (width 0)
        sizes = self.hs_split.sizes()
        if sizes and sizes[0] == 0:
            self.hs_split.setSizes([300, 550, 550])
```


**New version:**


```python
    def show_hide_tab(self, e, type_):
        """Dispatch left-clicks to tool actions or the three sidebar pages."""
        if e.button() != Qt.MouseButton.LeftButton:
            return

        # Return before changing page icons: opening a dock is independen of
        # the currently selected Folder/Search/Outline page.
        if type_ in ("terminal", "console"):
            dock = self.terminal_dock if type_ == "terminal" else self.console_dock
            dock.show()
            dock.raise_()
            if type_ == "terminal":
                self.terminal.output.setFocus()
            return

        if type_ == "settings":
            self._set_sidebar_icon("settings", True)
            try:
                self.open_settings()
            finally:
                self._set_sidebar_icon("settings", False)
            return

        panels = {
            "folder": self.file_manager_frame,
            "search": self.search_frame,
            "outline": self.outline_frame,
        }

        # Update icon states. Reset all to gray, then set active to blue
        icon_map = {
            "folder": (resource_path("icons/folder.png"), resource_path("icons/folder-active.png")),
            "search": (resource_path("icons/search.png"), resource_path("icons/search-active.png")),
            "outline": (
                resource_path("icons/outline.png"),
                resource_path("icons/outline-active.png"),
            ),
        }

        # Reset all sidebar icons to inactive gray
        for name, (inactive, active) in icon_map.items():
            label = self.sidebar_labels.get(name)
            if label:
                label.setPixmap(QPixmap(inactive).scaled(QSize(25, 25)))

        target = panels.get(type_)
        if target is None:
            return

        # If the target panel is already showing, hide the side panel
        if self.side_panel.isVisible() and self.side_panel.currentWidget() is target:
            # Clicking the active panel hiddes is, resets to gray
            self.side_panel.hide()
            return

        # Otherwise, switch to the target panel and show it
        self.side_panel.setCurrentWidget(target)
        self.side_panel.show()
        label = self.sidebar_labels.get(type_)
        if label:
            label.setPixmap(QPixmap(icon_map[type_][1]).scaled(QSize(25, 25)))
        # Restore splitter sizes if the side panel was hidden (width 0)
        sizes = self.hs_split.sizes()
        if sizes and sizes[0] == 0:
            self.hs_split.setSizes([300, 550, 550])
```


**Implementation:** inside `main.py`, replace only `MainWindow.show_hide_tab`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.43 Existing method/function `MainWindow.new_file`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2477–2485:**


```python
    def new_file(self, target_group=None):
        """Create an untitled editor in the active group."""
        editor = self.get_editor()
        self._connect_editor(editor)
        self.tab_view.add_editor(editor, "Untitled", target_group)

        self.current_file = None
        self.statusBar().showMessage("Created new file", 3000)
        return editor
```


**New version:**


```python
    def new_file(self, target_group=None):
        """Create an untitled editor in the active group."""
        editor = self.get_editor()
        self._connect_editor(editor)
        self.tab_view.add_editor(editor, "Untitled", target_group)

        self.current_file = None
        require_qt(self.statusBar()).showMessage("Created new file", 3000)
        return editor
```


**Implementation:** inside `main.py`, replace only `MainWindow.new_file`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.44 Existing method/function `MainWindow.open_file`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2487–2504:**


```python
    def open_file(self):
        # open file
        ops = QFileDialog.Options()
        ops |= QFileDialog.DontUseNativeDialog
        new_file, _ = QFileDialog.getOpenFileName(
            self,
            "Pick A File",
            "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py);;Markdown Files (*.md);;C Files (*.c)",
            options=ops,
        )

        if new_file == "":
            self.statusBar().showMessage("Cancelled", 2000)
            return
        f = Path(new_file)
        self.set_new_tab(f)
        self._add_to_recent_files(str(f))
```


**New version:**


```python
    def open_file(self):
        # open file
        """Choose a file and open it in the appropriate editor tab.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        ops = QFileDialog.Options()
        ops |= QFileDialog.Option.DontUseNativeDialog
        new_file, _ = QFileDialog.getOpenFileName(
            self,
            "Pick A File",
            "",
            "All Files (*);;Text Files (*.txt);;Python Files (*.py);;Markdown Files (*.md);;C Files (*.c)",
            options=ops,
        )

        if new_file == "":
            require_qt(self.statusBar()).showMessage("Cancelled", 2000)
            return
        f = Path(new_file)
        self.set_new_tab(f)
        self._add_to_recent_files(str(f))
```


**Implementation:** inside `main.py`, replace only `MainWindow.open_file`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.45 Existing method/function `MainWindow.open_folder`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 2506–2529:**


```python
    def open_folder(self):
        """Select a project folder and retarget project-scoped services."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        new_folder = QFileDialog.getExistingDirectory(
            self,
            "Pick A Folder",
            "",
            options=options,
        )
        if not new_folder:
            return
        selected = Path(new_folder).resolve()
        self.file_manager.model.setRootPath(str(selected))
        self.file_manager.setRootIndex(self.file_manager.model.index(str(selected)))
        self.terminal.set_working_directory(selected, restart=True)
        self._refresh_git_state()
        new_workspace = self._discover_workspace_root(selected)
        if new_workspace != self._workspace_root:
            self._restart_ruff(
                python_executable=self.python_runner.interpreter,
                workspace_root=new_workspace,
            )
        self.statusBar().showMessage(f"Opened {selected}", 2_000)
```


**New version:**


```python
    def open_folder(self):
        """Select a project folder and retarget project-scoped services."""
        options = QFileDialog.Options()
        options |= QFileDialog.Option.DontUseNativeDialog
        new_folder = QFileDialog.getExistingDirectory(
            self,
            "Pick A Folder",
            "",
            options=options,
        )
        if not new_folder:
            return
        selected = Path(new_folder).resolve()
        self.file_manager.fs_model.setRootPath(str(selected))
        self.file_manager.setRootIndex(self.file_manager.fs_model.index(str(selected)))
        self.terminal.set_working_directory(selected, restart=True)
        self._refresh_git_state()
        new_workspace = self._discover_workspace_root(selected)
        if new_workspace != self._workspace_root:
            self._restart_ruff(
                python_executable=self.python_runner.interpreter,
                workspace_root=new_workspace,
            )
        require_qt(self.statusBar()).showMessage(f"Opened {selected}", 2_000)
```


**Implementation:** inside `main.py`, replace only `MainWindow.open_folder`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.46 Existing method/function `MainWindow._save_editor_to_path`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.


**Old version — original lines 2606–2687:**


```python
    def _save_editor_to_path(
        self,
        editor,
        path: Path,
        *,
        check_external_change: bool = True,
    ) -> bool:
        """Format and atomically save without losing links or newer disk data."""
        logical_path = Path(path)

        try:
            target = save_target(logical_path)
        except OSError as error:
            QMessageBox.critical(self, "Save File", f"Broken symbolic link:\n{error}")
            return False

        if check_external_change and target.exists():
            expected = getattr(editor, "_disk_digest", None)
            try:
                actual = disk_digest(target)
            except OSError as error:
                QMessageBox.critical(self, "Save File", str(error))
                return False

            if expected is not None and actual != expected:
                reply = QMessageBox.warning(
                    self,
                    "File changed on disk",
                    f"'{logical_path.name}' changed outside the editor.\n"
                    "Overwrite the newer disk version?",
                    QMessageBox.Yes | QMessageBox.Cancel,
                    QMessageBox.Cancel,
                )
                if reply != QMessageBox.Yes:
                    return False

        original = editor.text()
        try:
            formatted = self._run_ruff_before_save(logical_path, original)
        except (OSError, subprocess.SubprocessError, RuntimeError) as error:
            reply = QMessageBox.warning(
                self,
                "Ruff on save",
                f"Ruff could not process this file:\n{error}\n\nSave without Ruff?",
                QMessageBox.Save | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            if reply != QMessageBox.Save:
                return False
            formatted = original
        temporary = None

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self._encode_editor_text(editor, formatted)
            with tempfile.NamedTemporaryFile(
                dir=target.parent,
                prefix=f".{target.name}.",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if target.exists():
                os.chmod(temporary, target.stat().st_mode)
            os.replace(temporary, target)
            temporary = None
        except OSError as error:
            QMessageBox.critical(self, "Save File", f"Could not save '{logical_path}':\n{error}")
            return False
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        if formatted != original:
            # Retain the pre-format text as one Undo step after the save.
            self._apply_formatted_text(editor, formatted)
        editor._save_target = target
        editor._disk_digest = hashlib.sha256(data).digest()
        self.mark_editor_clean(editor)
        return True
```


**New version:**


```python
    def _save_editor_to_path(
        self,
        editor,
        path: Path,
        *,
        check_external_change: bool = True,
    ) -> bool:
        """Format and atomically save without losing links or newer disk data."""
        logical_path = Path(path)

        try:
            target = save_target(logical_path)
        except OSError as error:
            QMessageBox.critical(self, "Save File", f"Broken symbolic link:\n{error}")
            return False

        if check_external_change and target.exists():
            expected = getattr(editor, "_disk_digest", None)
            try:
                actual = disk_digest(target)
            except OSError as error:
                QMessageBox.critical(self, "Save File", str(error))
                return False

            if expected is not None and actual != expected:
                reply = QMessageBox.warning(
                    self,
                    "File changed on disk",
                    f"'{logical_path.name}' changed outside the editor.\n"
                    "Overwrite the newer disk version?",
                    qt_flags(QMessageBox.StandardButtons, QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.Cancel),
                    QMessageBox.StandardButton.Cancel,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return False

        original = editor.text()
        try:
            formatted = self._run_ruff_before_save(logical_path, original)
        except (OSError, subprocess.SubprocessError, RuntimeError) as error:
            reply = QMessageBox.warning(
                self,
                "Ruff on save",
                f"Ruff could not process this file:\n{error}\n\nSave without Ruff?",
                qt_flags(QMessageBox.StandardButtons, QMessageBox.StandardButton.Save, QMessageBox.StandardButton.Cancel),
                QMessageBox.StandardButton.Save,
            )
            if reply != QMessageBox.StandardButton.Save:
                return False
            formatted = original
        temporary = None

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            data = self._encode_editor_text(editor, formatted)
            with tempfile.NamedTemporaryFile(
                dir=target.parent,
                prefix=f".{target.name}.",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if target.exists():
                os.chmod(temporary, target.stat().st_mode)
            os.replace(temporary, target)
            temporary = None
        except OSError as error:
            QMessageBox.critical(self, "Save File", f"Could not save '{logical_path}':\n{error}")
            return False
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        if formatted != original:
            # Retain the pre-format text as one Undo step after the save.
            self._apply_formatted_text(editor, formatted)
        editor._save_target = target
        editor._disk_digest = hashlib.sha256(data).digest()
        self.mark_editor_clean(editor)
        return True
```


**Implementation:** inside `main.py`, replace only `MainWindow._save_editor_to_path`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.47 Existing method/function `MainWindow.save_file`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2689–2711:**


```python
    def save_file(self):
        """
        Save the currently focused editor.
        An editor opened from disk has an existing 'editor.path', so it is written
        directly to that path. Only an untitled editor has path=None and must open
        the Save As dialog.
        """
        editor = self.current_editor()
        if editor is None:
            return False
        path = getattr(editor, "path", None)

        # Only untitled editors need  a user-selected destination.
        if path is None:
            return self.save_as()
        path = Path(path)
        if not self._save_editor_to_path(editor, path):
            return False
        self.current_file = path
        self.statusBar().showMessage(f"Saved {path.name}", 3000)
        self.cat.add_xp(1)
        self.cat.set_state("stretch", 2500)
        return True
```


**New version:**


```python
    def save_file(self):
        """
        Save the currently focused editor.
        An editor opened from disk has an existing 'editor.path', so it is written
        directly to that path. Only an untitled editor has path=None and must open
        the Save As dialog.
        """
        editor = self.current_editor()
        if editor is None:
            return False
        path = getattr(editor, "path", None)

        # Only untitled editors need  a user-selected destination.
        if path is None:
            return self.save_as()
        path = Path(path)
        if not self._save_editor_to_path(editor, path):
            return False
        self.current_file = path
        require_qt(self.statusBar()).showMessage(f"Saved {path.name}", 3000)
        self.cat.add_xp(1)
        self.cat.set_state("stretch", 2500)
        return True
```


**Implementation:** inside `main.py`, replace only `MainWindow.save_file`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.48 Existing method/function `MainWindow.save_as`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2713–2765:**


```python
    def save_as(self):
        """Save to a user-confirmed path and update the tab's editor type.
        The native file dialog owns the intentional overwrite confirmation.
        The source tab's disk digest belongs to its old path and must never be
        compared with bytes at the new destination.
        """

        editor = self.current_editor()
        if editor is None:
            return False

        file_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save As",
            os.getcwd(),
        )

        if not file_path:
            self.statusBar().showMessage("Cancelled", 2_000)
            return False
        path = Path(file_path)

        owner = self.tab_view.find_editor_by_path(path)
        if owner is not None and owner is not editor:
            QMessageBox.warning(self, "Save As", "That file is already open in another tab.")
            self.tab_view.focus_editor(owner)
            return False

        # The dialog confirmed replacement. Do not compare the destination to
        # the digest of the tab's previous path.
        if not self._save_editor_to_path(editor, path, check_external_change=False):
            return False

        editor.path = path
        editor.full_path = path.absolute()
        self.current_file = path
        self.tab_view.set_editor_tooltip(editor, str(editor.full_path))
        desired_class = PythonEditor if is_python_path(path) else MarkdownEditor
        converted = not isinstance(editor, desired_class)
        if converted:
            editor = self._convert_editor(editor, desired_class)

        if isinstance(editor, PythonEditor):
            # A newly converted PythonEditor was constructed with ``path`` and
            # already owns the correct URI. Only an existing Python editor must
            # migrate its old Ruff URI after Python-to-Python Save As.
            if not converted and editor.ruff_lsp is not None:
                editor.ruff_lsp.relocate(path)
            editor.auto_completer.file_path = str(editor.full_path)
        self.mark_editor_clean(editor)
        self._add_to_recent_files(str(path))
        self.statusBar().showMessage(f"Saved {path.name}", 2_000)
        return True
```


**New version:**


```python
    def save_as(self):
        """Save to a user-confirmed path and update the tab's editor type.
        The native file dialog owns the intentional overwrite confirmation.
        The source tab's disk digest belongs to its old path and must never be
        compared with bytes at the new destination.
        """

        editor = self.current_editor()
        if editor is None:
            return False

        file_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save As",
            os.getcwd(),
        )

        if not file_path:
            require_qt(self.statusBar()).showMessage("Cancelled", 2_000)
            return False
        path = Path(file_path)

        owner = self.tab_view.find_editor_by_path(path)
        if owner is not None and owner is not editor:
            QMessageBox.warning(self, "Save As", "That file is already open in another tab.")
            self.tab_view.focus_editor(owner)
            return False

        # The dialog confirmed replacement. Do not compare the destination to
        # the digest of the tab's previous path.
        if not self._save_editor_to_path(editor, path, check_external_change=False):
            return False

        editor.path = path
        editor.full_path = path.absolute()
        self.current_file = path
        self.tab_view.set_editor_tooltip(editor, str(editor.full_path))
        desired_class = PythonEditor if is_python_path(path) else MarkdownEditor
        converted = not isinstance(editor, desired_class)
        if converted:
            editor = self._convert_editor(editor, desired_class)

        if isinstance(editor, PythonEditor):
            # A newly converted PythonEditor was constructed with ``path`` and
            # already owns the correct URI. Only an existing Python editor must
            # migrate its old Ruff URI after Python-to-Python Save As.
            if not converted and editor.ruff_lsp is not None:
                editor.ruff_lsp.relocate(path)
            editor.auto_completer.file_path = str(editor.full_path)
        self.mark_editor_clean(editor)
        self._add_to_recent_files(str(path))
        require_qt(self.statusBar()).showMessage(f"Saved {path.name}", 2_000)
        return True
```


**Implementation:** inside `main.py`, replace only `MainWindow.save_as`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.49 Existing method/function `MainWindow.change_editor_python`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2858–2862:**


```python
    def change_editor_python(self):
        self.python_editor_active = True
        self._swap_editor(PythonEditor)
        self.preview.hide()
        self.statusBar().showMessage("Python-Editor applied", 2000)
```


**New version:**


```python
    def change_editor_python(self):
        """Switch the selected document to the Python editor implementation.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self.python_editor_active = True
        self._swap_editor(PythonEditor)
        self.preview.hide()
        require_qt(self.statusBar()).showMessage("Python-Editor applied", 2000)
```


**Implementation:** inside `main.py`, replace only `MainWindow.change_editor_python`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.50 Existing method/function `MainWindow.change_editor_markdown`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2864–2869:**


```python
    def change_editor_markdown(self):
        self.python_editor_active = False
        self._swap_editor(MarkdownEditor)
        self.preview.show()
        QTimer.singleShot(0, self.render_preview)
        self.statusBar().showMessage("Markdown-Editor applied", 2000)
```


**New version:**


```python
    def change_editor_markdown(self):
        """Switch the selected document to the Markdown editor implementation.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self.python_editor_active = False
        self._swap_editor(MarkdownEditor)
        self.preview.show()
        QTimer.singleShot(0, self.render_preview)
        require_qt(self.statusBar()).showMessage("Markdown-Editor applied", 2000)
```


**Implementation:** inside `main.py`, replace only `MainWindow.change_editor_markdown`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.51 Existing method/function `MainWindow.render_preview`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2890–2901:**


```python
    def render_preview(self):
        """Render only sanitized Markdown into the already loaded shell."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or not self._preview_ready:
            return
        safe_body = self._render_markdown_safely(editor.text())

        # json.dumps creats a valid JavaScript string literal. Never interpolate
        # document text directly into JavaScript source.
        payload = json.dumps(safe_body)
        script = f'document.getElementById("content").innerHTML = {payload};'
        self.preview.page().runJavaScript(script)
```


**New version:**


```python
    def render_preview(self):
        """Render only sanitized Markdown into the already loaded shell."""
        editor = self.current_editor()
        if not isinstance(editor, MarkdownEditor) or not self._preview_ready:
            return
        safe_body = self._render_markdown_safely(editor.text())

        # json.dumps creats a valid JavaScript string literal. Never interpolate
        # document text directly into JavaScript source.
        payload = json.dumps(safe_body)
        script = f'document.getElementById("content").innerHTML = {payload};'
        require_qt(self.preview.page()).runJavaScript(script)
```


**Implementation:** inside `main.py`, replace only `MainWindow.render_preview`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.52 Existing method/function `MainWindow._on_preview_loaded`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2903–2909:**


```python
    def _on_preview_loaded(self, ok):
        """Enable rendering only when the fixed preview shell loads."""
        self._preview_ready = bool(ok)
        if self._preview_ready:
            self.render_preview()
        else:
            self.statusBar().showMessage("Markdown preview failed to load.", 4000)
```


**New version:**


```python
    def _on_preview_loaded(self, ok):
        """Enable rendering only when the fixed preview shell loads."""
        self._preview_ready = bool(ok)
        if self._preview_ready:
            self.render_preview()
        else:
            require_qt(self.statusBar()).showMessage("Markdown preview failed to load.", 4000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._on_preview_loaded`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.53 Existing method/function `MainWindow.sync_scroll`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 2911–2926:**


```python
    def sync_scroll(self, editor):

        if not self._preview_ready or editor is not self.current_editor():
            return

        total = editor.lines()
        visible = editor.SendScintilla(2370)
        first = editor.firstVisibleLine()
        denom = max(total - visible, 1)
        ratio = min(max(first / denom, 0.0), 1.0)

        js = f"""
        var h = document.documentElement.scrollHeight - window.innerHeight;
        window.scrollTo(0, h * {ratio});
        """
        self.preview.page().runJavaScript(js)
```


**New version:**


```python
    def sync_scroll(self, editor):

        """Synchronize the preview scroll position with the active editor.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if not self._preview_ready or editor is not self.current_editor():
            return

        total = editor.lines()
        visible = editor.SendScintilla(2370)
        first = editor.firstVisibleLine()
        denom = max(total - visible, 1)
        ratio = min(max(first / denom, 0.0), 1.0)

        js = f"""
        var h = document.documentElement.scrollHeight - window.innerHeight;
        window.scrollTo(0, h * {ratio});
        """
        require_qt(self.preview.page()).runJavaScript(js)
```


**Implementation:** inside `main.py`, replace only `MainWindow.sync_scroll`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.54 Existing method/function `MainWindow._search_inputs`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 3049–3061:**


```python
    def _search_inputs(self, text, case_sensitive, whole_word, regex):
        """Compile and match once, converting input errors to a status message."""
        editor = self.current_editor()
        if editor is None:
            return None
        try:
            pattern = self._compile_find_pattern(text, case_sensitive, whole_word, regex)
            matches = self._validated_matches(pattern, editor.text())
        except (re.error, ValueError) as error:
            self.statusBar().showMessage(f"Invalid search: {error}", 4_000)
            return None

        return editor, pattern, matches
```


**New version:**


```python
    def _search_inputs(self, text, case_sensitive, whole_word, regex):
        """Compile and match once, converting input errors to a status message."""
        editor = self.current_editor()
        if editor is None:
            return None
        try:
            pattern = self._compile_find_pattern(text, case_sensitive, whole_word, regex)
            matches = self._validated_matches(pattern, editor.text())
        except (re.error, ValueError) as error:
            require_qt(self.statusBar()).showMessage(f"Invalid search: {error}", 4_000)
            return None

        return editor, pattern, matches
```


**Implementation:** inside `main.py`, replace only `MainWindow._search_inputs`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.55 Existing method/function `MainWindow._do_find_next`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 3089–3108:**


```python
    def _do_find_next(self, text, case_sensitive, whole_word, regex):
        """Select the next match, wrapping once at the document end."""
        result = self._search_inputs(text, case_sensitive, whole_word, regex)
        if result is None:
            return
        editor, _pattern, matches = result
        if not matches:
            self.statusBar().showMessage("No matches", 2_000)
            return
        source = editor.text()
        if editor.hasSelectedText():
            _start_line, _start_column, line, column = editor.getSelection()
        else:
            line, column = editor.getCursorPosition()
        cursor_offset = self._line_column_to_offset(source, line, column)
        match = next(
            (candidate for candidate in matches if candidate.start() >= cursor_offset),
            matches[0],
        )
        self._select_python_match(editor, match)
```


**New version:**


```python
    def _do_find_next(self, text, case_sensitive, whole_word, regex):
        """Select the next match, wrapping once at the document end."""
        result = self._search_inputs(text, case_sensitive, whole_word, regex)
        if result is None:
            return
        editor, _pattern, matches = result
        if not matches:
            require_qt(self.statusBar()).showMessage("No matches", 2_000)
            return
        source = editor.text()
        if editor.hasSelectedText():
            _start_line, _start_column, line, column = editor.getSelection()
        else:
            line, column = editor.getCursorPosition()
        cursor_offset = self._line_column_to_offset(source, line, column)
        match = next(
            (candidate for candidate in matches if candidate.start() >= cursor_offset),
            matches[0],
        )
        self._select_python_match(editor, match)
```


**Implementation:** inside `main.py`, replace only `MainWindow._do_find_next`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.56 Existing method/function `MainWindow._do_find_prev`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 3110–3126:**


```python
    def _do_find_prev(self, text, case_sensitive, whole_word, regex):
        """Select the previous match, wrapping once at the document start."""
        result = self._search_inputs(text, case_sensitive, whole_word, regex)
        if result is None:
            return
        editor, _pattern, matches = result
        if not matches:
            self.statusBar().showMessage("No matches", 2_000)
            return
        source = editor.text()
        if editor.hasSelectedText():
            line, column, _end_line, _end_column = editor.getSelection()
        else:
            line, column = editor.getCursorPosition()
        cursor_offset = self._line_column_to_offset(source, line, column)
        before = [candidate for candidate in matches if candidate.end() <= cursor_offset]
        self._select_python_match(editor, before[-1] if before else matches[-1])
```


**New version:**


```python
    def _do_find_prev(self, text, case_sensitive, whole_word, regex):
        """Select the previous match, wrapping once at the document start."""
        result = self._search_inputs(text, case_sensitive, whole_word, regex)
        if result is None:
            return
        editor, _pattern, matches = result
        if not matches:
            require_qt(self.statusBar()).showMessage("No matches", 2_000)
            return
        source = editor.text()
        if editor.hasSelectedText():
            line, column, _end_line, _end_column = editor.getSelection()
        else:
            line, column = editor.getCursorPosition()
        cursor_offset = self._line_column_to_offset(source, line, column)
        before = [candidate for candidate in matches if candidate.end() <= cursor_offset]
        self._select_python_match(editor, before[-1] if before else matches[-1])
```


**Implementation:** inside `main.py`, replace only `MainWindow._do_find_prev`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.57 Existing method/function `MainWindow._do_replace`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 3128–3152:**


```python
    def _do_replace(self, find_text, replace_text, case_sensitive, whole_word, regex):
        """Replace the selected full match, then select the next match."""
        result = self._search_inputs(
            find_text,
            case_sensitive,
            whole_word,
            regex,
        )

        if result is None:
            return

        editor, pattern, _matches = result

        try:
            self._validate_regex_replacement(pattern, replace_text, regex)
            selected = editor.selectedText() if editor.hasSelectedText() else ""
            match = pattern.fullmatch(selected) if selected else None
            if match is not None:
                replacement = match.expand(replace_text) if regex else replace_text
                editor.replace(replacement)
        except re.error as error:
            self.statusBar().showMessage(f"Invalid replacement: {error}", 4_000)
            return
        self._do_find_next(find_text, case_sensitive, whole_word, regex)
```


**New version:**


```python
    def _do_replace(self, find_text, replace_text, case_sensitive, whole_word, regex):
        """Replace the selected full match, then select the next match."""
        result = self._search_inputs(
            find_text,
            case_sensitive,
            whole_word,
            regex,
        )

        if result is None:
            return

        editor, pattern, _matches = result

        try:
            self._validate_regex_replacement(pattern, replace_text, regex)
            selected = editor.selectedText() if editor.hasSelectedText() else ""
            match = pattern.fullmatch(selected) if selected else None
            if match is not None:
                replacement = match.expand(replace_text) if regex else replace_text
                editor.replace(replacement)
        except re.error as error:
            require_qt(self.statusBar()).showMessage(f"Invalid replacement: {error}", 4_000)
            return
        self._do_find_next(find_text, case_sensitive, whole_word, regex)
```


**Implementation:** inside `main.py`, replace only `MainWindow._do_replace`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.58 Existing method/function `MainWindow._do_replace_all`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 3154–3192:**


```python
    def _do_replace_all(self, find_text, replace_text, case_sensitive, whole_word, regex):
        """Replace all validated matches as one undoable editor operation."""

        result = self._search_inputs(
            find_text,
            case_sensitive,
            whole_word,
            regex,
        )

        if result is None:
            return
        editor, pattern, matches = result
        try:
            self._validate_regex_replacement(pattern, replace_text, regex)
        except re.error as error:
            self.statusBar().showMessage(f"Invalid replacement: {error}", 4_000)
            return
        source = editor.text()
        editor.beginUndoAction()

        try:
            # Work backward so each earlier Python offset remains valid after a
            # later replacement changes the document length.
            for match in reversed(matches):
                start_line, start_column = self._offset_to_line_column(
                    source,
                    match.start(),
                )
                end_line, end_column = self._offset_to_line_column(
                    source,
                    match.end(),
                )
                editor.setSelection(start_line, start_column, end_line, end_column)
                replacement = match.expand(replace_text) if regex else replace_text
                editor.replace(replacement)
        finally:
            editor.endUndoAction()
        self.statusBar().showMessage(f"Replaced {len(matches)} occurrences", 3_000)
```


**New version:**


```python
    def _do_replace_all(self, find_text, replace_text, case_sensitive, whole_word, regex):
        """Replace all validated matches as one undoable editor operation."""

        result = self._search_inputs(
            find_text,
            case_sensitive,
            whole_word,
            regex,
        )

        if result is None:
            return
        editor, pattern, matches = result
        try:
            self._validate_regex_replacement(pattern, replace_text, regex)
        except re.error as error:
            require_qt(self.statusBar()).showMessage(f"Invalid replacement: {error}", 4_000)
            return
        source = editor.text()
        editor.beginUndoAction()

        try:
            # Work backward so each earlier Python offset remains valid after a
            # later replacement changes the document length.
            for match in reversed(matches):
                start_line, start_column = self._offset_to_line_column(
                    source,
                    match.start(),
                )
                end_line, end_column = self._offset_to_line_column(
                    source,
                    match.end(),
                )
                editor.setSelection(start_line, start_column, end_line, end_column)
                replacement = match.expand(replace_text) if regex else replace_text
                editor.replace(replacement)
        finally:
            editor.endUndoAction()
        require_qt(self.statusBar()).showMessage(f"Replaced {len(matches)} occurrences", 3_000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._do_replace_all`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.59 Existing method/function `MainWindow._background_work_running`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 3194–3230:**


```python
    def _background_work_running(self) -> bool:
        """Return whether an asynchronous component is still shutting down.
        Returns:
            True while an editor retirement, Git scan, project search, Python
            run, Ruff process, or terminal PTY worker remains active.
        The method is polled by `_finish_pending_close()` through QTimer. It
        must only inspect state and must never block the GUI thread.
        """
        git_worker = getattr(
            getattr(self, "file_manager", None),
            "git_checker",
            None,
        )

        search_worker = getattr(self, "search_worker", None)
        runner = getattr(self, "python_runner", None)
        ruff = getattr(self, "ruff_lsp_client", None)
        terminal = getattr(self, "terminal", None)
        git_service = getattr(self, "git_service", None)
        type_analysis = getattr(self, "type_diagnostics", None)

        return bool(
            # Retired editors remain here until their workers are disposed.
            self._retired_editors
            # QThread-based background services use isRunning().
            or (git_worker is not None and git_worker.isRunning())
            or (search_worker is not None and search_worker.isRunning())
            or (git_service is not None and git_service.is_running())
            # PythonRunner exposes its own public running-state method.
            or (runner is not None and runner.is_running())
            # Ruff still uses QProcess, so its existing state check remains.
            or (ruff is not None and ruff.process.state() != QProcess.NotRunning)
            # The PTY terminal no longer owns a QProcess. Ask its public API
            # whether the _PtySession worker is still running.
            or (terminal is not None and terminal.is_running())
            or (type_analysis is not None and type_analysis.is_running())
        )
```


**New version:**


```python
    def _background_work_running(self) -> bool:
        """Return whether an asynchronous component is still shutting down.
        Returns:
            True while an editor retirement, Git scan, project search, Python
            run, Ruff process, or terminal PTY worker remains active.
        The method is polled by `_finish_pending_close()` through QTimer. It
        must only inspect state and must never block the GUI thread.
        """
        git_worker = getattr(
            getattr(self, "file_manager", None),
            "git_checker",
            None,
        )

        search_worker = getattr(self, "search_worker", None)
        runner = getattr(self, "python_runner", None)
        ruff = getattr(self, "ruff_lsp_client", None)
        terminal = getattr(self, "terminal", None)
        git_service = getattr(self, "git_service", None)
        type_analysis = getattr(self, "type_diagnostics", None)

        return bool(
            # Retired editors remain here until their workers are disposed.
            self._retired_editors
            # QThread-based background services use isRunning().
            or (git_worker is not None and git_worker.isRunning())
            or (search_worker is not None and search_worker.isRunning())
            or (git_service is not None and git_service.is_running())
            # PythonRunner exposes its own public running-state method.
            or (runner is not None and runner.is_running())
            # Ruff still uses QProcess, so its existing state check remains.
            or (ruff is not None and ruff.process.state() != QProcess.ProcessState.NotRunning)
            # The PTY terminal no longer owns a QProcess. Ask its public API
            # whether the _PtySession worker is still running.
            or (terminal is not None and terminal.is_running())
            or (type_analysis is not None and type_analysis.is_running())
        )
```


**Implementation:** inside `main.py`, replace only `MainWindow._background_work_running`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.60 Existing method/function `MainWindow.closeEvent`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.


**Old version — original lines 3239–3291:**


```python
    def closeEvent(self, event):
        if getattr(self, "_close_ready", False):
            event.accept()
            return super().closeEvent(event)

        if not getattr(self, "_close_prompts_complete", False):
            for editor in list(self.tab_view.all_editors()):
                if editor not in self._dirty_editors:
                    continue
                self.tab_view.focus_editor(editor)
                path = getattr(editor, "path", None)
                name = Path(path).name if path is not None else "Untitled"
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"Save changes to '{name}'?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save,
                )
                if reply == QMessageBox.Cancel:
                    event.ignore()
                    return
                if reply == QMessageBox.Save and not self.save_file():
                    event.ignore()
                    return

            self._close_prompts_complete = True
            self.save_session()

        for editor in list(self.tab_view.all_editors()):
            self.tab_view.remove_editor(editor)
            self._dispose_editor(editor)
        self.terminal.stop()
        if hasattr(self, "type_diagnostics"):
            self.type_diagnostics.shutdown()
        if hasattr(self.python_runner, "shutdown"):
            self.python_runner.shutdown()
        else:
            # Compatibility until Fix 5 replaces PythonRunner.
            self.python_runner.stop()
        self.ruff_lsp_client.shutdown()
        if hasattr(self.search_worker, "shutdown"):
            self.search_worker.shutdown()
        self.settings.setValue("recent_files", self.recent_files)
        self.file_manager.git_checker.shutdown()
        self.git_service.shutdown()
        if self._background_work_running():
            event.ignore()
            QTimer.singleShot(100, self._finish_pending_close)
            return
        self._close_ready = True
        event.accept()
        super().closeEvent(event)
```


**New version:**


```python
    def closeEvent(self, event):
        """Handle window closure while preserving the existing shutdown checks.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if getattr(self, "_close_ready", False):
            event.accept()
            return super().closeEvent(event)

        if not getattr(self, "_close_prompts_complete", False):
            for editor in list(self.tab_view.all_editors()):
                if editor not in self._dirty_editors:
                    continue
                self.tab_view.focus_editor(editor)
                path = getattr(editor, "path", None)
                name = Path(path).name if path is not None else "Untitled"
                reply = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"Save changes to '{name}'?",
                    qt_flags(QMessageBox.StandardButtons, QMessageBox.StandardButton.Save, QMessageBox.StandardButton.Discard, QMessageBox.StandardButton.Cancel),
                    QMessageBox.StandardButton.Save,
                )
                if reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
                if reply == QMessageBox.StandardButton.Save and not self.save_file():
                    event.ignore()
                    return

            self._close_prompts_complete = True
            self.save_session()

        for editor in list(self.tab_view.all_editors()):
            self.tab_view.remove_editor(editor)
            self._dispose_editor(editor)
        self.terminal.stop()
        if hasattr(self, "type_diagnostics"):
            self.type_diagnostics.shutdown()
        if hasattr(self.python_runner, "shutdown"):
            self.python_runner.shutdown()
        else:
            # Compatibility until Fix 5 replaces PythonRunner.
            self.python_runner.stop()
        self.ruff_lsp_client.shutdown()
        if hasattr(self.search_worker, "shutdown"):
            self.search_worker.shutdown()
        self.settings.setValue("recent_files", self.recent_files)
        self.file_manager.git_checker.shutdown()
        self.git_service.shutdown()
        if self._background_work_running():
            event.ignore()
            QTimer.singleShot(100, self._finish_pending_close)
            return
        self._close_ready = True
        event.accept()
        super().closeEvent(event)
```


**Implementation:** inside `main.py`, replace only `MainWindow.closeEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.61 Existing method/function `MainWindow._install_problems`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 3293–3314:**


```python
    def _install_problems(self):
        """
        Create the common store, Problems dock and merge diagnostic renderer.
        
        This foundation works with Ruff alone, Later topics attach additional 
        providers to the same store and appen their actions to the same menu.
        Bind-pre existing editors because init_ui runs before this installer.
        """
        self.diagnostics_manager: DiagnosticsManager = DiagnosticsManager(self)
        self.problems_panel = ProblemsPanel(self)
        self.problems_dock = QDockWidget("Problems", self)
        self.problems_dock.setObjectName("ProblemsDock")
        self.problems_dock.setWidget(self.problems_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.problems_dock)
        self.problems_dock.hide()
        self.diagnostics_manager.changed.connect(self.problems_panel.set_diagnostics)
        self.diagnostics_manager.changed.connect(self._render_all_diagnostics)
        self.problems_panel.diagnosticActivated.connect(self._open_problem)
        self.diagnostics_menu = self.menuBar().addMenu("Diagnostics")
        self.diagnostics_menu.addAction(self.problems_dock.toggleViewAction())
        for editor in self.tab_view.all_editors():
            self._bind_diagnostic_editor(editor)
```


**New version:**


```python
    def _install_problems(self):
        """
        Create the common store, Problems dock and merge diagnostic renderer.
        
        This foundation works with Ruff alone, Later topics attach additional 
        providers to the same store and appen their actions to the same menu.
        Bind-pre existing editors because init_ui runs before this installer.
        """
        self.diagnostics_manager: DiagnosticsManager = DiagnosticsManager(self)
        self.problems_panel = ProblemsPanel(self)
        self.problems_dock = QDockWidget("Problems", self)
        self.problems_dock.setObjectName("ProblemsDock")
        self.problems_dock.setWidget(self.problems_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.problems_dock)
        self.problems_dock.hide()
        self.diagnostics_manager.changed.connect(self.problems_panel.set_diagnostics)
        self.diagnostics_manager.changed.connect(self._render_all_diagnostics)
        self.problems_panel.diagnosticActivated.connect(self._open_problem)
        self.diagnostics_menu = require_qt(require_qt(self.menuBar()).addMenu("Diagnostics"))
        self.diagnostics_menu.addAction(self.problems_dock.toggleViewAction())
        for editor in self.tab_view.all_editors():
            self._bind_diagnostic_editor(editor)
```


**Implementation:** inside `main.py`, replace only `MainWindow._install_problems`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.62 Existing method/function `MainWindow._render_all_diagnostics`

If one retained provider still describes an older revision, leave existing paint in place. Do not redraw its old line/column coordinates. Once retained records are current, render the merged collection; an empty collection clears resolved findings.


**Old version — original lines 3329–3366:**


```python
    def _render_all_diagnostics(self, rows: list[Diagnostic]) -> None:
        """
        Render each open buffer from all provider's current-version records.
        
        Args:
            rows: Complete snapshot emitted by DiagnosticsManager.changed.
            
        Providers replace only their own collection. This method merges their
        records per URI and filters stale versions before the view clears and 
        repaints its indicators. Raw Ruff payloads remain stored in the manager.
        """
        by_uri = {}
        for row in rows:
            by_uri.setdefault(row.uri, []).append(row)
        for editor in self.tab_view.all_editors():
            controller = getattr(editor, "ruff_lsp", None)
            if controller is None or controller._closed:
                continue
            display = []
            for row in by_uri.get(controller.uri, []):
                if row.revision != controller.document_version:
                    continue
                original = row.provider_data
                ruff_record = original if row.provider == "ruff" and isinstance(original, RuffDiagnostic) else None
                start, end = row.source_range.start, row.source_range.end
                display.append(RuffDiagnostic(
                    code=f"{row.provider}: {row.code}",
                    message=row.message,
                    severity=RuffSeverity(int(row.severity)),
                    start=RuffPosition(start.line, start.column),
                    end=RuffPosition(end.line, end.column),
                    revision=controller.document_version,
                    # Keep Ruff's raw range/data for request_quick_fixes.
                    raw=ruff_record.raw if ruff_record is not None else {},
                    fix=ruff_record.fix if ruff_record is not None else None,
                    provider=row.provider,
                ))
            controller.view.render(display)
```


**New version:**


```python
    def _render_all_diagnostics(self, rows: list[Diagnostic]) -> None:
        """
        Render a merged snapshot only when its retained records are current.
        
        Args:
            rows: Complete snapshot emitted by DiagnosticsManager.changed.
            
        Providers replace only their own collection. This method merges their
        records per URI. If a retained provider is still pending, it leaves the
        previous indicator paint intact; stale records are never repainted. Raw Ruff payloads remain stored in the manager.
        """
        by_uri = {}
        for row in rows:
            by_uri.setdefault(row.uri, []).append(row)
        for editor in self.tab_view.all_editors():
            controller = getattr(editor, "ruff_lsp", None)
            if controller is None or controller._closed:
                continue
            document_rows = by_uri.get(controller.uri, [])
            if any(row.revision != controller.document_version for row in document_rows):
                # One provider is still pending. Leave the existing indicator
                # positions alone instead of repainting old source coordinates.
                continue
            display = []
            for row in document_rows:
                if row.revision != controller.document_version:
                    continue
                original = row.provider_data
                ruff_record = original if row.provider == "ruff" and isinstance(original, RuffDiagnostic) else None
                start, end = row.source_range.start, row.source_range.end
                display.append(RuffDiagnostic(
                    code=f"{row.provider}: {row.code}",
                    message=row.message,
                    severity=RuffSeverity(int(row.severity)),
                    start=RuffPosition(start.line, start.column),
                    end=RuffPosition(end.line, end.column),
                    revision=controller.document_version,
                    # Keep Ruff's raw range/data for request_quick_fixes.
                    raw=ruff_record.raw if ruff_record is not None else {},
                    fix=ruff_record.fix if ruff_record is not None else None,
                    provider=row.provider,
                ))
            controller.view.render(display)
```


**Implementation:** inside `main.py`, replace only `MainWindow._render_all_diagnostics`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.63 Existing method/function `MainWindow._on_analysis_error`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 3368–3376:**


```python
    def _on_analysis_error(self, message: str) -> None:
        """
        Expose an analysis failure separately from errors in the user's code.
        
        A missing server package or directory is not a clean diagnostic result.
        Show a temporary status message and retain the detail in process output.
        """
        print(message)
        self.statusBar().showMessage(message, 15_000)
```


**New version:**


```python
    def _on_analysis_error(self, message: str) -> None:
        """
        Expose an analysis failure separately from errors in the user's code.
        
        A missing server package or directory is not a clean diagnostic result.
        Show a temporary status message and retain the detail in process output.
        """
        print(message)
        require_qt(self.statusBar()).showMessage(message, 15_000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._on_analysis_error`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.64 Existing method/function `MainWindow._restore_session`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 3485–3565:**


```python
    def _restore_session(self):
        """
        Reopen the tabs saved by _save_session().

        Strategy:
        1.  Parse the stored JSON (any error -> give up silently; a fresh session is always
            a valid state).
        2.  Create enough tab groups to reproduce the split layout.
        3.  Reopen each file with set_new_tab(), flipping self.python_editor_active
            per file so each tab gets the right editor class.
        4.  Re-focus the tab that was active at close time.



        set_new_tab() already handles the hard parts for us: binary-file rejection,
        duplicate detection (find_editor_by_path), recent-file bookkeeping and dirty-state signal wiring.
        """
        import json
        if not self.settings.value("restore_tabs", True, type=bool):
            return

        raw = self.settings.value("session", "", type=str)
        if not raw:
            return
        try:
            session = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return

        tabs = session.get("tabs", [])
        if not isinstance(tabs, list) or len(tabs) > 100:
            return

        tabs = [
            entry
            for entry in tabs
            if (
                isinstance(entry, dict)
                and isinstance(entry.get("path"), str)
                and isinstance(entry.get("python", False), bool)
                and isinstance(entry.get("group", 0), int)
                and 0 <= entry.get("group", 0) < 20
            )
        ]
        if not tabs:
            return

        # --- 2. Recreate the split layout --- #
        # Tab groups are created lazily by MultiTabView; to place tab into group 2 we must make sure
        # groups 0..2 exist first. _create_group() is technically private - optionally rename it to
        # create_group() in multi_tab_view.py and update this call
        # (plus its two internal callers) to keep things clean.
        max_group = max(entry["group"] for entry in tabs)
        while len(self.tab_view.groups()) <= max_group:
            self.tab_view._create_group()
        groups = list(self.tab_view.groups())

        # --- 2. Reopen every tab --- #

        active_editor = None
        for entry in tabs:
            path = Path(entry["path"])
            if not path.is_file():
                continue  # delete/move since last session - skip it
            # set_new_tab() branches on self.python_editor_active to choose PythonEditor vs MarkdownEditor.
            # Setting it per file restores each tab in the mode it was last edited with.
            editor = self.set_new_tab(
                path,
                target_group=groups[entry["group"]],
                is_python_file=entry["python"],
            )
            if editor is not None and session.get("active") == str(path):
                active_editor = editor

        # --- 3. Restore the global mode + focus --- #
        # The global flag governs NEW tabs opened after startup, so it refelcts
        # the mode the app was in at close time.
        self.python_editor_active = session.get("python_mode", False)
        if active_editor is not None:
            self.tab_view.focus_editor(active_editor)
        self.statusBar().showMessage(f"Restore {len(tabs)} tabs from last session", 5000)
```


**New version:**


```python
    def _restore_session(self):
        """
        Reopen the tabs saved by _save_session().

        Strategy:
        1.  Parse the stored JSON (any error -> give up silently; a fresh session is always
            a valid state).
        2.  Create enough tab groups to reproduce the split layout.
        3.  Reopen each file with set_new_tab(), flipping self.python_editor_active
            per file so each tab gets the right editor class.
        4.  Re-focus the tab that was active at close time.



        set_new_tab() already handles the hard parts for us: binary-file rejection,
        duplicate detection (find_editor_by_path), recent-file bookkeeping and dirty-state signal wiring.
        """
        import json
        if not self.settings.value("restore_tabs", True, type=bool):
            return

        raw = self.settings.value("session", "", type=str)
        if not raw:
            return
        try:
            session = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return

        tabs = session.get("tabs", [])
        if not isinstance(tabs, list) or len(tabs) > 100:
            return

        tabs = [
            entry
            for entry in tabs
            if (
                isinstance(entry, dict)
                and isinstance(entry.get("path"), str)
                and isinstance(entry.get("python", False), bool)
                and isinstance(entry.get("group", 0), int)
                and 0 <= entry.get("group", 0) < 20
            )
        ]
        if not tabs:
            return

        # --- 2. Recreate the split layout --- #
        # Tab groups are created lazily by MultiTabView; to place tab into group 2 we must make sure
        # groups 0..2 exist first. _create_group() is technically private - optionally rename it to
        # create_group() in multi_tab_view.py and update this call
        # (plus its two internal callers) to keep things clean.
        max_group = max(entry["group"] for entry in tabs)
        while len(self.tab_view.groups()) <= max_group:
            self.tab_view._create_group()
        groups = list(self.tab_view.groups())

        # --- 2. Reopen every tab --- #

        active_editor = None
        for entry in tabs:
            path = Path(entry["path"])
            if not path.is_file():
                continue  # delete/move since last session - skip it
            # set_new_tab() branches on self.python_editor_active to choose PythonEditor vs MarkdownEditor.
            # Setting it per file restores each tab in the mode it was last edited with.
            editor = self.set_new_tab(
                path,
                target_group=groups[entry["group"]],
                is_python_file=entry["python"],
            )
            if editor is not None and session.get("active") == str(path):
                active_editor = editor

        # --- 3. Restore the global mode + focus --- #
        # The global flag governs NEW tabs opened after startup, so it refelcts
        # the mode the app was in at close time.
        self.python_editor_active = session.get("python_mode", False)
        if active_editor is not None:
            self.tab_view.focus_editor(active_editor)
        require_qt(self.statusBar()).showMessage(f"Restore {len(tabs)} tabs from last session", 5000)
```


**Implementation:** inside `main.py`, replace only `MainWindow._restore_session`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.4.65 Existing method/function `MainWindow._show_update_dialog`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.


**Old version — original lines 3625–3641:**


```python
    def _show_update_dialog(self, version: str, download_url: str):
        """Show a dialog telling the user about the update."""
        reply = QMessageBox.information(
            self,
            "Update Available",
            f"A new version ({version}) is available!\n\n"
            f"You are currently running {APP_VERSION}.\n\n"
            f"Click OK to open the download page in your browser.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Ok,
        )

        if reply == QMessageBox.Ok:
            # webbrowser.open opens the URL in the user's default browser
            # Docs: https://docs.python.org/3/library/webbrowser.html#webbrowser.open
            import webbrowser
            webbrowser.open(download_url)
```


**New version:**


```python
    def _show_update_dialog(self, version: str, download_url: str):
        """Show a dialog telling the user about the update."""
        reply = QMessageBox.information(
            self,
            "Update Available",
            f"A new version ({version}) is available!\n\n"
            f"You are currently running {APP_VERSION}.\n\n"
            f"Click OK to open the download page in your browser.",
            qt_flags(QMessageBox.StandardButtons, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel),
            QMessageBox.StandardButton.Ok,
        )

        if reply == QMessageBox.StandardButton.Ok:
            # webbrowser.open opens the URL in the user's default browser
            # Docs: https://docs.python.org/3/library/webbrowser.html#webbrowser.open
            import webbrowser
            webbrowser.open(download_url)
```


**Implementation:** inside `main.py`, replace only `MainWindow._show_update_dialog`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.5. `side_bar_widgets/file_manager.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `from markdowneditor_assets import asset_path` (original line 21).


```python
from code_inteligence.qt_helpers import require_qt, qt_flags
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 2.5.1 Existing method/function `FileManager.__init__`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 24–79:**


```python
    def __init__(self, set_new_tab, main_window, parent=None):
        super(FileManager, self).__init__(None)

        self.set_new_tab = set_new_tab
        self.main_window = main_window
        
        self._rename_old_path = None
        self._rename_is_directory = False
        self.is_renaming = False
        self.current_edit_index = None

        self.manager_font = QFont("sans-serif", 13)

        self.model = GitAwareFileSystemModel(self)
        self.model.setRootPath(os.getcwd())
        # File system filters
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files | QDir.Drives)
        self.model.setReadOnly(False)
        self.setFocusPolicy(Qt.NoFocus)

        self.setFont(self.manager_font)
        self.setModel(self.model)
        self.setRootIndex(self.model.index(os.getcwd()))
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)

        # add text menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # hank
        self.clicked.connect(self.tree_view_clicked)
        self.setIndentation(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Hiding other columns except for name
        self.setHeaderHidden(True)
        self.setColumnHidden(1,True)
        self.setColumnHidden(2,True)
        self.setColumnHidden(3,True)

        # enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)

        # enable file name editing
        # renaming
        self.itemDelegate().closeEditor.connect(self._on_closeEditor)
        
        from python_editor.git_integration import GitStatusChecker
        self.git_checker = GitStatusChecker()
        self.git_checker.status_ready.connect(self._on_git_status)
        self.git_statuses = {}
```


**New version:**


```python
    def __init__(self, set_new_tab, main_window, parent=None):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super(FileManager, self).__init__(None)

        self.set_new_tab = set_new_tab
        self.main_window = main_window
        
        self._rename_old_path = None
        self._rename_is_directory = False
        self.is_renaming = False
        self.current_edit_index = None

        self.manager_font = QFont("sans-serif", 13)

        self.fs_model = GitAwareFileSystemModel(self)
        self.fs_model.setRootPath(os.getcwd())
        # File system filters
        self.fs_model.setFilter(qt_flags(QDir.Filters, QDir.Filter.NoDotAndDotDot, QDir.Filter.AllDirs, QDir.Filter.Files, QDir.Filter.Drives))
        self.fs_model.setReadOnly(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setFont(self.manager_font)
        self.setModel(self.fs_model)
        self.setRootIndex(self.fs_model.index(os.getcwd()))
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)

        # add text menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # hank
        self.clicked.connect(self.tree_view_clicked)
        self.setIndentation(10)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Hiding other columns except for name
        self.setHeaderHidden(True)
        self.setColumnHidden(1,True)
        self.setColumnHidden(2,True)
        self.setColumnHidden(3,True)

        # enable drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)

        # enable file name editing
        # renaming
        require_qt(self.itemDelegate()).closeEditor.connect(self._on_closeEditor)
        
        from python_editor.git_integration import GitStatusChecker
        self.git_checker = GitStatusChecker()
        self.git_checker.status_ready.connect(self._on_git_status)
        self.git_statuses = {}
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.2 Existing method/function `FileManager.check_git_status`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 81–83:**


```python
    def check_git_status(self):
        """Start a git status check for the current root path."""
        self.git_checker.check(self.model.rootPath())
```


**New version:**


```python
    def check_git_status(self):
        """Start a git status check for the current root path."""
        self.git_checker.check(self.fs_model.rootPath())
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.check_git_status`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.3 Existing method/function `FileManager._on_git_status`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 85–101:**


```python
    def _on_git_status(self, statuses: dict):
        """
        Store the new statuses and repaint.

        BUGFIX (Windows): the checker emits keys from Path.resolve()
        (backslash paths, e.g. C:\repo\file.py), while
        QFileSystemModel.filePath() reports FORWARD slashes
        (C:/repo/file.py). The lookup in get_git_color() never matched,
        so no file was ever colored. Normalizing both sides with
        os.path.normpath (unifies separators) + os.path.normcase
        (lowercases drive letters on Windows) makes the keys comparable.
        """
        self.git_statuses = {
            os.path.normcase(os.path.normpath(p)): code
            for p, code in statuses.items()
        }
        self.viewport().update()    # repaint with new colors
```


**New version:**


```python
    def _on_git_status(self, statuses: dict):
        """
        Store the new statuses and repaint.

        BUGFIX (Windows): the checker emits keys from Path.resolve()
        (backslash paths, e.g. C:\repo\file.py), while
        QFileSystemModel.filePath() reports FORWARD slashes
        (C:/repo/file.py). The lookup in get_git_color() never matched,
        so no file was ever colored. Normalizing both sides with
        os.path.normpath (unifies separators) + os.path.normcase
        (lowercases drive letters on Windows) makes the keys comparable.
        """
        self.git_statuses = {
            os.path.normcase(os.path.normpath(p)): code
            for p, code in statuses.items()
        }
        require_qt(self.viewport()).update()    # repaint with new colors
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager._on_git_status`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.4 Existing method/function `FileManager.tree_view_clicked`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 115–119:**


```python
    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = Path(path)
        if p.is_file():
            self.set_new_tab(p)
```


**New version:**


```python
    def tree_view_clicked(self, index: QModelIndex):
        """Open the clicked filesystem item when its model path identifies a file.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        path = self.fs_model.filePath(index)
        p = Path(path)
        if p.is_file():
            self.set_new_tab(p)
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.tree_view_clicked`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.5 Existing method/function `FileManager.show_context_menu`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 128–155:**


```python
    def show_context_menu(self, pos: QPoint):
        ix = self.indexAt(pos)
        menu = QMenu()
        menu.addAction("New File")
        menu.addAction("New Folder")
        menu.addAction("Open In File Manager")

        if ix.column() == 0:
            menu.addAction("Rename")
            menu.addAction("Delete")

        action = menu.exec_(self.viewport().mapToGlobal(pos))

        if not action:
            return

        if action.text() == "Rename":
            self.action_rename(ix)
        elif action.text() == "Delete":
            self.action_delete(ix)
        elif action.text() == "New Folder":
            self.action_new_folder(ix)
        elif action.text() == "New File":
            self.action_new_file(ix)
        elif action.text() == "Open In File Manager":
            self.action_open_in_file_manager(ix)
        else:
            pass
```


**New version:**


```python
    def show_context_menu(self, pos: QPoint):
        """Build and show the filesystem actions available at the clicked position.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        ix = self.indexAt(pos)
        menu = QMenu()
        menu.addAction("New File")
        menu.addAction("New Folder")
        menu.addAction("Open In File Manager")

        if ix.column() == 0:
            menu.addAction("Rename")
            menu.addAction("Delete")

        action = menu.exec_(require_qt(self.viewport()).mapToGlobal(pos))

        if not action:
            return

        if action.text() == "Rename":
            self.action_rename(ix)
        elif action.text() == "Delete":
            self.action_delete(ix)
        elif action.text() == "New Folder":
            self.action_new_folder(ix)
        elif action.text() == "New File":
            self.action_new_file(ix)
        elif action.text() == "Open In File Manager":
            self.action_open_in_file_manager(ix)
        else:
            pass
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.show_context_menu`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.6 Existing method/function `FileManager.show_dialog`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.


**Old version — original lines 157–168:**


```python
    def show_dialog(self, title, msg) -> int:
        """Display a consistently styled destructive-operation prompt."""
        dialog = QMessageBox(self)
        dialog.setFont(self.manager_font)
        dialog.font().setPointSize(13)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(QIcon(asset_path("icons/close-icon.svg")))
        dialog.setText(msg)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)
        dialog.setIcon(QMessageBox.Warning)
        return dialog.exec_()
```


**New version:**


```python
    def show_dialog(self, title, msg) -> int:
        """Display a consistently styled destructive-operation prompt."""
        dialog = QMessageBox(self)
        dialog.setFont(self.manager_font)
        dialog.font().setPointSize(13)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(QIcon(asset_path("icons/close-icon.svg")))
        dialog.setText(msg)
        dialog.setStandardButtons(qt_flags(QMessageBox.StandardButtons, QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No))
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        dialog.setIcon(QMessageBox.Icon.Warning)
        return dialog.exec_()
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.show_dialog`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.7 Existing method/function `FileManager.rename_file_with_index`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.

A cancelled/incomplete rename has no model index. Return before passing None to QFileSystemModel.filePath.


**Old version — original lines 170–196:**


```python
    def rename_file_with_index(self):
        """
        Notify MainWindow after QFileSystemModel completes a rename.
        
        QFileSystemModel performs the actual disk rename. This method only
        propagates the changed path to any editor tabs that represent it.
        """
        try:
            old_path = self._rename_old_path
            if old_path is None:
                return
            new_path = Path(
                self.model.filePath(self.current_edit_index)
            )

            if new_path == old_path:
                return
            self.main_window.on_file_rename(
                old_path=old_path,
                new_path=new_path,
                is_directory=self._rename_is_directory,
            )
        finally:
            self._rename_old_path = None
            self._rename_is_directory = False
            self.current_edit_index = None
            self.is_renaming = False
```


**New version:**


```python
    def rename_file_with_index(self):
        """
        Notify MainWindow after QFileSystemModel completes a rename.
        
        QFileSystemModel performs the actual disk rename. This method only
        propagates the changed path to any editor tabs that represent it.
        """
        try:
            old_path = self._rename_old_path
            if old_path is None or self.current_edit_index is None:
                return
            new_path = Path(
                self.fs_model.filePath(self.current_edit_index)
            )

            if new_path == old_path:
                return
            self.main_window.on_file_rename(
                old_path=old_path,
                new_path=new_path,
                is_directory=self._rename_is_directory,
            )
        finally:
            self._rename_old_path = None
            self._rename_is_directory = False
            self.current_edit_index = None
            self.is_renaming = False
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.rename_file_with_index`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.8 Existing method/function `FileManager.action_rename`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 198–207:**


```python
    def action_rename(self, ix):
        """Starts QFileSystemModel inline rename and remember the original path."""
        if not ix.isValid():
            return
        
        self._rename_old_path = Path(self.model.filePath(ix))
        self._rename_is_directory = self.model.isDir(ix)
        self.current_edit_index = ix
        self.is_renaming = True
        self.edit(ix)
```


**New version:**


```python
    def action_rename(self, ix):
        """Starts QFileSystemModel inline rename and remember the original path."""
        if not ix.isValid():
            return
        
        self._rename_old_path = Path(self.fs_model.filePath(ix))
        self._rename_is_directory = self.fs_model.isDir(ix)
        self.current_edit_index = ix
        self.is_renaming = True
        self.edit(ix)
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.action_rename`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.9 Existing method/function `FileManager.action_delete`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 223–308:**


```python
    def action_delete(self, index: QModelIndex):
        """Stage all paths, then close tabs and commit permanent deletion.

        Prompts occur before touching disk, but tabs remain alive until every
        staging rename succeeds. A failed stage can therefore restore paths
        without losing editor widgets or discarded in-memory buffers.
        """
        if not index.isValid():
            return

        rows = list(self.selectionModel().selectedRows())
        if index not in rows:
            self.selectionModel().clearSelection()
            self.selectionModel().select(
                index,
                QItemSelectionModel.Select | QItemSelectionModel.Rows,
            )
            rows = [index]

        selected = [(Path(self.model.filePath(row)), self.model.isDir(row)) for row in rows]
        targets = [
            (path, is_dir)
            for path, is_dir in selected
            if not any(other != path and other in path.parents for other, _ in selected)
        ]
        label = f"'{targets[0][0].name}'" if len(targets) == 1 else f"{len(targets)} selected items"
        answer = self.show_dialog(
            "Permanent Delete",
            f"Permanently delete {label}? This cannot be undone.",
        )
        if answer != QMessageBox.Yes:
            return

        # Gather all Save/Discard/Cancel decisions first. Save is performed now;
        # Discard does not close the editor until staging succeeds.
        for path, is_directory in targets:
            if not self.main_window.can_close_editors_for_path(path, is_directory=is_directory):
                return

        staged = []
        try:
            for path, _is_directory in targets:
                temporary = path.with_name(
                    f".{path.name}.markdowneditor-delete-{uuid4().hex}"
                )
                path.rename(temporary)
                staged.append((path, temporary))
        except OSError as error:
            rollback_errors = []
            for original, temporary in reversed(staged):
                try:
                    temporary.rename(original)
                except OSError as rollback_error:
                    rollback_errors.append(str(rollback_error))
            details = "\n".join(rollback_errors)
            QMessageBox.critical(
                self,
                "Delete",
                f"Nothing was deleted because staging failed:\n{error}"
                + (f"\nRollback errors:\n{details}" if details else ""),
            )
            return

        # Every disk target is now staged. Closing cannot invalidate rollback,
        # and no prompt is repeated because decisions were collected above.
        for path, is_directory in targets:
            self.main_window.close_editors_for_path(
                path,
                is_directory=is_directory,
                prompt=False,
            )

        cleanup_errors = []
        for original, temporary in staged:
            try:
                self.delete_file(temporary)
            except OSError as error:
                # The hidden staged path remains available for manual recovery.
                cleanup_errors.append(f"{original.name}: {error}")
        if cleanup_errors:
            QMessageBox.critical(
                self,
                "Delete cleanup",
                "Some staged recovery items could not be removed:\n"
                + "\n".join(cleanup_errors),
            )
```


**New version:**


```python
    def action_delete(self, index: QModelIndex):
        """Stage all paths, then close tabs and commit permanent deletion.

        Prompts occur before touching disk, but tabs remain alive until every
        staging rename succeeds. A failed stage can therefore restore paths
        without losing editor widgets or discarded in-memory buffers.
        """
        if not index.isValid():
            return

        rows = list(require_qt(self.selectionModel()).selectedRows())
        if index not in rows:
            require_qt(self.selectionModel()).clearSelection()
            require_qt(self.selectionModel()).select(
                index,
                qt_flags(QItemSelectionModel.SelectionFlags, QItemSelectionModel.SelectionFlag.Select, QItemSelectionModel.SelectionFlag.Rows),
            )
            rows = [index]

        selected = [(Path(self.fs_model.filePath(row)), self.fs_model.isDir(row)) for row in rows]
        targets = [
            (path, is_dir)
            for path, is_dir in selected
            if not any(other != path and other in path.parents for other, _ in selected)
        ]
        label = f"'{targets[0][0].name}'" if len(targets) == 1 else f"{len(targets)} selected items"
        answer = self.show_dialog(
            "Permanent Delete",
            f"Permanently delete {label}? This cannot be undone.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        # Gather all Save/Discard/Cancel decisions first. Save is performed now;
        # Discard does not close the editor until staging succeeds.
        for path, is_directory in targets:
            if not self.main_window.can_close_editors_for_path(path, is_directory=is_directory):
                return

        staged = []
        try:
            for path, _is_directory in targets:
                temporary = path.with_name(
                    f".{path.name}.markdowneditor-delete-{uuid4().hex}"
                )
                path.rename(temporary)
                staged.append((path, temporary))
        except OSError as error:
            rollback_errors = []
            for original, temporary in reversed(staged):
                try:
                    temporary.rename(original)
                except OSError as rollback_error:
                    rollback_errors.append(str(rollback_error))
            details = "\n".join(rollback_errors)
            QMessageBox.critical(
                self,
                "Delete",
                f"Nothing was deleted because staging failed:\n{error}"
                + (f"\nRollback errors:\n{details}" if details else ""),
            )
            return

        # Every disk target is now staged. Closing cannot invalidate rollback,
        # and no prompt is repeated because decisions were collected above.
        for path, is_directory in targets:
            self.main_window.close_editors_for_path(
                path,
                is_directory=is_directory,
                prompt=False,
            )

        cleanup_errors = []
        for original, temporary in staged:
            try:
                self.delete_file(temporary)
            except OSError as error:
                # The hidden staged path remains available for manual recovery.
                cleanup_errors.append(f"{original.name}: {error}")
        if cleanup_errors:
            QMessageBox.critical(
                self,
                "Delete cleanup",
                "Some staged recovery items could not be removed:\n"
                + "\n".join(cleanup_errors),
            )
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.action_delete`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.10 Existing method/function `FileManager.action_new_file`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 310–323:**


```python
    def action_new_file(self, ix: QModelIndex):
        root_path = self.model.rootPath()
        if ix.column() != -1 and self.model.isDir(ix):
            self.expand(ix)
            root_path = self.model.filePath(ix)

        f = Path(root_path) / "file"
        count = 1
        while f.exists():
            f = Path(f.parent / f"file{count}")
            count +=1
        f.touch()
        idx = self.model.index(str(f.absolute()))
        self.edit(idx)
```


**New version:**


```python
    def action_new_file(self, ix: QModelIndex):
        """Create a file using the file manager action and refresh the model.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        root_path = self.fs_model.rootPath()
        if ix.column() != -1 and self.fs_model.isDir(ix):
            self.expand(ix)
            root_path = self.fs_model.filePath(ix)

        f = Path(root_path) / "file"
        count = 1
        while f.exists():
            f = Path(f.parent / f"file{count}")
            count +=1
        f.touch()
        idx = self.fs_model.index(str(f.absolute()))
        self.edit(idx)
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.action_new_file`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.11 Existing method/function `FileManager.action_new_folder`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 325–337:**


```python
    def action_new_folder(self, ix=None):
        parent = Path(self.model.rootPath())
        if ix is not None and ix.isValid():
            selected = Path(self.model.filePath(ix))
            parent = selected if selected.is_dir() else selected.parent
        f = parent / "New Folder"
        count = 1
        while f.exists():
            f = Path(f.parent / f"New Folder{count}")
            count += 1
        idx = self.model.mkdir(self.model.index(str(parent)), f.name)
        # edit that index
        self.edit(idx)
```


**New version:**


```python
    def action_new_folder(self, ix=None):
        """Create a folder using the file manager action and refresh the model.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        parent = Path(self.fs_model.rootPath())
        if ix is not None and ix.isValid():
            selected = Path(self.fs_model.filePath(ix))
            parent = selected if selected.is_dir() else selected.parent
        f = parent / "New Folder"
        count = 1
        while f.exists():
            f = Path(f.parent / f"New Folder{count}")
            count += 1
        idx = self.fs_model.mkdir(self.fs_model.index(str(parent)), f.name)
        # edit that index
        self.edit(idx)
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.action_new_folder`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.12 Existing method/function `FileManager.action_open_in_file_manager`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 339–357:**


```python
    def action_open_in_file_manager(self, ix: QModelIndex):
        if not ix.isValid():
            return
        path = os.path.abspath(self.model.filePath(ix))
        is_dir = self.model.isDir(ix)
        try:
            if os.name == "nt":
                if is_dir:
                    subprocess.Popen(["explorer", path])
                else:
                    subprocess.Popen(["explorer", f"/select,{path}"])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path] if is_dir else ["open", "-R", path])
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", path if is_dir else os.path.dirname(path)])
            else:
                raise OSError(f"Unsupported OS: {os.name}")
        except OSError as error:
            QMessageBox.warning(self, "Open in file manager", str(error))
```


**New version:**


```python
    def action_open_in_file_manager(self, ix: QModelIndex):
        """Reveal the selected path in the platform file manager.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if not ix.isValid():
            return
        path = os.path.abspath(self.fs_model.filePath(ix))
        is_dir = self.fs_model.isDir(ix)
        try:
            if os.name == "nt":
                if is_dir:
                    subprocess.Popen(["explorer", path])
                else:
                    subprocess.Popen(["explorer", f"/select,{path}"])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path] if is_dir else ["open", "-R", path])
            elif os.name == "posix":
                subprocess.Popen(["xdg-open", path if is_dir else os.path.dirname(path)])
            else:
                raise OSError(f"Unsupported OS: {os.name}")
        except OSError as error:
            QMessageBox.warning(self, "Open in file manager", str(error))
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.action_open_in_file_manager`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.13 Existing method/function `FileManager.dropEvent`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 359–439:**


```python
    def dropEvent(self, event: QDropEvent) -> None:
        """Move/copy a validated batch without dereferencing symlink sources.

        Lexical paths identify the filesystem objects being manipulated.
        Resolved paths are used only for directory-containment validation.
        Copying a symlink preserves the link; moving a symlink moves the link.
        """
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        index = self.indexAt(event.pos())
        if index.isValid():
            selected = Path(self.model.filePath(index))
            target_dir = selected if selected.is_dir() else selected.parent
        else:
            target_dir = Path(self.model.rootPath())

        copy_requested = bool(event.keyboardModifiers() & Qt.ControlModifier)
        operations = []
        try:
            resolved_target_dir = target_dir.resolve(strict=True)
            for url in event.mimeData().urls():
                # absolute() preserves a symlink's identity; resolve() would
                # silently turn the operation into one on its target.
                source = Path(url.toLocalFile()).absolute()
                if not self._path_exists(source):
                    raise FileNotFoundError(f"Source does not exist: {source}")

                destination = target_dir / source.name
                if source == destination:
                    continue
                if self._path_exists(destination):
                    raise FileExistsError(f"Destination already exists: {destination}")

                # A real directory cannot be copied/moved into itself. A
                # directory symlink is treated as a link object, not traversed.
                if source.is_dir() and not source.is_symlink():
                    resolved_source = source.resolve(strict=True)
                    resolved_destination = (resolved_target_dir / source.name).resolve(
                        strict=False
                    )
                    if resolved_source in resolved_destination.parents:
                        raise OSError("Cannot copy a folder into itself")
                operations.append((source, destination))

            completed = []
            for source, destination in operations:
                if copy_requested:
                    if source.is_symlink():
                        # copy2(..., follow_symlinks=False) recreates the link
                        # rather than copying the target's bytes/tree.
                        shutil.copy2(source, destination, follow_symlinks=False)
                    elif source.is_dir():
                        shutil.copytree(source, destination)
                    else:
                        shutil.copy2(source, destination)
                else:
                    shutil.move(str(source), str(destination))
                completed.append((source, destination))
        except OSError as error:
            rollback_errors = []
            for source, destination in reversed(locals().get("completed", [])):
                try:
                    if copy_requested:
                        self.delete_file(destination)
                    elif self._path_exists(destination) and not self._path_exists(source):
                        shutil.move(str(destination), str(source))
                except OSError as rollback_error:
                    rollback_errors.append(str(rollback_error))
            details = "\n".join(rollback_errors)
            QMessageBox.critical(
                self,
                "File operation",
                str(error) + (f"\nRollback errors:\n{details}" if details else ""),
            )
            event.ignore()
            return

        event.setDropAction(Qt.CopyAction if copy_requested else Qt.MoveAction)
        event.accept()
```


**New version:**


```python
    def dropEvent(self, event: QDropEvent) -> None:
        """Move/copy a validated batch without dereferencing symlink sources.

        Lexical paths identify the filesystem objects being manipulated.
        Resolved paths are used only for directory-containment validation.
        Copying a symlink preserves the link; moving a symlink moves the link.
        """
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        index = self.indexAt(event.pos())
        if index.isValid():
            selected = Path(self.fs_model.filePath(index))
            target_dir = selected if selected.is_dir() else selected.parent
        else:
            target_dir = Path(self.fs_model.rootPath())

        copy_requested = bool(event.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier)
        operations = []
        try:
            resolved_target_dir = target_dir.resolve(strict=True)
            for url in event.mimeData().urls():
                # absolute() preserves a symlink's identity; resolve() would
                # silently turn the operation into one on its target.
                source = Path(url.toLocalFile()).absolute()
                if not self._path_exists(source):
                    raise FileNotFoundError(f"Source does not exist: {source}")

                destination = target_dir / source.name
                if source == destination:
                    continue
                if self._path_exists(destination):
                    raise FileExistsError(f"Destination already exists: {destination}")

                # A real directory cannot be copied/moved into itself. A
                # directory symlink is treated as a link object, not traversed.
                if source.is_dir() and not source.is_symlink():
                    resolved_source = source.resolve(strict=True)
                    resolved_destination = (resolved_target_dir / source.name).resolve(
                        strict=False
                    )
                    if resolved_source in resolved_destination.parents:
                        raise OSError("Cannot copy a folder into itself")
                operations.append((source, destination))

            completed = []
            for source, destination in operations:
                if copy_requested:
                    if source.is_symlink():
                        # copy2(..., follow_symlinks=False) recreates the link
                        # rather than copying the target's bytes/tree.
                        shutil.copy2(source, destination, follow_symlinks=False)
                    elif source.is_dir():
                        shutil.copytree(source, destination)
                    else:
                        shutil.copy2(source, destination)
                else:
                    shutil.move(str(source), str(destination))
                completed.append((source, destination))
        except OSError as error:
            rollback_errors = []
            for source, destination in reversed(locals().get("completed", [])):
                try:
                    if copy_requested:
                        self.delete_file(destination)
                    elif self._path_exists(destination) and not self._path_exists(source):
                        shutil.move(str(destination), str(source))
                except OSError as rollback_error:
                    rollback_errors.append(str(rollback_error))
            details = "\n".join(rollback_errors)
            QMessageBox.critical(
                self,
                "File operation",
                str(error) + (f"\nRollback errors:\n{details}" if details else ""),
            )
            event.ignore()
            return

        event.setDropAction(Qt.DropAction.CopyAction if copy_requested else Qt.DropAction.MoveAction)
        event.accept()
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.dropEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.14 Existing method/function `FileManager.current_folder`

`fs_model` is the filesystem-model instance. The old attribute named `model` hid `QTreeView.model()`, so the checker treated model access as a method conflict. Every affected caller shown here now uses `fs_model`.


**Old version — original lines 441–448:**


```python
    @property
    def current_folder(self) -> Path | None:
        """Return the current project-tree root as a resolved directory."""
        raw_path = self.model.rootPath()
        if not raw_path:
            return None
        path = Path(raw_path).resolve()
        return path if path.is_dir() else None
```


**New version:**


```python
    @property
    def current_folder(self) -> Path | None:
        """Return the current project-tree root as a resolved directory."""
        raw_path = self.fs_model.rootPath()
        if not raw_path:
            return None
        path = Path(raw_path).resolve()
        return path if path.is_dir() else None
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `FileManager.current_folder`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.5.15 Existing method/function `GitAwareFileSystemModel.data`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 469–474:**


```python
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.ForegroundRole:
            color = self.file_manager.get_git_color(self.filePath(index))
            if color:
                return QColor(color)
        return super().data(index, role)
```


**New version:**


```python
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Return Git foreground colors while delegating other model roles to Qt.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if role == Qt.ItemDataRole.ForegroundRole:
            color = self.file_manager.get_git_color(self.filePath(index))
            if color:
                return QColor(color)
        return super().data(index, role)
```


**Implementation:** inside `side_bar_widgets/file_manager.py`, replace only `GitAwareFileSystemModel.data`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.6. `code_inteligence/command_palette.py`


#### Imports and declarations outside methods


**Declaration change 1, original line 2. Old:**


```python
from PyQt5.QtWidgets import QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout
```


**New:**


```python
from PyQt5.QtWidgets import QDialog, QMainWindow, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout
```


**Implementation:** replace exactly this declaration/block; keep surrounding code.


**Import/declaration addition 2:** insert immediately after `from code_inteligence.command_regristry import Command, CommandRegistry` (original line 4).


```python

from code_inteligence.qt_helpers import require_qt
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 2.6.1 Existing method/function `CommandPaletteDialog.__init__`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 9–26:**


```python
    def __init__(self, registry: CommandRegistry, parent=None):
        """Build a search field and result list bound to the shared command registry."""
        super().__init__(parent, Qt.Popup)
        self.registry = registry
        self.setMinimumWidth(620)
        
        layout = QVBoxLayout(self)
        
        self.query = QLineEdit(self)
        self.query.setPlaceholderText("Type a command...")
        self.results = QListWidget(self)
        
        layout.addWidget(self.query)
        layout.addWidget(self.results)
        
        self.query.textChanged.connect(self._refill)
        self.query.returnPressed.connect(self._execute_current)
        self.results.itemActivated.connect(lambda _item: self._execute_current())
```


**New version:**


```python
    def __init__(self, registry: CommandRegistry, parent=None):
        """Build a search field and result list bound to the shared command registry."""
        super().__init__(parent, Qt.WindowType.Popup)
        self.registry = registry
        self.setMinimumWidth(620)
        
        layout = QVBoxLayout(self)
        
        self.query = QLineEdit(self)
        self.query.setPlaceholderText("Type a command...")
        self.results = QListWidget(self)
        
        layout.addWidget(self.query)
        layout.addWidget(self.results)
        
        self.query.textChanged.connect(self._refill)
        self.query.returnPressed.connect(self._execute_current)
        self.results.itemActivated.connect(lambda _item: self._execute_current())
```


**Implementation:** inside `code_inteligence/command_palette.py`, replace only `CommandPaletteDialog.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.6.2 Existing method/function `CommandPaletteDialog.open_palette`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

Check the palette parent before calling its main-window menu API; QObject.parent() does not promise a QMainWindow.


**Old version — original lines 28–35:**


```python
    def open_palette(self) -> None:
        """Refresh live menu actions, reset the query and focus the popup search field."""
        self.registry.refresh_menus(self.parent().menuBar())
        self.query.clear()
        self._refill("")
        self.show()
        self.raise_()
        self.query.setFocus()
```


**New version:**


```python
    def open_palette(self) -> None:
        """Refresh live menu actions, reset the query and focus the popup search field."""
        owner = self.parent()
        if not isinstance(owner, QMainWindow):
            raise RuntimeError("The command palette requires a main-window parent")
        self.registry.refresh_menus(require_qt(owner.menuBar()))
        self.query.clear()
        self._refill("")
        self.show()
        self.raise_()
        self.query.setFocus()
```


**Implementation:** inside `code_inteligence/command_palette.py`, replace only `CommandPaletteDialog.open_palette`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.6.3 Existing method/function `CommandPaletteDialog._refill`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.

Correct the actual QListWidgetItem API spelling from `flag()` to `flags()`. The old call would raise AttributeError when this path executes.


**Old version — original lines 37–51:**


```python
    def _refill(self, query: str) -> None:
        """Filter by all query tokens while displaying current shortcuts and disabled state."""
        tokens = query.casefold().split()
        self.results.clear()
        for command in self.registry.commands():
            if all(token in command.searchable_text for token in tokens):
                shortcut = command.action.shortcut().toString()
                suffix = f"    {shortcut}" if shortcut else ""
                item = QListWidgetItem(f"{command.category}: {command.label}{suffix}")
                item.setData(Qt.UserRole, command)
                item.setFlags(item.flags() | Qt.ItemIsEnabled if command.action.isEnabled() else item.flag() & ~Qt.ItemIsEnabled)
                self.results.addItem(item)
        
        if self.results.count():
            self.results.setCurrentRow(0)
```


**New version:**


```python
    def _refill(self, query: str) -> None:
        """Filter by all query tokens while displaying current shortcuts and disabled state."""
        tokens = query.casefold().split()
        self.results.clear()
        for command in self.registry.commands():
            if all(token in command.searchable_text for token in tokens):
                shortcut = command.action.shortcut().toString()
                suffix = f"    {shortcut}" if shortcut else ""
                item = QListWidgetItem(f"{command.category}: {command.label}{suffix}")
                item.setData(Qt.ItemDataRole.UserRole, command)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled if command.action.isEnabled() else item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.results.addItem(item)
        
        if self.results.count():
            self.results.setCurrentRow(0)
```


**Implementation:** inside `code_inteligence/command_palette.py`, replace only `CommandPaletteDialog._refill`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.6.4 Existing method/function `CommandPaletteDialog._execute_current`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 53–60:**


```python
    def _execute_current(self) -> None:
        """Close the popup and trigger the selected existing action only when enabled."""
        item = self.results.currentItem()
        command: Command | None = item.data(Qt.UserRole) if item else None
        if command is None or not command.action.isEnabled():
            return
        self.accept()
        command.action.trigger()
```


**New version:**


```python
    def _execute_current(self) -> None:
        """Close the popup and trigger the selected existing action only when enabled."""
        item = self.results.currentItem()
        command: Command | None = item.data(Qt.ItemDataRole.UserRole) if item else None
        if command is None or not command.action.isEnabled():
            return
        self.accept()
        command.action.trigger()
```


**Implementation:** inside `code_inteligence/command_palette.py`, replace only `CommandPaletteDialog._execute_current`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.7. `code_inteligence/documentation_popup.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QPlainTextEdit, QVBoxLayout` (original line 3).


```python

from code_inteligence.qt_helpers import require_qt, qt_flags
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 2.7.1 Existing method/function `DocumentationPopup.__init__`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 18–123:**


```python
    def __init__(self, parent=None):
        """Create a persistent documentation window with a draggable heading."""
        # Tool windows do not use Qt's automatic tooltip timeout/dismissal.
        super().__init__(
            parent,
            Qt.ToolTip | Qt.FramelessWindowHint,
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self._drag_origin = None
        self._drag_moved = False
        # Observe clicks throughout this application, including other docks.
        # Qt removes this filter automatically when the popup is destroyed.
        QApplication.instance().installEventFilter(self)
        # The object name is used by the stylesheet selector:
        # QFrame#DocumentationPopup (...)
        self.setObjectName("DocumentationPopup")
        
        # The popup must never take keyboard focus away from QScintilla.
        # The user should still be able to type while the popup is visible.
        self.setFocusPolicy(Qt.NoFocus)
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumWidth(self.MAX_WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)
        self.setMaximumHeight(self.MAX_HEIGHT)
        
        # QVBoxLayout stacks child widgets vertically:
        # title label at top, documentation editor below it.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)
        
        # The first line of Jedi output is used as a short heading,
        # for example: "Path" or "len (function)".
        self.title_label = QLabel(self)
        self.title_label.setCursor(Qt.SizeAllCursor)
        self.title_label.setToolTip("Drag to move, left-click to dismiss")
        
        # Display angle brackets, ampersands and similar characters
        # literally instead of allowing QLabel to interpret them as HTML.
        self.title_label.setTextFormat(Qt.PlainText)
        self.title_label.setWordWrap(True)
        
        # QPlainTextEdit is scrollable and preserves code/docstring spacing.
        self.body_edit = QPlainTextEdit(self)
        self.body_edit.setReadOnly(True)
        
        # Generate documentation does not need an undo history.
        self.body_edit.setUndoRedoEnabled(False)
        
        # A user may select/copy text, but the widget never takes focus.
        self.body_edit.setFocusPolicy(Qt.NoFocus)
        
        # Wrap normal prose at the popup width. 
        # This avoides requiring a horizontal scrollbar for ordinary paragraphs
        self.body_edit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        
        # This height forces long documentation into the scrollable viewport.
        self.body_edit.setMaximumHeight(300)
        
        # Use a code-oriented font for signatures and documentation examples.
        font = QFont("JetBrains Mono", 10)
        self.title_label.setFont(font)
        self.body_edit.setFont(font)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.body_edit)
        
        # The colors intentionally match the editor's dark Dracula-style UI
        self.setStyleSheet("""
            QFrame#DocumentationPopup {
                background-color: #1e1f22;
                border: 1px solid #4b5263;
                border-radius: 6px;
            }

            QLabel {
                background: transparent;
                color: #61afef;
                font-weight: bold;
            }

            QPlainTextEdit {
                background-color: #181a1f;
                color: #dcdfe4;
                border: 1px solid #30343d;
                border-radius: 4px;
                padding: 6px;
                selection-background-color: #3d424d;
            }

            QScrollBar:vertical {
                background-color: #1e1f22;
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background-color: #4b5263;
                border-radius: 4px;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #636d83;
            }
        """)
```


**New version:**


```python
    def __init__(self, parent=None):
        """Create a persistent documentation window with a draggable heading."""
        # Tool windows do not use Qt's automatic tooltip timeout/dismissal.
        super().__init__(
            parent,
            qt_flags(Qt.WindowFlags, Qt.WindowType.ToolTip, Qt.WindowType.FramelessWindowHint),
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._drag_origin = None
        self._drag_moved = False
        # Observe clicks throughout this application, including other docks.
        # Qt removes this filter automatically when the popup is destroyed.
        QApplication.instance().installEventFilter(self)
        # The object name is used by the stylesheet selector:
        # QFrame#DocumentationPopup (...)
        self.setObjectName("DocumentationPopup")
        
        # The popup must never take keyboard focus away from QScintilla.
        # The user should still be able to type while the popup is visible.
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumWidth(self.MAX_WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)
        self.setMaximumHeight(self.MAX_HEIGHT)
        
        # QVBoxLayout stacks child widgets vertically:
        # title label at top, documentation editor below it.
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)
        
        # The first line of Jedi output is used as a short heading,
        # for example: "Path" or "len (function)".
        self.title_label = QLabel(self)
        self.title_label.setCursor(Qt.CursorShape.SizeAllCursor)
        self.title_label.setToolTip("Drag to move, left-click to dismiss")
        
        # Display angle brackets, ampersands and similar characters
        # literally instead of allowing QLabel to interpret them as HTML.
        self.title_label.setTextFormat(Qt.TextFormat.PlainText)
        self.title_label.setWordWrap(True)
        
        # QPlainTextEdit is scrollable and preserves code/docstring spacing.
        self.body_edit = QPlainTextEdit(self)
        self.body_edit.setReadOnly(True)
        
        # Generate documentation does not need an undo history.
        self.body_edit.setUndoRedoEnabled(False)
        
        # A user may select/copy text, but the widget never takes focus.
        self.body_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Wrap normal prose at the popup width. 
        # This avoides requiring a horizontal scrollbar for ordinary paragraphs
        self.body_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # This height forces long documentation into the scrollable viewport.
        self.body_edit.setMaximumHeight(300)
        
        # Use a code-oriented font for signatures and documentation examples.
        font = QFont("JetBrains Mono", 10)
        self.title_label.setFont(font)
        self.body_edit.setFont(font)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.body_edit)
        
        # The colors intentionally match the editor's dark Dracula-style UI
        self.setStyleSheet("""
            QFrame#DocumentationPopup {
                background-color: #1e1f22;
                border: 1px solid #4b5263;
                border-radius: 6px;
            }

            QLabel {
                background: transparent;
                color: #61afef;
                font-weight: bold;
            }

            QPlainTextEdit {
                background-color: #181a1f;
                color: #dcdfe4;
                border: 1px solid #30343d;
                border-radius: 4px;
                padding: 6px;
                selection-background-color: #3d424d;
            }

            QScrollBar:vertical {
                background-color: #1e1f22;
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background-color: #4b5263;
                border-radius: 4px;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #636d83;
            }
        """)
```


**Implementation:** inside `code_inteligence/documentation_popup.py`, replace only `DocumentationPopup.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.7.2 Existing method/function `DocumentationPopup.show_documentation`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 126–163:**


```python
    def show_documentation(self, global_pos, info: str):
        """Load Jedi output into the popup and display it near the cursor."""
        
        # splitlines() turns a multi-line string into a list:
        # "Path\n(class)\n\nDocs" -> ["Path", "(class)", "", "Docs"]
        lines = info.splitlines()
        
        # The first line is a compact heading. If Jedi returned an empty string
        # for any reason, use a safe fallback title.
        title = lines[0] if lines else "Documentation"
        
        # Everything after the first line goes into the scrollable body.
        # strip() removes only leading/trailing blank lines, 
        # not internal formatting or indedtation in docstring examples.
        body = "\n".join(lines[1:]).strip()
        
        self.title_label.setText(title)
        self.body_edit.setPlainText(body or "No documentation available")
        
        # Always begin a new documentation result at the top instead of
        # preserving the scrollbar position from the previously hovered item.
        self.body_edit.verticalScrollBar().setValue(0)
        
        # Ask Qt for the natural size of the layout, then clamp it to the 
        # limits above. The body edit becomes scrollable when content is tall.
        self.adjustSize()
        self.resize(
            min(max(self.width(), self.MIN_WIDTH), self.MAX_WIDTH),
            min(max(self.height(), self.MIN_HEIGHT), self.MAX_HEIGHT),
        )
        
        # Do not place the popup directly under the mouse pointer.
        # A small lower-right offset keeps the hovered identifier visible.
        offset= QPoint(16, 20)
        self.move(global_pos + offset)
        
        self.show()
        self.raise_()
```


**New version:**


```python
    def show_documentation(self, global_pos, info: str):
        """Load Jedi output into the popup and display it near the cursor."""
        
        # splitlines() turns a multi-line string into a list:
        # "Path\n(class)\n\nDocs" -> ["Path", "(class)", "", "Docs"]
        lines = info.splitlines()
        
        # The first line is a compact heading. If Jedi returned an empty string
        # for any reason, use a safe fallback title.
        title = lines[0] if lines else "Documentation"
        
        # Everything after the first line goes into the scrollable body.
        # strip() removes only leading/trailing blank lines, 
        # not internal formatting or indedtation in docstring examples.
        body = "\n".join(lines[1:]).strip()
        
        self.title_label.setText(title)
        self.body_edit.setPlainText(body or "No documentation available")
        
        # Always begin a new documentation result at the top instead of
        # preserving the scrollbar position from the previously hovered item.
        require_qt(self.body_edit.verticalScrollBar()).setValue(0)
        
        # Ask Qt for the natural size of the layout, then clamp it to the 
        # limits above. The body edit becomes scrollable when content is tall.
        self.adjustSize()
        self.resize(
            min(max(self.width(), self.MIN_WIDTH), self.MAX_WIDTH),
            min(max(self.height(), self.MIN_HEIGHT), self.MAX_HEIGHT),
        )
        
        # Do not place the popup directly under the mouse pointer.
        # A small lower-right offset keeps the hovered identifier visible.
        offset= QPoint(16, 20)
        self.move(global_pos + offset)
        
        self.show()
        self.raise_()
```


**Implementation:** inside `code_inteligence/documentation_popup.py`, replace only `DocumentationPopup.show_documentation`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.7.3 Existing method/function `DocumentationPopup.eventFilter`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 170–200:**


```python
    def eventFilter(self, watched, event):
        """
        Dismiss on left-click; reserve a heading drag for moving the window.
        
        A heading press is resolved on release: a click dismisses, a drag mooves.
        Other left presses dismiss immediately without consuming the click, so 
        editor positioning and toolbar actions still work normally.
        """
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if self.isVisible() and watched is self.title_label:
                self._drag_origin = event.globalPos()
                self._window_origin = self.pos()
                self._drag_moved = False
                return True
            # Emit even while hidden: a left click must cancel a slow Jedi lookup.
            self.dismiss()
        
        elif event.type() == QEvent.MouseMove and self._drag_origin is not None:
            delta = event.globalPos() - self._drag_origin
            if delta.manhattanLength() >= QApplication.startDragDistance():
                self._drag_moved = True
            if self._drag_moved:
                self.move(self._window_origin + delta)
            return True
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if self._drag_origin is not None:
                self._drag_origin = None
                if not self._drag_moved:
                    self.dismiss()
                return True
        return super().eventFilter(watched, event)
```


**New version:**


```python
    def eventFilter(self, watched, event):
        """
        Dismiss on left-click; reserve a heading drag for moving the window.
        
        A heading press is resolved on release: a click dismisses, a drag mooves.
        Other left presses dismiss immediately without consuming the click, so 
        editor positioning and toolbar actions still work normally.
        """
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            if self.isVisible() and watched is self.title_label:
                self._drag_origin = event.globalPos()
                self._window_origin = self.pos()
                self._drag_moved = False
                return True
            # Emit even while hidden: a left click must cancel a slow Jedi lookup.
            self.dismiss()
        
        elif event.type() == QEvent.Type.MouseMove and self._drag_origin is not None:
            delta = event.globalPos() - self._drag_origin
            if delta.manhattanLength() >= QApplication.startDragDistance():
                self._drag_moved = True
            if self._drag_moved:
                self.move(self._window_origin + delta)
            return True
        elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            if self._drag_origin is not None:
                self._drag_origin = None
                if not self._drag_moved:
                    self.dismiss()
                return True
        return super().eventFilter(watched, event)
```


**Implementation:** inside `code_inteligence/documentation_popup.py`, replace only `DocumentationPopup.eventFilter`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.8. `code_inteligence/find_replace.py`


#### 2.8.1 Existing method/function `FindReplaceBar._connect_signals`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 189–209:**


```python
    def _connect_signals(self):
        # Enter in find input -> find next
        # returnPressed is a built-in QLineEdit signal
        # Docs: https://doc.qt.io/qt-5/qlineedit.html#returnPressed
        self.find_input.returnPressed.connect(self._on_find_next)

        # Shift+Enter → find previous
        prev_find = QShortcut(QKeySequence("Shift+Return"), self.find_input)
        prev_find.setContext(Qt.WidgetShortcut)
        prev_find.activated.connect(self._on_find_prev)

        # Escape → close
        esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        esc_shortcut.activated.connect(self._on_close)
        
        # Button clicks
        self.find_next_btn.clicked.connect(self._on_find_next)
        self.find_prev_btn.clicked.connect(self._on_find_prev)
        self.replace_btn.clicked.connect(self._on_replace)
        self.replace_all_btn.clicked.connect(self._on_replace_all)
        self.close_btn.clicked.connect(self._on_close)
```


**New version:**


```python
    def _connect_signals(self):
        # Enter in find input -> find next
        # returnPressed is a built-in QLineEdit signal
        # Docs: https://doc.qt.io/qt-5/qlineedit.html#returnPressed
        """Connect the find/replace controls to their existing commands.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self.find_input.returnPressed.connect(self._on_find_next)

        # Shift+Enter → find previous
        prev_find = QShortcut(QKeySequence("Shift+Return"), self.find_input)
        prev_find.setContext(Qt.ShortcutContext.WidgetShortcut)
        prev_find.activated.connect(self._on_find_prev)

        # Escape → close
        esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        esc_shortcut.activated.connect(self._on_close)
        
        # Button clicks
        self.find_next_btn.clicked.connect(self._on_find_next)
        self.find_prev_btn.clicked.connect(self._on_find_prev)
        self.replace_btn.clicked.connect(self._on_replace)
        self.replace_all_btn.clicked.connect(self._on_replace_all)
        self.close_btn.clicked.connect(self._on_close)
```


**Implementation:** inside `code_inteligence/find_replace.py`, replace only `FindReplaceBar._connect_signals`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.9. `code_inteligence/multi_tab_view.py`


#### 2.9.1 Existing method/function `MultiTabView.__init__`

Initialize this component and its existing Qt widgets and signal connections. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 14–22:**


```python
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        
        self.setChildrenCollapsible(False)
        self.setHandleWidth(2)
        
        self._groups = []
        self._active_group = None
        self._create_group()
```


**New version:**


```python
    def __init__(self, parent=None):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__(Qt.Orientation.Horizontal, parent)
        
        self.setChildrenCollapsible(False)
        self.setHandleWidth(2)
        
        self._groups = []
        self._active_group = None
        self._create_group()
```


**Implementation:** inside `code_inteligence/multi_tab_view.py`, replace only `MultiTabView.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.9.2 Existing method/function `MultiTabView._create_group`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 24–69:**


```python
    def _create_group(self, after=None):
        """
        Creates and registers a new QTabWidget.
        
        Parameters:
            - after:  Optional existing tab group. When provided, the new group is inserted
                        Immediately after it. When omitted, the group id appended.
        
        Returns:
            - The newly created QTabWidget
        """
        group = QTabWidget(self)
        group.setTabsClosable(True)
        group.setMovable(True)
        group.setDocumentMode(True)
        group.setElideMode(Qt.ElideMiddle)
        
        group.currentChanged.connect(
            lambda index, tab_group=group:
            self._on_group_current_changed(tab_group, index)
        )
        group.tabCloseRequested.connect(
            lambda index, tab_group=group:
            self._on_group_close_requested(tab_group, index)
        )

        # Right-clicks on a tab are forwarded to MainWindow via a signal
        group.setContextMenuPolicy(Qt.CustomContextMenu)
        group.customContextMenuRequested.connect(
            lambda pos, tab_group=group:
            self.tabContextMenuRequested.emit(tab_group, pos)
        )
        
        group.tabBar().installEventFilter(self)
        
        if after is None:
            insert_position = len(self._groups)
        else:
            insert_position = self._groups.index(after) + 1
            
        self._groups.insert(insert_position, group)
        self.insertWidget(insert_position, group)
        self._set_active_group(group)
        self._resize_groups()
        
        return group
```


**New version:**


```python
    def _create_group(self, after=None):
        """
        Creates and registers a new QTabWidget.
        
        Parameters:
            - after:  Optional existing tab group. When provided, the new group is inserted
                        Immediately after it. When omitted, the group id appended.
        
        Returns:
            - The newly created QTabWidget
        """
        group = QTabWidget(self)
        group.setTabsClosable(True)
        group.setMovable(True)
        group.setDocumentMode(True)
        group.setElideMode(Qt.TextElideMode.ElideMiddle)
        
        group.currentChanged.connect(
            lambda index, tab_group=group:
            self._on_group_current_changed(tab_group, index)
        )
        group.tabCloseRequested.connect(
            lambda index, tab_group=group:
            self._on_group_close_requested(tab_group, index)
        )

        # Right-clicks on a tab are forwarded to MainWindow via a signal
        group.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        group.customContextMenuRequested.connect(
            lambda pos, tab_group=group:
            self.tabContextMenuRequested.emit(tab_group, pos)
        )
        
        group.tabBar().installEventFilter(self)
        
        if after is None:
            insert_position = len(self._groups)
        else:
            insert_position = self._groups.index(after) + 1
            
        self._groups.insert(insert_position, group)
        self.insertWidget(insert_position, group)
        self._set_active_group(group)
        self._resize_groups()
        
        return group
```


**Implementation:** inside `code_inteligence/multi_tab_view.py`, replace only `MultiTabView._create_group`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.9.3 Existing method/function `MultiTabView.eventFilter`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 71–94:**


```python
    def eventFilter(self, watched, event):
        """
        Tracks user interaction with tab bars and editor widgets.
        
        Parameters:
            watched: The Qt object that recieved the event.
            event: The even being processed
            
        Returns:
            The result of the parent eventFilter() implementation.
        """
        if event.type() in (
            QEvent.MouseButtonPress,
            QEvent.FocusIn,
        ):
            for group in self._groups:
                if watched is group.tabBar():
                    self._set_active_group(group)
                    break
                    
            group = self.group_for_editor(watched)
            if group is not None:
                self._set_active_group(group)
        return super().eventFilter(watched, event)
```


**New version:**


```python
    def eventFilter(self, watched, event):
        """
        Tracks user interaction with tab bars and editor widgets.
        
        Parameters:
            watched: The Qt object that recieved the event.
            event: The even being processed
            
        Returns:
            The result of the parent eventFilter() implementation.
        """
        if event.type() in (
            QEvent.Type.MouseButtonPress,
            QEvent.Type.FocusIn,
        ):
            for group in self._groups:
                if watched is group.tabBar():
                    self._set_active_group(group)
                    break
                    
            group = self.group_for_editor(watched)
            if group is not None:
                self._set_active_group(group)
        return super().eventFilter(watched, event)
```


**Implementation:** inside `code_inteligence/multi_tab_view.py`, replace only `MultiTabView.eventFilter`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.10. `code_settings/settings_dialog.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `from markdowneditor_assets import asset_path` (original line 11).


```python

from code_inteligence.qt_helpers import qt_flags
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 2.10.1 Existing method/function `_build_pixmaps`

Draw the small QSS images at runtime (needs a QApplication to exist, The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 114–180:**


```python
def _build_pixmaps() -> dict:
    """
    Draw the small QSS images at runtime (needs a QApplication to exist,
    which is why this is a function and not module-level code).

    Why images instead of pure QSS: styling ::indicator with a stylesheet
    suppresses the native check glyph on most platform styles (empty
    orange box), and ::up-arrow / ::down-arrow render as flat dashes on
    some styles. Baking the glyphs into 16x16 / 7x5 pixmaps makes the
    dialog render identically on Fusion AND the Windows native style.

    :return: {"CHECK_ON": path, "CHECK_OFF": path,
              "UP_ARROW": path, "DOWN_ARROW": path} - absolute file paths
             injected into SETTINGS_QSS as url() targets.
    """
    import tempfile
    from PyQt5.QtCore import Qt, QRectF
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath

    out = {}

    def _save(pix, key):
        path = str(Path(tempfile.gettempdir()) / f"cozy_settings_{key}.png")
        pix.save(path)
        # QSS url() wants forward slashes even on Windows
        out[key] = path.replace("\\", "/")

    # --- checkbox indicators ------------------------------------------- #
    for checked, key in ((True, "CHECK_ON"), (False, "CHECK_OFF")):
        pix = QPixmap(16, 16)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor("#565b66"), 1))
        p.setBrush(QBrush(QColor("#ff5700") if checked else QColor("#2b2f38")))
        p.drawRoundedRect(QRectF(0.5, 0.5, 15, 15), 3, 3)
        if checked:
            # white checkmark path
            p.setPen(QPen(QColor("#ffffff"), 2.2))
            p.setBrush(Qt.NoBrush)
            path = QPainterPath()
            path.moveTo(3.6, 8.2)
            path.lineTo(6.6, 11.2)
            path.lineTo(12.4, 4.6)
            p.drawPath(path)
        p.end()
        _save(pix, key)

    # --- spinbox arrows ------------------------------------------------- #
    for up, key in ((True, "UP_ARROW"), (False, "DOWN_ARROW")):
        pix = QPixmap(7, 5)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#bcbec4")))
        path = QPainterPath()
        if up:
            path.moveTo(0.5, 4.5); path.lineTo(6.5, 4.5); path.lineTo(3.5, 0.5)
        else:
            path.moveTo(0.5, 0.5); path.lineTo(6.5, 0.5); path.lineTo(3.5, 4.5)
        path.closeSubpath()
        p.drawPath(path)
        p.end()
        _save(pix, key)

    return out
```


**New version:**


```python
def _build_pixmaps() -> dict:
    """
    Draw the small QSS images at runtime (needs a QApplication to exist,
    which is why this is a function and not module-level code).

    Why images instead of pure QSS: styling ::indicator with a stylesheet
    suppresses the native check glyph on most platform styles (empty
    orange box), and ::up-arrow / ::down-arrow render as flat dashes on
    some styles. Baking the glyphs into 16x16 / 7x5 pixmaps makes the
    dialog render identically on Fusion AND the Windows native style.

    :return: {"CHECK_ON": path, "CHECK_OFF": path,
              "UP_ARROW": path, "DOWN_ARROW": path} - absolute file paths
             injected into SETTINGS_QSS as url() targets.
    """
    import tempfile
    from PyQt5.QtCore import Qt, QRectF
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath

    out = {}

    def _save(pix, key):
        path = str(Path(tempfile.gettempdir()) / f"cozy_settings_{key}.png")
        pix.save(path)
        # QSS url() wants forward slashes even on Windows
        out[key] = path.replace("\\", "/")

    # --- checkbox indicators ------------------------------------------- #
    for checked, key in ((True, "CHECK_ON"), (False, "CHECK_OFF")):
        pix = QPixmap(16, 16)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor("#565b66"), 1))
        p.setBrush(QBrush(QColor("#ff5700") if checked else QColor("#2b2f38")))
        p.drawRoundedRect(QRectF(0.5, 0.5, 15, 15), 3, 3)
        if checked:
            # white checkmark path
            p.setPen(QPen(QColor("#ffffff"), 2.2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            path = QPainterPath()
            path.moveTo(3.6, 8.2)
            path.lineTo(6.6, 11.2)
            path.lineTo(12.4, 4.6)
            p.drawPath(path)
        p.end()
        _save(pix, key)

    # --- spinbox arrows ------------------------------------------------- #
    for up, key in ((True, "UP_ARROW"), (False, "DOWN_ARROW")):
        pix = QPixmap(7, 5)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#bcbec4")))
        path = QPainterPath()
        if up:
            path.moveTo(0.5, 4.5); path.lineTo(6.5, 4.5); path.lineTo(3.5, 0.5)
        else:
            path.moveTo(0.5, 0.5); path.lineTo(6.5, 0.5); path.lineTo(3.5, 4.5)
        path.closeSubpath()
        p.drawPath(path)
        p.end()
        _save(pix, key)

    return out
```


**Implementation:** inside `code_settings/settings_dialog.py`, replace only `_build_pixmaps`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.10.2 Existing method/function `SettingsDialog._style_form`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 237–245:**


```python
    def _style_form(self, layout: QFormLayout) -> QFormLayout:
        """Uniform paddings/gaps for every tab's form (keeps labels from
        colliding with the padded dark inputs)."""
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setHorizontalSpacing(26)     # label <-> input gap
        layout.setVerticalSpacing(14)
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        layout.setFormAlignment(Qt.AlignTop | Qt.AlignLeft)
        return layout
```


**New version:**


```python
    def _style_form(self, layout: QFormLayout) -> QFormLayout:
        """Uniform paddings/gaps for every tab's form (keeps labels from
        colliding with the padded dark inputs)."""
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setHorizontalSpacing(26)     # label <-> input gap
        layout.setVerticalSpacing(14)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        layout.setFormAlignment(qt_flags(Qt.Alignment, Qt.AlignmentFlag.AlignTop, Qt.AlignmentFlag.AlignLeft))
        return layout
```


**Implementation:** inside `code_settings/settings_dialog.py`, replace only `SettingsDialog._style_form`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.11. `con_term/console_widget.py`


#### 2.11.1 Existing method/function `ConsoleWidget._append`

Append console output using the requested text format. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 123–133:**


```python
    def _append(self, text: str, color: str):
        cursor = self.output.textCursor() # Gets a QTextCursor pointing to the current cursor position in the output area.
        cursor.movePosition(QTextCursor.End) # Moves the cursor tp the end of the document. You always append new text at the bottom.
        
        fmt = QTextCharFormat() # Creates a new format object. This describes how text should look (font, color, weight, etc.)
        fmt.setForeground(QColor(color)) # Sets the text Color
        cursor.setCharFormat(fmt) # Applies the format to the cursor. Any text inserted after this point will use this color.
        cursor.insertText(text) # Inserts the text at the cursor position with the current format.
        
        self.output.setTextCursor(cursor) # Updates the QPlainTextEdit's cursor to your modified cursor. This is needed because the textCursor() returns a copy, not a reference. You have to set it back.
        self.output.ensureCursorVisible() # Scrolls the output area so the cursor (which is at the end) is visible. Without this, new output would appear below the visible area and you'd have to manually scroll.
```


**New version:**


```python
    def _append(self, text: str, color: str):
        """Append console output using the requested text format.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        cursor = self.output.textCursor() # Gets a QTextCursor pointing to the current cursor position in the output area.
        cursor.movePosition(QTextCursor.MoveOperation.End) # Moves the cursor tp the end of the document. You always append new text at the bottom.
        
        fmt = QTextCharFormat() # Creates a new format object. This describes how text should look (font, color, weight, etc.)
        fmt.setForeground(QColor(color)) # Sets the text Color
        cursor.setCharFormat(fmt) # Applies the format to the cursor. Any text inserted after this point will use this color.
        cursor.insertText(text) # Inserts the text at the cursor position with the current format.
        
        self.output.setTextCursor(cursor) # Updates the QPlainTextEdit's cursor to your modified cursor. This is needed because the textCursor() returns a copy, not a reference. You have to set it back.
        self.output.ensureCursorVisible() # Scrolls the output area so the cursor (which is at the end) is visible. Without this, new output would appear below the visible area and you'd have to manually scroll.
```


**Implementation:** inside `con_term/console_widget.py`, replace only `ConsoleWidget._append`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.12. `con_term/terminal_widget.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `from PyQt5.QtWidgets import QAction, QApplication, QComboBox, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget` (original line 20).


```python

from code_inteligence.qt_helpers import require_qt, qt_flags
```


**Implementation:** insert once at module/class indentation exactly as shown.


**Declaration change 2, original line 307. Old:**


```python
    _KEY_SEQUENCES = {
        Qt.Key_Up: "\x1b[A",
        Qt.Key_Down: "\x1b[B",
        Qt.Key_Right: "\x1b[C",
        Qt.Key_Left: "\x1b[D",
        Qt.Key_Home: "\x1b[H",
        Qt.Key_End: "\x1b[F",
        Qt.Key_Insert: "\x1b[2~",
        Qt.Key_Delete: "\x1b[3~",
        Qt.Key_PageUp: "\x1b[5~",
        Qt.Key_PageDown: "\x1b[6~",
        Qt.Key_F1: "\x1bOP",
        Qt.Key_F2: "\x1bOQ",
        Qt.Key_F3: "\x1bOR",
        Qt.Key_F4: "\x1bOS",
        Qt.Key_F5: "\x1b[15~",
        Qt.Key_F6: "\x1b[17~",
        Qt.Key_F7: "\x1b[18~",
        Qt.Key_F8: "\x1b[19~",
        Qt.Key_F9: "\x1b[20~",
        Qt.Key_F10: "\x1b[21~",
        Qt.Key_F11: "\x1b[23~",
        Qt.Key_F12: "\x1b[24~",
```


**New:**


```python
    _KEY_SEQUENCES: dict[int, str] = {
        Qt.Key.Key_Up: "\x1b[A",
        Qt.Key.Key_Down: "\x1b[B",
        Qt.Key.Key_Right: "\x1b[C",
        Qt.Key.Key_Left: "\x1b[D",
        Qt.Key.Key_Home: "\x1b[H",
        Qt.Key.Key_End: "\x1b[F",
        Qt.Key.Key_Insert: "\x1b[2~",
        Qt.Key.Key_Delete: "\x1b[3~",
        Qt.Key.Key_PageUp: "\x1b[5~",
        Qt.Key.Key_PageDown: "\x1b[6~",
        Qt.Key.Key_F1: "\x1bOP",
        Qt.Key.Key_F2: "\x1bOQ",
        Qt.Key.Key_F3: "\x1bOR",
        Qt.Key.Key_F4: "\x1bOS",
        Qt.Key.Key_F5: "\x1b[15~",
        Qt.Key.Key_F6: "\x1b[17~",
        Qt.Key.Key_F7: "\x1b[18~",
        Qt.Key.Key_F8: "\x1b[19~",
        Qt.Key.Key_F9: "\x1b[20~",
        Qt.Key.Key_F10: "\x1b[21~",
        Qt.Key.Key_F11: "\x1b[23~",
        Qt.Key.Key_F12: "\x1b[24~",
```


**Implementation:** replace exactly this declaration/block; keep surrounding code.


#### 2.12.1 Existing method/function `TerminalView.__init__`

Combined enum bits are constructed as the concrete Qt flags type. The helper isolates the integer-constructor gap in the generated PyQt5 stubs; the selected flag bits and runtime behavior are preserved.


**Old version — original lines 332–352:**


```python
    def __init__(self, writer: Callable[[str], None], parent: QWidget | None = None) -> None:
        """
        Create a selectable but non-editable terminal surface.
        
        Args:
            writer: Callback that accepts text to send to the PTY.
            parent: Qt owner if the view.
        """
        super().__init__(parent)
        self._writer = writer
        
        # This is the central protection rule: Qt never edits terminal output
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        
        # Terminals use fixed columns; wrapping would corrupt cursor position;
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setFocusPolicy(Qt.StrongFocus)

        # Read-only does not prevent selecting text for copying.
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
```


**New version:**


```python
    def __init__(self, writer: Callable[[str], None], parent: QWidget | None = None) -> None:
        """
        Create a selectable but non-editable terminal surface.
        
        Args:
            writer: Callback that accepts text to send to the PTY.
            parent: Qt owner if the view.
        """
        super().__init__(parent)
        self._writer = writer
        
        # This is the central protection rule: Qt never edits terminal output
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        
        # Terminals use fixed columns; wrapping would corrupt cursor position;
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Read-only does not prevent selecting text for copying.
        self.setTextInteractionFlags(qt_flags(Qt.TextInteractionFlags, Qt.TextInteractionFlag.TextSelectableByMouse, Qt.TextInteractionFlag.TextSelectableByKeyboard))
```


**Implementation:** inside `con_term/terminal_widget.py`, replace only `TerminalView.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.12.2 Existing method/function `TerminalView.keyPressEvent`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.

Describe key lookup using integer key codes, and compare modifier bits as integers. This accommodates the generated PyQt5 flag stubs without changing key sequences or AltGr handling.


**Old version — original lines 354–444:**


```python
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Translate a Qt key press into terminal input or clipboard behavior.

        Args:
            event: Qt event containing the key, modifiers, and typed text.

        The base QPlainTextEdit implementation is intentionally never called,
        because doing so could move or edit the protected document caret.
        """
        modifiers = event.modifiers()
        key = event.key()
        control = bool(modifiers & Qt.ControlModifier)
        shift = bool(modifiers & Qt.ShiftModifier)

        # Ctrl+Shift+C and Ctrl+Insert are explicit terminal copy shortcuts.
        # They never become Ctrl+C/interrupt when no selection exists.
        if (control and shift and key == Qt.Key_C) or (
                control and key == Qt.Key_Insert
        ):
            if self.textCursor().hasSelection():
                self.copy()
            return

        # Standard Ctrl+C/Cmd+C copies selected terminal output.
        if event.matches(QKeySequence.Copy) and self.textCursor().hasSelection():
            self.copy()
            return

        # Support both GUI-standard and conventional terminal paste shortcuts.
        if (
                event.matches(QKeySequence.Paste)
                or (control and shift and key == Qt.Key_V)
                or (shift and key == Qt.Key_Insert)
        ):
            self.paste_clipboard()
            return

        # Shift+PageUp/PageDown scrolls local history. Without Shift, the key
        # is sent to the foreground terminal application.
        if shift and key in (Qt.Key_PageUp, Qt.Key_PageDown):
            scrollbar = self.verticalScrollBar()
            direction = -1 if key == Qt.Key_PageUp else 1
            scrollbar.setValue(
                scrollbar.value() + direction * scrollbar.pageStep()
            )
            return

        # A terminal Enter key is carriage return, not a GUI newline insert.
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._writer("\r")
            return

        if key == Qt.Key_Backspace:
            self._writer("\x7f")
            return

        if key == Qt.Key_Tab:
            self._writer("\t")
            return

        if key == Qt.Key_Backtab:
            self._writer("\x1b[Z")
            return

        if key == Qt.Key_Escape:
            self._writer("\x1b")
            return

        sequence = self._KEY_SEQUENCES.get(key)
        if sequence is not None:
            self._writer(sequence)
            return

        # Ctrl+A..Ctrl+Z are ASCII values 1..26. This includes Ctrl+C for
        # interrupt, Ctrl+D for EOF, and Ctrl+L for clear screen.
        if (
                control
                and not (modifiers & Qt.AltModifier)
                and Qt.Key_A <= key <= Qt.Key_Z
        ):
            self._writer(chr(key - Qt.Key_A + 1))
            return

        text = event.text()
        if text and not (modifiers & Qt.MetaModifier):
            # Alt+key is encoded as Escape followed by the typed character.
            # Ctrl+Alt is left untouched so AltGr can type @, {, }, and similar
            # characters on international Windows keyboards.
            if modifiers & Qt.AltModifier and not control:
                text = "\x1b" + text
            self._writer(text)
```


**New version:**


```python
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Translate a Qt key press into terminal input or clipboard behavior.

        Args:
            event: Qt event containing the key, modifiers, and typed text.

        The base QPlainTextEdit implementation is intentionally never called,
        because doing so could move or edit the protected document caret.
        """
        modifiers = event.modifiers()
        key = event.key()
        control = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        shift = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)

        # Ctrl+Shift+C and Ctrl+Insert are explicit terminal copy shortcuts.
        # They never become Ctrl+C/interrupt when no selection exists.
        if (control and shift and key == Qt.Key.Key_C) or (
                control and key == Qt.Key.Key_Insert
        ):
            if self.textCursor().hasSelection():
                self.copy()
            return

        # Standard Ctrl+C/Cmd+C copies selected terminal output.
        if event.matches(QKeySequence.StandardKey.Copy) and self.textCursor().hasSelection():
            self.copy()
            return

        # Support both GUI-standard and conventional terminal paste shortcuts.
        if (
                event.matches(QKeySequence.StandardKey.Paste)
                or (control and shift and key == Qt.Key.Key_V)
                or (shift and key == Qt.Key.Key_Insert)
        ):
            self.paste_clipboard()
            return

        # Shift+PageUp/PageDown scrolls local history. Without Shift, the key
        # is sent to the foreground terminal application.
        if shift and key in (Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
            scrollbar = require_qt(self.verticalScrollBar())
            direction = -1 if key == Qt.Key.Key_PageUp else 1
            scrollbar.setValue(
                scrollbar.value() + direction * scrollbar.pageStep()
            )
            return

        # A terminal Enter key is carriage return, not a GUI newline insert.
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._writer("\r")
            return

        if key == Qt.Key.Key_Backspace:
            self._writer("\x7f")
            return

        if key == Qt.Key.Key_Tab:
            self._writer("\t")
            return

        if key == Qt.Key.Key_Backtab:
            self._writer("\x1b[Z")
            return

        if key == Qt.Key.Key_Escape:
            self._writer("\x1b")
            return

        sequence = self._KEY_SEQUENCES.get(key)
        if sequence is not None:
            self._writer(sequence)
            return

        # Ctrl+A..Ctrl+Z are ASCII values 1..26. This includes Ctrl+C for
        # interrupt, Ctrl+D for EOF, and Ctrl+L for clear screen.
        if (
                control
                and not int(modifiers & Qt.KeyboardModifier.AltModifier)
                and Qt.Key.Key_A <= key <= Qt.Key.Key_Z
        ):
            self._writer(chr(key - Qt.Key.Key_A + 1))
            return

        text = event.text()
        if text and not int(modifiers & Qt.KeyboardModifier.MetaModifier):
            # Alt+key is encoded as Escape followed by the typed character.
            # Ctrl+Alt is left untouched so AltGr can type @, {, }, and similar
            # characters on international Windows keyboards.
            if int(modifiers & Qt.KeyboardModifier.AltModifier) and not control:
                text = "\x1b" + text
            self._writer(text)
```


**Implementation:** inside `con_term/terminal_widget.py`, replace only `TerminalView.keyPressEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.12.3 Existing method/function `TerminalView.contextMenuEvent`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 468–499:**


```python
    def contextMenuEvent(self, event) -> None:
        """Show Copy, Paste, and Select All actions for the terminal.

        Args:
            event: Context-menu event providing the global popup position.

        The default read-only QPlainTextEdit menu disables Paste, so the menu is
        rebuilt to send pasted text through the PTY callback.
        """
        menu = self.createStandardContextMenu()
        menu.clear()

        copy_action = QAction("Copy", menu)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.setEnabled(self.textCursor().hasSelection())
        copy_action.triggered.connect(self.copy)
        menu.addAction(copy_action)

        paste_action = QAction("Paste", menu)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_clipboard)
        menu.addAction(paste_action)

        menu.addSeparator()

        select_all_action = QAction("Select All", menu)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.selectAll)
        menu.addAction(select_all_action)

        menu.exec_(event.globalPos())
        menu.deleteLater()
```


**New version:**


```python
    def contextMenuEvent(self, event) -> None:
        """Show Copy, Paste, and Select All actions for the terminal.

        Args:
            event: Context-menu event providing the global popup position.

        The default read-only QPlainTextEdit menu disables Paste, so the menu is
        rebuilt to send pasted text through the PTY callback.
        """
        menu = require_qt(self.createStandardContextMenu())
        menu.clear()

        copy_action = QAction("Copy", menu)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setEnabled(self.textCursor().hasSelection())
        copy_action.triggered.connect(self.copy)
        menu.addAction(copy_action)

        paste_action = QAction("Paste", menu)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_clipboard)
        menu.addAction(paste_action)

        menu.addSeparator()

        select_all_action = QAction("Select All", menu)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.selectAll)
        menu.addAction(select_all_action)

        menu.exec_(event.globalPos())
        menu.deleteLater()
```


**Implementation:** inside `con_term/terminal_widget.py`, replace only `TerminalView.contextMenuEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.12.4 Existing method/function `TerminalWidget._render_screen`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 916–964:**


```python
    def _render_screen(self, force_bottom: bool = False) -> None:
        """Render terminal history and the active screen into the protected view.

        Args:
            force_bottom: If True, scroll to the newest output regardless of the
                user's previous scrollbar position.

        A user reading older output remains at the same scrollbar value. A user
        already at the bottom follows new output automatically.
        """
        scrollbar = self.output.verticalScrollBar()

        # A two-pixel tolerance avoids rounding differences at the bottom.
        at_bottom = force_bottom or scrollbar.value() >= scrollbar.maximum() - 2
        old_value = scrollbar.value()

        history = [
            self._history_line_text(line, self._screen.columns)
            for line in self._screen.history.top
        ]

        # screen.display already reflects ANSI cursor movement and erasure.
        visible = [self._visible_line_text(line, row, self._screen.cursor.y, self._screen.cursor.x) for row, line in enumerate(self._screen.display)]
        self.output.setPlainText("\n".join([*history, *visible]))

        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
        else:
            scrollbar.setValue(min(old_value, scrollbar.maximum()))

        if at_bottom and not self._screen.cursor.hidden:
            # History lines appear before terminal-screen row zero.
            block_number = len(history) + self._screen.cursor.y
            block = self.output.document().findBlockByNumber(block_number)

            if block.isValid():
                cursor = QTextCursor(block)

                # A trimmed row can be shorter than the virtual cursor column.
                safe_column = min(
                    self._screen.cursor.x,
                    max(0, block.length() - 1),
                )
                cursor.movePosition(
                    QTextCursor.Right,
                    QTextCursor.MoveAnchor,
                    safe_column,
                )
                self.output.setTextCursor(cursor)
```


**New version:**


```python
    def _render_screen(self, force_bottom: bool = False) -> None:
        """Render terminal history and the active screen into the protected view.

        Args:
            force_bottom: If True, scroll to the newest output regardless of the
                user's previous scrollbar position.

        A user reading older output remains at the same scrollbar value. A user
        already at the bottom follows new output automatically.
        """
        scrollbar = require_qt(self.output.verticalScrollBar())

        # A two-pixel tolerance avoids rounding differences at the bottom.
        at_bottom = force_bottom or scrollbar.value() >= scrollbar.maximum() - 2
        old_value = scrollbar.value()

        history = [
            self._history_line_text(line, self._screen.columns)
            for line in self._screen.history.top
        ]

        # screen.display already reflects ANSI cursor movement and erasure.
        visible = [self._visible_line_text(line, row, self._screen.cursor.y, self._screen.cursor.x) for row, line in enumerate(self._screen.display)]
        self.output.setPlainText("\n".join([*history, *visible]))

        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
        else:
            scrollbar.setValue(min(old_value, scrollbar.maximum()))

        if at_bottom and not self._screen.cursor.hidden:
            # History lines appear before terminal-screen row zero.
            block_number = len(history) + self._screen.cursor.y
            block = require_qt(self.output.document()).findBlockByNumber(block_number)

            if block.isValid():
                cursor = QTextCursor(block)

                # A trimmed row can be shorter than the virtual cursor column.
                safe_column = min(
                    self._screen.cursor.x,
                    max(0, block.length() - 1),
                )
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.MoveAnchor,
                    safe_column,
                )
                self.output.setTextCursor(cursor)
```


**Implementation:** inside `con_term/terminal_widget.py`, replace only `TerminalWidget._render_screen`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.12.5 Existing method/function `TerminalWidget._measure_terminal_size`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 1002–1018:**


```python
    def _measure_terminal_size(self) -> None:
        """Convert the output viewport from pixels to character cells."""
        metrics = self.output.fontMetrics()

        # Monospace "M" width represents one terminal column.
        cell_width = max(1, metrics.horizontalAdvance("M"))
        cell_height = max(1, metrics.lineSpacing())
        viewport = self.output.viewport().size()

        self._columns = max(
            self._MIN_COLUMNS,
            viewport.width() // cell_width,
            )
        self._rows = max(
            self._MIN_ROWS,
            viewport.height() // cell_height,
            )
```


**New version:**


```python
    def _measure_terminal_size(self) -> None:
        """Convert the output viewport from pixels to character cells."""
        metrics = self.output.fontMetrics()

        # Monospace "M" width represents one terminal column.
        cell_width = max(1, metrics.horizontalAdvance("M"))
        cell_height = max(1, metrics.lineSpacing())
        viewport = require_qt(self.output.viewport()).size()

        self._columns = max(
            self._MIN_COLUMNS,
            viewport.width() // cell_width,
            )
        self._rows = max(
            self._MIN_ROWS,
            viewport.height() // cell_height,
            )
```


**Implementation:** inside `con_term/terminal_widget.py`, replace only `TerminalWidget._measure_terminal_size`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.13. `cozy/cat_controller.py`


#### 2.13.1 Existing method/function `CatController.__init__`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 141–172:**


```python
    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("CodeEditor", "CodeEditor")

        # --- C2: progress, persisted across sessions ------------------- #
        self._xp = int(self._settings.value("cat_xp", 0, type=int))
        self._pets = int(self._settings.value("cat_pets", 0, type=int))

        # --- animation state ------------------------------------------- #
        self._state = "idle"      # currently playing state name
        self._frame = 0           # animation frame counter (mod frame count)
        self._hat = False         # C5: party hat on/off
        self._png_sheets, self._png_frames = self._load_png_frames()

        self.setFont(QFont("Consolas", 9))
        self.setCursor(Qt.PointingHandCursor)   # C1: announces "pettable"
        self.setToolTip("pet me")

        # Frame clock: repeating, 400 ms — the animation heart. It NEVER
        # stops while the app runs; it only advances self._frame.
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(400)

        # State timeout: single-shot — how long the CURRENT state plays
        # before snapping back to idle. Two timers, two jobs; merging them
        # would freeze mid-blink or make states permanent (see docstring).
        self._state_timer = QTimer(self)
        self._state_timer.setSingleShot(True)
        self._state_timer.timeout.connect(lambda: self.set_state("idle"))

        self._render()
```


**New version:**


```python
    def __init__(self, parent=None):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__(parent)
        self._settings = QSettings("CodeEditor", "CodeEditor")

        # --- C2: progress, persisted across sessions ------------------- #
        self._xp = int(self._settings.value("cat_xp", 0, type=int))
        self._pets = int(self._settings.value("cat_pets", 0, type=int))

        # --- animation state ------------------------------------------- #
        self._state = "idle"      # currently playing state name
        self._frame = 0           # animation frame counter (mod frame count)
        self._hat = False         # C5: party hat on/off
        self._png_sheets, self._png_frames = self._load_png_frames()

        self.setFont(QFont("Consolas", 9))
        self.setCursor(Qt.CursorShape.PointingHandCursor)   # C1: announces "pettable"
        self.setToolTip("pet me")

        # Frame clock: repeating, 400 ms — the animation heart. It NEVER
        # stops while the app runs; it only advances self._frame.
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(400)

        # State timeout: single-shot — how long the CURRENT state plays
        # before snapping back to idle. Two timers, two jobs; merging them
        # would freeze mid-blink or make states permanent (see docstring).
        self._state_timer = QTimer(self)
        self._state_timer.setSingleShot(True)
        self._state_timer.timeout.connect(lambda: self.set_state("idle"))

        self._render()
```


**Implementation:** inside `cozy/cat_controller.py`, replace only `CatController.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.13.2 Existing method/function `CatController.mousePressEvent`

C1: the whole label is one big pet button. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 240–243:**


```python
    def mousePressEvent(self, event):
        """C1: the whole label is one big pet button."""
        if event.button() == Qt.LeftButton:
            self.pet()
```


**New version:**


```python
    def mousePressEvent(self, event):
        """C1: the whole label is one big pet button."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pet()
```


**Implementation:** inside `cozy/cat_controller.py`, replace only `CatController.mousePressEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.13.3 Existing method/function `CatController._render`

Paint the current frame — PNG if available for this state, The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 287–326:**


```python
    def _render(self):
        """
        Paint the current frame — PNG if available for this state,
        ASCII otherwise. C5 hat is composed in both paths; C2 idle flair
        (shades / crown / halo) decorates the ASCII idle cat by level.
        """
        # 1. SHEET MODE: play the right rect of the full strip
        sheet = self._png_sheets.get(self._state)
        if sheet is not None and not sheet.isNull():
            cell = sheet.height()               # square cells
            n = max(1, sheet.width() // cell)
            pix = sheet.copy((self._frame % n) * cell, 0, cell, cell)
            if self._hat:
                painter = QPainter(pix)
                painter.setPen(QColor("#FFD700"))
                painter.drawText(4, 12, "^")
                painter.end()
            self.setPixmap(pix.scaled(24, 24, Qt.KeepAspectRatio))
            return

        # 2. FRAME MODE: one file per frame (v1 sprites)
        pngs = self._png_frames.get(self._state)
        if pngs:
            pix = QPixmap(pngs[self._frame % len(pngs)])
            if self._hat:
                painter = QPainter(pix)
                painter.setPen(QColor("#FFD700"))
                painter.drawText(2, 6, "^")
                painter.end()
            self.setPixmap(pix.scaled(24, 24, Qt.KeepAspectRatio))
            return

        # 3. ASCII fallback
        # C2: idle ASCII cat earns flair as it levels
        flair = ["", "", " 8)", " [w]", " (o)"][min(self.level, 4)]
        hat = "^ " if self._hat else ""
        frames = ASCII_FRAMES[self._state]
        if self._state == "idle" and flair:
            frames = [frames[0] + flair, frames[1]]
        self.setText(hat + frames[self._frame % len(frames)])
```


**New version:**


```python
    def _render(self):
        """
        Paint the current frame — PNG if available for this state,
        ASCII otherwise. C5 hat is composed in both paths; C2 idle flair
        (shades / crown / halo) decorates the ASCII idle cat by level.
        """
        # 1. SHEET MODE: play the right rect of the full strip
        sheet = self._png_sheets.get(self._state)
        if sheet is not None and not sheet.isNull():
            cell = sheet.height()               # square cells
            n = max(1, sheet.width() // cell)
            pix = sheet.copy((self._frame % n) * cell, 0, cell, cell)
            if self._hat:
                painter = QPainter(pix)
                painter.setPen(QColor("#FFD700"))
                painter.drawText(4, 12, "^")
                painter.end()
            self.setPixmap(pix.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
            return

        # 2. FRAME MODE: one file per frame (v1 sprites)
        pngs = self._png_frames.get(self._state)
        if pngs:
            pix = QPixmap(pngs[self._frame % len(pngs)])
            if self._hat:
                painter = QPainter(pix)
                painter.setPen(QColor("#FFD700"))
                painter.drawText(2, 6, "^")
                painter.end()
            self.setPixmap(pix.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
            return

        # 3. ASCII fallback
        # C2: idle ASCII cat earns flair as it levels
        flair = ["", "", " 8)", " [w]", " (o)"][min(self.level, 4)]
        hat = "^ " if self._hat else ""
        frames = ASCII_FRAMES[self._state]
        if self._state == "idle" and flair:
            frames = [frames[0] + flair, frames[1]]
        self.setText(hat + frames[self._frame % len(frames)])
```


**Implementation:** inside `cozy/cat_controller.py`, replace only `CatController._render`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.14. `cozy/neko.py`


#### 2.14.1 Existing method/function `NekoChaser.__init__`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 41–71:**


```python
    def __init__(self, window):
        super().__init__(window)
        self._window = window
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # never blocks clicks
        self.setFixedSize(DISPLAY_SIZE, DISPLAY_SIZE)
        self.setScaledContents(False)
        self.hide()

        self._target = None
        self._frame = 0

        # --- sprite sheets (v3): walk for the stroll, sleep on arrival -- #
        self._walk_sheet, self._walk_n = self._load_sheet("walk")
        self._sleep_sheet, self._sleep_n = self._load_sheet("sleep")

        # single-shot idle timer: armed by start(), re-armed on every
        # activity event, fires once when 30 s pass with nothing
        self._idle_timer = QTimer(self)
        self._idle_timer.setSingleShot(True)
        self._idle_timer.timeout.connect(self._wake)

        # walk clock: one 80 ms tick per STEP_PX toward the target
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._step)

        # nap clock: slow 400 ms cycle through the sleep sheet AFTER the
        # cat has arrived (breathing animation, not a sprint)
        self._nap_timer = QTimer(self)
        self._nap_timer.timeout.connect(self._nap_tick)

        self._filter_installed = False
```


**New version:**


```python
    def __init__(self, window):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__(window)
        self._window = window
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # never blocks clicks
        self.setFixedSize(DISPLAY_SIZE, DISPLAY_SIZE)
        self.setScaledContents(False)
        self.hide()

        self._target = None
        self._frame = 0

        # --- sprite sheets (v3): walk for the stroll, sleep on arrival -- #
        self._walk_sheet, self._walk_n = self._load_sheet("walk")
        self._sleep_sheet, self._sleep_n = self._load_sheet("sleep")

        # single-shot idle timer: armed by start(), re-armed on every
        # activity event, fires once when 30 s pass with nothing
        self._idle_timer = QTimer(self)
        self._idle_timer.setSingleShot(True)
        self._idle_timer.timeout.connect(self._wake)

        # walk clock: one 80 ms tick per STEP_PX toward the target
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._step)

        # nap clock: slow 400 ms cycle through the sleep sheet AFTER the
        # cat has arrived (breathing animation, not a sprint)
        self._nap_timer = QTimer(self)
        self._nap_timer.timeout.connect(self._nap_tick)

        self._filter_installed = False
```


**Implementation:** inside `cozy/neko.py`, replace only `NekoChaser.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.14.2 Existing method/function `NekoChaser._show_sheet_frame`

Play frame `index` of a strip: copy its rect, scale, show. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 93–97:**


```python
    def _show_sheet_frame(self, sheet, n, index):
        """Play frame `index` of a strip: copy its rect, scale, show."""
        cell = sheet.height()
        pix = sheet.copy((index % n) * cell, 0, cell, cell)
        self.setPixmap(pix.scaled(DISPLAY_SIZE, DISPLAY_SIZE, Qt.KeepAspectRatio, Qt.FastTransformation))
```


**New version:**


```python
    def _show_sheet_frame(self, sheet, n, index):
        """Play frame `index` of a strip: copy its rect, scale, show."""
        cell = sheet.height()
        pix = sheet.copy((index % n) * cell, 0, cell, cell)
        self.setPixmap(pix.scaled(DISPLAY_SIZE, DISPLAY_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
```


**Implementation:** inside `cozy/neko.py`, replace only `NekoChaser._show_sheet_frame`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.15. `cozy/overlays.py`


#### 2.15.1 Existing method/function `ScanlineOverlay.__init__`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 14–17:**


```python
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()
```


**New version:**


```python
    def __init__(self, parent):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()
```


**Implementation:** inside `cozy/overlays.py`, replace only `ScanlineOverlay.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.16. `cozy/power_mode.py`


#### 2.16.1 Existing method/function `Particle.__init__`

Initialize this component and its existing Qt widgets and signal connections. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 76–81:**


```python
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx = random.uniform(-2.2, 2.2)     # random sideways kick
        self.vy = random.uniform(-3.5, 0.5)     # mostly upward = spark
        self.life = random.randint(8, 18)    # tick @ 30ms = 240-540ms
        self.color = color
```


**New version:**


```python
    def __init__(self, x, y, color):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self.x, self.y = x, y
        self.vx = random.uniform(-2.2, 2.2)     # random sideways kick
        self.vy = random.uniform(-3.5, 0.5)     # mostly upward = spark
        self.life = random.randint(8, 18)    # tick @ 30ms = 240-540ms
        self.color = color
```


**Implementation:** inside `cozy/power_mode.py`, replace only `Particle.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.16.2 Existing method/function `ParticleOverlay.__init__`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 95–102:**


```python
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._particles = []
        self.sync_geometry()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)
        self._timer.start(30)                   # ~33 fps, plenty for confetti
```


**New version:**


```python
    def __init__(self, parent):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._particles = []
        self.sync_geometry()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)
        self._timer.start(30)                   # ~33 fps, plenty for confetti
```


**Implementation:** inside `cozy/power_mode.py`, replace only `ParticleOverlay.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.16.3 Existing method/function `ParticleOverlay.paintEvent`

Paint the current overlay effect using its existing drawing algorithm. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 133–142:**


```python
    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for p in self._particles:
            c = QColor(p.color)
            c.setAlpha(int(155 * p.life / 18))      # fade out as life runs down
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QPointF(p.x, p.y), 2.2, 2.2)
        painter.end()
```


**New version:**


```python
    def paintEvent(self, _):
        """Paint the current overlay effect using its existing drawing algorithm.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for p in self._particles:
            c = QColor(p.color)
            c.setAlpha(int(155 * p.life / 18))      # fade out as life runs down
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QPointF(p.x, p.y), 2.2, 2.2)
        painter.end()
```


**Implementation:** inside `cozy/power_mode.py`, replace only `ParticleOverlay.paintEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.16.4 Existing method/function `ScreenShake.__init__`

Initialize this component and its existing Qt widgets and signal connections. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 162–168:**


```python
    def __init__(self, widget, intensity=1):
        self._widget = widget
        self._intensity = intensity
        self._orig = widget.pos()
        self._ticks = 0
        self._timer = QTimer(widget)
        self._timer.timeout.connect(self._jolt)
```


**New version:**


```python
    def __init__(self, widget, intensity=1):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        self._widget = widget
        self._intensity = intensity
        self._orig = widget.pos()
        self._ticks = 0
        self._timer = QTimer(widget)
        self._timer.timeout.connect(self._jolt)
```


**Implementation:** inside `cozy/power_mode.py`, replace only `ScreenShake.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.16.5 Existing method/function `ComboTracker.__init__`

Initialize this component and its existing Qt widgets and signal connections. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 216–221:**


```python
    def __init__(self, parent=None):
        super().__init__(parent)
        self._count = 0
        self._idle = QTimer(self)
        self._idle.setSingleShot(True)
        self._idle.timeout.connect(self._reset)
```


**New version:**


```python
    def __init__(self, parent=None):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__(parent)
        self._count = 0
        self._idle = QTimer(self)
        self._idle.setSingleShot(True)
        self._idle.timeout.connect(self._reset)
```


**Implementation:** inside `cozy/power_mode.py`, replace only `ComboTracker.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.16.6 Existing method/function `ComboTracker.eventFilter`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 226–236:**


```python
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.text():
            # Only keys typed into a Scintilla editor count (duck-typed:
            # QLineEdit/QSpinBox & friends have no SendScintilla).
            if hasattr(obj, "SendScintilla"):
                self._count += 1
                self._idle.start(self.RESET_MS)
                self.keystroke.emit(obj)
                if self._count in (25, 50, 100):
                    self.combo_milestone.emit(self._count)
        return False
```


**New version:**


```python
    def eventFilter(self, obj, event):
        """Observe editor key events and count typing activity without consuming events.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if event.type() == QEvent.Type.KeyPress and event.text():
            # Only keys typed into a Scintilla editor count (duck-typed:
            # QLineEdit/QSpinBox & friends have no SendScintilla).
            if hasattr(obj, "SendScintilla"):
                self._count += 1
                self._idle.start(self.RESET_MS)
                self.keystroke.emit(obj)
                if self._count in (25, 50, 100):
                    self.combo_milestone.emit(self._count)
        return False
```


**Implementation:** inside `cozy/power_mode.py`, replace only `ComboTracker.eventFilter`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.16.7 Existing method/function `ComboGlow.__init__`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 247–254:**


```python
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._alpha = 0.0
        self.sync_geometry()

        self._anim = QVariantAnimation(self)
        self._anim.valueChanged.connect(self._set_alpha)
```


**New version:**


```python
    def __init__(self, parent):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._alpha = 0.0
        self.sync_geometry()

        self._anim = QVariantAnimation(self)
        self._anim.valueChanged.connect(self._set_alpha)
```


**Implementation:** inside `cozy/power_mode.py`, replace only `ComboGlow.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.16.8 Existing method/function `ComboGlow.paintEvent`

Paint the current overlay effect using its existing drawing algorithm. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 275–285:**


```python
    def paintEvent(self, _):
        if self._alpha <= 0.01:
            return                       # skip painting entirely when idle
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor("#FF5700")
        color.setAlphaF(self._alpha)
        painter.setPen(QPen(color, 6))
        painter.drawRoundedRect(
            QRectF(self.rect()).adjusted(3, 3, -3, -3), 8, 8)
        painter.end()
```


**New version:**


```python
    def paintEvent(self, _):
        """Paint the current overlay effect using its existing drawing algorithm.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        if self._alpha <= 0.01:
            return                       # skip painting entirely when idle
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor("#FF5700")
        color.setAlphaF(self._alpha)
        painter.setPen(QPen(color, 6))
        painter.drawRoundedRect(
            QRectF(self.rect()).adjusted(3, 3, -3, -3), 8, 8)
        painter.end()
```


**Implementation:** inside `cozy/power_mode.py`, replace only `ComboGlow.paintEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.16.9 Existing method/function `PowerModeController.eventFilter`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 347–352:**


```python
    def eventFilter(self, obj, event):
        """Window Resize -> keep overlays glued to the window edges."""
        if obj is self._window and event.type() == QEvent.Resize:
            self.particles.sync_geometry()
            self.glow.sync_geometry()
        return False
```


**New version:**


```python
    def eventFilter(self, obj, event):
        """Window Resize -> keep overlays glued to the window edges."""
        if obj is self._window and event.type() == QEvent.Type.Resize:
            self.particles.sync_geometry()
            self.glow.sync_geometry()
        return False
```


**Implementation:** inside `cozy/power_mode.py`, replace only `PowerModeController.eventFilter`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.17. `git_ui/commit_graph.py`


#### Imports and declarations outside methods


**Declaration change 1, original line 25. Old:**


```python
ROW_ROLE = Qt.UserRole + 1
REF_ROLE = Qt.UserRole + 2
```


**New:**


```python
from code_inteligence.qt_helpers import require_qt

ROW_ROLE = Qt.ItemDataRole.UserRole + 1
REF_ROLE = Qt.ItemDataRole.UserRole + 2
```


**Implementation:** replace exactly this declaration/block; keep surrounding code.


#### 2.17.1 Existing method/function `HistoryDelegate.paint`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 44–60:**


```python
    def paint(self, painter, option, index):
        """Draw standard selection first, then graph or reference content."""
        if index.column() not in (0, 2):
            return super().paint(painter, option, index)
        styled = QStyleOptionViewItem(option)
        self.initStyleOption(styled, index)
        styled.text = ""
        self.panel.style().drawControl(QStyle.CE_ItemViewItem, styled, painter, self.panel)
        painter.save()
        painter.setClipRect(option.rect)
        if index.column() == 0:
            row = index.data(ROW_ROLE)
            if row is not None:
                self._paint_graph(painter, option.rect, row)
        else:
            self._paint_refs(painter, option, index)
        painter.restore()
```


**New version:**


```python
    def paint(self, painter, option, index):
        """Draw standard selection first, then graph or reference content."""
        if index.column() not in (0, 2):
            return super().paint(painter, option, index)
        styled = QStyleOptionViewItem(option)
        self.initStyleOption(styled, index)
        styled.text = ""
        require_qt(self.panel.style()).drawControl(QStyle.ControlElement.CE_ItemViewItem, styled, painter, self.panel)
        painter.save()
        painter.setClipRect(option.rect)
        if index.column() == 0:
            row = index.data(ROW_ROLE)
            if row is not None:
                self._paint_graph(painter, option.rect, row)
        else:
            self._paint_refs(painter, option, index)
        painter.restore()
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `HistoryDelegate.paint`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.17.2 Existing method/function `HistoryDelegate._paint_graph`

Connect row boundaries using model-supplied parent edges. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 62–85:**


```python
    def _paint_graph(self, painter, rect, row):
        """Connect row boundaries using model-supplied parent edges."""
        painter.setRenderHint(QPainter.Antialiasing)
        middle = rect.top() + rect.height() / 2
        left = rect.left() + 16
        for lane, color in row.incoming:
            painter.setPen(QPen(self.panel.lane_color(color), 2))
            x = left + lane * LANE_WIDTH
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, middle))
        for start, end, color in row.outgoing:
            painter.setPen(QPen(self.panel.lane_color(color), 2))
            x1, x2 = left + start * LANE_WIDTH, left + end * LANE_WIDTH
            path = QPainterPath(QPointF(x1, middle))
            bottom = rect.top() + rect.height()
            path.cubicTo(x1, bottom - 4, x2, middle + 4, x2, bottom)
            painter.drawPath(path)
        center = QPointF(left + row.lane * LANE_WIDTH, middle)
        painter.setBrush(self.panel.lane_color(row.color_index))
        painter.setPen(QPen(QColor(self.panel.background), 2))
        painter.drawEllipse(center, 5, 5)
        if "HEAD" in row.commit.decorations:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(self.panel.lane_color(row.color_index), 1))
            painter.drawEllipse(center, 8, 8)
```


**New version:**


```python
    def _paint_graph(self, painter, rect, row):
        """Connect row boundaries using model-supplied parent edges."""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        middle = rect.top() + rect.height() / 2
        left = rect.left() + 16
        for lane, color in row.incoming:
            painter.setPen(QPen(self.panel.lane_color(color), 2))
            x = left + lane * LANE_WIDTH
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, middle))
        for start, end, color in row.outgoing:
            painter.setPen(QPen(self.panel.lane_color(color), 2))
            x1, x2 = left + start * LANE_WIDTH, left + end * LANE_WIDTH
            path = QPainterPath(QPointF(x1, middle))
            bottom = rect.top() + rect.height()
            path.cubicTo(x1, bottom - 4, x2, middle + 4, x2, bottom)
            painter.drawPath(path)
        center = QPointF(left + row.lane * LANE_WIDTH, middle)
        painter.setBrush(self.panel.lane_color(row.color_index))
        painter.setPen(QPen(QColor(self.panel.background), 2))
        painter.drawEllipse(center, 5, 5)
        if "HEAD" in row.commit.decorations:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(self.panel.lane_color(row.color_index), 1))
            painter.drawEllipse(center, 8, 8)
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `HistoryDelegate._paint_graph`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.17.3 Existing method/function `CommitGraphPanel.__init__`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 112–138:**


```python
    def __init__(self, parent=None):
        """Configure columns, selection, delegates, and read-only actions."""
        super().__init__(parent)
        self.setObjectName("GitHistoryTree")
        self._snapshot = None
        self._rows = {}
        self.setColumnCount(6)
        self.setHeaderLabels(
            ("Graph", "Commit message", "Branches / tags", "Commit", "Author", "Date")
        )
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setSortingEnabled(False)  # Sorting would falsify ancestry.
        self.setHorizontalScrollMode(QTreeWidget.ScrollPerPixel)
        self.setItemDelegate(HistoryDelegate(self))
        self.header().setStretchLastSection(False)
        self.header().setMinimumSectionSize(60)
        for column, width in enumerate((90, 330, 240, 100, 155, 155)):
            self.header().setSectionResizeMode(column, QHeaderView.Interactive)
            self.setColumnWidth(column, width)
        self.itemActivated.connect(self._activate)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)
        self.apply_theme()
```


**New version:**


```python
    def __init__(self, parent=None):
        """Configure columns, selection, delegates, and read-only actions."""
        super().__init__(parent)
        self.setObjectName("GitHistoryTree")
        self._snapshot = None
        self._rows = {}
        self.setColumnCount(6)
        self.setHeaderLabels(
            ("Graph", "Commit message", "Branches / tags", "Commit", "Author", "Date")
        )
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setSortingEnabled(False)  # Sorting would falsify ancestry.
        self.setHorizontalScrollMode(QTreeWidget.ScrollPerPixel)
        self.setItemDelegate(HistoryDelegate(self))
        require_qt(self.header()).setStretchLastSection(False)
        require_qt(self.header()).setMinimumSectionSize(60)
        for column, width in enumerate((90, 330, 240, 100, 155, 155)):
            require_qt(self.header()).setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)
            self.setColumnWidth(column, width)
        self.itemActivated.connect(self._activate)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)
        self.apply_theme()
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `CommitGraphPanel.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.17.4 Existing method/function `CommitGraphPanel.resizeEvent`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 144–148:**


```python
    def resizeEvent(self, event):
        """Keep summaries readable in narrow docks; scroll other columns."""
        super().resizeEvent(event)
        occupied = sum(self.columnWidth(i) for i in (0, 2, 3, 4, 5))
        self.setColumnWidth(1, max(330, self.viewport().width() - occupied))
```


**New version:**


```python
    def resizeEvent(self, event):
        """Keep summaries readable in narrow docks; scroll other columns."""
        super().resizeEvent(event)
        occupied = sum(self.columnWidth(i) for i in (0, 2, 3, 4, 5))
        self.setColumnWidth(1, max(330, require_qt(self.viewport()).width() - occupied))
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `CommitGraphPanel.resizeEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.17.5 Existing method/function `CommitGraphPanel.apply_theme`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 154–211:**


```python
    def apply_theme(self, theme_path=None):
        """Read the editor's theme file with safe dark-theme fallbacks."""
        theme = {}
        if theme_path:
            try:
                with open(theme_path, encoding="utf-8") as stream:
                    theme = json.load(stream).get("theme", {})
            except (OSError, ValueError, AttributeError):
                theme = {}
        if not isinstance(theme, dict):
            theme = {}
        editor = theme.get("editor", {})
        editor = editor if isinstance(editor, dict) else {}
        paper = editor.get("paper-color", "#1e1f22")
        background = QColor(paper if isinstance(paper, str) else "#1e1f22")
        if not background.isValid():
            background = QColor("#1e1f22")
        dark = background.lightness() < 128
        self.background = background.name()
        foreground = "#bcbec4" if dark else "#24292f"
        surface = background.lighter(125).name() if dark else background.darker(105).name()
        selection = "#35465d" if dark else "#d6e8ff"
        border = "#393b40" if dark else "#c8cdd3"
        self._lane_colors = (
            ("#82aaff", "#c792ea", "#66d9a8", "#ecc48d", "#f78c9c", "#89ddff")
            if dark
            else ("#185abc", "#753ab7", "#197347", "#8c5900", "#b32243", "#006a80")
        )
        font_settings = editor.get("font", {})
        font_settings = font_settings if isinstance(font_settings, dict) else {}
        try:
            size = max(9, min(20, int(font_settings.get("font-size", 11))))
        except (ValueError, TypeError):
            size = 11
        self.setFont(QFont(str(font_settings.get("family", "monospace")), size))
        # Measure fixed metadata columns at the selected font size, not at the
        # system default. Otherwise even an eight-character SHA gets ellipsized.
        metrics = self.fontMetrics()
        self.setColumnWidth(2, max(280, metrics.horizontalAdvance("feature/git-history") + 40))
        self.setColumnWidth(3, metrics.horizontalAdvance("01234567") + 30)
        self.setColumnWidth(4, metrics.horizontalAdvance("David Schubba") + 30)
        self.setColumnWidth(5, metrics.horizontalAdvance("2026-09-16 12:48") + 30)
        palette = self.palette()
        palette.setColor(QPalette.Base, background)
        palette.setColor(QPalette.Text, QColor(foreground))
        self.setPalette(palette)
        self.setStyleSheet(f"""
            QTreeWidget#GitHistoryTree {{ background:{self.background}; color:{foreground};
                alternate-background-color:{surface}; border:0; outline:0; }}
            QTreeWidget#GitHistoryTree::item {{ padding:0 7px; border:0; }}
            QTreeWidget#GitHistoryTree::item:selected {{ background:{selection}; color:{foreground}; }}
            QHeaderView::section {{ background:{surface}; color:{foreground};
                padding:9px 8px; border:0; border-bottom:1px solid {border}; }}
            QScrollBar {{ background:{self.background}; width:12px; height:12px; }}
            QScrollBar::handle {{ background:{border}; border-radius:4px; min-height:24px; min-width:24px; }}
            QMenu {{ background:{surface}; color:{foreground}; }}
        """)
        self.viewport().update()
```


**New version:**


```python
    def apply_theme(self, theme_path=None):
        """Read the editor's theme file with safe dark-theme fallbacks."""
        theme = {}
        if theme_path:
            try:
                with open(theme_path, encoding="utf-8") as stream:
                    theme = json.load(stream).get("theme", {})
            except (OSError, ValueError, AttributeError):
                theme = {}
        if not isinstance(theme, dict):
            theme = {}
        editor = theme.get("editor", {})
        editor = editor if isinstance(editor, dict) else {}
        paper = editor.get("paper-color", "#1e1f22")
        background = QColor(paper if isinstance(paper, str) else "#1e1f22")
        if not background.isValid():
            background = QColor("#1e1f22")
        dark = background.lightness() < 128
        self.background = background.name()
        foreground = "#bcbec4" if dark else "#24292f"
        surface = background.lighter(125).name() if dark else background.darker(105).name()
        selection = "#35465d" if dark else "#d6e8ff"
        border = "#393b40" if dark else "#c8cdd3"
        self._lane_colors = (
            ("#82aaff", "#c792ea", "#66d9a8", "#ecc48d", "#f78c9c", "#89ddff")
            if dark
            else ("#185abc", "#753ab7", "#197347", "#8c5900", "#b32243", "#006a80")
        )
        font_settings = editor.get("font", {})
        font_settings = font_settings if isinstance(font_settings, dict) else {}
        try:
            size = max(9, min(20, int(font_settings.get("font-size", 11))))
        except (ValueError, TypeError):
            size = 11
        self.setFont(QFont(str(font_settings.get("family", "monospace")), size))
        # Measure fixed metadata columns at the selected font size, not at the
        # system default. Otherwise even an eight-character SHA gets ellipsized.
        metrics = self.fontMetrics()
        self.setColumnWidth(2, max(280, metrics.horizontalAdvance("feature/git-history") + 40))
        self.setColumnWidth(3, metrics.horizontalAdvance("01234567") + 30)
        self.setColumnWidth(4, metrics.horizontalAdvance("David Schubba") + 30)
        self.setColumnWidth(5, metrics.horizontalAdvance("2026-09-16 12:48") + 30)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, background)
        palette.setColor(QPalette.ColorRole.Text, QColor(foreground))
        self.setPalette(palette)
        self.setStyleSheet(f"""
            QTreeWidget#GitHistoryTree {{ background:{self.background}; color:{foreground};
                alternate-background-color:{surface}; border:0; outline:0; }}
            QTreeWidget#GitHistoryTree::item {{ padding:0 7px; border:0; }}
            QTreeWidget#GitHistoryTree::item:selected {{ background:{selection}; color:{foreground}; }}
            QHeaderView::section {{ background:{surface}; color:{foreground};
                padding:9px 8px; border:0; border-bottom:1px solid {border}; }}
            QScrollBar {{ background:{self.background}; width:12px; height:12px; }}
            QScrollBar::handle {{ background:{border}; border-radius:4px; min-height:24px; min-width:24px; }}
            QMenu {{ background:{surface}; color:{foreground}; }}
        """)
        require_qt(self.viewport()).update()
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `CommitGraphPanel.apply_theme`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.17.6 Existing method/function `CommitGraphPanel.set_snapshot`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 213–260:**


```python
    def set_snapshot(self, snapshot: GitSnapshot):
        """Replace history atomically and retain selection during refreshes."""
        if snapshot == self._snapshot:
            return
        rows = layout_graph(snapshot.commits)  # Validate before clearing old data.
        current = self.currentItem()
        same_root = self._snapshot is not None and self._snapshot.root == snapshot.root
        selected = current.data(0, Qt.UserRole) if current and same_root else None
        scroll = self.verticalScrollBar().value() if same_root else 0
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            self._snapshot = snapshot
            self._rows = {row.commit.sha: row for row in rows}
            for row in rows:
                commit = row.commit
                try:
                    date = datetime.fromisoformat(commit.authored_at).strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    date = commit.authored_at
                refs = tuple(filter(None, commit.decorations.split(", ")))
                item = QTreeWidgetItem(
                    ("", commit.subject, "  ".join(refs), commit.sha[:8], commit.author, date)
                )
                item.setData(0, Qt.UserRole, commit.sha)
                item.setData(0, ROW_ROLE, row)
                item.setData(2, REF_ROLE, refs)
                for column, value in enumerate(
                    (
                        commit.sha,
                        commit.subject,
                        commit.decorations,
                        commit.sha,
                        commit.author,
                        commit.authored_at,
                    )
                ):
                    item.setToolTip(column, "<qt>" + escape(value) + "</qt>")
                self.addTopLevelItem(item)
                if commit.sha == selected:
                    self.setCurrentItem(item)
            lanes = max((row.lane_count for row in rows), default=1)
            self.setColumnWidth(0, max(75, 32 + lanes * LANE_WIDTH))
            # Recompute scrollbar limits before restoring the previous position.
            self.doItemsLayout()
            self.verticalScrollBar().setValue(scroll)
        finally:
            self.setUpdatesEnabled(True)
```


**New version:**


```python
    def set_snapshot(self, snapshot: GitSnapshot):
        """Replace history atomically and retain selection during refreshes."""
        if snapshot == self._snapshot:
            return
        rows = layout_graph(snapshot.commits)  # Validate before clearing old data.
        current = self.currentItem()
        same_root = self._snapshot is not None and self._snapshot.root == snapshot.root
        selected = current.data(0, Qt.ItemDataRole.UserRole) if current and same_root else None
        scroll = require_qt(self.verticalScrollBar()).value() if same_root else 0
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            self._snapshot = snapshot
            self._rows = {row.commit.sha: row for row in rows}
            for row in rows:
                commit = row.commit
                try:
                    date = datetime.fromisoformat(commit.authored_at).strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    date = commit.authored_at
                refs = tuple(filter(None, commit.decorations.split(", ")))
                item = QTreeWidgetItem(
                    ("", commit.subject, "  ".join(refs), commit.sha[:8], commit.author, date)
                )
                item.setData(0, Qt.ItemDataRole.UserRole, commit.sha)
                item.setData(0, ROW_ROLE, row)
                item.setData(2, REF_ROLE, refs)
                for column, value in enumerate(
                    (
                        commit.sha,
                        commit.subject,
                        commit.decorations,
                        commit.sha,
                        commit.author,
                        commit.authored_at,
                    )
                ):
                    item.setToolTip(column, "<qt>" + escape(value) + "</qt>")
                self.addTopLevelItem(item)
                if commit.sha == selected:
                    self.setCurrentItem(item)
            lanes = max((row.lane_count for row in rows), default=1)
            self.setColumnWidth(0, max(75, 32 + lanes * LANE_WIDTH))
            # Recompute scrollbar limits before restoring the previous position.
            self.doItemsLayout()
            require_qt(self.verticalScrollBar()).setValue(scroll)
        finally:
            self.setUpdatesEnabled(True)
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `CommitGraphPanel.set_snapshot`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.17.7 Existing method/function `CommitGraphPanel._activate`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 268–273:**


```python
    def _activate(self, item, _column):
        """Emit the SHA and display non-mutating details on activation."""
        sha = item.data(0, Qt.UserRole)
        if sha:
            self.commitActivated.emit(str(sha))
            self._show_details(str(sha))
```


**New version:**


```python
    def _activate(self, item, _column):
        """Emit the SHA and display non-mutating details on activation."""
        sha = item.data(0, Qt.ItemDataRole.UserRole)
        if sha:
            self.commitActivated.emit(str(sha))
            self._show_details(str(sha))
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `CommitGraphPanel._activate`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.17.8 Existing method/function `CommitGraphPanel._show_details`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 275–298:**


```python
    def _show_details(self, sha):
        """Show snapshot metadata without executing repository commands."""
        row = self._rows.get(sha)
        if row is None:
            return
        commit = row.commit
        dialog = QDialog(self)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.setWindowTitle("Commit details")
        dialog.resize(720, 330)
        layout = QVBoxLayout(dialog)
        text = QPlainTextEdit(dialog)
        text.setReadOnly(True)
        text.setFont(self.font())
        text.setStyleSheet(
            f"background:{self.background};color:{self.palette().color(QPalette.Text).name()};"
        )
        text.setPlainText(
            f"Commit: {sha}\nAuthor: {commit.author}\nDate: {commit.authored_at}\n"
            f"Refs: {commit.decorations or '(none)'}\n"
            f"Parents: {', '.join(commit.parents) or '(root commit)'}\n\n{commit.subject}"
        )
        layout.addWidget(text)
        dialog.show()
```


**New version:**


```python
    def _show_details(self, sha):
        """Show snapshot metadata without executing repository commands."""
        row = self._rows.get(sha)
        if row is None:
            return
        commit = row.commit
        dialog = QDialog(self)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.setWindowTitle("Commit details")
        dialog.resize(720, 330)
        layout = QVBoxLayout(dialog)
        text = QPlainTextEdit(dialog)
        text.setReadOnly(True)
        text.setFont(self.font())
        text.setStyleSheet(
            f"background:{self.background};color:{self.palette().color(QPalette.ColorRole.Text).name()};"
        )
        text.setPlainText(
            f"Commit: {sha}\nAuthor: {commit.author}\nDate: {commit.authored_at}\n"
            f"Refs: {commit.decorations or '(none)'}\n"
            f"Parents: {', '.join(commit.parents) or '(root commit)'}\n\n{commit.subject}"
        )
        layout.addWidget(text)
        dialog.show()
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `CommitGraphPanel._show_details`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.17.9 Existing method/function `CommitGraphPanel._context_menu`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 300–312:**


```python
    def _context_menu(self, position):
        """Offer copy and inspect actions, never checkout or discard."""
        item = self.itemAt(position)
        if item is None:
            return
        sha = item.data(0, Qt.UserRole)
        menu = QMenu(self)
        menu.addAction("Copy commit SHA", lambda: QApplication.clipboard().setText(sha))
        menu.addAction(
            "Copy commit message", lambda: QApplication.clipboard().setText(item.text(1))
        )
        menu.addAction("Commit details", lambda: self._show_details(sha))
        menu.exec_(self.viewport().mapToGlobal(position))
```


**New version:**


```python
    def _context_menu(self, position):
        """Offer copy and inspect actions, never checkout or discard."""
        item = self.itemAt(position)
        if item is None:
            return
        sha = item.data(0, Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        menu.addAction("Copy commit SHA", lambda: QApplication.clipboard().setText(sha))
        menu.addAction(
            "Copy commit message", lambda: QApplication.clipboard().setText(item.text(1))
        )
        menu.addAction("Commit details", lambda: self._show_details(sha))
        menu.exec_(require_qt(self.viewport()).mapToGlobal(position))
```


**Implementation:** inside `git_ui/commit_graph.py`, replace only `CommitGraphPanel._context_menu`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.18. `markdown_editor/markdowneditor.py`


#### 2.18.1 Existing method/function `MarkdownEditor.__init__`

Initialize this component and its existing Qt widgets and signal connections. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 13–61:**


```python
    def __init__(self, parent=None, path: Path | None=None, is_python_file: bool=False):
        super(MarkdownEditor, self).__init__(parent)
        self.path = path
        self._loading_text = False
        self._shutting_down = False
        self.full_path = self.path.absolute() if self.path else None
        self.is_python_file = is_python_file
        # encoding
        self.setUtf8(True)
        # NOTE: no editor-level font anymore — the theme (via the lexer)
        # owns family, size, colors and paper. _apply_theme_editor_style()
        # below pulls the editor-wide look from the lexer after it loads
        # the theme. JetBrains Mono 13 is only the pre-lexer fallback.

        # brace matching
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # indentation
        self.setIndentationGuides(True)
        self.setTabWidth(2)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)

        self.setEolMode(QsciScintilla.EolUnix if sys.platform != "win32" else QsciScintilla.EolWindows)
        self.setEolVisibility(False)

        # autocomplete
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # caret (fallbacks; the theme's editor section replaces them via
        # _apply_theme_editor_style once the lexer is attached)
        self.setCaretForegroundColor(QColor('#f31122'))  # sets text caret color
        self.setCaretLineVisible(True)  # enables the background color of the caret line
        self.setCaretWidth(2)  # sets the caret with
        self.setCaretLineBackgroundColor(QColor('#3d424d')) # changes the background color of the caret line

        # set lexer — it loads themes/theme.json itself and derives every
        # font/color/paper from it (single source of truth)
        self.md_lexer = MarkdownCustomLexer(self)
        self.setLexer(self.md_lexer)
        self._apply_theme_editor_style()

        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)
```


**New version:**


```python
    def __init__(self, parent=None, path: Path | None=None, is_python_file: bool=False):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super(MarkdownEditor, self).__init__(parent)
        self.path = path
        self._loading_text = False
        self._shutting_down = False
        self.full_path = self.path.absolute() if self.path else None
        self.is_python_file = is_python_file
        # encoding
        self.setUtf8(True)
        # NOTE: no editor-level font anymore — the theme (via the lexer)
        # owns family, size, colors and paper. _apply_theme_editor_style()
        # below pulls the editor-wide look from the lexer after it loads
        # the theme. JetBrains Mono 13 is only the pre-lexer fallback.

        # brace matching
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # indentation
        self.setIndentationGuides(True)
        self.setTabWidth(2)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)

        self.setEolMode(QsciScintilla.EolUnix if sys.platform != "win32" else QsciScintilla.EolWindows)
        self.setEolVisibility(False)

        # autocomplete
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # caret (fallbacks; the theme's editor section replaces them via
        # _apply_theme_editor_style once the lexer is attached)
        self.setCaretForegroundColor(QColor('#f31122'))  # sets text caret color
        self.setCaretLineVisible(True)  # enables the background color of the caret line
        self.setCaretWidth(2)  # sets the caret with
        self.setCaretLineBackgroundColor(QColor('#3d424d')) # changes the background color of the caret line

        # set lexer — it loads themes/theme.json itself and derives every
        # font/color/paper from it (single source of truth)
        self.md_lexer = MarkdownCustomLexer(self)
        self.setLexer(self.md_lexer)
        self._apply_theme_editor_style()

        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "000")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)
```


**Implementation:** inside `markdown_editor/markdowneditor.py`, replace only `MarkdownEditor.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.19. `markdowneditor_assets/icon_provider.py`


#### 2.19.1 Existing method/function `themed_icon`

Correct `QIcon.on` to the actual `QIcon.State.On` member. This is a case-sensitive API correction.


**Old version — original lines 7–19:**


```python
def themed_icon(name: str) -> QIcon:
    """Load existing 24px SVG icons with actual disabled/selected Qt states."""
    # Do not turn abitrary text in asset path; the sidebar has six
    # supported actions and an explitcit allowlist is easier to review.
    if name not in {"folder", "search", "outline", "terminal", "console", "settings"}:
        raise ValueError("unsupported icon")
    path = Path(asset_path(f"icons/{name}.svg"))
    icon = QIcon(str(path))
    # Qt generates a disabled palette variant when no explicit asset is added.
    active = Path(asset_path(f"icons/{name}-active.svg"))
    if active.is_file():
        icon.addFile(str(active), mode=QIcon.Normal, state=QIcon.on)
    return icon
```


**New version:**


```python
def themed_icon(name: str) -> QIcon:
    """Load existing 24px SVG icons with actual disabled/selected Qt states."""
    # Do not turn abitrary text in asset path; the sidebar has six
    # supported actions and an explitcit allowlist is easier to review.
    if name not in {"folder", "search", "outline", "terminal", "console", "settings"}:
        raise ValueError("unsupported icon")
    path = Path(asset_path(f"icons/{name}.svg"))
    icon = QIcon(str(path))
    # Qt generates a disabled palette variant when no explicit asset is added.
    active = Path(asset_path(f"icons/{name}-active.svg"))
    if active.is_file():
        icon.addFile(str(active), mode=QIcon.Mode.Normal, state=QIcon.State.On)
    return icon
```


**Implementation:** inside `markdowneditor_assets/icon_provider.py`, replace only `themed_icon`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.20. `python_editor/python_runner.py`


#### 2.20.1 Existing method/function `PythonRunner.send_input`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 122–125:**


```python
    def send_input(self, text: str):
        """Send one UTF-8 input line only while the child is running."""
        if self.process.state() == QProcess.Running:
            self.process.write((text + "\n").encode("utf-8"))
```


**New version:**


```python
    def send_input(self, text: str):
        """Send one UTF-8 input line only while the child is running."""
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.write((text + "\n").encode("utf-8"))
```


**Implementation:** inside `python_editor/python_runner.py`, replace only `PythonRunner.send_input`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.20.2 Existing method/function `PythonRunner._stop_process`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 131–142:**


```python
    def _stop_process(self, *, clear_pending: bool):
        """Request graceful termination and arm a generation-bound kill."""
        if clear_pending:
            self._pending_start = None
        if self.process.state() == QProcess.NotRunning:
            self._kill_timer.stop()
            self._terminating_generation = None
            return

        self._terminating_generation = self._process_generation
        self.process.terminate()
        self._kill_timer.start()
```


**New version:**


```python
    def _stop_process(self, *, clear_pending: bool):
        """Request graceful termination and arm a generation-bound kill."""
        if clear_pending:
            self._pending_start = None
        if self.process.state() == QProcess.ProcessState.NotRunning:
            self._kill_timer.stop()
            self._terminating_generation = None
            return

        self._terminating_generation = self._process_generation
        self.process.terminate()
        self._kill_timer.start()
```


**Implementation:** inside `python_editor/python_runner.py`, replace only `PythonRunner._stop_process`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.20.3 Existing method/function `PythonRunner._kill_if_still_stopping`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 144–148:**


```python
    def _kill_if_still_stopping(self):
        """Force-kill only the exact generation that was asked to stop."""
        same_generation = self._terminating_generation == self._process_generation
        if same_generation and self.process.state() != QProcess.NotRunning:
            self.process.kill()
```


**New version:**


```python
    def _kill_if_still_stopping(self):
        """Force-kill only the exact generation that was asked to stop."""
        same_generation = self._terminating_generation == self._process_generation
        if same_generation and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
```


**Implementation:** inside `python_editor/python_runner.py`, replace only `PythonRunner._kill_if_still_stopping`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.20.4 Existing method/function `PythonRunner._on_state_changed`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 173–174:**


```python
    def _on_state_changed(self, state):
        self.state_changed.emit("stopped" if state == QProcess.NotRunning else "running")
```


**New version:**


```python
    def _on_state_changed(self, state):
        """Forward the Python process state through the runner state-change signal.

        Compare the actual QProcess state/error enum. This preserves the
        existing lifecycle behavior and avoids unrecognized alias attributes.
        """
        self.state_changed.emit("stopped" if state == QProcess.ProcessState.NotRunning else "running")
```


**Implementation:** inside `python_editor/python_runner.py`, replace only `PythonRunner._on_state_changed`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.20.5 Existing method/function `PythonRunner.is_running`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 184–186:**


```python
    def is_running(self) -> bool:
        """Return true for both starting and running process states."""
        return self.process.state() != QProcess.NotRunning
```


**New version:**


```python
    def is_running(self) -> bool:
        """Return true for both starting and running process states."""
        return self.process.state() != QProcess.ProcessState.NotRunning
```


**Implementation:** inside `python_editor/python_runner.py`, replace only `PythonRunner.is_running`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.21. `python_editor/pythoneditor.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `from ruff_implementation.ruff_lsp_controller import RuffLspController` (original line 21).


```python
from code_inteligence.qt_helpers import require_qt
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 2.21.1 Existing method/function `PythonEditor.__init__`

The annotation now includes `None`, which the existing default and unsaved-document branch already accept. This makes the contract match the existing behavior.


**Old version — original lines 37–179:**


```python
    def __init__(self, parent=None, path: Path = None, is_python_file: bool = True, ruff_lsp_client = None):
        super().__init__(parent)
        
        # Store the absolute logical file path. Ruff LSP uses it to form the stable
        # document UEI sent in didOpen/didChanged notifications.
        
        self.path = path
        self.full_path = self.path.absolute() if self.path else None
        self.is_python_file = is_python_file
        self.ruff_lsp = None
        self._manual_completion_generation = None

        self._ruff_hover_active = False
        self._loading_text = False
        self._shutting_down = False
        self._autocomplete_timer = QTimer(self)
        self._autocomplete_timer.setSingleShot(True)
        self._autocomplete_timer.setInterval(300)
        self._autocomplete_timer.timeout.connect(self._trigger_autocomplete)

        self._pending_line = 0
        self._pending_index = 0
        self.cursorPositionChanged.connect(self._cursorPositionChanged)

        self.setUtf8(True)

        # NOTE: no editor-level font anymore. The theme (via the lexer)
        # owns family, size, colors and paper — one source of truth.
        # The lexer is created below; helpers on it (editor_font(),
        # editor_color()) supply the margins/popup/caret values.

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setIndentationGuides(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)
        self.setEolMode(
            QsciScintilla.EolUnix if sys.platform != "win32" else QsciScintilla.EolWindows
        )
        self.setEolVisibility(False)

        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # Caret styling defaults; replaced by theme values once the lexer
        # exists (see _apply_theme_editor_style below + _apply_editor_settings
        # in main.py after a lexer swap). Kept as safe fallbacks so the
        # widget is never unstyled before a theme loads.
        self.setCaretForegroundColor(QColor("#f31122"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#3d424d"))
        self.setCaretWidth(2)

        if self.is_python_file:
            if ruff_lsp_client is not None:
                self.ruff_lsp = RuffLspController(editor=self, client=ruff_lsp_client, parent=self)


            self._ruff_hover_timer = QTimer(self)
            self._ruff_hover_timer.setSingleShot(True)
            self._ruff_hover_timer.setInterval(150)
            self._ruff_hover_timer.timeout.connect(self._trigger_ruff_hover)
            
            # An owned timer can be stopped when Space/Enter dismisses help.
            self._signature_timer = QTimer(self)
            self._signature_timer.setSingleShot(True)
            self._signature_timer.setInterval(50)
            self._signature_timer.timeout.connect(self._trigger_signature_help)
            self.signature_helper = SignatureHelper()
            self.signature_helper.signature_ready.connect(self._on_signature_ready)
            self.signature_helper.signature_empty.connect(self._on_signature_empty)

            self.hover_helper = HoverHelper()
            self.hover_helper.hover_info_ready.connect(self._on_hover_ready)
            self.hover_helper.hover_info_empty.connect(self._on_hover_empty)

            # DocumentationPopup ows only the UI. HoverHelper still performs
            # Jedi analysis is its worker thread and emits plain text results.
            # Create one popup for this editor tab. Passing self as parent means
            # Qt cleans it up automatically when this PythonEditor is destroyed.
            # The lexer loads the theme itself — font, colors and paper all
            # come from themes/theme.json (or the theme chosen in Settings).
            # Created FIRST so everything below can read its theme helpers.
            self.py_lexer = PyCustomLexer(self)

            self.documentation_popup = DocumentationPopup(self)
            self.documentation_popup.dismissed.connect(self._cancel_documentation)
            self._documentation_global_pos = None
            # Popup font follows the theme's global editor font (the old
            # self.window_font is gone — the lexer owns fonts now).
            self.documentation_popup.set_documentation_font(
                self.py_lexer.editor_font())

            self.setMouseTracking(True)

            self._apply_theme_editor_style()

            self._api = QsciAPIs(self.py_lexer)
            self.auto_completer = AutoCompleter(
                str(self.full_path) if self.full_path else None, self._api
            )
            self.auto_completer.completions_ready.connect(self._apply_completions)
            self.auto_completer.error.connect(self._handle_completion_error)

            self.setLexer(self.py_lexer)
        else:
            # No lexer in this mode yet (tab not converted): neutral defaults.
            # Once a lexer attaches, _apply_theme_editor_style takes over.
            self.setPaper(QColor("#1e1f22"))
            self.setColor(QColor("#abb2bf"))

        self.definition_finder = DefinitionFinder()
        self.definition_finder.definition_found.connect(self._on_definition_found)
        self.definition_finder.definition_not_found.connect(self._on_definition_not_found)
        self.definition_finder.error.connect(self._on_definition_error)

        # Margin 0: source-code line numbers.
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")

        # Margin 1: Ruff error, warning, information and quick-fix symbols.
        self.setMarginType(1, QsciScintilla.SymbolMargin)
        self.setMarginWidth(1, "000")

        ruff_marker_mask = (
            (1 << RuffDiagnosticView.ERROR_MARKER)
            | (1 << RuffDiagnosticView.WARNING_MARKER)
            | (1 << RuffDiagnosticView.INFO_MARKER)
            | (1 << RuffDiagnosticView.FIX_MARKER)
        )
        self.setMarginMarkerMask(1, ruff_marker_mask)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)

        # Final theme application (font, margins, caret, paper) — AFTER all
        # margin setup so nothing overrides it. The old hardcoded
        # setMarginsForegroundColor/BackgroundColor/setMarginsFont lines
        # that used to live here are replaced by this one theme-driven call.
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()
```


**New version:**


```python
    def __init__(self, parent=None, path: Path | None = None, is_python_file: bool = True, ruff_lsp_client = None):
        """Initialize this component and its existing Qt widgets and signal connections.

        Use the declared Qt enum scope and checked required objects so the
        installed PyQt5 stubs can describe the same values used at runtime.
        """
        super().__init__(parent)
        
        # Store the absolute logical file path. Ruff LSP uses it to form the stable
        # document UEI sent in didOpen/didChanged notifications.
        
        self.path = path
        self.full_path = self.path.absolute() if self.path else None
        self.is_python_file = is_python_file
        self.ruff_lsp = None
        self._manual_completion_generation = None

        self._ruff_hover_active = False
        self._loading_text = False
        self._shutting_down = False
        self._autocomplete_timer = QTimer(self)
        self._autocomplete_timer.setSingleShot(True)
        self._autocomplete_timer.setInterval(300)
        self._autocomplete_timer.timeout.connect(self._trigger_autocomplete)

        self._pending_line = 0
        self._pending_index = 0
        self.cursorPositionChanged.connect(self._cursorPositionChanged)

        self.setUtf8(True)

        # NOTE: no editor-level font anymore. The theme (via the lexer)
        # owns family, size, colors and paper — one source of truth.
        # The lexer is created below; helpers on it (editor_font(),
        # editor_color()) supply the margins/popup/caret values.

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setIndentationGuides(True)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)
        self.setEolMode(
            QsciScintilla.EolUnix if sys.platform != "win32" else QsciScintilla.EolWindows
        )
        self.setEolVisibility(False)

        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)

        # Caret styling defaults; replaced by theme values once the lexer
        # exists (see _apply_theme_editor_style below + _apply_editor_settings
        # in main.py after a lexer swap). Kept as safe fallbacks so the
        # widget is never unstyled before a theme loads.
        self.setCaretForegroundColor(QColor("#f31122"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#3d424d"))
        self.setCaretWidth(2)

        if self.is_python_file:
            if ruff_lsp_client is not None:
                self.ruff_lsp = RuffLspController(editor=self, client=ruff_lsp_client, parent=self)


            self._ruff_hover_timer = QTimer(self)
            self._ruff_hover_timer.setSingleShot(True)
            self._ruff_hover_timer.setInterval(150)
            self._ruff_hover_timer.timeout.connect(self._trigger_ruff_hover)
            
            # An owned timer can be stopped when Space/Enter dismisses help.
            self._signature_timer = QTimer(self)
            self._signature_timer.setSingleShot(True)
            self._signature_timer.setInterval(50)
            self._signature_timer.timeout.connect(self._trigger_signature_help)
            self.signature_helper = SignatureHelper()
            self.signature_helper.signature_ready.connect(self._on_signature_ready)
            self.signature_helper.signature_empty.connect(self._on_signature_empty)

            self.hover_helper = HoverHelper()
            self.hover_helper.hover_info_ready.connect(self._on_hover_ready)
            self.hover_helper.hover_info_empty.connect(self._on_hover_empty)

            # DocumentationPopup ows only the UI. HoverHelper still performs
            # Jedi analysis is its worker thread and emits plain text results.
            # Create one popup for this editor tab. Passing self as parent means
            # Qt cleans it up automatically when this PythonEditor is destroyed.
            # The lexer loads the theme itself — font, colors and paper all
            # come from themes/theme.json (or the theme chosen in Settings).
            # Created FIRST so everything below can read its theme helpers.
            self.py_lexer = PyCustomLexer(self)

            self.documentation_popup = DocumentationPopup(self)
            self.documentation_popup.dismissed.connect(self._cancel_documentation)
            self._documentation_global_pos = None
            # Popup font follows the theme's global editor font (the old
            # self.window_font is gone — the lexer owns fonts now).
            self.documentation_popup.set_documentation_font(
                self.py_lexer.editor_font())

            self.setMouseTracking(True)

            self._apply_theme_editor_style()

            self._api = QsciAPIs(self.py_lexer)
            self.auto_completer = AutoCompleter(
                str(self.full_path) if self.full_path else None, self._api
            )
            self.auto_completer.completions_ready.connect(self._apply_completions)
            self.auto_completer.error.connect(self._handle_completion_error)

            self.setLexer(self.py_lexer)
        else:
            # No lexer in this mode yet (tab not converted): neutral defaults.
            # Once a lexer attaches, _apply_theme_editor_style takes over.
            self.setPaper(QColor("#1e1f22"))
            self.setColor(QColor("#abb2bf"))

        self.definition_finder = DefinitionFinder()
        self.definition_finder.definition_found.connect(self._on_definition_found)
        self.definition_finder.definition_not_found.connect(self._on_definition_not_found)
        self.definition_finder.error.connect(self._on_definition_error)

        # Margin 0: source-code line numbers.
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")

        # Margin 1: Ruff error, warning, information and quick-fix symbols.
        self.setMarginType(1, QsciScintilla.SymbolMargin)
        self.setMarginWidth(1, "000")

        ruff_marker_mask = (
            (1 << RuffDiagnosticView.ERROR_MARKER)
            | (1 << RuffDiagnosticView.WARNING_MARKER)
            | (1 << RuffDiagnosticView.INFO_MARKER)
            | (1 << RuffDiagnosticView.FIX_MARKER)
        )
        self.setMarginMarkerMask(1, ruff_marker_mask)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWrapMode(QsciScintilla.WrapNone)

        # Final theme application (font, margins, caret, paper) — AFTER all
        # margin setup so nothing overrides it. The old hardcoded
        # setMarginsForegroundColor/BackgroundColor/setMarginsFont lines
        # that used to live here are replaced by this one theme-driven call.
        if getattr(self, "py_lexer", None) is not None:
            self._apply_theme_editor_style()
```


**Implementation:** inside `python_editor/pythoneditor.py`, replace only `PythonEditor.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.21.2 Existing method/function `PythonEditor.contextMenuEvent`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 267–298:**


```python
    def contextMenuEvent(self, event):
        """
        Request documentation for a right-clicked identifier.
        
        Blank space retains the existing diagnostic/editor context menu. 
        A keyboard menu request also keeps the normal context menu behavior.
        """
        from PyQt5.QtGui import QContextMenuEvent
        # A mirrored view routes fixes through the sole document synchronizer;
        controller = self.ruff_lsp
        store = getattr(self.window(), "documents", None)
        if controller is None and store is not None and self in store.documents:
            controller = getattr(store.document(self).analysis_owner, "ruff_lsp", None)
        if (controller is not None and event.reason() == QContextMenuEvent.Mouse and controller.context_menu(event, self)):
            event.accept()
            return
        
        if (self.is_python_file and not self._shutting_down and event.reason() == QContextMenuEvent.Mouse):
            target = self._documentation_target(event.pos())
            if target is not None:
                self._ruff_hover_timer.stop()
                self._dismiss_signature()
                self._documentation_global_pos = event.globalPos()
                line, column = target
                self.hover_helper.get_hover(
                    line, column, self.text(),
                    str(self.full_path) if self.full_path else None,
                )
                event.accept()
                return
        
        super().contextMenuEvent(event)
```


**New version:**


```python
    def contextMenuEvent(self, event):
        """
        Request documentation for a right-clicked identifier.
        
        Blank space retains the existing diagnostic/editor context menu. 
        A keyboard menu request also keeps the normal context menu behavior.
        """
        from PyQt5.QtGui import QContextMenuEvent
        # A mirrored view routes fixes through the sole document synchronizer;
        controller = self.ruff_lsp
        store = getattr(self.window(), "documents", None)
        if controller is None and store is not None and self in store.documents:
            controller = getattr(require_qt(store.document(self)).analysis_owner, "ruff_lsp", None)
        if (controller is not None and event.reason() == QContextMenuEvent.Reason.Mouse and controller.context_menu(event, self)):
            event.accept()
            return
        
        if (self.is_python_file and not self._shutting_down and event.reason() == QContextMenuEvent.Reason.Mouse):
            target = self._documentation_target(event.pos())
            if target is not None:
                self._ruff_hover_timer.stop()
                self._dismiss_signature()
                self._documentation_global_pos = event.globalPos()
                line, column = target
                self.hover_helper.get_hover(
                    line, column, self.text(),
                    str(self.full_path) if self.full_path else None,
                )
                event.accept()
                return
        
        super().contextMenuEvent(event)
```


**Implementation:** inside `python_editor/pythoneditor.py`, replace only `PythonEditor.contextMenuEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.21.3 Existing method/function `PythonEditor.keyPressEvent`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 420–477:**


```python
    def keyPressEvent(self, event: QKeyEvent) -> None:
            """Handle editor shortcuts, indentation, and signature scheduling."""
            # Do this before early returns for completion acceptance/indentation.
            if self.is_python_file and event.key() in (
                    Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape):
                self._dismiss_signature()

            if event.key() == Qt.Key.Key_F12:
                self.goto_definition()
                return

            if (
                    event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and event.key() == Qt.Key.Key_Space
                    and self.is_python_file
            ):
                line, column = self.getCursorPosition()
                self._manual_completion_generation = self.auto_completer.get_completions(
                    line + 1,
                    column,
                    self.text(),
                )
                return

            if (
                    event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and event.key() == Qt.Key.Key_X
                    and not self.hasSelectedText()
            ):
                line, _column = self.getCursorPosition()
                self.setSelection(line, 0, line, self.lineLength(line))
                self.cut()
                return

            if (
                    event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and self.SendScintilla(SCI_AUTOCACTIVE)
            ):
                return super().keyPressEvent(event)

            if (
                    self.is_python_file
                    and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and event.modifiers() == Qt.KeyboardModifier.NoModifier
                    and not self.hasSelectedText()
            ):
                self._handle_python_return()
                return

            if event.text() == "(" and self.is_python_file and not self._shutting_down:
                line, column = self.getCursorPosition()
                before = self.text(line)[:column]
                if self._has_callable_before_parenthesis(before):
                    # Let the base handler insert '(' first. The delayed lookup then
                    # sees the cursor/source state Jedi expects.
                    self._signature_timer.start()

            return super().keyPressEvent(event)
```


**New version:**


```python
    def keyPressEvent(self, event: QKeyEvent) -> None:
            """Handle editor shortcuts, indentation, and signature scheduling."""
            # Do this before early returns for completion acceptance/indentation.
            if self.is_python_file and event.key() in (
                    Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape):
                self._dismiss_signature()

            if event.key() == Qt.Key.Key_F12:
                self.goto_definition()
                return

            if (
                    event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and event.key() == Qt.Key.Key_Space
                    and self.is_python_file
            ):
                line, column = self.getCursorPosition()
                self._manual_completion_generation = self.auto_completer.get_completions(
                    line + 1,
                    column,
                    self.text(),
                )
                return

            if (
                    event.modifiers() == Qt.KeyboardModifier.ControlModifier
                    and event.key() == Qt.Key.Key_X
                    and not self.hasSelectedText()
            ):
                line, _column = self.getCursorPosition()
                self.setSelection(line, 0, line, self.lineLength(line))
                self.cut()
                return

            if (
                    event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and self.SendScintilla(SCI_AUTOCACTIVE)
            ):
                return super().keyPressEvent(event)

            if (
                    self.is_python_file
                    and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and event.modifiers() == Qt.KeyboardModifier.NoModifier
                    and not self.hasSelectedText()
            ):
                self._handle_python_return()
                return

            if event.text() == "(" and self.is_python_file and not self._shutting_down:
                line, column = self.getCursorPosition()
                before = self.text(line)[:column]
                if self._has_callable_before_parenthesis(before):
                    # Let the base handler insert '(' first. The delayed lookup then
                    # sees the cursor/source state Jedi expects.
                    self._signature_timer.start()

            return super().keyPressEvent(event)
```


**Implementation:** inside `python_editor/pythoneditor.py`, replace only `PythonEditor.keyPressEvent`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.22. `ruff_implementation/ruff_lsp_client.py`


#### 2.22.1 Existing method/function `RuffLspClient.is_ready`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 95–98:**


```python
    @property
    def is_ready(self) -> bool:
        """Return True only after Ruff completed LSP initialization."""
        return self._initialized and self.process.state() == QProcess.Running
```


**New version:**


```python
    @property
    def is_ready(self) -> bool:
        """Return True only after Ruff completed LSP initialization."""
        return self._initialized and self.process.state() == QProcess.ProcessState.Running
```


**Implementation:** inside `ruff_implementation/ruff_lsp_client.py`, replace only `RuffLspClient.is_ready`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.22.2 Existing method/function `RuffLspClient._send`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 312–326:**


```python
    def _send(self, payload: dict):
        """Frame and write a UTF-8 JSON-RPC message to Ruff stdin."""
        if self.process.state() != QProcess.Running:
            self.server_error.emit("Ruff server is not running.")
            return False

        # Compact JSON is optional but produces fewer bytes over the local pipe.
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

        # LSP framing uses the NUMBER OF UTF-8 BYTES, not len(str) characters.
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")

        # QProcess.write queues the bytes asynchronously to Ruff's stdin.
        self.process.write(header + body)
        return True
```


**New version:**


```python
    def _send(self, payload: dict):
        """Frame and write a UTF-8 JSON-RPC message to Ruff stdin."""
        if self.process.state() != QProcess.ProcessState.Running:
            self.server_error.emit("Ruff server is not running.")
            return False

        # Compact JSON is optional but produces fewer bytes over the local pipe.
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

        # LSP framing uses the NUMBER OF UTF-8 BYTES, not len(str) characters.
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")

        # QProcess.write queues the bytes asynchronously to Ruff's stdin.
        self.process.write(header + body)
        return True
```


**Implementation:** inside `ruff_implementation/ruff_lsp_client.py`, replace only `RuffLspClient._send`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.22.3 Existing method/function `RuffLspClient.shutdown`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 443–460:**


```python
    def shutdown(self):
        """Perform the LSP shutdown → exit sequence, then enforce a timeout."""
        self._shutting_down = True
        if self.process.state() == QProcess.NotRunning:
            return

        def after_shutdown(_result, error):
            if error is None and self.process.state() == QProcess.Running:
                self.notify("exit", {})
            else:
                self._force_stop()

        if self._initialized:
            # LSP shutdown has no params. Sending {} is invalid for Ruff.
            self.request("shutdown", None, after_shutdown)
            QTimer.singleShot(2000, self._force_stop)
        else:
            self._force_stop()
```


**New version:**


```python
    def shutdown(self):
        """Perform the LSP shutdown → exit sequence, then enforce a timeout."""
        self._shutting_down = True
        if self.process.state() == QProcess.ProcessState.NotRunning:
            return

        def after_shutdown(_result, error):
            """Complete the language-server shutdown after its response arrives.

            Compare the actual QProcess state/error enum. This preserves the
            existing lifecycle behavior and avoids unrecognized alias attributes.
            """
            if error is None and self.process.state() == QProcess.ProcessState.Running:
                self.notify("exit", {})
            else:
                self._force_stop()

        if self._initialized:
            # LSP shutdown has no params. Sending {} is invalid for Ruff.
            self.request("shutdown", None, after_shutdown)
            QTimer.singleShot(2000, self._force_stop)
        else:
            self._force_stop()
```


**Implementation:** inside `ruff_implementation/ruff_lsp_client.py`, replace only `RuffLspClient.shutdown`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.22.4 Existing method/function `RuffLspClient._force_stop`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 462–465:**


```python
    def _force_stop(self):
        """Kill only when graceful shutdown did not finish."""
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
```


**New version:**


```python
    def _force_stop(self):
        """Kill only when graceful shutdown did not finish."""
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
```


**Implementation:** inside `ruff_implementation/ruff_lsp_client.py`, replace only `RuffLspClient._force_stop`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.23. `side_bar_widgets/code_outline.py`


#### 2.23.1 Existing method/function `CodeOutlineTree.update_outline`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 37–71:**


```python
    def update_outline(self, code: str):
        """Parse Python code and rebuild the tree."""
        self.clear()
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Code has syntax errors -- can't parse item
            return
        
        # Walk the top-level nodes of the module body
        # We only look at top-level classes and functions.
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_item = QTreeWidgetItem(self)
                class_item.setText(0, f"class {node.name}")
                class_item.setData(0, Qt.UserRole, (node.lineno - 1, node.col_offset))
                class_item.setForeground(0, self._color("#e5c07b"))

                # Add methods as children
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_item = QTreeWidgetItem(class_item)
                        method_item.setText(0, f"def {child.name}()")
                        method_item.setData(0, Qt.UserRole, (child.lineno - 1, child.col_offset))
                        method_item.setForeground(0, self._color("#61afef"))
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_item = QTreeWidgetItem(self)
                function_item.setText(0, f"def {node.name}()")
                function_item.setData(0, Qt.UserRole, (node.lineno - 1, node.col_offset))
                function_item.setForeground(0, self._color("#61afef"))
                
        # Expand all class nodes by default
        self.expandAll()
```


**New version:**


```python
    def update_outline(self, code: str):
        """Parse Python code and rebuild the tree."""
        self.clear()
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Code has syntax errors -- can't parse item
            return
        
        # Walk the top-level nodes of the module body
        # We only look at top-level classes and functions.
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_item = QTreeWidgetItem(self)
                class_item.setText(0, f"class {node.name}")
                class_item.setData(0, Qt.ItemDataRole.UserRole, (node.lineno - 1, node.col_offset))
                class_item.setForeground(0, self._color("#e5c07b"))

                # Add methods as children
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_item = QTreeWidgetItem(class_item)
                        method_item.setText(0, f"def {child.name}()")
                        method_item.setData(0, Qt.ItemDataRole.UserRole, (child.lineno - 1, child.col_offset))
                        method_item.setForeground(0, self._color("#61afef"))
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_item = QTreeWidgetItem(self)
                function_item.setText(0, f"def {node.name}()")
                function_item.setData(0, Qt.ItemDataRole.UserRole, (node.lineno - 1, node.col_offset))
                function_item.setForeground(0, self._color("#61afef"))
                
        # Expand all class nodes by default
        self.expandAll()
```


**Implementation:** inside `side_bar_widgets/code_outline.py`, replace only `CodeOutlineTree.update_outline`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.23.2 Existing method/function `CodeOutlineTree._on_item_clicked`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 73–78:**


```python
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """When the user clicks a symbol, emit the line/column"""
        data = item.data(0, Qt.UserRole)
        if data is not None:
            line, col = data
            self.symbol_clicked.emit(line, col)
```


**New version:**


```python
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """When the user clicks a symbol, emit the line/column"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data is not None:
            line, col = data
            self.symbol_clicked.emit(line, col)
```


**Implementation:** inside `side_bar_widgets/code_outline.py`, replace only `CodeOutlineTree._on_item_clicked`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.24. `side_bar_widgets/problems_panel.py`


#### 2.24.1 Existing method/function `ProblemsPanel.set_diagnostics`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 19–44:**


```python
    def set_diagnostics(self, diagnostics: list[Diagnostic]) -> None:
        """
        Replace displayed rows with a complete, provider-labelledsnapshot.
        
        Line and column labels are one-based for users, while the stored record
        retains zero-based positions for navigation. Preserve the actual record
        in Qt.UserRole rather than trying to parse labels when a row is opened.
        """
        self.clear()
        labels = {
            DiagnosticSeverity.ERROR: "Error",
            DiagnosticSeverity.WARNING: "Warning",
            DiagnosticSeverity.INFORMATION: "Info",
        }
        
        for diagnostic in diagnostics:
            start = diagnostic.source_range.start
            row = QTreeWidgetItem((
                labels[diagnostic.severity],
                diagnostic.path.name if diagnostic.path else diagnostic.uri,
                str(start.line + 1), str(start.column + 1),
                f"{diagnostic.provider}: {diagnostic.code}", 
                diagnostic.message,
            ))
            row.setData(0, Qt.UserRole, diagnostic)
            self.addTopLevelItem(row)
```


**New version:**


```python
    def set_diagnostics(self, diagnostics: list[Diagnostic]) -> None:
        """
        Replace displayed rows with a complete, provider-labelledsnapshot.
        
        Line and column labels are one-based for users, while the stored record
        retains zero-based positions for navigation. Preserve the actual record
        in Qt.UserRole rather than trying to parse labels when a row is opened.
        """
        self.clear()
        labels = {
            DiagnosticSeverity.ERROR: "Error",
            DiagnosticSeverity.WARNING: "Warning",
            DiagnosticSeverity.INFORMATION: "Info",
        }
        
        for diagnostic in diagnostics:
            start = diagnostic.source_range.start
            row = QTreeWidgetItem((
                labels[diagnostic.severity],
                diagnostic.path.name if diagnostic.path else diagnostic.uri,
                str(start.line + 1), str(start.column + 1),
                f"{diagnostic.provider}: {diagnostic.code}", 
                diagnostic.message,
            ))
            row.setData(0, Qt.ItemDataRole.UserRole, diagnostic)
            self.addTopLevelItem(row)
```


**Implementation:** inside `side_bar_widgets/problems_panel.py`, replace only `ProblemsPanel.set_diagnostics`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.24.2 Existing method/function `ProblemsPanel._activate`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 46–50:**


```python
    def _activate(self, item: QTreeWidgetItem, _column: int) -> None:
        """Emnit the diagnostic stored on the activated row without parsing visible text."""
        diagnostic = item.data(0, Qt.UserRole)
        if diagnostic is not None:
            self.diagnosticActivated.emit(diagnostic)
```


**New version:**


```python
    def _activate(self, item: QTreeWidgetItem, _column: int) -> None:
        """Emnit the diagnostic stored on the activated row without parsing visible text."""
        diagnostic = item.data(0, Qt.ItemDataRole.UserRole)
        if diagnostic is not None:
            self.diagnosticActivated.emit(diagnostic)
```


**Implementation:** inside `side_bar_widgets/problems_panel.py`, replace only `ProblemsPanel._activate`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.25. `tests/test_terminal_widget.py`


#### 2.25.1 Existing method/function `_press`

Deliver one synthetic key press directly to a terminal view. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 10–25:**


```python
def _press(
        view: TerminalView,
        key: int,
        text: str = "",
        modifiers=Qt.NoModifier,
) -> None:
    """Deliver one synthetic key press directly to a terminal view.

    Args:
        view: TerminalView under test.
        key: Qt key constant such as Qt.Key_Up.
        text: Printable Unicode associated with the event.
        modifiers: Ctrl, Shift, Alt, or Meta modifier flags.
    """
    event = QKeyEvent(QKeyEvent.KeyPress, key, modifiers, text)
    view.keyPressEvent(event)
```


**New version:**


```python
def _press(
        view: TerminalView,
        key: int,
        text: str = "",
        modifiers=Qt.KeyboardModifier.NoModifier,
) -> None:
    """Deliver one synthetic key press directly to a terminal view.

    Args:
        view: TerminalView under test.
        key: Qt key constant such as Qt.Key_Up.
        text: Printable Unicode associated with the event.
        modifiers: Ctrl, Shift, Alt, or Meta modifier flags.
    """
    event = QKeyEvent(QKeyEvent.KeyPress, key, modifiers, text)
    view.keyPressEvent(event)
```


**Implementation:** inside `tests/test_terminal_widget.py`, replace only `_press`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.25.2 Existing method/function `test_history_and_editing_keys_are_forwarded`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 27–45:**


```python
def test_history_and_editing_keys_are_forwarded(qtbot) -> None:
    """Translate history and line-editing keys to their VT sequences."""
    written: list[str] = []
    view = TerminalView(written.append)
    qtbot.addWidget(view)

    _press(view, Qt.Key_Up)
    _press(view, Qt.Key_Down)
    _press(view, Qt.Key_Left)
    _press(view, Qt.Key_Backspace)
    _press(view, Qt.Key_Return)

    assert written == [
        "\x1b[A",
        "\x1b[B",
        "\x1b[D",
        "\x7f",
        "\r",
    ]
```


**New version:**


```python
def test_history_and_editing_keys_are_forwarded(qtbot) -> None:
    """Translate history and line-editing keys to their VT sequences."""
    written: list[str] = []
    view = TerminalView(written.append)
    qtbot.addWidget(view)

    _press(view, Qt.Key.Key_Up)
    _press(view, Qt.Key.Key_Down)
    _press(view, Qt.Key.Key_Left)
    _press(view, Qt.Key.Key_Backspace)
    _press(view, Qt.Key.Key_Return)

    assert written == [
        "\x1b[A",
        "\x1b[B",
        "\x1b[D",
        "\x7f",
        "\r",
    ]
```


**Implementation:** inside `tests/test_terminal_widget.py`, replace only `test_history_and_editing_keys_are_forwarded`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.25.3 Existing method/function `test_typing_cannot_edit_previous_output`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 47–65:**


```python
def test_typing_cannot_edit_previous_output(qtbot) -> None:
    """Keep rendered output unchanged when typing after clicking an old line."""
    written: list[str] = []
    view = TerminalView(written.append)
    qtbot.addWidget(view)
    view.setPlainText("PS C:\\project> ")

    # Simulate clicking at the very start of historical terminal output.
    cursor = view.textCursor()
    cursor.setPosition(0)
    view.setTextCursor(cursor)

    _press(view, Qt.Key_A, "a")

    # Qt did not insert the character into its read-only document.
    assert view.toPlainText() == "PS C:\\project> "

    # The character was forwarded to the shell writer instead.
    assert written == ["a"]
```


**New version:**


```python
def test_typing_cannot_edit_previous_output(qtbot) -> None:
    """Keep rendered output unchanged when typing after clicking an old line."""
    written: list[str] = []
    view = TerminalView(written.append)
    qtbot.addWidget(view)
    view.setPlainText("PS C:\\project> ")

    # Simulate clicking at the very start of historical terminal output.
    cursor = view.textCursor()
    cursor.setPosition(0)
    view.setTextCursor(cursor)

    _press(view, Qt.Key.Key_A, "a")

    # Qt did not insert the character into its read-only document.
    assert view.toPlainText() == "PS C:\\project> "

    # The character was forwarded to the shell writer instead.
    assert written == ["a"]
```


**Implementation:** inside `tests/test_terminal_widget.py`, replace only `test_typing_cannot_edit_previous_output`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.25.4 Existing method/function `test_ctrl_c_copies_selection_or_interrupts`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 67–86:**


```python
def test_ctrl_c_copies_selection_or_interrupts(qtbot) -> None:
    """Copy selected text but interrupt the shell when nothing is selected."""
    written: list[str] = []
    view = TerminalView(written.append)
    qtbot.addWidget(view)
    view.setPlainText("output")

    # With no selection, Ctrl+C becomes ASCII ETX (code point 3).
    _press(view, Qt.Key_C, "\x03", Qt.ControlModifier)
    assert written == ["\x03"]

    cursor = view.textCursor()
    cursor.select(QTextCursor.Document)
    view.setTextCursor(cursor)

    # With a selection, Ctrl+C uses the normal Qt clipboard behavior.
    _press(view, Qt.Key_C, "\x03", Qt.ControlModifier)

    assert QApplication.clipboard().text() == "output"
    assert written == ["\x03"]
```


**New version:**


```python
def test_ctrl_c_copies_selection_or_interrupts(qtbot) -> None:
    """Copy selected text but interrupt the shell when nothing is selected."""
    written: list[str] = []
    view = TerminalView(written.append)
    qtbot.addWidget(view)
    view.setPlainText("output")

    # With no selection, Ctrl+C becomes ASCII ETX (code point 3).
    _press(view, Qt.Key.Key_C, "\x03", Qt.KeyboardModifier.ControlModifier)
    assert written == ["\x03"]

    cursor = view.textCursor()
    cursor.select(QTextCursor.SelectionType.Document)
    view.setTextCursor(cursor)

    # With a selection, Ctrl+C uses the normal Qt clipboard behavior.
    _press(view, Qt.Key.Key_C, "\x03", Qt.KeyboardModifier.ControlModifier)

    assert QApplication.clipboard().text() == "output"
    assert written == ["\x03"]
```


**Implementation:** inside `tests/test_terminal_widget.py`, replace only `test_ctrl_c_copies_selection_or_interrupts`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 2.25.5 Existing method/function `test_paste_is_sent_without_editing_document`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 88–102:**


```python
def test_paste_is_sent_without_editing_document(qtbot) -> None:
    """Send pasted text to the shell and preserve the protected Qt document."""
    written: list[str] = []
    view = TerminalView(written.append)
    qtbot.addWidget(view)
    view.setPlainText("PS> ")
    QApplication.clipboard().setText("one\ntwo")

    _press(view, Qt.Key_V, "v", Qt.ControlModifier)

    # The QPlainTextEdit remains a rendering surface, not the input buffer.
    assert view.toPlainText() == "PS> "

    # The newline was converted to the terminal Enter representation.
    assert written == ["one\rtwo"]
```


**New version:**


```python
def test_paste_is_sent_without_editing_document(qtbot) -> None:
    """Send pasted text to the shell and preserve the protected Qt document."""
    written: list[str] = []
    view = TerminalView(written.append)
    qtbot.addWidget(view)
    view.setPlainText("PS> ")
    QApplication.clipboard().setText("one\ntwo")

    _press(view, Qt.Key.Key_V, "v", Qt.KeyboardModifier.ControlModifier)

    # The QPlainTextEdit remains a rendering surface, not the input buffer.
    assert view.toPlainText() == "PS> "

    # The newline was converted to the terminal Enter representation.
    assert written == ["one\rtwo"]
```


**Implementation:** inside `tests/test_terminal_widget.py`, replace only `test_paste_is_sent_without_editing_document`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 2.26. `title_bar.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `from PyQt5.QtWidgets import QHBoxLayout, QLabel, QStyle, QToolButton, QWidget` (original line 3).


```python

from code_inteligence.qt_helpers import require_qt
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 2.26.1 Existing method/function `CustomTitleBar.__init__`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 9–69:**


```python
    def __init__(self, parent: QWidget) -> None:
        """Create the title label and connect each window-control button."""
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Highlight)
        self.initial_pos = None

        # Supplying self both owns and installs the layout.
        titlebar_layout = QHBoxLayout(self)
        titlebar_layout.setContentsMargins(0, 0, 0, 0)
        titlebar_layout.setSpacing(2)

        self.title = QLabel(self.__class__.__name__, self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title.setText(title)
        titlebar_layout.addWidget(self.title)

        self.min_btn = QToolButton(self)
        self.min_btn.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_TitleBarMinButton
            )
        )
        # Connect bound methods. Parentheses would invoke them now.
        self.min_btn.clicked.connect(self.window().showMinimized)

        self.max_btn = QToolButton(self)
        self.max_btn.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_TitleBarMaxButton
            )
        )
        self.max_btn.clicked.connect(self.window().showMaximized)

        self.close_btn = QToolButton(self)
        self.close_btn.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_TitleBarCloseButton
            )
        )
        self.close_btn.clicked.connect(self.window().close)

        self.norm_btn = QToolButton(self)
        self.norm_btn.setIcon(
            self.style().standardIcon(
                QStyle.StandardPixmap.SP_TitleBarNormalButton
            )
        )
        self.norm_btn.clicked.connect(self.window().showNormal)
        self.norm_btn.setVisible(False)

        for button in (
            self.min_btn,
            self.norm_btn,
            self.max_btn,
            self.close_btn,
        ):
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(28, 28))
            titlebar_layout.addWidget(button)
```


**New version:**


```python
    def __init__(self, parent: QWidget) -> None:
        """Create the title label and connect each window-control button."""
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.ColorRole.Highlight)
        self.initial_pos = None

        # Supplying self both owns and installs the layout.
        titlebar_layout = QHBoxLayout(self)
        titlebar_layout.setContentsMargins(0, 0, 0, 0)
        titlebar_layout.setSpacing(2)

        self.title = QLabel(self.__class__.__name__, self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if title := parent.windowTitle():
            self.title.setText(title)
        titlebar_layout.addWidget(self.title)

        self.min_btn = QToolButton(self)
        self.min_btn.setIcon(
            require_qt(self.style()).standardIcon(
                QStyle.StandardPixmap.SP_TitleBarMinButton
            )
        )
        # Connect bound methods. Parentheses would invoke them now.
        self.min_btn.clicked.connect(self.window().showMinimized)

        self.max_btn = QToolButton(self)
        self.max_btn.setIcon(
            require_qt(self.style()).standardIcon(
                QStyle.StandardPixmap.SP_TitleBarMaxButton
            )
        )
        self.max_btn.clicked.connect(self.window().showMaximized)

        self.close_btn = QToolButton(self)
        self.close_btn.setIcon(
            require_qt(self.style()).standardIcon(
                QStyle.StandardPixmap.SP_TitleBarCloseButton
            )
        )
        self.close_btn.clicked.connect(self.window().close)

        self.norm_btn = QToolButton(self)
        self.norm_btn.setIcon(
            require_qt(self.style()).standardIcon(
                QStyle.StandardPixmap.SP_TitleBarNormalButton
            )
        )
        self.norm_btn.clicked.connect(self.window().showNormal)
        self.norm_btn.setVisible(False)

        for button in (
            self.min_btn,
            self.norm_btn,
            self.max_btn,
            self.close_btn,
        ):
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(QSize(28, 28))
            titlebar_layout.addWidget(button)
```


**Implementation:** inside `title_bar.py`, replace only `CustomTitleBar.__init__`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### Implement and check Topic 2


The only new files in this topic are `code_inteligence/qt_helpers.py` and `code_inteligence/clickable_label.py`, both in the existing folder. Complete their creation before adding imports. Existing files are changed method by method above; no existing file is deleted. Preserve all methods not shown, including Ruff action application and quick-fix revision checks.


Restart the editor, open its menus and sidebar, click a sidebar icon, and open a project folder. QAction/menu/status-bar construction and QFileSystemModel access must still work. This topic also includes the window-side guard needed for Topic 4; it becomes useful when the providers retain pending results. It does not change Ruff’s selected lint rules.


```powershell
python -m basedpyright --project pyproject.toml
```


This command still reports remaining issues; it is not expected to exit cleanly for this repository. Do not change missing-attribute/undefined-name rules to `none` merely to obtain a clean report. Also do not install PyQt5-stubs as part of this guide: the tested replacement-stub package masked QScintilla information in this environment.


## Topic 3 — Repair the basedpyright language-server connection


### Explanation and documentation


The pushed connection has concrete protocol/configuration errors: `_settings()` returns a tuple because of a trailing comma; four setting names are misspelled; the frame reader lowercases header names and then looks up mixed-case `Content-Length`; and initialization continues after an error. These prevent correct configuration or kill a valid connection. The replacements below repair those boundaries without removing document-version checks.


Documentation: [LSP base protocol](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/baseProtocol/), [LSP initialization](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#initialize), [basedpyright language-server settings](https://docs.basedpyright.com/latest/configuration/language-server-settings/).


### 3.1. `ruff_implementation/type_diagnostic.py`


#### 3.1.1 Existing method/function `TypeDiagnostics.update`

Remove the eager empty replacement. The stored previous collection remains available until the server publishes a matching current revision; the existing version checks still reject late responses.


**Old version — original lines 99–110:**


```python
    def update(self, snapshot: DocumentSnapshot) -> None:
        """
        Retain only the newest source for this URI and debounce transmission.
        
        Recording the new version immediately invalidates older server results
        even before the debounce expires and didChange has been transmitted.
        """
        if self._closing:
            return
        self._documents[snapshot.uri] = snapshot
        self.manager.replace("basedpyright", snapshot.uri, [])
        self._debounce.start()
```


**New version:**


```python
    def update(self, snapshot: DocumentSnapshot) -> None:
        """
        Retain only the newest source for this URI and debounce transmission.
        
        Recording the new version immediately invalidates older server results
        even before the debounce expires and didChange has been transmitted.
        """
        if self._closing:
            return
        self._documents[snapshot.uri] = snapshot
        # Retain the last-known collection until a matching response replaces
        # it. Clearing here makes every keystroke erase the shared underlines.
        self._debounce.start()
```


**Implementation:** inside `ruff_implementation/type_diagnostic.py`, replace only `TypeDiagnostics.update`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 3.1.2 Existing method/function `TypeDiagnostics._settings`

Fix all four misspelled configuration keys and return a dictionary rather than a one-element tuple. Keep unknown-name, missing-attribute and optional-member checks at error severity. The standard checking profile is an explicit policy change, not proof that every previous warning was false.


**Old version — original lines 132–154:**


```python
    def _settings(self) -> dict:
        """
        Return server settings with semantic errirs enabled by default.
        
        Project basedpyright configuration can refine these defaults. 
        Python's interpreter Path is seperate from analysis settings because
        the server uses it to resolve installed packages and their type information.
        """
        return {
            "python": {"pythonPath": self.python},
            "basedpyright": {
                "disableOrganizedImports": True,
                "analysis": {
                    "diagnosticMode": "openFilesOnly",
                    "typedCheckingMode": "recommended",
                    "diagnosticSevereityOverrides": {
                        "reportUndefinedOverrides": "error",
                        "reportAttributeAccessIssue": "error",
                        "reportOptionalMemberAccess": "error",
                    },
                },
            },
        },
```


**New version:**


```python
    def _settings(self) -> dict:
        """
        Return correctly named LSP settings with core semantic checks enabled.
        
        Project basedpyright configuration can refine these defaults. 
        Python's interpreter Path is seperate from analysis settings because
        the server uses it to resolve installed packages and their type information.
        """
        # Return a dictionary, not a one-element tuple: configuration requests
        # select nested sections from this object.
        return {
            "python": {"pythonPath": self.python},
            "basedpyright": {
                "disableOrganizeImports": True,
                "analysis": {
                    "diagnosticMode": "openFilesOnly",
                    "typeCheckingMode": "standard",
                    "diagnosticSeverityOverrides": {
                        "reportUndefinedVariable": "error",
                        "reportAttributeAccessIssue": "error",
                        "reportOptionalMemberAccess": "error",
                    },
                },
            },
        }
```


**Implementation:** inside `ruff_implementation/type_diagnostic.py`, replace only `TypeDiagnostics._settings`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 3.1.3 Existing method/function `TypeDiagnostics._initialized`

Return immediately after a failed initialize response. A killed/failed server must not become ready or receive document notifications.


**Old version — original lines 178–200:**


```python
    def _initialized(self, result, error) -> None:
        """
        Complete the handshake, configure analysis, then send current buffers.
        
        No didOpen sis sent before initialized. A failed handshake kills this
        process and reports why instead of silently leaving analysis disabled.
        """
        if self._closing or self._restart_requested:
            self.process.kill()
            return
        if error:
            self.error.emit(f"basedpyright initialization failed: {error}")
            self.process.kill()
        encoding = (result or {}).get("capabilities", {}).get("positionEncoding", "utf-16")
        if encoding != "utf-16":
            self.error.emit(f"Unsupported basedpyright position encoding: {encoding}")
            self.process.kill()
            return
        self._deadline.stop()
        self._notify("initialized", {})
        self._ready = True
        self._notify("workspace/didChangeConfiguration", {"settings": self._settings()})
        self._flush()
```


**New version:**


```python
    def _initialized(self, result, error) -> None:
        """
        Complete the handshake, configure analysis, then send current buffers.
        
        No didOpen sis sent before initialized. A failed handshake kills this
        process and reports why instead of silently leaving analysis disabled.
        """
        if self._closing or self._restart_requested:
            self.process.kill()
            return
        if error:
            self.error.emit(f"basedpyright initialization failed: {error}")
            self.process.kill()
            return  # A failed initialize response must never set _ready.
        encoding = (result or {}).get("capabilities", {}).get("positionEncoding", "utf-16")
        if encoding != "utf-16":
            self.error.emit(f"Unsupported basedpyright position encoding: {encoding}")
            self.process.kill()
            return
        self._deadline.stop()
        self._notify("initialized", {})
        self._ready = True
        self._notify("workspace/didChangeConfiguration", {"settings": self._settings()})
        self._flush()
```


**Implementation:** inside `ruff_implementation/type_diagnostic.py`, replace only `TypeDiagnostics._initialized`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 3.1.4 Existing method/function `TypeDiagnostics._send`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 231–243:**


```python
    def _send(self, payload: dict) -> None:
        """
        Frame JSON with its UTF-8 byte length and queue it to server stdin.

        Python string length is not a valid Content-Length for umlauts or emoji.
        QProcess.write queues bytes without waiting for server analysis
        :param payload:
        :return:
        """
        if self.process.state() != QProcess.Running:
            return
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.process.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body)
```


**New version:**


```python
    def _send(self, payload: dict) -> None:
        """
        Frame JSON with its UTF-8 byte length and queue it to server stdin.

        Python string length is not a valid Content-Length for umlauts or emoji.
        QProcess.write queues bytes without waiting for server analysis
        :param payload:
        :return:
        """
        if self.process.state() != QProcess.ProcessState.Running:
            return
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.process.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body)
```


**Implementation:** inside `ruff_implementation/type_diagnostic.py`, replace only `TypeDiagnostics._send`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 3.1.5 Existing method/function `TypeDiagnostics._read_stdout`

Header names are lowercased when parsed, so Content-Length must be looked up as `content-length`. The old mixed-case lookup killed a valid connection with KeyError.


**Old version — original lines 245–273:**


```python
    def _read_stdout(self) -> None:
        """
        Reassemble partial or concatenated Content-Length protocol messages.

        Keep incomplete frames for the next readyRead signal. A malformed frame
        terminates the connection because continuing could misread later bytes.
        """
        self._buffer.extend(bytes(self.process.readAllStandardOutput()))
        try:
            if len(self._buffer) > 32 * 1024 * 1024:
                raise ValueError("protocol buffer exceeded 32 MiB")
            while True:
                header_end = self._buffer.find(b"\r\n\r\n")
                if header_end < 0:
                    return
                headers = self._buffer[:header_end].decode("ascii")
                fields = dict(line.lower().split(":", 1) for line in headers.split("\r\n"))
                size = int(fields["Content-Length"].strip())
                if not 0 <= size <= 32 * 1024 * 1024:
                    raise ValueError("invalid Content-Length")
                end = header_end + 4 + size
                if len(self._buffer) < end:
                    return
                message = json.loads(bytes(self._buffer[header_end + 4:end]))
                del self._buffer[:end]
                self._route(message)
        except (ValueError, KeyError, UnicodeError, TypeError) as error:
            self.error.emit(f"basedpyright protocol error: {error}")
            self.process.kill()
```


**New version:**


```python
    def _read_stdout(self) -> None:
        """
        Reassemble partial or concatenated Content-Length protocol messages.

        Keep incomplete frames for the next readyRead signal. A malformed frame
        terminates the connection because continuing could misread later bytes.
        """
        self._buffer.extend(bytes(self.process.readAllStandardOutput()))
        try:
            if len(self._buffer) > 32 * 1024 * 1024:
                raise ValueError("protocol buffer exceeded 32 MiB")
            while True:
                header_end = self._buffer.find(b"\r\n\r\n")
                if header_end < 0:
                    return
                headers = self._buffer[:header_end].decode("ascii")
                fields = dict(line.lower().split(":", 1) for line in headers.split("\r\n"))
                # Header names were normalized above; use the normalized key.
                size = int(fields["content-length"].strip())
                if not 0 <= size <= 32 * 1024 * 1024:
                    raise ValueError("invalid Content-Length")
                end = header_end + 4 + size
                if len(self._buffer) < end:
                    return
                message = json.loads(bytes(self._buffer[header_end + 4:end]))
                del self._buffer[:end]
                self._route(message)
        except (ValueError, KeyError, UnicodeError, TypeError) as error:
            self.error.emit(f"basedpyright protocol error: {error}")
            self.process.kill()
```


**Implementation:** inside `ruff_implementation/type_diagnostic.py`, replace only `TypeDiagnostics._read_stdout`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 3.1.6 Existing method/function `TypeDiagnostics.is_running`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 456–458:**


```python
    def is_running(self) -> bool:

        return self.process.state() != QProcess.NotRunning
```


**New version:**


```python
    def is_running(self) -> bool:

        """Return whether the basedpyright QProcess is starting or running.

        Compare the actual QProcess state/error enum. This preserves the
        existing lifecycle behavior and avoids unrecognized alias attributes.
        """
        return self.process.state() != QProcess.ProcessState.NotRunning
```


**Implementation:** inside `ruff_implementation/type_diagnostic.py`, replace only `TypeDiagnostics.is_running`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 3.1.7 Existing method/function `TypeDiagnostics._process_error`

The enum is accessed through its declared scope. These values were compared with their old runtime aliases in the installed Qt binding; this changes how the type checker resolves the symbol.


**Old version — original lines 480–485:**


```python
    def _process_error(self, error) -> None:

        if error == QProcess.FailedToStart:
            self._deadline.stop()
        if not self._closing:
            self.error.emit("basedpyright process error:" + self.process.errorString())
```


**New version:**


```python
    def _process_error(self, error) -> None:

        """Report process launch or runtime failures through the analysis error signal.

        Compare the actual QProcess state/error enum. This preserves the
        existing lifecycle behavior and avoids unrecognized alias attributes.
        """
        if error == QProcess.ProcessError.FailedToStart:
            self._deadline.stop()
        if not self._closing:
            self.error.emit("basedpyright process error:" + self.process.errorString())
```


**Implementation:** inside `ruff_implementation/type_diagnostic.py`, replace only `TypeDiagnostics._process_error`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### Implement and check Topic 3


Keep the existing singular filename `type_diagnostic.py`; do not create a parallel `type_diagnostics.py` module. No folder/file deletion is needed. Restart the editor so the corrected settings and framing code are used by a fresh server connection. Select the interpreter that actually contains basedpyright. Your reported terminal path and interpreter live under differently named project folders; that alone does not prove an error, so this guide does not change or hard-code your interpreter path.


For a small scratch Python document, use the following deliberate errors, then correct `aply` to `apply` and remove the final undefined name:


```python
class Applier:
    """Provide one declared method for a missing-member check."""

    def apply(self) -> None:
        """Represent a valid operation with no return value."""
        pass

Applier().aply()  # Deliberate missing attribute: must be reported.
missing_name      # Deliberate undefined name: must be reported.
```


The live-server regression test detected both error categories, then accepted a newer clean document version and removed the findings. Existing valid Qt code is a different case from these deliberate semantic errors.


## Topic 4 — Retain underlines while new analysis is pending


### Explanation and documentation


The old code explicitly empties diagnostic collections on each edit. That causes the observed disappearance; it is not syntax-token coloring stopping. The replacement retains last-known indicator paint while the asynchronous servers analyze newer text. Scintilla moves indicator ranges with edits. Cached Python line/column records do not move, so pending records must not supply hover text or quick fixes.


This is last-known feedback, not a claim that every visible underline already describes the current revision. Current server responses still must match the live revision. The shared renderer waits if a retained provider is stale, so another provider cannot clear its paint by publishing first. Empty current results clear resolved underlines. A long-running or stalled provider can therefore keep last-known paint visible longer; server failures must remain visible.


Documentation: [Scintilla indicators](https://www.scintilla.org/ScintillaDoc.html#Indicators), [LSP diagnostics](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_publishDiagnostics), [QTimer](https://doc.qt.io/archives/qt-5.15/qtimer.html).


### 4.1. `ruff_implementation/ruff_diagnostics_view.py`


#### 4.1.1 New method/function `RuffDiagnosticView.mark_pending`

Advance the document revision while retaining Scintilla indicator paint. Discard the old Python hover cache and any open quick-fix menu, because those records do not move with edited text.

**New code:**


```python
    def mark_pending(self) -> None:
        """Keep movable indicator paint but invalidate stale interactive data.

        Scintilla adjusts indicator positions when text is inserted or deleted.
        The Python records in ``by_line`` do not move with it, so they must not
        drive a tooltip or a quick fix until a fresh merged snapshot is painted.
        This method deliberately leaves indicator and gutter marker IDs intact.
        """
        self.by_line.clear()
        QToolTip.hideText()
```


**Implementation:** add this method before `RuffDiagnosticView.clear` in `ruff_implementation/ruff_diagnostics_view.py`. Keep it inside its named class where applicable. No old method is deleted.


### 4.2. `ruff_implementation/ruff_lsp_controller.py`


#### Imports and declarations outside methods


**Import/declaration addition 1:** insert immediately after `from ruff_implementation.ruff_lsp_client import RuffLspClient` (original line 21).


```python

from code_inteligence.qt_helpers import require_qt
```


**Implementation:** insert once at module/class indentation exactly as shown.


#### 4.2.1 Existing method/function `RuffLspController._on_text_changed`

Advance the document revision while retaining Scintilla indicator paint. Discard the old Python hover cache and any open quick-fix menu, because those records do not move with edited text.


**Old version — original lines 164–181:**


```python
    def _on_text_changed(self):
        """Advance document version and schedule one debounced didChange."""
        if self._closed:
            return
        
        # Each text state must have a stricly newer version that the last.
        self.document_version = next(_VERSIONS)
        self._clear_problem_rows()
        self.document_changed.emit(self.snapshot())
        # Normally MainWindow starts Ruff before editors are made. This fallback
        # makes the controller safe if a tab is created during server startup.
        if not self._opened:
            self.open_document()
        
        if self._opened:
            # Calling start() again on s single-shot timer resets its countdown.
            # One change is sent only after typing has been idle for 180 ms.
            self.change_timer.start()
```


**New version:**


```python
    def _on_text_changed(self):
        """Queue fresh analysis without erasing the last-known underlines.

        Every edit receives a new revision. Existing Scintilla indicators stay
        visible while the asynchronous servers catch up; cached hover records
        and open quick-fix menus are discarded because their positions are old.
        Version checks in the response and action handlers remain mandatory.
        """
        if self._closed:
            return
        
        # Each text state must have a stricly newer version that the last.
        self.document_version = next(_VERSIONS)
        # Scintilla moves existing indicators with the edited text. Keep that
        # last-known paint, but invalidate old hover positions and quick fixes.
        self.view.mark_pending()
        self._close_quick_fix_menu()
        self.document_changed.emit(self.snapshot())
        # Normally MainWindow starts Ruff before editors are made. This fallback
        # makes the controller safe if a tab is created during server startup.
        if not self._opened:
            self.open_document()
        
        if self._opened:
            # Calling start() again on s single-shot timer resets its countdown.
            # One change is sent only after typing has been idle for 180 ms.
            self.change_timer.start()
```


**Implementation:** inside `ruff_implementation/ruff_lsp_controller.py`, replace only `RuffLspController._on_text_changed`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 4.2.2 Existing method/function `RuffLspController._to_diagnostic`

Translate one Ruff result into the existing editor record format. The replacement below includes the updated declaration and explanatory comments.


**Old version — original lines 231–253:**


```python
    def _to_diagnostic(self, raw: dict) -> RuffDiagnostic:
        """Translate one Ruff result into the existing editor record format.

        Clamp line numbers to the live buffer and preserve the original LSP
        payload. Severity mapping is explicit because LSP numbers are reversed.
        """
        span = raw.get("range") or {}
        start = span.get("start") or {}
        end = span.get("end") or start
        last_line = max(0, self.editor.lines() - 1)
        first = min(last_line, max(0, int(start.get("line", 0))))
        last = min(last_line, max(first, int(end.get("line", first))))
        levels = {1: RuffSeverity.ERROR, 2: RuffSeverity.WARNING,
                  3: RuffSeverity.INFO, 4: RuffSeverity.INFO}
        return RuffDiagnostic(
            code=str(raw.get("code", "Ruff")),
            message=str(raw.get("message", "Ruff diagnostic")),
            severity=levels.get(raw.get("severity"), RuffSeverity.WARNING),
            start=RuffPosition(first, self._lsp_column_to_character(first, start.get("character", 0))),
            end=RuffPosition(last, self._lsp_column_to_character(last, end.get("character", 0))),
            revision=self.document_version,
            raw=raw,
        )
```


**New version:**


```python
    def _to_diagnostic(self, raw: dict) -> RuffDiagnostic:
        """Translate one Ruff result into the existing editor record format.

        Clamp line numbers to the live buffer and preserve the original LSP
        payload. Severity mapping is explicit because LSP numbers are reversed.
        """
        span = raw.get("range") or {}
        start = span.get("start") or {}
        end = span.get("end") or start
        last_line = max(0, self.editor.lines() - 1)
        first = min(last_line, max(0, int(start.get("line", 0))))
        last = min(last_line, max(first, int(end.get("line", first))))
        levels = {1: RuffSeverity.ERROR, 2: RuffSeverity.WARNING,
                  3: RuffSeverity.INFO, 4: RuffSeverity.INFO}
        return RuffDiagnostic(
            code=str(raw.get("code", "Ruff")),
            message=str(raw.get("message", "Ruff diagnostic")),
            severity=levels.get(raw.get("severity", 2), RuffSeverity.WARNING),
            start=RuffPosition(first, self._lsp_column_to_character(first, start.get("character", 0))),
            end=RuffPosition(last, self._lsp_column_to_character(last, end.get("character", 0))),
            revision=self.document_version,
            raw=raw,
        )
```


**Implementation:** inside `ruff_implementation/ruff_lsp_controller.py`, replace only `RuffLspController._to_diagnostic`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 4.2.3 Existing method/function `RuffLspController.context_menu`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 295–344:**


```python
    def context_menu(self, event, view=None) -> bool:
        """Show native editing commands plus Ruff quick fixes for the clicked line.

        Args:
            event: Temporary QContextMenuEvent; used synchronously, never captured.
            view: View receiving the click, or the controller's own editor.

        Returns:
            True when this method displays the menu. False lets PythonEditor's
            existing documentation/default-menu behavior handle the click.

        Only current Ruff records can request Ruff actions. Type and spelling
        diagnostics may share the same line but are never sent to Ruff as input.
        """
        target = self.editor if view is None else view
        if self._closed or not self.client.is_ready or not self._opened:
            return False
        byte_position = target.SendScintilla(2022, event.pos().x(), event.pos().y())
        if byte_position < 0:
            return False
        line = target.SendScintilla(target.SCI_LINEFROMPOSITION, byte_position)
        diagnostics = [item for item in self.view.by_line.get(line, [])
                       if item.provider == "ruff"
                       and item.revision == self.document_version
                       and isinstance(item.raw.get("range"), dict)]
        if not diagnostics:
            return False

        self._close_quick_fix_menu()
        generation = self._quick_fix_generation
        client = self.client
        # Copy the position before returning; the Qt event will not stay alive.
        global_position = event.globalPos()
        menu = target.createStandardContextMenu()
        self._quick_fix_menu = menu
        menu.aboutToHide.connect(partial(self._forget_quick_fix_menu, menu))
        menu.addSeparator()
        fixes = menu.addMenu("Ruff quick fixes")
        groups = []
        for diagnostic in diagnostics:
            group = fixes.addMenu(f"{diagnostic.code}: {diagnostic.message[:80]}")
            group.addAction("Loading fixes…").setEnabled(False)
            groups.append((diagnostic, group))
        menu.popup(global_position)
        for diagnostic, group in groups:
            self.request_quick_fixes(
                diagnostic,
                partial(self._populate_quick_fixes, menu, group, generation, client),
            )
        return True
```


**New version:**


```python
    def context_menu(self, event, view=None) -> bool:
        """Show native editing commands plus Ruff quick fixes for the clicked line.

        Args:
            event: Temporary QContextMenuEvent; used synchronously, never captured.
            view: View receiving the click, or the controller's own editor.

        Returns:
            True when this method displays the menu. False lets PythonEditor's
            existing documentation/default-menu behavior handle the click.

        Only current Ruff records can request Ruff actions. Type and spelling
        diagnostics may share the same line but are never sent to Ruff as input.
        """
        target = self.editor if view is None else view
        if self._closed or not self.client.is_ready or not self._opened:
            return False
        byte_position = target.SendScintilla(2022, event.pos().x(), event.pos().y())
        if byte_position < 0:
            return False
        line = target.SendScintilla(target.SCI_LINEFROMPOSITION, byte_position)
        diagnostics = [item for item in self.view.by_line.get(line, [])
                       if item.provider == "ruff"
                       and item.revision == self.document_version
                       and isinstance(item.raw.get("range"), dict)]
        if not diagnostics:
            return False

        self._close_quick_fix_menu()
        generation = self._quick_fix_generation
        client = self.client
        # Copy the position before returning; the Qt event will not stay alive.
        global_position = event.globalPos()
        menu = require_qt(target.createStandardContextMenu())
        self._quick_fix_menu = menu
        menu.aboutToHide.connect(partial(self._forget_quick_fix_menu, menu))
        menu.addSeparator()
        fixes = require_qt(menu.addMenu("Ruff quick fixes"))
        groups = []
        for diagnostic in diagnostics:
            group = require_qt(fixes.addMenu(f"{diagnostic.code}: {diagnostic.message[:80]}"))
            require_qt(group.addAction("Loading fixes…")).setEnabled(False)
            groups.append((diagnostic, group))
        menu.popup(global_position)
        for diagnostic, group in groups:
            self.request_quick_fixes(
                diagnostic,
                partial(self._populate_quick_fixes, menu, group, generation, client),
            )
        return True
```


**Implementation:** inside `ruff_implementation/ruff_lsp_controller.py`, replace only `RuffLspController.context_menu`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


#### 4.2.4 Existing method/function `RuffLspController._populate_quick_fixes`

Required Qt return values are checked before use. This narrows `T | None` to `T` without disabling optional-member diagnostics. An unexpected missing object raises a visible error instead of producing a later attribute failure.


**Old version — original lines 387–427:**


```python
    def _populate_quick_fixes(self, menu, group, generation, client,
                              actions, error, uri, revision) -> None:
        """Replace one loading submenu with validated, explicit user choices.

        This callback runs later on the GUI thread. Check menu identity before
        touching any Qt submenu that could already have been deleted. Unsupported
        command/resolve forms are displayed disabled instead of partly executed.
        """
        if (self._closed or self._quick_fix_menu is not menu
                or sip.isdeleted(menu) or sip.isdeleted(group)
                or generation != self._quick_fix_generation
                or client is not self.client or not client.is_ready
                or self.uri != uri or self.document_version != revision):
            return
        group.clear()
        if error:
            message = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            group.addAction("Ruff request failed: " + message).setEnabled(False)
            return
        if not actions:
            group.addAction("No Ruff quick fix available").setEnabled(False)
            return
        for action in actions:
            if not isinstance(action, dict):
                continue
            title = str(action.get("title", "Ruff action"))
            reason = None
            disabled = action.get("disabled")
            if disabled is not None:
                reason = disabled.get("reason", "Disabled by Ruff") if isinstance(disabled, dict) else str(disabled)
            elif action.get("command") is not None or not isinstance(action.get("edit"), dict):
                reason = "Requires a command or resolve step not supported by this editor"
            entry = group.addAction(title if reason is None else f"{title} — {reason}")
            if reason is not None:
                entry.setEnabled(False)
            else:
                # partial binds this loop's action; a late-binding lambda would
                # make every menu item apply the final action in the list.
                entry.triggered.connect(partial(
                    self._activate_quick_fix, action, uri, revision, client, generation
                ))
```


**New version:**


```python
    def _populate_quick_fixes(self, menu, group, generation, client,
                              actions, error, uri, revision) -> None:
        """Replace one loading submenu with validated, explicit user choices.

        This callback runs later on the GUI thread. Check menu identity before
        touching any Qt submenu that could already have been deleted. Unsupported
        command/resolve forms are displayed disabled instead of partly executed.
        """
        if (self._closed or self._quick_fix_menu is not menu
                or sip.isdeleted(menu) or sip.isdeleted(group)
                or generation != self._quick_fix_generation
                or client is not self.client or not client.is_ready
                or self.uri != uri or self.document_version != revision):
            return
        group.clear()
        if error:
            message = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            require_qt(group.addAction("Ruff request failed: " + message)).setEnabled(False)
            return
        if not actions:
            require_qt(group.addAction("No Ruff quick fix available")).setEnabled(False)
            return
        for action in actions:
            if not isinstance(action, dict):
                continue
            title = str(action.get("title", "Ruff action"))
            reason = None
            disabled = action.get("disabled")
            if disabled is not None:
                reason = disabled.get("reason", "Disabled by Ruff") if isinstance(disabled, dict) else str(disabled)
            elif action.get("command") is not None or not isinstance(action.get("edit"), dict):
                reason = "Requires a command or resolve step not supported by this editor"
            entry = require_qt(group.addAction(title if reason is None else f"{title} — {reason}"))
            if reason is not None:
                entry.setEnabled(False)
            else:
                # partial binds this loop's action; a late-binding lambda would
                # make every menu item apply the final action in the list.
                entry.triggered.connect(partial(
                    self._activate_quick_fix, action, uri, revision, client, generation
                ))
```


**Implementation:** inside `ruff_implementation/ruff_lsp_controller.py`, replace only `RuffLspController._populate_quick_fixes`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### Implement and check Topic 4


Finish Topics 2 and 3 first: `MainWindow._render_all_diagnostics` and `TypeDiagnostics.update` are part of this behavior. Add `mark_pending` before `RuffDiagnosticView.clear`; replace the controller methods shown above. Keep `_clear_problem_rows` for closing, loading and rebinding documents. Do not globally remove it or remove response/action version checks. `apply_code_action` is retained, not deleted or replaced.


Open a document with a real diagnostic and insert text above it. Existing underlines should remain and move with the text. Pending old diagnostics must not offer a quick fix; fresh results restore interactive records. Correct the error and pause: the next accepted merged snapshot removes its underline. The existing 180 ms Ruff and 228 ms basedpyright debounce intervals remain; continuous typing can defer fresh analysis. This guide preserves useful paint during that interval instead of falsely presenting stale findings as current.


## Topic 5 — Suppress background Git console creation on Windows


### Explanation and documentation


The repository has a 15-second Git refresh timer, matching the reported rhythm. Its status/history workers launch Git subprocesses without console-suppression flags. Ruff and basedpyright already use persistent QProcess connections; typing is not supposed to relaunch those servers. The code establishes a plausible source of periodic Windows console creation, but the process behind your visible windows was not captured here, so it is not a confirmed visual diagnosis.


Use `subprocess.CREATE_NO_WINDOW` on the two background Git launch boundaries. `getattr(..., 0)` leaves other operating systems unchanged. Do not suppress the user-facing integrated terminal or Explorer launches.


Documentation: [Python CREATE_NO_WINDOW](https://docs.python.org/3/library/subprocess.html#subprocess.CREATE_NO_WINDOW), [QProcess](https://doc.qt.io/archives/qt-5.15/qprocess.html).


### 5.1. `python_editor/git_integration.py`


#### 5.1.1 Existing method/function `GitStatusChecker._git`

Pass CREATE_NO_WINDOW to the background Git subprocess on Windows. Other platforms receive zero flags. The command remains an argument list with no shell, and existing output capture, timeout and cancellation behavior is retained.


**Old version — original lines 40–53:**


```python
    def _git(self, *args, binary=False):
        """Run a git command in repo_path. Returns stdout or None."""
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=not binary,
            encoding=None if binary else "utf-8",
            errors=None if binary else "replace",
            timeout=5,
        )
        if result.returncode != 0:
            return None
        return result.stdout
```


**New version:**


```python
    def _git(self, *args, binary=False):
        """Run a git command in repo_path. Returns stdout or None."""
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=not binary,
            encoding=None if binary else "utf-8",
            errors=None if binary else "replace",
            timeout=5,
            # Windows GUI launches must not create a console for background Git.
            # On other platforms this constant is absent and the flags stay zero.
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode != 0:
            return None
        return result.stdout
```


**Implementation:** inside `python_editor/git_integration.py`, replace only `GitStatusChecker._git`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### 5.2. `git_implementation/git_service.py`


#### 5.2.1 Existing method/function `GitHistoryWorker._run`

Pass CREATE_NO_WINDOW to the background Git subprocess on Windows. Other platforms receive zero flags. The command remains an argument list with no shell, and existing output capture, timeout and cancellation behavior is retained.


**Old version — original lines 80–136:**


```python
    def _run(
        self,
        cwd: Path,
        *arguments: str,
    ) -> subprocess.CompletedProcess[str]:
        """Run Git with a timeout that remains responsive to cancellation.

        ``subprocess.run()`` cannot observe ``requestInterruption()`` while it
        waits. Short ``communicate()`` timeouts let shutdown terminate a Git
        child before Qt destroys the worker thread.
        """
        command = ["git", *arguments]
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 15

        while True:
            if self.isInterruptionRequested():
                process.terminate()
                try:
                    process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                raise InterruptedError("Git history refresh was cancelled")

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.kill()
                stdout, stderr = process.communicate()
                raise subprocess.TimeoutExpired(
                    command,
                    15,
                    output=stdout,
                    stderr=stderr,
                )

            try:
                stdout, stderr = process.communicate(
                    timeout=min(0.1, remaining)
                )
            except subprocess.TimeoutExpired:
                continue

            return subprocess.CompletedProcess(
                command,
                process.returncode,
                stdout,
                stderr,
            )
```


**New version:**


```python
    def _run(
        self,
        cwd: Path,
        *arguments: str,
    ) -> subprocess.CompletedProcess[str]:
        """Run Git with a timeout that remains responsive to cancellation.

        ``subprocess.run()`` cannot observe ``requestInterruption()`` while it
        waits. Short ``communicate()`` timeouts let shutdown terminate a Git
        child before Qt destroys the worker thread.
        """
        command = ["git", *arguments]
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # Windows GUI launches must not create a console for background Git.
            # On other platforms this constant is absent and the flags stay zero.
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        deadline = time.monotonic() + 15

        while True:
            if self.isInterruptionRequested():
                process.terminate()
                try:
                    process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                raise InterruptedError("Git history refresh was cancelled")

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.kill()
                stdout, stderr = process.communicate()
                raise subprocess.TimeoutExpired(
                    command,
                    15,
                    output=stdout,
                    stderr=stderr,
                )

            try:
                stdout, stderr = process.communicate(
                    timeout=min(0.1, remaining)
                )
            except subprocess.TimeoutExpired:
                continue

            return subprocess.CompletedProcess(
                command,
                process.returncode,
                stdout,
                stderr,
            )
```


**Implementation:** inside `git_implementation/git_service.py`, replace only `GitHistoryWorker._run`, including its displayed decorators and docstring. Keep the indentation shown. Stop before the following sibling method; do not replace its enclosing class or the whole file.


### Implement and check Topic 5


No new files/folders and no deletions. Replace only the two displayed methods. Start `python main.py`, open a Git project and leave it open for at least three refresh intervals. Git status/history should continue updating without a background console being created by these launches. The launch arguments were tested here; the visible Windows behavior still requires this check on your machine. An existing EXE will need to be rebuilt from the corrected source before it contains these changes.


## Verification results and remaining limits


The local test run used Linux/Python 3.12 with PyQt5 5.15.11, QScintilla 2.14.1, basedpyright 1.40.1, Ruff 0.16.7 and Cython 3.2.9. The type checker targeted Python 3.14. This is not a native Windows/Python 3.14.4 execution. The basedpyright integration test used the installed system Node to run that exact server package; your normal application launcher remains the Python console entry point.


**59 tests passed; 4 asset-existence cases were deselected.** The text-only GitHub working copy used for this audit did not contain the required icon binaries. The selected existing suite contributed 32 passing checks; 27 focused checks covered delimiter combinations, the exact screenshot source, both real lexer paths, Qt factories/enums/flags, the model-method conflict, click/slot behavior, split LSP frames, failed initialization, live basedpyright diagnostics, a live Ruff 0.16.7 server retaining its process across document changes, retained indicator paint, revision-safe merging, and the Git launch flags. The Cython extension was compiled successfully with GCC.


The project-wide basedpyright comparison went from **767 errors / 5,624 warnings** to **124 errors / 4 warnings**. Some of that reduction is the explicit switch from recommended to standard checking, so it must not be presented as thousands of repaired runtime bugs. The final report is still not clean. Remaining categories include Qt override/signature mismatches, optional token access in the Markdown lexer, optional terminal/window objects, worker request narrowing and platform-specific imports. Those are not silently disabled or claimed fixed here.


The following remaining counts come from that final static report. They are unresolved findings, not a list of tested runtime failures:


| File | Remaining errors |
|---|---:|

| `code_inteligence/clickable_label.py` | 1 |

| `code_inteligence/command_palette.py` | 1 |

| `code_inteligence/definition_finder.py` | 2 |

| `code_inteligence/documentation_popup.py` | 2 |

| `code_inteligence/hover_helper.py` | 3 |

| `code_inteligence/multi_tab_view.py` | 2 |

| `code_inteligence/references_finder.py` | 1 |

| `code_inteligence/signature_helper.py` | 2 |

| `con_term/terminal_widget.py` | 13 |

| `cozy/cat_controller.py` | 1 |

| `cozy/neko.py` | 2 |

| `cozy/overlays.py` | 3 |

| `cozy/power_mode.py` | 11 |

| `git_ui/commit_graph.py` | 6 |

| `main.py` | 12 |

| `markdown_editor/markdowncustomlexer.py` | 36 |

| `markdown_editor/markdowneditor.py` | 1 |

| `markdowneditor_assets/paths.py` | 1 |

| `python_editor/pythoneditor.py` | 7 |

| `side_bar_widgets/file_manager.py` | 7 |

| `side_bar_widgets/fuzzy_searcher.py` | 1 |

| `tests/test_release_contract.py` | 1 |

| `tests/test_terminal_widget.py` | 3 |

| `title_bar.py` | 5 |


No blanket “all errors fixed” or “no new bugs possible” guarantee is justified by these tests. The demonstrated lexer/LSP/retention fixes have evidence; a complete Windows smoke test and cleanup of the remaining project-wide type findings are still outstanding. No GitHub commit or push was made.

