import re
from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QTimer, Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QToolButton, QVBoxLayout
from .i18n import tr
from .theme import C_MUTED, C_OK, C_TEXT


class BulkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("bulk_title"))
        self.resize(660, 440)
        lay = QVBoxLayout(self)
        info = QLabel(tr("bulk_info"))
        info.setStyleSheet("color:%s;" % C_MUTED)
        lay.addWidget(info)

        self.edit = QPlainTextEdit()
        self.edit.setPlaceholderText(
            "https://site.com/video1/master.m3u8\n"
            "https://site.com/video2/index.m3u8 | bolum-2.mp4")
        self.edit.textChanged.connect(self._update_count)
        lay.addWidget(self.edit, 1)

        self.count = QLabel(tr("bulk_count", 0))
        self.count.setStyleSheet("color:%s;" % C_MUTED)
        lay.addWidget(self.count)

        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                               QDialogButtonBox.StandardButton.Cancel)
        box.button(QDialogButtonBox.StandardButton.Ok).setText(tr("bulk_ok"))
        box.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("bulk_cancel"))
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        lay.addWidget(box)

    def _parse(self):
        out = []
        for line in self.edit.toPlainText().splitlines():
            line = line.strip()
            if not line:
                continue
            name = ""
            if "|" in line:
                line, name = [x.strip() for x in line.split("|", 1)]
            m = re.search(r'https?://\S+', line)
            if not m:
                continue
            url = m.group(0).rstrip('",\'')
            out.append((url, name))
        return out

    def _update_count(self):
        n = len(self._parse())
        self.count.setText(tr("bulk_count", n))
        self.count.setStyleSheet("color:%s;" % (C_OK if n else C_MUTED))

    def links(self):
        return self._parse()


class ClipboardToast(QFrame):
    download_now = pyqtSignal(str)
    add_queue = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("toast")
        self.url = ""
        self.setFixedSize(360, 148)
        self.hide()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        top = QHBoxLayout()
        self.title_lbl = title = QLabel(tr("toast_title"))
        title.setStyleSheet("color:%s; font-weight:700; font-size:13px;" % C_TEXT)
        top.addWidget(title, 1)
        close = QToolButton()
        close.setText("✕")
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setStyleSheet("QToolButton{color:%s;border:none;font-size:13px;}"
                            "QToolButton:hover{color:%s;}" % (C_MUTED, C_TEXT))
        close.clicked.connect(self.dismiss)
        top.addWidget(close)
        lay.addLayout(top)

        self.link = QLabel("")
        self.link.setStyleSheet("color:%s; font-size:11px;" % C_MUTED)
        self.link.setWordWrap(False)
        lay.addWidget(self.link)
        lay.addStretch(1)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.btn_now = QPushButton(tr("download_now"))
        self.btn_now.setObjectName("primary")
        self.btn_now.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_queue = QPushButton(tr("add_queue"))
        self.btn_queue.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_now.clicked.connect(lambda: (self.download_now.emit(self.url), self.dismiss()))
        self.btn_queue.clicked.connect(lambda: (self.add_queue.emit(self.url), self.dismiss()))
        row.addWidget(self.btn_now, 1)
        row.addWidget(self.btn_queue, 1)
        lay.addLayout(row)

        self._anim = QPropertyAnimation(self, b"pos", self)
        self._anim.setDuration(320)
        self._dismissing = False
        self._anim.finished.connect(self._on_anim_finished)
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.dismiss)

    def _on_anim_finished(self):
        if self._dismissing:
            self._dismissing = False
            self.hide()

    def retranslate(self):
        self.title_lbl.setText(tr("toast_title"))
        self.btn_now.setText(tr("download_now"))
        self.btn_queue.setText(tr("add_queue"))

    def show_for(self, url):
        self.url = url
        self._dismissing = False
        short = url if len(url) < 52 else url[:26] + " … " + url[-22:]
        self.link.setText(short)
        p = self.parentWidget()
        end = QPoint(p.width() - self.width() - 24, p.height() - self.height() - 24)
        start = QPoint(end.x(), p.height() + 20)
        self.move(start)
        self.show()
        self.raise_()
        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self._anim.start()
        self._hide_timer.start(20000)

    def dismiss(self):
        if not self.isVisible() or self._dismissing:
            return
        self._hide_timer.stop()
        p = self.parentWidget()
        self._anim.stop()
        self._dismissing = True
        self._anim.setStartValue(self.pos())
        self._anim.setEndValue(QPoint(self.x(), p.height() + 20))
        self._anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim.start()

    def reposition(self):
        if self.isVisible():
            p = self.parentWidget()
            self.move(p.width() - self.width() - 24, p.height() - self.height() - 24)
