from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QProgressBar,
    QStackedLayout
)
from PySide6.QtCore import Qt

from src.ui.course_detail import CourseDetailWidget


# ================= COURSE CARD =================
class CourseCard(QFrame):
    def __init__(self, course, on_click):
        super().__init__()

        self.setObjectName("CardWhite")
        self.setFixedHeight(170)
        self.setCursor(Qt.PointingHandCursor)

        self.course = course
        self.on_click = on_click

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Top
        top = QHBoxLayout()

        icon = QLabel("📘")
        icon.setStyleSheet("font-size: 22px;")

        status = QLabel("Đang học")
        status.setStyleSheet("""
            background: #E8FFF3;
            color: #10B981;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 11px;
        """)

        top.addWidget(icon)
        top.addStretch()
        top.addWidget(status)

        # Title
        title = QLabel(course["name"])
        title.setStyleSheet("font-size:16px;font-weight:bold;")

        info = QLabel(f"{course['code']} • {course['professor']}")
        info.setStyleSheet("color:#6F767E;font-size:12px;")

        # Progress
        prog_layout = QHBoxLayout()
        prog_label = QLabel("Tiến độ")
        percent = QLabel(f"{course.get('progress', 0)}%")

        prog_layout.addWidget(prog_label)
        prog_layout.addStretch()
        prog_layout.addWidget(percent)

        bar = QProgressBar()
        bar.setValue(course.get("progress", 0))
        bar.setTextVisible(False)
        bar.setFixedHeight(6)

        layout.addLayout(top)
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
        layout.addLayout(prog_layout)
        layout.addWidget(bar)

    def mousePressEvent(self, event):
        self.on_click(self.course)


# ================= MAIN =================
class CoursesWidget(QWidget):
    def __init__(self, controller, user_id):
        super().__init__()

        self.controller = controller
        self.user_id = user_id

        # STACK (List + Detail)
        self.stack = QStackedLayout(self)

        self.page_list = QWidget()
        self.page_detail = CourseDetailWidget(controller)

        self.stack.addWidget(self.page_list)
        self.stack.addWidget(self.page_detail)

        self.setup_list_ui()

        # Back button
        self.page_detail.back_btn.clicked.connect(self.go_back)

    # ================= LIST PAGE =================
    def setup_list_ui(self):
        self.layout = QVBoxLayout(self.page_list)
        self.layout.setSpacing(20)

        # Header
        header = QHBoxLayout()

        title_v = QVBoxLayout()

        title = QLabel("Khóa học của tôi")
        title.setStyleSheet("font-size:26px;font-weight:bold;")

        subtitle = QLabel("Quản lý danh sách các môn học.")
        subtitle.setStyleSheet("color:#6F767E;")

        title_v.addWidget(title)
        title_v.addWidget(subtitle)

        btn_add = QPushButton("+ Thêm khóa học")
        btn_add.setObjectName("BtnAddSchedule")
        btn_add.setFixedHeight(40)
        btn_add.clicked.connect(self.add_course)

        header.addLayout(title_v)
        header.addStretch()
        header.addWidget(btn_add)

        self.layout.addLayout(header)

        # Grid
        self.grid = QGridLayout()
        self.grid.setSpacing(20)

        self.layout.addLayout(self.grid)
        self.layout.addStretch()

        # Load data
        self.load_courses()

    # ================= LOAD COURSES =================
    def load_courses(self):
        # clear grid
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        courses = self.controller.get_courses(self.user_id)

        row, col = 0, 0
        for course in courses:
            card = CourseCard(course, self.open_detail)
            self.grid.addWidget(card, row, col)

            col += 1
            if col == 3:
                col = 0
                row += 1

    # ================= ADD COURSE =================
    def add_course(self):
        # demo nhanh
        self.controller.add_course(
            self.user_id,
            "Môn mới",
            "NEW101",
            "Giảng viên"
        )
        self.load_courses()

    # ================= OPEN DETAIL =================
    def open_detail(self, course):
        self.page_detail.load_course(course)
        self.stack.setCurrentWidget(self.page_detail)

    # ================= BACK =================
    def go_back(self):
        self.stack.setCurrentWidget(self.page_list)
        self.load_courses()