"""Compatibility shim for qtawesome to allow headless import in CI.

Modules can `from src.ui.qtawesome_compat import qta` and call `qta.icon(...)`.
If qtawesome (and PySide6) are available, this exposes the real module. Otherwise
it provides a dummy object with an `icon` method that returns None.
"""

from typing import Any

try:
    import qtawesome as _real_qta  # type: ignore

    qta = _real_qta
except Exception:  # pragma: no cover - CI may lack Qt/OpenGL libs

    class _DummyQta:
        @staticmethod
        def icon(name: str, **kwargs) -> Any:
            # Return a minimal sentinel (None) for headless contexts where QIcon
            # cannot be constructed. Call sites must handle None gracefully.
            return None

    qta = _DummyQta()
