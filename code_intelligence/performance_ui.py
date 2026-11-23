# Window-owned capture controls and an event-loop lateness probe.
import json
import platform
from pathlib import Path
from time import perf_counter

from PyQt5.QtCore import QObject, QTimer, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from code_intelligence.performance import PERFORMANCE



class PerformanceTools(QObject):
    """Expose opt-in capture without logging or rebuilding tables while typing.
    
    Construct once after the window UI exists and before command discovery.
    The timer is owned by this object; shutdown on application quit stops it.
    """
    
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self._last_tick = None
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self._tick)
        menu = window.menuBar().addMenu("Performance")
        self.capture_action = menu.addAction("Capture Timings")
        self.capture_action.setObjectName("performance.capture")
        self.capture_action.setCheckable(True)
        self.capture_action.toggled.connect(self.set_enabled)
        clear = menu.addAction("Clear Timings")
        clear.setObjectName("performance.clear")
        clear.triggered.connect(self.clear)
        export = menu.addAction("Export Timings")
        export.setObjectName("performance.export")
        export.triggered.connect(self.export)
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().aboutToQuit.connect(self.shutdown)
        
    def set_enabled(self, enabled):
        """Toggle both collection and probing; do not persist capture across runs."""
        PERFORMANCE.set_enabled(enabled)
        self._last_tick = perf_counter() if enabled else None
        if enabled:
            self.timer.start()
        else:
            self.timer.stop()
            
            
    def clear(self):
        """Begin a fresh sample window without attributing the previous interval."""
        PERFORMANCE.clear()
        self._last_tick = perf_counter() if PERFORMANCE.enabled else None
        
    def _tick(self):
        """Record excess time beyond the nominal 50 ms GUI timer interval.
        
        This is an event-lpp[ lateness proxy, not keystroke-to-pixel latency.
        OS scheduling, sleep and modal interaction can also cause long samples.
        """
        now = perf_counter()
        if self._last_tick is not None:
            PERFORMANCE.records("gui.timer_lateness", max(0.0, (now - self._last_tick) * 1000 - 50))
        self._last_tick = now
        
    
    def export(self):
        """Stop capture before dialogs and write timing aggregates to a chosen file.
        
        The report contains runtime versions and lexer backend information, never 
        document text or file paths. An export failure leaves in-memory data intact.
        """
        self.capture_action.setChecked(False)
        from python_editor import custompythonlexer
        report = PERFORMANCE.snapshot()
        report["runtime"] = {
            "python": platform.python_version(),
            "qt": QT_VERSION_STR, "pyqt": PYQT_VERSION_STR,
            "cython_lexer_loaded": bool(custompythonlexer._HAS_CYTHON),
        }
        path, _ = QFileDialog.getSaveFileName(
            self.window, "Export performance timings", "editor-timings.json", "JSON files (*.json)"
        )
        if not path:
            return
        
        try:
            Path(path).write_text(json.dumps(report, indent=2), encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(self.window, "Performance export failed", str(error))
            return
        self.window.statusBar().showMessage("Performance report exported", 4000)
        
    
    def shutdown(self):
        """Stop the owned timer and invalidate unfinished timing measurements."""
        self.timer.stop()
        PERFORMANCE.set_enabled(False)
        self._last_tick = None
        
        
        