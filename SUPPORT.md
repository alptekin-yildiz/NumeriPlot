# NumeriPlot Support

This guide covers safe first-line troubleshooting for NumeriPlot users. For a
Turkish version, see [`SUPPORT_TR.md`](SUPPORT_TR.md).

NumeriPlot 0.2.x is a Public Beta. Keep the original data and independent
backups of important project files, and independently verify numerical results.

## Before troubleshooting

Record the following information before asking for help:

- the NumeriPlot version or commit;
- whether you installed the macOS app or run from source;
- the operating system and version, plus the hardware architecture;
- the exact steps, expected result, and actual result; and
- the smallest synthetic input that reproduces the problem.

Never publish private research data, student or patient information,
credentials, personal paths, or an unredacted log.

## Installation and startup

### macOS app

Follow the [Mac installation guide](docs/MACOS_INSTALL.md). The app requires
an Apple Silicon Mac with macOS 14 or later. Download the disk image only from
the official GitHub Release page; optionally compare its SHA-256 checksum with
the published `.sha256` file before opening it.

The app is unsigned and not notarized. At first launch macOS shows
**“NumeriPlot” Not Opened**: choose **Done** (the blue default button is
**Move to Trash**), then **System Settings → Privacy & Security → Open Anyway**,
**Open Anyway** again in **Open “NumeriPlot”?**, and Touch ID or the password.
The button appears for about an hour after the blocked attempt. Do not routinely remove
quarantine attributes. Do not bypass a warning that says the app is damaged or
contains malware.

- The app opens within a few seconds. It keeps a Matplotlib font cache in
  `~/Library/Caches/NumeriPlot`, which may be deleted at any time. Clicking
  the icon repeatedly while it opens can start a second copy.
- Copy the app to **Applications** before opening it, rather than running it
  from the disk image window.
- Intel Macs and macOS 13 or earlier are not supported by the app; use the
  source route below.

### Source checkout

For other computers and for development, follow the
[source installation guide](docs/SOURCE_INSTALL.md). It covers Python 3.11,
launching, and the specific SciPy load failure observed on the validation
host. Newer Python versions are not automatically validated.

## Data import

NumeriPlot imports CSV, TXT, XLSX, and XLS data. If a table is not interpreted
as expected, check:

- delimiter and text encoding;
- whether the file contains a header row;
- the number of rows skipped before import;
- decimal characters and numeric column types; and
- the selected worksheet for Excel files.

Try to reproduce the behavior with a few rows of synthetic data. Importing a
new data file replaces the current table and clears plots, fits, and text items,
so save the current project first when needed.

## Plotting and fitting

For a missing or unexpected plot, verify the X, Y Left, Y Right, X Error, and Y
Error column roles, then check the selected series, plot type, axes, and visible
ranges.

For a fit problem, record:

- the selected model and fit range;
- parameter initial values and bounds;
- parameter units and the valid data domain;
- the complete error message; and
- an independently calculated expected result with a numerical tolerance.

A fit that converges is not automatically scientifically valid. Inspect the
residuals, sensitivity to starting values and range, and whether the model is
appropriate for the data. NumeriPlot is not validated for safety-critical,
clinical, regulatory, or certification calculations.

## Project files

New NumeriPlot projects use the top-level `"schema_version": "1.0"` field. A
file with a missing or unsupported schema identifier is rejected rather than
interpreted silently.

Keep an independent backup before troubleshooting a valuable project. Do not
edit project JSON manually unless you understand the format. When reporting a
problem, prefer a minimal synthetic project that reproduces the behavior.

## Export

NumeriPlot exports figures as PNG, PDF, or SVG; tables as CSV or XLSX; and
reproducible code as Python or notebook files. If export fails, check:

- that the destination directory exists and is writable;
- that the filename uses the expected extension;
- whether the destination file is open in another application; and
- whether the same problem occurs with a simple synthetic project.

Inspect generated scripts and notebooks before using them in research. An
exported artifact is not a substitute for independent numerical validation.

## Logs and privacy

On macOS, diagnostic logs are stored locally at:

```text
~/Library/Logs/NumeriPlot/numeriplot.log
```

NumeriPlot does not upload logs automatically. Before sharing an excerpt,
remove personal paths, filenames, research content, credentials, and any other
sensitive information. Share only the smallest section needed to understand
the problem.

## Where to ask for help

After the public repository opens:

- use the [bug report](https://github.com/alptekin-yildiz/NumeriPlot/issues/new/choose)
  path for reproducible software problems;
- use the same issue chooser for a focused feature request or documented fit
  model proposal; and
- follow [`SECURITY.md`](SECURITY.md) for a vulnerability, privacy issue, or
  report containing sensitive details.

Do not open a public issue for security-sensitive information. This independent
academic project has limited maintainer capacity and does not guarantee a
response time.

Logs rotate across at most four files of 2 MiB each. In a source checkout,
setup check failures are recorded in `venv/runtime-check.log`; remove personal
paths and sensitive content before sharing.
