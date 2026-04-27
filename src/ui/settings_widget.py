import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QFrame, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QObject


# ─────────────────────────────────────────────
#  TRANSLATIONS
# ─────────────────────────────────────────────
TRANSLATIONS = {
    "vi": {
        # Settings page
        "settings_title":       "⚙️ Cài đặt",
        "appearance_title":     "🎨 Giao diện",
        "appearance_desc":      "Chuyển đổi giữa chủ đề sáng và tối.",
        "dark_mode_on":         "🌙 Chế độ tối",
        "dark_mode_off":        "☀️ Chế độ sáng",
        "ai_title":             "🤖 Cài đặt AI",
        "ai_desc":              "Số lượng flashcard tối đa được tạo mỗi phiên AI.",
        "ai_limit_lbl":         "Giới hạn flashcard:",
        "ai_limit_placeholder": "Nhập số (VD: 10)",
        "data_title":           "🗂 Dữ liệu",
        "data_desc":            "Xuất hoặc nhập dữ liệu flashcard dạng JSON.",
        "export_btn":           "⬆ Xuất Flashcards",
        "import_btn":           "⬇ Nhập Flashcards",
        "save_btn":             "💾 Lưu cài đặt",
        "language_title":       "🌐 Ngôn ngữ",
        "language_desc":        "Chọn ngôn ngữ hiển thị cho toàn bộ ứng dụng.",
        # Dialogs
        "invalid_input":        "Đầu vào không hợp lệ",
        "invalid_input_msg":    "Giới hạn flashcard phải là số nguyên dương.",
        "saved_title":          "Đã lưu",
        "saved_msg":            "Đã lưu cài đặt!\n\n• Giới hạn AI: {limit}\n• Chế độ tối: {dark}",
        "dark_on":              "Bật",
        "dark_off":             "Tắt",
        "export_ok":            "Xuất thành công",
        "export_ok_msg":        "Đã xuất flashcards tới:\n{path}",
        "export_fail":          "Xuất thất bại",
        "import_ok":            "Nhập thành công",
        "import_ok_msg":        "Đã tải {count} flashcard(s) từ:\n{path}",
        "import_fail":          "Nhập thất bại",
        # Sidebar
        "menu_overview":        "Tổng quan",
        "menu_schedule":        "Thời khóa biểu",
        "menu_courses":         "Khóa học",
        "menu_flash":           "Flashcards",
        "menu_summary":         "Tóm tắt AI",
        "menu_todo":            "Todo List",
        "menu_settings":        "Cài đặt",
        "logout":               "↪ Đăng xuất",
    },
    "en": {
        # Settings page
        "settings_title":       "⚙️ Settings",
        "appearance_title":     "🎨 Appearance",
        "appearance_desc":      "Switch between light and dark theme.",
        "dark_mode_on":         "🌙 Toggle Dark Mode",
        "dark_mode_off":        "☀️ Light Mode",
        "ai_title":             "🤖 AI Settings",
        "ai_desc":              "Maximum number of flashcards generated per AI session.",
        "ai_limit_lbl":         "Flashcard limit:",
        "ai_limit_placeholder": "Enter number (e.g. 10)",
        "data_title":           "🗂 Data",
        "data_desc":            "Export or import your flashcard data as JSON.",
        "export_btn":           "⬆ Export Flashcards",
        "import_btn":           "⬇ Import Flashcards",
        "save_btn":             "💾 Save Settings",
        "language_title":       "🌐 Language",
        "language_desc":        "Select the display language for the entire application.",
        # Dialogs
        "invalid_input":        "Invalid Input",
        "invalid_input_msg":    "Flashcard limit must be a positive integer.",
        "saved_title":          "Saved",
        "saved_msg":            "Settings saved!\n\n• AI flashcard limit: {limit}\n• Dark mode: {dark}",
        "dark_on":              "On",
        "dark_off":             "Off",
        "export_ok":            "Export Successful",
        "export_ok_msg":        "Flashcards exported to:\n{path}",
        "export_fail":          "Export Failed",
        "import_ok":            "Import Successful",
        "import_ok_msg":        "Loaded {count} flashcard(s) from:\n{path}",
        "import_fail":          "Import Failed",
        # Sidebar
        "menu_overview":        "Overview",
        "menu_schedule":        "Schedule",
        "menu_courses":         "Courses",
        "menu_flash":           "Flashcards",
        "menu_summary":         "AI Summary",
        "menu_todo":            "Todo List",
        "menu_settings":        "Settings",
        "logout":               "↪ Logout",
    },
    "ja": {
        # Settings page
        "settings_title":       "⚙️ 設定",
        "appearance_title":     "🎨 外観",
        "appearance_desc":      "ライトとダークテーマを切り替えます。",
        "dark_mode_on":         "🌙 ダークモード",
        "dark_mode_off":        "☀️ ライトモード",
        "ai_title":             "🤖 AI設定",
        "ai_desc":              "AIセッションごとに生成されるフラッシュカードの最大数。",
        "ai_limit_lbl":         "フラッシュカード上限:",
        "ai_limit_placeholder": "数字を入力 (例: 10)",
        "data_title":           "🗂 データ",
        "data_desc":            "フラッシュカードデータをJSONでエクスポート/インポート。",
        "export_btn":           "⬆ エクスポート",
        "import_btn":           "⬇ インポート",
        "save_btn":             "💾 設定を保存",
        "language_title":       "🌐 言語",
        "language_desc":        "アプリ全体の表示言語を選択します。",
        # Dialogs
        "invalid_input":        "無効な入力",
        "invalid_input_msg":    "フラッシュカード上限は正の整数でなければなりません。",
        "saved_title":          "保存完了",
        "saved_msg":            "設定を保存しました！\n\n• AI上限: {limit}\n• ダークモード: {dark}",
        "dark_on":              "オン",
        "dark_off":             "オフ",
        "export_ok":            "エクスポート成功",
        "export_ok_msg":        "エクスポート先:\n{path}",
        "export_fail":          "エクスポート失敗",
        "import_ok":            "インポート成功",
        "import_ok_msg":        "{count}件のフラッシュカードを読み込みました:\n{path}",
        "import_fail":          "インポート失敗",
        # Sidebar
        "menu_overview":        "概要",
        "menu_schedule":        "時間割",
        "menu_courses":         "コース",
        "menu_flash":           "フラッシュカード",
        "menu_summary":         "AI要約",
        "menu_todo":            "Todoリスト",
        "menu_settings":        "設定",
        "logout":               "↪ ログアウト",
    },
}

