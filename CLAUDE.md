# CLAUDE.md — Phoenix Master Tool

> Operator orientation. Canonical Phoenix-platform doctrine (consumed
> post-Phase-8a) lives in the sibling `phoenix-commons` repo's
> `docs/ui-platform-baseline-v1/`. This repo does NOT carry a commons
> submodule yet.

## Purpose

PySide6 desktop tool that decodes, validates, and guides the build
of Phoenix valve model numbers across 9 product lines. Includes a
Parts List / Inventory tool backed by an ATS SharePoint-synced JSON
catalog.

## Repo identity (renamed at v1.1.0)

| Item | Pre-rename | Post-rename |
|------|-----------|-------------|
| Display name | ValveMasterTool | Phoenix Master Tool |
| Exe | `ValveMasterTool.exe` | `PhoenixMasterTool.exe` |
| GitHub repo | `valve-master-tool` | `phoenix-master-tool` |
| Install path | `\ATS Inc\ValveMasterTool` | `\ATS Inc\PhoenixMasterTool` |
| Local working dir name | (still `ValveMasterTool` — local history preserved) |
| AppId GUID | `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` | **same** (preserved per Inno Setup upgrade contract) |

`updater.py` was hardened in v1.1.0 against the rename pain
(legacy-zip-filename + running-exe-overwrite handling).

## Operational entrypoints

```powershell
py -3.12 -m venv .venv                         # canonical per ADR-014; CI matrix also tests 3.10 + 3.11
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe phoenix_master_pyside6.py
```

`requirements.txt` was added during the Operational Hardening Sprint
2026-05-19 for CI / fresh-clone convenience. `build.bat` does NOT
consume it (assumes pre-prepared venv).

## Retrofit state

**Not yet retrofitted to commons.** Phase 8a is the scheduled
retrofit; gated by Phase 3C (PCC) completing first per
`MIGRATION_RULES.md § Migration order` + § Frequency limits.

v1.1.0 already shipped **`phoenix_style.qss`** at repo root — System A
theme adoption is partially complete. Phase 8a retrofit scope is
therefore reduced: widget facade + updater facade + paths facade
only; theme work is largely done.

## CI

`.github/workflows/test.yml` — ubuntu-latest, Python matrix
3.10/3.11/3.12, unittest discover + baseline self-test
(`run_baseline_debug_benchmark`). Pre-rename CI preserved per user
direction during the Operational Hardening Sprint — **intentional
divergence** from the family's `ci.yml` + windows-latest convention.

## Do NOT change casually

| Item | Reason |
|------|--------|
| AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` | Inno Setup upgrade-detection identity. Only tool in the family with an explicit AppId. Hard rule per `MIGRATION_RULES.md § Stop conditions`. |
| Updater zip payload | **Exe-only** per ADR-003 (`PhoenixMasterTool.zip` contains the exe only) |
| Base64-embedded brand assets in `assets.py` | PyInstaller bundles via module scan, not `--add-data=`. Swapping assets requires editing `assets.py`. |
| Inventory tool's SharePoint-synced JSON path | User-side OneDrive Business sync; path drift breaks catalog load |
| `tests/test_updater.py` + `tests/test_validation.py` | Pre-Phase-8a regression baseline |

## Canonical references

- `phoenix-commons/docs/ui-platform-baseline-v1/MIGRATION_RULES.md`
  (sibling repo)
- `phoenix-commons/docs/ui-platform-baseline-v1/RETROFIT_PLAYBOOK.md`
  (when Phase 8a kicks off)
- `CHANGELOG.md` — v1.1.0 rename + 9 product lines + Inventory tool
- `GIT_SETUP.md` — git workflow specifics (kept separate)
