from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)

ROLE_MOD_ID = Qt.ItemDataRole.UserRole
ROLE_ORDER = Qt.ItemDataRole.UserRole + 1
ROLE_TITLE = Qt.ItemDataRole.UserRole + 2
ROLE_SOURCE = Qt.ItemDataRole.UserRole + 3
ROLE_MOD_REF = Qt.ItemDataRole.UserRole + 4


class ActiveModsItemDelegate(QStyledItemDelegate):
    """Custom row renderer for the active load order list."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        if index.column() != 0:
            return

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""
        opt.icon = QIcon()

        widget = opt.widget
        style = widget.style() if widget else QApplication.style()
        style.drawPrimitive(
            QStyle.PrimitiveElement.PE_PanelItemViewItem, opt, painter, widget
        )

        order_text = str(index.data(ROLE_ORDER) or "")
        title = str(index.data(ROLE_TITLE) or "")
        source_text = str(index.data(ROLE_SOURCE) or "")

        content_rect = opt.rect.adjusted(8, 4, -8, -4)
        badge_rect = QRect(
            content_rect.left(),
            content_rect.top() + max(0, (content_rect.height() - 24) // 2),
            34,
            24,
        )
        text_left = badge_rect.right() + 10
        title_rect = QRect(
            text_left,
            content_rect.top(),
            max(0, content_rect.right() - text_left),
            max(16, content_rect.height() // 2 + 2),
        )
        source_rect = QRect(
            text_left,
            title_rect.bottom(),
            max(0, content_rect.right() - text_left),
            max(14, content_rect.bottom() - title_rect.bottom()),
        )

        selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        text_color = opt.palette.color(
            QPalette.ColorRole.HighlightedText if selected else QPalette.ColorRole.Text
        )
        muted_color = opt.palette.color(
            QPalette.ColorRole.HighlightedText
            if selected
            else QPalette.ColorRole.PlaceholderText
        )
        badge_background = opt.palette.color(
            QPalette.ColorRole.Highlight
            if selected
            else QPalette.ColorRole.AlternateBase
        )
        badge_text = opt.palette.color(
            QPalette.ColorRole.HighlightedText if selected else QPalette.ColorRole.Text
        )

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(badge_background)
        painter.drawRoundedRect(badge_rect, 6, 6)

        painter.setPen(badge_text)
        painter.drawText(
            badge_rect,
            Qt.AlignmentFlag.AlignCenter,
            order_text,
        )

        painter.setPen(text_color)
        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            opt.fontMetrics.elidedText(
                title,
                Qt.TextElideMode.ElideRight,
                title_rect.width(),
            ),
        )

        painter.setPen(muted_color)
        painter.drawText(
            source_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            opt.fontMetrics.elidedText(
                source_text,
                Qt.TextElideMode.ElideRight,
                source_rect.width(),
            ),
        )
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index):
        return QSize(0, max(44, option.fontMetrics.height() * 2 + 12))

    def editorEvent(self, event, model, option, index):
        if index.column() != 0:
            return False
        return super().editorEvent(event, model, option, index)

    def createEditor(self, parent: QWidget, option, index):
        return None
