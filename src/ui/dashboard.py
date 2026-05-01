from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QLineEdit,
    QProgressBar, QStackedWidget, QApplication
)
from PySide6.QtCore import Qt, Signal
from datetime import datetime

from src.ui.schedule import ScheduleWidget
from src.ui.summary import SummaryWidget
from src.ui.flashcard import FlashcardWidget
from src.ui.course import CoursesWidget
from src.ui.settings_widget import SettingsWidget, LanguageManager, tr
from src.ui.todo_widget import TodoWidget
from src.ui.grade_widget import GradeWidget                      # ← NEW
from src.services.schedule_notifier import ScheduleNotifier

from src.controllers.flashcard_controller import FlashcardController
from src.controllers.course_controller import CourseController
from src.controllers.summary_controller import SummaryController
from src.controllers.schedule_controller import ScheduleController
from src.controllers.grade_controller import GradeController     # ← NEW


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
        self.db = db
        self.ai = ai

        # Controllers
        self.course_controller   = CourseController(self.db, self.ai)
        self.flash_controller    = FlashcardController(self.db, self.ai)
        self.summary_controller  = SummaryController(self.ai, self.db)
        self.schedule_controller = ScheduleController(self.db)
        self.grade_controller    = GradeController(self.db)      # ← NEW
        self.notifier = ScheduleNotifier(self.schedule_controller, self.user_info["id"])

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
        self.current_theme = "light"
        self.apply_theme("light")

        self.retranslate_ui()

        # Cập nhật sidebar text mỗi khi ngôn ngữ thay đổi
        LanguageManager.instance().language_changed.connect(
            lambda _: self.retranslate_ui()
        )

    # ================= SIDEBAR =================
    def setup_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 30, 20, 20)

        logo = QLabel("📘 EduFlow")
        logo.setStyleSheet("font-size:22px;font-weight:bold;color:#2D60FF;")
        layout.addWidget(logo)

        layout.addSpacing(30)

        # ── "grades" được chèn giữa "todo" và "settings" ──
        self.menu_items = [
            "overview", "schedule", "courses",
            "flash", "summary", "todo",
            "grades",        # ← NEW (nằm giữa todo và settings)
            "settings",
        ]
        names = [
            tr("menu_overview"), tr("menu_schedule"), tr("menu_courses"),
            tr("menu_flash"),    tr("menu_summary"),  tr("menu_todo"),
            tr("menu_grades"),   # ← NEW
            tr("menu_settings"),
        ]

        self.menu_buttons = {}

        for key, text in zip(self.menu_items, names):
            btn = DashMenuButton(f"  {text}")
            layout.addWidget(btn)
            self.menu_buttons[key] = btn

            page = self.create_page(key)
            self.page_map[key] = page
            self.pages.addWidget(page)

            btn.clicked.connect(lambda _, k=key: self.switch_page(k))

        self.menu_buttons["overview"].setChecked(True)

        layout.addStretch()

        # USER INFO
        user_frame  = QFrame()
        user_layout = QHBoxLayout(user_frame)

        avatar = QLabel(self.user_info["name"][0])
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("background:#555;color:white;border-radius:20px;")

        info = QVBoxLayout()
        info.addWidget(QLabel(self.user_info["name"]))
        info.addWidget(QLabel(self.user_info["email"]))

        user_layout.addWidget(avatar)
        user_layout.addLayout(info)

        layout.addWidget(user_frame)

        # LOGOUT
        self.logout_btn = QPushButton(tr("logout"))
        self.logout_btn.setObjectName("LogoutBtn")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(self.logout_btn)

        self.main_layout.addWidget(sidebar)

    # ================= CONTENT =================
    def setup_content(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(25)

        # HEADER
        header = QHBoxLayout()

        self.greeting = QLabel()
        self.greeting.setTextFormat(Qt.RichText)
        self.greeting.setStyleSheet("font-size:24px;font-weight:bold;")

        self.search = QLineEdit()
        self.search.setFixedWidth(250)

        btn_add = QPushButton("+")
        btn_add.setFixedSize(40, 40)
        btn_add.setStyleSheet("""
            background:#2D60FF;
            color:white;
            border-radius:10px;
            font-size:18px;
        """)

        header.addWidget(self.greeting)
        header.addStretch()
        header.addWidget(self.search)
        header.addWidget(btn_add)

        layout.addLayout(header)
        layout.addWidget(self.pages)

        self.main_layout.addWidget(container)

    # ================= GREETING =================
    def get_greeting(self):
        now  = datetime.now()
        hour = now.hour

        if hour < 12:
            time_str = tr("greeting_morning")
        elif hour < 18:
            time_str = tr("greeting_afternoon")
        else:
            time_str = tr("greeting_evening")

        days = [
            tr("mon"), tr("tue"), tr("wed"),
            tr("thu"), tr("fri"), tr("sat"), tr("sun")
        ]

        day_name = days[now.weekday()]
        date_str = f"{day_name}, {now.day}/{now.month}/{now.year}"

        return f"""
        {time_str}! 👋<br>
        <span style='font-size:13px;color:#6F767E;'>
        {date_str}
        </span>
        """

    # ================= SWITCH =================
    def switch_page(self, key):
        for k, btn in self.menu_buttons.items():
            btn.setChecked(k == key)

        self.pages.setCurrentWidget(self.page_map[key])

    # ================= CREATE PAGE =================
    def create_page(self, key):
        if key == "overview":
            return self.create_overview_page()

        elif key == "schedule":
            return ScheduleWidget(self.schedule_controller, self.user_info["id"])

        elif key == "courses":
            return CoursesWidget(self.course_controller, self.user_info["id"])

        elif key == "flash":
            return FlashcardWidget(self.flash_controller, self.user_info["id"])

        elif key == "summary":
            return SummaryWidget(self.summary_controller, self.user_info["id"])

        elif key == "todo":
            return TodoWidget()

        elif key == "grades":                                       # ← NEW
            return GradeWidget(self.grade_controller, self.user_info["id"])

        elif key == "settings":
            return SettingsWidget(self)

    # ================= OVERVIEW =================
    def create_overview_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(25)

        # ===== CARDS =====
        cards = QHBoxLayout()

        # BLUE CARD
        blue = QFrame()
        blue.setObjectName("CardBlue")
        v1 = QVBoxLayout(blue)

        top = QHBoxLayout()
        top.addWidget(QLabel("📘"))
        top.addStretch()

        badge = QLabel(tr("semester"))
        badge.setStyleSheet("background:rgba(255,255,255,0.2);padding:4px 10px;border-radius:10px;")
        top.addWidget(badge)

        v1.addLayout(top)
        self.lbl_courses = QLabel()
        v1.addWidget(self.lbl_courses)

        total = len(self.db.get_courses(self.user_info["id"]))
        num = QLabel(str(total))
        num.setStyleSheet("font-size:40px;font-weight:bold;")
        v1.addWidget(num)

        # WHITE CARD
        white = QFrame()
        white.setObjectName("CardWhite")
        v2 = QVBoxLayout(white)

        top2 = QHBoxLayout()
        top2.addWidget(QLabel("✅"))
        top2.addStretch()

        percent = QLabel("+12%")
        percent.setStyleSheet("color:#10B981;font-weight:bold;")
        top2.addWidget(percent)

        v2.addLayout(top2)
        self.lbl_avg = QLabel()
        v2.addWidget(self.lbl_avg)

        avg = QLabel("78%")
        avg.setStyleSheet("font-size:40px;font-weight:bold;color:#2D60FF;")
        v2.addWidget(avg)

        cards.addWidget(blue, 2)
        cards.addWidget(white, 1)

        layout.addLayout(cards)

        # ===== ROW 2 =====
        row2 = QHBoxLayout()

        # schedule
        sch = QFrame()
        sch.setObjectName("CardWhite")
        v = QVBoxLayout(sch)
        v.setSpacing(8)

        self.lbl_today = QLabel()
        v.addWidget(self.lbl_today)

        today_col      = datetime.now().weekday()
        all_schedules  = self.db.get_schedule(self.user_info["id"]) or []
        today_schedules = sorted(
            [s for s in all_schedules if s.get("day") == today_col],
            key=lambda s: s.get("start_time", 0)
        )

        if not today_schedules:
            v.addStretch()
            self.no_schedule_label = QLabel()
            self.no_schedule_label.setAlignment(Qt.AlignCenter)
            self.no_schedule_label.setText(tr("no_schedule"))

            v.addWidget(self.no_schedule_label)

            v.addStretch()
        else:
            v.addSpacing(4)
            for s in today_schedules:
                item = QFrame()
                item.setObjectName("ScheduleItem")
                h = QHBoxLayout(item)
                h.setContentsMargins(10, 6, 10, 6)

                bar = QFrame()
                bar.setObjectName("ScheduleAccentBar")
                bar.setFixedWidth(4)
                h.addWidget(bar)
                h.addSpacing(8)

                info_v = QVBoxLayout()
                lbl_course = QLabel(f"<b>{s.get('course', '')}</b>")
                lbl_course.setObjectName("ScheduleItemTitle")
                sh, sm = s["start_time"] // 60, s["start_time"] % 60
                eh, em = s["end_time"]   // 60, s["end_time"]   % 60
                time_room = f"{sh:02d}:{sm:02d} – {eh:02d}:{em:02d}"
                if s.get("room"):
                    time_room += f"  •  {s['room']}"
                lbl_detail = QLabel(time_room)
                lbl_detail.setObjectName("ScheduleItemDetail")
                info_v.addWidget(lbl_course)
                info_v.addWidget(lbl_detail)

                h.addLayout(info_v)
                h.addStretch()
                v.addWidget(item)

            v.addStretch()

        # progress
        prog = QFrame()
        prog.setObjectName("CardWhite")
        prog.setFixedWidth(300)

        vp = QVBoxLayout(prog)
        self.lbl_progress = QLabel()
        vp.addWidget(self.lbl_progress)

        subjects = [("Cơ sở dữ liệu", 40), ("Python", 65), ("AI", 85)]

        for name, val in subjects:
            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            row.addStretch()
            row.addWidget(QLabel(f"{val}%"))

            bar = QProgressBar()
            bar.setValue(val)
            bar.setTextVisible(False)
            bar.setFixedHeight(6)

            vp.addLayout(row)
            vp.addWidget(bar)

        row2.addWidget(sch, 2)
        row2.addWidget(prog, 1)

        layout.addLayout(row2)

        return page

    # ================= THEME =================
    def load_qss(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def apply_theme(self, theme):
        app = QApplication.instance()

        if theme == "dark":
            qss = self.load_qss("assets/style_dark.qss")
            self.current_theme = "dark"
        else:
            qss = self.load_qss("assets/style.qss")
            self.current_theme = "light"

        app.setStyleSheet(qss)

    # ================= RETRANSLATE =================
    def retranslate_ui(self):
        if not hasattr(self, "menu_buttons"):
            return

        menu_keys = {
            "overview": "menu_overview",
            "schedule": "menu_schedule",
            "courses":  "menu_courses",
            "flash":    "menu_flash",
            "summary":  "menu_summary",
            "todo":     "menu_todo",
            "grades":   "menu_grades",   # ← NEW
            "settings": "menu_settings",
        }

        for key, tr_key in menu_keys.items():
            btn = self.menu_buttons.get(key)
            if btn:
                btn.setText(f"  {tr(tr_key)}")

        if hasattr(self, "logout_btn"):
            self.logout_btn.setText(tr("logout"))

        if hasattr(self, "greeting"):
            self.greeting.setText(self.get_greeting())

        if hasattr(self, "search"):
            self.search.setPlaceholderText(f"🔍 {tr('search')}")

        if hasattr(self, "lbl_courses"):
            self.lbl_courses.setText(tr("courses_studying"))

        if hasattr(self, "lbl_avg"):
            self.lbl_avg.setText(tr("avg_progress"))

        if hasattr(self, "lbl_today"):
            self.lbl_today.setText(f"<b>{tr('today_schedule')}</b>")

        if hasattr(self, "lbl_progress"):
            self.lbl_progress.setText(f"<b>{tr('study_progress')}</b>")

        if hasattr(self, "no_schedule_label"):
            self.no_schedule_label.setText(tr("no_schedule"))

    # ================= LOGOUT =================
    def handle_logout(self):
        self.logout_signal.emit()
        self.deleteLater()