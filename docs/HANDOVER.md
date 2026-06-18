# Phoenix Master Tool — Handover

For transferring this codebase to a new Claude session (e.g. Claude Cowork).
Pair this with **`CLAUDE.md`** at the repo root — that file is the canonical
operator orientation; this file complements it with product-line architecture,
recent session context, and a quick-start for typical changes.

---

## 1. Read in this order

1. **`CLAUDE.md`** (repo root) — operational entrypoints, retrofit state, CI,
   do-not-change rules, canonical platform references.
2. **`CHANGELOG.md`** (repo root) — formal release log. Newest at top.
3. **`phoenix-commons/docs/ui-platform-baseline-v1/`** (sibling repo, pinned
   via `commons/` submodule) — platform doctrine, ADRs, migration rules,
   retrofit playbook. CLAUDE.md links to the specific docs.
4. **This file** — product-line decoder architecture + memory-file index
   + recent session context.

---

## 2. Project at a glance

**Phoenix Master Tool (PMT)** — Windows PySide6 desktop app that decodes
Phoenix Controls valve model numbers across 13 product lines, plus a
Parts List / Inventory tool backed by an ATS SharePoint-synced JSON
catalog. Used internally at ATS Inc.

| | |
|---|---|
| GitHub | https://github.com/JustinGlave/phoenix-master-tool |
| Old name (redirects work) | `JustinGlave/valve-master-tool` |
| Latest release | **v1.1.1** (2026-05-30 — Wave 8a commons retrofit, no functional changes) |
| Working dir on disk | `C:\Users\justing\PycharmProjects\ValveMasterTool` (folder name still legacy) |
| Canonical venv | Python 3.12 per ADR-014 (`py -3.12 -m venv .venv`) |
| Commons submodule | `commons/` — pinned to `phoenix-commons` `main` |
| QSettings key | `("ATSInc", "PhoenixMasterTool")` |
| Admin password (parts list) | `Alerton1986@` (hard-coded in `inventory.is_admin_password`) |
| Inventory data path | `%USERPROFILE%\ATS\Phoenix - Documents\Valve Master Tool\inventory.json` (folder name still legacy on SharePoint — deliberate) |

---

## 3. Source files

### Repo-root Python (the app)

| File | Purpose |
|---|---|
| `phoenix_master_pyside6.py` | All GUI: `ValveMasterMainWindow`, dialogs (`TestModelsDialog`, `CfmCalculatorDialog`, `PartsListDialog`, `SelfTestDialog`, `VersionHistoryDialog`), helpers (`SectionCard`, `WatermarkWidget`, `Phoenix*Button`, `BadgeLabel`, `PhoenixTable`), `VALID_TEST_MODELS` / `FAILING_TEST_MODELS`, entry point `main()`. |
| `phoenix_master_backend.py` | All decoder + validator logic. `decode_model()` is the entry point. Per-schema parsers, per-line `validate_<line>_rules()`, `build_<line>_notes()`, `standard_product_configs` field maps, `TABLE_DATA`, `NOTE_BUILDERS`. |
| `inventory.py` | Parts List backend: `load_inventory()`, `save_inventory()`, `is_admin_password()`, `inventory_json_path()`. Cache at `%APPDATA%`. |
| `paths.py` | **Wave 8a B2 facade** over `phoenix_commons.paths`. Binds tool-specific source-tree base to commons' `resource_path`. |
| `updater.py` | **Wave 8a B3 hybrid facade** over `phoenix_commons.updater`. Preserves `LEGACY_EXE_NAMES` rename-tolerance + multi-fallback asset lookup. Exe-only payload per ADR-003. |
| `version.py` | One line: `__version__ = "1.1.1"`. Read by GUI / updater / build.bat. |
| `assets.py` | Auto-generated. Base64 blobs `ICO_B64` + `PNG_B64`. PyInstaller bundles via module scan (NOT `--add-data=`). Regenerate by hand-running a base64 script when the source PNG/ICO changes (snippet in §10). |
| `tests/test_validation.py` | **146 tests** across 13 product-line test classes + `ValidModelsTests` / `FailingModelsTests` for GUI fixtures. |
| `tests/test_updater.py` | 10 tests covering version parsing + PowerShell string escaping (preserved at module level in `updater.py` for this contract). |

