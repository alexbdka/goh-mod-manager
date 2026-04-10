import qtawesome as qta
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QStyle, QStyleOptionViewItem, QWidget

from src.ui.appearance_manager import AppearanceManager

ROLE_MOD_ID = Qt.ItemDataRole.UserRole
ROLE_TITLE = Qt.ItemDataRole.UserRole + 1
ROLE_PIXMAP = Qt.ItemDataRole.UserRole + 2
ROLE_STATUS_ENTRIES = Qt.ItemDataRole.UserRole + 3
ROLE_IS_ACTIVE = Qt.ItemDataRole.UserRole + 4


class CatalogueItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QWidget | None = None, thumbnail_enabled: bool = True):
        super().__init__(parent)
        self._thumbnail_enabled = thumbnail_enabled
        self._icon_cache: dict[tuple[str, str], QIcon] = {}

    def set_thumbnail_enabled(self, enabled: bool):
        self._thumbnail_enabled = enabled

    def clear_icon_cache(self):
        self._icon_cache.clear()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        opt.icon = QIcon()

        widget = opt.widget
        style = widget.style() if widget else QApplication.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, opt, painter, widget)

        title = index.data(ROLE_TITLE) or ""
        thumbnail = index.data(ROLE_PIXMAP)
        status_entries = index.data(ROLE_STATUS_ENTRIES) or []
        is_active = bool(index.data(ROLE_IS_ACTIVE))

        content_rect = opt.rect.adjusted(6, 2, -6, -2)
        text_left = content_rect.left()
        if self._thumbnail_enabled:
            thumbnail_rect = QRect(
                content_rect.left(),
                content_rect.top() + max(0, (content_rect.height() - 32) // 2),
                32,
                32,
            )
            if isinstance(thumbnail, QPixmap) and not thumbnail.isNull():
                painter.drawPixmap(thumbnail_rect, thumbnail)
            text_left = thumbnail_rect.right() + 8

        status_width = len(status_entries) * 16 + max(0, len(status_entries) - 1) * 4
        status_left = content_rect.right() - status_width + 1 if status_entries else content_rect.right() + 1
        text_rect = QRect(
            text_left,
            content_rect.top(),
            max(0, status_left - text_left - (6 if status_entries else 0)),
            content_rect.height(),
        )

        text_color = (
            opt.palette.color(QPalette.ColorRole.HighlightedText)
            if opt.state & QStyle.StateFlag.State_Selected
            else opt.palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text)
            if is_active
            else opt.palette.color(QPalette.ColorRole.Text)
        )

        painter.save()
        painter.setPen(text_color)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            opt.fontMetrics.elidedText(
                title,
                Qt.TextElideMode.ElideRight,
                text_rect.width(),
            ),
        )
        painter.restore()

        x = status_left
        for entry in status_entries:
            icon = self._build_status_icon(entry, widget)
            if icon.isNull():
                continue
            icon_rect = QRect(
                x,
                content_rect.top() + max(0, (content_rect.height() - 16) // 2),
                16,
                16,
            )
            icon.paint(painter, icon_rect)
            x += 20

    def sizeHint(self, option: QStyleOptionViewItem, index):
        height = max(option.fontMetrics.height() + 8, 36 if self._thumbnail_enabled else 24)
        return QSize(0, height)

    def _build_status_icon(self, entry: dict, source: QWidget | None) -> QIcon:
        kind = entry.get("kind")
        theme_mode = AppearanceManager.resolve_theme_mode(source)
        cache_key = (kind or "", theme_mode)
        cached_icon = self._icon_cache.get(cache_key)
        if cached_icon is not None:
            return cached_icon

        if kind == "missing_dependencies":
            warning_color = "#f59e0b" if theme_mode == "dark" else "#b45309"
            icon = qta.icon(
                "fa5s.exclamation-triangle",
                color=warning_color,
                color_active=warning_color,
                color_selected=warning_color,
                color_disabled=warning_color,
            )
        elif kind == "dependencies":
            icon = qta.icon("fa5s.link", **AppearanceManager.get_icon_colors(source))
        else:
            icon = QIcon()

        self._icon_cache[cache_key] = icon
        return icon
