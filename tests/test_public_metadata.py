import re
from pathlib import Path

from src.version import MACOS_MINIMUM_VERSION, VERSION


ROOT = Path(__file__).resolve().parents[1]

# NumeriPlot release numbers: 0.2.0, 0.2.x, and v0.2.0 in links. The one-digit
# minor keeps dependency versions such as cycler 0.12.1 out of the check.
NUMERIPLOT_VERSION = re.compile(r"(?<![\w.])v?(0\.\d\.(?:\d+|x))(?!\d|\.\d)")

# Lines that may name another release, each with its reason.
OTHER_VERSION_ALLOWED = (
    # The guide says its screenshots come from the 0.1.0 source version.
    ("docs/guide/essentials.json", "0.1.0 kaynak sürümünden"),
    ("docs/guide/essentials.json", "0.1.0 source version"),
)


def test_required_public_release_documents_exist():
    required = {
        "README.md",
        "README_TR.md",
        "SUPPORT.md",
        "SUPPORT_TR.md",
        "AGENTS.md",
        "LICENSE",
        "CITATION.cff",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "THIRD_PARTY_NOTICES.md",
        "CHANGELOG.md",
        "licenses/LGPL-3.0-only.txt",
        "docs/MACOS_INSTALL.md",
        "docs/MACOS_INSTALL_TR.md",
    }

    missing = sorted(path for path in required if not (ROOT / path).is_file())
    assert not missing


def test_license_is_unmodified_gpl_v3_text():
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")

    assert "GNU GENERAL PUBLIC LICENSE" in license_text
    assert "Version 3, 29 June 2007" in license_text
    assert "changing it is not allowed" in license_text
    assert "END OF TERMS AND CONDITIONS" in license_text


def test_citation_metadata_uses_canonical_public_identity():
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")

    assert "cff-version: 1.2.0" in citation
    assert "title: NumeriPlot" in citation
    assert f"version: {VERSION}" in citation
    assert "license: GPL-3.0-only" in citation
    assert "repository-code: https://github.com/alptekin-yildiz/NumeriPlot" in citation


def test_mac_install_guides_show_existing_images_and_safe_first_launch():
    for name, minimum_images, labels in (
        ("docs/MACOS_INSTALL_TR.md", 5, ("Bitti", "Yine de Aç", "Çöp Sepeti'ne Taşı")),
        ("docs/MACOS_INSTALL.md", 1, ("Done", "Open Anyway", "Move to Trash")),
    ):
        guide = (ROOT / name).read_text(encoding="utf-8")
        images = re.findall(r"!\[[^\]]+\]\(([^)]+)\)", guide)
        assert len(images) >= minimum_images, name
        for image in images:
            assert (ROOT / "docs" / image).is_file(), (name, image)
        for label in labels:
            assert label in guide, (name, label)
        assert "xattr" in guide  # only as a warning not to use it


def test_packaged_app_includes_license_materials():
    spec = (ROOT / "NumeriPlot.spec").read_text(encoding="utf-8")

    assert "('LICENSE', '.')" in spec
    assert "('THIRD_PARTY_NOTICES.md', '.')" in spec
    assert "('licenses', 'licenses')" in spec


def test_readmes_cover_phase_4_user_guidance():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_tr = (ROOT / "README_TR.md").read_text(encoding="utf-8")

    for heading in (
        "## Screenshots",
        "## Install the macOS app",
        "### Gatekeeper and the unsigned beta",
        "## First workflow",
        "## Data and project files",
    ):
        assert heading in readme_en

    for heading in (
        "## Ekran görüntüleri",
        "## macOS uygulamasını kurma",
        "### Gatekeeper ve imzasız beta",
        "## İlk iş akışı",
        "## Veri ve proje dosyaları",
    ):
        assert heading in readme_tr

    apple_guidance = (
        "https://support.apple.com/guide/mac-help/"
        "open-a-mac-app-from-an-unknown-developer-mh40616/mac"
    )
    assert apple_guidance in readme_en
    assert apple_guidance in readme_tr


