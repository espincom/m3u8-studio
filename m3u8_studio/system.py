import os
import shutil
import subprocess
import sys

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from .config import log

LINUX_MANAGERS = (
    ("nautilus", ["nautilus", "--select"]),
    ("dolphin", ["dolphin", "--select"]),
    ("nemo", ["nemo"]),
    ("caja", ["caja", "--select"]),
    ("thunar", ["thunar"]),
    ("pcmanfm", ["pcmanfm"]),
    ("pcmanfm-qt", ["pcmanfm-qt"]),
    ("konqueror", ["konqueror", "--select"]),
)


def _no_window():
    return {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}


def _open_folder(folder):
    if not os.path.isdir(folder):
        return False
    return QDesktopServices.openUrl(QUrl.fromLocalFile(folder))


def _reveal_linux(path):
    uri = QUrl.fromLocalFile(path).toString()
    if shutil.which("dbus-send"):
        try:
            done = subprocess.run(
                ["dbus-send", "--session", "--print-reply",
                 "--dest=org.freedesktop.FileManager1", "--type=method_call",
                 "/org/freedesktop/FileManager1",
                 "org.freedesktop.FileManager1.ShowItems",
                 "array:string:" + uri, "string:m3u8studio"],
                capture_output=True, timeout=6)
            if done.returncode == 0:
                return True
        except (OSError, subprocess.SubprocessError):
            pass

    for exe, cmd in LINUX_MANAGERS:
        if shutil.which(exe):
            try:
                subprocess.Popen(cmd + [path])
                return True
            except OSError:
                continue
    return False


def reveal_in_folder(path):
    if not path:
        return False
    path = os.path.abspath(path)
    folder = os.path.dirname(path)
    exists = os.path.exists(path)

    try:
        if sys.platform.startswith("win"):
            if exists:
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
                return True
        elif sys.platform == "darwin":
            if exists:
                subprocess.Popen(["open", "-R", path])
                return True
            subprocess.Popen(["open", folder])
            return True
        else:
            if exists and _reveal_linux(path):
                return True
    except (OSError, subprocess.SubprocessError) as exc:
        log.warning("Dosya yoneticisi acilamadi (%s): %s", sys.platform, exc)

    return _open_folder(folder)
