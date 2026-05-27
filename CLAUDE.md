# CLAUDE.md — Phoenix Master Tool

> Operator orientation. Canonical Phoenix-platform doctrine lives in
> the sibling `phoenix-commons` repo's `docs/ui-platform-baseline-v1/`.
> Wave 8a B1 added the commons submodule at `commons/` (pinned to
> `phoenix-commons` `main`; see `.gitmodules`).

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
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe phoenix_master_pyside6.py
```

`requirements.txt` and `requirements-dev.txt` were **added at Wave 8a
B1 (2026-05-26)** per Decision #2 of `WAVE_8A_KICKOFF_DECISION_RECORD.md`.
An earlier note that referenced the 2026-05-19 Operational Hardening
Sprint was stale (the files were not actually present at repo root
before B1). `build.bat` continues to assume a pre-prepared venv (does
NOT install from requirements automatically — that's an operator step).

## Retrofit state

**Wave 8a (commons retrofit) in progress.** B1 (commons submodule +
requirements + family-standard ci.yml) landed 2026-05-26 by explicit
operator-approved early-open override (the doctrinal cooldown floor
was 2026-06-02; floor breached intentionally with no unresolved
technical blockers). B2 through B9 sequence is in
`phoenix-commons/docs/ui-platform-baseline-v1/WAVE_8A_IMPLEMENTATION_BRIEF.md`.

v1.1.0 already shipped **`phoenix_style.qss`** at repo root with the
canonical System A palette (byte-match verified per
`WAVE_8A_VALVEMASTER_PREFLIGHT_AUDIT.md`). Wave 8a is therefore a
**facade retrofit** — commons-backed architecture alignment + build
hardening + updater/theme/widget facades. Expected visible change
≈ 0% (Phoenix-CAD profile). NOT a theme swap.

## CI

Two parallel workflows after Wave 8a B1:

- `.github/workflows/test.yml` (pre-existing) — ubuntu-latest, Python
  matrix 3.10/3.11/3.12, unittest discover + baseline self-test
  (`run_baseline_debug_benchmark`). Preserved per Decision #3 of
  `WAVE_8A_KICKOFF_DECISION_RECORD.md` — **intentional divergence**
  preserved.
- `.github/workflows/ci.yml` (added at Wave 8a B1) — windows-latest,
  Python 3.12, `submodules: recursive` checkout + commons `import`
  smoke + `compileall` + pytest. Family-standard signal.

Both workflows must pass on the retrofit branch tip before merge.

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
