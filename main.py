import sys
import os
import logging
import traceback
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from src.version import (
    APP_NAME,
    APP_SLUG,
    APP_VERSION,
    CRASH_DIALOG_TITLE,
    DISPLAY_VERSION,
    LOG_FILENAME,
    ORGANIZATION_NAME,
    SUPPORT_EMAIL,
)

# ── Log dosyası konumu ────────────────────────────────────────────────────────
def _setup_logging() -> Path:
    """
    macOS: ~/Library/Logs/<APP_SLUG>/<LOG_FILENAME>
    Diğer: ~/.<app_slug_lower>/<LOG_FILENAME>
    """
    if sys.platform == "darwin":
        log_dir = Path.home() / "Library" / "Logs" / APP_SLUG
    else:
        log_dir = Path.home() / f".{APP_SLUG.lower()}"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / LOG_FILENAME

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),   # terminal açıksa orada da göster
        ],
    )
    return log_file


# ── Global exception handler ──────────────────────────────────────────────────
def _make_exception_handler(log_file: Path):
    """Yakalanmamış her hatayı loglar ve kullanıcıya bildirir."""
    logger = logging.getLogger(f"{APP_SLUG.lower()}.crash")

    def handler(exc_type, exc_value, exc_tb):
        # KeyboardInterrupt'ı (Ctrl+C) normale bırak
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return

        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.critical("Yakalanmamış hata / Uncaught exception:\n%s", tb_str)

        # Kullanıcıya nazik hata penceresi
        try:
            msg = QMessageBox()
            msg.setWindowTitle(CRASH_DIALOG_TITLE)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText(
                "<b>Beklenmeyen bir hata oluştu ve uygulama kapanıyor.</b><br><br>"
                "Hata ayrıntıları log dosyasına kaydedildi:<br>"
                f"<code>{log_file}</code><br><br>"
                "Lütfen bu dosyayı geliştirici ile paylaşın:<br>"
                f"<a href='mailto:{SUPPORT_EMAIL}'>{SUPPORT_EMAIL}</a>"
            )
            msg.setDetailedText(tb_str)
            msg.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse |
                Qt.TextInteractionFlag.LinksAccessibleByMouse
            )
            msg.exec()
        except Exception:
            pass  # GUI de çöktüyse sessizce geç

    return handler


# ── Uygulama başlangıcı ───────────────────────────────────────────────────────
if __name__ == "__main__":
    log_file = _setup_logging()
    logger = logging.getLogger(f"{APP_SLUG.lower()}.main")

    # Global exception handler'ı kur
    sys.excepthook = _make_exception_handler(log_file)

    logger.info("%s %s başlatılıyor...", APP_NAME, DISPLAY_VERSION)
    logger.info("Python %s | Platform: %s", sys.version, sys.platform)

    # PyInstaller ile paketlendiğinde kaynak kök
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys._MEIPASS)
        sys.path.insert(0, str(base_dir))
        logger.info("PyInstaller modu — base: %s", base_dir)
    else:
        base_dir = Path(__file__).parent
        logger.info("Geliştirici modu — base: %s", base_dir)

    try:
        from src.ui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName(ORGANIZATION_NAME)

        logger.info("Ana pencere oluşturuluyor...")
        window = MainWindow()
        window.show()
        logger.info("Uygulama hazır.")

        exit_code = app.exec()
        logger.info("Uygulama kapatıldı (exit code: %d)", exit_code)
        sys.exit(exit_code)

    except Exception:
        logger.critical("Başlatma hatası:\n%s", traceback.format_exc())
        raise
