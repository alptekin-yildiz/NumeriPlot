# NumeriPlot Support

This guide covers safe first-line troubleshooting for NumeriPlot users. For a
Turkish version, see [`SUPPORT_TR.md`](SUPPORT_TR.md).

NumeriPlot 0.1.0 is a Public Beta. Keep the original data and independent
backups of important project files, and independently verify numerical results.

## Before troubleshooting

Record the following information before asking for help:

- the NumeriPlot version or commit;
- whether you installed the macOS ZIP or run from source;
- the operating system and version, plus the hardware architecture;
- the exact steps, expected result, and actual result; and
- the smallest synthetic input that reproduces the problem.

Never publish private research data, student or patient information,
credentials, personal paths, or an unredacted log.

## Installation and startup

### macOS ZIP

Official ZIP instructions apply after a NumeriPlot release is published. Check
that the ZIP came from the official GitHub Release page and compare its full
SHA-256 checksum with the published `.sha256` file before opening it.

The first Public Beta is planned to be unsigned and not notarized. Follow the
Gatekeeper steps in [`README.md`](README.md), including Control-clicking the app
and choosing **Open**. Do not routinely remove quarantine attributes. Do not
bypass a warning that says the app is damaged or contains malware.

### Source checkout

NumeriPlot requires Python 3.11 or newer. From the repository root, run:

```bash
bash setup.sh
source venv/bin/activate
python3 main.py
```

If setup fails, confirm the Python version with `python3 --version`, check that
the initial dependency download has internet access, and keep the complete
error message. Before sharing it, remove credentials and personal paths.

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
