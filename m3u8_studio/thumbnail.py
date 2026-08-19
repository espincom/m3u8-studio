import os
import subprocess
from PyQt6.QtCore import QObject, QThread, QTimer, QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QImage
from PyQt6.QtMultimedia import QMediaPlayer, QVideoSink
from .config import find_ffmpeg, log


class _FFmpegThumbJob(QThread):
    done = pyqtSignal(object, object, str)

    def __init__(self, ffmpeg, sample_path, task, parent=None):
        super().__init__(parent)
        self.ffmpeg, self.sample_path, self.task = ffmpeg, sample_path, task

    def run(self):
        img = None
        out = self.sample_path + ".jpg"
        try:
            subprocess.run(
                [self.ffmpeg, "-y", "-ss", "3", "-i", self.sample_path, "-frames:v", "1",
                 "-vf", "scale=320:-1", out],
                capture_output=True, timeout=25,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if os.path.exists(out):
                loaded = QImage(out)
                if not loaded.isNull():
                    img = loaded
        except Exception:
            img = None
        self.done.emit(self.task, img, self.sample_path)


class ThumbnailGrabber(QObject):
    ready = pyqtSignal(object, QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._jobs = {}
        self._ff_jobs = {}

    def request(self, task, sample_path):
        log.info("Thumbnail istegi: %s (%.1f KB)", os.path.basename(sample_path),
                 os.path.getsize(sample_path) / 1024.0 if os.path.exists(sample_path) else 0)
        ffmpeg = find_ffmpeg()
        if ffmpeg:
            job = _FFmpegThumbJob(ffmpeg, sample_path, task, self)
            job.done.connect(self._on_ffmpeg_job)
            job.finished.connect(lambda j=job: self._ff_jobs.pop(id(j), None))
            self._ff_jobs[id(job)] = job
            job.start()
            return
        self._grab_with_qt(task, sample_path)

    def _on_ffmpeg_job(self, task, img, sample_path):
        if img is not None and not img.isNull():
            self.ready.emit(task, img)
        else:
            self._grab_with_qt(task, sample_path)

    def _grab_with_qt(self, task, sample_path):
        key = id(task)
        if key in self._jobs:
            return
        player = QMediaPlayer()
        sink = QVideoSink()
        player.setVideoSink(sink)
        state = {"frames": 0, "best": None}

        def cleanup():
            job = self._jobs.pop(key, None)
            if job:
                job["timer"].stop()
                try:
                    job["player"].stop()
                    job["player"].setSource(QUrl())
                except RuntimeError:
                    pass

        def on_frame(frame):
            if not frame.isValid():
                return
            state["frames"] += 1
            img = frame.toImage()
            if img.isNull():
                return
            state["best"] = img.copy()
            if state["frames"] >= 12:
                self.ready.emit(task, state["best"])
                cleanup()

        def on_timeout():
            if state["best"] is not None:
                self.ready.emit(task, state["best"])
            cleanup()

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(on_timeout)
        timer.start(9000)

        log.info("Qt Multimedia ile kare yakalama basliyor")
        sink.videoFrameChanged.connect(on_frame)
        self._jobs[key] = {"player": player, "sink": sink, "timer": timer}
        player.setSource(QUrl.fromLocalFile(os.path.abspath(sample_path)))
        player.play()

    def shutdown(self):
        for key in list(self._ff_jobs):
            job = self._ff_jobs.pop(key)
            job.wait(1500)
        for key in list(self._jobs):
            job = self._jobs.pop(key)
            job["timer"].stop()
            try:
                job["player"].stop()
            except RuntimeError:
                pass
