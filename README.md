# NumeriPlot

**Scientific Plotting, Data Analysis and Curve Fitting**

NumeriPlot is a free and open-source desktop application for scientific
plotting, data processing, and curve fitting, designed primarily for students
and researchers.

## First time here?

**[Install and use on Mac →](docs/SOURCE_INSTALL.md)** · [Türkçe kurulum →](docs/SOURCE_INSTALL_TR.md)

No coding or application build is required. Follow the guide to download
the source and complete the one-time setup. Afterwards, **double-click
`NumeriPlot.command` in Finder** to open the desktop interface. Keep the
launcher inside the project folder.

> **Public Beta notice:** NumeriPlot 0.1.1 is a Public Beta.
> Version 0.1.1 is distributed as source code, without a prebuilt Mac ZIP.
> Interfaces, workflows, and the project-file format may still
> change. Independently verify numerical results before using them in research,
> teaching, or reports.

NumeriPlot is an independent academic software project maintained by Alptekin
YILDIZ. Istanbul Technical University is listed only as the developer's
academic affiliation; it is not the owner, publisher, sponsor, or support
provider of the project.

Türkçe özet için [README_TR.md](README_TR.md) dosyasına bakın.

## Current capabilities

- CSV and Excel data import with editable data tables
- Role-based X, Y, secondary-Y, X-error, and Y-error assignment
- Line, scatter, and grouped bar plots with configurable axes and legends
- Built-in curve-fitting models and fit-range controls
- Peak finding and common data-processing operations
- Project save/load with explicit schema validation
- PNG, PDF, SVG, table, Python script, and notebook export paths
- Turkish and English user interfaces

## Illustrated user guide

