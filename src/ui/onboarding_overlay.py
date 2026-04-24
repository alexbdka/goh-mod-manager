from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, QPoint, QRectF, Qt
from PySide6.QtGui import QAction, QColor, QKeyEvent, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.ui.language_change_mixin import LanguageChangeMixin


@dataclass(frozen=True)
class OnboardingStep:
    """Single onboarding step describing a target widget or action plus copy."""

    target: QWidget | QAction | list[QWidget | QAction] | None
    title: str
    body: str


class OnboardingOverlay(LanguageChangeMixin, QWidget):
    """Lightweight first-run tour overlay that highlights existing UI elements."""

    def __init__(
        self,
        parent: QMainWindow,
        steps: list[OnboardingStep],
        on_finished: Callable[[], None] | None = None,
    ):
        super().__init__(parent)
        self._steps = steps
        self._on_finished = on_finished
        self._index = 0
        self._highlight_rect = QRectF()
        self._highlight_rects: list[QRectF] = []

        self._setup_ui()
        self._sync_geometry()
        self.hide()
        parent.installEventFilter(self)

    def _setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._card = QFrame(self)
        self._card.setAutoFillBackground(True)
        self._card.setFrameShape(QFrame.Shape.StyledPanel)
        self._card.setFrameShadow(QFrame.Shadow.Raised)

        layout = QVBoxLayout(self._card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        self._title_label = QLabel(self._card)
        self._title_label.setWordWrap(True)
        self._title_label.setStyleSheet("font-weight: 600; font-size: 15px;")
        layout.addWidget(self._title_label)

        self._body_label = QLabel(self._card)
        self._body_label.setWordWrap(True)
        layout.addWidget(self._body_label)

        self._step_label = QLabel(self._card)
        self._step_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self._step_label)

        button_row = QHBoxLayout()
        self._skip_button = QPushButton(self._card)
        self._back_button = QPushButton(self._card)
        self._next_button = QPushButton(self._card)

        self._skip_button.clicked.connect(self.finish)
        self._back_button.clicked.connect(self._previous_step)
        self._next_button.clicked.connect(self._next_step)

        button_row.addWidget(self._skip_button)
        button_row.addStretch(1)
        button_row.addWidget(self._back_button)
        button_row.addWidget(self._next_button)
        layout.addLayout(button_row)

    def start(self):
        """Show the overlay and jump to the first step."""
        if not self._steps:
            self.finish()
            return

        self._index = 0
        self._sync_geometry()
        self._update_step()
        self.show()
        self.raise_()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def finish(self):
        """Hide the overlay and notify the caller that the tour completed."""
        self.hide()
        if self._on_finished:
            self._on_finished()

    def retranslate_ui(self):
        self._skip_button.setText(self.tr("Skip"))
        self._back_button.setText(self.tr("Back"))
        is_last = self._index == len(self._steps) - 1
        self._next_button.setText(self.tr("Done") if is_last else self.tr("Next"))
        self._step_label.setText(
            self.tr("Step {current} of {total}").format(
                current=self._index + 1,
                total=len(self._steps),
            )
        )

    def _update_step(self):
        """Refresh the card copy and highlight geometry for the current step."""
        step = self._steps[self._index]
        self._title_label.setText(step.title)
        self._body_label.setText(step.body)
        self._back_button.setEnabled(self._index > 0)
        self._update_highlight_rects(step.target)
        self.retranslate_ui()
        self._position_card()
        self.update()

    def _previous_step(self):
        if self._index <= 0:
            return
        self._index -= 1
        self._update_step()

    def _next_step(self):
        if self._index >= len(self._steps) - 1:
            self.finish()
            return
        self._index += 1
        self._update_step()

    def _update_highlight_rects(
        self, target: QWidget | QAction | list[QWidget | QAction] | None
    ):
        """Resolve one or more targets into screen-space highlight rectangles."""
        targets = target if isinstance(target, list) else [target]
        rects = [
            rect
            for rect in (self._rect_for_target(item) for item in targets)
            if rect is not None
        ]
        self._highlight_rects = rects

        if not rects:
            self._highlight_rect = QRectF()
            return

        combined = QRectF(rects[0])
        for rect in rects[1:]:
            combined = combined.united(rect)
        self._highlight_rect = combined

    def _rect_for_target(self, target: QWidget | QAction | None) -> QRectF | None:
        if isinstance(target, QAction):
            return self._rect_for_action(target)
        return self._rect_for_widget(target)

    def _rect_for_widget(self, widget: QWidget | None) -> QRectF | None:
        if widget is None or not widget.isVisible():
            return None

        top_left = self.mapFromGlobal(widget.mapToGlobal(QPoint(0, 0)))
        return QRectF(top_left.x(), top_left.y(), widget.width(), widget.height())

    def _rect_for_action(self, action: QAction) -> QRectF | None:
        """Resolve a top-level menu action into a rectangle inside the overlay."""
        parent = self.parentWidget()
        if not isinstance(parent, QMainWindow):
            return None

        menu_bar = parent.menuBar()
        if not isinstance(menu_bar, QMenuBar):
            return None

        action_rect = menu_bar.actionGeometry(action)
        if action_rect.isNull():
            return None

        top_left = self.mapFromGlobal(menu_bar.mapToGlobal(action_rect.topLeft()))
        return QRectF(
            top_left.x(),
            top_left.y(),
            action_rect.width(),
            action_rect.height(),
        )

    def _position_card(self):
        """Place the explanation card beside the current highlight when possible."""
        margin = 18
        available_width = max(260, self.width() - margin * 2)
        max_width = min(460, available_width)
        self._card.setMaximumWidth(max_width)
        self._card.setMinimumWidth(min(300, max_width))
        self._card.adjustSize()
        card_size = self._card.sizeHint()
        self._card.resize(card_size)

        if self._highlight_rect.isNull():
            x = (self.width() - card_size.width()) // 2
            y = (self.height() - card_size.height()) // 2
            self._card.move(max(margin, x), max(margin, y))
            return

        rect = self._highlight_rect.toRect()
        right_space = self.width() - rect.right() - margin
        left_space = rect.left() - margin
        below_space = self.height() - rect.bottom() - margin

        if right_space >= card_size.width():
            x = rect.right() + margin
            y = self._clamp(
                rect.top(), margin, self.height() - card_size.height() - margin
            )
        elif left_space >= card_size.width():
            x = rect.left() - margin - card_size.width()
            y = self._clamp(
                rect.top(), margin, self.height() - card_size.height() - margin
            )
        elif below_space >= card_size.height():
            x = self._clamp(
                rect.left(), margin, self.width() - card_size.width() - margin
            )
            y = rect.bottom() + margin
        else:
            x = self._clamp(
                rect.left(), margin, self.width() - card_size.width() - margin
            )
            y = max(margin, rect.top() - margin - card_size.height())

        self._card.move(x, y)

    def _sync_geometry(self):
        """Keep the overlay stretched over its parent widget."""
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.rect())

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is self.parentWidget() and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Move,
        ):
            if self.isVisible():
                self._sync_geometry()
                self._update_highlight_rects(self._steps[self._index].target)
                self._position_card()
                self.update()
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.finish()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Right):
            self._next_step()
            return
        if event.key() == Qt.Key.Key_Left:
            self._previous_step()
            return
        super().keyPressEvent(event)

    def paintEvent(self, _event):
        """Dim the background and draw the current highlight outline."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        overlay_path = QPainterPath()
        overlay_path.addRect(QRectF(self.rect()))
        for rect in self._highlight_rects:
            overlay_path = overlay_path.subtracted(self._highlight_path(rect))

        painter.fillPath(overlay_path, QColor(0, 0, 0, 155))

        pen = QPen(QColor(88, 166, 255, 235), 3)
        painter.setPen(pen)
        for rect in self._highlight_rects:
            painter.drawPath(self._highlight_path(rect))

    @staticmethod
    def _highlight_path(rect: QRectF) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(rect.adjusted(-6, -6, 6, 6), 8, 8)
        return path

    @staticmethod
    def _clamp(value: int, minimum: int, maximum: int) -> int:
        if maximum < minimum:
            return minimum
        return max(minimum, min(maximum, value))