def test_github_community_templates_exist():
    required = {
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
        ".github/ISSUE_TEMPLATE/fit_model_proposal.md",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/pull_request_template.md",
    }

    missing = sorted(path for path in required if not (ROOT / path).is_file())
    assert not missing


def test_issue_templates_set_safe_and_actionable_expectations():
    issue_dir = ROOT / ".github" / "ISSUE_TEMPLATE"
    bug = (issue_dir / "bug_report.md").read_text(encoding="utf-8")
    feature = (issue_dir / "feature_request.md").read_text(encoding="utf-8")
    fit_model = (issue_dir / "fit_model_proposal.md").read_text(encoding="utf-8")
    chooser = (issue_dir / "config.yml").read_text(encoding="utf-8")

    for template in (bug, feature, fit_model):
        assert template.startswith("---\nname:")
        assert "about:" in template
        assert "SECURITY.md" in template
        assert "synthetic" in template.lower()

    for prompt in (
        "NumeriPlot version",
        "macOS version",
        "Steps to reproduce",
        "Expected behavior",
        "Actual behavior",
        "Sanitized log output",
    ):
        assert prompt in bug

    for prompt in ("Problem or use case", "Proposed workflow", "Alternatives"):
        assert prompt in feature

    for prompt in (
        "Equation",
        "Parameter names and physical meanings",
        "Valid data domain",
        "Initial values and bounds",
        "Scientific reference",
        "Validation data",
        "Expected tolerance",
    ):
        assert prompt in fit_model

    assert "blank_issues_enabled: false" in chooser
    assert "NumeriPlot/security/policy" in chooser


def test_pull_request_template_covers_release_and_contribution_rules():
    template = (ROOT / ".github" / "pull_request_template.md").read_text(
        encoding="utf-8"
    )

    for expectation in (
        "## Summary",
        "## Validation",
        "bash release_check.sh",
        "synthetic",
        "numerical tolerance",
        "Signed-off-by",
        "SECURITY.md",
    ):
        assert expectation in template


def test_support_guides_cover_common_user_workflows():
    support_en = (ROOT / "SUPPORT.md").read_text(encoding="utf-8")
    support_tr = (ROOT / "SUPPORT_TR.md").read_text(encoding="utf-8")

    for heading in (
        "## Installation and startup",
        "## Data import",
        "## Plotting and fitting",
        "## Project files",
        "## Export",
        "## Logs and privacy",
        "## Where to ask for help",
    ):
        assert heading in support_en

    for heading in (
        "## Kurulum ve başlatma",
        "## Veri içe aktarma",
        "## Grafik ve fit",
        "## Proje dosyaları",
        "## Dışa aktarma",
        "## Loglar ve gizlilik",
        "## Nereden yardım alınır?",
    ):
        assert heading in support_tr

    for guide in (support_en, support_tr):
        assert "numeriplot.log" in guide
        assert "SECURITY.md" in guide
        assert "synthetic" in guide.lower() or "sentetik" in guide.lower()


def test_agent_guidance_supports_users_and_development_safely():
    guidance = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for expectation in (
        "## User support workflow",
        "## Development workflow",
        "## Repository map",
        "## Numerical integrity",
        "## Privacy and security",
        "## Actions requiring explicit maintainer approval",
        "SUPPORT.md",
        "bash release_check.sh",
        "numerical tolerance",
        "synthetic",
        "Do not push",
    ):
        assert expectation in guidance


