from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class Spinner(QWidget):
    """Petit spinner circulaire dessiné à la main (sans GIF externe)."""

    def __init__(self, parent=None, size: int = 28, color: str = "#4dabf7",
                 line_width: int = 3, interval_ms: int = 30):
        super().__init__(parent)
        self._size = size
        self._color = QColor(color)
        self._line_width = line_width
        self._angle = 0

        self.setFixedSize(QSize(size, size))

        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self._on_tick)

    def start(self) -> None:
        if not self._timer.isActive():
            self._timer.start()
        self.show()

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def _on_tick(self) -> None:
        self._angle = (self._angle + 12) % 360
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pad = self._line_width + 1
        rect = self.rect().adjusted(pad, pad, -pad, -pad)

        # piste de fond (très faible alpha)
        bg = QColor(self._color)
        bg.setAlphaF(0.18)
        pen_bg = QPen(bg, self._line_width)
        pen_bg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)

        # arc actif
        pen_fg = QPen(self._color, self._line_width)
        pen_fg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_fg)
        # 270° d'arc qui tourne
        start = -self._angle * 16
        painter.drawArc(rect, start, 270 * 16)


class SpinnerWithLabel(QWidget):
    """Spinner + label horizontal, utile dans un placeholder."""

    def __init__(self, text: str = "Chargement…", parent=None):
        super().__init__(parent)
        self._spinner = Spinner(self)
        self._label = QLabel(text)
        self._label.setObjectName("subtitle")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()
        layout.addWidget(self._spinner)
        layout.addWidget(self._label)
        layout.addStretch()

    def set_text(self, text: str) -> None:
        self._label.setText(text)

    def start(self) -> None:
        self._spinner.start()
        self.show()

    def stop(self) -> None:
        self._spinner.stop()
        self.hide()
