from __future__ import annotations

from typing import Any

import jedi
from jedi import Project, Script, create_environment
from PyQt5.QtCore import QThread, pyqtSignal

from code_inteligence.jedi_guard import serialized_jedi

# The existing helpers run concurrently; disable's Jedi's shared mutable fast parser
jedi.settings.fast_parser = True



class ReferencesFinder(QThread):
    """Find references without blocking, replaying only the newest request."""

    references_found = pyqtSignal(int, list)
    references_empty = pyqtSignal(int)
    error = pyqtSignal(int, str)

    def __init__(self):
        """Initialize latest-request generations and replay pening work after the active thread finished."""
        super().__init__(None)
        self._generation = 0
        self._request = None
        self._pending = None
        self._shutting_down = False
        self.finished.connect(self._start_pending)

    def find_references(self, line: Any, column: Any, code: Any, file_path: Any=None, workspace: Any=None, interpreter: Any=None) -> None:
        """Capture plain source, caret, project and interpreter values for the newest request."""
        if self._shutting_down:
            return None
        self._generation += 1
        request = (self._generation, line, column, code, file_path, workspace, interpreter)
        if self.isRunning():
            self._pending = request
        else:
            self._request = request
            self.start()
        return self._generation

    def _start_pending(self):
        """Start only the most recent request when the previous worker finishes."""
        if self._shutting_down or self._pending is None:
            return
        self._request, self._pending = self._pending, None
        self.start()
    
    @serialized_jedi
    def run(self) -> None:
        """Run semantic Jedi reference lookup off the GUI thread and emit plain locations or an error."""
        generation, line, column, code, file_path, workspace, interpreter = self._request
        try:
            names = Script(code=code, path=file_path, project=Project(workspace) if workspace else None,
                           environment=create_environment(interpreter, safe=False) if interpreter else None).get_references(line=line, column=column, include_builtins=False)
            if self._shutting_down:
                return
            references = [
                (str(name.module_path), name.line - 1, name.column, name.name)
                for name in names
                if name.module_path is not None
            ]
            if references:
                self.references_found.emit(generation, references)
            else:
                self.references_empty.emit(generation)
        except Exception as exc:
            if not self._shutting_down:
                self.error.emit(generation, str(exc))

    def shutdown(self):
        """Reject future/results requests; completion remains asynchronous."""
        self._shutting_down = True
        self._pending = None
        self.requestInterruption()
        
        
    def invalidate(self) -> None:
        """Reject in-flight results without forcibly terminating a running thread."""
        self._generation += 1
        self._pending = False
        
    @property
    def generation(self) -> Any:
        """Expose the current GUI-side request generation for delivery checks."""
        return self._generation
