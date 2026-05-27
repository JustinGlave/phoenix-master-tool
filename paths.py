"""Phoenix Master Tool — local paths facade.

Re-exports commons path helpers and binds the tool-specific source-tree
``base`` for ``resource_path`` so call sites can use the historical
``resource_path(filename) -> str`` shape (byte-identical to the
``_resource_path`` helper this file retires at Wave 8a B2).

Wave 8a B2 — created 2026-05-26 (operator-approved early-open override).

Why the wrapper?

  ``phoenix_commons.paths.resource_path(filename, base=None)`` returns
  ``Path(filename)`` in source mode when no ``base`` is provided, which
  is cwd-relative and brittle. The retired ``_resource_path`` always
  resolved against ``dirname(abspath(__file__))`` (the repo root, since
  the function lived in ``phoenix_master_pyside6.py``). Binding
  ``base = Path(__file__).resolve().parent`` here preserves that
  behavior — ``paths.py`` lives at repo root alongside the main module,
  so the resolved base is identical.

Frozen-mode behavior is unchanged (commons returns ``_MEIPASS / filename``
when ``is_frozen()`` is true, regardless of ``base``).

Return type is ``str`` (not ``Path``) to preserve byte-identity with the
old helper for any caller that may stringify or concatenate.
"""

from __future__ import annotations

from pathlib import Path

from phoenix_commons.paths import is_frozen, user_data_dir
from phoenix_commons.paths import resource_path as _commons_resource_path

__all__ = ["is_frozen", "user_data_dir", "resource_path"]

_TOOL_ROOT: Path = Path(__file__).resolve().parent


def resource_path(filename: str) -> str:
    """Resolve a bundled-resource path. Frozen-aware via commons.

    Returns the same string a caller would have gotten from the retired
    ``_resource_path`` helper in ``phoenix_master_pyside6.py``.
    """
    return str(_commons_resource_path(filename, base=_TOOL_ROOT))