# ─────────────────────────────────────────────
#  LANGUAGE MANAGER  (singleton-style QObject)
# ─────────────────────────────────────────────
class LanguageManager(QObject):
    """Emits language_changed whenever the active locale is swapped."""
    language_changed = Signal(str)          # emits new lang code, e.g. "en"

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._lang = "vi"                   # default

    # ── public API ──────────────────────────
    @property
    def lang(self) -> str:
        return self._lang

    def set_lang(self, code: str):
        if code != self._lang and code in TRANSLATIONS:
            self._lang = code
            self.language_changed.emit(code)

    def tr(self, key: str, **fmt) -> str:
        """Return translated string, falling back to key if missing."""
        text = TRANSLATIONS.get(self._lang, {}).get(key, key)
        return text.format(**fmt) if fmt else text


# Convenience shortcut used throughout the app:
#   from src.ui.settings_widget import tr
def tr(key: str, **fmt) -> str:
    return LanguageManager.instance().tr(key, **fmt)


# ─────────────────────────────────────────────
#  DARK / LIGHT STYLESHEETS  (unchanged)
# ─────────────────────────────────────────────
DARK_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #1E1E2E;
        color: #CDD6F4;
    }
    QFrame#Sidebar {
        background-color: #181825;
        border-right: 1px solid #313244;
    }
    QPushButton#MenuBtn {
        background: transparent;
        color: #CDD6F4;
        border: none;
        text-align: left;
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 14px;
    }
    QPushButton#MenuBtn:checked {
        background: #313244;
        color: #89B4FA;
        font-weight: bold;
    }
    QPushButton#MenuBtn:hover { background: #2A2A3D; }
    QPushButton#LogoutBtn {
        background: transparent;
        color: #F38BA8;
        border: none;
        text-align: left;
        padding: 8px;
        font-size: 13px;
    }
    QFrame#CardBlue {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #2D60FF,stop:1 #539BFF);
        border-radius: 16px;
        padding: 20px;
        color: white;
    }
    QFrame#CardWhite {
        background: #313244;
        border-radius: 16px;
        padding: 20px;
        color: #CDD6F4;
    }
    QFrame#SettingsSection {
        background: #313244;
        border-radius: 12px;
        padding: 16px;
    }
    QLineEdit {
        background: #45475A;
        border: 1px solid #585B70;
        border-radius: 8px;
        padding: 8px 12px;
        color: #CDD6F4;
        font-size: 13px;
    }
    QProgressBar { background: #45475A; border-radius: 3px; }
    QProgressBar::chunk { background: #89B4FA; border-radius: 3px; }
"""

LIGHT_STYLESHEET = ""


# ─────────────────────────────────────────────
#  LANGUAGE BUTTON  (one flag-pill per locale)
# ─────────────────────────────────────────────
class LangButton(QPushButton):
    """A toggleable pill button for one language option."""

    # Map locale code → display label
    _LABELS = {"vi": "🇻🇳  Tiếng Việt", "en": "🇬🇧  English", "ja": "🇯🇵  日本語"}

    def __init__(self, code: str, parent=None):
        super().__init__(self._LABELS.get(code, code), parent)
        self.code = code
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(38)
        self._refresh_style(False)

    def _refresh_style(self, active: bool):
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background: #2D60FF;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 20px;
                    font-size: 13px;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    border: 1.5px solid #2D60FF;
                    color: #2D60FF;
                    background: transparent;
                    border-radius: 8px;
                    padding: 0 20px;
                    font-size: 13px;
                }
                QPushButton:hover { background: #EEF2FF; }
                QPushButton:pressed { background: #DDE4FF; }
            """)

    def set_active(self, active: bool):
        self.setChecked(active)
        self._refresh_style(active)


# ─────────────────────────────────────────────
#  SETTINGS WIDGET
# ─────────────────────────────────────────────
class SettingsWidget(QWidget):
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        self.settings = {"ai_limit": 10, "dark_mode": False}

        app = QApplication.instance()
        self.light_stylesheet = app.styleSheet()

        self._lm = LanguageManager.instance()
        self._lang_buttons: dict[str, LangButton] = {}

        self.setup_ui()
        self.connect_signals()

        # Re-render text whenever language changes
        self._lm.language_changed.connect(self._retranslate)

    # ══════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # Title
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size:22px; font-weight:bold;")
        root.addWidget(self.lbl_title)

        # ── (1) Language ─────────────────────────────────────────
        lang_content, self._lang_buttons = self._language_content()
        self._section_language = self._section("", lang_content)
        root.addWidget(self._section_language)

        # ── (2) Appearance ───────────────────────────────────────
        self._section_appear = self._section("", self._appearance_content())
        root.addWidget(self._section_appear)

        # ── (3) AI Settings ──────────────────────────────────────
        ai_content, self.ai_limit_input = self._ai_content()
        self._section_ai = self._section("", ai_content)
        root.addWidget(self._section_ai)

        # ── (4) Data ─────────────────────────────────────────────
        self._section_data = self._section("", self._data_content())
        root.addWidget(self._section_data)

        root.addStretch()

        # Save button
        self.save_btn = QPushButton()
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setFixedHeight(44)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #2D60FF;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover   { background: #1A4FE0; }
            QPushButton:pressed { background: #1440C0; }
        """)
        root.addWidget(self.save_btn)

        # Translate everything on first render
        self._retranslate()

    # ──────────────────────────────────────────
    #  Section wrapper
    # ──────────────────────────────────────────
    def _section(self, heading: str, content_widget: QWidget) -> QFrame:
        frame = QFrame()
        frame.setObjectName("SettingsSection")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        lbl = QLabel(heading)
        lbl.setObjectName("SectionHeading")
        lbl.setStyleSheet("font-size:15px; font-weight:bold; color:#2D60FF;")
        layout.addWidget(lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#E8ECF0;")
        layout.addWidget(sep)

        layout.addWidget(content_widget)
        return frame

    def _get_section_heading(self, frame: QFrame) -> QLabel:
        return frame.findChild(QLabel, "SectionHeading")

    # ──────────────────────────────────────────
    #  Language section
    # ──────────────────────────────────────────
    def _language_content(self):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._lang_desc = QLabel()
        self._lang_desc.setStyleSheet("color:#6F767E; font-size:13px;")

        layout.addWidget(self._lang_desc)
        layout.addStretch()

        buttons: dict[str, LangButton] = {}
        current = self._lm.lang

        for code in ("vi", "en", "ja"):
            btn = LangButton(code)
            btn.set_active(code == current)
            btn.clicked.connect(lambda _, c=code: self._select_language(c))
            layout.addWidget(btn)
            buttons[code] = btn

        return w, buttons

    # ──────────────────────────────────────────
    #  Appearance section
    # ──────────────────────────────────────────
    def _appearance_content(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)

        self._appear_desc = QLabel()
        self._appear_desc.setStyleSheet("color:#6F767E; font-size:13px;")

        self.dark_mode_btn = QPushButton()
        self.dark_mode_btn.setCursor(Qt.PointingHandCursor)
        self.dark_mode_btn.setFixedHeight(38)
        self.dark_mode_btn.setStyleSheet(self._ghost_btn_style())

        layout.addWidget(self._appear_desc)
        layout.addStretch()
        layout.addWidget(self.dark_mode_btn)
        return w

    # ──────────────────────────────────────────
    #  AI section
    # ──────────────────────────────────────────
    def _ai_content(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._ai_desc = QLabel()
        self._ai_desc.setStyleSheet("color:#6F767E; font-size:13px;")
        layout.addWidget(self._ai_desc)

        row = QHBoxLayout()
        self._ai_limit_lbl = QLabel()
        self._ai_limit_lbl.setFixedWidth(140)

        inp = QLineEdit()
        inp.setFixedWidth(200)
        inp.setFixedHeight(36)

        row.addWidget(self._ai_limit_lbl)
        row.addWidget(inp)
        row.addStretch()
        layout.addLayout(row)

        return w, inp

    # ──────────────────────────────────────────
    #  Data section
    # ──────────────────────────────────────────
    def _data_content(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._data_desc = QLabel()
        self._data_desc.setStyleSheet("color:#6F767E; font-size:13px;")

        self.export_btn = QPushButton()
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setFixedHeight(38)
        self.export_btn.setStyleSheet(self._ghost_btn_style())

        self.import_btn = QPushButton()
        self.import_btn.setCursor(Qt.PointingHandCursor)
        self.import_btn.setFixedHeight(38)
        self.import_btn.setStyleSheet(self._ghost_btn_style())

        layout.addWidget(self._data_desc)
        layout.addStretch()
        layout.addWidget(self.export_btn)
        layout.addWidget(self.import_btn)
        return w

    @staticmethod
    def _ghost_btn_style() -> str:
        return """
            QPushButton {
                border: 1.5px solid #2D60FF;
                color: #2D60FF;
                background: transparent;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
            }
            QPushButton:hover   { background: #EEF2FF; }
            QPushButton:pressed { background: #DDE4FF; }
        """

    # ══════════════════════════════════════════
    #  SIGNALS
    # ══════════════════════════════════════════
    def connect_signals(self):
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        self.export_btn.clicked.connect(self.export_flashcards)
        self.import_btn.clicked.connect(self.import_flashcards)
        self.save_btn.clicked.connect(self.save_settings)

    # ══════════════════════════════════════════
    #  RETRANSLATE  — called on every lang change
    # ══════════════════════════════════════════
    def _retranslate(self, _lang: str = ""):
        t = self._lm.tr          # shortcut

        # Page title
        self.lbl_title.setText(t("settings_title"))

        # Section headings
        self._get_section_heading(self._section_language).setText(t("language_title"))
        self._get_section_heading(self._section_appear).setText(t("appearance_title"))
        self._get_section_heading(self._section_ai).setText(t("ai_title"))
        self._get_section_heading(self._section_data).setText(t("data_title"))

        # Descriptions
        self._lang_desc.setText(t("language_desc"))
        self._appear_desc.setText(t("appearance_desc"))
        self._ai_desc.setText(t("ai_desc"))
        self._data_desc.setText(t("data_desc"))

        # Buttons & inputs
        dark_key = "dark_mode_off" if self.settings["dark_mode"] else "dark_mode_on"
        self.dark_mode_btn.setText(t(dark_key))
        self._ai_limit_lbl.setText(t("ai_limit_lbl"))
        self.ai_limit_input.setPlaceholderText(t("ai_limit_placeholder"))
        self.export_btn.setText(t("export_btn"))
        self.import_btn.setText(t("import_btn"))
        self.save_btn.setText(t("save_btn"))

        # Mark active language button
        for code, btn in self._lang_buttons.items():
            btn.set_active(code == self._lm.lang)

        # Propagate to dashboard sidebar (optional hook)
        if hasattr(self.dashboard, "retranslate_ui"):
            self.dashboard.retranslate_ui()

    # ══════════════════════════════════════════
    #  HANDLERS
    # ══════════════════════════════════════════
    def _select_language(self, code: str):
        """Switch active language and update button states immediately."""
        self._lm.set_lang(code)          # triggers language_changed → _retranslate

    def toggle_dark_mode(self):
        self.settings["dark_mode"] = not self.settings["dark_mode"]
        self.dashboard.apply_theme("dark" if self.settings["dark_mode"] else "light")
        self._retranslate()              # update button text after toggle

    def save_settings(self):
        raw = self.ai_limit_input.text().strip()
        if raw:
            if not raw.isdigit() or int(raw) <= 0:
                QMessageBox.warning(self, tr("invalid_input"), tr("invalid_input_msg"))
                return
            self.settings["ai_limit"] = int(raw)

        dark_str = tr("dark_on") if self.settings["dark_mode"] else tr("dark_off")
        QMessageBox.information(
            self,
            tr("saved_title"),
            tr("saved_msg", limit=self.settings["ai_limit"], dark=dark_str),
        )

    def export_flashcards(self):
        path, _ = QFileDialog.getSaveFileName(
            self, tr("export_btn"), "flashcards_export.json", "JSON Files (*.json)"
        )
        if not path:
            return

        dummy_data = {
            "exported_at": "2025-01-01T00:00:00",
            "flashcards": [
                {"id": 1, "front": "What is Python?", "back": "A programming language."},
                {"id": 2, "front": "What is PySide6?", "back": "Qt bindings for Python."},
            ],
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dummy_data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, tr("export_ok"), tr("export_ok_msg", path=path))
        except Exception as e:
            QMessageBox.critical(self, tr("export_fail"), str(e))

    def import_flashcards(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("import_btn"), "", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data.get("flashcards", []))
            QMessageBox.information(
                self, tr("import_ok"), tr("import_ok_msg", count=count, path=path)
            )
        except Exception as e:
            QMessageBox.critical(self, tr("import_fail"), str(e))