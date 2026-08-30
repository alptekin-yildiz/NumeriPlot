from lang.en import STRINGS as EN
from lang.tr import STRINGS as TR
from src.version import (
    APP_NAME,
    APP_SLUG,
    APP_SUBTITLE,
    APP_VERSION,
    BUNDLE_ID,
    BUNDLE_SHORT_VERSION,
    BUNDLE_VERSION,
    CHANNEL_LABEL,
    DISPLAY_VERSION,
    LOG_FILENAME,
    ORGANIZATION_NAME,
    VERSION,
    WINDOW_TITLE,
    ZIP_BASENAME,
)


def test_numeriplot_public_beta_identity():
    assert APP_NAME == "NumeriPlot"
    assert APP_SLUG == "NumeriPlot"
    assert APP_SUBTITLE == "Scientific Plotting, Data Analysis and Curve Fitting"
    assert ORGANIZATION_NAME == "NumeriPlot Project"
    assert VERSION == "0.1.0"
    assert CHANNEL_LABEL == "Public Beta"
    assert APP_VERSION == "0.1.0-beta"
    assert DISPLAY_VERSION == "Public Beta v0.1.0"
    assert WINDOW_TITLE == "NumeriPlot Public Beta v0.1.0"


def test_packaging_and_log_names_follow_canonical_identity():
    assert BUNDLE_ID == "io.github.alptekin-yildiz.numeriplot"
    assert BUNDLE_SHORT_VERSION == VERSION
    assert BUNDLE_VERSION == VERSION
    assert LOG_FILENAME == "numeriplot.log"
    assert ZIP_BASENAME == "NumeriPlot_v0.1.0_macOS.zip"


def test_localized_product_names_follow_canonical_identity():
    assert EN["app_title"] == APP_NAME
    assert TR["app_title"] == APP_NAME
    assert APP_NAME in EN["action_about"]
    assert EN["msg_about"] == f"{APP_NAME}\n{APP_SUBTITLE}"
    assert TR["msg_about"] == f"{APP_NAME}\n{APP_SUBTITLE}"


def test_critical_project_workflow_texts_are_localized():
    assert EN["action_load_data"] == "📥 Load Data…"
    assert TR["action_load_data"] == "📥 Veri Yükle…"
    assert EN["action_open_project"] == "📂 Open Project…"
    assert TR["action_open_project"] == "📂 Proje Aç…"
    assert EN["action_save_project"] == "💾 Save Project"
    assert TR["action_save_project"] == "💾 Projeyi Kaydet"
    assert "unsupported or missing schema" in EN["msg_project_schema_error"]
    assert "desteklenmeyen veya eksik" in TR["msg_project_schema_error"]
    assert "{error}" in EN["msg_export_error"]
    assert "{error}" in TR["msg_export_error"]
    assert "unsaved changes" in EN["msg_exit_text"]
    assert "Kaydedilmemiş değişiklikler" in TR["msg_exit_text"]
