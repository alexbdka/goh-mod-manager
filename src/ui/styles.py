from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeTokens:
    """Small palette used by app-specific stylesheet additions."""

    panel_border: str
    panel_hover_border: str
    drop_background: str
    drop_hover_background: str
    subtle_text: str
    toast_background: str
    toast_border: str
    toast_success: str
    toast_warning: str
    toast_error: str


def build_app_stylesheet(theme_mode: str) -> str:
    """Return the app-specific stylesheet layered on top of qdarktheme."""
    tokens = _tokens_for_theme(theme_mode)
    return f"""
QLabel[uiRole="sectionTitle"] {{
    padding: 0 0 4px 0;
}}

QLabel[uiRole="sectionMeta"] {{
    color: {tokens.subtle_text};
    padding: 0 0 4px 0;
}}

QLabel[uiRole="emptyState"] {{
    color: {tokens.subtle_text};
    padding: 28px;
}}

QLabel[uiRole="onboardingTitle"] {{
    font-weight: 600;
}}

QLabel[uiRole="onboardingStep"] {{
    color: {tokens.subtle_text};
}}

QLabel[uiRole="detailsTitle"] {{
    font-weight: 600;
}}

QLabel[uiRole="detailsMeta"] {{
    color: {tokens.subtle_text};
}}

QLabel#ModDetailsImage {{
    border: 1px solid {tokens.panel_border};
    border-radius: 6px;
    padding: 4px;
}}

QTextBrowser#ModDetailsDescription {{
    margin: 0;
}}

QPushButton[uiRole="iconButton"] {{
    min-width: 30px;
    max-width: 30px;
    min-height: 28px;
    padding: 2px;
}}

QPushButton[uiRole="compactAction"] {{
    padding: 4px 10px;
}}

QToolBar#MainToolBar {{
    spacing: 4px;
    padding: 2px 6px;
}}

QPushButton[uiRole="toolbarButton"],
QPushButton[uiRole="toolbarPrimaryButton"] {{
    min-width: 34px;
    max-width: 34px;
    min-height: 30px;
    max-height: 30px;
    padding: 0;
}}

QPushButton[uiRole="toolbarPrimaryButton"] {{
    font-weight: 600;
}}

QWidget#ImportDropZone {{
    border: 1px dashed {tokens.panel_border};
    border-radius: 8px;
    background: {tokens.drop_background};
}}

QWidget#ImportDropZone[dragHover="true"] {{
    border: 2px dashed {tokens.panel_hover_border};
    background: {tokens.drop_hover_background};
}}

QFrame[uiRole="toast"] {{
    background: {tokens.toast_background};
    border: 1px solid {tokens.toast_border};
    border-radius: 8px;
}}

QFrame[uiRole="toast"][toastLevel="success"] {{
    border-left: 4px solid {tokens.toast_success};
}}

QFrame[uiRole="toast"][toastLevel="warning"] {{
    border-left: 4px solid {tokens.toast_warning};
}}

QFrame[uiRole="toast"][toastLevel="error"] {{
    border-left: 4px solid {tokens.toast_error};
}}

QLabel[uiRole="toastTitle"] {{
    font-weight: 600;
}}

QLabel[uiRole="toastMessage"] {{
    color: {tokens.subtle_text};
}}

QPushButton[uiRole="toastClose"] {{
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
    padding: 0;
    border: none;
}}

QLabel[uiRole="dropZoneTitle"] {{
    font-weight: 600;
}}

QLabel[uiRole="dropZoneSubtitle"] {{
    color: {tokens.subtle_text};
}}
""".strip()


def _tokens_for_theme(theme_mode: str) -> ThemeTokens:
    if theme_mode == "dark":
        return ThemeTokens(
            panel_border="#5f6670",
            panel_hover_border="#58a6ff",
            drop_background="rgba(255, 255, 255, 0.025)",
            drop_hover_background="rgba(88, 166, 255, 0.10)",
            subtle_text="#c7cdd4",
            toast_background="#22272e",
            toast_border="#3d444d",
            toast_success="#2ea043",
            toast_warning="#d29922",
            toast_error="#f85149",
        )

    return ThemeTokens(
        panel_border="#aab2bd",
        panel_hover_border="#1f6feb",
        drop_background="rgba(0, 0, 0, 0.025)",
        drop_hover_background="rgba(31, 111, 235, 0.08)",
        subtle_text="#4b5563",
        toast_background="#ffffff",
        toast_border="#d0d7de",
        toast_success="#1a7f37",
        toast_warning="#9a6700",
        toast_error="#cf222e",
    )