### Repo-root docs + config

| File | Purpose |
|---|---|
| `CLAUDE.md` | **Canonical operator orientation.** Read first. |
| `CHANGELOG.md` | Formal Keep-a-Changelog file. |
| `README.md` / `GIT_SETUP.md` / `CONTRIBUTING.md` / `SECURITY.md` / `CODE_OF_CONDUCT.md` | Standard repo metadata. |
| `phoenix_style.qss` | Phoenix Controls dark navy QSS. **Single source of truth for visual rules.** Code uses `objectName` + dynamic properties only — never inline `setStyleSheet`. |
| `Transparent_red.png` | Watermark logo (must have real alpha channel — source: `C:\Users\justing\PycharmProjects\Design Items\colors\red.png`). |
| `Normal_red.ico` | App icon. |
| `build.bat` | Build pipeline (PyInstaller → Inno Setup → 2 zips). Hardened at Wave 8a B6 with Python 3.12 soft-warn + commons preflight + Step 0 full cleanup + `--noupx` + `--collect-all=phoenix_commons` + stdlib excludes. Signing dispatched through `:sign_exe` / `:sign_installer` subroutines to dodge cmd's nested-IF paren parser. |
| `installer.iss` | Inno Setup script. **AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}` is a hard-do-not-change rule** (upgrade-detection identity). |
| `requirements.txt` / `requirements-dev.txt` | Added Wave 8a B1. `build.bat` does NOT install from these — operator step. |
| `commons/` | `phoenix-commons` submodule. **Fresh clones / worktrees need `git submodule update --init` + `pip install -e ./commons`.** |
| `.github/workflows/test.yml` | Pre-existing CI — Linux, Python matrix 3.10/3.11/3.12. **Intentionally preserved alongside ci.yml.** |
| `.github/workflows/ci.yml` | Wave 8a B1 family-standard CI — Windows, Python 3.12, `submodules: recursive`. |

---

## 4. Product-line architecture (the decoder)

PMT decodes **13 product lines** across **6 schemas**.

### Schemas

| Schema | Format | Used by |
|---|---|---|
| `valve` | `[3-prefix][C][B][SS][P]-[D][C][C][O][F]-[proto?]-[opts...]` | CSCP, Celeris II, Theris, Theris FLEX, Traccel, Venturian, BxV-CV, BxV-Tiered, Analog |
| `pbc` | `PBC[series]-[function]` | PBC |
| `fhd500` | `FHD500-[opt]-[opt]…` | FHD500 |
| `fhd130` | `FHD[series]-[lang]-[opt]…` | Sentry FHD130 |
| `zps` | `ZPS[series][module-count]` (no dashes) | ZPS |
| `upgrade_kit` | `[fam]X[B][SS][P]-X[C][C]X[F]-[existing]-[opts...]` | C2U / TXU |

### The 13 product lines

| # | Code | Display name | Prefix(es) |
|---|---|---|---|
| 1 | `CSCP` | CSCP | PVE, PVS |
| 2 | `CELERIS_II` | Celeris II | MAV, EXV |
| 3 | `THERIS` | Theris | HSV, HEV |
| 4 | `THERIS_FLEX` | Theris FLEX | FSV, FEV |
| 5 | `TRACCEL` | Traccel | TSV, TEV |
| 6 | `VENTURIAN` | Venturian | VSV, VEV |
| 7 | `BASE_UPGRADEABLE_CV` | CV / Base Upgradeable | CSV, CEV, BSV\*, BEV\* |
| 8 | `BASE_UPGRADEABLE_TIERED` | Base Upgradeable (Tiered Solutions) | BSV\*, BEV\* |
| 9 | `ANALOG` | Analog | MAV, EXV (mode toggle) |
| 10 | `PBC` | Programmable BACnet Controller | PBC |
| 11 | `FHD500` | Fume Hood Display 500 (CSCP) | FHD |
| 12 | `FHD130` | Sentry Fume Hood Display (Celeris) | FHD |
| 13 | `ZPS` | Zone Presence Sensor | ZPS |
| 14 | `UPGRADE_KIT` | Valve Upgrade Kits | C2U, TXU |

\*BSV/BEV is disambiguated by control type: `Q/S/T` → Tiered, `C/B/F/H/I/L/Z` → CV.

### Code locations (all in `phoenix_master_backend.py`)

- **Schema dispatch:** `_PRODUCT_LINE_SCHEMA` dict + `_schema_for()`
- **Per-schema parsers:** `_parse_valve_schema()`, `_parse_pbc_schema()`, `_parse_fhd500_schema()`, `_parse_fhd130_schema()`, `_parse_zps_schema()`, `_parse_upgrade_kit_schema()`
- **Per-schema decoders:** `_decode_pbc()`, `_decode_fhd500()`, etc. — dispatched from `decode_model()`
- **Validators:** `validate_model()` dispatches to per-line `validate_<line>_rules()`
- **Notes builders:** `NOTE_BUILDERS` dict → `build_<line>_notes()` functions
- **Operating-range tables:** `TABLE_DATA[<line>]` (most lines share `SHARED_STANDARD_TABLE_DATA`)
- **Field-code maps:** `standard_product_configs[<line>]`

### Deliberately out of scope

- **Compact Cage Rack Valves** (`VALVE-CAGE-RACK`, PDS p.52) — ATS doesn't sell them.
- **Valve Reorientation Kits** (PDS p.53) — no model-number system; requires a Phoenix phone call.
- **Spare parts catalog** (PDS p.89+) — owned by the Inventory feature, not the decoder.

---

## 5. GUI structure

```
QMainWindow (ValveMasterMainWindow, showMaximized on launch)
└── WatermarkWidget (central — paints centered logo at 35 % opacity / 60 % scale)
    └── QVBoxLayout
        ├── HeaderCard (title + badges + CFM/FV Calc / Parts List / Test Models buttons)
        ├── QSplitter (WA_TranslucentBackground)
        │   ├── Left panel (fixed 380 px, WA_TranslucentBackground)
        │   │   ├── SectionCard "Input"
        │   │   └── SectionCard "Flow / Pressure Operating Table"
        │   ├── Center panel (WA_TranslucentBackground)
        │   │   └── SectionCard "Decoded Fields" → cards_container (QGridLayout)
        │   └── Right panel (WA_TranslucentBackground)
        │       └── SectionCard "Notes" (expanding) → QTextEdit (NoFrame)
        └── QStatusBar
