# Pure configuration and server-request handling for the Basedpyright adapter.
from __future__ import annotations
from typing import Any


def settings_for(interpreter: str) -> dict[str, Any]:
    """Return a fresh settings tree for one selected Python environment.
    
    python.pythonPath selects import resolution. basedpyright.analysis selects 
    analysis behavior. Project configuration can override analysis defaults.
    Returning new dictionaries prevents one request mustating later replies.
    """
    return {
        "python": {"pythonPath": interpreter},
        "basedpyright": {
            "diableOrganizeImports": True,
            "analysis": {
                "diagnosticMode": "openFilesOlny",
                "typeCheckingMode": "standard",
                "autoSearchPaths": True,
                "useLibraryCodeForTypes": True,
            },
        },
    }
    
    
def server_reply(message: Any, settings: dict[str, Any], folders: list[dict]) -> dict | None:
    """Build a JSON-RPC response for a server request; otherwise return None.
    
    Inputs are decoded JSON, the workspace settings tree and workspace folders.
    Only request with a string method and integer/string ID are intercepted.
    Configuration items preserve request orders. Missing sections produce null.
    Unknown methods receive MethodNotFound, rather than false acknowledgement.
    Invalid configuration parameters receive InvalidParams, never an exception
    in the GUI event loop. Repsonses nad notifications go to the base router.
    """
    if (not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or "id" not in message or not isinstance(message.get("method"), str) or type(message["id"]) not in (int, str)):
        return None
    reply = {"jsonrpc": "2.0", "id": message["id"]}
    method = message["method"]
    if method == "workspace/workspaceFolders":
        reply["result"] = folders
        return reply
    if method != "workspace/configuration":
        reply["error"] = {"code": -32601, "message": "Unsupported client request"}
        return reply
    params = message.get("params")
    items = params.get("items") if isinstance(params, dict) else None 
    if (not isinstance(items, list) or any(not isinstance(item, dict) or (item.get("section") is not None and not isinstance(item["section"], str)) for item in items)):
        reply["error"] = {"code": -32602, "message": "Invalid configuration items"}
        return reply
    values = []
    for item in items:
        section = item.get("section")
        value: Any = settings
        if section:
            for part in section.split("."):
                value = value.get(part) if isinstance(value, dict) else None
        values.append(value)
    reply["result"] = values
    return reply
        