[Read the guide online](https://alptekin-yildiz.github.io/NumeriPlot/en.html).

The offline HTML guide covers panels, menus, dropdowns, plot settings, fitting,
and exports with real interface screenshots. Download the repository, then open
[`docs/guide/en.html`](docs/guide/en.html) in a browser; no server is required.
Keep the `docs/guide` folder together. [Türkçe](docs/guide/index.html).

## Screenshots

The screenshots below were captured from the real NumeriPlot interface using
only the tracked, reproducible synthetic Gaussian example.

![NumeriPlot plot workspace showing synthetic Gaussian observations, error bars, and a fitted curve](assets/screenshots/numeriplot-overview.png)

![NumeriPlot analysis report showing fit parameters and synthetic residuals](assets/screenshots/numeriplot-fit-analysis.png)

## Synthetic examples

The [`examples/`](examples/) directory contains three deterministic synthetic
CSV datasets and a ready-to-open NumeriPlot project:

- noisy linear data;
- a Gaussian peak with a saved Gaussian fit and residual statistics; and
- single-exponential saturation data.

No research, student, patient, or personal data is included. See
[`examples/README.md`](examples/README.md) for the formulas, parameters, and
fixed random seed. Regenerate the data and project from the repository root:

```bash
python3 examples/generate_examples.py
```

The example project can be opened with **File → Open Project…**. Maintainers
can reproduce the screenshots from that project with:

```bash
QT_QPA_PLATFORM=offscreen python3 examples/capture_screenshots.py
```

## Status and platforms

**0.1.1 Public Beta is distributed as source code.** No
prebuilt 0.1.1 Mac application ZIP is included. Users install dependencies on
their own computer and run the normal desktop interface from source.
Project schema remains **1.0**.

| Environment | Current validation |
| --- | --- |
| Apple Silicon, macOS 27.0.1, Python 3.11.1 | Source workflow and automated tests checked locally; see the documented SciPy workaround |
| Other macOS versions or Python versions | Not independently validated by this check |
| Intel Mac, Windows, Linux | No equivalent source or packaged-release validation is claimed |

The historical [0.1.0 pre-release](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.1.0)
contains an older binary. It does not include the 0.1.1 fixes and is not the
installation route described below. Existing release assets have not been removed.

## Run from source

Start with the [step-by-step Mac installation guide](docs/SOURCE_INSTALL.md)
([Türkçe](docs/SOURCE_INSTALL_TR.md)). It explains installing Python, downloading
source without Git, first setup, daily launch, troubleshooting, and updates.
No `.app` build is required for everyday use.

With Python 3.11 installed, Git users can run the following commands one at a
time. Stop on errors; use the guide's troubleshooting instructions:

```bash
git clone https://github.com/alptekin-yildiz/NumeriPlot.git
cd NumeriPlot
python3.11 -m venv venv
source venv/bin/activate
bash setup.sh
python3 main.py
```

For later launches, enter the same source folder and run:

```bash
./venv/bin/python main.py
```

For contributors, install development tools into the same environment and
run the full checks. Apply the guide's SciPy workaround first if required:

```bash
source venv/bin/activate
bash setup.sh --dev
bash release_check.sh
```

## Install the macOS ZIP

**Historical 0.1.0 instructions only.** For 0.1.1 use the source guide above.

These instructions apply to the official `v0.1.0` pre-release assets on the
[NumeriPlot GitHub Releases page](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.1.0):

1. Download `NumeriPlot_v0.1.0_macOS.zip` and its `.sha256` file only from the
   official NumeriPlot GitHub Release page.
2. In Terminal, calculate the downloaded ZIP's checksum:

   ```bash
   shasum -a 256 NumeriPlot_v0.1.0_macOS.zip
   ```

   Compare the complete result with the published checksum before opening the
   ZIP.
3. Double-click the ZIP and move `NumeriPlot.app` to `Applications`.
4. Control-click or right-click `NumeriPlot.app`, choose **Open**, and review
   the macOS warning before deciding whether to continue.

### Gatekeeper and the unsigned beta

The public beta build has no Apple Developer ID signature and is not
notarized. macOS therefore cannot identify the developer or confirm that Apple
has checked the application for malicious software.

If macOS still blocks the app after you try to open it, first confirm that it
came from the official release page and that its checksum matches. If you then
choose to proceed, open **System Settings → Privacy & Security**, find the
blocked-app message under **Security**, choose **Open Anyway**, and review the
confirmation dialog. Apple documents this exception process in
[Open a Mac app from an unknown developer](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unknown-developer-mh40616/mac).

Do not bypass a warning that says the application is damaged or contains
malware. Do not use a quarantine-removal command as a routine installation
step.

## First workflow

1. Choose **File → Load Data…** and select a CSV, TXT, XLSX, or XLS file.
2. Review delimiter, encoding, header, skipped-row, and column-type choices in
   the import dialog, then import the table.
3. Open the **Data Table** tab. Assign column roles from a header's context
   menu, or apply a role template. A typical table uses one **X** column and
   one or more **Y Left** columns. A Y-only dataset can use automatic `1..n` X
   values.
4. Choose a plot type and select **Add Plot**. Use the series list and Plot
   settings to adjust style, axes, legend, layout, and labels.
5. To fit a curve, select a plotted series, choose a model under
   **Analysis & Fit**, select **Fit**, and review the parameters, goodness-of-fit
   values, and residuals.
6. Save the working project with **File → Save Project**. Export the figure,
   table, Python script, or notebook separately when needed.

When X is automatic, missing or nonnumeric Y entries are removed and the
remaining observations are numbered consecutively from 1. Supply an explicit
X column to preserve measurement times or gaps between observations.

Fits are unweighted: displayed error bars do not enter the fit calculation.
Initial parameter values must be finite numbers. Infinite X/Y values and
invalid model results are rejected; for constant Y data, R² is undefined and
is reported as such. A parameter-uncertainty warning means that a returned
curve still needs careful review; convergence alone does not validate a model.

## Data and project files

NumeriPlot imports `.csv`, `.txt`, `.xlsx`, and `.xls` data. Image exports use
PNG, PDF, or SVG; table exports use CSV or XLSX. Python and notebook exports
use `.py` and `.ipynb`.

A NumeriPlot project is a JSON file containing an embedded copy of the current
table together with plot series, fit results, text items, panel layout, and
display settings. Project JSON is an application format, not a stable public
data-exchange API. Keep the original data file and independent backups of
important projects, especially during the Public Beta.

Newly saved projects use the top-level `"schema_version": "1.0"` field.
Files with an unsupported or missing schema identifier are rejected instead of
being interpreted silently.

Loading a new data file replaces the current table and clears the current
plots, fits, and text items. Save the current project first if you may need it
again. Do not edit project JSON manually unless you understand the schema and
have a backup.

## Data, privacy, and logs

NumeriPlot processes data locally. It contains no telemetry, user tracking, or
automatic update checks. On macOS, diagnostic logs are written locally to:

```text
~/Library/Logs/NumeriPlot/numeriplot.log
```

Logs are not uploaded automatically. Before sharing a log or project file,
remove private research data, personal paths, credentials, and other sensitive
information.

## Scientific responsibility

NumeriPlot is provided without warranty. Fit parameters and other numerical
results depend on the data quality, model, initial values, constraints, and
selected range. Users are responsible for validating results independently.
The software is not validated for safety-critical, clinical, regulatory, or
certification calculations.

## Development process and AI assistance

NumeriPlot has been developed with substantial assistance from AI coding
agents, including OpenAI Codex, in implementation, testing, documentation, and
release preparation. The human maintainer directs the project, reviews and
accepts release-facing changes, and remains responsible for licensing,
releases, and scientific claims. AI assistance is not evidence of scientific
correctness; numerical results must still be independently verified.

NumeriPlot itself does not use AI services at runtime and does not send user
data to AI providers. Its local data and log behavior is described in
[Data, privacy, and logs](#data-privacy-and-logs).

## Citation

If NumeriPlot contributes to a publication, thesis, report, or teaching
material, please cite the software using the metadata in
[`CITATION.cff`](CITATION.cff). Citation is strongly appreciated but is not an
additional license condition.

## Contributing and support

See [`SUPPORT.md`](SUPPORT.md) for troubleshooting and
[`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing a change. Once the public
repository is opened, normal questions and bug reports will use
[GitHub Issues](https://github.com/alptekin-yildiz/NumeriPlot/issues).
Security reports or reports containing sensitive data must follow
[`SECURITY.md`](SECURITY.md) instead of being posted publicly.

## License

NumeriPlot is licensed under the GNU General Public License v3.0 only. See
[`LICENSE`](LICENSE). Third-party components remain under their respective
licenses; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
