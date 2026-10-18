# Changelog

## 0.2.0 - 2026-10-18 (Public Beta)

- Distribute NumeriPlot as a standalone Mac app for Apple Silicon (macOS 14 or
  later): download one disk image, drag the app to Applications, and open it
  with its own icon. No Python installation is needed. The app is unsigned;
  macOS asks for permission once at first launch.
- Add a bilingual Mac installation guide with the first-launch steps; keep the
  source installation for other computers and for development.
- Open the packaged app in about two seconds, including the first launch: keep
  the Matplotlib font cache between launches and build it without the slow
  macOS `system_profiler` font query (previously 12–20 seconds per launch).
- Add **File → Open Example Project**, which opens the bundled synthetic
  example without making it the save target.
- Show Qt's notice and a **Third-Party Licenses** viewer in the About dialog.
  Ship the collected license notices inside the app and publish the source
  archives of its GPL/LGPL components with each release.
- Build the disk image with `build_macos.sh`, which now checks the SciPy wheel,
  collects the notices, verifies the bundle, and removes only its own outputs.
  Leave unused Qt parts (QtPdf, QtNetwork, extra image-format plugins) out of
  the app.
- Fix setup in paths containing spaces and non-ASCII characters.
- Reuse the existing virtual environment during setup without prior activation;
  prefer Python 3.11 for a new environment and explain unusable environments.
- Verify startup imports at setup time; automatically repair only the known
  SciPy 1.15.2 wheel error on macOS 27 / arm64 / Python 3.11, then recheck.
- Report startup exceptions without trying to create a dialog before Qt exists.
- Bound logs to four files of up to 2 MiB each and reduce console noise.
- Clarify launcher location errors and source-specific Gatekeeper instructions.

## 0.1.1 - 2026-10-16 (Public Beta)

- Distribute 0.1.1 as source code; no prebuilt Mac ZIP is planned. Add
  bilingual installation, daily-use, troubleshooting, and optional local-build guides.
- Highlight first-time setup in both READMEs and the web guide. Add a
  double-click Mac launcher for an installed source checkout, with setup and
  startup-failure guidance.
- Save projects atomically so a failed write preserves the previous file.
- Reject non-finite fit inputs, invalid initial parameters, and invalid model
  results; report R² as undefined for constant observations.
- Explain unweighted fitting and parameter-uncertainty warnings in both UI
  languages. Fit formulas and project schema 1.0 are unchanged.
- Add an illustrated Turkish/English offline and online user guide with
  18 sections, 52 synthetic-data screenshots, search, and image enlargement.
- Document automatic X numbering and fit limitations in both READMEs.
- Expand regression coverage for saving and fitting. Keep one Qt application
  alive across GUI test modules to avoid CI teardown crashes.
- Set the 0.1.1 Apple Silicon package minimum to macOS 14, matching its
  bundled native libraries; exclude local source bytecode caches from the app.

## 0.1.0 - 2026-08-31 (Public Beta)

- Prepared the NumeriPlot application identity for its first public beta.
- Added GPLv3 licensing, citation metadata, public project policies, and a
  documented third-party binary-license release gate.
- Expanded English and Turkish user documentation for installation, first use,
  project files, privacy, and unsigned macOS Gatekeeper handling.
- Added deterministic synthetic datasets, an example project, and reproducible
  screenshots captured from the real application interface.
- Split runtime and development dependencies, pinned release tooling, and made
  the release gate use one explicit Python environment.
- Introduced explicit project schema 1.0 and safe rejection of unknown schemas.
- Added a least-privilege macOS GitHub Actions release gate and expanded
  headless GUI, project workflow, data operation, settings, and export tests.
- Added bilingual troubleshooting guides, repository instructions for AI
  agents, and transparent AI-assisted contribution guidance.
- Fixed invalid fallback parameter names in exported Python scripts and
  notebooks when a saved fit's model source is unavailable.
- Added table multi-cell paste from clipboard with undo and live plot refresh.
- Improved save flow with direct overwrite on `Save` and explicit `Save As`.
- Added canvas-empty-space double-click shortcut to open Canvas settings.
- Added header context action to rename data columns safely with reference sync.
- Added new fit model: single exponential saturation (`ΔR/R0`).

- Data table is now the default opening tab in the right panel.
- Role-based plotting workflow was refined for faster curve creation.
- Plot settings axes layout was reorganized into clearer 3-row groups.
- Scientific/offset tick formatting controls were expanded and stabilized.
- Tick offset text now follows configured tick font size.
- Data-table row/column/cell edit flows were improved.
