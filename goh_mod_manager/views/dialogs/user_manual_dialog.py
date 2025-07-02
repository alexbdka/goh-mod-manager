from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTextEdit,
    QPushButton,
    QWidget,
    QLabel,
)


class UserManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("User Manual")
        self.setFixedSize(800, 600)
        self.setModal(True)
        self.setup_ui()
        self.tab_widget = None

    def setup_ui(self):
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("User Guide")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Tabs Widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create Tab
        self.create_language_tabs()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

    def create_language_tabs(self):
        manuals_content = {
            "English": """
                <h2>Mod Manager User Manual</h2>

                <h3>Initial Setup</h3>
                <p>On first launch, you'll need to configure two important paths:</p>

                <h4>1. Mods Directory</h4>
                <p>This is where Steam Workshop mods are stored. The path is typically:</p>
                <p><code>DRIVE/STEAM_FOLDER/steamapps/workshop/content/400750</code></p>
                <p><strong>Examples:</strong></p>
                <ul>
                <li><code>C:/Program Files (x86)/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>D:/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>C:/Steam/steamapps/workshop/content/400750</code></li>
                </ul>
                <p><em>Replace DRIVE with your disk (C:, D:, etc.) and STEAM_FOLDER with your Steam installation directory.</em></p>

                <h4>2. Options.set File</h4>
                <p>This file can be found in one of two locations:</p>
                <p><strong>Location 1 (Most Common):</strong></p>
                <p><code>C:/Users/YOUR_USERNAME/Documents/My Games/gates of hell/profiles/STEAM_USER_ID/options.set</code></p>
                <p><strong>Location 2 (Alternative):</strong></p>
                <p><code>C:/Users/YOUR_USERNAME/AppData/Local/digitalmindsoft/gates of hell/profiles/STEAM_USER_ID/options.set</code></p>
                <p><em>Replace YOUR_USERNAME with your Windows username and STEAM_USER_ID with your Steam user ID (a long number).</em></p>

                <h3>Interface Layout</h3>
                <div style="display: flex; gap: 20px;">
                <div style="flex: 1;">
                <h4>Left Panel: Installed Mods</h4>
                <p>Shows all mods available in your mods directory</p>
                </div>
                <div style="flex: 1;">
                <h4>Right Panel: Active Mods</h4>
                <p>Shows currently enabled mods that will load in-game</p>
                </div>
                </div>

                <h3>Managing Mods</h3>
                <h4>Activating Mods</h4>
                <ul>
                <li><strong>Double-click</strong> any installed mod to activate it</li>
                <li><strong>Select multiple mods</strong> (Ctrl+click) and use "Add Selected"</li>
                </ul>

                <h4>Deactivating Mods</h4>
                <ul>
                <li><strong>Double-click</strong> any active mod to remove it</li>
                <li><strong>Select multiple mods</strong> and click "Remove"</li>
                <li><strong>"Clear All"</strong> removes all active mods at once</li>
                </ul>

                <h3>Mod Information Panel</h3>
                <p>Click any mod to view its details automatically. This can be disabled in the menu if preferred.</p>

                <h3>Preset System</h3>
                <p>Save and load different mod configurations:</p>
                <ul>
                <li><strong>"Save"</strong> - Create a preset from current active mods</li>
                <li><strong>"Load"</strong> - Apply a saved preset</li>
                <li><strong>"Delete"</strong> - Remove a preset permanently</li>
                </ul>

                <h3>Sharing Configurations</h3>
                <p>Share your mod setups with other players:</p>
                <ul>
                <li><strong>"Export"</strong> - Generate a shareable code in the text field</li>
                <li><strong>"Import"</strong> - Load a configuration from a shared code</li>
                </ul>

                <h3>Support</h3>
                <p>Found a bug or have suggestions? The interface is designed to be user-friendly - feel free to experiment and provide feedback for improvements.</p>
                """,
            "Français": """
                <h2>Manuel d'utilisation - Gestionnaire de Mods</h2>

                <h3>Configuration initiale</h3>
                <p>Au premier lancement, vous devez configurer deux chemins importants :</p>

                <h4>1. Répertoire des Mods</h4>
                <p>C'est là où Steam Workshop stocke les mods. Le chemin est généralement :</p>
                <p><code>DISQUE/DOSSIER_STEAM/steamapps/workshop/content/400750</code></p>
                <p><strong>Exemples :</strong></p>
                <ul>
                <li><code>C:/Program Files (x86)/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>D:/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>C:/Steam/steamapps/workshop/content/400750</code></li>
                </ul>
                <p><em>Remplacez DISQUE par votre disque (C:, D:, etc.) et DOSSIER_STEAM par votre répertoire d'installation Steam.</em></p>

                <h4>2. Fichier Options.set</h4>
                <p>Ce fichier se trouve dans l'un de ces deux emplacements :</p>
                <p><strong>Emplacement 1 (Le plus courant) :</strong></p>
                <p><code>C:/Users/VOTRE_NOM_UTILISATEUR/Documents/My Games/gates of hell/profiles/ID_UTILISATEUR_STEAM/options.set</code></p>
                <p><strong>Emplacement 2 (Alternatif) :</strong></p>
                <p><code>C:/Users/VOTRE_NOM_UTILISATEUR/AppData/Local/digitalmindsoft/gates of hell/profiles/ID_UTILISATEUR_STEAM/options.set</code></p>
                <p><em>Remplacez VOTRE_NOM_UTILISATEUR par votre nom d'utilisateur Windows et ID_UTILISATEUR_STEAM par votre ID Steam (un long nombre).</em></p>

                <h3>Disposition de l'interface</h3>
                <div style="display: flex; gap: 20px;">
                <div style="flex: 1;">
                <h4>Panneau gauche : Mods installés</h4>
                <p>Affiche tous les mods disponibles dans votre répertoire</p>
                </div>
                <div style="flex: 1;">
                <h4>Panneau droit : Mods actifs</h4>
                <p>Affiche les mods actuellement activés qui se chargeront en jeu</p>
                </div>
                </div>

                <h3>Gestion des mods</h3>
                <h4>Activation des mods</h4>
                <ul>
                <li><strong>Double-clic</strong> sur n'importe quel mod installé pour l'activer</li>
                <li><strong>Sélection multiple</strong> (Ctrl+clic) et utilisez "Add Selected"</li>
                </ul>

                <h4>Désactivation des mods</h4>
                <ul>
                <li><strong>Double-clic</strong> sur n'importe quel mod actif pour le retirer</li>
                <li><strong>Sélection multiple</strong> et cliquez sur "Remove"</li>
                <li><strong>"Clear All"</strong> retire tous les mods actifs d'un coup</li>
                </ul>

                <h3>Panneau d'informations des mods</h3>
                <p>Cliquez sur n'importe quel mod pour voir ses détails automatiquement. Ceci peut être désactivé dans le menu si préféré.</p>

                <h3>Système de presets</h3>
                <p>Sauvegardez et chargez différentes configurations de mods :</p>
                <ul>
                <li><strong>"Save"</strong> - Créer un preset à partir des mods actuellement actifs</li>
                <li><strong>"Load"</strong> - Appliquer un preset sauvegardé</li>
                <li><strong>"Delete"</strong> - Supprimer définitivement un preset</li>
                </ul>

                <h3>Partage de configurations</h3>
                <p>Partagez vos configurations de mods avec d'autres joueurs :</p>
                <ul>
                <li><strong>"Export"</strong> - Générer un code partageable dans le champ de texte</li>
                <li><strong>"Import"</strong> - Charger une configuration à partir d'un code partagé</li>
                </ul>

                <h3>Support</h3>
                <p>Trouvé un bug ou avez des suggestions ? L'interface est conçue pour être conviviale - n'hésitez pas à expérimenter et fournir des commentaires pour des améliorations.</p>
                """,
            "Deutsch": """
                <h2>Benutzerhandbuch - Mod-Manager</h2>

                <h3>Ersteinrichtung</h3>
                <p>Beim ersten Start müssen Sie zwei wichtige Pfade konfigurieren:</p>

                <h4>1. Mod-Verzeichnis</h4>
                <p>Hier speichert Steam Workshop die Mods. Der Pfad ist normalerweise:</p>
                <p><code>LAUFWERK/STEAM_ORDNER/steamapps/workshop/content/400750</code></p>
                <p><strong>Beispiele:</strong></p>
                <ul>
                <li><code>C:/Program Files (x86)/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>D:/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>C:/Steam/steamapps/workshop/content/400750</code></li>
                </ul>
                <p><em>Ersetzen Sie LAUFWERK durch Ihre Festplatte (C:, D:, etc.) und STEAM_ORDNER durch Ihr Steam-Installationsverzeichnis.</em></p>

                <h4>2. Options.set Datei</h4>
                <p>Diese Datei befindet sich an einem von zwei Orten:</p>
                <p><strong>Ort 1 (Am häufigsten):</strong></p>
                <p><code>C:/Users/IHR_BENUTZERNAME/Documents/My Games/gates of hell/profiles/STEAM_BENUTZER_ID/options.set</code></p>
                <p><strong>Ort 2 (Alternativ):</strong></p>
                <p><code>C:/Users/IHR_BENUTZERNAME/AppData/Local/digitalmindsoft/gates of hell/profiles/STEAM_BENUTZER_ID/options.set</code></p>
                <p><em>Ersetzen Sie IHR_BENUTZERNAME durch Ihren Windows-Benutzernamen und STEAM_BENUTZER_ID durch Ihre Steam-Benutzer-ID (eine lange Zahl).</em></p>

                <h3>Interface-Layout</h3>
                <div style="display: flex; gap: 20px;">
                <div style="flex: 1;">
                <h4>Linkes Panel: Installierte Mods</h4>
                <p>Zeigt alle verfügbaren Mods in Ihrem Mod-Verzeichnis</p>
                </div>
                <div style="flex: 1;">
                <h4>Rechtes Panel: Aktive Mods</h4>
                <p>Zeigt derzeit aktivierte Mods, die im Spiel geladen werden</p>
                </div>
                </div>

                <h3>Mod-Verwaltung</h3>
                <h4>Mods aktivieren</h4>
                <ul>
                <li><strong>Doppelklick</strong> auf jeden installierten Mod, um ihn zu aktivieren</li>
                <li><strong>Mehrere Mods auswählen</strong> (Strg+Klick) und "Add Selected" verwenden</li>
                </ul>

                <h4>Mods deaktivieren</h4>
                <ul>
                <li><strong>Doppelklick</strong> auf jeden aktiven Mod, um ihn zu entfernen</li>
                <li><strong>Mehrere Mods auswählen</strong> und auf "Remove" klicken</li>
                <li><strong>"Clear All"</strong> entfernt alle aktiven Mods auf einmal</li>
                </ul>

                <h3>Mod-Informationspanel</h3>
                <p>Klicken Sie auf jeden Mod, um seine Details automatisch anzuzeigen. Dies kann im Menü deaktiviert werden, falls gewünscht.</p>

                <h3>Preset-System</h3>
                <p>Speichern und laden Sie verschiedene Mod-Konfigurationen:</p>
                <ul>
                <li><strong>"Save"</strong> - Preset aus aktuell aktiven Mods erstellen</li>
                <li><strong>"Load"</strong> - Gespeichertes Preset anwenden</li>
                <li><strong>"Delete"</strong> - Preset dauerhaft entfernen</li>
                </ul>

                <h3>Konfigurationen teilen</h3>
                <p>Teilen Sie Ihre Mod-Setups mit anderen Spielern:</p>
                <ul>
                <li><strong>"Export"</strong> - Teilbaren Code im Textfeld generieren</li>
                <li><strong>"Import"</strong> - Konfiguration aus geteiltem Code laden</li>
                </ul>

                <h3>Support</h3>
                <p>Fehler gefunden oder Vorschläge? Die Benutzeroberfläche ist benutzerfreundlich gestaltet - experimentieren Sie gerne und geben Sie Feedback für Verbesserungen.</p>
                """,
            "Русский": """
                <h2>Руководство пользователя - Менеджер модов</h2>

                <h3>Первоначальная настройка</h3>
                <p>При первом запуске вам нужно настроить два важных пути:</p>

                <h4>1. Директория модов</h4>
                <p>Здесь Steam Workshop хранит моды. Путь обычно:</p>
                <p><code>ДИСК/ПАПКА_STEAM/steamapps/workshop/content/400750</code></p>
                <p><strong>Примеры:</strong></p>
                <ul>
                <li><code>C:/Program Files (x86)/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>D:/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>C:/Steam/steamapps/workshop/content/400750</code></li>
                </ul>
                <p><em>Замените ДИСК на ваш диск (C:, D:, и т.д.) и ПАПКА_STEAM на вашу директорию установки Steam.</em></p>

                <h4>2. Файл Options.set</h4>
                <p>Этот файл может находиться в одном из двух мест:</p>
                <p><strong>Место 1 (Наиболее распространенное):</strong></p>
                <p><code>C:/Users/ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ/Documents/My Games/gates of hell/profiles/ID_ПОЛЬЗОВАТЕЛЯ_STEAM/options.set</code></p>
                <p><strong>Место 2 (Альтернативное):</strong></p>
                <p><code>C:/Users/ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ/AppData/Local/digitalmindsoft/gates of hell/profiles/ID_ПОЛЬЗОВАТЕЛЯ_STEAM/options.set</code></p>
                <p><em>Замените ВАШЕ_ИМЯ_ПОЛЬЗОВАТЕЛЯ на ваше имя пользователя Windows и ID_ПОЛЬЗОВАТЕЛЯ_STEAM на ваш Steam ID (длинное число).</em></p>

                <h3>Макет интерфейса</h3>
                <div style="display: flex; gap: 20px;">
                <div style="flex: 1;">
                <h4>Левая панель: Установленные моды</h4>
                <p>Показывает все доступные моды в вашей директории</p>
                </div>
                <div style="flex: 1;">
                <h4>Правая панель: Активные моды</h4>
                <p>Показывает текущие включенные моды, которые загрузятся в игре</p>
                </div>
                </div>

                <h3>Управление модами</h3>
                <h4>Активация модов</h4>
                <ul>
                <li><strong>Двойной клик</strong> по любому установленному моду для его активации</li>
                <li><strong>Выберите несколько модов</strong> (Ctrl+клик) и используйте "Add Selected"</li>
                </ul>

                <h4>Деактивация модов</h4>
                <ul>
                <li><strong>Двойной клик</strong> по любому активному моду для его удаления</li>
                <li><strong>Выберите несколько модов</strong> и нажмите "Remove"</li>
                <li><strong>"Clear All"</strong> удаляет все активные моды сразу</li>
                </ul>

                <h3>Панель информации о модах</h3>
                <p>Нажмите на любой мод, чтобы автоматически просмотреть его детали. Это можно отключить в меню при желании.</p>

                <h3>Система пресетов</h3>
                <p>Сохраняйте и загружайте различные конфигурации модов:</p>
                <ul>
                <li><strong>"Save"</strong> - Создать пресет из текущих активных модов</li>
                <li><strong>"Load"</strong> - Применить сохраненный пресет</li>
                <li><strong>"Delete"</strong> - Удалить пресет навсегда</li>
                </ul>

                <h3>Обмен конфигурациями</h3>
                <p>Делитесь своими настройками модов с другими игроками:</p>
                <ul>
                <li><strong>"Export"</strong> - Генерировать код для обмена в текстовом поле</li>
                <li><strong>"Import"</strong> - Загрузить конфигурацию из общего кода</li>
                </ul>

                <h3>Поддержка</h3>
                <p>Нашли ошибку или есть предложения? Интерфейс разработан для удобства использования - не стесняйтесь экспериментировать и предоставлять отзывы для улучшений.</p>
                """,
            "中文": """
                <h2>用户手册 - 模组管理器</h2>

                <h3>初始设置</h3>
                <p>首次启动时，您需要配置两个重要路径：</p>

                <h4>1. 模组目录</h4>
                <p>这是Steam创意工坊存储模组的地方。路径通常是：</p>
                <p><code>磁盘/STEAM文件夹/steamapps/workshop/content/400750</code></p>
                <p><strong>示例：</strong></p>
                <ul>
                <li><code>C:/Program Files (x86)/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>D:/Steam/steamapps/workshop/content/400750</code></li>
                <li><code>C:/Steam/steamapps/workshop/content/400750</code></li>
                </ul>
                <p><em>将"磁盘"替换为您的磁盘(C:、D:等)，将"STEAM文件夹"替换为Steam安装目录。</em></p>

                <h4>2. Options.set文件</h4>
                <p>此文件可能位于以下两个位置之一：</p>
                <p><strong>位置1（最常见）：</strong></p>
                <p><code>C:/Users/您的用户名/Documents/My Games/gates of hell/profiles/STEAM用户ID/options.set</code></p>
                <p><strong>位置2（备选）：</strong></p>
                <p><code>C:/Users/您的用户名/AppData/Local/digitalmindsoft/gates of hell/profiles/STEAM用户ID/options.set</code></p>
                <p><em>将"您的用户名"替换为您的Windows用户名，将"STEAM用户ID"替换为您的Steam用户ID（一个长数字）。</em></p>

                <h3>界面布局</h3>
                <div style="display: flex; gap: 20px;">
                <div style="flex: 1;">
                <h4>左侧面板：已安装模组</h4>
                <p>显示模组目录中所有可用的模组</p>
                </div>
                <div style="flex: 1;">
                <h4>右侧面板：活跃模组</h4>
                <p>显示当前启用的将在游戏中加载的模组</p>
                </div>
                </div>

                <h3>模组管理</h3>
                <h4>激活模组</h4>
                <ul>
                <li><strong>双击</strong>任何已安装的模组来激活它</li>
                <li><strong>选择多个模组</strong>（Ctrl+点击）并使用"Add Selected"</li>
                </ul>

                <h4>停用模组</h4>
                <ul>
                <li><strong>双击</strong>任何活跃的模组来移除它</li>
                <li><strong>选择多个模组</strong>并点击"Remove"</li>
                <li><strong>"Clear All"</strong>一次性移除所有活跃模组</li>
                </ul>

                <h3>模组信息面板</h3>
                <p>点击任何模组可自动查看其详细信息。如果需要，可以在菜单中禁用此功能。</p>

                <h3>预设系统</h3>
                <p>保存和加载不同的模组配置：</p>
                <ul>
                <li><strong>"Save"</strong> - 从当前活跃模组创建预设</li>
                <li><strong>"Load"</strong> - 应用已保存的预设</li>
                <li><strong>"Delete"</strong> - 永久删除预设</li>
                </ul>

                <h3>配置分享</h3>
                <p>与其他玩家分享您的模组设置：</p>
                <ul>
                <li><strong>"Export"</strong> - 在文本框中生成可分享的代码</li>
                <li><strong>"Import"</strong> - 从分享的代码加载配置</li>
                </ul>

                <h3>支持</h3>
                <p>发现错误或有建议？界面设计为用户友好 - 请随意试验并提供改进反馈。</p>
                """,
        }

        for language, content in manuals_content.items():
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(0, 0, 0, 0)

            text_edit = QTextEdit()
            text_edit.setHtml(content)
            text_edit.setReadOnly(True)
            tab_layout.addWidget(text_edit)

            self.tab_widget.addTab(tab_widget, language)

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
