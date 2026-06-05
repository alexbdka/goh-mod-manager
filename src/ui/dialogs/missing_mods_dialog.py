from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from src.utils import system_actions


class MissingModsDialog(QDialog):
    def __init__(self, parent, title: str, description: str, missing_items: list):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(550, 350)
        self.setAccessibleName("missingModsDialog")

        layout = QVBoxLayout(self)

        # We use a scroll area in case there are many missing mods
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setOpenExternalLinks(False)
        label.linkActivated.connect(self._open_link)
        label.setAccessibleName("missingModsContent")

        # build HTML
        items_html = []
        for item in missing_items:
            if isinstance(item, dict):
                mod_id = str(item.get("id", ""))
                mod_name = str(item.get("name", mod_id))
                source = str(item.get("source", ""))
            else:
                mod_id = str(item)
                mod_name = str(item)
                source = ""

            # Simple heuristic: Workshop IDs are usually purely numeric
            if source == "local":
                local_mod = self.tr("Local mod")
                install_manually = self.tr("Install this local mod manually.")
                items_html.append(
                    f"<li>{mod_name} ({local_mod}, ID: {mod_id})"
                    f"<br>{install_manually}</li>"
                )
            elif mod_id.isdigit():
                steam_url = f"steam://url/CommunityFilePage/{mod_id}"
                web_url = (
                    f"https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}"
                )
                open_steam = self.tr("Open in Steam")
                browser = self.tr("Browser")
                links = (
                    f'<a href="{steam_url}">{open_steam}</a> | '
                    f'<a href="{web_url}">{browser}</a>'
                )
                items_html.append(f"<li>{mod_name} (ID: {mod_id})<br>{links}</li>")
            else:
                local_id = self.tr("(Local or unknown ID)")
                items_html.append(f"<li>{mod_name} {local_id}</li>")

        list_html = "<ul>" + "".join(items_html) + "</ul>"
        full_html = f"<p>{description}</p>{list_html}"

        label.setText(full_html)
        content_layout.addWidget(label)
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # OK button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton(self.tr("OK"))
        ok_btn.setMinimumWidth(80)
        ok_btn.setAccessibleName("missingModsOkButton")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

    def _open_link(self, url: str):
        system_actions.open_url(url)
