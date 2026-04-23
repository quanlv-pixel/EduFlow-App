import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QFrame, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt


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
    QPushButton#MenuBtn:hover {
        background: #2A2A3D;
    }
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
    QProgressBar {
        background: #45475A;
        border-radius: 3px;
    }
    QProgressBar::chunk {
        background: #89B4FA;
        border-radius: 3px;
    }
"""

LIGHT_STYLESHEET = ""  # PySide6 default


class SettingsWidget(QWidget):
    def __init__(self,dashboard):
        super().__init__()
        self.dashboard = dashboard
        self.settings = {
            "ai_limit": 10,
            "dark_mode": False,
        }

        app = QApplication.instance()
        self.light_stylesheet = app.styleSheet()

        self.setup_ui()
        self.connect_signals()

    # ================= UI =================
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # Title
        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size:22px; font-weight:bold;")
        root.addWidget(title)

        # (1) Appearance
        root.addWidget(self._section(
            "🎨 Appearance",
            self._appearance_content()
        ))

        # (2) AI Settings
        ai_content, self.ai_limit_input = self._ai_content()
        root.addWidget(self._section("🤖 AI Settings", ai_content))

        # (3) Data
        root.addWidget(self._section("🗂 Data", self._data_content()))

        root.addStretch()

        # (4) Save button
        self.save_btn = QPushButton("💾 Save Settings")
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
            QPushButton:hover { background: #1A4FE0; }
            QPushButton:pressed { background: #1440C0; }
        """)
        root.addWidget(self.save_btn)

    def _section(self, heading: str, content_widget: QWidget) -> QFrame:
        """Wrap a heading + content widget inside a styled card frame."""
        frame = QFrame()
        frame.setObjectName("SettingsSection")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        lbl = QLabel(heading)
        lbl.setStyleSheet("font-size:15px; font-weight:bold; color:#2D60FF;")
        layout.addWidget(lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#E8ECF0;")
        layout.addWidget(sep)

        layout.addWidget(content_widget)
        return frame

    def _appearance_content(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)

        desc = QLabel("Switch between light and dark theme.")
        desc.setStyleSheet("color:#6F767E; font-size:13px;")

        self.dark_mode_btn = QPushButton("🌙 Toggle Dark Mode")
        self.dark_mode_btn.setCursor(Qt.PointingHandCursor)
        self.dark_mode_btn.setFixedHeight(38)
        self.dark_mode_btn.setStyleSheet(self._ghost_btn_style())

        layout.addWidget(desc)
        layout.addStretch()
        layout.addWidget(self.dark_mode_btn)
        return w

    def _ai_content(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        desc = QLabel("Maximum number of flashcards generated per AI session.")
        desc.setStyleSheet("color:#6F767E; font-size:13px;")
        layout.addWidget(desc)

        row = QHBoxLayout()
        lbl = QLabel("Flashcard limit:")
        lbl.setFixedWidth(120)

        inp = QLineEdit()
        inp.setPlaceholderText("Enter number (e.g. 10)")
        inp.setFixedWidth(200)
        inp.setFixedHeight(36)

        row.addWidget(lbl)
        row.addWidget(inp)
        row.addStretch()
        layout.addLayout(row)

        return w, inp

    def _data_content(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        desc = QLabel("Export or import your flashcard data as JSON.")
        desc.setStyleSheet("color:#6F767E; font-size:13px;")

        self.export_btn = QPushButton("⬆ Export Flashcards")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setFixedHeight(38)
        self.export_btn.setStyleSheet(self._ghost_btn_style())

        self.import_btn = QPushButton("⬇ Import Flashcards")
        self.import_btn.setCursor(Qt.PointingHandCursor)
        self.import_btn.setFixedHeight(38)
        self.import_btn.setStyleSheet(self._ghost_btn_style())

        layout.addWidget(desc)
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
            QPushButton:hover { background: #EEF2FF; }
            QPushButton:pressed { background: #DDE4FF; }
        """

    # ================= SIGNALS =================
    def connect_signals(self):
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        self.export_btn.clicked.connect(self.export_flashcards)
        self.import_btn.clicked.connect(self.import_flashcards)
        self.save_btn.clicked.connect(self.save_settings)

    # ================= HANDLERS =================
    def toggle_dark_mode(self):
        self.settings["dark_mode"] = not self.settings["dark_mode"]

        if self.settings["dark_mode"]:
            self.dashboard.apply_theme("dark")
            self.dark_mode_btn.setText("☀️ Light Mode")
        else:
            self.dashboard.apply_theme("light")
            self.dark_mode_btn.setText("🌙 Dark Mode")

    def save_settings(self):
        raw = self.ai_limit_input.text().strip()
        if raw:
            if not raw.isdigit() or int(raw) <= 0:
                QMessageBox.warning(self, "Invalid Input",
                                    "Flashcard limit must be a positive integer.")
                return
            self.settings["ai_limit"] = int(raw)

        QMessageBox.information(
            self, "Saved",
            f"Settings saved!\n\n"
            f"• AI flashcard limit: {self.settings['ai_limit']}\n"
            f"• Dark mode: {'On' if self.settings['dark_mode'] else 'Off'}"
        )

    def export_flashcards(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Flashcards", "flashcards_export.json",
            "JSON Files (*.json)"
        )
        if not path:
            return

        dummy_data = {
            "exported_at": "2025-01-01T00:00:00",
            "flashcards": [
                {"id": 1, "front": "What is Python?", "back": "A programming language."},
                {"id": 2, "front": "What is PySide6?", "back": "Qt bindings for Python."},
            ]
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dummy_data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Export Successful",
                                    f"Flashcards exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def import_flashcards(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Flashcards", "",
            "JSON Files (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            count = len(data.get("flashcards", []))
            QMessageBox.information(
                self, "Import Successful",
                f"Loaded {count} flashcard(s) from:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", str(e))