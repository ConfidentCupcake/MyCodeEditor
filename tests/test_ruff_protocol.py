# Excercise actual transport methods with deterministic signals/process/timers.

# These tests do not start Qt or Ruff. They verify routing and lifetime decisions

import ast
import json
import unittest
from pathlib import Path

from code_intelligence.lsp_coordinates import lsp_to_character

ROOT = Path(__file__).resolve().parents[1]


class Signal:
    def __init__(self):
        self.values = []
    def connect(self, callback):
        self.callback = callback
    def emit(self, *args):
        self.values.append(args)
        
        
class Timers:
    def __init__(self, parent=None):
        self.timeout = Signal()
        self.active = False
    def setSingleShot(self, value): pass
    def setInterval(self, value): self.interval = value
    def start(self, value=None): self.active = True
    def stop(self): self.active = False
    def deleteLater(self): self.deleted = True
    
class Process:
    Running, NotRunning, CrashExit, FailedToStart = 2, 0, 1, 0
    def __init__(self):
        self.writes, self.stdout = [], b""
        self.killed = False
    def state(self): return self.Running
    def write(self, data): self.writes.append(data)
    def readAllStandardOutput(self):
        value, self.stdout = self.stdout, b""
        return value
    def setWorkingDirectory(self, value): self.directory = value
    def start(self, program, arguments): self.launched = (program, arguments)

    def kill(self):
        """Imitate QProcess.kill() for the invalid-header regression test."""
        self.killed = True
def client():
    """Load real methods without executing Qt imports or its constructor."""
    path = ROOT / "ruff_implementation/ruff_lsp_client.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    original = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    methods = [n for n in original.body if isinstance(n, ast.FunctionDef) and n.name != "__init__"]
    cls = ast.ClassDef(name="Client", bases=[], keywords=[], body=methods, decorator_list=[])
    ast.fix_missing_locations(cls)
    ns = {"QTimer": Timers, "QProcess": Process, "json": json}
    exec(compile(ast.Module(body=[cls], type_ignores=[]), str(path), "exec"), ns)
    obj = ns["Client"]()
    obj.process = Process()
    obj._pending_requests, obj._request_timers = {}, {}
    obj._next_request_id = 1
    obj._started, obj._initialized, obj._shutting_down = True, True, False
    obj._suppress_restart_once = False
    obj._restart_attempts, obj._max_restart_attempts = 0, 3
    obj._initialize_timer, obj._restart_timer, obj._stable_timer = Timers(), Timers(), Timers()
    obj.server_error, obj.server_ready, obj.server_stopped = Signal(), Signal(), Signal()
    obj.diagnostics_published = Signal()
    obj._read_buffer = bytearray()
    return obj


class RuffProtocolTests(unittest.TestCase):
    def test_unicode_coordinates(self):
        text = "ä😀x"
        self.assertEqual(lsp_to_character(text, 6, "utf-8"), 2)
        self.assertEqual(lsp_to_character(text, 3, "utf-16"), 2)
        self.assertEqual(lsp_to_character(text, 2, "utf-16"), 1)
        self.assertEqual(lsp_to_character(text, 999, "utf-8"), 3)
        with self.assertRaises(ValueError): lsp_to_character(text, -1, "utf-16")
        with self.assertRaises(ValueError): lsp_to_character(text, 1, "unknown")

    def test_start_does_not_wait(self):
        obj = client()
        obj._started = False
        obj.workspace_root = Path.cwd()
        obj.python_executable, obj.launch_arguments = "python", ["-m", "ruff", "server"]
        obj.start()
        self.assertTrue(obj._initialize_timer.active)
        self.assertEqual(obj.process.launched[1], obj.launch_arguments)
        # Process deliberately has no waitForStarted method.

    def test_response_finishes_once(self):
        obj = client(); results = []
        request = obj.request("example", {}, lambda *args: results.append(args))
        response = {"jsonrpc": "2.0", "id": request, "result": []}
        obj._handle_message(response); obj._handle_message(response)
        self.assertEqual(results, [([], None)])
        self.assertFalse(obj._request_timers)

    def test_timeout_rejects_late_response(self):
        obj = client(); results = []
        request = obj.request("example", {}, lambda *args: results.append(args))
        obj._request_expired(request)
        obj._handle_message({"jsonrpc": "2.0", "id": request, "result": "late"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1]["code"], -32800)

    def test_malformed_does_not_clear_diagnostics(self):
        obj = client()
        for message in [[], None, 12, {"jsonrpc": "2.0", "method": "textDocument/publishDiagnostics", "params": {"uri": "file:///a.py", "diagnostics": None}}]:
            obj._handle_message(message)
        self.assertFalse(obj.diagnostics_published.values)
        obj._handle_message({"jsonrpc": "2.0", "method": "textDocument/publishDiagnostics", "params": {"uri": "file:///a.py", "diagnostics": [], "version": 4}})
        self.assertEqual(obj.diagnostics_published.values, [("file:///a.py", [], 4)])

    def test_fragmented_unicode_frame(self):
        obj = client(); results = []
        request = obj.request("example", None, lambda *args: results.append(args))
        body = json.dumps({"jsonrpc": "2.0", "id": request, "result": "Größe 😀"}, ensure_ascii=False).encode("utf-8")
        frame = f"Content-Length: {len(body)}\r\n\r\n".encode() + body
        for byte in frame:
            obj.process.stdout = bytes([byte]); obj._read_stdout()
        self.assertEqual(results, [("Größe 😀", None)])

    def test_invalid_framing_stops_process(self):
        obj = client()
        obj.process.stdout = b"Content-Length: broken\r\n\r\n"
        obj._read_stdout()
        self.assertTrue(obj.process.killed)

    def test_stop_finishes_pending_and_bounds_retries(self):
        obj = client(); results = []
        obj.request("example", {}, lambda *args: results.append(args))
        obj._on_finished(1, Process.CrashExit)
        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0][1])
        self.assertTrue(obj._restart_timer.active)
        obj._on_finished(1, Process.CrashExit)
        self.assertEqual(obj._restart_attempts, 1)
        obj._restart_timer.stop()
        obj._started = True; obj._restart_attempts = 3
        obj._on_finished(1, Process.CrashExit)
        self.assertFalse(obj._restart_timer.active)


if __name__ == "__main__":
    unittest.main()