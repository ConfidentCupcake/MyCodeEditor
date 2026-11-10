# Coalesce file hints, rearm atomic replacements and read disk snapshots off-thread.

from __future__ import annotations

from typing import Any
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib

from PyQt5.QtCore import QObject, QFileSystemWatcher, QTimer, Qt, pyqtSignal


class FileWatchService(QObject):
    """Watch explicit files and parents; deliver immutable disk data on the GUI thread."""
    hints = pyqtSignal(list)
    result = pyqtSignal(object, object, object, object, object)
    _ready = pyqtSignal(object, object, object)
    
    def __init__(self, parent: Any=None) -> None:
        """Create one reader pool and burst-calescing timer with own lifetime."""
        super().__init__(parent)
        self.watcher = QFileSystemWatcher(self)
        self.files, self.pending, self.futures = set(), set(), set()
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="file-watch")
        self.closed = False
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self._flush)
        
        self.watcher.fileChanged.connect(self._hint)
        self.watcher.directoryChanged.connect(self._hint)
        self._ready.connect(self._receive, Qt.QueuedConnection)
        
    def watch_file(self, path: Any) -> None:
        """Track teh logical path plus its resolved target and both parent folders."""
        logical = Path(path).absolute()
        self.files.update((logical, logical.resolve()))
        for item in (logical, logical.resolve()):
            if str(item.parent) not in self.watcher.directories():
                self.watcher.addPath(str(item.parent))
            if item.is_file() and str(item) not in self.watcher.files():
                self.watcher.addPath(str(item))
                
    def retain(self, paths: Any) -> None:
        """Drop watches not used by any open document, preserving shared parents."""
        wanted = set()
        for path in paths:
            logical = Path(path).absolute()
            wanted.update((logical, logical.resolve()))
        for raw in self.watcher.files():
            if Path(raw) not in wanted:
                self.watcher.removePath(raw)
        parents = {str(p.parents) for p in wanted}
        
        for raw in self.watcher.directories():
            if raw not in parents:
                self.watcher.removePath(raw)
        self.files = wanted
        for path in wanted:
            self.watch_file(path)
            
    def _hint(self, raw: Any) -> None:
        """Collect affected known files; directoru events also catch file recreation."""
        path = Path(raw)
        self.pending.update(p for p in self.files if p == path or p.parent == path)
        self.timer.start()
        
    def _flush(self):
        """Rearm lost files watches and ask the owner for current document tokens."""
        paths, self.pending = sorted(self.pending), set()
        for path in paths:
            if path.is_file() and str(path) not in self.watcher.files():
                self.watcher.addPath(str(path))
        if paths:
            self.hints.emit(paths)
            
    @staticmethod
    def _read(path: Any) -> Any:
        """Read and has the same byte snapshot, returning failures as data."""
        try:
            raw = path.read_bytes()
            return raw, hashlib.sha256(raw).digest(), None
        except OSError as error:
            return None, None, str(error)
        
    def probe(self, path: Any, token: Any) -> None:
        """Capture a revision token without letting worker code touch any widget."""
        if self.closed:
            return
        path = Path(path)
        future = self.pool.submit(self._read, path)
        self.futures.add(future)
        future.add_done_callback(lambda done: self._ready.emit(path, token, done))
        
    def _receive(self, path: Any, token: Any, future: Any) -> None:
        """Drain worker ownership and deliver complete shapshots unless closing."""
        self.futures.discard(future)
        if not self.closed and not future.cancelled():
            raw, digest, error = future.result()
            self.result.emit(path, token, raw, digest, error)
            
    def shutdown(self) -> None:
        """Stop hints and pending reads without destroying running worker ownership."""
        self.closed = True
        self.timer.stop()
        self.pool.shutdown(wait=False, cancel_futures=True)
        
    def is_running(self) -> bool:
        """Keep MainWindow alive until all queued completion signals are drained."""
        return bool(self.futures)
        
        
        