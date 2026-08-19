import math
from PyQt6.QtCore import QEasingCurve, QPointF, QPropertyAnimation, QRectF, QTimer, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import QAbstractButton, QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QSizePolicy, QToolButton, QVBoxLayout, QWidget
from .i18n import tr
from .theme import C_ACCENT, C_ACCENT_2, C_BORDER, C_ERR, C_MUTED, C_OK, C_SURFACE_2, C_TEXT, C_WARN


class Meter(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._shine = 0.0
        self._active = False
        self._color = QColor(C_ACCENT)
        self.setFixedHeight(8)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._anim = QPropertyAnimation(self, b"value", self)
        self._anim.setDuration(400)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._shine_timer = QTimer(self)
        self._shine_timer.setInterval(33)
        self._shine_timer.timeout.connect(self._tick)

    def _tick(self):
        self._shine = (self._shine + 0.02) % 1.6
        self.update()

    def getValue(self):
        return self._value

    def setValue(self, v):
        self._value = max(0.0, min(1.0, float(v)))
        self.update()

    value = pyqtProperty(float, fget=getValue, fset=setValue)

    def animate_to(self, v):
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(max(0.0, min(1.0, float(v))))
        self._anim.start()

    def set_active(self, active):
        self._active = active
        if active and not self._shine_timer.isActive():
            self._shine_timer.start()
        elif not active:
            self._shine_timer.stop()
            self.update()

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        radius = r.height() / 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#232936"))
        p.drawRoundedRect(r, radius, radius)

        w = r.width() * self._value
        if w <= 0:
            return
        fill = QRectF(0, 0, w, r.height())
        grad = QLinearGradient(0, 0, max(w, 1), 0)
        grad.setColorAt(0.0, self._color)
        grad.setColorAt(1.0, QColor(C_ACCENT_2) if self._color.name() == QColor(C_ACCENT).name()
                        else self._color.lighter(125))
        path = QPainterPath()
        path.addRoundedRect(fill, radius, radius)
        p.setClipPath(path)
        p.fillRect(fill, QBrush(grad))

        if self._active:
            x = (self._shine - 0.3) * r.width()
            shine = QLinearGradient(x, 0, x + r.width() * 0.28, 0)
            shine.setColorAt(0.0, QColor(255, 255, 255, 0))
            shine.setColorAt(0.5, QColor(255, 255, 255, 70))
            shine.setColorAt(1.0, QColor(255, 255, 255, 0))
            p.fillRect(fill, QBrush(shine))


class Thumb(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(132, 76)
        self._pix = None
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._tick)
        self._timer.start()
        self._fade = 0.0

    def _tick(self):
        self._phase = (self._phase + 0.022) % 2.0
        if self._pix is not None and self._fade < 1.0:
            self._fade = min(1.0, self._fade + 0.08)
        elif self._pix is not None:
            self._timer.stop()
        self.update()

    def set_image(self, img: QImage):
        pix = QPixmap.fromImage(img).scaled(
            self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation)
        self._pix = pix
        self._fade = 0.0
        if not self._timer.isActive():
            self._timer.start()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(r, 10, 10)
        p.setClipPath(path)

        p.fillRect(r, QColor("#1b2130"))
        if self._pix is None:
            x = (self._phase - 0.5) * r.width()
            g = QLinearGradient(x, 0, x + r.width() * 0.6, r.height())
            g.setColorAt(0.0, QColor(255, 255, 255, 0))
            g.setColorAt(0.5, QColor(255, 255, 255, 16))
            g.setColorAt(1.0, QColor(255, 255, 255, 0))
            p.fillRect(r, QBrush(g))
            p.setPen(QPen(QColor(C_MUTED)))
            f = QFont(); f.setPointSize(16)
            p.setFont(f)
            p.drawText(r, Qt.AlignmentFlag.AlignCenter, "▶")
        else:
            p.setOpacity(self._fade)
            p.drawPixmap(self.rect(), self._pix,
                         self._pix.rect().adjusted(
                             max(0, (self._pix.width() - self.width()) // 2), 0,
                             -max(0, (self._pix.width() - self.width()) // 2), 0))
            p.setOpacity(1.0)
        p.setClipping(False)
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r.adjusted(0.5, 0.5, -0.5, -0.5), 10, 10)


def icon_button(glyph, tooltip, color=C_TEXT, size=32):
    b = QToolButton()
    b.setText(glyph)
    b.setToolTip(tooltip)
    b.setFixedSize(size, size)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet("""
        QToolButton {
            background: %s; color: %s; border: 1px solid %s;
            border-radius: %dpx; font-size: 14px;
        }
        QToolButton:hover { background: #2b3242; border-color: %s; }
        QToolButton:pressed { background: #333c50; }
        QToolButton:disabled { color: #4a5164; border-color: #222836; background: #171c26; }
    """ % (C_SURFACE_2, color, C_BORDER, size // 2, C_ACCENT))
    return b


class FlagButton(QAbstractButton):

    def __init__(self, code, parent=None):
        super().__init__(parent)
        self.code = code
        self.setCheckable(True)
        self.setFixedSize(38, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hover = 0.0
        self._anim = QPropertyAnimation(self, b"hover", self)
        self._anim.setDuration(160)

    def getHover(self):
        return self._hover

    def setHover(self, v):
        self._hover = float(v)
        self.update()

    hover = pyqtProperty(float, fget=getHover, fset=setHover)

    def enterEvent(self, e):
        self._anim.stop(); self._anim.setEndValue(1.0); self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._anim.stop(); self._anim.setEndValue(0.0); self._anim.start()
        super().leaveEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(2, 2, self.width() - 4, self.height() - 4)
        path = QPainterPath()
        path.addRoundedRect(r, 5, 5)
        p.save()
        p.setClipPath(path)

        if self.code == "tr":
            p.fillRect(r, QColor("#E30A17"))
            cx, cy, rad = r.left() + r.width() * 0.38, r.center().y(), r.height() * 0.30
            p.setBrush(QColor("white")); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), rad, rad)
            p.setBrush(QColor("#E30A17"))
            p.drawEllipse(QPointF(cx + rad * 0.34, cy), rad * 0.80, rad * 0.80)
            p.setBrush(QColor("white"))
            star = QPainterPath()
            sx, sy, sr = r.left() + r.width() * 0.62, cy, r.height() * 0.17
            for i in range(5):
                ang = math.radians(-90 + i * 144)
                px, py = sx + sr * math.cos(ang), sy + sr * math.sin(ang)
                if i == 0:
                    star.moveTo(px, py)
                else:
                    star.lineTo(px, py)
            star.closeSubpath()
            p.drawPath(star)
        else:
            p.fillRect(r, QColor("#012169"))
            pen_w = r.height() * 0.20
            p.setPen(QPen(QColor("white"), pen_w))
            p.drawLine(QPointF(r.left(), r.top()), QPointF(r.right(), r.bottom()))
            p.drawLine(QPointF(r.right(), r.top()), QPointF(r.left(), r.bottom()))
            p.setPen(QPen(QColor("#C8102E"), pen_w * 0.5))
            p.drawLine(QPointF(r.left(), r.top()), QPointF(r.right(), r.bottom()))
            p.drawLine(QPointF(r.right(), r.top()), QPointF(r.left(), r.bottom()))
            p.setPen(QPen(QColor("white"), r.height() * 0.34))
            p.drawLine(QPointF(r.center().x(), r.top()), QPointF(r.center().x(), r.bottom()))
            p.drawLine(QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y()))
            p.setPen(QPen(QColor("#C8102E"), r.height() * 0.19))
            p.drawLine(QPointF(r.center().x(), r.top()), QPointF(r.center().x(), r.bottom()))
            p.drawLine(QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y()))

        p.restore()
        if self.isChecked():
            p.setPen(QPen(QColor(C_ACCENT), 2))
        else:
            alpha = int(60 + 120 * self._hover)
            p.setPen(QPen(QColor(255, 255, 255, alpha), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 5, 5)
        if not self.isChecked():
            p.fillPath(path, QColor(0, 0, 0, int(90 - 70 * self._hover)))


class ContactCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, glyph, title, value, accent, parent=None):
        super().__init__(parent)
        self.glyph, self.value, self.accent = glyph, value, QColor(accent)
        self.title_text = title
        self.hint_text = ""
        self._glow = 0.0
        self.setFixedHeight(76)
        self.setMinimumWidth(300)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; border: none;")
        self._anim = QPropertyAnimation(self, b"glow", self)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def getGlow(self):
        return self._glow

    def setGlow(self, v):
        self._glow = float(v)
        self.update()

    glow = pyqtProperty(float, fget=getGlow, fset=setGlow)

    def set_texts(self, title, hint):
        self.title_text, self.hint_text = title, hint
        self.update()

    def enterEvent(self, e):
        self._anim.stop(); self._anim.setEndValue(1.0); self._anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._anim.stop(); self._anim.setEndValue(0.0); self._anim.start()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = self._glow
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)

        bg = QLinearGradient(r.topLeft(), r.bottomRight())
        bg.setColorAt(0.0, QColor(32, 38, 52).lighter(100 + int(12 * g)))
        bg.setColorAt(1.0, QColor(24, 29, 40).lighter(100 + int(10 * g)))
        path = QPainterPath()
        path.addRoundedRect(r, 14, 14)
        p.fillPath(path, QBrush(bg))

        pen = QPen(QColor(self.accent.red(), self.accent.green(), self.accent.blue(),
                          int(60 + 165 * g)), 1 + g)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 14, 14)

        ic = QRectF(r.left() + 14, r.center().y() - 20, 40, 40)
        icg = QLinearGradient(ic.topLeft(), ic.bottomRight())
        icg.setColorAt(0.0, self.accent.lighter(115))
        icg.setColorAt(1.0, self.accent.darker(130))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(icg))
        p.drawEllipse(ic)
        f = QFont()
        f.setPointSize(11 if len(self.glyph) > 1 else 14)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QPen(QColor("white")))
        p.drawText(ic, Qt.AlignmentFlag.AlignCenter, self.glyph)

        tx = ic.right() + 16
        f2 = QFont(); f2.setPointSize(8); f2.setBold(True)
        p.setFont(f2)
        p.setPen(QPen(QColor(C_MUTED)))
        p.drawText(QRectF(tx, r.top() + 14, r.width() - tx, 14),
                   Qt.AlignmentFlag.AlignVCenter, self.title_text.upper())
        f3 = QFont(); f3.setPointSize(11); f3.setBold(True)
        p.setFont(f3)
        p.setPen(QPen(QColor(C_TEXT)))
        p.drawText(QRectF(tx, r.top() + 29, r.width() - tx - 12, 20),
                   Qt.AlignmentFlag.AlignVCenter, self.value)
        if self.hint_text:
            f4 = QFont(); f4.setPointSize(8)
            p.setFont(f4)
            p.setPen(QPen(QColor(139, 147, 167, int(120 + 135 * g))))
            p.drawText(QRectF(tx, r.top() + 48, r.width() - tx - 12, 16),
                       Qt.AlignmentFlag.AlignVCenter, self.hint_text)

        p.setPen(QPen(QColor(255, 255, 255, int(40 + 150 * g)), 2))
        ax = r.right() - 22 + 4 * g
        ay = r.center().y()
        p.drawLine(QPointF(ax - 4, ay - 5), QPointF(ax + 1, ay))
        p.drawLine(QPointF(ax + 1, ay), QPointF(ax - 4, ay + 5))


