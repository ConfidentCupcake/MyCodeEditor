"""Run with python -m unittest discover -s tests -p test_performance_monitor.py."""
import unittest

from code_intelligence.performance import PERFORMANCE, PerformanceMonitor, timed


class MonitorTests(unittest.TestCase):
    def test_disabled_capture_is_empty(self):
        monitor = PerformanceMonitor()
        with monitor.measure("noop"):
            result = 2 + 2
        self.assertEqual(result, 4)
        self.assertEqual(monitor.snapshot()["retained"], 0)

    def test_capacity_and_percentile(self):
        monitor = PerformanceMonitor(3)
        monitor.set_enabled(True)
        for value in (1, 2, 3, 4):
            monitor.records("work", value)
        report = monitor.snapshot()
        self.assertEqual(report["overwritten"], 1)
        self.assertEqual(report["operations"][0]["mean_ms"], 3)
        self.assertEqual(report["operations"][0]["p95_ms"], 4)

    def test_clear_rejects_inflight_measurement(self):
        monitor = PerformanceMonitor()
        monitor.set_enabled(True)
        with monitor.measure("old"):
            monitor.clear()
        self.assertEqual(monitor.snapshot()["retained"], 0)

    def test_exception_is_recorded_and_propagated(self):
        monitor = PerformanceMonitor()
        monitor.set_enabled(True)
        with self.assertRaisesRegex(ValueError, "original"):
            with monitor.measure("failure"):
                raise ValueError("original")
        self.assertEqual(monitor.snapshot()["operations"][0]["failures"], 1)

    def test_toggle_rejects_cross_capture_measurement(self):
        monitor = PerformanceMonitor()
        monitor.set_enabled(True)
        with monitor.measure("old"):
            monitor.set_enabled(False)
            monitor.set_enabled(True)
        self.assertEqual(monitor.snapshot()["retained"], 0)

    def test_decorator_preserves_return_and_name(self):
        @timed("test.add")
        def add(left, right):
            return left + right
        PERFORMANCE.clear()
        PERFORMANCE.set_enabled(True)
        try:
            self.assertEqual(add(2, 3), 5)
            self.assertEqual(add.__name__, "add")
            self.assertEqual(PERFORMANCE.snapshot()["retained"], 1)
        finally:
            PERFORMANCE.set_enabled(False)
            PERFORMANCE.clear()


if __name__ == "__main__":
    unittest.main()