def test_public_guidance_discloses_ai_assistance_and_human_responsibility():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_tr = (ROOT / "README_TR.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    pull_request = (ROOT / ".github" / "pull_request_template.md").read_text(
        encoding="utf-8"
    )

    assert "## Development process and AI assistance" in readme_en
    assert "OpenAI Codex" in readme_en
    assert "does not use AI services at runtime" in readme_en
    assert "(SUPPORT.md)" in readme_en

    assert "## Geliştirme süreci ve AI desteği" in readme_tr
    assert "OpenAI Codex" in readme_tr
    assert "çalışma sırasında AI hizmetlerini kullanmaz" in readme_tr
    assert "(SUPPORT_TR.md)" in readme_tr

    for expectation in (
        "## AI-assisted contributions",
        "human contributor",
        "disclose",
        "sensitive data",
    ):
        assert expectation.casefold() in contributing.casefold()
    assert "DCO" in contributing

    assert "## AI assistance" in pull_request
    assert "human review" in pull_request


def test_public_documents_start_with_current_numeriplot_identity():
    public_documents = (
        "README.md",
        "README_TR.md",
        "SUPPORT.md",
        "SUPPORT_TR.md",
        "AGENTS.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
    )
    disallowed_history_terms = (
        "legacy",
        "legacy v2",
        "eski v2",
        "eski sürüm",
        "renamed the application",
    )

    for path in public_documents:
        content = (ROOT / path).read_text(encoding="utf-8").casefold()
        for term in disallowed_history_terms:
            assert term not in content, f"{path} contains {term!r}"


def _public_document_lines():
    """Yield (path, line number, line) for the tracked public documents.

    Local maintainer files listed in .gitignore are skipped, and so is the
    CHANGELOG history below the current release.
    """
    ignored = set((ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())
    paths = {
        *ROOT.glob("*.md"),
        ROOT / "CITATION.cff",
        ROOT / "NumeriPlot.command",
        *(ROOT / "docs").glob("*.md"),
        ROOT / "docs" / "guide" / "README.md",
        *(ROOT / "docs" / "guide").glob("*.json"),
        *(ROOT / ".github").rglob("*.md"),
        *(ROOT / "assets" / "dmg").glob("*.txt"),
    }
    for path in sorted(paths):
        name = path.relative_to(ROOT).as_posix()
        if name in ignored:
            continue
        text = path.read_text(encoding="utf-8")
        if name == "CHANGELOG.md":
            releases = [match.start() for match in re.finditer(r"(?m)^## \d", text)]
            text = text[: releases[1]] if len(releases) > 1 else text
        for number, line in enumerate(text.splitlines(), start=1):
            yield name, number, line


def _names_another_release_on_purpose(name, line):
    return any(name == path and part in line for path, part in OTHER_VERSION_ALLOWED)


def test_public_documents_name_only_the_current_version():
    series = VERSION.rsplit(".", 1)[0] + ".x"
    stale = [
        f"{name}:{number}: {found}"
        for name, number, line in _public_document_lines()
        if not _names_another_release_on_purpose(name, line)
        for found in NUMERIPLOT_VERSION.findall(line)
        if found not in (VERSION, series)
    ]
    assert not stale, "Update these, or allow them with a reason:\n" + "\n".join(
        stale
    )


def test_public_documents_state_the_bundle_minimum_macos():
    minimum = MACOS_MINIMUM_VERSION.split(".")[0]
    claim = re.compile(
        r"macOS (\d+)(?:\+| or (?:newer|later)| veya (?:üstü|üzeri|sonrası))"
    )
    wrong = [
        f"{name}:{number}: macOS {found}"
        for name, number, line in _public_document_lines()
        for found in claim.findall(line)
        if found != minimum
    ]
    assert not wrong, "\n".join(wrong)


def test_changelog_and_citation_record_the_current_release():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")

    release = re.search(r"(?m)^## (\d+\.\d+\.\d+) - (\d{4}-\d{2}-\d{2})", changelog)
    released = re.search(r"(?m)^date-released: '?(\d{4}-\d{2}-\d{2})'?$", citation)

    assert release and release.group(1) == VERSION
    assert released and released.group(1) == release.group(2)