class TaskWidget(QFrame):
    start_requested = pyqtSignal(object)
    stop_requested = pyqtSignal(object)
    remove_requested = pyqtSignal(object)
    open_requested = pyqtSignal(object)

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("taskCard")
        self.setFixedHeight(100)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(14)

        self.thumb = Thumb()
        lay.addWidget(self.thumb)

        mid = QVBoxLayout()
        mid.setSpacing(6)
        self.title = QLabel(task.name)
        self.title.setStyleSheet("color:%s; font-size:13px; font-weight:600;" % C_TEXT)
        self.title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        mid.addWidget(self.title)

        self.meter = Meter()
        mid.addWidget(self.meter)

        self.sub = QLabel(tr("st_queued"))
        self.sub.setStyleSheet("color:%s; font-size:11px;" % C_MUTED)
        mid.addWidget(self.sub)
        lay.addLayout(mid, 1)

        self.badge = QLabel("")
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge.setFixedWidth(74)
        self.badge.setStyleSheet(
            "color:%s; background:#202634; border-radius:9px; padding:3px 6px; font-size:11px;"
            % C_MUTED)
        lay.addWidget(self.badge)

        self.btn_start = icon_button("⬇", tr("tip_start"), C_ACCENT)
        self.btn_stop = icon_button("■", tr("tip_stop"), C_WARN)
        self.btn_open = icon_button("📂", tr("tip_open"))
        self.btn_del = icon_button("✕", tr("tip_remove"), C_ERR)
        for b in (self.btn_start, self.btn_stop, self.btn_open, self.btn_del):
            lay.addWidget(b)
        self.btn_start.clicked.connect(lambda: self.start_requested.emit(self.task))
        self.btn_stop.clicked.connect(lambda: self.stop_requested.emit(self.task))
        self.btn_open.clicked.connect(lambda: self.open_requested.emit(self.task))
        self.btn_del.clicked.connect(lambda: self.remove_requested.emit(self.task))

        self.refresh()

    def refresh(self):
        try:
            self._refresh()
        except RuntimeError:
            pass

    def _refresh(self):
        t = self.task
        self.title.setText(t.name)
        self.sub.setText(t.detail_text())
        self.badge.setText(t.quality or "-")

        running = t.status == "running"
        self.meter.set_active(running)
        if t.status == "done":
            self.meter.set_color(QColor(C_OK))
            self.meter.animate_to(1.0)
        elif t.status == "error":
            self.meter.set_color(QColor(C_ERR))
        else:
            self.meter.set_color(QColor(C_ACCENT))
            self.meter.animate_to(t.progress)

        colors = {"queued": C_MUTED, "running": C_ACCENT, "done": C_OK,
                  "error": C_ERR, "stopped": C_WARN}
        self.badge.setStyleSheet(
            "color:%s; background:#202634; border-radius:9px; padding:3px 6px; font-size:11px;"
            % colors.get(t.status, C_MUTED))

        self.btn_start.setEnabled(t.status in ("queued", "error", "stopped"))
        self.btn_stop.setEnabled(running)
        self.btn_open.setEnabled(t.status == "done" and bool(t.result_path))

    def retranslate(self):
        self.btn_start.setToolTip(tr("tip_start"))
        self.btn_stop.setToolTip(tr("tip_stop"))
        self.btn_open.setToolTip(tr("tip_open"))
        self.btn_del.setToolTip(tr("tip_remove"))
        self.refresh()

    def set_thumb(self, img):
        self.thumb.set_image(img)

    def play_intro(self):
        eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(eff)
        a = QPropertyAnimation(eff, b"opacity", self)
        a.setDuration(420)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.finished.connect(lambda: self.setGraphicsEffect(None))
        a.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
