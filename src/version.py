"""Single source of truth for app identity/version metadata."""

APP_NAME = "NumeriPlot"
APP_SLUG = "NumeriPlot"
APP_SUBTITLE = "Scientific Plotting, Data Analysis and Curve Fitting"
ORGANIZATION_NAME = "NumeriPlot Project"
SUPPORT_EMAIL = "alptekin.yildiz@itu.edu.tr"
VERSION = "0.1.1"
CHANNEL_LABEL = "Public Beta"
PRERELEASE_TAG = "beta"

DISPLAY_VERSION = f"{CHANNEL_LABEL} v{VERSION}"
APP_VERSION = f"{VERSION}-{PRERELEASE_TAG}"
WINDOW_TITLE = f"{APP_NAME} {DISPLAY_VERSION}"
CRASH_DIALOG_TITLE = f"{APP_NAME} — Beklenmeyen Hata"

# macOS bundle fields
BUNDLE_ID = "io.github.alptekin-yildiz.numeriplot"
BUNDLE_SHORT_VERSION = VERSION
BUNDLE_VERSION = VERSION
MACOS_MINIMUM_VERSION = "14.0"

# Local logging and artifact naming
LOG_FILENAME = f"{APP_SLUG.lower()}.log"
ZIP_BASENAME = f"{APP_SLUG}_v{VERSION}_macOS.zip"
