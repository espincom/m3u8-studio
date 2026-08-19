import math
from PyQt6.QtCore import QPointF, QRectF, QTimer, QUrl, Qt
from PyQt6.QtGui import QBrush, QColor, QDesktopServices, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from .i18n import tr
from .theme import C_ACCENT, C_ACCENT_2, C_BG, C_MUTED, C_TEXT
from .widgets import ContactCard


class AboutPage(QWidget):

    MAIL = "kayhankafali@gmail.com"
    MAIL_SHOWN = "@kayhankafali"
    GITHUB = "https://github.com/espincom"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 30, 40, 26)
        lay.setSpacing(0)
        lay.addStretch(1)

        self.logo = QLabel("⬇")
        self.logo.setFixedSize(76, 76)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 %s, stop:1 %s);"
            "border-radius: 22px; color: white; font-size: 34px; font-weight: 800;"
            % (C_ACCENT, C_ACCENT_2))
        lay.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(16)

        self.title = QLabel("M3U8 Studio")
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title.setStyleSheet("font-size: 30px; font-weight: 800; letter-spacing: 1px;")
        lay.addWidget(self.title)
        lay.addSpacing(4)

        self.sub = QLabel("")
        self.sub.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.sub.setStyleSheet("color:%s; font-size: 12px;" % C_MUTED)
        lay.addWidget(self.sub)
        lay.addSpacing(22)

        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.message.setWordWrap(True)
        self.message.setStyleSheet("font-size: 14px; color:%s;" % C_TEXT)
        lay.addWidget(self.message)
        lay.addSpacing(18)

        self.by = QLabel("By espin0")
        self.by.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.by.setFixedHeight(30)
        self.by.setStyleSheet(
            "color: white; font-size: 12px; font-weight: 700; padding: 0 18px;"
            "border-radius: 15px;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 %s, stop:1 %s);"
            % (C_ACCENT, C_ACCENT_2))
        lay.addWidget(self.by, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(22)

        cards = QVBoxLayout()
        cards.setSpacing(12)
        self.mail_card = ContactCard("✉", "Gmail", self.MAIL_SHOWN, C_ACCENT)
        self.mail_card.setToolTip(self.MAIL)
        self.mail_card.clicked.connect(self._open_mail)
        self.git_card = ContactCard("</>", "GitHub", "github.com/espincom", C_ACCENT_2)
        self.git_card.setToolTip(self.GITHUB)
        self.git_card.clicked.connect(self._open_github)
        holder = QHBoxLayout()
        holder.addStretch(1)
        inner = QVBoxLayout()
        inner.setSpacing(12)
        inner.addWidget(self.mail_card)
        inner.addWidget(self.git_card)
        holder.addLayout(inner)
        holder.addStretch(1)
        cards.addLayout(holder)
        lay.addLayout(cards)

        lay.addSpacing(18)
        self.foot = QLabel("")
        self.foot.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.foot.setStyleSheet("color:%s; font-size: 11px;" % C_MUTED)
        lay.addWidget(self.foot)
        lay.addStretch(2)

        self.retranslate()

    def retranslate(self):
        self.sub.setText(tr("tagline"))
        self.message.setText(tr("ab_message"))
        self.by.setText(tr("ab_by"))
        self.mail_card.set_texts(tr("ab_mail_label"), tr("ab_mail_hint"))
        self.git_card.set_texts(tr("ab_github_label"), tr("ab_github_hint"))
        self.foot.setText("")

    def _tick(self):
        self._phase = (self._phase + 0.004) % 1.0
        self.update()

    def _open_mail(self):
        QApplication.clipboard().setText(self.MAIL)
        QDesktopServices.openUrl(QUrl("mailto:" + self.MAIL))
        self._flash(tr("ab_copied"))

    def _open_github(self):
        QDesktopServices.openUrl(QUrl(self.GITHUB))

    def _flash(self, text):
        self.foot.setText(text)
        QTimer.singleShot(2200, lambda: self.foot.setText(""))

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        p.fillRect(r, QColor(C_BG))

        ph = self._phase * 2 * math.pi
        for i, color in enumerate((QColor(C_ACCENT), QColor(C_ACCENT_2))):
            cx = r.center().x() + math.cos(ph + i * 2.1) * r.width() * 0.26
            cy = r.center().y() + math.sin(ph * 1.3 + i * 1.7) * r.height() * 0.28
            rad = min(r.width(), r.height()) * (0.55 + 0.05 * math.sin(ph + i))
            grad = QRadialGradient(QPointF(cx, cy), rad)
            c = QColor(color)
            c.setAlpha(46)
            grad.setColorAt(0.0, c)
            c2 = QColor(color)
            c2.setAlpha(0)
            grad.setColorAt(1.0, c2)
            p.fillRect(r, QBrush(grad))

        p.setPen(QPen(QColor(255, 255, 255, 8), 1))
        step = 32
        x = int(r.left())
        while x < r.right():
            p.drawLine(x, int(r.top()), x, int(r.bottom()))
            x += step
        y = int(r.top())
        while y < r.bottom():
            p.drawLine(int(r.left()), y, int(r.right()), y)
            y += step
