"""Source-dependent regression tests. Run against real repo with pytest -q tests/test_diagnostic_regressions.py"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_method(path: str, class_name: str, name: str, injected=None):
    file = ROOT / path
    tree = ast.parse(file.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    method.decorator_list = []
    node = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(node)
    ns = dict(injected or {})
    exec(compile(node, str(file), "exec"), ns)
    return ns[name]


class Signal:
    def __init__(self): self.called = []
    def connect(self, callback): self.called.append(("connect", callback))
    def disconnect(self, callback): self.called.append(("disconnect", callback))
    def emit(self, *args): self.called.append(("emit", args))


def fake_client():
    return SimpleNamespace(server_ready=Signal(), server_stopped=Signal(), diagnostics_published=Signal(), is_ready=False)


def test_ruff_restart_replaces_the_client_reference():
    set_client = load_method("ruff_implementation/ruff_lsp_controller.py", "RuffLspController", "set_client")
    old, new = fake_client(), fake_client()
    obj = SimpleNamespace(client=old, open_document=lambda: None,
                          _on_server_stopped=lambda: None, _on_diagnostics_published=lambda *args: None,
                          _retire_display=lambda: None, _opened=True)
    set_client(obj, new)
    assert obj.client is new
    assert obj._opened is False


def test_ruff_handshake_uses_server_selected_utf8_encoding():
    initialize = load_method("ruff_implementation/ruff_lsp_client.py", "RuffLspClient", "_on_initialized")
    init_timer, stable_timer, ready, errors = Signal(), Signal(), Signal(), Signal()
    killed = []
    obj = SimpleNamespace(_initialize_timer=SimpleNamespace(stop=lambda: init_timer.emit()),
        _stable_timer=SimpleNamespace(start=lambda: stable_timer.emit()), _shutting_down=False,
        _started=True, _initialized=False, _suppress_restart_once=False,
        process=SimpleNamespace(kill=lambda: killed.append(True)), server_error=errors,
        notify=lambda *args: None, server_ready=ready, position_encoding="utf-16")
    initialize(obj, {"capabilities": {"positionEncoding": "utf-8"}}, None)
    assert obj.position_encoding == "utf-8"
    assert obj._initialized
    assert not killed
    assert ("emit", ()) in ready.called


def test_basedpyright_settings_match_documented_keys_and_values():
    from ruff_implementation.type_protocol import settings_for
    settings = settings_for("C:/venv/Scripts/python.exe")
    assert settings["basedpyright"]["disableOrganizeImports"] is True
    assert settings["basedpyright"]["analysis"]["diagnosticMode"] == "openFilesOnly"


def test_python_spelling_scans_tokens_without_crashing():
    from ruff_implementation.spelling_core import regions, check_words
    result = list(regions('description = "helllo world"\n# typoos here\n', False))
    assert any("helllo" in source for _, _, source in result)
    rows = check_words('description = "helllo world"\n', False, known=lambda word: word != 'helllo')
    assert rows.complete
    assert (0, 15, 21, "helllo") in rows.findings


def test_basedpyright_paints_the_validated_diagnostic_snapshot():
    publish = load_method("ruff_implementation/provider_bridge.py", "ProviderBridge", "receive_types",
                          {"convert_types": lambda *args: ["converted-diagnostic"],
                           "paint_document": lambda *args: painted.append(args)})
    painted = []
    replaced = []
    document = SimpleNamespace(path=Path("some.py"))
    editor = SimpleNamespace(lines=lambda: 1, text=lambda n=0: "bad")
    controller = SimpleNamespace(document_version=4, editor=editor)
    obj = SimpleNamespace(closed=False, buffers=lambda: {"file:///some.py": (document, controller)},
                          versions=SimpleNamespace(accepts=lambda *a: True),
                          window=SimpleNamespace(diagnostics_manager=SimpleNamespace(replace=lambda *args: replaced.append(args))),
                          _error=lambda message: None)
    publish(obj, "file:///some.py", [], 9)
    assert replaced == [("basedpyright", "file:///some.py", ["converted-diagnostic"])]
    assert painted == [(document, "basedpyright", ["converted-diagnostic"])]