from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QLineEdit,
    QProgressBar, QStackedWidget, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer
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

        # Auto-refresh overview mỗi 30 giây khi đang ở tab tổng quan
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(30000)  # 30s
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start()

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
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(10)

        # Avatar — lấy chữ cái đầu của tên
        name_str = self.user_info.get("name") or "?"
        avatar = QLabel(name_str[0].upper())
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            "background:#2D60FF;color:white;border-radius:20px;"
            "font-size:16px;font-weight:bold;"
        )

        info = QVBoxLayout()
        info.setSpacing(1)

        lbl_name = QLabel(self.user_info.get("name", ""))
        lbl_name.setStyleSheet("font-weight:600;font-size:13px;")

        # Hiện username nếu có, fallback sang email
        username = self.user_info.get("username")
        sub_text = f"@{username}" if username else self.user_info.get("email", "")
        lbl_sub = QLabel(sub_text)
        lbl_sub.setStyleSheet("color:#6F767E;font-size:11px;")
        lbl_sub.setToolTip(self.user_info.get("email", ""))  # hover để xem email

        info.addWidget(lbl_name)
        info.addWidget(lbl_sub)

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

        # Refresh overview mỗi khi user click vào tab Tổng quan
        if key == "overview":
            self.refresh_overview()

    # ================= CREATE PAGE =================
    def create_page(self, key):
        if key == "overview":
            return self.create_overview_page()

        elif key == "schedule":
            return ScheduleWidget(self.schedule_controller, self.user_info["id"])

        elif key == "courses":
            return CoursesWidget(self.course_controller, self.user_info["id"])

        elif key == "flash":
            self.flash_widget = FlashcardWidget(self.flash_controller, self.user_info["id"])
            return self.flash_widget

        elif key == "summary":
            return SummaryWidget(self.summary_controller, self.user_info["id"])

        elif key == "todo":
            return TodoWidget()

        elif key == "grades":                                       # ← NEW
            return GradeWidget(self.grade_controller, self.user_info["id"])

        elif key == "settings":
            self.settings_widget = SettingsWidget(self)
            # Kết nối signal giới hạn flashcard → FlashcardWidget
            if hasattr(self, "flash_widget"):
                self.settings_widget.ai_limit_changed.connect(self.flash_widget.set_ai_limit)
            return self.settings_widget

    # ================= OVERVIEW =================
    def create_overview_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(25)

        # ===== CARDS =====
        cards = QHBoxLayout()

        # BLUE CARD — số khóa học
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

        # Lưu lại để refresh được
        self.lbl_total_courses = QLabel("0")
        self.lbl_total_courses.setStyleSheet("font-size:40px;font-weight:bold;")
        v1.addWidget(self.lbl_total_courses)

        # WHITE CARD — % trung bình
        white = QFrame()
        white.setObjectName("CardWhite")
        v2 = QVBoxLayout(white)
        top2 = QHBoxLayout()
        top2.addWidget(QLabel("✅"))
        top2.addStretch()
        v2.addLayout(top2)

        self.lbl_avg = QLabel()
        v2.addWidget(self.lbl_avg)

        self.lbl_avg_num = QLabel("0%")
        self.lbl_avg_num.setStyleSheet("font-size:40px;font-weight:bold;color:#2D60FF;")
        v2.addWidget(self.lbl_avg_num)

        cards.addWidget(blue, 2)
        cards.addWidget(white, 1)
        layout.addLayout(cards)

        # ===== ROW 2 =====
        row2 = QHBoxLayout()

        # Schedule card
        sch = QFrame()
        sch.setObjectName("CardWhite")
        self._sch_layout = QVBoxLayout(sch)
        self._sch_layout.setSpacing(8)

        self.lbl_today = QLabel()
        self._sch_layout.addWidget(self.lbl_today)
        # Nội dung schedule sẽ được fill bởi refresh_overview()

        # Progress card
        prog = QFrame()
        prog.setObjectName("CardWhite")
        prog.setFixedWidth(300)

        self._prog_layout = QVBoxLayout(prog)
        self._prog_layout.setSpacing(10)

        self.lbl_progress = QLabel()
        self._prog_layout.addWidget(self.lbl_progress)
        # Nội dung progress sẽ được fill bởi refresh_overview()

        row2.addWidget(sch, 2)
        row2.addWidget(prog, 1)
        layout.addLayout(row2)

        # Fill data lần đầu
        self.refresh_overview()

        return page

    def refresh_overview(self):
        """Cập nhật toàn bộ số liệu trên trang Tổng quan từ DB."""
        user_id = self.user_info["id"]

        # ── Card số khóa học ──────────────────────────────────
        if hasattr(self, "lbl_total_courses"):
            try:
                total = len(self.db.get_courses(user_id) or [])
                self.lbl_total_courses.setText(str(total))
            except RuntimeError:
                pass

        # ── Card % trung bình ─────────────────────────────────
        if hasattr(self, "lbl_avg_num"):
            try:
                courses = self.db.get_courses(user_id) or []
                if courses:
                    avg_val = int(
                        sum(self.db.get_course_progress(c["id"]) for c in courses)
                        / len(courses)
                    )
                else:
                    avg_val = 0
                self.lbl_avg_num.setText(f"{avg_val}%")
            except RuntimeError:
                pass

        # ── Schedule hôm nay ──────────────────────────────────
        if hasattr(self, "_sch_layout"):
            try:
                self._refresh_schedule()
            except RuntimeError:
                pass

        # ── Progress từng khóa ────────────────────────────────
        if hasattr(self, "_prog_layout"):
            try:
                self._refresh_progress()
            except RuntimeError:
                pass

    def _refresh_schedule(self):
        """Xóa và vẽ lại danh sách lịch hôm nay."""
        layout = self._sch_layout
        # Xóa hết widget cũ trừ lbl_today (index 0)
        while layout.count() > 1:
            item = layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                layout.removeItem(item)

        today_col = datetime.now().weekday()
        all_schedules = self.db.get_schedule(self.user_info["id"]) or []
        today_schedules = sorted(
            [s for s in all_schedules if s.get("day") == today_col],
            key=lambda s: s.get("start_time", 0)
        )

        if not today_schedules:
            layout.addStretch()
            lbl = QLabel(tr("no_schedule"))
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            layout.addStretch()
        else:
            layout.addSpacing(4)
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
                layout.addWidget(item)
            layout.addStretch()

    def _refresh_progress(self):
        """Xóa và vẽ lại danh sách tiến độ khóa học."""
        layout = self._prog_layout
        # Xóa hết widget cũ trừ lbl_progress (index 0)
        while layout.count() > 1:
            item = layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                layout.removeItem(item)

        courses_list = self.db.get_courses(self.user_info["id"]) or []

        if not courses_list:
            lbl = QLabel("Chưa có khóa học nào.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#9BA3AF;font-size:13px;")
            layout.addStretch()
            layout.addWidget(lbl)
            layout.addStretch()
            return

        for c in courses_list[:5]:
            course_progress = self.db.get_course_progress(c["id"])
            course_name = c.get("name", "")
            display_name = (course_name[:22] + "…") if len(course_name) > 24 else course_name

            row = QHBoxLayout()
            row.setSpacing(6)

            lbl_name = QLabel(display_name)
            lbl_name.setStyleSheet("font-size:12px;color:#1E2328;")

            lbl_pct = QLabel(f"{course_progress}%")
            lbl_pct.setStyleSheet(
                "font-size:12px;font-weight:bold;"
                + ("color:#10B981;" if course_progress == 100 else "color:#2D60FF;")
            )

            row.addWidget(lbl_name)
            row.addStretch()
            row.addWidget(lbl_pct)

            bar_widget = QProgressBar()
            bar_widget.setValue(course_progress)
            bar_widget.setTextVisible(False)
            bar_widget.setFixedHeight(6)
            chunk_color = "#10B981" if course_progress == 100 else "#2D60FF"
            bar_widget.setStyleSheet(f"""
                QProgressBar {{
                    border:none; background:#EEF0F4; border-radius:3px;
                }}
                QProgressBar::chunk {{
                    background:{chunk_color}; border-radius:3px;
                }}
            """)

            layout.addLayout(row)
            layout.addWidget(bar_widget)

        if len(courses_list) > 5:
            lbl_more = QLabel(f"+ {len(courses_list) - 5} khóa học khác")
            lbl_more.setStyleSheet("color:#6F767E;font-size:11px;")
            lbl_more.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_more)

        layout.addStretch()

    def _auto_refresh(self):
        """Chỉ refresh khi đang ở tab overview — tránh load DB không cần thiết."""
        current = self.pages.currentWidget()
        overview = self.page_map.get("overview")
        if current is overview:
            self.refresh_overview()

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