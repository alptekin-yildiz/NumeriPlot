"""What the NumeriPlot macOS app leaves out; shared by the spec, checks and tests."""
import posixpath

# NumeriPlot imports QtCore, QtGui and QtWidgets; QtGui itself needs QtDBus, and
# QtSvg stays for SVG icons. The parts below reach the bundle only through
# plugins NumeriPlot never loads. Leaving them out keeps the app smaller and
# limits the Qt source offered with a release to these modules.
QT_SOURCE_MODULES = ("qtbase", "qtsvg")

EXCLUDED_QT_PATHS = (
    "PyQt6/Qt6/lib/QtPdf.framework",
    "PyQt6/Qt6/lib/QtNetwork.framework",
    "PyQt6/Qt6/plugins/generic",
    "PyQt6/Qt6/plugins/imageformats/libqpdf.dylib",
    # Image formats from the qtimageformats module.
    "PyQt6/Qt6/plugins/imageformats/libqicns.dylib",
    "PyQt6/Qt6/plugins/imageformats/libqmacheif.dylib",
    "PyQt6/Qt6/plugins/imageformats/libqmacjp2.dylib",
    "PyQt6/Qt6/plugins/imageformats/libqtga.dylib",
    "PyQt6/Qt6/plugins/imageformats/libqtiff.dylib",
    "PyQt6/Qt6/plugins/imageformats/libqwbmp.dylib",
    "PyQt6/Qt6/plugins/imageformats/libqwebp.dylib",
)

EXCLUDED_QT_FRAMEWORKS = ("QtPdf", "QtNetwork")


def is_excluded(dest_name):
    dest = str(dest_name).replace("\\", "/")
    return any(dest == path or dest.startswith(path + "/") for path in EXCLUDED_QT_PATHS)


def is_excluded_entry(dest_name, src_name, typecode):
    """A PyInstaller TOC entry for an excluded part, or a symlink pointing at one."""
    if is_excluded(dest_name):
        return True
    if typecode != "SYMLINK":
        return False
    # PyInstaller also links e.g. 'QtPdf' -> 'PyQt6/Qt6/lib/QtPdf.framework/Versions/A/QtPdf'.
    dest = str(dest_name).replace("\\", "/")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(dest), str(src_name).replace("\\", "/")))
    return is_excluded(target)
