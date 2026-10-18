import sys
import os
import logging
import time
import traceback
from logging.handlers import RotatingFileHandler
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

    file_handler = RotatingFileHandler(
        log_file, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.WARNING)
    console.addFilter(lambda record: not getattr(record, 'file_only', False))
    # Full tracebacks stay in the bounded log; the console stays readable.
    class ConsoleFormatter(logging.Formatter):
        def format(self, record):
            first_line = (record.getMessage().splitlines() or [""])[0]
            return f"{record.levelname}: {first_line}"

    console.setFormatter(ConsoleFormatter())
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[file_handler, console],
        force=True,
    )
    for name in ("matplotlib", "PIL"):
        logging.getLogger(name).setLevel(logging.ERROR)
    return log_file


# ── Paket içi Matplotlib önbelleği ────────────────────────────────────────────
def _matplotlib_cache_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / APP_SLUG / "matplotlib"


def _use_persistent_matplotlib_cache():
    """Keep Matplotlib's font cache between launches of the packaged app.

    PyInstaller's runtime hook points MPLCONFIGDIR at a new temporary folder on
    every launch, so the font cache was rebuilt each time.
    Matplotlib rebuilds a cache itself when it no longer matches the app.
    """
    hook_dir = os.environ.get("MPLCONFIGDIR")
    cache_dir = _matplotlib_cache_dir()
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None  # keep PyInstaller's temporary folder
    os.environ["MPLCONFIGDIR"] = str(cache_dir)
    if hook_dir and Path(hook_dir) != cache_dir:
        try:
            os.rmdir(hook_dir)  # still empty: Matplotlib is not imported yet
        except OSError:
            pass
    return cache_dir


def _build_matplotlib_font_cache():
    """Build or read the packaged app's font cache without ``system_profiler``.

    On macOS, Matplotlib also asks ``system_profiler SPFontsDataType`` for the
    installed fonts. That query takes about 10 s, while the font folders that
    Matplotlib scans anyway yield the same fonts. Matplotlib treats a failed
    query as an empty list, so only this slow step is skipped.
    """
    import subprocess

    check_output = subprocess.check_output

    def without_system_profiler(args, *pargs, **kwargs):
        if args and args[0] == "system_profiler":
            raise OSError("NumeriPlot skips the slow system_profiler font query")
        return check_output(args, *pargs, **kwargs)

    subprocess.check_output = without_system_profiler
    try:
        import matplotlib.font_manager  # builds the cache, or reads it later
    finally:
        subprocess.check_output = check_output


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
        logger.critical("Yakalanmamış hata / Uncaught exception:\n%s", tb_str,
                        extra={'file_only': True})

        if QApplication.instance() is None:
            # The Finder launcher supplies the recovery instructions once.
            if getattr(sys, 'frozen', False):
                recovery = "Kılavuz / Guide: docs/MACOS_INSTALL_TR.md / docs/MACOS_INSTALL.md\n"
            elif os.environ.get('NUMERIPLOT_LAUNCHER') == '1':
                recovery = ""
            else:
                recovery = (
                    "Kurulumu yeniden çalıştırın: bash setup.sh / Run setup again: bash setup.sh\n"
                    "Kılavuz bölüm 6 / Guide section 6: docs/SOURCE_INSTALL_TR.md / docs/SOURCE_INSTALL.md\n"
                )
            print(
                "NumeriPlot açılamadı / NumeriPlot could not start.\n"
                + recovery +
                f"Log: {log_file}\n"
                "Paylaşmadan kişisel yolları temizleyin / Remove personal paths before sharing.",
                file=sys.stderr,
            )
            return

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
        logger.info("Matplotlib önbelleği: %s", _use_persistent_matplotlib_cache())
        started = time.perf_counter()
        _build_matplotlib_font_cache()
        logger.info("Yazı tipi önbelleği hazır (%.1f sn)", time.perf_counter() - started)
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
        sys.excepthook(*sys.exc_info())
        sys.exit(1)
