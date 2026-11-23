# Opt-in bounded timings; never reatin editor objects or source text.
from collections import deque
from contextlib import contextmanager
from functools import wraps
from math import ceil, isfinite
from threading import Lock
from time import perf_counter


class PerformanceMonitor:
    """Collect recent operations durations across GUI and worker threads.
    
    Sampes are (fixed operation name, milliseconds, failed) tuples. A global
    capacity bounds memory. This is an inclusive wall-clock profiler: nested
    method durations overlap and worker durations are not GUI blocking time.
    """
    
    def __init__(self, capacity=4000):
        """Initialize disabled; reject a nonpositive sample capacity."""
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self._samples = deque(maxlen=capacity)
        self._capacity = capacity
        self._lock = Lock()
        self._enabled = False
        self._generation = 0
        self._dropped = 0
        
    @property
    def enabled(self):
        """Expose the capture flag without aquiring a lock on the disabled path."""
        return self._enabled
    
    def set_enabled(self, enabled):
        """Start/stop capture and invalidate measurements crossing that boundary."""
        with self._lock:
            self._enabled = bool(enabled)
            self._generation += 1
            
    def clear(self):
        """Remove retained samples and reject measuremtns started before clearing."""
        with self._lock:
            self._samples.clear()
            self._dropped = 0
            self._generation += 1
            
    
    def records(self, name, milliseconds, failed=False, generation=None):
        """Store a finite duration only for an active, current capture.
        
        Args:
            name: Fixed operation label; never pass source, path or diagnostics.
            milliseconds: Nonnegative elapsed wall time.
            failed: Wheter the timed function raised an exception.
            generation: Optional capture identity from measure().
        """
        
        if not isfinite(milliseconds) or milliseconds < 0:
            return
        with self._lock:
            if not self._enabled:
                return
            if generation is not None and generation != self._generation:
                return
            if len(self._samples) == self._capacity:
                self._dropped += 1
            self._samples.append((name, float(milliseconds), bool(failed)))
            
    @contextmanager
    def measure(self, name):
        """Measure a scope, preserve its exceptions, and avoid clocks when disabled."""
        if not self._enabled:
            yield
            return
        generation = self._generation
        started = perf_counter()
        failed = True
        
        try:
            yield
            failed = False
        finally:
            self.records(name, (perf_counter() - started) * 1000, failed, generation)
        
    
    def snapshot(self):
        """Return JSON-rady aggregates computed outside the collection lock.
        
        Counts and percentiles describe the retained window, not lifetime totals.
        p95 uses the nearest-rank definition; do not add nested operations totals.
        """
        with self._lock:
            samples = list(self._samples)
            dropped = self._dropped
        grouped = {}
        for name, duration, failed in samples:
            grouped.setdefault(name, []).append((duration, failed))
        operations = []
        for name, values in sorted(grouped.items()):
            durations = sorted(value[0] for value in values)
            count = len(durations)
            operations.append({
                "name": name, "count": count,
                "mean_ms": sum(durations) / count,
                "p95_ms": durations[max(0, ceil(count * 0.95) - 1)],
                "max_ms": durations[-1],
                "failures": sum(value[1] for value in values),
            })
        return {"capacity": self._capacity, "retained": len(samples),
                "overwritten": dropped, "operations": operations}
                
PERFORMANCE = PerformanceMonitor()


def timed(name):
    """Decorat a synchronous function without changing its result or exceptions.
    
    This wrapper measured the function's actual execution. Decorating a scheduler
    does not measure later asynchronous work; instrument the worker separately.
    """
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if not PERFORMANCE.enabled:
                return function(*args, **kwargs)
            with PERFORMANCE.measure(name):
                return function(*args, **kwargs)
        return wrapped
    return decorate