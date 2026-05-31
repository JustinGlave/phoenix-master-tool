# Changelog

All notable changes to **Phoenix Master Tool** (working repo
previously "ValveMasterTool"; renamed at v1.1.0) are documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.1] — 2026-05-30

Wave 8a commons retrofit + release hardening — no functional changes.

### Changed
- **Wave 8a commons retrofit complete** (merged 2026-05-26,
  commit `631dbe8`). Migrated to commons-backed pattern per
  ADR-015 (`phoenix-commons` git submodule + editable install).
  Theme + widgets + paths + updater now facade through
  `phoenix_commons` rather than local duplicates. Local QSS
  overlay preserved per MIGRATION_RULES § Local backup QSS
  strategy (System A palette was already shipped in v1.1.0;
  this retrofit is widget/theme/updater facade work only).
  AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` preserved
  byte-for-byte. Exe-only updater payload contract preserved
  per ADR-003 (`expected_internal=False`). Detailed reports
  under `phoenix-commons/docs/ui-platform-baseline-v1/WAVE_8A_*.md`
  + `PHASE_8A_VALVEMASTER_REPORT.md`.
- **Build pipeline hardened** per FROZEN_BUILD_BASELINE
  (Wave 8a B6, merged 2026-05-26). `build.bat` now enforces
  Python 3.12 soft-warn + Step 0 full cleanup +
  `--noupx` + `--collect-all=phoenix_commons` + 8× stdlib
  `--exclude-module` flags. S1-safe profile per ADR-014.
- **Decoded Fields visual fix** (Wave 8a B8a, 2026-05-26):
  valid decoded segments now correctly render with green
  success treatment and invalid segments with red error
  treatment, via two-layer QSS compose preserving the
  app-specific `#FieldCardButton` selectors.

### Added
- CHANGELOG.md (this file) — Operational Hardening Sprint
  2026-05-19.

## [1.1.0] — 2026-05-10

Major release: tool renamed from "ValveMasterTool" to "Phoenix Master
Tool", expanded product line coverage, new Inventory tool.

### Changed
- **Renamed**: ValveMasterTool → Phoenix Master Tool throughout.
  Exe: `ValveMasterTool.exe` → `PhoenixMasterTool.exe`. Install path:
  `{localappdata}\ATS Inc\ValveMasterTool` → `{localappdata}\ATS Inc\PhoenixMasterTool`.
  GitHub release asset: `ValveMasterTool.zip` → `PhoenixMasterTool.zip`.
  AppId GUID preserved per Inno Setup upgrade contract.
- Python module renames: `valve_master_pyside6.py` →
  `phoenix_master_pyside6.py`, `valve_master_backend.py` →
  `phoenix_master_backend.py`.

### Added
- 9 Phoenix product lines covered by the model-number decoder.
- New **Inventory tool** (`inventory.py`) — parts list / inventory
  data layer with SharePoint-synced catalog.
- Phoenix dark-navy design system — `phoenix_style.qss` at repo
  root (moving off System B `#1c1c1c` grey to System A navy).
- Updater hardening against rename pain — legacy-zip detection +
  running-exe overwrite handling.
- `tests/` — `test_updater.py` + `test_validation.py` (unittest).
- `.github/workflows/test.yml` — CI matrix on Python 3.10/3.11/3.12
  (Ubuntu).
- `build.bat` signing subroutine + IF-block escaping fix.

## [1.0.9] — 2026-04-16

Last release under the "ValveMasterTool" name. Theme toggle button
added to header; parts list CSV export.

### See also
- Earlier 1.0.x patch releases (V1.0.1 through 1.0.8) — see git tags.
  Not reproduced here per the Phoenix Tools CHANGELOG policy
  ("current release + retrofit milestone only" — full history in
  git log).
