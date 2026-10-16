# NumeriPlot repository instructions for AI agents

These instructions apply to AI agents answering user questions or changing
files anywhere in this repository. Keep public explanations focused on the
current NumeriPlot identity, version 0.1.1, and project schema 1.0.

## Sources of truth

- Use [`README.md`](README.md) and [`README_TR.md`](README_TR.md) for product,
  installation, workflow, platform, and scientific-responsibility claims.
- Use [`SUPPORT.md`](SUPPORT.md) and [`SUPPORT_TR.md`](SUPPORT_TR.md) for safe
  troubleshooting and issue routing.
- Use [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution, DCO, and AI-use
  rules.
- Use [`SECURITY.md`](SECURITY.md) for private vulnerability and sensitive-data
  reports.
- Treat code and tests as authoritative for behavior. Do not invent features,
  platform support, release availability, or scientific guarantees.

## User support workflow

1. Reply in the user's language when it is Turkish or English.
2. Establish the NumeriPlot version, operating system and architecture, and
   whether the user installed a ZIP or runs from source.
3. Classify the question as installation, import, plotting, fitting, project
   files, export, privacy, or development.
4. Follow the relevant support guide and give short, numbered, reversible
   steps. Explain terminal commands before asking a non-developer to run them.
5. Ask for exact steps, expected and actual behavior, and the smallest synthetic
   reproducer. Never request private research, student, patient, or credential
   data.
6. For logs, point to `~/Library/Logs/NumeriPlot/numeriplot.log` and require
   personal paths and sensitive content to be removed before sharing.
7. Route ordinary bugs, feature requests, and fit model proposals through the
   matching issue template. Route vulnerabilities and sensitive reports through
   `SECURITY.md`, never a public issue.

For an unsigned macOS build, recommend only the documented checksum and
Gatekeeper workflow. Do not recommend routine quarantine removal, and never
advise bypassing a damaged-app or malware warning.

When discussing a fit, distinguish numerical convergence from scientific
validity. Ask about the model, data domain, fit range, initial values, bounds,
units, residuals, and an independently checkable expected result. Never present
NumeriPlot as validated for safety-critical, clinical, regulatory, or
certification calculations.

## Repository map

- `main.py`: application entry point.
- `src/ui/`: user interface and interaction workflows.
- `src/analysis/`: data management, fitting helpers, and text utilities.
- `src/plotting/`: Matplotlib canvas and plot behavior.
- `src/project_schema.py`: schema 1.0 validation and project loading policy.
- `src/version.py`: canonical product identity and version strings.
- `models/`: fit model implementations.
- `lang/`: Turkish and English UI resources.
- `tests/`: unit, integration, GUI workflow, and public-metadata tests.
- `examples/`: deterministic synthetic datasets and reproducible screenshots.
- `.github/`: CI and contributor-facing templates.

## Development workflow

Before changing code, inspect the current Git status and the relevant module and
tests. Preserve unrelated user changes and keep the patch focused.

Set up the pinned development environment with:

```bash
bash setup.sh --dev
source venv/bin/activate
```

Run a focused test while iterating, then run the complete release gate before
declaring work complete:

```bash
python3 -m pytest -q tests/path_to_relevant_test.py
bash release_check.sh
```

Do not weaken, skip, or delete a failing test merely to make a change pass.
Explain dependency changes and avoid adding a dependency when the standard
library or an existing pinned package is sufficient.

For UI text, update Turkish and English resources together. For project files,
preserve schema 1.0 validation, safe rejection of unsupported schemas, and
non-destructive save behavior. Keep public documentation centered on current
NumeriPlot behavior.

## Numerical integrity

- Add tests for every numerical behavior change.
- Use synthetic or otherwise safely redistributable fixtures.
- State the independently calculated expected result and numerical tolerance.
- Cover invalid domains, non-finite values, bounds, and convergence failures
  when relevant.
- Do not infer correctness from a successful optimizer return alone.
- Do not change fit formulas, parameter meanings, defaults, or bounds without a
  documented scientific basis and focused validation.

## Privacy and security

- Never add real research, student, patient, credential, or other private data
  to code, fixtures, examples, screenshots, issues, or logs.
- Remove personal filesystem paths and metadata from tracked artifacts.
- Use deterministic synthetic data for examples and reproductions.
- Do not expose secrets through commands, test output, or generated files.
- Do not post vulnerability details publicly; follow `SECURITY.md`.
- Treat third-party and AI-produced code as untrusted until its license,
  behavior, tests, and security implications have been reviewed.

## AI-assisted changes

AI assistance is allowed, but the human contributor remains responsible for
the submitted change. Disclose material AI use in the pull request, including
the tools, scope, human review, and validation performed. Do not paste private
prompts or sensitive context into issues or pull requests.

An AI tool cannot provide the human DCO certification. The contributor must
understand the change, have the right to submit it under `GPL-3.0-only`, and add
their own `Signed-off-by` line.

## Actions requiring explicit maintainer approval

- Do not push commits or branches to GitHub.
- Do not create or publish a release.
- Do not change repository visibility, Issues, security, branch protection, or
  other remote settings.
- Do not add a major feature, fit model, dependency, or project-format change
  unless the task explicitly authorizes it.
- Do not publish local maintainer material, private data, credentials, or
  machine-specific paths.

Approval for one action does not imply approval for another.

## Completion evidence

Before handing off a change, report:

- files changed and the user-visible effect;
- focused test results and the full `bash release_check.sh` result;
- remaining warnings, risks, or remote-only steps;
- whether the worktree is clean or what changes remain; and
- confirmation that no push or release occurred unless explicitly authorized.
