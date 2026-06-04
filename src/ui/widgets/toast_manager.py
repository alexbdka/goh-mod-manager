from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)
from src.ui.appearance_manager import AppearanceManager
from src.ui.qtawesome_compat import qta


class ToastWidget(QFrame):
    def __init__(
        self,
        parent: QWidget,
        title: str,
        message: str,
        level: str,
        on_close: Callable[[ToastWidget], None],
    ):
        super().__init__(parent)
        self.setProperty("uiRole", "toast")
        self.setProperty("toastLevel", level)
        self.setObjectName("ToastWidget")
        self.setAccessibleName("toastNotification")
        self._on_close = on_close
        self._setup_ui(title, message, level)

    def _setup_ui(self, title: str, message: str, level: str) -> None:
        container = QHBoxLayout(self)
        container.setContentsMargins(12, 10, 10, 10)
        container.setSpacing(8)

        icon_label = QLabel(self)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        icon_label.setPixmap(self._build_icon(level).pixmap(16, 16))
        container.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        title_label = QLabel(title, self)
        title_label.setProperty("uiRole", "toastTitle")
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)

        message_label = QLabel(message, self)
        message_label.setProperty("uiRole", "toastMessage")
        message_label.setWordWrap(True)
        text_layout.addWidget(message_label)

        container.addLayout(text_layout, stretch=1)

        close_button = QPushButton(self)
        close_button.setProperty("uiRole", "toastClose")
        close_button.setAccessibleName("toastCloseButton")
        close_button.setIcon(
            qta.icon("fa5s.times", **AppearanceManager.get_icon_colors(self))
        )
        close_button.clicked.connect(self.close)
        container.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignTop)

        self.setMinimumWidth(320)
        self.setMaximumWidth(420)

    def _build_icon(self, level: str):
        icon_colors = AppearanceManager.get_icon_colors(self)
        if level == "success":
            return qta.icon("fa5s.check-circle", color="#2ea043")
        if level == "warning":
            return qta.icon("fa5s.exclamation-triangle", color="#d29922")
        if level == "error":
            return qta.icon("fa5s.times-circle", color="#f85149")
        return qta.icon("fa5s.info-circle", **icon_colors)

    def closeEvent(self, event):
        super().closeEvent(event)
        self._on_close(self)


class ToastManager:
    def __init__(self, parent: QWidget):
        self._parent = parent
        self._toasts: list[ToastWidget] = []

    def show_toast(
        self,
        *,
        title: str,
        message: str,
        level: str = "info",
        duration_ms: int = 5000,
    ) -> None:
        toast = ToastWidget(
            self._parent,
            title=title,
            message=message,
            level=level,
            on_close=self._on_toast_closed,
        )
        toast.show()
        toast.raise_()
        self._toasts.append(toast)
        self.reposition_toasts()
        QTimer.singleShot(duration_ms, toast.close)

    def reposition_toasts(self) -> None:
        margin = 4
        gap = 8
        available_rect = self._available_rect(margin, gap)
        y = available_rect.bottom() + 1

        for toast in reversed(self._toasts):
            if not toast.isVisible():
                continue

            toast.ensurePolished()
            toast.adjustSize()
            size_hint = toast.sizeHint()
            max_width = toast.maximumWidth() if toast.maximumWidth() > 0 else 10_000
            preferred_width = min(
                max(size_hint.width(), toast.minimumWidth()),
                max_width,
            )
            toast_width = min(preferred_width, max(1, available_rect.width()))
            toast_height = min(size_hint.height(), max(1, available_rect.height()))
            toast.resize(toast_width, toast_height)

            y -= toast.height()
            x = available_rect.right() - toast.width() + 1
            toast.move(
                QPoint(max(available_rect.left(), x), max(available_rect.top(), y))
            )
            y -= gap

    def _available_rect(self, margin: int, gap: int) -> QRect:
        rect = self._parent.rect()
        top = rect.top() + margin
        left = rect.left() + margin
        right = rect.right() - margin

        status_bar_top = self._status_bar_top()
        if status_bar_top is not None:
            bottom = status_bar_top - gap
        else:
            bottom = rect.bottom() - margin

        available = QRect(
            left,
            top,
            max(1, right - left + 1),
            max(1, bottom - top + 1),
        )
        if available.isEmpty():
            return rect
        return available

    def _status_bar_top(self) -> int | None:
        parent = self._parent
        if isinstance(parent, QMainWindow):
            status_bar = parent.statusBar()
            if status_bar.isVisible():
                return status_bar.geometry().top()

        status_bar = parent.findChild(QStatusBar)
        if status_bar and status_bar.isVisible():
            return status_bar.geometry().top()

        return None

    def _on_toast_closed(self, toast: ToastWidget) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
            self.reposition_toasts()
