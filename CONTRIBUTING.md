# Contributing to NumeriPlot

Thank you for considering a contribution. NumeriPlot is an independent
academic software project with a small maintainer capacity, so focused and
well-tested changes are the easiest to review.

## Before starting

- Small bug fixes, tests, translations, and documentation improvements may be
  submitted directly as pull requests.
- Open an issue before starting a major feature, new fit model, project-format
  change, or architectural refactor.
- Do not include real research, student, patient, or other private data. Use
  synthetic fixtures and examples.
- Do not report security issues or sensitive data in a public issue; follow
  [`SECURITY.md`](SECURITY.md).

## Development setup

```bash
bash setup.sh --dev
source venv/bin/activate
bash release_check.sh
```

Runtime packages are pinned in `requirements.txt`. Test, lint, and packaging
tools are pinned separately in `requirements-dev.txt`. The release gate uses
the active environment's Python for every check.

Keep changes narrow. Preserve compatibility with supported project files and
keep Turkish and English translation keys synchronized. Numerical changes must
include tests with stated tolerances and independently checkable expected
results.

## Fit-model proposals

A new fit model proposal should provide:

- the equation and parameter names;
- the physical or mathematical meaning of each parameter;
- the valid data domain;
- initial-value and bound guidance;
- a scientific reference;
- synthetic or otherwise redistributable validation data; and
- expected results with numerical tolerances.

## Pull requests

A pull request should explain the problem, the chosen solution, test evidence,
and any user-visible or compatibility impact. Update both language resources
when UI text changes. Do not mix unrelated formatting or refactoring into the
same change.

## AI-assisted contributions

AI coding tools may be used for implementation, tests, documentation, or review,
but the human contributor remains responsible for every submitted change. The
contributor must understand the change, be able to explain it, review the full
diff, and validate the result rather than relying on an AI response alone.

Disclose material AI assistance in the pull request. Name the tool or tool
category, describe the affected scope, and summarize the human review and tests
performed. Routine completion of a few tokens does not need a detailed report.
Do not paste private prompts, credentials, unpublished research content,
student or patient information, or other sensitive data into a public issue or
pull request.

Check AI-assisted output for correctness, security, public-code similarity, and
license compatibility. AI assistance does not establish scientific validity or
the right to submit third-party material. Only the human contributor can make
the DCO certification; the `Signed-off-by` line is the contributor's own. A
maintainer may explicitly ask an AI agent to add it to a commit they have
authorized. Do not list AI tools as authors or co-authors, for example in
`Co-Authored-By` trailers; describe the assistance instead.

Contributors retain copyright in their contributions and agree to provide them
under the repository's `GPL-3.0-only` license. NumeriPlot uses a Developer
Certificate of Origin (DCO) sign-off instead of a contributor license
agreement. Sign each commit with:

```bash
git commit -s
```

The resulting `Signed-off-by` line certifies that you have the right to submit
the contribution under the project's license. See
[developercertificate.org](https://developercertificate.org/) for the full DCO
text.

By participating, you agree to follow [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
