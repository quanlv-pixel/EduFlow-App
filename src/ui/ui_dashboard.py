from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QLineEdit,
    QProgressBar, QStackedWidget
)
from PySide6.QtCore import Qt, Signal

from src.ui.ui_schedule import ScheduleWidget
from src.ui.ui_summary import SummaryWidget
from src.ui.ui_flashcard import FlashcardWidget
from src.ui.ui_course import CoursesWidget   


# ================= MENU BUTTON =================
class DashMenuButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("MenuBtn")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)


# ================= MAIN DASHBOARD =================
class EduDashboard(QMainWindow):
    logout_signal = Signal()

    def __init__(self, user_info=None):
        super().__init__()

        self.user_info = user_info or {
            "name": "LÊ VĂN QUÂN",
            "email": "quanlv.25ai@vku.udn.vn"
        }

        self.setWindowTitle("EduFlow - Dashboard")
        self.resize(1300, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

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

        # LOGO
        logo = QLabel("📘 EduFlow")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D60FF;")
        layout.addWidget(logo)

        # MENU ITEMS
        self.menu_items = [
            ("overview", "  Tổng quan", self.create_overview_page),
            ("schedule", "  Thời khóa biểu", ScheduleWidget),
            ("courses", "  Khóa học", CoursesWidget),   # 👈 ĐÃ THÊM
            ("flash", "  Flashcards", FlashcardWidget),
            ("summary", "  Tóm tắt AI", SummaryWidget),
        ]

        self.menu_buttons = {}

        for key, text, widget_cls in self.menu_items:
            btn = DashMenuButton(text)
            layout.addWidget(btn)
            self.menu_buttons[key] = btn

            # tạo page
            page = widget_cls() if callable(widget_cls) else widget_cls
            self.page_map[key] = page
            self.pages.addWidget(page)

            btn.clicked.connect(lambda checked, k=key: self.switch_page(k))

        # default page
        self.menu_buttons["overview"].setChecked(True)

        layout.addStretch()

        # USER INFO
        user_frame = QFrame()
        user_layout = QHBoxLayout(user_frame)

        avatar = QLabel(self.user_info['name'][0].upper())
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            "background:#535C67;color:white;border-radius:20px;font-weight:bold;"
        )

        info = QVBoxLayout()

        name = QLabel(self.user_info['name'])
        name.setStyleSheet("font-weight:bold;font-size:13px;")

        email = QLabel(self.user_info['email'])
        email.setStyleSheet("color:#6F767E;font-size:11px;")

        info.addWidget(name)
        info.addWidget(email)

        user_layout.addWidget(avatar)
        user_layout.addLayout(info)

        layout.addWidget(user_frame)

        # LOGOUT
        logout_btn = QPushButton("↪ Đăng xuất")
        logout_btn.setStyleSheet(
            "color:#FF4D4F;border:none;text-align:left;padding:10px 0;font-weight:bold;"
        )
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)

        self.main_layout.addWidget(sidebar)

    # ================= CONTENT =================
    def setup_content(self):
        container = QWidget()
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(35, 30, 35, 30)
        content_layout.setSpacing(25)

        # HEADER
        header = QHBoxLayout()

        greeting = QLabel(
            "Chào mừng trở lại! 👋<br>"
            "<span style='font-size:12px;color:#6F767E;'>Hôm nay là Thứ Hai</span>"
        )
        greeting.setTextFormat(Qt.RichText)
        greeting.setStyleSheet("font-size:22px;font-weight:bold;")

        search = QLineEdit()
        search.setPlaceholderText("🔍 Tìm kiếm...")
        search.setFixedWidth(280)
        search.setStyleSheet(
            "padding:10px;border-radius:10px;border:1px solid #EAEAEA;background:white;font-family: 'Segoe UI',sans-serif; font-size: 15px; color: black;"
        )

        header.addWidget(greeting)
        header.addStretch()
        header.addWidget(search)

        content_layout.addLayout(header)
        content_layout.addWidget(self.pages)

        self.main_layout.addWidget(container)

    # ================= SWITCH PAGE =================
    def switch_page(self, key):
        for k, btn in self.menu_buttons.items():
            btn.setChecked(k == key)

        self.pages.setCurrentWidget(self.page_map[key])

    # ================= OVERVIEW =================
    def create_overview_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(25)

        # ===== CARDS =====
        cards = QHBoxLayout()
        cards.setSpacing(20)

        # BLUE CARD
        card_blue = QFrame()
        card_blue.setObjectName("CardBlue")
        v1 = QVBoxLayout(card_blue)

        lbl1 = QLabel("📘 Khóa học đang học")
        lbl2 = QLabel("3")
        lbl2.setStyleSheet("font-size:48px;font-weight:bold;")

        v1.addWidget(lbl1)
        v1.addWidget(lbl2)
        v1.addStretch()

        # WHITE CARD
        card_white = QFrame()
        card_white.setObjectName("CardWhite")
        v2 = QVBoxLayout(card_white)

        lbl3 = QLabel("Tiến độ trung bình")
        lbl4 = QLabel("78%")
        lbl4.setStyleSheet("font-size:48px;font-weight:bold;color:#2D60FF;")

        v2.addWidget(lbl3)
        v2.addWidget(lbl4)
        v2.addStretch()

        cards.addWidget(card_blue)
        cards.addWidget(card_white)

        layout.addLayout(cards)

        # ===== ROW 2 =====
        row2 = QHBoxLayout()
        row2.setSpacing(20)

        # SCHEDULE CARD
        sch = QFrame()
        sch.setObjectName("CardWhite")
        sch_v = QVBoxLayout(sch)

        title = QLabel("<b>Lịch học hôm nay</b>")
        msg = QLabel("Không có lịch học nào hôm nay.")
        msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet("color:#999;")

        sch_v.addWidget(title)
        sch_v.addStretch()
        sch_v.addWidget(msg)
        sch_v.addStretch()

        # PROGRESS CARD
        prog = QFrame()
        prog.setObjectName("CardWhite")
        prog.setFixedWidth(320)
        prog_v = QVBoxLayout(prog)

        title2 = QLabel("<b>Tiến độ học tập</b>")
        prog_v.addWidget(title2)

        subjects = [
            ("Cơ sở dữ liệu", 40),
            ("Python", 65),
            ("AI", 85)
        ]

        for name, val in subjects:
            lbl = QLabel(f"{name} ({val}%)")
            bar = QProgressBar()
            bar.setValue(val)
            bar.setFixedHeight(8)
            bar.setTextVisible(False)

            prog_v.addWidget(lbl)
            prog_v.addWidget(bar)

        row2.addWidget(sch, 2)
        row2.addWidget(prog, 1)

        layout.addLayout(row2)

        return page

    # ================= LOGOUT =================
    def handle_logout(self):
        self.logout_signal.emit()
        self.close()