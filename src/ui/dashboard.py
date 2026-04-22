from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QLineEdit,
    QStackedWidget
)
from PySide6.QtCore import Qt, Signal

from src.ui.schedule import ScheduleWidget
from src.ui.summary import SummaryWidget
from src.ui.flashcard import FlashcardWidget
from src.ui.course import CoursesWidget

from src.controllers.flashcard_controller import FlashcardController
from src.controllers.course_controller import CourseController
from src.controllers.summary_controller import SummaryController
from src.controllers.schedule_controller import ScheduleController


# ================= MENU BUTTON =================
class DashMenuButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("MenuBtn")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)


# ================= MAIN =================
class EduDashboard(QMainWindow):
    logout_signal = Signal()

    def __init__(self, user_info, db, ai):
        super().__init__()

        self.user_info = user_info
        self.user_id = user_info["id"]

        self.db = db
        self.ai = ai

        # ===== CONTROLLERS =====
        self.course_controller = CourseController(self.db, self.ai)
        self.flash_controller = FlashcardController(self.db, self.ai)
        self.summary_controller = SummaryController(self.ai, self.db)
        self.schedule_controller = ScheduleController(self.db)

        self.setWindowTitle("EduFlow - Dashboard")
        self.resize(1300, 850)

        central = QWidget()
        self.setCentralWidget(central)

        self.main_layout = QHBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.pages = QStackedWidget()
        self.page_map = {}

        self.setup_sidebar()
        self.setup_content()

    # ================= SIDEBAR =================
    def setup_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(280)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(25, 40, 25, 25)

        logo = QLabel("📘 EduFlow")
        logo.setStyleSheet("font-size:24px;font-weight:bold;color:#2D60FF;")
        layout.addWidget(logo)

        # ===== MENU =====
        self.menu_items = [
            ("overview", "  Tổng quan"),
            ("schedule", "  Thời khóa biểu"),
            ("courses", "  Khóa học"),
            ("flash", "  Flashcards"),
            ("summary", "  Tóm tắt AI"),
        ]

        self.menu_buttons = {}

        for key, text in self.menu_items:
            btn = DashMenuButton(text)
            layout.addWidget(btn)

            self.menu_buttons[key] = btn

            page = self.create_page(key)
            self.page_map[key] = page
            self.pages.addWidget(page)

            btn.clicked.connect(lambda _, k=key: self.switch_page(k))

        self.menu_buttons["overview"].setChecked(True)
        layout.addStretch()

        # ===== USER =====
        user_frame = QFrame()
        user_layout = QHBoxLayout(user_frame)

        avatar = QLabel(self.user_info["name"][0].upper())
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            "background:#535C67;color:white;border-radius:20px;font-weight:bold;"
        )

        info = QVBoxLayout()
        info.addWidget(QLabel(self.user_info["name"]))
        info.addWidget(QLabel(self.user_info["email"]))

        user_layout.addWidget(avatar)
        user_layout.addLayout(info)

        layout.addWidget(user_frame)

        logout_btn = QPushButton("↪ Đăng xuất")
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)

        self.main_layout.addWidget(sidebar)

    # ================= CREATE PAGE =================
    def create_page(self, key):
        if key == "overview":
            return self.create_overview_page()

        elif key == "schedule":
            return ScheduleWidget(
                controller=self.schedule_controller,
                user_id=self.user_info["id"]
            )

        elif key == "courses":
            return CoursesWidget(
                controller=self.course_controller,
                user_id=self.user_id
            )

        elif key == "flash":
            return FlashcardWidget(
                controller=self.flash_controller,
                user_id=self.user_id
            )

        elif key == "summary":
            return SummaryWidget(
                controller=self.summary_controller,
                user_id=self.user_info["id"]
            )

    # ================= CONTENT =================
    def setup_content(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        header = QHBoxLayout()

        greeting = QLabel(f"Chào {self.user_info['name']} 👋")
        greeting.setStyleSheet("font-size:22px;font-weight:bold;")

        search = QLineEdit()
        search.setPlaceholderText("🔍 Tìm kiếm...")

        header.addWidget(greeting)
        header.addStretch()
        header.addWidget(search)

        layout.addLayout(header)
        layout.addWidget(self.pages)

        self.main_layout.addWidget(container)

    # ================= SWITCH =================
    def switch_page(self, key):
        for k, btn in self.menu_buttons.items():
            btn.setChecked(k == key)

        self.pages.setCurrentWidget(self.page_map[key])

    # ================= OVERVIEW =================
    def create_overview_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        courses = self.db.get_courses(self.user_id)
        total = len(courses)

        avg = 0
        if total > 0:
            avg = sum([c.get("progress", 0) for c in courses]) // total

        lbl = QLabel(f"Bạn có {total} khóa học\nTiến độ TB: {avg}%")
        lbl.setStyleSheet("font-size:18px;")

        layout.addWidget(lbl)
        layout.addStretch()

        return page

    # ================= LOGOUT =================
    def handle_logout(self):
        self.logout_signal.emit()
        self.close()