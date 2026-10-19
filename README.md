# NumeriPlot

**Scientific Plotting, Data Analysis and Curve Fitting**

NumeriPlot is a free and open-source desktop application for scientific
plotting, data processing, and curve fitting, designed primarily for students
and researchers.

## First time here?

**[Install on Mac →](docs/MACOS_INSTALL.md)** · [Türkçe kurulum →](docs/MACOS_INSTALL_TR.md)

1. Download `NumeriPlot-0.2.0-macOS-AppleSilicon.dmg` from the
   [0.2.0 release page](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.2.0).
2. Open it and drag **NumeriPlot** onto **Applications**.
3. Open NumeriPlot from Applications. The first time, allow it once under
   **System Settings → Privacy & Security → Open Anyway**; the guide shows
   every step.

The app needs an Apple Silicon Mac with macOS 14 or later. No Python or
Terminal is required. Other computers can
[run NumeriPlot from source](docs/SOURCE_INSTALL.md).

> **Public Beta notice:** NumeriPlot 0.2.0 Public Beta is the first release
> distributed as a standalone Mac app. Interfaces, workflows, and the
> project-file format may still change. Independently verify numerical
> results before using them in research, teaching, or reports.

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

The app opens the example project with **File → Open Example Project**; from
a source checkout, **File → Open Project…** opens it as well. Maintainers can
reproduce the screenshots from that project with:

```bash
QT_QPA_PLATFORM=offscreen python3 examples/capture_screenshots.py
```

## Status and platforms

**0.2.0 Public Beta is distributed as a Mac app for Apple Silicon.** The disk
image contains a self-contained `NumeriPlot.app`; Python is not required.
The app has no paid Apple Developer ID signature, so macOS asks for permission
once at first launch. Project schema remains **1.0**.

| Environment | Current validation |
| --- | --- |
| Apple Silicon, macOS 27.0.1 | App built, installed from the disk image, and checked locally |
| Apple Silicon, macOS 14–26 | Supported by the bundled libraries (minimum macOS 14); not tested on these versions |
| Intel Mac, Windows, Linux | No app is provided; running from source is possible but not validated |

## Run from source

On an Apple Silicon Mac, the app above is the recommended route. Running from
source is meant for other computers (Intel Mac, Windows, Linux; at your own
effort) and for development. The [source installation guide](docs/SOURCE_INSTALL.md)
([Türkçe](docs/SOURCE_INSTALL_TR.md)) explains installing Python, downloading
source without Git, first setup, launching, troubleshooting, and updates.

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

## Install the macOS app

Requirements: an Apple Silicon Mac (M1 or later) with macOS 14 or later. The
[installation guide](docs/MACOS_INSTALL.md) explains each step in detail.

1. Download `NumeriPlot-0.2.0-macOS-AppleSilicon.dmg` only from the official
   [0.2.0 release page](https://github.com/alptekin-yildiz/NumeriPlot/releases/tag/v0.2.0).
2. Optional: download its `.sha256` file too and check the disk image in
   Terminal. The result must say `OK`:

   ```bash
   cd ~/Downloads
   shasum -a 256 -c NumeriPlot-0.2.0-macOS-AppleSilicon.dmg.sha256
   ```

3. Double-click the disk image and drag **NumeriPlot** onto **Applications**.
4. Open NumeriPlot from **Applications** and follow the next section the first
   time. The app opens within a few seconds.

### Gatekeeper and the unsigned beta

NumeriPlot is free and has no paid Apple Developer ID signature or
notarization. macOS therefore cannot identify the developer and stops the
first launch with a **“NumeriPlot” Not Opened** message. Allow it once:

1. In the message, choose **Done**. The highlighted blue button is
   **Move to Trash**; do not choose it.
2. Open **System Settings → Privacy & Security**, scroll to **Security**, and
   choose **Open Anyway** next to the message about NumeriPlot. The button
   appears for about an hour after the blocked attempt.
3. In the **Open “NumeriPlot”?** message, choose **Open Anyway** (again, not
   **Move to Trash**), then confirm with Touch ID or your Mac password.

NumeriPlot then opens normally. Apple documents this exception process in
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

The app also keeps a Matplotlib font cache in `~/Library/Caches/NumeriPlot`,
which may be deleted at any time.

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
agents, including OpenAI Codex and Anthropic Claude Code, in implementation,
testing, documentation, and release preparation. The human maintainer directs the project, reviews and
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
licenses; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). The Mac app
bundles Qt (LGPL v3), PyQt6 (GPL v3), and other open-source components without
modification. Their full license texts are in the app under
**File → About NumeriPlot → Third-Party Licenses**, and the source archives
of the GPL/LGPL components are published with each release.
