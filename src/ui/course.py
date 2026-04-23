from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QProgressBar,
    QStackedLayout, QInputDialog, QMessageBox,
    QLineEdit, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

from src.ui.course_detail import CourseDetailWidget


# ================= COURSE CARD =================
class CourseCard(QFrame):
    def __init__(self, course, on_click):
        super().__init__()

        self.course = course
        self.on_click = on_click

        self.setFixedHeight(190)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Always show white card with border
        self.setStyleSheet("""
            CourseCard {
                background-color: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #EDEDED;
            }
        """)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        # TOP ROW: icon + status badge
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        icon = QLabel("📘")
        icon.setStyleSheet("font-size: 22px; background: transparent;")

        status_text = course.get("status", "Đang học")
        status = QLabel(status_text)
        status.setStyleSheet("""
            background: #ECFDF5;
            color: #10B981;
            padding: 3px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        """)

        top.addWidget(icon)
        top.addStretch()
        top.addWidget(status)

        # TITLE
        title = QLabel(course["name"])
        title.setStyleSheet("""
            font-size: 17px;
            font-weight: bold;
            color: #1E2328;
            background: transparent;
        """)
        title.setWordWrap(True)

        # INFO
        info = QLabel(f"{course['code']}  •  {course['professor']}")
        info.setStyleSheet("""
            color: #6F767E;
            font-size: 12px;
            background: transparent;
        """)

        # PROGRESS
        progress = course.get("progress", 0)

        prog_row = QHBoxLayout()
        prog_row.setContentsMargins(0, 0, 0, 0)

        lbl_progress = QLabel("Tiến độ")
        lbl_progress.setStyleSheet("color: #6F767E; font-size: 12px; background: transparent;")

        lbl_pct = QLabel(f"{progress}%")
        lbl_pct.setStyleSheet("color: #1E2328; font-size: 12px; font-weight: bold; background: transparent;")

        prog_row.addWidget(lbl_progress)
        prog_row.addStretch()
        prog_row.addWidget(lbl_pct)

        bar = QProgressBar()
        bar.setValue(progress)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #EEF0F4;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #2D60FF;
                border-radius: 3px;
            }
        """)

        layout.addLayout(top)
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
        layout.addLayout(prog_row)
        layout.addWidget(bar)

        # Apply initial style (white card always visible)
        self._apply_style(hover=False)

    def _apply_style(self, hover=False):
        border = "#2D60FF" if hover else "#EDEDED"
        width = "1.5px" if hover else "1px"
        self.setStyleSheet(f"""
            CourseCard {{
                background-color: #FFFFFF;
                border-radius: 20px;
                border: {width} solid {border};
            }}
        """)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_click(self.course)

    def enterEvent(self, event):
        self._apply_style(hover=True)

    def leaveEvent(self, event):
        self._apply_style(hover=False)


# ================= MAIN =================
class CoursesWidget(QWidget):
    def __init__(self, controller, user_id):
        super().__init__()

        self.controller = controller
        self.user_id = user_id

        self.stack = QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.page_list = QWidget()
        self.page_detail = CourseDetailWidget(self.controller)

        self.stack.addWidget(self.page_list)
        self.stack.addWidget(self.page_detail)

        self.setup_list_ui()

        self.page_detail.back_btn.clicked.connect(self.go_back)

    # ================= LIST PAGE =================
    def setup_list_ui(self):
        outer = QVBoxLayout(self.page_list)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── HEADER ──────────────────────────────
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 24)

        title_v = QVBoxLayout()
        title_v.setSpacing(4)

        lbl_title = QLabel("Khóa học của tôi")
        lbl_title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #1E2328;
            background: transparent;
        """)

        lbl_sub = QLabel("Quản lý danh sách các môn học trong học kỳ này.")
        lbl_sub.setStyleSheet("""
            font-size: 13px;
            color: #6F767E;
            background: transparent;
        """)

        title_v.addWidget(lbl_title)
        title_v.addWidget(lbl_sub)

        btn_add = QPushButton("  +  Thêm khóa học")
        btn_add.setObjectName("BtnAddSchedule")
        btn_add.setFixedHeight(42)
        btn_add.setMinimumWidth(160)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet("""
            QPushButton#BtnAddSchedule {
                background-color: #2D60FF;
                color: white;
                border-radius: 10px;
                padding: 0px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton#BtnAddSchedule:hover {
                background-color: #1A4FE0;
            }
        """)
        btn_add.clicked.connect(self.add_course)

        header_layout.addLayout(title_v)
        header_layout.addStretch()
        header_layout.addWidget(btn_add)

        outer.addWidget(header_widget)

        # ── SCROLL AREA → GRID ───────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")

        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.grid = QGridLayout()
        self.grid.setSpacing(18)
        self.grid.setContentsMargins(0, 0, 0, 0)

        self.content_layout.addLayout(self.grid)
        self.content_layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        self.load_courses()

    # ================= LOAD =================
    def load_courses(self):
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        courses = self.controller.get_courses(self.user_id)

        if not courses:
            empty = QLabel("Chưa có khóa học nào 😢")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #6F767E; font-size: 15px; background: transparent;")
            self.grid.addWidget(empty, 0, 0, 1, 3)
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
        name, ok1 = QInputDialog.getText(self, "Tên môn", "Nhập tên môn học:")
        if not ok1 or not name.strip():
            return

        code, ok2 = QInputDialog.getText(self, "Mã môn", "Nhập mã môn:")
        if not ok2:
            return

        prof, ok3 = QInputDialog.getText(self, "Giảng viên", "Nhập tên giảng viên:")
        if not ok3:
            return

        success = self.controller.add_course(self.user_id, name, code, prof)

        if success:
            self.load_courses()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thêm được khóa học!")

    # ================= DETAIL =================
    def open_detail(self, course):
        try:
            # Chuẩn hóa field "id" — hỗ trợ mọi tên field
            if "id" not in course or course["id"] is None:
                course["id"] = course.get("course_id") or course.get("_id")

            self.page_detail.load_course(course)
            self.stack.setCurrentWidget(self.page_detail)
        except Exception as e:
            print(f"[CoursesWidget] Lỗi open_detail: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể mở khóa học:\n{e}")

    # ================= BACK =================
    def go_back(self):
        self.stack.setCurrentWidget(self.page_list)
        self.load_courses()