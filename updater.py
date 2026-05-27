"""
updater.py — GitHub-based auto-updater for PhoenixMasterTool.

Wave 8a B3 hybrid facade. As of 2026-05-26, this module delegates the
generic update-check + download/apply path to ``phoenix_commons.updater``
while preserving the ValveMaster-specific multi-fallback asset-name
resolution (rename-tolerance from the v1.0 -> v1.1 renaming sprint).

ADR-003 — Phoenix Master Tool ships an **exe-only** updater payload.
``download_and_apply`` therefore calls commons with
``expected_internal=False``; commons handles the zip validation
(checking only that ``<EXE_NAME>`` exists at zip root) and uses its
inline-PowerShell batch wrapper to extract the single exe over the
running binary, then relaunch.

How it works
------------
1. On startup the GUI calls ``check_for_update()`` in a background thread.
2. That function hits the GitHub Releases API (via commons) and compares
   the latest tag against the local ``__version__`` string.
3. If a newer version exists it returns an ``UpdateInfo`` object; the
   GUI shows a banner in the status bar with an "Install & Restart"
   button.
4. When the user clicks the button, ``download_and_apply()`` is called.
   commons downloads, validates, and runs a PowerShell-driven exe-only
   replacement before relaunching.

Preserved-local logic (MIGRATION_RULES § 1 hybrid facade)
---------------------------------------------------------
- ``GITHUB_OWNER`` / ``GITHUB_REPO`` / ``EXE_NAME`` / ``LEGACY_EXE_NAMES``:
  Naming constants. ``LEGACY_EXE_NAMES`` is the rename-tolerance list
  for the v1.0 ``ValveMasterTool`` -> v1.1 ``PhoenixMasterTool``
  transition; commons has no equivalent.

- Multi-fallback asset-name lookup inside ``check_for_update()``:
  commons takes a single ``zip_asset_name`` and exact-matches. The
  ValveMaster facade wraps it in a loop over candidate zip names
  derived from ``EXE_NAME`` and ``LEGACY_EXE_NAMES``, preserving the
  forward-compat behavior the v1.0 updater originally had.

- ``_parse_version`` / ``_ps_single_quote``: kept at module level for
  the ``tests/test_updater.py`` regression baseline. commons has its
  own internal copies; ours stay independently exercised by the unit
  tests so the regression contract is preserved without needing to
  reach into commons internals.

UpdateInfo identity contract
----------------------------
``updater.UpdateInfo is phoenix_commons.updater.UpdateInfo`` — verified
by the B3 commit's identity check. Callers that previously imported
``UpdateInfo`` from this module continue to work unchanged.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

# Commons facade imports — these provide the generic update-check and
# exe-only download/apply implementation. UpdateInfo is re-exported here
# (identity preserved) so callers that do ``from updater import UpdateInfo``
# don't change.
from phoenix_commons.updater import UpdateInfo
from phoenix_commons.updater import check_for_update as _commons_check_for_update
from phoenix_commons.updater import download_and_apply as _commons_download_and_apply

try:
    from version import __version__
except ImportError:
    __version__ = "0.0.0"

logger = logging.getLogger(__name__)

# ── ValveMaster / Phoenix Master Tool release contract ──────────────────────
GITHUB_OWNER = "JustinGlave"
GITHUB_REPO = "phoenix-master-tool"
EXE_NAME = "PhoenixMasterTool.exe"
# Legacy exe names that older installs may have on disk. The auto-updater
# resolves asset names by trying the canonical zip first (derived from
# EXE_NAME's stem), then each legacy candidate in order. Keep oldest first
# so a freshly-renamed install still works.
LEGACY_EXE_NAMES = ("ValveMasterTool.exe",)
# ────────────────────────────────────────────────────────────────────────────

__all__ = [
    "UpdateInfo",
    "check_for_update",
    "download_and_apply",
    "GITHUB_OWNER",
    "GITHUB_REPO",
    "EXE_NAME",
    "LEGACY_EXE_NAMES",
    # Helpers below are preserved for the tests/test_updater.py regression
    # baseline. They are also independently useful for any future code that
    # needs PowerShell string escaping or tag parsing.
    "_parse_version",
    "_ps_single_quote",
]


# ─── Preserved-local helpers (test surface) ──────────────────────────────────

def _ps_single_quote(value: str) -> str:
    """Escape a string for safe inclusion inside a PowerShell single-quoted literal.

    PowerShell single-quoted strings escape ``'`` as ``''``. Without this, a
    path such as ``"C:\\Users\\O'Brien\\..."`` would terminate the string
    mid-path and break the extraction script.

    Preserved-local for ``tests/test_updater.py``. commons has its own
    equivalent (``phoenix_commons.updater.installer._ps_literal``) used
    internally; keeping this here means the unit-test contract is
    independent of commons internals.
    """
    return value.replace("'", "''")


def _parse_version(tag: str) -> tuple[int, ...]:
    """Convert ``'v1.2.3'``, ``'V1.2.3'``, or ``'1.2.3'`` to ``(1, 2, 3)`` for comparison.

    Preserved-local for ``tests/test_updater.py``. commons has its own
    private ``_parse_version`` in ``phoenix_commons.updater.client``; the
    behavior is equivalent but kept here as an independent test surface.
    """
    cleaned = re.sub(r"[^\d.]", "", tag.lstrip("vV"))
    try:
        return tuple(int(part) for part in cleaned.split(".") if part)
    except ValueError:
        return (0,)


# ─── Public API — hybrid facade around phoenix_commons.updater ───────────────

def check_for_update() -> Optional[UpdateInfo]:
    """Query the GitHub Releases API and return an :class:`UpdateInfo` when newer.

    Wave 8a B3 facade. Delegates per-asset lookup to
    :func:`phoenix_commons.updater.check_for_update` and wraps it in a
    multi-candidate fallback loop that preserves the ValveMaster
    rename-tolerance contract:

    1. Try the canonical zip first (``PhoenixMasterTool.zip``, derived
       from ``EXE_NAME``'s stem).
    2. Fall back to any zip derived from ``LEGACY_EXE_NAMES``.

    Safe to call from a background thread — never raises. commons logs
    network failures at DEBUG and payload-parse problems at WARNING.
    """
    candidate_zips: list[str] = [f"{Path(EXE_NAME).stem}.zip"]
    candidate_zips += [f"{Path(name).stem}.zip" for name in LEGACY_EXE_NAMES]

    for zip_asset_name in candidate_zips:
        info = _commons_check_for_update(
            owner=GITHUB_OWNER,
            repo=GITHUB_REPO,
            current_version=__version__,
            zip_asset_name=zip_asset_name,
        )
        if info is not None:
            return info

    return None


def download_and_apply(info: UpdateInfo, progress_callback=None) -> None:
    """Download the update zip, validate the exe-only payload, apply, and relaunch.

    Wave 8a B3 facade. Delegates to
    :func:`phoenix_commons.updater.download_and_apply` with the
    ValveMaster release contract baked in:

    - ``exe_name=EXE_NAME`` (``PhoenixMasterTool.exe``) — the entry name
      commons looks for in the zip and the basename used to construct
      the PowerShell extraction script.
    - ``expected_internal=False`` per **ADR-003** — Phoenix Master Tool
      ships an exe-only updater zip (no ``_internal/`` folder). commons
      validates only that ``<EXE_NAME>`` exists at the zip root.
    - ``progress_callback(bytes_done, total_bytes)`` — forwarded
      verbatim for GUI progress-bar driving.

    The legacy-name tolerance from v1.0.x upgrades is preserved
    naturally: commons extracts the ``EXE_NAME`` entry from the zip and
    writes it to ``Path(sys.executable).resolve()`` — whatever the
    running exe is actually called (``ValveMasterTool.exe`` for legacy
    installs, ``PhoenixMasterTool.exe`` post-rename). The bytes are
    swapped in place regardless of the on-disk filename.

    Raises :class:`RuntimeError` (or
    :class:`phoenix_commons.updater.installer.UpdatePackageError`,
    a subclass) on any failure so the caller can show an error dialog
    rather than silently fail.
    """
    _commons_download_and_apply(
        info,
        exe_name=EXE_NAME,
        expected_internal=False,
        progress_callback=progress_callback,
    )
