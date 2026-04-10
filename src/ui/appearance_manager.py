import qdarktheme
import qtawesome as qta
from PySide6.QtGui import QFont, QFontDatabase, QPalette
from PySide6.QtWidgets import QApplication, QWidget

from src.utils import app_paths


class AppearanceManager:
    """
    Centralized manager for application styling.
    Uses qdarktheme as the single styling entry point.
    """

    _fonts_loaded = False

    @staticmethod
    def setup_appearance(
        app: QApplication, theme: str = "auto", font_name: str = "Inter"
    ):
        AppearanceManager._setup_fonts(app, font_name)

        normalized_theme = theme if theme in {"auto", "dark", "light"} else "auto"

        app.setStyleSheet("")
        qdarktheme.setup_theme(normalized_theme)
        app.setProperty(
            "resolved_theme_mode",
            AppearanceManager.resolve_theme_mode(app, normalized_theme),
        )
        AppearanceManager._setup_icon_defaults(app)

    @staticmethod
    def _setup_fonts(app: QApplication, font_name: str):
        if not AppearanceManager._fonts_loaded:
            font_dir = app_paths.get_resource_path("assets", "fonts")
            inter_path = font_dir / "Inter-Regular.otf"
            opendyslexic_path = font_dir / "OpenDyslexic-Regular.otf"

            QFontDatabase.addApplicationFont(str(opendyslexic_path))
            QFontDatabase.addApplicationFont(str(inter_path))
            AppearanceManager._fonts_loaded = True

        if font_name == "default":
            app_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
        else:
            app_font = QFont(font_name)

        app_font.setPointSize(10)
        app.setFont(app_font)

    @staticmethod
    def _setup_icon_defaults(app: QApplication):
        icon_colors = AppearanceManager.get_icon_colors(app)

        qta.set_defaults(
            color=icon_colors["color"],
            color_active=icon_colors["color_active"],
            color_selected=icon_colors["color_selected"],
            color_disabled=icon_colors["color_disabled"],
        )
        qta.reset_cache()

    @staticmethod
    def resolve_theme_mode(
        source: QApplication | QWidget | None = None, configured_theme: str = "auto"
    ) -> str:
        if configured_theme in {"dark", "light"}:
            return configured_theme

        if source is None:
            app = QApplication.instance()
            palette = app.palette() if app else QPalette()
        else:
            palette = source.palette()

        is_dark = palette.color(QPalette.ColorRole.Window).lightness() < 128
        return "dark" if is_dark else "light"

    @staticmethod
    def get_icon_colors(source: QApplication | QWidget | None = None) -> dict[str, str]:
        app = QApplication.instance()
        resolved_theme = (
            app.property("resolved_theme_mode") if app is not None else None
        )
        if resolved_theme not in {"dark", "light"}:
            resolved_theme = AppearanceManager.resolve_theme_mode(source)

        if resolved_theme == "dark":
            return {
                "color": "#f1f3f4",
                "color_active": "#ffffff",
                "color_selected": "#ffffff",
                "color_disabled": "#6f747a",
            }

        return {
            "color": "#202124",
            "color_active": "#111111",
            "color_selected": "#111111",
            "color_disabled": "#9aa0a6",
        }
