# Serialized legacy Jedi worker until the shared scheduler is installed.
from __future__ import annotations

from functools import wraps
from threading import RLock
from typing import Callable, ParamSpec, TypeVar  # noqa: UP035

import jedi

P = ParamSpec("P")
R = TypeVar("R")
_LOCK = RLock()

def serialized_jedi(function: Callable[P, R]) -> Callable[P, R]:
    """Hold on lock while a worker creates, uses and releases its Jedi objects."""
    @wraps(function)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        """Run a complete lookup without interleaving another parser request."""
        with _LOCK:
            jedi.settings.fast_parser = True
            return function(*args, **kwargs)
    return wrapped

