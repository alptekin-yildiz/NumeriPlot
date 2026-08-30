from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
    assert "version: 0.1.0" in citation
    assert "license: GPL-3.0-only" in citation
    assert "repository-code: https://github.com/alptekin-yildiz/NumeriPlot" in citation


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
        "## Install the macOS ZIP",
        "### Gatekeeper and the unsigned beta",
        "## First workflow",
        "## Data and project files",
    ):
        assert heading in readme_en

    for heading in (
        "## Ekran görüntüleri",
        "## macOS ZIP kurulumu",
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
