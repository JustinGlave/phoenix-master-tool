# Changelog

All notable changes to **Phoenix Master Tool** (working repo
previously "ValveMasterTool"; renamed at v1.1.0) are documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- CHANGELOG.md (this file) — Operational Hardening Sprint
  2026-05-19.

### Pending
- Phase 8a retrofit to commons-backed pattern per
  MIGRATION_RULES.md § Migration order (the System B grey →
  System A navy palette swap is already complete — phoenix_style.qss
  shipped in v1.1.0 — so Phase 8a is now widget/theme/updater
  facade work only). Local CI (`test.yml`) and tests are already in
  place; the retrofit gains them rather than adds them.

## [1.1.0] — 2026

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
