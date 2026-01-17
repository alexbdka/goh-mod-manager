from dataclasses import dataclass
from typing import Callable, List, Optional

from PySide6.QtCore import QEvent, QPoint, QRectF, Qt
from PySide6.QtGui import QAction, QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGraphicsBlurEffect,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QHBoxLayout,
    QLabel,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class GuidedTourStep:
    target: Optional[object]
    title: str
    body: str


@dataclass(frozen=True)
class GuidedTourTargetAction:
    menu_bar: QMenuBar
    action: QAction


class GuidedTourOverlay(QWidget):
    def __init__(
        self,
        parent: QWidget,
        steps: List[GuidedTourStep],
        on_finish: Optional[Callable[[bool], None]] = None,
    ) -> None:
        super().__init__(parent)
        self._steps = steps
        self._index = 0
        self._highlight_rect = QRectF()
        self._highlight_rects: List[QRectF] = []
        self._on_finish = on_finish
        self._is_refreshing = False
        self._blur_pixmap = QPixmap()
        self._source_pixmap = QPixmap()

        self._setup_ui()
        self._sync_geometry()
        self.hide()
        parent.installEventFilter(self)

    def _setup_ui(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        self._card = QFrame(self)
        self._card.setObjectName("guidedTourCard")
        self._card.setStyleSheet(
            "QFrame#guidedTourCard {"
            "background: #1E1E1E;"
            "color: #FFFFFF;"
            "border-radius: 8px;"
            "}"
        )

        layout = QVBoxLayout(self._card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self._title_label = QLabel(self._card)
        self._title_label.setWordWrap(True)
        self._title_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(self._title_label)

        self._body_label = QLabel(self._card)
        self._body_label.setWordWrap(True)
        self._body_label.setContentsMargins(0, 2, 0, 2)
        layout.addWidget(self._body_label)

        self._step_label = QLabel(self._card)
        self._step_label.setStyleSheet("color: #B0B0B0; font-size: 11px;")
        layout.addWidget(self._step_label)

        self._dont_show_again = QCheckBox(self.tr("Don't show on startup"), self._card)
        layout.addWidget(self._dont_show_again)

        button_row = QHBoxLayout()
        button_row.addStretch(1)

        self._back_button = QPushButton(self.tr("Back"), self._card)
        self._next_button = QPushButton(self.tr("Next"), self._card)
        self._skip_button = QPushButton(self.tr("Skip"), self._card)

        self._back_button.clicked.connect(self._previous_step)
        self._next_button.clicked.connect(self._next_step)
        self._skip_button.clicked.connect(self._finish)

        button_row.addWidget(self._back_button)
        button_row.addWidget(self._next_button)
        button_row.addWidget(self._skip_button)

        layout.addLayout(button_row)

    def start(self) -> None:
        self._index = 0
        self._update_step()
        self._sync_geometry()
        self._refresh_blur(force=True)
        self.show()
        self.raise_()

    def _update_step(self) -> None:
        if not self._steps:
            self._finish()
            return

        step = self._steps[self._index]
        self._title_label.setText(step.title)
        self._body_label.setText(step.body)
        self._step_label.setText(
            self.tr("Step {current} of {total}").format(
                current=self._index + 1, total=len(self._steps)
            )
        )

        self._back_button.setEnabled(self._index > 0)
        is_last = self._index == len(self._steps) - 1
        self._next_button.setText(self.tr("Finish") if is_last else self.tr("Next"))

        self._update_highlight_rect(step.target)
        self._position_card()
        self.update()

    def _get_current_target(self) -> Optional[QWidget]:
        if not self._steps:
            return None
        return self._steps[self._index].target

    def _update_highlight_rect(self, target: Optional[object]) -> None:
        if target is None:
            self._highlight_rect = QRectF()
            self._highlight_rects = []
            return

        if isinstance(target, (list, tuple)):
            rects = [
                rect
                for rect in (self._rect_for_target(item) for item in target)
                if rect is not None
            ]
            if not rects:
                self._highlight_rect = QRectF()
                self._highlight_rects = []
                return
            combined = rects[0]
            for rect in rects[1:]:
                combined = combined.united(rect)
            self._highlight_rect = combined
            self._highlight_rects = rects
            return

        rect = self._rect_for_target(target)
        if rect is None:
            self._highlight_rect = QRectF()
            self._highlight_rects = []
        else:
            self._highlight_rect = rect
            self._highlight_rects = [rect]

    def _rect_for_target(self, target: object) -> Optional[QRectF]:
        if isinstance(target, GuidedTourTargetAction):
            return self._rect_for_action(target)

        if isinstance(target, QAction):
            parent = self.parentWidget()
            if parent is None:
                return None
            return self._rect_for_action(
                GuidedTourTargetAction(parent.menuBar(), target)
            )

        if isinstance(target, QWidget):
            if not target.isVisible():
                return None
            top_left = self.mapFromGlobal(target.mapToGlobal(QPoint(0, 0)))
            return QRectF(
                top_left.x(),
                top_left.y(),
                target.width(),
                target.height(),
            )

        return None

    def _rect_for_action(self, target: GuidedTourTargetAction) -> Optional[QRectF]:
        menu_bar = target.menu_bar
        action_rect = menu_bar.actionGeometry(target.action)
        if action_rect.isNull():
            return None
        top_left = self.mapFromGlobal(menu_bar.mapToGlobal(action_rect.topLeft()))
        return QRectF(
            top_left.x(),
            top_left.y(),
            action_rect.width(),
            action_rect.height(),
        )

    def _position_card(self) -> None:
        margin = 16
        available_width = max(0, self.width() - margin * 2)
        max_width = min(520, available_width)
        min_width = min(320, max_width)
        if max_width:
            self._card.setMaximumWidth(max_width)
            self._card.setMinimumWidth(min_width)
            self._card.adjustSize()
        card_size = self._card.sizeHint()
        self._card.resize(card_size)

        if self._highlight_rect.isNull():
            x = (self.width() - card_size.width()) // 2
            y = (self.height() - card_size.height()) // 2
            self._card.move(x, y)
            return

        rect = self._highlight_rect.toRect()
        right_space = self.width() - rect.right() - margin
        left_space = rect.left() - margin
        below_space = self.height() - rect.bottom() - margin
        above_space = rect.top() - margin

        if right_space >= card_size.width():
            x = rect.right() + margin
            y = max(
                margin, min(self.height() - card_size.height() - margin, rect.top())
            )
        elif left_space >= card_size.width():
            x = rect.left() - margin - card_size.width()
            y = max(
                margin, min(self.height() - card_size.height() - margin, rect.top())
            )
        elif below_space >= card_size.height():
            x = max(margin, min(self.width() - card_size.width() - margin, rect.left()))
            y = rect.bottom() + margin
        else:
            x = max(margin, min(self.width() - card_size.width() - margin, rect.left()))
            y = max(margin, rect.top() - margin - card_size.height())

        self._card.move(x, y)

    def _previous_step(self) -> None:
        if self._index > 0:
            self._index -= 1
            self._update_step()

    def _next_step(self) -> None:
        if self._index >= len(self._steps) - 1:
            self._finish()
            return
        self._index += 1
        self._update_step()

    def _finish(self) -> None:
        self.hide()
        show_on_startup = not self._dont_show_again.isChecked()
        if self._on_finish:
            self._on_finish(show_on_startup)

    def _sync_geometry(self) -> None:
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.rect())

    @staticmethod
    def _create_blurred_pixmap(pixmap: QPixmap) -> QPixmap:
        if pixmap.isNull():
            return QPixmap()

        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(12)
        item.setGraphicsEffect(blur)
        scene.addItem(item)

        result = QPixmap(pixmap.size())
        result.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result)
        scene.render(painter)
        painter.end()

        return result

    def _refresh_blur(self, force: bool = False) -> None:
        parent = self.parentWidget()
        if not parent:
            return
        if not force and not self.isVisible():
            return
        if self._is_refreshing:
            return

        self._is_refreshing = True
        try:
            self.setUpdatesEnabled(False)
            self.hide()
            pixmap = parent.grab()
            self._source_pixmap = pixmap
            self._blur_pixmap = self._create_blurred_pixmap(pixmap)
            self.show()
        finally:
            self.setUpdatesEnabled(True)
            self._is_refreshing = False

    def eventFilter(self, obj, event) -> bool:
        if obj is self.parentWidget() and event.type() in (
            QEvent.Type.Resize,
            QEvent.Type.Move,
        ):
            if not self.isVisible():
                return False
            if self._is_refreshing:
                return False
            self._sync_geometry()
            self._refresh_blur()
            self._update_highlight_rect(self._get_current_target())
            self._position_card()
            self.update()
        return super().eventFilter(obj, event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._blur_pixmap.isNull():
            painter.drawPixmap(0, 0, self._blur_pixmap)

        overlay_color = QColor(0, 0, 0, 100)
        painter.fillRect(self.rect(), overlay_color)

        if self._highlight_rects and not self._source_pixmap.isNull():
            pen = QPen(QColor(255, 255, 255, 220), 2)
            painter.setPen(pen)
            for rect in self._highlight_rects:
                highlight_rect = rect.adjusted(-4, -4, 4, 4)
                path = QPainterPath()
                path.addRoundedRect(highlight_rect, 8, 8)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, self._source_pixmap)
                painter.setClipping(False)
                painter.drawRoundedRect(highlight_rect, 8, 8)
