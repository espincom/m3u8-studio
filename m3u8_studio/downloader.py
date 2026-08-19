import os
import shutil
import subprocess
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtCore import QThread, pyqtSignal
from .cache import acquire_cache, release_cache
from .config import AES, HAS_CRYPTO, APP_TMP, log
from .hls import make_session, parse_master, parse_media, unique_path
from .i18n import tr


class DownloadWorker(QThread):
    log = pyqtSignal(str)
    state = pyqtSignal(str)
    quality = pyqtSignal(str)
    progress = pyqtSignal(int, int, float, float, float, int, int, int)
    preview = pyqtSignal(str)
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, url, headers, out_path, threads, remux, ffmpeg=None):
        super().__init__()
        self.url, self.headers = url, headers
        self.out_path, self.threads, self.remux = out_path, threads, remux
        self.ffmpeg = ffmpeg
        self.stop_event = threading.Event()
        self._lock = threading.Lock()
        self._done = 0
        self._bytes = 0
        self._keys = {}
        self._preview_sent = False
        self._retries = 0
        self._rate_warned = False
        self._durations = deque(maxlen=200)
        self._missing = []
        self._retrying = 0
        self._miss_limit = 2
        self._fail_times = deque(maxlen=60)
        self._cooldown_until = 0.0
        self._cooldown_level = 0
        self._give_up = False
        self._completed = False
        self._partial = 0
        self._cache_dir = None
        self.stall_limit = 240.0
        self._samples = deque()

    def cancel(self):
        self.stop_event.set()

    def _get_key(self, session, uri):
        with self._lock:
            if uri in self._keys:
                return self._keys[uri]
        key = session.get(uri, timeout=30).content
        with self._lock:
            self._keys[uri] = key
        return key

    def _fetch_once(self, session, seg, path):
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with self._lock:
                self._done += 1
                self._bytes += os.path.getsize(path)
            return True

        try:
            headers = {}
            if seg.byte_range:
                length, offset = seg.byte_range
                headers["Range"] = "bytes=%d-%d" % (offset, offset + length - 1)
            t_seg = time.time()
            r = session.get(seg.url, timeout=45, headers=headers)
            r.raise_for_status()
            data = r.content
            dt_seg = time.time() - t_seg
            with self._lock:
                self._durations.append(dt_seg)
            if dt_seg > 10:
                log.warning("YAVAS segment %d: %.1fs (%d bayt)", seg.index, dt_seg, len(data))

            method = (seg.key_method or "NONE").upper()
            if method == "AES-128" and seg.key_uri:
                if not HAS_CRYPTO:
                    raise RuntimeError(tr("e_encrypted"))
                cipher = AES.new(self._get_key(session, seg.key_uri), AES.MODE_CBC, seg.key_iv)
                data = cipher.decrypt(data)
                pad = data[-1] if data else 0
                if 0 < pad <= 16:
                    data = data[:-pad]
            elif method not in ("NONE", ""):
                raise RuntimeError(tr("e_unsupported", seg.key_method))

            tmp = path + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
            with self._lock:
                self._done += 1
                self._bytes += len(data)
                if self._cooldown_level and time.time() - self._cooldown_until > 45:
                    self._cooldown_level = 0
            return True

        except Exception as e:
            code = getattr(getattr(e, "response", None), "status_code", None)
            log.warning("segment %d basarisiz | HTTP=%s | %s: %s",
                        seg.index, code, type(e).__name__, str(e)[:160])
            if code in (429, 503) and not self._rate_warned:
                self._rate_warned = True
                self.log.emit(
                    tr("w_ratelimit", code))
            pause = self._note_failure()
            if pause:
                log.warning("SOGUMA: sunucu ard arda hata donuyor, tum istekler "
                            "%.0f saniye duraklatiliyor (seviye %d)",
                            pause, self._cooldown_level)
                self.state.emit(tr("st_no_response", pause))
            self._last_err = e
            return False

    def _emit_preview(self, tmpdir, paths, init_path, is_fmp4):
        if self._preview_sent:
            return
        ready = [p for p in paths[:8] if os.path.exists(p) and os.path.getsize(p) > 0]
        if len(ready) < min(3, len(paths)):
            return
        try:
            probe = os.path.join(APP_TMP, "probe_%d_%s" % (id(self), ".mp4" if is_fmp4 else ".ts"))
            with open(probe, "wb") as out:
                if init_path:
                    with open(init_path, "rb") as f:
                        shutil.copyfileobj(f, out)
                for p in ready[:6]:
                    with open(p, "rb") as f:
                        shutil.copyfileobj(f, out)
            self._preview_sent = True
            self.preview.emit(probe)
        except OSError:
            pass

    def _note_failure(self):
        now = time.time()
        with self._lock:
            self._fail_times.append(now)
            recent = sum(1 for t in self._fail_times if now - t < 8.0)
            if recent >= 3 and now >= self._cooldown_until:
                self._cooldown_level = min(self._cooldown_level + 1, 5)
                pause = 15.0 * self._cooldown_level
                self._cooldown_until = now + pause
                return pause
        return 0.0

    def _wait_cooldown(self):
        while not self.stop_event.is_set():
            with self._lock:
                remain = self._cooldown_until - time.time()
            if remain <= 0:
                return
            time.sleep(min(remain, 0.4))

    def _emit_progress(self, now, t0, total):
        with self._lock:
            done, total_bytes, retries = self._done, self._bytes, self._retries
            retrying, missing = self._retrying, len(self._missing)
        self._samples.append((now, total_bytes))
        while len(self._samples) > 1 and now - self._samples[0][0] > 3.0:
            self._samples.popleft()
        t_old, b_old = self._samples[0]
        span = max(now - t_old, 0.001)
        inst = (total_bytes - b_old) / 1048576.0 / span
        mb = total_bytes / 1048576.0
        avg = mb / max(now - t0, 0.001)
        self.progress.emit(done, total, mb, inst, avg, retries, retrying, missing)

        if now - getattr(self, "_last_log", 0) > 3.0:
            self._last_log = now
            with self._lock:
                d = sorted(self._durations)
            if d:
                p50 = d[len(d) // 2]
                p95 = d[min(len(d) - 1, int(len(d) * 0.95))]
                log.info("ILERLEME %d/%d | anlik %.2f MB/s | ort %.2f MB/s | retry=%d "
                         "(su an %d) | atlanan=%d | "
                         "segment suresi p50=%.2fs p95=%.2fs (son %d)",
                         done, total, inst, avg, retries, retrying, missing,
                         p50, p95, len(d))
            else:
                log.info("ILERLEME %d/%d | anlik %.2f MB/s | retry=%d | henuz olcum yok",
                         done, total, inst, retries)

    def run(self):
        tmpdir = None
        cache_shared = False
        try:
            session = make_session(self.headers, pool=self.threads)

            self.state.emit(tr("st_reading"))
            r = session.get(self.url, timeout=30)
            r.raise_for_status()
            text, final_url = r.text, r.url
            if "#EXTM3U" not in text:
                raise ValueError(tr("e_not_m3u8"))

            if "#EXT-X-STREAM-INF" in text:
                variants = parse_master(text, final_url)
                if not variants:
                    raise ValueError(tr("e_no_variant"))
                best = variants[0]
                self.quality.emit(best.label())
                self.log.emit(tr("w_quality", best.label()))
                r = session.get(best.url, timeout=30)
                r.raise_for_status()
                text, final_url = r.text, r.url

            media = parse_media(text, final_url)
            if not media.segments:
                raise ValueError(tr("e_no_segment"))
            if media.total_duration:
                self.log.emit(tr("w_duration", media.total_duration / 60))

            total = len(media.segments)
            self._miss_limit = max(2, int(total * 0.01))
            self.state.emit(tr("st_downloading"))
            self.log.emit(tr("w_segments", total, self.threads))

            tmpdir, cache_shared = acquire_cache(media)
            self._cache_dir = tmpdir
            already = sum(1 for i in range(total)
                          if os.path.exists(os.path.join(tmpdir, "%06d.seg" % i)))
            if already:
                log.info("Onbellekte %d/%d segment bulundu, kaldigi yerden devam ediliyor",
                         already, total)
                self.log.emit(tr("w_resume", already))
            paths = [os.path.join(tmpdir, "%06d.seg" % i) for i in range(total)]

            init_path = None
            if media.init_url:
                init_path = os.path.join(tmpdir, "init.mp4")
                with open(init_path, "wb") as f:
                    f.write(session.get(media.init_url, timeout=45).content)

            self._last_err = None
            t0 = time.time()
            last_emit = 0.0
            self._samples.append((t0, 0))
            pending = list(range(total))
            rounds = 5

            for rnd in range(rounds):
                if self.stop_event.is_set():
                    break
                failed, failed_lock = [], threading.Lock()
                if rnd:
                    with self._lock:
                        self._retrying = len(pending)
                        self._retries += len(pending)
                    log.info("TUR %d/%d: %d segment yeniden denenecek",
                             rnd + 1, rounds, len(pending))
                    self.state.emit(tr("st_retrying_n", len(pending)))

                def task(i, _failed=failed, _lock=failed_lock):
                    if self.stop_event.is_set():
                        return
                    self._wait_cooldown()
                    if self.stop_event.is_set():
                        return
                    if not self._fetch_once(session, media.segments[i], paths[i]):
                        with _lock:
                            _failed.append(i)

                round_start = self._done
                stall_mark, stall_done = time.time(), self._done
                with ThreadPoolExecutor(max_workers=self.threads) as pool:
                    futures = [pool.submit(task, i) for i in pending]
                    while any(not f.done() for f in futures):
                        now = time.time()
                        if now - last_emit > 0.25:
                            self._emit_progress(now, t0, total)
                            self._emit_preview(tmpdir, paths, init_path, media.is_fmp4)
                            last_emit = now
                        if self._done != stall_done:
                            stall_done, stall_mark = self._done, now
                        elif now - stall_mark > self.stall_limit and not self._give_up:
                            log.warning("TAKILMA: %.0f saniyedir hic segment inmiyor (%d/%d)",
                                        now - stall_mark, self._done, total)
                            self.log.emit(tr("w_stalled", now - stall_mark))
                            self._give_up = True
                            self.stop_event.set()
                        time.sleep(0.08)

                with self._lock:
                    self._retrying = 0
                gained = self._done - round_start
                pending = sorted(failed)
                if not pending or self.stop_event.is_set():
                    break
                if gained == 0:
                    log.warning("Tur %d'de hicbir segment inmedi (%d segment reddediliyor) - "
                                "yeniden denemeler durduruluyor", rnd + 1, len(pending))
                    self.log.emit(tr("w_unreachable", len(pending), pending[0]))
                    break

                bekleme = min(10.0 * (rnd + 1), 45.0)
                log.info("Tur %d bitti, %d segment basarisiz. %.0f sn sonra tekrar denenecek.",
                         rnd + 1, len(pending), bekleme)
                self.log.emit(tr("w_retry_wait", len(pending), bekleme))
                self.state.emit(tr("st_waiting_n", len(pending), bekleme))
                son = time.time() + bekleme
                while time.time() < son and not self.stop_event.is_set():
                    time.sleep(0.2)

            self._emit_progress(time.time(), t0, total)

            if self.stop_event.is_set() and not self._give_up:
                raise RuntimeError(tr("w_cancelled"))

            self._missing = sorted(set(self._missing) | set(pending))
            if self._missing:
                log.error("%d segment tum turlarda indirilemedi: %s",
                          len(self._missing), self._missing[:20])
                with self._lock:
                    self._done = total
                self._emit_progress(time.time(), t0, total)

            got = sum(1 for p in paths if os.path.exists(p) and os.path.getsize(p) > 0)
            oran = got / float(total or 1)
            if got < total:
                log.info("Eksik bitis: %d/%d segment elde (%%%.0f)", got, total, oran * 100)
                if oran < 0.5:
                    raise RuntimeError(tr("e_too_few", int(oran * 100), got, total))
                if oran < 0.95:
                    self._partial = int(round(oran * 100))
                    stem, ext = os.path.splitext(self.out_path)
                    self.out_path = "%s (eksik %%%d)%s" % (stem, self._partial, ext)
                    self.log.emit(tr("w_partial_save", self._partial))
                else:
                    self.log.emit(tr("w_gaps", total - got))

            log.info("Tum segmentler indi, birlestirme basliyor (%d segment, %.1f MB)",
                     total, self._bytes / 1048576.0)
            self.state.emit(tr("st_merging"))
            raw_ext = ".mp4" if media.is_fmp4 else ".ts"
            raw_path = os.path.splitext(self.out_path)[0] + ".raw" + raw_ext
            os.makedirs(os.path.dirname(os.path.abspath(raw_path)) or ".", exist_ok=True)
            with open(raw_path, "wb") as out:
                if init_path:
                    with open(init_path, "rb") as f:
                        shutil.copyfileobj(f, out)
                for i, p in enumerate(paths):
                    if not os.path.exists(p):
                        continue
                    with open(p, "rb") as f:
                        shutil.copyfileobj(f, out, 1024 * 1024)

            ffmpeg = self.ffmpeg
            if self.remux and ffmpeg:
                self.state.emit(tr("st_converting"))
                final_path = self.out_path
                proc = subprocess.run(
                    [ffmpeg, "-y", "-i", raw_path, "-c", "copy",
                     "-bsf:a", "aac_adtstoasc", final_path],
                    capture_output=True, text=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                if proc.returncode != 0 or not os.path.exists(final_path):
                    log.warning("ffmpeg donusturme basarisiz (kod=%s): %s",
                                proc.returncode, (proc.stderr or "").strip()[-400:])
                    self.log.emit(tr("w_ffmpeg_fail"))
                    if os.path.exists(final_path):
                        try:
                            os.remove(final_path)
                        except OSError:
                            pass
                    self.log.emit((proc.stderr or "").strip()[-500:])
                    final_path = raw_path
                else:
                    os.remove(raw_path)
            else:
                final_path = unique_path(os.path.splitext(self.out_path)[0] + raw_ext)
                os.replace(raw_path, final_path)

            self._completed = not self._missing and not self._give_up
            log.info("TAMAMLANDI%s %s (%.1f MB)",
                     "" if self._completed else " (EKSIK)", final_path,
                     os.path.getsize(final_path) / 1048576.0)
            self.log.emit(tr("w_finished", os.path.getsize(final_path) / 1048576.0))
            self.finished_ok.emit(final_path)

        except Exception as e:
            if self.stop_event.is_set() and "iptal" in str(e).lower():
                log.info("Gorev kullanici tarafindan iptal edildi: %s", self.out_path)
            else:
                log.error("GOREV HATASI (%s): %s", self.out_path, e, exc_info=True)
            self.failed.emit(str(e))
        finally:
            if tmpdir and os.path.isdir(tmpdir):
                release_cache(tmpdir, cache_shared)
                if not cache_shared or (self._completed and not self._missing):
                    shutil.rmtree(tmpdir, ignore_errors=True)
                else:
                    kept = len([f for f in os.listdir(tmpdir) if f.endswith(".seg")])
                    log.info("Onbellek korundu (%d segment): %s", kept, tmpdir)