```

**Watermark approach** mimics the Project Tracking Tool's `_BackgroundWidget`:
paint the logo directly via `QPainter.setOpacity` in `paintEvent`, centered,
60 % of `min(width, height)`. Panel containers are `WA_TranslucentBackground`
so the watermark shows through the gutters between cards.

---

## 6. Recent session context (May 2026)

This session shipped **v1.1.0** (rename + 9 product lines + Inventory tool +
design system + 156 tests) on 2026-05-10. While I was writing the prior
version of this handover, a parallel **Wave 8a commons-retrofit branch
landed v1.1.1** on 2026-05-30 (no functional changes — facade work + build
hardening).

### What this session shipped under v1.1.0

- Renamed Valve Master Tool → Phoenix Master Tool (binary, repo, branding)
- Phoenix Controls dark navy design system (`phoenix_style.qss`)
- Inventory / Parts List tool with SharePoint JSON sync + offline cache
- 9 new/split product lines: Theris FLEX, Venturian, BxV-CV, BxV-Tiered, PBC, FHD500, Sentry FHD130, ZPS, Upgrade Kits
- 156-test unittest suite
- Test Models fly-out dialog (replaced the cramped inline list panel)
- CFM table widened (left panel 380 px)
- PTT-style centered watermark (real-transparent PNG, 35 % opacity)
- Notes panel wrapped in expanding `SectionCard`
- App opens maximized
- `build.bat` paren-escape fix (cmd parser was crashing on `(x86)` and `(exe only)` inside nested IF blocks)

### Late-session bug + fix (v1.0.9 → v1.1.0 update path)

A user reported the auto-updater "restarts but doesn't update". Root cause:
v1.0.9's bundled updater hard-codes `valvemastertool.zip` (asset lookup) and
`ValveMasterTool.exe` (zip-entry name). The v1.1.0 release shipped
`PhoenixMasterTool.zip` containing `PhoenixMasterTool.exe`, so v1.0.9's
PowerShell extract step silently no-op'd and the `.bat` relaunched the
unchanged old exe.

**Two fixes shipped:**

1. **Server-side:** Uploaded `ValveMasterTool.zip` (v1.1.0 binary renamed) as
   an extra asset on the v1.1.0 release. v1.0.9's hard-coded lookup picks it
   up and the rename-tolerance kicks in.
2. **In-code:** Hardened `updater.py` — candidate-list zip lookup + overwrite
   running exe in place (commit `f6a8c48`). Then Wave 8a B3 (`828a99a`)
   refactored this into the **commons-backed hybrid facade**, preserving the
   `LEGACY_EXE_NAMES` rename-tolerance contract.

**Open follow-up:** `build.bat` does NOT auto-produce the legacy
`ValveMasterTool.zip`. Future releases need that asset uploaded by hand
(or `build.bat` extended to produce it) until you're confident no v1.0.x
users remain. Recipe:

```bash
cd dist
cp PhoenixMasterTool/PhoenixMasterTool.exe ValveMasterTool.exe
powershell -Command "Compress-Archive -Path ValveMasterTool.exe -DestinationPath ValveMasterTool.zip -Force"
gh release upload vX.Y.Z dist/ValveMasterTool.zip
```

---

## 7. Deferred / open items

Tracked in user memory (`project_deferred_items.md`); reproduced here for
agents that don't have memory access.

1. **CSCP stainless protocol limit** — Confirm whether protocols `504`/`505`
   are valid for stainless E/F constructions. PDS image was cropped; only
   `BMT`, `500`, `501` visible. Code currently allows all 5. To tighten:
   edit `validate_cscp_rules()` in `phoenix_master_backend.py`.

2. **Theris FLEX size 06 CFM data** — Operating-range CFM data missing for
   FLEX size 06. PDS p.24 only documents sizes 08 and 10. Add the row to
   `TABLE_DATA["THERIS_FLEX"][("M", "A")]["data"]` when the data arrives.

3. **QSettings rename one-time cosmetic** — Key changed `"ValveMasterTool"`
   → `"PhoenixMasterTool"`. Users see fresh defaults on first launch of
   v1.1.0. **Acknowledged, no migration planned.**

4. **SharePoint folder still named "Valve Master Tool"** — `inventory.py`
   path constant uses that legacy segment. Update if/when the SharePoint
   folder is ever renamed.

5. **`build.bat` doesn't auto-produce the legacy-name zip** — see §6.

---

## 8. User preferences (from memory — see §9 for files)

- User is a sales / PM engineer at ATS Inc., **not a software engineer**.
  Frame explanations at a product person's level, not a dev's.
- **Repo ownership** (`JustinGlave/phoenix-master-tool`) is intentional.
  Don't suggest migrating to an ATS GitHub org.
- **Skip distribution hardening.** Don't recommend code-signing certs,
  SHA256 update verification, or other security hardening for the
  auto-updater.
- **Defer open items during multi-phase work** — bundle into a list at the
  end, don't bullet-flag inline.
- **Authoritative ordering-guide facts** for Theris/Traccel are in
  `project_theris_traccel_data.md` in memory — load before claiming any
  fact about those lines.

---

## 9. Memory files (in `<claude-config>/memory/`)

`MEMORY.md` is the auto-loaded index. The individual files:

| File | Type | Contents |
|---|---|---|
| `feedback_repo_ownership.md` | feedback | Repo ownership is intentional. |
| `feedback_distribution_hardening_skip.md` | feedback | Skip code-signing + update-verification recommendations. |
| `feedback_defer_open_items.md` | feedback | Bundle deferred items at end of multi-phase work. |
| `project_theris_traccel_data.md` | project | Authoritative options / construction / WRE / structural-rule facts from MKT-0228 + MKT-0242. |
| `project_phoenix_product_data.md` | project | Authoritative reference for all 13 product lines, schema dispatch, code locations, deliberate exclusions. |
| `project_deferred_items.md` | project | The 5 deferred items in §7. |

---

## 10. Gotchas

- **`build.bat` is cmd-fragile.** Any `echo` line with literal `(...)` inside
  an `if (...) (...)` block crashes cmd's parser with "Windows was unexpected
  at this time". Escape with `^(` and `^)`, or push the work into a
  `call :label` subroutine. The signing block uses subroutines for exactly
  this reason.

- **`assets.py` is auto-generated.** If the watermark PNG or icon changes,
  regenerate the relevant block. There's no committed generator script —
  the snippet that's been used:

  ```python
  import base64, re, textwrap
  from pathlib import Path
  png = Path("Transparent_red.png").read_bytes()
  b64 = base64.b64encode(png).decode()
  chunks = textwrap.wrap(b64, 96)
  block = "PNG_B64 = (\n" + "\n".join(f'    "{c}"' for c in chunks) + "\n)\n"
  text = Path("assets.py").read_text()
  text = re.sub(r"PNG_B64\s*=\s*\(.*?\n\)\n", block, text, flags=re.DOTALL)
  Path("assets.py").write_text(text)
  ```

- **The test suite is fast (< 10 ms for 156 tests)** — pure Python, no GUI.
  Always run before committing: `python -m unittest discover -s tests`.

- **The GUI cannot be tested via tests.** Smoke-launch with
  `.venv\Scripts\python.exe phoenix_master_pyside6.py` and verify
  visually. Offscreen render for programmatic screenshot:

  ```python
  os.environ["QT_QPA_PLATFORM"] = "offscreen"
  app = QApplication(sys.argv)
  w = ValveMasterMainWindow()
  w.resize(1600, 900); w.show()
  app.processEvents(); app.processEvents()
  w.grab().save("smoke.png")
  ```

- **`Transparent_red.png`** has historically been mis-shipped with a solid
  black background (no alpha channel). The correct source is at
  `C:\Users\justing\PycharmProjects\Design Items\colors\red.png`. If the
  watermark ever looks dark / muddy again, that's the first thing to check.

- **`commons/` is a git submodule.** Fresh worktrees / clones need
  `git submodule update --init` + `pip install -e ./commons`. CI's `ci.yml`
  uses `submodules: recursive` checkout.

- **AppId GUID `{A7F3C2D1-9B4E-4F6A-8C3D-1E5B7A9F2C4D}`** in `installer.iss`
  is a hard-do-not-change rule — Inno Setup uses it for upgrade detection.

- **Updater payload is exe-only** per ADR-003. The zip contains only
  `PhoenixMasterTool.exe`, no `_internal/` folder. commons' validator is
  called with `expected_internal=False`.

---

## 11. Quick-start: typical change recipes

### Adding a validation rule

1. `phoenix_master_backend.py` → find `validate_<line>_rules()`.
2. Append a check; push to `issues`:
   `{"field": "<field-key>", "message": "<user-facing reason>"}`.
3. Add a test in `tests/test_validation.py` under the matching
   `<Line>RulesTests` class.
4. `python -m unittest discover -s tests` until green.

### Adding a notes paragraph

1. `phoenix_master_backend.py` → find `build_<line>_notes()`.
2. Append a `(heading, body)` tuple to the returned list.

### Adding an operating-range row

1. `phoenix_master_backend.py` → find `TABLE_DATA["<LINE>"][(pressure, diffuser)]`.
2. Append `(size, single_cfm, dual_cfm, pressure_drop)`.

### Bumping the version + releasing

Run `/ship`. The skill drives compile, test, version bump, commit, build,
release, and asset upload. **Don't forget to manually upload the legacy
`ValveMasterTool.zip`** (see §6) until that's automated in `build.bat`.
