import hashlib
import os
import shutil
import tempfile
import threading
import time
from .config import APP_TMP, log
from urllib.parse import urlparse


CACHE_ROOT = os.path.join(tempfile.gettempdir(), "m3u8studio_cache")


def cache_dir_for(media):
    h = hashlib.sha1()
    for seg in media.segments:
        h.update(urlparse(seg.url).path.encode("utf-8", "ignore"))
    d = os.path.join(CACHE_ROOT, h.hexdigest()[:16])
    os.makedirs(d, exist_ok=True)
    return d


_CACHE_LOCK = threading.Lock()


_CACHE_INUSE = set()


def acquire_cache(media):
    d = cache_dir_for(media)
    with _CACHE_LOCK:
        if d not in _CACHE_INUSE:
            _CACHE_INUSE.add(d)
            return d, True
    log.info("Onbellek zaten kullanimda, bu gorev icin gecici klasor aciliyor")
    return tempfile.mkdtemp(prefix="seg_", dir=APP_TMP), False


def release_cache(path, shared):
    if shared:
        with _CACHE_LOCK:
            _CACHE_INUSE.discard(path)


def clean_old_cache(days=3):
    if not os.path.isdir(CACHE_ROOT):
        return
    limit = time.time() - days * 86400
    for name in os.listdir(CACHE_ROOT):
        d = os.path.join(CACHE_ROOT, name)
        try:
            if os.path.isdir(d) and os.path.getmtime(d) < limit:
                shutil.rmtree(d, ignore_errors=True)
                log.info("Eski onbellek silindi: %s", name)
        except OSError:
            pass
