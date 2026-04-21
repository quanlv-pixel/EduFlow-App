from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QProgressBar,
    QStackedLayout
)
from PySide6.QtCore import Qt

from src.ui.ui_course_detail import CourseDetailWidget
from src.ui.ui_add_course import AddCourseDialog

# ================= COURSE CARD =================
class CourseCard(QFrame):
    def __init__(self, name, code, professor, progress, on_click):
        super().__init__()

        self.setObjectName("CardWhite")
        self.setFixedHeight(170)
        self.setCursor(Qt.PointingHandCursor)

        self.name = name
        self.code = code
        self.professor = professor
        self.progress = progress
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
        title = QLabel(name)
        title.setStyleSheet("font-size:16px;font-weight:bold;")

        info = QLabel(f"{code} • {professor}")
        info.setStyleSheet("color:#6F767E;font-size:12px;")

        # Progress
        prog_layout = QHBoxLayout()
        prog_label = QLabel("Tiến độ")
        percent = QLabel(f"{progress}%")

        prog_layout.addWidget(prog_label)
        prog_layout.addStretch()
        prog_layout.addWidget(percent)

        bar = QProgressBar()
        bar.setValue(progress)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)

        layout.addLayout(top)
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
        layout.addLayout(prog_layout)
        layout.addWidget(bar)

    def mousePressEvent(self, event):
        self.on_click(self.name, self.code, self.professor, self.progress)


# ================= MAIN =================
class CoursesWidget(QWidget):
    def __init__(self):
        super().__init__()

        # STACK (List + Detail)
        self.stack = QStackedLayout(self)

        self.page_list = QWidget()
        self.page_detail = CourseDetailWidget()

        self.stack.addWidget(self.page_list)
        self.stack.addWidget(self.page_detail)

        self.setup_list_ui()

        # Kết nối nút back từ detail
        self.page_detail.findChild(QPushButton).clicked.connect(self.go_back)

    # ================= LIST PAGE =================
    def setup_list_ui(self):
        layout = QVBoxLayout(self.page_list)
        layout.setSpacing(20)


        # Header
        header = QHBoxLayout()

        title_v = QVBoxLayout()

        title = QLabel("Khóa học của tôi")
        title.setStyleSheet("font-size:26px;font-weight:bold;")

        subtitle = QLabel("Quản lý danh sách các môn học trong học kỳ này.")
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

        layout.addLayout(header)

        # Grid courses
        self.grid = QGridLayout()
        self.grid.setSpacing(20)

        courses = [
            ("Cơ sở dữ liệu", "DB202", "Prof. Johnson", 40),
            ("Python", "PY101", "Dr. Smith", 65),
            ("AI", "AI303", "Dr. Lee", 85),
        ]

        row, col = 0, 0
        for course in courses:
            card = CourseCard(*course, self.open_detail)
            self.grid.addWidget(card, row, col)

            col += 1
            if col == 3:
                col = 0
                row += 1

        layout.addLayout(self.grid)
        layout.addStretch()

    # ================= ADD COURSE =================
    def add_course(self):
        dialog = AddCourseDialog()

        if dialog.exec():
            name, code, prof, prog = dialog.get_data()

            card = CourseCard(name, code, prof, prog, self.open_detail)

            count = self.grid.count()
            row = count // 3
            col = count % 3

            self.grid.addWidget(card, row, col)

    # ================= OPEN DETAIL =================
    def open_detail(self, name, code, professor, progress):
        self.page_detail.set_course(name, code, professor, progress)
        self.stack.setCurrentWidget(self.page_detail)

    # ================= BACK =================
    def go_back(self):
        self.stack.setCurrentWidget(self.page_list)