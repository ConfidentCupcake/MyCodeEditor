# MarkdownEditor: finish type diagnostics, retain Ruff quick fixes, add English/German spelling

This guide starts from your [updated repository](https://github.com/ConfidentCupcake/MarkdownEditor/tree/9380350959dbbc16440c927c7ee511a6d1abdec5), including the controller changes you have already implemented. OLD blocks below come from that version, not the earlier revision used in the previous guide. Follow the steps once; skip a step if your code already matches NEW.

The previous guide omitted your existing **`request_quick_fixes` and `apply_code_action`** path. Keep those methods and `workspace_edit.py`. The current `context_menu` returns `False`, and `_render_all_diagnostics` loses the raw Ruff payload when constructing display records. Both connections are completed here. The method is named `request_quick_fixes` in the repository; there is no separate `quick_fixes` method to delete or rename.

Your attached controller matches the repository's controller except that **the attachment lacks the `WorkspaceEditApplier` / `WorkspaceEditError` import already present on GitHub**. The quick-fix topic explicitly covers that difference.

Implement **Topic 1 first**, then **Topic 2** for Ruff actions and **Topic 3** for bilingual spelling. Topics 2 and 3 are independent after Topic 1. Type setup, the shared store, snapshots and several MainWindow hooks already exist, so this guide does not tell you to recreate them. Each changed method has OLD, NEW, the exact placement and a change explanation. Full-file code is used only for a genuinely new file. Paths are relative to the repository root. Keep decorators with their methods and retain the shown indentation.

## Topic 1 — Complete the existing diagnostics integration

### Topic explanation

Basedpyright supplies semantic analysis: unresolved names/members, incompatible types and unsafe optional-member access. Ruff continues to supply syntax/lint findings. The common store allows both sets of findings to remain visible at once.

Your repository already has `DocumentSnapshot`, the correctly named `Diagnostic.revision` field, controller lifecycle signals, a Problems store, `TypeDiagnostics`, its dependency/configuration, startup, restart and shutdown hooks. The type-client file is **`ruff_implementation/type_diagnostic.py` (singular)**. Retain that name and its existing MainWindow import.

The remaining failures are specific: `attach` reads a controller flag without its leading underscore; `_settings` contains misspelled keys and a trailing comma that returns a tuple; `_initialize` sends `inizialize`; `_initialized` calls `self.settings()` and can continue after an error; `_read_stdout` lowercases header keys but looks up `Content-Length`; the timeout calls `self.error.emot`. The new-tab attach block in MainWindow is commented out. These steps correct those methods rather than replacing the whole client.

The renderer also needs byte-position support already assumed by `_open_problem`, and must retain raw Ruff metadata for the following quick-fix topic. A provider field keeps Ruff actions separate from basedpyright and spelling findings.

Documentation:

- [Basedpyright configuration](https://docs.basedpyright.com/latest/configuration/config-files/) and [language-server settings](https://docs.basedpyright.com/latest/configuration/language-server-settings/) — valid configuration names, rule severities and interpreter selection.
- [Basedpyright installation](https://docs.basedpyright.com/latest/installation/command-line-and-language-server/) — install in the selected interpreter.
- [LSP initialization and transport](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) — method names, Content-Length and document versions.
- [Scintilla indicators and positions](https://www.scintilla.org/ScintillaDoc.html#Indicators) — UTF-8 byte coordinates for highlighting/navigation.
- [Ruff and type checkers](https://docs.astral.sh/ruff/faq/) — complementary analyses.

### Topic code and implementation — file by file

### Existing file: `ruff_implementation/type_diagnostic.py`

**Folder:** `ruff_implementation` already exists.

#### Step 1: Change `TypeDiagnostics.attach`

**Why:** Use the attachment flag that RuffLspController actually defines.

**OLD — the existing method:**

```python
    def attach(self, controller: RuffLspController) -> None:
        """
        Subscribe once to a controller's source and close notifications.
        
        Initial analysis is explicitly queued because its first buffer load may 
        have happened before this service or its signals connections existed.
        """
        if controller.type_diagnostics_attached:
            return
        controller.type_diagnostics_attached = True
        controller.document_changed.connect(self.update)
        controller.document_closed.connect(self.close_document)
        self.update(controller.snapshot())
```

**NEW — use this in place of the old code above:**

```python
    def attach(self, controller: RuffLspController) -> None:
        """Subscribe once to a controller's source and close notifications.

        Initial analysis is explicitly queued because its first buffer load may
        have happened before this service or its signal connections existed.
        """
        if controller._type_diagnostics_attached:
            return
        controller._type_diagnostics_attached = True
        controller.document_changed.connect(self.update)
        controller.document_closed.connect(self.close_document)
        self.update(controller.snapshot())
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `attach`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `update` method and its decorators.

**What changed:** Change type_diagnostics_attached to _type_diagnostics_attached in both accesses. Keep initial snapshot submission and lifecycle connections.

#### Step 2: Change `TypeDiagnostics._settings`

**Why:** Send a dictionary containing supported setting names.

**OLD — the existing method:**

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

**NEW — use this in place of the old code above:**

```python
    def _settings(self) -> dict:
        """Return server settings with semantic errors enabled by default.

        Project basedpyright configuration can refine these defaults. Python's
        interpreter path is separate from analysis settings because the server
        uses it to resolve installed packages and their type information.
        """
        return {
            "python": {"pythonPath": self.python},
            "basedpyright": {
                "disableOrganizeImports": True,
                "analysis": {
                    "diagnosticMode": "openFilesOnly",
                    "typeCheckingMode": "recommended",
                    "diagnosticSeverityOverrides": {
                        "reportUndefinedVariable": "error",
                        "reportAttributeAccessIssue": "error",
                        "reportOptionalMemberAccess": "error",
                    },
                },
            },
        }
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_settings`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_initialize` method and its decorators.

**What changed:** Correct disableOrganizedImports → disableOrganizeImports, typedCheckingMode → typeCheckingMode, diagnosticSevereityOverrides → diagnosticSeverityOverrides, and reportUndefinedOverrides → reportUndefinedVariable. Remove the trailing comma after the returned dictionary so the result is not a one-item tuple.

#### Step 3: Change `TypeDiagnostics._initialize`

**Why:** Use the exact LSP handshake method and capability key.

**OLD — the existing method:**

```python
    def _initialize(self) -> None:
        """
        Advertise precisely the protocol features implemented by this client.
        
        UTF-16 is requested deliberately and converted at the boundary. Config
        requests are supported; dynamic regristration and editing are not.
        """
        self._request("inizialize", {
            "processId": None,
            "rootUri": self.root.as_uri(),
            "workspaceFolders": [{"uri": self.root.as_uri(), "name": self.root.name}],
            "capabilities": {
                "general": {"positionEncodings": ["utf-16"]},
                "workspace": {"configuration": True, "workspaceFolders": True},
                "textDocument": {
                    "synchronization": {"dynamicRegristration": False, "didSave": False},
                    "publishDiagnostics": {"versionSupport": True, "relatedInformation": True},
                },
            },
        }, self._initialized)
```

**NEW — use this in place of the old code above:**

```python
    def _initialize(self) -> None:
        """Advertise precisely the protocol features implemented by this client.

        UTF-16 is requested deliberately and converted at the boundary. Config
        requests are supported; dynamic registrations and editing are not.
        """
        self._request("initialize", {
            "processId": None,
            "rootUri": self.root.as_uri(),
            "workspaceFolders": [{"uri": self.root.as_uri(), "name": self.root.name}],
            "capabilities": {
                "general": {"positionEncodings": ["utf-16"]},
                "workspace": {"configuration": True, "workspaceFolders": True},
                "textDocument": {
                    "synchronization": {"dynamicRegistration": False, "didSave": False},
                    "publishDiagnostics": {"versionSupport": True, "relatedInformation": True},
                },
            },
        }, self._initialized)
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_initialize`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_initialized` method and its decorators.

**What changed:** Change inizialize to initialize and dynamicRegristration to dynamicRegistration. Keep UTF-16 negotiation and versioned diagnostics.

#### Step 4: Change `TypeDiagnostics._initialized`

**Why:** Finish initialization only on success and call the correct settings method.

**OLD — the existing method:**

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
        self._notify("workspace/didChangeConfiguration", {"settings": self.settings()})
        self._flush()
```

**NEW — use this in place of the old code above:**

```python
    def _initialized(self, result, error) -> None:
        """Complete the handshake, configure analysis, then send current buffers.

        No didOpen is sent before initialized. A failed handshake kills this
        process and reports why instead of silently leaving analysis disabled.
        """
        if self._closing or self._restart_requested:
            self.process.kill()
            return
        if error:
            self.error.emit(f"basedpyright initialization failed: {error}")
            self.process.kill()
            return
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

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_initialized`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_request` method and its decorators.

**What changed:** Return immediately after initialization failure. Use self._settings(), not self.settings(). Preserve the closing/restart guard and flush current snapshots only after initialization.

#### Step 5: Change `TypeDiagnostics._read_stdout`

**Why:** Match the normalized protocol header name.

**OLD — the existing method:**

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

**NEW — use this in place of the old code above:**

```python
    def _read_stdout(self) -> None:
        """Reassemble partial or concatenated Content-Length protocol messages.

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

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_read_stdout`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_route` method and its decorators.

**What changed:** After lowercasing headers, retrieve fields["content-length"]. Keep partial-frame buffering, the size bound and protocol-error handling.

#### Step 6: Change `TypeDiagnostics._initialization_timeout`

**Why:** Report a stalled server without raising an AttributeError.

**OLD — the existing method:**

```python
    def _initialization_timeout(self) -> None:

        self.error.emot("basedpyright initialization timed out; check the selected interpreter.")
        self.process.kill()
```

**NEW — use this in place of the old code above:**

```python
    def _initialization_timeout(self) -> None:
        """Abort a server that never completed initialization within the deadline.

        A stalled handshake must not leave the UI implying that live analysis
        is working. The error explains why no semantic findings are arriving.
        """
        self.error.emit("basedpyright initialization timed out; check the selected interpreter.")
        self.process.kill()
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_initialization_timeout`, including any decorator shown in OLD. Keep four-space class indentation. Stop at the end of this method; retain the class and other methods.

**What changed:** Change self.error.emot to self.error.emit, then kill the stalled process. The new docstring explains the visible failure state.

#### Step 7: Change `TypeDiagnostics.restart`

**Why:** Document the lifecycle method already implemented in this file.

**OLD — the existing method:**

```python
    def restart(self) -> None:

        if self._closing:
            return
        self.manager.clear_provider("basedpyright")
        if not self.is_running():
            self.start()
            return
        self._restart_requested = True
        self._stop()
```

**NEW — use this in place of the old code above:**

```python
    def restart(self) -> None:
        """Request a clean server replacement while keeping current buffers.

        This public action also recovers from a failed installation/startup.
        The new process begins only after the previous process has exited.
        """

        if self._closing:
            return
        self.manager.clear_provider("basedpyright")
        if not self.is_running():
            self.start()
            return
        self._restart_requested = True
        self._stop()
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `restart`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_stop` method and its decorators.

**What changed:** Documentation only: the executable body is retained. The docstring explains its shutdown/restart responsibility and how callers must keep Qt objects alive.

#### Step 8: Change `TypeDiagnostics._stop`

**Why:** Document the lifecycle method already implemented in this file.

**OLD — the existing method:**

```python
    def _stop(self) -> None:

        self._deadline.stop()
        self._debounce.stop()
        if self._ready:
            self._request("shutdown", None, self._shutdown_reply)
        else:
            self.process.kill()
        self._ready = False
        self._kill_timer.start(2000)
```

**NEW — use this in place of the old code above:**

```python
    def _stop(self) -> None:
        """Attempt orderly shutdown and enforce a two-second process deadline.

        The owned kill timer is stopped when the old process exits, preventing
        a delayed timeout from accidentally killing a replacement process.
        """

        self._deadline.stop()
        self._debounce.stop()
        if self._ready:
            self._request("shutdown", None, self._shutdown_reply)
        else:
            self.process.kill()
        self._ready = False
        self._kill_timer.start(2000)
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_stop`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_shutdown_reply` method and its decorators.

**What changed:** Documentation only: the executable body is retained. The docstring explains its shutdown/restart responsibility and how callers must keep Qt objects alive.

#### Step 9: Change `TypeDiagnostics._shutdown_reply`

**Why:** Document the lifecycle method already implemented in this file.

**OLD — the existing method:**

```python
    def _shutdown_reply(self, result, error) -> None:

        if error:
            self.process.kill()
        else:
            self._notify("exit", None)
```

**NEW — use this in place of the old code above:**

```python
    def _shutdown_reply(self, result, error) -> None:
        """Finish LSP shutdown after the server acknowledges the request.

        A protocol error triggers immediate process termination; otherwise exit
        tells the server that it may release its resources and finish normally.
        """

        if error:
            self.process.kill()
        else:
            self._notify("exit", None)
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_shutdown_reply`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `shutdown` method and its decorators.

**What changed:** Documentation only: the executable body is retained. The docstring explains its shutdown/restart responsibility and how callers must keep Qt objects alive.

#### Step 10: Change `TypeDiagnostics.shutdown`

**Why:** Document the lifecycle method already implemented in this file.

**OLD — the existing method:**

```python
    def shutdown(self) -> None:
        self._closing = True
        self._restart_requested = False
        self._debounce.stop()
        if self.is_running():
            self._stop()
```

**NEW — use this in place of the old code above:**

```python
    def shutdown(self) -> None:
        """Stop permanently when MainWindow begins asynchronous application exit.

        No later restart or document update is accepted. MainWindow must keep
        this QObject alive until is_running returns False.
        """
        self._closing = True
        self._restart_requested = False
        self._debounce.stop()
        if self.is_running():
            self._stop()
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `shutdown`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `is_running` method and its decorators.

**What changed:** Documentation only: the executable body is retained. The docstring explains its shutdown/restart responsibility and how callers must keep Qt objects alive.

#### Step 11: Change `TypeDiagnostics.is_running`

**Why:** Document the lifecycle method already implemented in this file.

**OLD — the existing method:**

```python
    def is_running(self) -> bool:

        return self.process.state() != QProcess.NotRunning
```

**NEW — use this in place of the old code above:**

```python
    def is_running(self) -> bool:
        """Report process activity without blocking the application close loop.

        Starting counts as active too; destroying a starting QProcess would
        interrupt startup while its operating-system process is being created.
        """

        return self.process.state() != QProcess.NotRunning
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `is_running`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_finished` method and its decorators.

**What changed:** Documentation only: the executable body is retained. The docstring explains its shutdown/restart responsibility and how callers must keep Qt objects alive.

#### Step 12: Change `TypeDiagnostics._finished`

**Why:** Document the lifecycle method already implemented in this file.

**OLD — the existing method:**

```python
    def _finished(self, exit_code: int, exit_status) -> None:

        self._ready = False
        self._deadline.stop()
        self._kill_timer.stop()
        self._sent.clear()
        self._pending.clear()
        self._buffer.clear()
        self.manager.clear_provider("basedpyright")
        if self._restart_requested and not self._closing:
            self._restart_requested = False
            QTimer.singleShot(0, self.start)
        elif not self._closing:
            self.error.emit(f"basedpyright stopped: ({exit_code}). {self._stderr_tail[-1500:]}")
```

**NEW — use this in place of the old code above:**

```python
    def _finished(self, exit_code: int, exit_status) -> None:
        """Clear server-owned state and perform a requested restart once.

        Unexpected exits leave a visible error. Automatic endless restart loops
        would obscure missing packages or invalid interpreter configuration.
        """

        self._ready = False
        self._deadline.stop()
        self._kill_timer.stop()
        self._sent.clear()
        self._pending.clear()
        self._buffer.clear()
        self.manager.clear_provider("basedpyright")
        if self._restart_requested and not self._closing:
            self._restart_requested = False
            QTimer.singleShot(0, self.start)
        elif not self._closing:
            self.error.emit(f"basedpyright stopped: ({exit_code}). {self._stderr_tail[-1500:]}")
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_finished`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_read_stderr` method and its decorators.

**What changed:** Documentation only: the executable body is retained. The docstring explains its shutdown/restart responsibility and how callers must keep Qt objects alive.

#### Step 13: Change `TypeDiagnostics._read_stderr`

**Why:** Document the lifecycle method already implemented in this file.

**OLD — the existing method:**

```python
    def _read_stderr(self) -> None:

        self._stderr_tail = (self._stderr_tail + bytes(
            self.process.readAllStandardError()).decode("utf8", errors="replace"))[-4000:]
```

**NEW — use this in place of the old code above:**

```python
    def _read_stderr(self) -> None:
        """Retain bounded process logs separately from JSON-RPC stdout.

        Import errors from the bootstrap appear here. Keeping the final portion
        gives the user an actionable failure message without unbounded storage.
        """

        self._stderr_tail = (self._stderr_tail + bytes(
            self.process.readAllStandardError()).decode("utf8", errors="replace"))[-4000:]
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_read_stderr`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_process_error` method and its decorators.

**What changed:** Documentation only: the executable body is retained. The docstring explains its shutdown/restart responsibility and how callers must keep Qt objects alive.

#### Step 14: Change `TypeDiagnostics._process_error`

**Why:** Document the lifecycle method already implemented in this file.

**OLD — the existing method:**

```python
    def _process_error(self, error) -> None:

        if error == QProcess.FailedToStart:
            self._deadline.stop()
        if not self._closing:
            self.error.emit("basedpyright process error:" + self.process.errorString())
```

**NEW — use this in place of the old code above:**

```python
    def _process_error(self, error) -> None:
        """Expose launch/runtime failure independently of source diagnostics.

        FailedToStart may not emit finished, so stop the initialization timer
        explicitly. The Restart type analysis action allows recovery later.
        """

        if error == QProcess.FailedToStart:
            self._deadline.stop()
        if not self._closing:
            self.error.emit("basedpyright process error:" + self.process.errorString())
```

**Where and how to apply:** In `ruff_implementation/type_diagnostic.py`, replace only `_process_error`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_initialization_timeout` method and its decorators.

**What changed:** Documentation only: the executable body is retained. The docstring explains its shutdown/restart responsibility and how callers must keep Qt objects alive.

**Keep in `ruff_implementation/type_diagnostic.py`:** `__init__`, `update`, `start`, `_request`, `_notify`, `_send`, `_route`, `_flush`, `_position`, `_publish`, `close_document`, `reconfigure`. Their existing implementation remains. In particular, retain the current debounce interval and the consistently used _SERVER_BOOSTSTRAP constant; its spelling is not the cause of a startup failure.

### Existing file: `ruff_implementation/ruff_diagnostics_model.py`

**Folder:** `ruff_implementation` already exists.

#### Step 15: Add provider identity to RuffDiagnostic

**Why:** Distinguish fixable Ruff input from other providers after display adaptation.

**OLD — the exact existing block:**

```python
@dataclass(frozen=True)
class RuffDiagnostic:
    """
    Complete diagnostic state for new visualisation and quick fixes.
    
    revision is the editor document revision that produced this result.
    It prevents old diagnostics and olf fixes from changing newer source text.
    """
    code: str
    message: str
    severity: RuffSeverity
    start: RuffPosition
    end: RuffPosition
    revision: int
    fix: RuffFix | None = None
    raw: dict[str, Any] = field(default_factory=dict, compare=False)
```

**NEW — use this in place of the old code above:**

```python
@dataclass(frozen=True)
class RuffDiagnostic:
    """
    Complete diagnostic state for new visualisation and quick fixes.
    
    revision is the editor document revision that produced this result.
    It prevents old diagnostics and old fixes from changing newer source text.
    raw preserves the provider's original diagnostic for code-action requests.
    provider identifies which service owns the record; other providers must not
    have their findings submitted to Ruff's code-action endpoint.
    """
    code: str
    message: str
    severity: RuffSeverity
    start: RuffPosition
    end: RuffPosition
    revision: int
    fix: RuffFix | None = None
    raw: dict[str, Any] = field(default_factory=dict, compare=False)
    # Appended with a default to preserve all existing positional construction.
    # Ruff-produced records are Ruff by default; the shared renderer sets others.
    provider: str = "ruff"
```

**Where and how to apply:** Replace only the RuffDiagnostic dataclass, including @dataclass(frozen=True), at the bottom of this file.

**What changed:** Append provider="ruff" after raw, preserving existing constructor positions. The generic Diagnostic already has provider_data; no change to diagnostic_model.py is needed.

### Existing file: `ruff_implementation/ruff_diagnostics_view.py`

**Folder:** `ruff_implementation` already exists.

#### Step 16: Change `RuffDiagnosticView.clear`

**Why:** Clear diagnostic ranges using the buffer’s actual byte length.

**OLD — the existing method:**

```python
    def clear(self):
        """Remoce only Ruff visual state across the current document."""
        lines = self.editor.lines()
        if lines:
            end = self.editor.lineLength(lines - 1)
            for indicator in (self.ERROR_INDICATOR, self.WARNING_INDICATOR, self.INFO_INDICATOR, self.FIX_INDICATOR):
                self.editor.clearIndicatorRange(0, 0, lines - 1, end, indicator)
                
        for marker in (self.ERROR_MARKER, self.WARNING_MARKER, self.INFO_MARKER, self.FIX_MARKER):
            self.editor.markerDeleteAll(marker)
        self.by_line = {}
```

**NEW — use this in place of the old code above:**

```python
    def clear(self) -> None:
        """Remove only diagnostic-owned decorations and cached hover records.

        Scintilla's byte-oriented clearing covers the entire UTF-8 buffer.
        Search selections, lexer styles and unrelated marker IDs remain intact.
        """
        length = self.editor.SendScintilla(QsciScintilla.SCI_GETLENGTH)
        for number in (20, 21, 22, 23):
            self.editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, number)
            self.editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, length)
            self.editor.markerDeleteAll(number)
        self.by_line.clear()
```

**Where and how to apply:** In `ruff_implementation/ruff_diagnostics_view.py`, replace only `clear`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `render` method and its decorators.

**What changed:** Use Scintilla’s byte-oriented clearing for IDs 20–23, then clear the hover map. Other visual IDs remain untouched.

#### Step 17: Add `RuffDiagnosticView._byte_position`

**Why:** MainWindow._open_problem already calls this missing method.

**OLD:** This method does not exist. There is no old method to replace.

**NEW — method to add:**

```python
    def _byte_position(self, line: int, column: int) -> int:
        """Convert a Python-character column to an absolute Scintilla byte offset.

        Encoding only the line prefix gives the correct offset after German
        umlauts or emoji. The document uses UTF-8 through PythonEditor.setUtf8.
        """
        value = self.editor.text(line).rstrip("\r\n")
        prefix = value[:max(0, min(column, len(value)))].encode("utf-8")
        return self.editor.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, line) + len(prefix)
```

**Where and how to apply:** In `ruff_implementation/ruff_diagnostics_view.py`, inside `RuffDiagnosticView`, insert this method immediately after `clear`, before the next method. Keep the shown four-space indentation. Do not put it inside `clear`.

**What the new method does:** Convert a bounded Python-character column to an absolute UTF-8 byte offset. The same helper is used for drawing and navigation.

#### Step 18: Change `RuffDiagnosticView.render`

**Why:** Paint a merged snapshot at the correct positions without losing existing fix markers.

**OLD — the existing method:**

```python
    def render(self, diagnostics: list[RuffDiagnostic]):
        """Paint exact source ranges and cache diagnostics for hover/context menus."""
        self.clear()
        for diagnostic in diagnostics:
            if diagnostic.start.line < 0 or diagnostic.start.line >= self.editor.lines():
                continue
            # Ruff zero-length ranges still need a visible one-character span.
            end_line = max(diagnostic.end.line, diagnostic.start.line)
            end_column = diagnostic.end.column
            if end_line == diagnostic.start.line and end_column <= diagnostic.start.column:
                end_column = min(diagnostic.start.column + 1, self.editor.lineLength(diagnostic.start.line))
            indicator = {RuffSeverity.ERROR: self.ERROR_INDICATOR, RuffSeverity.WARNING: self.WARNING_INDICATOR, RuffSeverity.INFO: self.INFO_INDICATOR}[diagnostic.severity]
            marker = {RuffSeverity.ERROR: self.ERROR_MARKER, RuffSeverity.WARNING: self.WARNING_MARKER, RuffSeverity.INFO: self.INFO_MARKER}[diagnostic.severity]
            self.editor.fillIndicatorRange(diagnostic.start.line, diagnostic.start.column, end_line, end_column, indicator)
            self.editor.markerAdd(diagnostic.start.line, marker)
            if diagnostic.fix:
                self.editor.markerAdd(diagnostic.start.line, self.FIX_MARKER)
            self.by_line.setdefault(diagnostic.start.line, []).append(diagnostic)
```

**NEW — use this in place of the old code above:**

```python
    def render(self, diagnostics: list[RuffDiagnostic]) -> None:
        """Paint one complete merged snapshot and cache all findings for hover.

        The caller filters by source revision. Clearing once here is safe only
        because the supplied list includes every provider, not merely the latest
        server response. Empty ranges receive a neighboring character when possible.
        """
        self.clear()
        for item in diagnostics:
            if not 0 <= item.start.line < self.editor.lines():
                continue
            end_line = min(self.editor.lines() - 1, max(item.start.line, item.end.line))
            start = self._byte_position(item.start.line, item.start.column)
            end = self._byte_position(end_line, item.end.column)
            if end <= start:
                line_text = self.editor.text(item.start.line).rstrip("\r\n")
                if item.start.column < len(line_text):
                    end = self._byte_position(item.start.line, item.start.column + 1)
                elif item.start.column > 0:
                    start = self._byte_position(item.start.line, item.start.column - 1)
                    end = self._byte_position(item.start.line, item.start.column)
            number = {RuffSeverity.ERROR: 20, RuffSeverity.WARNING: 21, RuffSeverity.INFO: 22}[item.severity]
            if end > start:
                self.editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, number)
                self.editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start, end - start)
            self.editor.markerAdd(item.start.line, number)
            if item.fix is not None:
                self.editor.markerAdd(item.start.line, self.FIX_MARKER)
            for line in range(item.start.line, end_line + 1):
                self.by_line.setdefault(line, []).append(item)
```

**Where and how to apply:** In `ruff_implementation/ruff_diagnostics_view.py`, replace only `render`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `at_line` method and its decorators.

**What changed:** Use _byte_position and byte ranges, cache multiline findings, and retain the existing FIX_MARKER behavior when an original Ruff record contains a fix.

#### Step 19: Change `RuffDiagnosticView.tooltip`

**Why:** Keep tooltip claims consistent until Ruff’s server has answered an action request.

**OLD — the existing method:**

```python
    def tooltip(self, diagnostic: RuffDiagnostic) -> str:
        """Build a new Ruff-only hover card; no Jedi pyflakes content."""
        fix_line = "\nQuick fix available: right-click the diagnostic." if diagnostic.fix else ""
        return f"{diagnostic.code} - {diagnostic.message}{fix_line}"
```

**NEW — use this in place of the old code above:**

```python
    def tooltip(self, diagnostic: RuffDiagnostic) -> str:
        """Show provider/rule and message without claiming an unrequested fix exists.

        All providers use this renderer. Actual Ruff action availability is
        queried when the quick-fix menu is opened, not inferred from severity.
        """
        return f"{diagnostic.code}\n{diagnostic.message}"
```

**Where and how to apply:** In `ruff_implementation/ruff_diagnostics_view.py`, replace only `tooltip`, including any decorator shown in OLD. Keep four-space class indentation. Stop at the end of this method; retain the class and other methods.

**What changed:** Remove the unconditional pre-existing fix advertisement. Topic 2 adds a conditional invitation to request Ruff actions, including the possibility of no available fix.

**Keep in `ruff_implementation/ruff_diagnostics_view.py`:** `__init__`, `_define_visuals`, `at_line`. Keep the existing palette, reserved IDs and compatibility helper.

### Existing file: `main.py`

**Folder:** repository root.

#### Step 20: Change `MainWindow._render_all_diagnostics`

**Why:** Retain the original Ruff diagnostic needed by request_quick_fixes.

**OLD — the existing method:**

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
                start = row.source_range.start
                end = row.source_range.end
                display.append(RuffDiagnostic(
                    code=f"{row.provider}: {row.code}",
                    message=row.message,
                    severity=RuffSeverity(int(row.severity)),
                    start=RuffPosition(start.line, start.column),
                    end=RuffPosition(end.line, end.column),
                    revision=controller.document_version,
                ))
            controller.view.render(display)
```

**NEW — use this in place of the old code above:**

```python
    def _render_all_diagnostics(self, rows: list[Diagnostic]) -> None:
        """Merge providers for drawing without discarding Ruff action metadata.

        Args:
            rows: Complete snapshot from DiagnosticsManager.changed.

        Retain the original RuffDiagnostic.raw payload and provider identity.
        Ruff's code-action endpoint needs its original diagnostic, including
        provider-specific data that cannot be recreated from a displayed label.
        Other providers keep separate ownership and cannot enter Ruff's fix flow.
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

**Where and how to apply:** In `main.py`, replace only `_render_all_diagnostics`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_on_analysis_error` method and its decorators.

**What changed:** Copy raw and fix from row.provider_data when it is a RuffDiagnostic, and set provider on every display record. Continue filtering by URI/revision. _publish_problems already retains the original object; keep it.

#### Step 21: Change `MainWindow._connect_editor`

**Why:** Attach tabs created after TypeDiagnostics starts.

**OLD — the existing method:**

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
            #if hasattr(self, "type_diagnostics"):
            #   self.type_diagnostics.attach(editor.ruff_lsp)
        if hasattr(self, "diagnostics_manager"):
            self._bind_diagnostic_editor(editor)
```

**NEW — use this in place of the old code above:**

```python
    def _connect_editor(self, editor):
        """Connect UI signals, bind the shared store and attach type analysis.

        Early tabs are bound later by the installers when services are created.
        Later Python tabs must explicitly attach here; otherwise basedpyright
        never receives their document snapshots. Non-Python tabs are skipped.
        """
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

**Where and how to apply:** In `main.py`, replace only `_connect_editor`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_cat_unbox` method and its decorators.

**What changed:** Delete the commented-out attach lines and add a live guarded attach after manager binding. Retain the existing UI connections and early-tab initialization behavior.

**Keep in `main.py`:** `_install_problems`, `_bind_diagnostic_editor`, `_publish_problems`, `_open_problem`, `_on_ruff_diagnostics`, `_install_type_diagnostics`. These are already installed. Keep the existing __init__ installer calls, type_diagnostic import, _restart_ruff reconfiguration, closeEvent shutdown and _background_work_running condition; do not duplicate them.

### Finish Topic 1

Your `pyproject.toml` already includes basedpyright and `[tool.basedpyright]`; do not add either twice. Install the existing project dependencies in the application environment if you have not done so:

```bash
python -m pip install -e .
```

In a different selected project interpreter, install `basedpyright>=1.39.9,<2` there as well. Restart the editor after these changes. Semantic findings now have a functioning server startup and later-tab attachment, and shared findings retain their provider metadata. Keep `document_snapshot.py`, `diagnostic_model.py`, `diagnostics_manager.py`, `problems_panel.py` and `ruff_lsp_client.py` as they are. Delete no files. The next topic connects the Ruff action UI; spelling remains optional.

## Topic 2 — Preserve and connect Ruff quick fixes

### Topic explanation

Keep **request_quick_fixes**, **apply_code_action** and **WorkspaceEditApplier.apply**. They are different parts of one flow:

| Method | Responsibility |
| --- | --- |
| `PythonEditor.contextMenuEvent` | Routes the click to `controller.context_menu(event, self)` before documentation handling. |
| `RuffLspController.context_menu` | Opens the native editing menu and adds Ruff quick-fix submenus for current Ruff findings on the clicked line. |
| `request_quick_fixes` | Flushes current source, sends the original raw diagnostic to `textDocument/codeAction`, and rejects stale replies. |
| `_populate_quick_fixes` | Fills the open submenu after the asynchronous response arrives. |
| `_activate_quick_fix` | Rechecks the document/server identity when the user selects an action. |
| `apply_code_action` | Accepts a supported direct edit and delegates complete validation/application. |
| `WorkspaceEditApplier.apply` | Validates the full single-document edit and applies it as one undo group. |

The click event is temporary. The menu stores a copied position and request identity, not the event. Editing, renaming, closing or replacing the server invalidates pending actions. The menu contains ordinary editing commands too. Dismissing it does not prevent the selected QAction from firing; that ordering matters in Qt.

Only Ruff records are sent to Ruff. Basedpyright and spelling underlines remain visible but do not acquire unrelated Ruff fixes. Not every Ruff diagnostic has an action. Ruff may offer manually selected unsafe fixes, so the menu does not describe every returned action as safe. Review the action title before selecting it.

This preserves the repository's intended **direct, single-document edit** scope. Command-only actions, unresolved actions, annotated edits, resource operations and multi-file edits are not partially applied. Unsupported menu forms are disabled; unsupported edit payloads produce a clear error. There is no blanket automatic correction of spelling or undefined methods.

Documentation:

- [Ruff code actions and fix safety](https://docs.astral.sh/ruff/editors/features/#code-actions).
- [LSP CodeAction and WorkspaceEdit](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) — raw diagnostic context, disabled actions, edit/command forms and document changes.
- [Qt QMenu popup and lifecycle](https://doc.qt.io/qt-6/qmenu.html#popup) — the popup/aboutToHide pattern; the implementation uses the PyQt5 APIs already in the repository.
- [Scintilla targets](https://www.scintilla.org/ScintillaDoc.html#SCI_REPLACETARGET) and [undo grouping](https://www.scintilla.org/ScintillaDoc.html#SCI_BEGINUNDOACTION) — byte-oriented edits and a single undo operation.

### Topic code and implementation — file by file

### Existing file: `ruff_implementation/workspace_edit.py`

**Folder:** `ruff_implementation` already exists.

#### Step 22: Change `WorkspaceEditApplier._position`

**Why:** Correct a missing raise and use exact UTF-8 offsets for edits.

**OLD — the existing method:**

```python
    def _position(self, point):
        """Reject out-of-range postitions and split UTF-8/UTF-16 characters."""
        editor = self.controller.editor
        if not isinstance(point, dict):
            raise WorkspaceEditError("Malformed position")
        
        line, column = point.get("line"), point.get("character")
        if type(line) is not int or type(column) is not int or not 0 <= line < editor.lines() or column < 0:
            raise WorkspaceEditError("Position is outside the document")
        
        text = editor.text(line).rstrip("\r\n")
        encoding = self.controller.client.position_encoding
        codec = {"utf-8": "utf-8", "utf-16": "utf-16-le", "utf-32": "utf-32-le"}.get(encoding)
        if codec is None:
            WorkspaceEditError("Unsuported position encoding")
        
        raw = text.encode(codec)
        width = {"utf-8": 1, "utf-16": 2, "utf-32": 4}[encoding]
        stop = column * width
        if stop > len(raw):
            raise WorkspaceEditError("Column is outside the line")
        
        try:
            prefix = raw[:stop].decode(codec)
        except UnicodeError as error:
            raise WorkspaceEditError("Position splits a Unicode character") from error
        return editor.positionFromLineIndex(line, len(prefix))
```

**NEW — use this in place of the old code above:**

```python
    def _position(self, point) -> int:
        """Validate an LSP point and convert it to an absolute UTF-8 byte offset.

        Reject malformed fields, positions past a line, and boundaries inside
        a UTF-8 sequence or UTF-16 surrogate pair. The controller's negotiated
        encoding determines units; Scintilla's document storage remains UTF-8.
        """
        editor = self.controller.editor
        if not isinstance(point, dict):
            raise WorkspaceEditError("Malformed position")
        line, column = point.get("line"), point.get("character")
        if (type(line) is not int or type(column) is not int
                or not 0 <= line < editor.lines() or column < 0):
            raise WorkspaceEditError("Position is outside the document")
        text = editor.text(line).rstrip("\r\n")
        encoding = self.controller.client.position_encoding
        codec = {"utf-8": "utf-8", "utf-16": "utf-16-le", "utf-32": "utf-32-le"}.get(encoding)
        if codec is None:
            raise WorkspaceEditError("Unsupported position encoding")
        width = {"utf-8": 1, "utf-16": 2, "utf-32": 4}[encoding]
        raw = text.encode(codec)
        stop = column * width
        if stop > len(raw):
            raise WorkspaceEditError("Column is outside the line")
        try:
            prefix = raw[:stop].decode(codec)
        except UnicodeError as error:
            raise WorkspaceEditError("Position splits a Unicode character") from error
        return editor.SendScintilla(editor.SCI_POSITIONFROMLINE, line) + len(prefix.encode("utf-8"))
```

**Where and how to apply:** In `ruff_implementation/workspace_edit.py`, replace only `_position`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `apply` method and its decorators.

**What changed:** Actually raise WorkspaceEditError for unsupported encodings, keep strict Unicode-boundary checks and compute the byte offset directly from the line prefix.

#### Step 23: Change `WorkspaceEditApplier.apply`

**Why:** Validate every edit before mutation and reject unsupported payloads completely.

**OLD — the existing method:**

```python
    def apply(self, payload, uri, version):
        """Validate identity, version, ranges, annotations and overlap before mutation."""
        owner = self.controller
        editor = owner.editor
        if owner._closed or owner.uri != uri or owner.document_version != version:
            raise WorkspaceEditError("Document changed after this action was requested")
        if editor.isReadOnly() or not isinstance(payload, dict):
            raise WorkspaceEditError("Document is ready-only or edit is malformed")
        if payload.get("changeAnnotations"):
            raise WorkspaceEditError("Annotated edits require a separate approval UI")
        if "changes" in payload and "documentChanges" in payload:
            raise WorkspaceEditError("Ambiguous workspace edit")
        if "changes" in payload:
            changes = payload["changes"]
            if not isinstance(changes, dict) or set(changes) != {uri}:
                raise WorkspaceEditError("Only complete single-document edits are supported")
            raw_edits = changes[uri]
        
        else:
            entries = payload.get("documentChanges")
            if not isinstance(entries, list) or len(entries) != 1:
                raise WorkspaceEditError("Only one text-document change is supported")
            entry = entries[0]
            if not isinstance(entry, dict) or "kind" in entry:
                raise WorkspaceEditError("File creation, rename and deletions are not supported")
            document = entry.get("textDocument", {})
            if document.get("uri") != uri or document.get("version") not in (None, version):
                raise WorkspaceEditError("Action refers to another document or revision")
            raw_edits = entry.get("edits")
        
        if not isinstance(raw_edits, list):
            raise WorkspaceEditError("Malformed edit list")
        
        edits = []
        for raw in raw_edits:
            if not isinstance(raw, dict) or not isinstance(raw.get("newText"), str) or "annotaionId" in raw:
                raise WorkspaceEditError("Malformed or annotated text edit")
            value = raw.get("range", {})
            start, end = self._position(value.get("start")), self._position(value.get("end"))
            if end < start:
                raise WorkspaceEditError("Reversed edit range")
            edits.append(EditorTextEdit(start, end, raw["newText"]))
        edits.sort(key=lambda item: (item.start, item.end))
        
        previous = None
        for edit in edits:
            if previous is not None and (edit.start < previous.end or edit.start == previous.start):
                raise WorkspaceEditError("Overlapping or ambiguous edits")
            previous = edit
        
        # All checks happen first; demanding byte positions survive later replacements.
        editor.beginUndoAction()
        try:
            for edit in reversed(edits):
                first = editor.lineIndexFromPosition(edit.start)
                last = editor.lineIndexFromPosition(edit.end)
                editor.setSelection(*first, *last)
                editor.replaceSelectedText(edit.text)
        finally:
            editor.endUndoAction()
```

**NEW — use this in place of the old code above:**

```python
    def apply(self, payload, uri, version) -> None:
        """Apply a validated single-document WorkspaceEdit as one undo operation.

        Args:
            payload: WorkspaceEdit containing changes or one textDocument change.
            uri: URI captured when the user requested the action.
            version: Captured editor revision; different live text is rejected.

        Validate every entry, Unicode boundary, annotation and overlap before
        the first mutation. Only direct edits to this open document are supported;
        resource operations and cross-file actions are rejected in their entirety.
        Apply in descending byte order so earlier positions remain valid.
        """
        owner = self.controller
        editor = owner.editor
        if owner._closed or owner.uri != uri or owner.document_version != version:
            raise WorkspaceEditError("Document changed after this action was requested")
        if editor.isReadOnly() or not isinstance(payload, dict):
            raise WorkspaceEditError("Document is read-only or edit is malformed")
        if payload.get("changeAnnotations"):
            raise WorkspaceEditError("Annotated edits are not supported")
        if "changes" in payload and "documentChanges" in payload:
            raise WorkspaceEditError("Ambiguous workspace edit")
        if "changes" in payload:
            changes = payload["changes"]
            if not isinstance(changes, dict) or set(changes) != {uri}:
                raise WorkspaceEditError("Only complete single-document edits are supported")
            raw_edits = changes[uri]
        else:
            entries = payload.get("documentChanges")
            if not isinstance(entries, list) or len(entries) != 1:
                raise WorkspaceEditError("Only one text-document change is supported")
            entry = entries[0]
            if not isinstance(entry, dict) or "kind" in entry:
                raise WorkspaceEditError("File creation, rename and deletion are not supported")
            document = entry.get("textDocument")
            if not isinstance(document, dict) or document.get("uri") != uri:
                raise WorkspaceEditError("Action refers to another or malformed document")
            requested_version = document.get("version")
            if requested_version is not None and (type(requested_version) is not int or requested_version != version):
                raise WorkspaceEditError("Action refers to another revision")
            raw_edits = entry.get("edits")
        if not isinstance(raw_edits, list):
            raise WorkspaceEditError("Malformed edit list")
        edits = []
        for raw in raw_edits:
            if (not isinstance(raw, dict) or not isinstance(raw.get("newText"), str)
                    or "annotationId" in raw):
                raise WorkspaceEditError("Malformed or annotated text edit")
            value = raw.get("range")
            if not isinstance(value, dict):
                raise WorkspaceEditError("Malformed edit range")
            start, end = self._position(value.get("start")), self._position(value.get("end"))
            if end < start:
                raise WorkspaceEditError("Reversed edit range")
            try:
                raw["newText"].encode("utf-8")
            except UnicodeError as error:
                raise WorkspaceEditError("Replacement contains invalid Unicode") from error
            edits.append(EditorTextEdit(start, end, raw["newText"]))
        edits.sort(key=lambda item: (item.start, item.end))
        previous = None
        for edit in edits:
            if previous is not None and (edit.start < previous.end or edit.start == previous.start):
                raise WorkspaceEditError("Overlapping or ambiguous edits")
            previous = edit
        if not edits:
            return
        editor.beginUndoAction()
        try:
            for edit in reversed(edits):
                replacement = edit.text.encode("utf-8")
                # Byte targets avoid mixing LSP units with QScintilla selections.
                editor.SendScintilla(editor.SCI_SETTARGETSTART, edit.start)
                editor.SendScintilla(editor.SCI_SETTARGETEND, edit.end)
                editor.SendScintilla(editor.SCI_REPLACETARGET, len(replacement), replacement)
        finally:
            editor.endUndoAction()
```

**Where and how to apply:** In `ruff_implementation/workspace_edit.py`, replace only `apply`, including any decorator shown in OLD. Keep four-space class indentation. Stop at the end of this method; retain the class and other methods.

**What changed:** Correct annotaionId to annotationId; validate nested document/range objects and replacement Unicode; reject overlaps and stale versions. Apply descending byte targets inside one undo group. Keep WorkspaceEditError, EditorTextEdit and the existing constructor.

### Existing file: `ruff_implementation/ruff_lsp_controller.py`

**Folder:** `ruff_implementation` already exists.

**Attachment difference:** GitHub already contains the following import. Your uploaded controller does not. If editing that attached copy directly, insert this line after the PyQt imports, before the other ruff_implementation imports. Do not add it twice if you are editing the repository version:

```python
from ruff_implementation.workspace_edit import WorkspaceEditApplier, WorkspaceEditError
```

#### Step 24: Add menu callback and widget-lifetime imports

**Why:** Bind each asynchronous callback to its own menu/action without late-binding loop variables.

**OLD — the exact existing block:**

```python
from itertools import count
```

**NEW — use this in place of the old code above:**

```python
from itertools import count
from functools import partial
```

**Where and how to apply:** At the module import section, directly after the count import. Replace only this shown block; keep all surrounding code.

**What changed:** Add functools.partial; keep existing imports.

#### Step 25: Import PyQt object-lifetime checks

**Why:** Late server replies must not touch a Qt menu whose native widget was deleted.

**OLD — the exact existing block:**

```python
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
```

**NEW — use this in place of the old code above:**

```python
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5 import sip
```

**Where and how to apply:** At the Qt imports. Replace only this shown block; keep all surrounding code.

**What changed:** sip.isdeleted checks the native Qt object before accessing a retained Python wrapper.

#### Step 26: Add the message-box import

**Why:** A rejected edit must be reported without escaping a Qt callback.

**OLD — the exact existing block:**

```python
from PyQt5.QtWidgets import QToolTip
```

**NEW — use this in place of the old code above:**

```python
from PyQt5.QtWidgets import QToolTip, QMessageBox
```

**Where and how to apply:** Replace this one QtWidgets import line.

**What changed:** Keep QToolTip and add QMessageBox.

#### Step 27: Change `RuffLspController.__init__`

**Why:** Initialize popup ownership alongside the existing diagnostic state.

**OLD — the existing method:**

```python
    def __init__(self, editor: PythonEditor, client: RuffLspClient, parent=None):
        # Parent this controller to the editor unless a different explicit parent was supplied.
        # Destroying the tab then also destroys its controller.
        super().__init__(parent or editor)

        self.editor = editor
        self.client = client
        self.diagnostics_manager: DiagnosticsManager | None = None
        self._uri = self._uri_for_path(editor.full_path)
        
        # Reuse the existing visual layer. It remains responsible only for QScintilla
        # indicators, marker circles, tooltips and range caching.
        self.view = RuffDiagnosticView(editor)
        
        # LSP versions begin at an integer and must increase for every didChange.
        self.document_version = next(_VERSIONS)
        
        # didOpen must be sent exactly once per URI/server lifecycle.
        self._opened = False
        self._closed = False

        self._type_diagnostics_attached = False
        self._spelling_attached = False
        self._warned_versionless = False
        
        # Full-buffer updates are delayed slightly while a user is typing.
        # This prevents sending one didChange messafe for every individual keypress.
        self.change_timer = QTimer(self)
        self.change_timer.setSingleShot(True)
        self.change_timer.setInterval(180)
        self.change_timer.timeout.connect(self._send_change)
        
        # QScintilla emits textChanged for user input, pasted text, fixes, etc.
        editor.textChanged.connect(self._on_text_changed)
        
        # If Ruff is still starting when this tab is constructed, open_document
        # wil run as soon as initialize/initialized completes.
        client.server_ready.connect(self.open_document)
        client.server_stopped.connect(self._on_server_stopped)

        client.diagnostics_published.connect(self._on_diagnostics_published)
        if client.is_ready:
            self.open_document()
```

**NEW — use this in place of the old code above:**

```python
    def __init__(self, editor: PythonEditor, client: RuffLspClient, parent=None):
        """Connect the document to Ruff and initialize diagnostic/action state.

        The manager is injected after MainWindow creates it. A retained popup
        and monotonically changing generation tie asynchronous quick-fix replies
        to one menu; document lifecycle hooks invalidate obsolete actions.
        """
        # Parent this controller to the editor unless a different explicit parent was supplied.
        # Destroying the tab then also destroys its controller.
        super().__init__(parent or editor)

        self.editor = editor
        self.client = client
        self.diagnostics_manager: DiagnosticsManager | None = None
        self._uri = self._uri_for_path(editor.full_path)
        
        # Reuse the existing visual layer. It remains responsible only for QScintilla
        # indicators, marker circles, tooltips and range caching.
        self.view = RuffDiagnosticView(editor)
        
        # LSP versions begin at an integer and must increase for every didChange.
        self.document_version = next(_VERSIONS)
        
        # didOpen must be sent exactly once per URI/server lifecycle.
        self._opened = False
        self._closed = False

        self._type_diagnostics_attached = False
        self._spelling_attached = False
        self._warned_versionless = False
        # Own the asynchronous popup and invalidate obsolete reply callbacks.
        self._quick_fix_menu = None
        self._quick_fix_generation = 0
        
        # Full-buffer updates are delayed slightly while a user is typing.
        # This prevents sending one didChange messafe for every individual keypress.
        self.change_timer = QTimer(self)
        self.change_timer.setSingleShot(True)
        self.change_timer.setInterval(180)
        self.change_timer.timeout.connect(self._send_change)
        
        # QScintilla emits textChanged for user input, pasted text, fixes, etc.
        editor.textChanged.connect(self._on_text_changed)
        
        # If Ruff is still starting when this tab is constructed, open_document
        # wil run as soon as initialize/initialized completes.
        client.server_ready.connect(self.open_document)
        client.server_stopped.connect(self._on_server_stopped)

        client.diagnostics_published.connect(self._on_diagnostics_published)
        if client.is_ready:
            self.open_document()
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `__init__`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `uri` method and its decorators.

**What changed:** Add _quick_fix_menu and _quick_fix_generation only; retain the snapshot signals, typed manager, revision counter and all current Ruff connections.

#### Step 28: Change `RuffLspController.snapshot`

**Why:** Document the existing shared-diagnostics boundary.

**OLD — the existing method:**

```python
    def snapshot(self):
        path = Path(self.editor.full_path).resolve() if self.editor.full_path else None
        return DocumentSnapshot(self.uri, path, self.editor.text(), self.document_version)
```

**NEW — use this in place of the old code above:**

```python
    def snapshot(self) -> DocumentSnapshot:
        """Copy current source on the GUI thread for asynchronous analysis.

        Returns:
            Immutable text, revision, URI and optional real disk path.
            Providers must analyze this text rather than rereading the file.
        """
        path = Path(self.editor.full_path).resolve() if self.editor.full_path else None
        return DocumentSnapshot(self.uri, path, self.editor.text(), self.document_version)
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `snapshot`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `bind_manager` method and its decorators.

**What changed:** Retain the implemented behavior; add detailed documentation and the return annotation for snapshot where needed. Neither method is removed or duplicated.

#### Step 29: Change `RuffLspController.bind_manager`

**Why:** Document the existing shared-diagnostics boundary.

**OLD — the existing method:**

```python
    def bind_manager(self, manager: DiagnosticsManager) -> None:
        self.diagnostics_manager = manager
```

**NEW — use this in place of the old code above:**

```python
    def bind_manager(self, manager: DiagnosticsManager) -> None:
        """Inject the actual diagnostic store after MainWindow creates it.

        A typed reference replaces getattr(window, ...). Type analysis now knows
        which methods exist instead of receiving an unconstrained Any value.
        """
        self.diagnostics_manager = manager
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `bind_manager`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_uri_for_path` method and its decorators.

**What changed:** Retain the implemented behavior; add detailed documentation and the return annotation for snapshot where needed. Neither method is removed or duplicated.

#### Step 30: Add `RuffLspController._close_quick_fix_menu`

**Why:** Invalidate menus when their text/server context changes.

**OLD:** This method does not exist. There is no old method to replace.

**NEW — method to add:**

```python
    def _close_quick_fix_menu(self) -> None:
        """Invalidate pending menu replies/actions and dispose of the old popup.

        Called when text, URI or server identity changes and before opening a
        new popup. Advancing the generation prevents an older asynchronous reply
        from populating a replacement menu that happens to use the same document.
        """
        self._quick_fix_generation += 1
        menu = self._quick_fix_menu
        self._quick_fix_menu = None
        if menu is not None and not sip.isdeleted(menu):
            menu.close()
            menu.deleteLater()
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, inside `RuffLspController`, insert this method immediately after `hover`, before the next method. Keep the shown four-space indentation. Do not put it inside `hover`.

**What the new method does:** Increment the generation, forget the old menu, then close/delete it if its Qt object is still alive.

#### Step 31: Add `RuffLspController._forget_quick_fix_menu`

**Why:** Release normal menu dismissal without cancelling its selected action.

**OLD:** This method does not exist. There is no old method to replace.

**NEW — method to add:**

```python
    def _forget_quick_fix_menu(self, menu) -> None:
        """Release a dismissed popup without invalidating its selected action.

        Qt can hide a menu before emitting QAction.triggered. Do not advance the
        generation here: the selected action still needs its final document and
        server checks. Late request replies are rejected by the menu-identity check.
        """
        if self._quick_fix_menu is menu:
            self._quick_fix_menu = None
        if not sip.isdeleted(menu):
            menu.deleteLater()
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, inside `RuffLspController`, insert this method immediately after `_close_quick_fix_menu`, before the next method. Keep the shown four-space indentation. Do not put it inside `_close_quick_fix_menu`.

**What the new method does:** Clear only the retained menu reference and schedule deletion. Do not advance generation here, because Qt may hide the menu before QAction.triggered.

#### Step 32: Change `RuffLspController.context_menu`

**Why:** Replace the unconditional False placeholder with the actual Ruff menu.

**OLD — the existing method:**

```python
    def context_menu(self, event, view=None) -> bool:
        """Display current Ruff quick fixes without retaining the temporary Qt event."""
        return False
```

**NEW — use this in place of the old code above:**

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

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `context_menu`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `request_quick_fixes` method and its decorators.

**What changed:** Keep the event/view signature used by PythonEditor. Select current Ruff records, preserve native editing commands, request actions asynchronously and return True only when the menu is displayed.

#### Step 33: Change `RuffLspController.request_quick_fixes`

**Why:** Preserve this method and make its provider/lifecycle contract explicit.

**OLD — the existing method:**

```python
    def request_quick_fixes(self, diagnostic, callback):
        """Request action with raw provider data and capture the ecaxt document identity."""
        uri, revision, client = self.uri, self.document_version, self.client
        if self._closed or diagnostic.revision != revision or not client.is_ready:
            callback([], {"message": "Diagnostic is stale"}, uri, revision)
            return
        
        self.change_timer.stop()
        self._send_change()
        
        def receive(result, error):
            """Discard repolies after closure, relocation, editing or server replacement."""
            if self._closed or client is not self.client or self.uri != uri or self.document_version != revision:
                return
            callback(result if isinstance(result, list) else [], error, uri, revision)
        client.request("textDocument/codeAction", {
            "textDocument": {"uri": uri}, "range": diagnostic.raw["range"],
            "context": {"diagnostics": [diagnostic.raw], "only": ["quickfix"], "triggerKind": 1}}, receive)
```

**NEW — use this in place of the old code above:**

```python
    def request_quick_fixes(self, diagnostic, callback) -> None:
        """Request Ruff code actions using the unchanged provider diagnostic.

        Args:
            diagnostic: Current RuffDiagnostic with provider='ruff' and raw LSP data.
            callback: Receives (actions, error, uri, revision). Stale asynchronous
                replies are discarded rather than attached to newer source text.

        Flush the pending buffer before requesting actions so Ruff's ranges refer
        to the same revision. The raw diagnostic contains Ruff-specific fix data;
        rebuilding it from only a displayed message would lose that information.
        """
        uri, revision, client = self.uri, self.document_version, self.client
        if (self._closed or not self._opened or not client.is_ready
                or diagnostic.provider != "ruff" or diagnostic.revision != revision
                or not isinstance(diagnostic.raw, dict)
                or not isinstance(diagnostic.raw.get("range"), dict)):
            callback([], {"message": "Ruff diagnostic is stale or has no action data"}, uri, revision)
            return
        self.change_timer.stop()
        self._send_change()

        def receive(result, error):
            """Forward only replies still owned by this document and server.

            Closing, editing, renaming or replacing the client invalidates this
            request. The popup separately checks its generation and visibility.
            """
            if (self._closed or client is not self.client or not client.is_ready
                    or not self._opened or self.uri != uri
                    or self.document_version != revision):
                return
            callback(result if isinstance(result, list) else [], error, uri, revision)

        client.request("textDocument/codeAction", {
            "textDocument": {"uri": uri},
            "range": diagnostic.raw["range"],
            "context": {"diagnostics": [diagnostic.raw], "only": ["quickfix"], "triggerKind": 1},
        }, receive)
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `request_quick_fixes`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `apply_code_action` method and its decorators.

**What changed:** Validate provider, revision and raw range; flush pending text; send the original raw diagnostic. The nested receive callback discards replies after edits, URI changes, close or client replacement.

#### Step 34: Add `RuffLspController._populate_quick_fixes`

**Why:** Turn the asynchronous response into menu items safely.

**OLD:** This method does not exist. There is no old method to replace.

**NEW — method to add:**

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

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, inside `RuffLspController`, insert this method immediately after `request_quick_fixes`, before the next method. Keep the shown four-space indentation. Do not put it inside `request_quick_fixes`.

**What the new method does:** Check menu identity, Qt lifetime, generation, document and client. Display no-action/error states; disable unsupported forms and bind each supported action to its own callback.

#### Step 35: Add `RuffLspController._activate_quick_fix`

**Why:** Revalidate an action at the moment the user selects it.

**OLD:** This method does not exist. There is no old method to replace.

**NEW — method to add:**

```python
    def _activate_quick_fix(self, action, uri, revision, client, generation, checked=False) -> None:
        """Apply the selected action only if its document/server snapshot is current.

        The checked argument is supplied by QAction.triggered and is unused.
        Recheck after menu dismissal because hide may occur before triggered.
        Validation failures are shown to the user; they never escape a Qt slot.
        """
        if (self._closed or generation != self._quick_fix_generation
                or client is not self.client or not client.is_ready
                or self.uri != uri or self.document_version != revision):
            return
        try:
            self.apply_code_action(action, uri, revision)
        except WorkspaceEditError as error:
            QMessageBox.warning(self.editor, "Ruff quick fix", str(error))
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, inside `RuffLspController`, insert this method immediately after `_populate_quick_fixes`, before the next method. Keep the shown four-space indentation. Do not put it inside `_populate_quick_fixes`.

**What the new method does:** Reject stale document/server/generation state, call apply_code_action and show WorkspaceEditError messages without crashing the event callback.

#### Step 36: Change `RuffLspController.apply_code_action`

**Why:** Keep edit application separate from requesting/menu presentation.

**OLD — the existing method:**

```python
    def apply_code_action(self, action, uri, revision):
        """Apply a direct edit completely or report an unsupported action form."""
        if action.get("disabled") or action.get("command") or not isinstance(action.get("edit"), dict):
            raise WorkspaceEditError("This action needs an unsupported command or resolve step")
        WorkspaceEditApplier(self).apply(action["edit"], uri, revision)
```

**NEW — use this in place of the old code above:**

```python
    def apply_code_action(self, action, uri, revision) -> None:
        """Validate a direct Ruff edit, then delegate its complete application.

        Args:
            action: LSP CodeAction selected explicitly by the user.
            uri: Document identity captured when actions were requested.
            revision: Source version captured with that URI.

        Command-only actions, disabled actions and unresolved actions are rejected.
        WorkspaceEditApplier validates the entire edit before changing the buffer;
        this method does not silently apply only part of a compound action.
        """
        if (self._closed or not self.client.is_ready
                or self.uri != uri or self.document_version != revision):
            raise WorkspaceEditError("Document or Ruff connection changed after the request")
        if (not isinstance(action, dict) or action.get("disabled") is not None
                or action.get("command") is not None
                or not isinstance(action.get("edit"), dict)):
            raise WorkspaceEditError("This action is disabled or requires a command/resolve step")
        WorkspaceEditApplier(self).apply(action["edit"], uri, revision)
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `apply_code_action`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_clear_problem_rows` method and its decorators.

**What changed:** Retain delegation to WorkspaceEditApplier.apply. Add explicit lifecycle and payload checks; reject disabled, command-based and unresolved forms before applying anything.

#### Step 37: Change `RuffLspController._on_server_stopped`

**Why:** Invalidate quick-fix UI when its underlying context is no longer valid.

**OLD — the existing method:**

```python
    def _on_server_stopped(self):
        self._opened = False
        manager = self.diagnostics_manager
        if manager is not None:
            manager.replace("ruff", self.uri, [])
```

**NEW — use this in place of the old code above:**

```python
    def _on_server_stopped(self):
        """Invalidate actions and forget only Ruff results when its process stops.

        Other providers keep their own diagnostics. Closing the action popup also
        prevents a reply from the old process being used after Ruff restarts.
        """
        self._close_quick_fix_menu()
        self._opened = False
        manager = self.diagnostics_manager
        if manager is not None:
            manager.replace("ruff", self.uri, [])
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `_on_server_stopped`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `relocate` method and its decorators.

**What changed:** Add _close_quick_fix_menu before the existing operation. Existing row clearing and signal reconnection remain. _clear_problem_rows is already called on edits, loads, rename and shutdown, so those paths also invalidate actions.

#### Step 38: Change `RuffLspController.set_client`

**Why:** Invalidate quick-fix UI when its underlying context is no longer valid.

**OLD — the existing method:**

```python
    def set_client(self, client):
        """Reconnect this document when the selected Ruff interpreter changes."""
        self.client.server_ready.disconnect(self.open_document)
        self.client.server_stopped.disconnect(self._on_server_stopped)
        self.client.diagnostics_published.disconnect(self._on_diagnostics_published)
        self.client = client
        self._opened = False
        self._warned_versionless = False
        client.server_ready.connect(self.open_document)
        client.server_stopped.connect(self._on_server_stopped)
        client.diagnostics_published.connect(self._on_diagnostics_published)
        if client.is_ready:
            self.open_document()
```

**NEW — use this in place of the old code above:**

```python
    def set_client(self, client):
        """Reconnect this document when the selected Ruff interpreter changes."""
        self._close_quick_fix_menu()
        self.client.server_ready.disconnect(self.open_document)
        self.client.server_stopped.disconnect(self._on_server_stopped)
        self.client.diagnostics_published.disconnect(self._on_diagnostics_published)
        self.client = client
        self._opened = False
        self._warned_versionless = False
        client.server_ready.connect(self.open_document)
        client.server_stopped.connect(self._on_server_stopped)
        client.diagnostics_published.connect(self._on_diagnostics_published)
        if client.is_ready:
            self.open_document()
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `set_client`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `open_document` method and its decorators.

**What changed:** Add _close_quick_fix_menu before the existing operation. Existing row clearing and signal reconnection remain. _clear_problem_rows is already called on edits, loads, rename and shutdown, so those paths also invalidate actions.

#### Step 39: Change `RuffLspController._clear_problem_rows`

**Why:** Invalidate quick-fix UI when its underlying context is no longer valid.

**OLD — the existing method:**

```python
    def _clear_problem_rows(self) -> None:
        """Remove every provider's results when this source version is invalid.

        The local variable has type DiagnosticsManager | None. The guard narrows
        it to DiagnosticsManager, so clear_document is a known, valid method.
        """
        manager = self.diagnostics_manager
        if manager is not None:
            manager.clear_document(self.uri)
```

**NEW — use this in place of the old code above:**

```python
    def _clear_problem_rows(self) -> None:
        """Remove every provider's results when this source version is invalid.

        The local variable has type DiagnosticsManager | None. The guard narrows
        it to DiagnosticsManager, so clear_document is a known, valid method.
        """
        self._close_quick_fix_menu()
        manager = self.diagnostics_manager
        if manager is not None:
            manager.clear_document(self.uri)
```

**Where and how to apply:** In `ruff_implementation/ruff_lsp_controller.py`, replace only `_clear_problem_rows`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `shutdown` method and its decorators.

**What changed:** Add _close_quick_fix_menu before the existing operation. Existing row clearing and signal reconnection remain. _clear_problem_rows is already called on edits, loads, rename and shutdown, so those paths also invalidate actions.

**Keep in `ruff_implementation/ruff_lsp_controller.py`:** `uri`, `_uri_for_path`, `relocate`, `open_document`, `sync_from_editor`, `_on_text_changed`, `_send_change`, `_lsp_column_to_character`, `_on_diagnostics_published`, `_to_diagnostic`, `hover`, `shutdown`. Keep their implemented shared-diagnostics behavior. In particular, do not replace the whole controller with the older guide’s file or delete request_quick_fixes/apply_code_action.

### Existing file: `ruff_implementation/ruff_diagnostics_view.py`

**Folder:** `ruff_implementation` already exists.

#### Step 40: Change `RuffDiagnosticView.tooltip`

**Why:** Make the new menu discoverable on Ruff findings only.

**OLD — the existing method:**

```python
    def tooltip(self, diagnostic: RuffDiagnostic) -> str:
        """Show provider/rule and message without claiming an unrequested fix exists.

        All providers use this renderer. Actual Ruff action availability is
        queried when the quick-fix menu is opened, not inferred from severity.
        """
        return f"{diagnostic.code}\n{diagnostic.message}"
```

**NEW — use this in place of the old code above:**

```python
    def tooltip(self, diagnostic: RuffDiagnostic) -> str:
        """Describe a finding and advertise only the appropriate provider action.

        Ruff's raw diagnostic allows a request, not a guarantee that a fix exists.
        Basedpyright and spelling records get no Ruff action invitation.
        """
        message = f"{diagnostic.code}\n{diagnostic.message}"
        if diagnostic.provider == "ruff" and isinstance(diagnostic.raw.get("range"), dict):
            message += "\nRight-click to request Ruff quick fixes."
        return message
```

**Where and how to apply:** In `ruff_implementation/ruff_diagnostics_view.py`, replace only `tooltip`, including any decorator shown in OLD. Keep four-space class indentation. Stop at the end of this method; retain the class and other methods.

**What changed:** Add a conditional request hint for Ruff records containing a raw range. A request can return no available fixes; the tooltip does not promise a correction.

### Finish Topic 2

Save the changed model/view/controller/edit-applier code and restart the editor. **Keep `PythonEditor.contextMenuEvent` unchanged**: it already passes `(event, self)` to the controller before its documentation popup. Keep `RuffLspClient.request` and its existing code-action capability support. No separate method named `quick_fixes` or new extensions class is needed.

Right-click a current Ruff diagnostic line to open the native editing menu with Ruff quick-fix submenus. Select an available direct action explicitly; valid single-document edits are grouped for one undo. Unavailable fixes and unsupported action forms are stated rather than silently discarded. Type and spelling diagnostics never enter the Ruff request. Delete no files.

## Topic 3 — English and German spelling in identifiers, comments, docstrings and strings

### Topic explanation


This topic uses `pyspellchecker` with **both English and German dictionaries loaded together**. A word recognized by either dictionary is accepted. Checking is entirely local; source text is not sent to a remote spelling service.

Python tokenization identifies names, comments and strings. The worker checks identifier fragments, including `snake_case` and `camelCase`, and preserves the original source offsets. Docstrings are covered because they are string tokens. It checks other strings too, including text that happens to be an API key, path or URL; it does not guess that a string is user-facing prose.

Dictionary checking and semantic checking answer different questions. A consistently used misspelled identifier can be valid Python and still receive a spelling finding. Conversely, a correctly spelled but nonexistent method is detected by basedpyright when its type is known. The source code is never automatically renamed or corrected.

**Spelling findings are errors in this implementation, as requested.** Their wording says “Possible spelling error” because dictionary absence does not prove a mistake. Valid technical terms, names and German compounds may be missing. Add intentional words or whole identifiers to a project file named `.markdowneditor-spelling.txt`. The file supplements both languages; it never suppresses basedpyright's unresolved-name or missing-member errors.

One persistent worker thread loads the dictionaries and checks immutable text. Typing is debounced, queued old versions are replaced, and results are discarded after a source change, dictionary reload, rename or close. Dictionary construction and scanning never read an editor widget from the worker thread.

Practical boundaries are explicit: single-letter symbols and Python keywords/builtins are exempt; a typo that is another valid English or German word cannot be detected by dictionary membership. This is spelling rather than grammar analysis. Incomplete Python tokenization can stop spelling coverage after the last valid token until the next edit completes the source. Ruff/basedpyright remain responsible for syntax findings. Escape sequences in ordinary string tokens are masked without changing offsets; raw strings retain literal backslashes. Python versions expose f-string pieces differently, so interpolation/format text can also produce dictionary findings. Accepted-word entries handle intentional source vocabulary.

Documentation used:

- [pyspellchecker overview](https://pyspellchecker.readthedocs.io/en/latest/) and [SpellChecker API](https://pyspellchecker.readthedocs.io/en/latest/code.html#spellchecker.SpellChecker) — loading multiple dictionaries and checking membership.
- [Python tokenize](https://docs.python.org/3/library/tokenize.html) — token kinds and original line/column positions.
- [Python regular expressions](https://docs.python.org/3/library/re.html) — Unicode words and identifier boundaries.
- [Python condition variables](https://docs.python.org/3/library/threading.html#condition-objects) — a sleeping, replaceable worker queue.
- [Qt 5 QThread](https://doc.qt.io/archives/qt-5.15/qthread.html) and [Qt thread affinity / queued connections](https://doc.qt.io/archives/qt-5.15/qobject.html#thread-affinity) — delivering worker results safely to the GUI.

### Topic code and implementation — file by file

### Existing file: `pyproject.toml`

**Folder:** repository root.

#### Step 41: Add the spelling dependency

**Why:** Spelling runs in the application process with both bundled dictionaries.

**OLD — the exact existing block:**

```toml
    "ruff>=0.12,<1",
```

**NEW — use this in place of the old code above:**

```toml
    "ruff>=0.12,<1",
    "pyspellchecker>=0.9,<1",
```

**Where and how to apply:** Inside the existing [project].dependencies array. Replace only this shown block; keep all surrounding code.

**What changed:** Retain the already installed basedpyright entry and every other dependency.

### New file: `ruff_implementation/spelling_diagnostics.py`

**Folder:** `ruff_implementation` already exists.

#### Step 42: Create `spelling_diagnostics.py`

**Purpose:** Run local English/German dictionary checks on immutable source snapshots without reading editor widgets from a worker.

**OLD:** This file does not exist in the starting repository. No existing code is replaced.

**NEW — contents of the new file:**

```python
"""Local English/German spelling diagnostics for Python source buffers."""

from __future__ import annotations

import builtins
import io
import keyword
import re
import threading
import tokenize
from dataclasses import dataclass
from pathlib import Path

from PyQt5.QtCore import QObject, QThread, QTimer, Qt, pyqtSignal

from ruff_implementation.diagnostic_model import Diagnostic, DiagnosticSeverity, Position, SourceRange
from ruff_implementation.diagnostics_manager import DiagnosticsManager
from ruff_implementation.document_snapshot import DocumentSnapshot
from ruff_implementation.ruff_lsp_controller import RuffLspController

_WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
_CAMEL_BOUNDARY = re.compile(
    r"(?<=[a-zäöüß])(?=[A-ZÄÖÜ])|(?<=[A-ZÄÖÜ])(?=[A-ZÄÖÜ][a-zäöüß])"
)
_STRING_START = re.compile(r'''(?i:[rubf]*)("""|\x27\x27\x27|"|\x27)''')
_ESCAPE = re.compile(r"\\(?:N\{[^}\n]*\}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|x[0-9a-fA-F]{2}|[0-7]{1,3}|[^\n])")
_STANDARD_WORDS = {
    name.lower() for name in dir(builtins)
} | set(keyword.kwlist) | set(keyword.softkwlist) | {"self", "cls", "args", "kwargs"}


@dataclass(frozen=True)
class SpellingJob:
    """Pair an immutable document with the dictionary context used to check it.

    root selects .markdowneditor-spelling.txt. generation changes when the
    workspace or dictionary is reloaded, so matching source versions alone
    cannot accidentally accept results from the previous dictionary context.
    """

    snapshot: DocumentSnapshot
    root: Path
    generation: int


class BilingualSpeller:
    """Find dictionary-unknown word fragments without executing Python source.

    One instance lives entirely in the worker thread. English and German words
    are accepted together. Dictionary absence means a possible spelling error;
    it is not proof that an identifier is an invalid Python reference.
    """

    def __init__(self):
        """Load both bundled dictionaries once, outside the GUI thread.

        Importing here also turns a missing optional package into a worker error
        instead of preventing the editor's other diagnostic providers starting.
        """
        from spellchecker import SpellChecker
        self.dictionary = SpellChecker(language=["en", "de"])

    @staticmethod
    def _allowed(root: Path) -> set[str]:
        """Read project-specific accepted words without modifying dictionaries.

        Use one word or whole identifier per UTF-8 line. Blank lines and lines
        beginning with # are ignored. A missing file simply adds no project words.
        """
        path = root / ".markdowneditor-spelling.txt"
        values = set(_STANDARD_WORDS)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return values
        values.update(line.strip().lower() for line in text.splitlines()
                      if line.strip() and not line.lstrip().startswith("#"))
        return values

    @staticmethod
    def _mask_escape(match: re.Match) -> str:
        """Hide escape spelling while preserving every original source offset.

        Decoding a string would change its length and move underlines. Replacing
        an escape with equal-length spaces leaves following words at real columns.
        """
        return " " * len(match.group())

    @staticmethod
    def _fragments(text: str):
        """Yield source fragments eligible for spelling with exact start positions.

        Names, comments and string bodies are included. Completed tokens before
        a tokenizer error remain usable while the user is typing incomplete code.
        F-string/template-string middle tokens are recognized on Python versions
        that expose them; Python 3.11 represents a whole f-string as STRING.
        """
        stream = tokenize.generate_tokens(io.StringIO(text).readline)
        middle_types = {getattr(tokenize, "FSTRING_MIDDLE", -1),
                        getattr(tokenize, "TSTRING_MIDDLE", -2)}
        try:
            for item in stream:
                line, column = item.start
                if item.type in (tokenize.NAME, tokenize.COMMENT):
                    yield line - 1, column, item.string
                elif item.type == tokenize.STRING:
                    prefix = _STRING_START.match(item.string)
                    if prefix is None:
                        continue
                    quote = prefix.group(1)
                    body = item.string[prefix.end():-len(quote)]
                    # A raw string has literal backslashes; its words remain text.
                    flags = item.string[:prefix.start(1)].lower()
                    if "r" not in flags:
                        body = _ESCAPE.sub(BilingualSpeller._mask_escape, body)
                    yield line - 1, column + prefix.end(), body
                elif item.type in middle_types:
                    # Keep original source text: do not evaluate interpolation.
                    yield line - 1, column, item.string
        except (tokenize.TokenError, IndentationError, SyntaxError):
            # Syntax findings come from Ruff/basedpyright. Spelling resumes on
            # the next complete snapshot, instead of creating invented tokens.
            return

    def scan(self, job: SpellingJob, cancelled) -> list[Diagnostic]:
        """Check source words and return character-based findings for one job.

        Args:
            job: Buffer text, version and project dictionary context.
            cancelled: Thread-safe callback allowing shutdown or newer work to
                stop an obsolete scan between fragments.

        Returns:
            Spelling errors for words absent from both language dictionaries and
            the project allow-list. Single-letter symbols are intentionally left
            alone. No suggestions or corrections modify the user's source.
        """
        allowed = self._allowed(job.root)
        snapshot = job.snapshot
        findings = []
        known_cache: dict[str, bool] = {}
        for first_line, first_column, fragment in self._fragments(snapshot.text):
            if cancelled():
                return []
            # A whole identifier can be allowed even if it contains underscores.
            if fragment.lower() in allowed:
                continue
            for relative_line, text_line in enumerate(fragment.split("\n")):
                if cancelled():
                    return []
                base_column = first_column if relative_line == 0 else 0
                for word_match in _WORD.finditer(text_line):
                    whole = word_match.group()
                    if whole.lower() in allowed:
                        continue
                    # Splitting on camel boundaries preserves the offset of
                    # each piece; underscores/digits were separated by _WORD.
                    cuts = [0] + [match.start() for match in _CAMEL_BOUNDARY.finditer(whole)] + [len(whole)]
                    for begin, end in zip(cuts, cuts[1:]):
                        word = whole[begin:end]
                        normalized = word.lower().replace("’", "'")
                        if len(word) == 1 or normalized in allowed:
                            continue
                        if normalized not in known_cache:
                            known_cache[normalized] = bool(self.dictionary.known([normalized]))
                        if known_cache[normalized]:
                            continue
                        line = first_line + relative_line
                        column = base_column + word_match.start() + begin
                        findings.append(Diagnostic(
                            "spelling", snapshot.uri, snapshot.path,
                            SourceRange(Position(line, column), Position(line, column + len(word))),
                            # User-requested severity: dictionary findings are errors.
                            DiagnosticSeverity.ERROR, "unknown-word-en-de",
                            f"Possible spelling error: '{word}' is absent from the English and German dictionaries. "
                            "If intentional, add the word to .markdowneditor-spelling.txt.",
                            snapshot.revision,
                        ))
        return findings


class SpellingWorker(QThread):
    """Serialize spelling jobs on one reusable background thread.

    Pending work is a URI-keyed map: newer snapshots replace queued older ones.
    A condition variable sleeps without polling. Only immutable Python data,
    never editor widgets or the GUI diagnostic store, crosses this boundary.
    """

    completed = pyqtSignal(object, list, str)
    failed = pyqtSignal(str)

    def __init__(self, parent=None):
        """Create an empty queue and its synchronization primitive.

        The dictionary itself is constructed in run, after the new thread starts.
        Parent ownership keeps the QThread alive until application shutdown ends.
        """
        super().__init__(parent)
        self._condition = threading.Condition()
        self._pending: dict[str, SpellingJob] = {}
        self._stop_requested = False

    def submit(self, job: SpellingJob) -> None:
        """Queue or replace a URI's pending job from the GUI thread.

        Wake the worker only after publishing the complete immutable job. Work
        submitted after shutdown has started is ignored.
        """
        with self._condition:
            if not self._stop_requested:
                self._pending[job.snapshot.uri] = job
                self._condition.notify()

    def discard(self, uri: str) -> None:
        """Drop queued work for a closed document without blocking an active scan.

        A scan already in progress may finish; the GUI service checks whether
        its document still exists before accepting the result.
        """
        with self._condition:
            self._pending.pop(uri, None)

    def stop(self) -> None:
        """Request cooperative termination and wake a worker waiting for work.

        No unsafe QThread.terminate call is used. An active scan notices this
        flag between fragments, returns, and lets run finish normally.
        """
        with self._condition:
            self._stop_requested = True
            self._pending.clear()
            self._condition.notify_all()

    def _cancelled(self, job: SpellingJob) -> bool:
        """Tell a scan whether shutdown or a queued newer version supersedes it.

        Inspect the shared queue while holding its condition lock; the GUI may
        be replacing that URI at the same time.
        """
        with self._condition:
            newer = self._pending.get(job.snapshot.uri)
            return self._stop_requested or (newer is not None and newer != job)

    def run(self) -> None:
        """Load dictionaries once and process pending documents until stopped.

        Results are emitted through queued Qt connections. A failed dictionary
        load is reported explicitly; it never appears as successful clean text.
        """
        try:
            speller = BilingualSpeller()
        except Exception as error:
            self.failed.emit(f"Spelling could not start: {error}")
            return
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self._stop_requested or bool(self._pending))
                if self._stop_requested:
                    return
                uri = next(iter(self._pending))
                job = self._pending.pop(uri)
            try:
                rows = speller.scan(job, lambda: self._cancelled(job))
                self.completed.emit(job, rows, "")
            except Exception as error:
                self.completed.emit(job, [], f"Spelling failed: {error}")


class SpellingDiagnostics(QObject):
    """Manage live spelling snapshots and accept results on the GUI thread.

    This provider depends only on the shared document/store integration. It can
    be installed with or without the basedpyright topic.
    """

    error = pyqtSignal(str)

    def __init__(self, manager: DiagnosticsManager, root: Path, parent=None):
        """Start a worker and prepare a debounce for bursts of source changes.

        Args:
            manager: Shared GUI-thread diagnostic store.
            root: Directory containing the project's accepted-word file.
            parent: MainWindow, retained until the worker stops on exit.
        """
        super().__init__(parent)
        self.manager = manager
        self.root = Path(root).resolve()
        self._generation = 0
        self._closing = False
        self._documents: dict[str, DocumentSnapshot] = {}
        self._dirty: set[str] = set()
        self.worker = SpellingWorker(self)
        self.worker.completed.connect(self._completed, Qt.QueuedConnection)
        self.worker.failed.connect(self.error.emit, Qt.QueuedConnection)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(350)
        self._timer.timeout.connect(self._flush)
        self.worker.start()

    def attach(self, controller: RuffLspController) -> None:
        """Subscribe once and analyze the controller's currently loaded text.

        The controller owns document identity and emits close notifications on
        rename as well as tab closure, so no file-watcher guesses are required.
        """
        if controller._spelling_attached:
            return
        controller._spelling_attached = True
        controller.document_changed.connect(self.update)
        controller.document_closed.connect(self.close_document)
        self.update(controller.snapshot())

    def update(self, snapshot: DocumentSnapshot) -> None:
        """Replace the live snapshot, invalidate spelling rows and schedule work.

        Old in-flight results become unacceptable immediately, before the new
        job reaches the worker, because _completed compares live versions.
        """
        if self._closing:
            return
        self._documents[snapshot.uri] = snapshot
        self.manager.replace("spelling", snapshot.uri, [])
        self._dirty.add(snapshot.uri)
        self._timer.start()

    def _flush(self) -> None:
        """Submit one latest job for each changed document after typing pauses.

        Job data includes the dictionary generation as well as the source
        revision. Editing the accepted-word file can therefore invalidate work
        without changing the document text.
        """
        if self._closing:
            return
        for uri in self._dirty:
            snapshot = self._documents.get(uri)
            if snapshot is not None:
                self.worker.submit(SpellingJob(snapshot, self.root, self._generation))
        self._dirty.clear()

    def _completed(self, job: SpellingJob, rows: list[Diagnostic], error: str) -> None:
        """Publish only results that still describe the live text and dictionary.

        This slot runs on the GUI thread. A closed URI, newer source revision,
        or dictionary reload makes the received job obsolete.
        """
        current = self._documents.get(job.snapshot.uri)
        if self._closing or current != job.snapshot or job.generation != self._generation:
            return
        if error:
            self.error.emit(error)
        self.manager.replace("spelling", job.snapshot.uri, rows)

    def close_document(self, uri: str) -> None:
        """Forget a removed URI and clear exactly its spelling collection.

        Other providers and other open documents keep their findings. Active
        worker results for this URI will be rejected by _completed.
        """
        self._documents.pop(uri, None)
        self._dirty.discard(uri)
        self.worker.discard(uri)
        self.manager.replace("spelling", uri, [])

    def reconfigure(self, root: Path) -> None:
        """Switch the accepted-word directory after a workspace change.

        Both bundled language dictionaries remain loaded. Only project-specific
        words and the generation used for result acceptance change.
        """
        self.root = Path(root).resolve()
        self.recheck()

    def recheck(self) -> None:
        """Reload project words for every open buffer through fresh worker jobs.

        Connect this method to Diagnostics > Recheck spelling. Use it after
        editing .markdowneditor-spelling.txt without changing the source file.
        """
        if self._closing:
            return
        self._generation += 1
        self.manager.clear_provider("spelling")
        self._dirty.update(self._documents)
        self._timer.start()

    def shutdown(self) -> None:
        """Stop queuing work and request cooperative worker termination.

        MainWindow polls is_running before allowing Qt to destroy this service.
        No GUI-thread wait is used while a dictionary or document is processed.
        """
        self._closing = True
        self._timer.stop()
        self.worker.stop()

    def is_running(self) -> bool:
        """Expose worker activity to the existing asynchronous close mechanism.

        Keep the service and its QThread alive while this returns True, avoiding
        the 'QThread destroyed while still running' failure during application exit.
        """
        return self.worker.isRunning()
```

**Where and how to apply:** Create `ruff_implementation/spelling_diagnostics.py` and paste this code into the empty file. This is a new-file operation; do not paste it into another existing module.

**How to read this new file, class by class and method by method:**

| Class or method | Responsibility |
| --- | --- |
| `SpellingJob` | Pair an immutable document with the dictionary context used to check it. |
| `BilingualSpeller` | Find dictionary-unknown word fragments without executing Python source. |
| `BilingualSpeller.__init__` | Load both bundled dictionaries once, outside the GUI thread. |
| `BilingualSpeller._allowed` | Read project-specific accepted words without modifying dictionaries. |
| `BilingualSpeller._mask_escape` | Hide escape spelling while preserving every original source offset. |
| `BilingualSpeller._fragments` | Yield source fragments eligible for spelling with exact start positions. |
| `BilingualSpeller.scan` | Check source words and return character-based findings for one job. |
| `SpellingWorker` | Serialize spelling jobs on one reusable background thread. |
| `SpellingWorker.__init__` | Create an empty queue and its synchronization primitive. |
| `SpellingWorker.submit` | Queue or replace a URI's pending job from the GUI thread. |
| `SpellingWorker.discard` | Drop queued work for a closed document without blocking an active scan. |
| `SpellingWorker.stop` | Request cooperative termination and wake a worker waiting for work. |
| `SpellingWorker._cancelled` | Tell a scan whether shutdown or a queued newer version supersedes it. |
| `SpellingWorker.run` | Load dictionaries once and process pending documents until stopped. |
| `SpellingDiagnostics` | Manage live spelling snapshots and accept results on the GUI thread. |
| `SpellingDiagnostics.__init__` | Start a worker and prepare a debounce for bursts of source changes. |
| `SpellingDiagnostics.attach` | Subscribe once and analyze the controller's currently loaded text. |
| `SpellingDiagnostics.update` | Replace the live snapshot, invalidate spelling rows and schedule work. |
| `SpellingDiagnostics._flush` | Submit one latest job for each changed document after typing pauses. |
| `SpellingDiagnostics._completed` | Publish only results that still describe the live text and dictionary. |
| `SpellingDiagnostics.close_document` | Forget a removed URI and clear exactly its spelling collection. |
| `SpellingDiagnostics.reconfigure` | Switch the accepted-word directory after a workspace change. |
| `SpellingDiagnostics.recheck` | Reload project words for every open buffer through fresh worker jobs. |
| `SpellingDiagnostics.shutdown` | Stop queuing work and request cooperative worker termination. |
| `SpellingDiagnostics.is_running` | Expose worker activity to the existing asynchronous close mechanism. |

The docstrings inside the code give the arguments, lifecycle requirements and important limits. Inline comments explain the position conversions, version checks or thread boundaries at the point where they are used.

### New file: `.markdowneditor-spelling.txt`

**Folder:** repository root.

#### Step 43: Create `.markdowneditor-spelling.txt`

**Purpose:** Accept intentional technical vocabulary and German compounds for this workspace.

**OLD:** This file does not exist in the starting repository. No existing code is replaced.

**NEW — contents of the new file:**

```text
# Intentional technical terms; one word or complete identifier per line.
# Add project names and valid German compounds when they are flagged.
Ruff
basedpyright
PyQt
QScintilla
Qt
GUI
LSP
URI
UTF
API
RPC
JSON
Jedi
docstring
docstrings
```

**Where and how to apply:** Create `.markdowneditor-spelling.txt` and paste this code into the empty file. This is a new-file operation; do not paste it into another existing module.

### Existing file: `main.py`

**Folder:** repository root.

#### Step 44: Import the spelling provider

**Why:** Add spelling while retaining the current singular type_diagnostic module name.

**OLD — the exact existing block:**

```python
from ruff_implementation.type_diagnostic import TypeDiagnostics
```

**NEW — use this in place of the old code above:**

```python
from ruff_implementation.type_diagnostic import TypeDiagnostics
from ruff_implementation.spelling_diagnostics import SpellingDiagnostics
```

**Where and how to apply:** Beside the existing type-analysis import. Replace only this shown block; keep all surrounding code.

**What changed:** Add only the spelling import.

#### Step 45: Add `MainWindow._install_spelling_diagnostics`

**Why:** Create the bilingual worker after the shared store exists.

**OLD:** This method does not exist. There is no old method to replace.

**NEW — method to add:**

```python
    def _install_spelling_diagnostics(self) -> None:
        """Create bilingual spelling independently of the type-analysis service.

        Dictionaries run on one worker. The explicit recheck action rereads the
        project's accepted-word file for all open Python buffers.
        """
        self.spelling_diagnostics = SpellingDiagnostics(
            self.diagnostics_manager, self._workspace_root, self
        )
        self.spelling_diagnostics.error.connect(self._on_analysis_error)
        self.diagnostics_menu.addAction(
            "Recheck spelling", self.spelling_diagnostics.recheck
        )
        for editor in self.tab_view.all_editors():
            if isinstance(editor, PythonEditor) and editor.ruff_lsp is not None:
                self.spelling_diagnostics.attach(editor.ruff_lsp)
```

**Where and how to apply:** In `main.py`, inside `MainWindow`, insert this method immediately after `_install_type_diagnostics`, before the next method. Keep the shown four-space indentation. Do not put it inside `_install_type_diagnostics`.

**What the new method does:** Connect error reporting, add Recheck spelling and attach existing controllers.

#### Step 46: Start spelling in MainWindow.__init__

**Why:** Start the optional provider before session restoration.

**OLD — the exact existing block:**

```python
        self._install_type_diagnostics()
```

**NEW — use this in place of the old code above:**

```python
        self._install_type_diagnostics()
        self._install_spelling_diagnostics()
```

**Where and how to apply:** Inside __init__, immediately after the existing type installer call. Replace only this shown block; keep all surrounding code.

**What changed:** The common store already exists; do not duplicate its setup.

#### Step 47: Change `MainWindow._connect_editor`

**Why:** Attach spelling to tabs opened after its installer runs.

**OLD — the existing method:**

```python
    def _connect_editor(self, editor):
        """Connect UI signals, bind the shared store and attach type analysis.

        Early tabs are bound later by the installers when services are created.
        Later Python tabs must explicitly attach here; otherwise basedpyright
        never receives their document snapshots. Non-Python tabs are skipped.
        """
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

**NEW — use this in place of the old code above:**

```python
    def _connect_editor(self, editor):
        """Connect UI signals, bind the shared store and attach type analysis.

        Early tabs are bound later by the installers when services are created.
        Later Python tabs must explicitly attach here; otherwise basedpyright
        never receives their document snapshots. Non-Python tabs are skipped.
        """
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
        if (isinstance(editor, PythonEditor) and editor.ruff_lsp is not None
                and hasattr(self, "spelling_diagnostics")):
            self.spelling_diagnostics.attach(editor.ruff_lsp)
```

**Where and how to apply:** In `main.py`, replace only `_connect_editor`, including any decorator shown in OLD. Keep four-space class indentation. Stop before the following `_cat_unbox` method and its decorators.

**What changed:** Append the guarded spelling attach after type attachment, retaining all signals and manager binding from Topic 1.

#### Step 48: Reload spelling on workspace changes

**Why:** Accepted words belong to the current workspace root.

**OLD — the exact existing block:**

```python
        client.start()
```

**NEW — use this in place of the old code above:**

```python
        client.start()
        # Reload accepted words from the newly selected workspace.
        if hasattr(self, "spelling_diagnostics"):
            self.spelling_diagnostics.reconfigure(root)
```

**Where and how to apply:** At the end of MainWindow._restart_ruff, after client.start(). Replace only this shown block; keep all surrounding code.

**What changed:** Keep existing basedpyright reconfiguration above; add spelling reconfiguration using the existing root.

#### Step 49: Stop spelling on application exit

**Why:** Stop worker queuing before the application destroys Qt objects.

**OLD — the exact existing block:**

```python
        self.ruff_lsp_client.shutdown()
```

**NEW — use this in place of the old code above:**

```python
        self.ruff_lsp_client.shutdown()
        if hasattr(self, "spelling_diagnostics"):
            self.spelling_diagnostics.shutdown()
```

**Where and how to apply:** Inside MainWindow.closeEvent at the existing Ruff shutdown call. Replace only this shown block; keep all surrounding code.

**What changed:** Request cooperative worker shutdown; keep existing type shutdown.

#### Step 50: Track spelling worker lifetime

**Why:** Add the optional spelling service to the existing close poll.

**OLD — the exact existing block:**

```python
        type_analysis = getattr(self, "type_diagnostics", None)
```

**NEW — use this in place of the old code above:**

```python
        type_analysis = getattr(self, "type_diagnostics", None)
        spelling = getattr(self, "spelling_diagnostics", None)
```

**Where and how to apply:** Inside _background_work_running beside the existing type_analysis local. Replace only this shown block; keep all surrounding code.

**What changed:** Keep all current references and add spelling.

#### Step 51: Wait asynchronously for spelling worker completion

**Why:** Prevent QThread destruction while its scan is still running.

**OLD — the exact existing block:**

```python
            or (type_analysis is not None and type_analysis.is_running())
```

**NEW — use this in place of the old code above:**

```python
            or (type_analysis is not None and type_analysis.is_running())
            or (spelling is not None and spelling.is_running())
```

**Where and how to apply:** Inside the existing return bool(...) expression in _background_work_running. Replace only this shown block; keep all surrounding code.

**What changed:** Append the new Boolean condition inside the same parentheses.

### Finish Topic 3

Run `python -m pip install -e .` in the application’s environment, then restart MarkdownEditor. Spelling runs in that process, not a different selected project interpreter. Both English and German dictionaries are included in pyspellchecker. A frozen executable must be rebuilt with the package and dictionary data.

Add accepted words or whole identifiers to the root-level `.markdowneditor-spelling.txt`, save it and choose **Diagnostics → Recheck spelling**. This does not suppress undefined-name/member errors from basedpyright. Source edits also submit new spelling jobs. No spelling correction is applied automatically. Spelling findings remain errors as requested, labelled `spelling: unknown-word-en-de`, while dictionary limitations are explained in their messages.

No existing files are deleted. The guide retains your controller lifecycle work, the current `type_diagnostic.py`, Ruff request/application methods and `workspace_edit.py`; only the method-level corrections and additions shown above are needed.

