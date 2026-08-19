import logging
import os
import shutil
import sys
import tempfile
from PyQt6.QtCore import QSettings

try:
    from Crypto.Cipher import AES
    HAS_CRYPTO = True
except ImportError:
    AES = None
    HAS_CRYPTO = False


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


APP_TMP = tempfile.mkdtemp(prefix="m3u8studio_")


PKG_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(PKG_DIR)
LOG_PATH = os.path.join(APP_DIR, "m3u8_studio.log")


SETTINGS_SCOPE = os.environ.get("M3U8_SETTINGS_SCOPE", "downloader")


log = logging.getLogger("m3u8")


def setup_logging():
    log.setLevel(logging.DEBUG)
    if log.handlers:
        return
    fmt = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)-7s %(message)s",
                            datefmt="%H:%M:%S")
    fh = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    fh.setFormatter(fmt)
    log.addHandler(fh)
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    log.addHandler(sh)

    def excepthook(exc_type, exc, tb):
        log.error("YAKALANMAMIS HATA", exc_info=(exc_type, exc, tb))
        sys.__excepthook__(exc_type, exc, tb)

    sys.excepthook = excepthook
    log.info("=" * 70)
    log.info("Oturum basladi | Python %s | ffmpeg=%s | crypto=%s",
             sys.version.split()[0], find_ffmpeg(), HAS_CRYPTO)


def _as_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in ("true", "1", "yes", "evet")


_FFMPEG_CACHE = {"path": None, "checked": False}


def find_ffmpeg(refresh=False):
    if _FFMPEG_CACHE["checked"] and not refresh:
        return _FFMPEG_CACHE["path"]

    found = None

    custom = QSettings("m3u8studio", SETTINGS_SCOPE).value("ffmpeg_path", "")
    if custom and os.path.isfile(custom):
        found = custom

    if not found:
        found = shutil.which("ffmpeg")

    if not found:
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.isfile(exe):
                found = exe
        except Exception:
            pass

    if not found:
        cands = []
        for here in (APP_DIR, PKG_DIR):
            cands += [os.path.join(here, "ffmpeg.exe"),
                      os.path.join(here, "ffmpeg", "ffmpeg.exe"),
                      os.path.join(here, "ffmpeg", "bin", "ffmpeg.exe")]
        for cand in cands:
            if os.path.isfile(cand):
                found = cand
                break

    _FFMPEG_CACHE.update(path=found, checked=True)
    return found
