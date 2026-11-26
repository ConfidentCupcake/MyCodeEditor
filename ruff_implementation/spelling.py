# GUI ownership, quiet-time scheduling and publication for local spelling.
from __future__ import annotations

from concurrent.futures import CancelledError, ThreadPoolExecutor
from pathlib import Path
from threading import Event
from time import monotonic
from uuid import uuid4

from PyQt5 import sip
from PyQt5.QtCore import QObject, QTimer
from ruff_implementation.diagnostic_layer import configure_document, paint_document

from markdown_editor.markdowneditor import MarkdownEditor
from ruff_implementation.diagnostics_model import (
    Diagnostic,
    DiagnosticSeverity,
    Position,
    SourceRange,
)
from ruff_implementation.spelling_core import scan


class SpellingProvider(QObject):
    """Own at most one immutable scan and never queue every intermediate edit.
    
    GUI metadata polling runs every 100 ms. Text is copied only after 650 ms of
    quiet and only when the single worker is free. Large-file mode and buffers
    over 2 MiB of UTF-8 source are excluded. Worker results are revision-gated.
    """
    
    def __init__(self, window):
        """Create a lazy single-worker executer and a GUI owned scheduling timer."""
        super().__init__(window)
        self.window = window
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="editor-spelling")
        self.job = None
        self.live = {}
        self.observed = {}
        self.done = {}
        self.generation = 0
        self.closed = False
        self.timer = QTimer(self)
        self.timer.setInterval(100) 
        self.timer.timeout.connect(self.sync)
        self.timer.start()
        
    def buffers(self):
        """Return URI -> identity tuple for eligible live Python/Markdown documents.
        
        The tuple carries document, owner, local revision, language, root and vocabulary 
        generation. Untitled Markdown gets a stable per-document URI.
        Python uses the existing controller revision; Markdown uses DocumentState."""
        result = {}
        for doc in self.window.documents.all():
            editor = doc.analysis_owner
            if (editor is None or sip.isdeleted(editor) or getattr(editor, "large_file_mode", False) or editor.length() > 2 * 1024 * 1024):
                continue
            controller = getattr(editor, "ruff_lsp", None)
            markdown = isinstance(editor, MarkdownEditor)
            if not markdown and (controller is None or controller._closed):
                continue
            if not hasattr(doc, "spelling_id"):
                doc.spelling_id = "untitled:" + uuid4().hex
            uri = controller.uri if controller is not None else (Path(doc.path).resolve().as_uri() if doc.path else doc.spelling_id)
            revision = doc.revision if markdown else controller.document_version
            result[uri] = (doc, editor, revision, markdown, self.window._workspace_root, self.generation)
        return result
    
    def reload(self):
        """Invalidate vocabulary results and rescan quiet buffers on explicit action."""
        if self.closed:
            return
        self.generation += 1
        if self.job is not None:
            self.job[3].set()
        self.done.clear()
        self.observed.clear()
        self.sync()
    
    def sync(self):
        """Retire old identities, consume completed work and submit the oldest due scan.
        
        futures never touch the GUI. We poll done() before result(), so reading
        a result cannot wait. A changed key cancels the running job cooperatively.
        Pending keys are metadata, not copied source or an unbounded task queue.
        """
        if self.closed:
            return
        current = self.buffers()
        now = monotonic()
        for uri, key in self.live.items():
            replacement = current.get(uri)
            if replacement is None or replacement[:2] != key[:2] or replacement[:4] != key[:4]:
                self.window.diagnostics_manager.clear_collection("spelling", uri)
                paint_document(key[0], "spelling", [])
                self.observed.pop(uri, None)
                self.done.pop(uri, None)
        self.live = current
        for uri, key in current.items():
            configure_document(key[0], "spelling")
            if uri not in self.observed or self.observed[uri][0] != key:
                self.observed[uri] = (key, now + 0.650)
                self.window.diagnostics_manager.clear_collection("spelling", uri)
        if self.job is not None:
            future, uri, key, cancelled = self.job
            if current.get(uri) != key:
                cancelled.set()
            if not future.done():
                return
            self.job = None
            if current.get(uri) == key:
                self.done[uri] = key
                try:
                    result = future.result()
                except CancelledError:
                    self.done.pop(uri, None)
                except Exception as error:
                    self.window.statusBar().showMessage(f"Spelling scan failed: {error}. Use Reload Spelling to retry.", 8000)
                else:
                    self.publish(uri, key, result)
        due = [(deadline, uri, key) for uri, (key, deadline) in self.observed.items() if uri in current and current[uri] == key and self.done.get(uri) != key and now >= deadline]
        if due:
            _, uri, key = min(due, key=lambda item: item[0])
            cancelled = Event()
            future = self.pool.submit(scan, key[1].text(), key[3], key[4], cancelled)
            self.job = future, uri, key, cancelled
    
    
    def publish(self, uri, key, result):
        """Replace current spelling rows and only indicator 28 after a complete scan."""
        if self.closed or self.buffers().get(uri) != key:
            return
        if not result.complete:
            self.window.statusBar().showMessage("Spelling is waiting for complete Python tokens.", 3000)
            return
        doc, owner, revision, markdown, root, generation = key
        rows = [Diagnostic("spelling", uri, doc.path, SourceRange(Position(line,start), Position(line, end)), DiagnosticSeverity.INFORMATION, "spelling", f"Unknown word: {word}", revision) for line, start, end, word in result.findings] 
        self.window.diagnostics_manager.replace("spelling", uri, rows)
        paint_document(doc, "spelling", rows)
        if result.limited:
            self.window.statusBar().showMessage("Spelling displays the first 500 findings in this document.", 6000)
            

    def is_running(self):
        """Report unfinished immutable work for the window's asynchronous close wait."""
        return self.job is not None and not self.job[0].done()
    
    def shutdown(self):
        """Stop publication, cancel cooperatively and never join a worker in the GUI."""
        if self.closed:
            return
        self.closed = True
        self.timer.stop()
        if self.job is not None:
            self.job[3].set()
        self.pool.shutdown(wait=False, cancel_futures=True)


