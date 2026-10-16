# Changelog

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
