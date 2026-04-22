from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QProgressBar,
    QStackedLayout, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt

from src.ui.course_detail import CourseDetailWidget


# ================= COURSE CARD =================
class CourseCard(QFrame):
    def __init__(self, course, on_click):
        super().__init__()

        self.course = course
        self.on_click = on_click

        self.setObjectName("CardWhite")
        self.setFixedHeight(170)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)

        # TOP
        top = QHBoxLayout()

        icon = QLabel("📘")
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

        # TITLE
        title = QLabel(course["name"])
        title.setStyleSheet("font-size:16px;font-weight:bold;")

        info = QLabel(f"{course['code']} • {course['professor']}")
        info.setStyleSheet("color:#6F767E;font-size:12px;")

        # PROGRESS
        progress = course.get("progress", 0)

        prog_layout = QHBoxLayout()
        prog_layout.addWidget(QLabel("Tiến độ"))
        prog_layout.addStretch()
        prog_layout.addWidget(QLabel(f"{progress}%"))

        bar = QProgressBar()
        bar.setValue(progress)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)

        # ADD
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

        self.stack = QStackedLayout(self)

        self.page_list = QWidget()
        self.page_detail = CourseDetailWidget()  # ✅ FIX

        self.stack.addWidget(self.page_list)
        self.stack.addWidget(self.page_detail)

        self.setup_list_ui()

        # 👉 FIX BACK BUTTON
        self.page_detail.back_btn.clicked.connect(self.go_back)

    # ================= LIST =================
    def setup_list_ui(self):
        self.layout = QVBoxLayout(self.page_list)

        # HEADER
        header = QHBoxLayout()

        title_v = QVBoxLayout()
        title_v.addWidget(QLabel("Khóa học của tôi"))
        title_v.addWidget(QLabel("Quản lý danh sách các môn học."))

        btn_add = QPushButton("+ Thêm khóa học")
        btn_add.setObjectName("BtnAddSchedule")
        btn_add.clicked.connect(self.add_course)

        header.addLayout(title_v)
        header.addStretch()
        header.addWidget(btn_add)

        self.layout.addLayout(header)

        # GRID
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        self.layout.addStretch()

        self.load_courses()

    # ================= LOAD =================
    def load_courses(self):
        # clear
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.deleteLater()

        courses = self.controller.get_courses(self.user_id)

        if not courses:
            empty = QLabel("Chưa có khóa học nào 😢")
            empty.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(empty, 0, 0)
            return

        row = col = 0
        for course in courses:
            card = CourseCard(course, self.open_detail)
            self.grid.addWidget(card, row, col)

            col += 1
            if col == 3:
                col = 0
                row += 1

    # ================= ADD =================
    def add_course(self):
        name, ok1 = QInputDialog.getText(self, "Tên môn", "Nhập tên môn:")
        if not ok1 or not name:
            return

        code, ok2 = QInputDialog.getText(self, "Mã môn", "Nhập mã môn:")
        if not ok2:
            return

        prof, ok3 = QInputDialog.getText(self, "Giảng viên", "Nhập tên GV:")
        if not ok3:
            return

        success = self.controller.add_course(
            self.user_id, name, code, prof
        )

        if success:
            self.load_courses()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thêm được!")

    # ================= DETAIL =================
    def open_detail(self, course):
        self.page_detail.set_course(
            course["name"],
            course["code"],
            course["professor"],
            course.get("progress", 0)
        )
        self.stack.setCurrentWidget(self.page_detail)

    # ================= BACK =================
    def go_back(self):
        self.stack.setCurrentWidget(self.page_list)
        self.load_courses()