import os
import re
import shutil
import subprocess
import time
from PyQt6.QtCore import QSettings, QSize, QTimer, Qt
from PyQt6.QtWidgets import QApplication, QCheckBox, QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget
from .about import AboutPage
from .config import APP_TMP, SETTINGS_SCOPE, _as_bool, find_ffmpeg, log
from .dialogs import BulkDialog, ClipboardToast
from .downloader import DownloadWorker
from .hls import suggest_name, unique_path
from .i18n import STRINGS, current_language, set_language, tr
from .models import Task
from .system import reveal_in_folder
from . import sounds
from .theme import C_ACCENT, C_ACCENT_2, C_MUTED, C_OK, C_WARN
from .thumbnail import ThumbnailGrabber
from .widgets import FlagButton, TaskWidget
from urllib.parse import urlparse


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app_title"))
        self.resize(1060, 760)
        self.setMinimumSize(880, 600)

        self.settings = QSettings("m3u8studio", SETTINGS_SCOPE)
        self.tasks = []
        self._zombies = []
        self.grabber = ThumbnailGrabber(self)
        self.grabber.ready.connect(self.on_thumb_ready)
        self._last_clip = ""

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_header())

        body = QWidget()
        blay = QVBoxLayout(body)
        blay.setContentsMargins(20, 16, 20, 16)
        blay.setSpacing(14)
        blay.addWidget(self._build_input_panel())
        blay.addWidget(self._build_options_panel())
        blay.addWidget(self._build_queue_panel(), 1)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.about_page = AboutPage()
        self.tabs.addTab(body, tr("tab_downloader"))
        self.tabs.addTab(self.about_page, tr("tab_about"))
        outer.addWidget(self.tabs, 1)

        outer.addWidget(self._build_footer())

        self.toast = ClipboardToast(root)
        self.toast.download_now.connect(lambda u: self.add_link(u, start_now=True))
        self.toast.add_queue.connect(lambda u: self.add_link(u, start_now=False))

        self._load_settings()

        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard)

        self.pump = QTimer(self)
        self.pump.timeout.connect(self.pump_queue)
        self.pump.start(700)

        self._wd_last = time.time()
        self._watchdog = QTimer(self)
        self._watchdog.timeout.connect(self._check_responsive)
        self._watchdog.start(250)
        self.update_footer()

    def _build_header(self):
        h = QFrame()
        h.setObjectName("header")
        h.setFixedHeight(74)
        lay = QHBoxLayout(h)
        lay.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("⬇")
        logo.setFixedSize(42, 42)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 %s, stop:1 %s);"
            "border-radius: 12px; color: white; font-size: 19px; font-weight: 800;"
            % (C_ACCENT, C_ACCENT_2))
        lay.addWidget(logo)

        col = QVBoxLayout()
        col.setSpacing(0)
        t = QLabel("M3U8 Studio")
        t.setObjectName("h1")
        s = QLabel(tr("tagline"))
        s.setObjectName("sub")
        col.addWidget(t)
        col.addWidget(s)
        lay.addLayout(col)
        lay.addStretch(1)

        self.clip_check = QCheckBox(tr("clip_watch"))
        self.clip_check.setToolTip(tr("clip_watch_tip"))
        self.clip_check.setChecked(True)
        lay.addWidget(self.clip_check)

        lay.addSpacing(14)
        self.flag_en = FlagButton("en")
        self.flag_tr = FlagButton("tr")
        self.flag_en.setToolTip(tr("lang_tip_en"))
        self.flag_tr.setToolTip(tr("lang_tip_tr"))
        self.flag_en.clicked.connect(lambda: self.change_language("en"))
        self.flag_tr.clicked.connect(lambda: self.change_language("tr"))
        lay.addWidget(self.flag_en)
        lay.addWidget(self.flag_tr)

        self.header_title = t
        self.header_sub = s
        return h

    def _build_input_panel(self):
        p = QFrame()
        p.setObjectName("panel")
        lay = QVBoxLayout(p)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(10)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText(tr("url_placeholder"))
        self.url_edit.returnPressed.connect(self.on_add_clicked)
        row.addWidget(self.url_edit, 1)

        self.add_btn = add_btn = QPushButton(tr("add_queue"))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.on_add_clicked)
        row.addWidget(add_btn)

        self.now_btn = now_btn = QPushButton(tr("download_now"))
        now_btn.setObjectName("primary")
        now_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        now_btn.clicked.connect(lambda: self.on_add_clicked(start_now=True))
        row.addWidget(now_btn)

        self.bulk_btn = bulk_btn = QPushButton(tr("bulk_add"))
        bulk_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bulk_btn.clicked.connect(self.on_bulk)
        row.addWidget(bulk_btn)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        self.dir_label = QLabel(tr("save_folder"))
        row2.addWidget(self.dir_label)
        self.dir_edit = QLineEdit(os.path.join(os.path.expanduser("~"), "Downloads"))
        row2.addWidget(self.dir_edit, 1)
        self.browse_btn = br = QPushButton(tr("browse"))
        br.setCursor(Qt.CursorShape.PointingHandCursor)
        br.clicked.connect(self.on_browse)
        row2.addWidget(br)
        lay.addLayout(row2)
        return p

    def _build_options_panel(self):
        p = QFrame()
        p.setObjectName("panel")
        lay = QHBoxLayout(p)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(18)

        f1 = QFormLayout()
        self.referer_edit = QLineEdit()
        self.referer_edit.setPlaceholderText(tr("referer_ph"))
        self.cookie_edit = QLineEdit()
        self.cookie_edit.setPlaceholderText(tr("cookie_ph"))
        self.lbl_referer = QLabel(tr("referer"))
        self.lbl_cookie = QLabel(tr("cookie"))
        f1.addRow(self.lbl_referer, self.referer_edit)
        f1.addRow(self.lbl_cookie, self.cookie_edit)
        lay.addLayout(f1, 1)

        f2 = QFormLayout()
        self.threads_spin = QSpinBox()
        self.threads_spin.setRange(1, 32)
        self.threads_spin.setValue(8)
        self.parallel_spin = QSpinBox()
        self.parallel_spin.setRange(1, 5)
        self.parallel_spin.setValue(2)
        self.lbl_threads = QLabel(tr("seg_conn"))
        self.lbl_parallel = QLabel(tr("parallel_video"))
        f2.addRow(self.lbl_threads, self.threads_spin)
        f2.addRow(self.lbl_parallel, self.parallel_spin)
        lay.addLayout(f2)

        col = QVBoxLayout()
        col.setSpacing(8)
        self.autostart_check = QCheckBox(tr("autostart"))
        self.autostart_check.setChecked(False)
        col.addWidget(self.autostart_check)
        self.remux_check = QCheckBox(tr("remux"))
        self.remux_check.setEnabled(False)
        col.addWidget(self.remux_check)

        ff_row = QHBoxLayout()
        ff_row.setSpacing(6)
        self.ffmpeg_label = QLabel("")
        self.ffmpeg_label.setStyleSheet("color:%s; font-size:11px;" % C_MUTED)
        ff_row.addWidget(self.ffmpeg_label, 1)
        self.ffmpeg_btn = QPushButton("ffmpeg…")
        self.ffmpeg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ffmpeg_btn.setToolTip(tr("ffmpeg_btn_tip"))
        self.ffmpeg_btn.clicked.connect(self.on_ffmpeg_setup)
        ff_row.addWidget(self.ffmpeg_btn)
        col.addLayout(ff_row)
        col.addStretch(1)
        lay.addLayout(col)
        return p

    def _build_queue_panel(self):
        p = QFrame()
        p.setObjectName("panel")
        lay = QVBoxLayout(p)
        lay.setContentsMargins(14, 12, 14, 14)
        lay.setSpacing(10)

        head = QHBoxLayout()
        self.queue_title = title = QLabel(tr("queue_title"))
        title.setStyleSheet("font-size:14px; font-weight:700;")
        head.addWidget(title)
        head.addStretch(1)
        self.queue_buttons = []
        for key, slot in (("download_all", self.start_all),
                          ("clear_done", self.clear_done),
                          ("clear_all", self.clear_all)):
            b = QPushButton(tr(key))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(slot)
            head.addWidget(b)
            self.queue_buttons.append((b, key))
        lay.addLayout(head)

        self.list = QListWidget()
        self.list.setSpacing(8)
        self.list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        lay.addWidget(self.list, 1)

        self.empty_label = QLabel(tr("queue_empty"))
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color:%s; font-size:12px;" % C_MUTED)
        lay.addWidget(self.empty_label)
        return p

    def _build_footer(self):
        f = QFrame()
        f.setObjectName("header")
        f.setFixedHeight(38)
        lay = QHBoxLayout(f)
        lay.setContentsMargins(20, 0, 20, 0)
        self.status = QLabel(tr("ready"))
        self.status.setObjectName("sub")
        lay.addWidget(self.status)
        lay.addStretch(1)
        self.hint = QLabel("")
        self.hint.setObjectName("sub")
        lay.addWidget(self.hint)
        return f

    def _load_settings(self):
        s = self.settings
        self._loading = True

        saved_dir = s.value("out_dir", "")
        if saved_dir:
            self.dir_edit.setText(saved_dir)
        self.referer_edit.setText(s.value("referer", ""))
        self.cookie_edit.setText(s.value("cookie", ""))
        try:
            self.threads_spin.setValue(int(s.value("threads", 8)))
            self.parallel_spin.setValue(int(s.value("parallel", 2)))
        except (TypeError, ValueError):
            pass
        set_language(s.value("lang", "en"))
        self.flag_en.setChecked(current_language() == "en")
        self.flag_tr.setChecked(current_language() == "tr")
        self.clip_check.setChecked(_as_bool(s.value("clipboard", True), True))
        self.autostart_check.setChecked(_as_bool(s.value("autostart", False), False))

        ff = find_ffmpeg()
        remux = _as_bool(s.value("remux", bool(ff)), bool(ff)) and bool(ff)
        if ff and not _as_bool(s.value("ffmpeg_seen", False), False):
            remux = True
            s.setValue("ffmpeg_seen", True)
        self.remux_check.setChecked(remux)
        self.refresh_ffmpeg_state()

        self._loading = False
        self._bind_autosave()
        if current_language() != "en":
            self.retranslate_ui()

    def _bind_autosave(self):
        for w in (self.dir_edit, self.referer_edit, self.cookie_edit):
            w.textChanged.connect(self._save_settings)
        for w in (self.threads_spin, self.parallel_spin):
            w.valueChanged.connect(self._save_settings)
        for w in (self.clip_check, self.autostart_check, self.remux_check):
            w.toggled.connect(self._save_settings)

    def _save_settings(self, *_):
        if getattr(self, "_loading", False):
            return
        s = self.settings
        s.setValue("out_dir", self.dir_edit.text())
        s.setValue("referer", self.referer_edit.text())
        s.setValue("cookie", self.cookie_edit.text())
        s.setValue("threads", self.threads_spin.value())
        s.setValue("parallel", self.parallel_spin.value())
        s.setValue("clipboard", self.clip_check.isChecked())
        s.setValue("autostart", self.autostart_check.isChecked())
        s.setValue("remux", self.remux_check.isChecked())
        s.sync()

    def refresh_ffmpeg_state(self):
        ff = find_ffmpeg(refresh=True)
        self.remux_check.setEnabled(bool(ff))
        self.remux_check.setText(tr("remux"))
        if ff:
            self.ffmpeg_label.setText(tr("ffmpeg_found", os.path.basename(ff)))
            self.ffmpeg_label.setToolTip(ff)
            self.ffmpeg_label.setStyleSheet("color:%s; font-size:11px;" % C_OK)
        else:
            self.remux_check.setChecked(False)
            self.ffmpeg_label.setText(tr("ffmpeg_missing"))
            self.ffmpeg_label.setToolTip("")
            self.ffmpeg_label.setStyleSheet("color:%s; font-size:11px;" % C_WARN)

    def on_ffmpeg_setup(self):
        ff = find_ffmpeg(refresh=True)
        if ff:
            box = QMessageBox(self)
            box.setWindowTitle(tr("ff_title"))
            box.setText(tr("ff_found_body", ff))
            change = box.addButton(tr("ff_pick_other"), QMessageBox.ButtonRole.ActionRole)
            box.addButton(tr("ff_ok"), QMessageBox.ButtonRole.RejectRole)
            box.exec()
            if box.clickedButton() is not change:
                return
        else:
            box = QMessageBox(self)
            box.setWindowTitle(tr("ff_setup_title"))
            box.setText(tr("ff_setup_body"))
            again = box.addButton(tr("ff_search_again"), QMessageBox.ButtonRole.AcceptRole)
            pick = box.addButton(tr("ff_pick"), QMessageBox.ButtonRole.ActionRole)
            box.addButton(tr("ff_close"), QMessageBox.ButtonRole.RejectRole)
            box.exec()
            clicked = box.clickedButton()
            if clicked is again:
                self.refresh_ffmpeg_state()
                found = find_ffmpeg()
                self.status.setText(tr("ff_now_found", found) if found
                                    else tr("ff_still_missing"))
                return
            if clicked is not pick:
                return

        path, _ = QFileDialog.getOpenFileName(
            self, tr("ff_dialog_pick"), "", "ffmpeg (ffmpeg.exe);;All files (*)")
        if path:
            self.settings.setValue("ffmpeg_path", path)
            self.settings.sync()
            self.refresh_ffmpeg_state()
            self.status.setText(tr("ff_set", path))

    def headers(self):
        h = {}
        ref = self.referer_edit.text().strip()
        if ref:
            h["Referer"] = ref
            u = urlparse(ref)
            if u.scheme and u.netloc:
                h["Origin"] = "%s://%s" % (u.scheme, u.netloc)
        if self.cookie_edit.text().strip():
            h["Cookie"] = self.cookie_edit.text().strip()
        return h

    def on_browse(self):
        d = QFileDialog.getExistingDirectory(self, tr("dlg_pick_folder"), self.dir_edit.text())
        if d:
            self.dir_edit.setText(d)

    def on_add_clicked(self, start_now=False):
        url = self.url_edit.text().strip()
        if not url:
            return
        if self.add_link(url, start_now=start_now or self.autostart_check.isChecked()):
            self.url_edit.clear()

    def on_bulk(self):
        dlg = BulkDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        links = dlg.links()
        added = 0
        for url, name in links:
            if self.add_link(url, name=name, start_now=self.autostart_check.isChecked(),
                             silent=True):
                added += 1
        self.status.setText(tr("bulk_added", added, len(links) - added))

    def add_link(self, url, name="", start_now=False, silent=False):
        url = url.strip()
        if not url.lower().startswith(("http://", "https://")):
            if not silent:
                QMessageBox.warning(self, tr("msg_invalid_title"), tr("msg_invalid"))
            return False
        if any(t.url == url and t.status in ("queued", "running") for t in self.tasks):
            if not silent:
                self.status.setText(tr("msg_dup"))
            return False

        out_dir = self.dir_edit.text().strip() or os.getcwd()
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, tr("msg_folder_err"), str(e))
            return False

        name = name.strip() or suggest_name(url)
        if not os.path.splitext(name)[1]:
            name += ".mp4"

        task = Task(url, name, out_dir)
        self.tasks.append(task)

        widget = TaskWidget(task)
        widget.start_requested.connect(self.start_task)
        widget.stop_requested.connect(self.stop_task)
        widget.remove_requested.connect(self.remove_task)
        widget.open_requested.connect(self.open_task)
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 108))
        task.item, task.widget = item, widget
        self.list.addItem(item)
        self.list.setItemWidget(item, widget)
        widget.play_intro()
        self.list.scrollToBottom()

        if start_now:
            self.start_task(task)
        self.update_footer()
        return True

    def running_count(self):
        return sum(1 for t in self.tasks if t.status == "running")

    def pump_queue(self):
        self._zombies = [w for w in self._zombies if w.isRunning()]
        """Bos slot varsa siradaki isaretli gorevi baslatir."""
        limit = self.parallel_spin.value()
        for t in self.tasks:
            if self.running_count() >= limit:
                break
            if t.status == "queued" and getattr(t, "wanted", False):
                self.start_task(t, force=True)
        self.update_footer()

    def start_all(self):
        for t in self.tasks:
            if t.status in ("queued", "error", "stopped"):
                t.status = "queued"
                t.wanted = True
                t.set_detail("st_queued")
                t.widget.refresh()
        self.pump_queue()

    def start_task(self, task, force=False):
        if task.status == "running":
            return
        task.wanted = True
        if not force and self.running_count() >= self.parallel_spin.value():
            task.status = "queued"
            task.set_detail("st_queued")
            task.widget.refresh()
            self.update_footer()
            return

        out_path = unique_path(os.path.join(task.out_dir, task.name))
        sounds.play("download")
        task.status = "running"
        task.progress = 0.0
        task.set_detail("st_starting")
        task.widget.refresh()

        w = DownloadWorker(task.url, self.headers(), out_path,
                           self.threads_spin.value(), self.remux_check.isChecked(),
                           find_ffmpeg())
        task.worker = w
        w.state.connect(lambda s, t=task: self._on_state(t, s))
        w.quality.connect(lambda q, t=task: self._on_quality(t, q))
        w.progress.connect(
            lambda d, n, mb, sp, av, rt, rg, ms, t=task:
            self._on_progress(t, d, n, mb, sp, av, rt, rg, ms))
        w.preview.connect(lambda p, t=task: self.grabber.request(t, p))
        w.finished_ok.connect(
            lambda p, t=task, wk=w: (setattr(t, "missing", len(wk._missing)),
                                     setattr(t, "partial", wk._partial),
                                     self._on_done(t, p)))
        w.failed.connect(lambda e, t=task: self._on_failed(t, e))
        w.log.connect(lambda m, t=task: self.status.setText("%s — %s" % (t.name, m)))
        log.info("BASLADI '%s' | %s | hedef=%s | segment baglantisi=%d | remux=%s",
                 task.name, task.url, out_path, self.threads_spin.value(),
                 self.remux_check.isChecked())
        w.start()
        self.update_footer()

    def stop_task(self, task):
        if task.worker:
            task.worker.cancel()
            task.set_detail("st_stopping")
            task.widget.refresh()

    def remove_task(self, task):
        if task.worker:
            try:
                task.worker.disconnect()
            except (TypeError, RuntimeError):
                pass
            task.worker.cancel()
            self._zombies.append(task.worker)
            task.worker = None
        row = self.list.row(task.item)
        if row >= 0:
            self.list.takeItem(row)
        task.widget = None
        task.item = None
        if task in self.tasks:
            self.tasks.remove(task)
        self.update_footer()

    def open_task(self, task):
        if task.result_path and os.path.exists(task.result_path):
            reveal_in_folder(task.result_path)

    def clear_done(self):
        for t in [t for t in self.tasks if t.status == "done"]:
            self.remove_task(t)

    def clear_all(self):
        if not self.tasks:
            return
        if QMessageBox.question(self, tr("msg_clear_title"), tr("msg_clear_body")) \
                != QMessageBox.StandardButton.Yes:
            return
        for t in list(self.tasks):
            self.remove_task(t)

    def _on_state(self, task, text):
        if task.widget is None:
            return
        log.info("DURUM '%s' -> %s", task.name, text)
        task.set_detail_raw(text)
        task.widget.refresh()

    def _on_quality(self, task, q):
        if task.widget is None:
            return
        task.quality = q
        task.widget.refresh()

    def _on_progress(self, task, done, total, mb, speed, avg, retries, retrying, missing):
        if task.widget is None:
            return
        task.progress = (done / total) if total else 0.0
        detail = tr("pr_line", done, total, task.progress * 100, mb, speed, avg)
        if retrying:
            detail += tr("pr_stuck", retrying)
        elif retries:
            detail += tr("pr_retries", retries)
        if missing:
            detail += tr("pr_skipped", missing)
        if not retrying and total - done and total - done < self.threads_spin.value():
            detail += tr("pr_last")
        task.set_detail_raw(detail)
        task.widget.refresh()

    def _on_done(self, task, path):
        if task.widget is None:
            return
        sounds.play("done")
        task.status = "done"
        task.progress = 1.0
        task.result_path = path
        task.wanted = False
        size = os.path.getsize(path) / 1048576.0 if os.path.exists(path) else 0
        part = getattr(task, "partial", 0)
        miss = getattr(task, "missing", 0)
        if part:
            task.set_detail("done_partial", part, size, os.path.basename(path))
        elif miss:
            task.set_detail("done_missing", miss, size, os.path.basename(path))
        else:
            task.set_detail("done_line", size, os.path.basename(path))
        task.widget.refresh()
        self.update_footer()

    def _on_failed(self, task, msg):
        if task.widget is None:
            return
        log.error("GOREV BASARISIZ '%s': %s", task.name, msg)
        cancelled = msg in (tr("w_cancelled"), STRINGS["w_cancelled"][0],
                            STRINGS["w_cancelled"][1])
        if not cancelled:
            sounds.play("error")
        task.status = "stopped" if cancelled else "error"
        task.wanted = False
        if cancelled:
            task.set_detail("st_stopped")
        else:
            task.set_detail("st_error", msg[:120])
        task.widget.refresh()
        self.update_footer()

    def on_thumb_ready(self, task, img):
        if task.widget is None:
            return
        log.info("Thumbnail hazir '%s' (%dx%d)", task.name, img.width(), img.height())
        if task.widget:
            task.widget.set_thumb(img)

    def on_clipboard(self):
        if not self.clip_check.isChecked():
            return
        try:
            text = (self.clipboard.text() or "").strip()
        except RuntimeError:
            return
        if not text or text == self._last_clip or len(text) > 2000:
            return
        m = re.search(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', text)
        if not m:
            return
        url = m.group(0)
        self._last_clip = text
        if any(t.url == url and t.status in ("queued", "running") for t in self.tasks):
            return
        sounds.play("pop")
        self.toast.show_for(url)

    def change_language(self, code):
        set_language(code)
        self.flag_en.setChecked(current_language() == "en")
        self.flag_tr.setChecked(current_language() == "tr")
        self.settings.setValue("lang", current_language())
        self.settings.sync()
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(tr("app_title"))
        self.header_sub.setText(tr("tagline"))
        self.clip_check.setText(tr("clip_watch"))
        self.clip_check.setToolTip(tr("clip_watch_tip"))
        self.flag_en.setToolTip(tr("lang_tip_en"))
        self.flag_tr.setToolTip(tr("lang_tip_tr"))

        self.tabs.setTabText(0, tr("tab_downloader"))
        self.tabs.setTabText(1, tr("tab_about"))
        self.about_page.retranslate()

        self.url_edit.setPlaceholderText(tr("url_placeholder"))
        self.add_btn.setText(tr("add_queue"))
        self.now_btn.setText(tr("download_now"))
        self.bulk_btn.setText(tr("bulk_add"))
        self.dir_label.setText(tr("save_folder"))
        self.browse_btn.setText(tr("browse"))

        self.lbl_referer.setText(tr("referer"))
        self.lbl_cookie.setText(tr("cookie"))
        self.referer_edit.setPlaceholderText(tr("referer_ph"))
        self.cookie_edit.setPlaceholderText(tr("cookie_ph"))
        self.lbl_threads.setText(tr("seg_conn"))
        self.lbl_parallel.setText(tr("parallel_video"))
        self.autostart_check.setText(tr("autostart"))
        self.ffmpeg_btn.setToolTip(tr("ffmpeg_btn_tip"))
        self.refresh_ffmpeg_state()

        self.queue_title.setText(tr("queue_title"))
        for btn, key in self.queue_buttons:
            btn.setText(tr(key))
        self.empty_label.setText(tr("queue_empty"))

        self.status.setText(tr("ready"))
        self.toast.retranslate()
        for t in self.tasks:
            if t.widget is not None:
                t.widget.retranslate()
        self.update_footer()

    def _check_responsive(self):
        now = time.time()
        lag = now - self._wd_last - 0.25
        self._wd_last = now
        if lag > 0.75:
            log.warning("ARAYUZ %.2f saniye takildi (olay dongusu blokelendi)", lag)

    def update_footer(self):
        run = sum(1 for t in self.tasks if t.status == "running")
        q = sum(1 for t in self.tasks if t.status == "queued")
        d = sum(1 for t in self.tasks if t.status == "done")
        e = sum(1 for t in self.tasks if t.status in ("error", "stopped"))
        self.hint.setText(tr("footer_stats", run, q, d, e))
        self.empty_label.setVisible(not self.tasks)
        self.list.setVisible(bool(self.tasks))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.toast.reposition()

    def closeEvent(self, event):
        self._save_settings()
        for t in self.tasks:
            if t.status == "running" and t.worker:
                t.worker.cancel()
        for t in self.tasks:
            if t.worker:
                t.worker.wait(2500)
        self.grabber.shutdown()
        sounds.shutdown()
        shutil.rmtree(APP_TMP, ignore_errors=True)
        event.accept()
