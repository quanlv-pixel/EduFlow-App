from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QLineEdit,
    QProgressBar, QStackedWidget, QApplication,
    QDialog, QFormLayout, QMessageBox, QDialogButtonBox,
    QGridLayout
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

def parse_time_to_minutes(value):
    try:
        if isinstance(value, str):
            parts = value.split(":")
            h = int(parts[0])
            m = int(parts[1])

            return h * 60 + m

        return int(value)

    except Exception:
        return 0

# ================= CLICKABLE FRAME =================
class ClickableFrame(QFrame):
    """QFrame bắt sự kiện click chuột, phát signal clicked."""
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


# ================= PROFILE DIALOG =================
class ProfileDialog(QDialog):
    def __init__(self, user_info: dict, db, parent=None, current_theme="light"):
        super().__init__(parent)
        self.user_info = user_info
        self.db = db
        self.current_theme = current_theme

        # ===== THEME COLORS =====
        is_dark = (self.current_theme == "dark")
        bg_main        = "#1E1E2E" if is_dark else "#FFFFFF"
        text_main      = "#CDD6F4" if is_dark else "#111827"
        text_sub       = "#A6ADC8" if is_dark else "#6B7280"
        input_bg       = "#313244" if is_dark else "#F9FAFB"
        input_focus_bg = "#1E1E2E" if is_dark else "#FFFFFF"
        input_border   = "#45475A" if is_dark else "#E5E7EB"
        input_readonly = "#181825" if is_dark else "#F3F4F6"
        btn_can_bg     = "#313244" if is_dark else "#F3F4F6"
        btn_can_txt    = "#CDD6F4" if is_dark else "#4B5563"
        btn_can_hvr    = "#45475A" if is_dark else "#E5E7EB"

        self.setWindowTitle(tr("profile_title"))
        self.setFixedSize(650, 480)
        self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {bg_main}; }}")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # 1. HEADER
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        lbl_title = QLabel(tr("profile_title"))
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {text_main};")
        
        lbl_desc = QLabel(tr("profile_desc"))
        lbl_desc.setStyleSheet(f"font-size: 13px; color: {text_sub};")
        
        header_layout.addWidget(lbl_title)
        header_layout.addWidget(lbl_desc)
        main_layout.addLayout(header_layout)

        # 2. AVATAR & STATUS
        avatar_status_layout = QHBoxLayout()
        avatar_status_layout.setSpacing(20)

        name_str = self.user_info.get("name") or "?"
        avatar_char = name_str[0].upper()
        self.avatar_lbl = QLabel(avatar_char)
        self.avatar_lbl.setFixedSize(80, 80)
        self.avatar_lbl.setAlignment(Qt.AlignCenter)
        self.avatar_lbl.setStyleSheet("""
            background-color: #2D60FF;
            color: white;
            border-radius: 16px;
            font-size: 32px;
            font-weight: bold;
        """)
        avatar_status_layout.addWidget(self.avatar_lbl)

        status_layout = QVBoxLayout()
        status_layout.setSpacing(8)
        status_layout.setAlignment(Qt.AlignVCenter)

        lbl_status_title = QLabel(tr("profile_status_title"))
        lbl_status_title.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {text_sub}; letter-spacing: 1px;")
        
        indicator_layout = QHBoxLayout()
        indicator_layout.setSpacing(8)
        
        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet("background-color: #10B981; border-radius: 5px;") 
        
        lbl_status_text = QLabel(tr("profile_status_active"))
        lbl_status_text.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {text_main};")
        
        indicator_layout.addWidget(dot)
        indicator_layout.addWidget(lbl_status_text)
        indicator_layout.addStretch()

        lbl_status_desc = QLabel(tr("profile_avatar_desc"))
        lbl_status_desc.setStyleSheet(f"font-size: 12px; color: {text_sub};")

        status_layout.addWidget(lbl_status_title)
        status_layout.addLayout(indicator_layout)
        status_layout.addWidget(lbl_status_desc)

        avatar_status_layout.addLayout(status_layout)
        avatar_status_layout.addStretch()
        
        main_layout.addLayout(avatar_status_layout)

        # 3. FORM FIELDS
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        input_style = f"""
            QLineEdit {{
                border: 1px solid {input_border}; border-radius: 8px;
                padding: 8px 12px; font-size: 14px;
                color: {text_main}; background-color: {input_bg};
            }}
            QLineEdit:focus {{ border: 1px solid #2D60FF; background-color: {input_focus_bg}; }}
            QLineEdit:read-only {{ color: {text_sub}; background-color: {input_readonly}; }}
        """

        def create_field(label_text, widget):
            layout = QVBoxLayout()
            layout.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {text_sub}; letter-spacing: 1px;")
            widget.setStyleSheet(input_style)
            widget.setFixedHeight(40)
            layout.addWidget(lbl)
            layout.addWidget(widget)
            return layout

        self.name_field = QLineEdit(user_info.get("name", ""))
        self.username_field = QLineEdit(user_info.get("username", ""))
        
        self.email_field = QLineEdit(user_info.get("email", ""))
        self.email_field.setReadOnly(True) 
        
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setPlaceholderText(tr("profile_password_ph"))

        grid_layout.addLayout(create_field(tr("profile_name"), self.name_field), 0, 0)
        grid_layout.addLayout(create_field(tr("profile_username"), self.username_field), 0, 1)
        grid_layout.addLayout(create_field(tr("profile_email"), self.email_field), 1, 0)
        grid_layout.addLayout(create_field(tr("profile_password"), self.password_field), 1, 1)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        # 4. BUTTONS
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        btn_cancel = QPushButton(tr("profile_cancel"))
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFixedSize(100, 40)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background-color: {btn_can_bg}; color: {btn_can_txt}; font-weight: bold; border: none; border-radius: 8px; }}
            QPushButton:hover {{ background-color: {btn_can_hvr}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton(tr("profile_save"))
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setFixedSize(120, 40)
        btn_save.setStyleSheet("""
            QPushButton { background-color: #2D60FF; color: white; font-weight: bold; border: none; border-radius: 8px; }
            QPushButton:hover { background-color: #1A4BDB; }
        """)
        btn_save.clicked.connect(self._on_save)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        main_layout.addLayout(btn_layout)

    def _on_save(self):
        name     = self.name_field.text().strip()
        username = self.username_field.text().strip()
        password = self.password_field.text()

        if not name:
            QMessageBox.warning(self, tr("error"), tr("profile_err_empty_name"))
            return
        if not username:
            QMessageBox.warning(self, tr("error"), tr("profile_err_empty_username"))
            return

        result = self.db.update_user_info(self.user_info["id"], name, username, password)

        if result == "username":
            QMessageBox.warning(self, tr("error"), tr("profile_err_exists_username"))
            return
        elif result is True:
            self.user_info["name"]     = name
            self.user_info["username"] = username
            self.accept()
        else:
            QMessageBox.critical(self, tr("error"), tr("profile_err_fail"))


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
        self.notifier = ScheduleNotifier(self.schedule_controller, self.user_info["id"], self.user_info.get("email"))

        self.setWindowTitle("EduFlow - Dashboard")
        self.resize(1300, 850)
        self.setMinimumSize(1000, 700)
        self.setMaximumWidth(1920)

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

        # USER INFO — bọc trong ClickableFrame để click mở ProfileDialog
        self.user_frame = ClickableFrame()
        self.user_frame.setObjectName("UserFrame")
        self.user_frame.setToolTip("Nhấn để chỉnh sửa profile")
        user_layout = QHBoxLayout(self.user_frame)
        user_layout.setContentsMargins(8, 8, 8, 8)
        user_layout.setSpacing(10)

        # Avatar — lấy chữ cái đầu của tên
        name_str = self.user_info.get("name") or "?"
        self.avatar_label = QLabel(name_str[0].upper())
        self.avatar_label.setFixedSize(40, 40)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet(
            "background:#2D60FF;color:white;border-radius:20px;"
            "font-size:16px;font-weight:bold;"
        )

        info = QVBoxLayout()
        info.setSpacing(1)

        self.lbl_name = QLabel(self.user_info.get("name", ""))
        self.lbl_name.setStyleSheet("font-weight:600;font-size:13px;")

        # Hiện username nếu có, fallback sang email
        username = self.user_info.get("username")
        sub_text = f"@{username}" if username else self.user_info.get("email", "")
        self.lbl_sub = QLabel(sub_text)
        self.lbl_sub.setStyleSheet("color:#6F767E;font-size:11px;")
        self.lbl_sub.setToolTip(self.user_info.get("email", ""))

        info.addWidget(self.lbl_name)
        info.addWidget(self.lbl_sub)

        user_layout.addWidget(self.avatar_label)
        user_layout.addLayout(info)

        # Kết nối click → mở ProfileDialog
        self.user_frame.clicked.connect(self._open_profile_dialog)

        layout.addWidget(self.user_frame)

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
        prog.setMinimumWidth(260)
        prog.setMaximumWidth(320)

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

        layout = self._sch_layout

        # Xóa widget cũ
        while layout.count() > 1:
            item = layout.takeAt(1)

            if item.widget():
                item.widget().deleteLater()

            elif item.spacerItem():
                spacer = item.spacerItem()
                layout.removeItem(spacer)

        today_col = datetime.now().weekday()

        all_schedules = self.db.get_schedule(
            self.user_info["id"]
        ) or []

        today_schedules = []

        for s in all_schedules:

            try:
                lesson_day = int(s.get("day"))
            except:
                continue

            if lesson_day == today_col:
                today_schedules.append(s)

        # sort theo giờ
        today_schedules.sort(
            key=lambda s: parse_time_to_minutes(
                s.get("start_time", 0)
            )
        )

        if not today_schedules:

            layout.addStretch()

            lbl = QLabel(tr("no_schedule"))
            lbl.setAlignment(Qt.AlignCenter)

            layout.addWidget(lbl)

            layout.addStretch()

            return

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

            course_name = s.get("course", "")

            lbl_course = QLabel(f"<b>{course_name}</b>")
            lbl_course.setObjectName("ScheduleItemTitle")

            # FIX parse time
            start_min = parse_time_to_minutes(
                s.get("start_time", 0)
            )

            end_min = parse_time_to_minutes(
                s.get("end_time", 0)
            )

            sh, sm = start_min // 60, start_min % 60
            eh, em = end_min // 60, end_min % 60

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
                spacer = item.spacerItem()
                layout.removeItem(spacer)

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

        if hasattr(self, "user_frame"):
            self.user_frame.setToolTip(tr("profile_tooltip"))

    # ================= PROFILE =================
    def _open_profile_dialog(self):
        # Truyền thêm self.current_theme vào
        dialog = ProfileDialog(self.user_info, self.db, self, self.current_theme)
        
        if dialog.exec() == QDialog.Accepted:
            # user_info đã được cập nhật bên trong dialog, chỉ cần refresh UI
            name     = self.user_info.get("name", "")
            username = self.user_info.get("username", "")

            # Cập nhật avatar (chữ cái đầu)
            self.avatar_label.setText((name[0].upper()) if name else "?")

            # Cập nhật label tên
            self.lbl_name.setText(name)

            # Cập nhật label username/email
            sub_text = f"@{username}" if username else self.user_info.get("email", "")
            self.lbl_sub.setText(sub_text)

            # Xử lý màu sắc cho Popup Thông báo Thành công
            is_dark = (self.current_theme == "dark")
            msg_bg = "#313244" if is_dark else "#FFFFFF"
            msg_txt = "#CDD6F4" if is_dark else "#111827"

            msg = QMessageBox(self)
            msg.setWindowTitle(tr("profile_success_title"))
            msg.setText(tr("profile_success_msg"))
            msg.setIcon(QMessageBox.Information)
            
            msg.setStyleSheet(f"""
                QMessageBox {{ background-color: {msg_bg}; }}
                QLabel {{ color: {msg_txt}; font-size: 14px; font-weight: bold; }}
                QPushButton {{ background-color: #2D60FF; color: white; border: none; font-weight: bold; border-radius: 5px; padding: 6px 15px; min-width: 60px; }}
                QPushButton:hover {{ background-color: #1A4BDB; }}
            """)
            msg.exec()
    # ================= LOGOUT =================
    def handle_logout(self):

        # stop notifier timer
        try:
            if hasattr(self, "notifier"):
                self.notifier.timer.stop()
        except:
            pass

        # stop refresh timer
        try:
            if hasattr(self, "_refresh_timer"):
                self._refresh_timer.stop()
        except:
            pass

        self.logout_signal.emit()
        self.deleteLater()