from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QProgressBar,
    QStackedLayout, QInputDialog, QMessageBox,
    QLineEdit, QScrollArea, QSizePolicy,
    QDialog, QButtonGroup, QRadioButton, QApplication
)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette, QIcon
from src.ui.settings_widget import LanguageManager, tr

from src.ui.course_detail import CourseDetailWidget


# ================= SEARCH WORKER (QThread) =================
# Dùng QThread để tránh freeze UI khi gọi API search
class SearchWorker(QThread):
    finished = Signal(list)   # trả về list kết quả
    error = Signal(str)

    def __init__(self, controller, query: str):
        super().__init__()
        self.controller = controller
        self.query = query

    def run(self):
        try:
            results = self.controller.search_online_courses(self.query)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


# ================= COURSE SELECTION DIALOG =================
class CourseSelectDialog(QDialog):
    """
    Dialog 2 bước:
    Bước 1: Nhập thông tin môn học + bắt đầu tìm kiếm
    Bước 2: Hiện danh sách course tìm được → user chọn 1
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Thêm khóa học")
        self.setFixedWidth(560)
        self.setMinimumHeight(300)
        self.setStyleSheet("background: #FFFFFF;")

        self._results = []
        self._selected = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(32, 28, 32, 28)
        self.main_layout.setSpacing(16)

        self._build_step1()

    # ── STEP 1: Nhập thông tin ──────────────────────
    def _build_step1(self):
        self._clear_layout()

        title = QLabel("📚 Thêm khóa học mới")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E2328;")
        self.main_layout.addWidget(title)

        subtitle = QLabel("Nhập thông tin môn học. Hệ thống sẽ tự tìm tài liệu phù hợp.")
        subtitle.setStyleSheet("font-size: 13px; color: #6F767E;")
        subtitle.setWordWrap(True)
        self.main_layout.addWidget(subtitle)

        self.main_layout.addSpacing(4)

        # Inputs
        self.inp_name = self._make_input("Tên môn học *", "Ví dụ: Machine Learning, Python...")
        self.inp_code = self._make_input("Mã môn (tuỳ chọn)", "Ví dụ: CS101")
        self.inp_prof = self._make_input("Giảng viên (tuỳ chọn)", "Ví dụ: Nguyễn Văn A")

        # Nút tìm kiếm
        self.btn_search = QPushButton("🔍  Tìm khóa học")
        self.btn_search.setCursor(Qt.PointingHandCursor)
        self.btn_search.setFixedHeight(44)
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #2D60FF;
                color: white;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #1A4FE0; }
            QPushButton:disabled { background-color: #B0C4FF; }
        """)
        self.btn_search.clicked.connect(self._start_search)
        self.main_layout.addWidget(self.btn_search)

        # Nút huỷ
        btn_cancel = QPushButton("Huỷ")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6F767E;
                border: 1px solid #EDEDED;
                border-radius: 10px;
                font-size: 13px;
            }
            QPushButton:hover { background: #F9FAFB; }
        """)
        btn_cancel.clicked.connect(self.reject)
        self.main_layout.addWidget(btn_cancel)

        self.adjustSize()

    def _make_input(self, label: str, placeholder: str) -> QLineEdit:
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #374151;")
        self.main_layout.addWidget(lbl)

        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(40)
        inp.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                color: #1E2328;
                background: #F9FAFB;
            }
            QLineEdit:focus {
                border: 1.5px solid #2D60FF;
                background: #FFFFFF;
            }
        """)
        self.main_layout.addWidget(inp)
        return inp

    # ── BẮT ĐẦU TÌM KIẾM ──────────────────────────
    def _start_search(self):
        name = self.inp_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập tên môn học!")
            return

        # Lưu tạm để dùng ở step 2
        self._name = name
        self._code = self.inp_code.text().strip()
        self._prof = self.inp_prof.text().strip()

        # Hiện trạng thái loading
        self.btn_search.setEnabled(False)
        self.btn_search.setText("⏳  Đang tìm kiếm...")

        self._worker = SearchWorker(self.controller, name)
        self._worker.finished.connect(self._on_search_done)
        self._worker.error.connect(self._on_search_error)
        self._worker.start()

    def _on_search_done(self, results: list):
        self._results = results
        self._build_step2(results)

    def _on_search_error(self, msg: str):
        self.btn_search.setEnabled(True)
        self.btn_search.setText("🔍  Tìm khóa học")
        QMessageBox.warning(self, "Lỗi tìm kiếm", f"Không thể tìm kiếm:\n{msg}")

    # ── STEP 2: Chọn course ────────────────────────
    def _build_step2(self, results: list):
        self._clear_layout()
        self.setMinimumHeight(400)

        title = QLabel(f"📋 Chọn khóa học cho: {self._name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E2328;")
        title.setWordWrap(True)
        self.main_layout.addWidget(title)

        subtitle = QLabel("Chọn 1 khóa học phù hợp. Hệ thống sẽ tự tạo bài giảng.")
        subtitle.setStyleSheet("font-size: 13px; color: #6F767E;")
        self.main_layout.addWidget(subtitle)

        self.main_layout.addSpacing(4)

        if not results:
            info = QLabel("⚠️ Không tìm thấy khóa học nào. Sẽ tạo môn học trống.")
            info.setStyleSheet("""
                background: #FFF7ED;
                color: #D97706;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            """)
            info.setWordWrap(True)
            self.main_layout.addWidget(info)
            self._selected = None
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setMaximumHeight(280)
            scroll.setStyleSheet("background: transparent; border: none;")

            container = QWidget()
            container.setStyleSheet("background: transparent;")
            list_layout = QVBoxLayout(container)
            list_layout.setContentsMargins(0, 0, 0, 0)
            list_layout.setSpacing(8)

            self._btn_group = QButtonGroup(self)
            self._radio_map = {}   

            for i, r in enumerate(results):
                frame, rb = self._make_result_radio(r, i)
                self._btn_group.addButton(rb, i)
                list_layout.addWidget(frame)
                self._radio_map[rb] = r

            first = self._btn_group.button(0)
            if first:
                first.setChecked(True)
                self._selected = results[0]

            self._btn_group.buttonClicked.connect(
                lambda btn: self._radio_map.__setitem__("_cur", self._radio_map[btn])
                or setattr(self, "_selected", self._radio_map[btn])
            )

            list_layout.addStretch()
            scroll.setWidget(container)
            self.main_layout.addWidget(scroll)

        # Buttons row
        btn_row = QHBoxLayout()

        btn_back = QPushButton("← Quay lại")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setFixedHeight(42)
        btn_back.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6F767E;
                border: 1px solid #EDEDED;
                border-radius: 10px;
                font-size: 13px;
            }
            QPushButton:hover { background: #F9FAFB; }
        """)
        btn_back.clicked.connect(self._build_step1)

        btn_confirm = QPushButton("✅  Tạo khóa học")
        btn_confirm.setCursor(Qt.PointingHandCursor)
        btn_confirm.setFixedHeight(42)
        btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #2D60FF;
                color: white;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #1A4FE0; }
        """)
        btn_confirm.clicked.connect(self.accept)

        btn_row.addWidget(btn_back)
        btn_row.addWidget(btn_confirm)
        self.main_layout.addLayout(btn_row)

        self.adjustSize()

    def _make_result_radio(self, result: dict, index: int) -> QWidget:

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #F9FAFB;
                border-radius: 10px;
                border: 1px solid #E5E7EB;
            }
            QFrame:hover {
                border: 1.5px solid #2D60FF;
                background: #EEF2FF;
            }
        """)

        h = QHBoxLayout(frame)
        h.setContentsMargins(14, 10, 14, 10)
        h.setSpacing(10)

        rb = QRadioButton()
        rb.setStyleSheet("QRadioButton { background: transparent; }")

        v = QVBoxLayout()
        v.setSpacing(2)

        lbl_title = QLabel(result.get("title", f"Khóa học {index + 1}"))
        lbl_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #1E2328; background: transparent;")
        lbl_title.setWordWrap(True)

        link = result.get("link", "")
        source = self._detect_source(link)
        score = result.get("score", 0)

        lbl_meta = QLabel(f"🌐 {source}  •  Điểm phù hợp: {score}")
        lbl_meta.setStyleSheet("font-size: 11px; color: #6F767E; background: transparent;")

        v.addWidget(lbl_title)
        v.addWidget(lbl_meta)

        h.addWidget(rb)
        h.addLayout(v, stretch=1)

        frame.mousePressEvent = lambda _: rb.setChecked(True) or setattr(self, "_selected", result)

        rb._result = result
        rb._frame = frame
        return frame, rb

    def _detect_source(self, link: str) -> str:
        link = link.lower()
        for name in ["coursera", "youtube", "w3schools", "udemy", "freecodecamp", "edx"]:
            if name in link:
                return name.capitalize()
        return "Online"

    def _clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    child = item.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

    # ── Getters ──────────────────────────────────
    def get_name(self): return getattr(self, "_name", "")
    def get_code(self): return getattr(self, "_code", "")
    def get_prof(self): return getattr(self, "_prof", "")
    def get_selected(self): return getattr(self, "_selected", None)


# ================= COURSE CARD =================
class CourseCard(QFrame):
    def __init__(self, course, on_click, on_delete=None):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self.update)

        self.course = course
        self.on_click = on_click
        self.on_delete = on_delete

        self.setFixedHeight(190)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._apply_style(hover=False)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        # TOP ROW
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        icon = QLabel("📘")
        icon.setStyleSheet("font-size: 22px; background: transparent;")

        progress = course.get("progress", 0)
        if progress == 100:
            status_text = "✅ Hoàn thành"
            status_style = "background: #ECFDF5; color: #10B981;"
        else:
            status_text = course.get("status", tr("course_status_learning"))
            status_style = "background: #EEF2FF; color: #2D60FF;"

        status = QLabel(status_text)
        status.setStyleSheet(f"""
            {status_style}
            padding: 3px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        """)

        
        btn_del = QPushButton("✕")
        btn_del.setFixedSize(26, 26)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setToolTip("Xóa khóa học")
        btn_del.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #CBD5E1;
                border: none;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #FEE2E2;
                color: #EF4444;
            }
        """)
        
        btn_del.clicked.connect(self._on_delete_clicked)

        top.addWidget(icon)
        top.addStretch()
        top.addWidget(status)
        top.addSpacing(6)
        top.addWidget(btn_del)

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
        info.setStyleSheet("color: #6F767E; font-size: 12px; background: transparent;")

        # PROGRESS
        prog_row = QHBoxLayout()
        prog_row.setContentsMargins(0, 0, 0, 0)

        lbl_progress = QLabel(tr("progress"))
        lbl_progress.setStyleSheet("color: #6F767E; font-size: 12px; background: transparent;")

        lbl_pct = QLabel(f"{progress}%")
        lbl_pct.setStyleSheet(
            "color: #1E2328; font-size: 12px; font-weight: bold; background: transparent;"
        )

        prog_row.addWidget(lbl_progress)
        prog_row.addStretch()
        prog_row.addWidget(lbl_pct)

        bar = QProgressBar()
        bar.setValue(progress)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        
        chunk_color = "#10B981" if progress == 100 else "#2D60FF"
        bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #EEF0F4;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {chunk_color};
                border-radius: 3px;
            }}
        """)

        layout.addLayout(top)
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()
        layout.addLayout(prog_row)
        layout.addWidget(bar)

    def _on_delete_clicked(self):
        if self.on_delete:
            self.on_delete(self.course)

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


# ================= MAIN COURSES WIDGET =================
class CoursesWidget(QWidget):
    def __init__(self, controller, user_id):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

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

        self._retranslate()

    # ================= LIST PAGE =================
    def setup_list_ui(self):
        outer = QVBoxLayout(self.page_list)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # HEADER
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 24)

        title_v = QVBoxLayout()
        title_v.setSpacing(4)

        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #1E2328;
            background: transparent;
        """)

        self.lbl_sub = QLabel()
        self.lbl_sub.setStyleSheet("font-size: 13px; color: #6F767E; background: transparent;")

        title_v.addWidget(self.lbl_title)
        title_v.addWidget(self.lbl_sub)

        self.btn_add = QPushButton()
        self.btn_add.setObjectName("BtnAddSchedule")
        self.btn_add.setFixedHeight(42)
        self.btn_add.setMinimumWidth(160)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton#BtnAddSchedule {
                background-color: #2D60FF;
                color: white;
                border-radius: 10px;
                padding: 0px 20px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton#BtnAddSchedule:hover { background-color: #1A4FE0; }
        """)
        self.btn_add.clicked.connect(self.add_course)

        header_layout.addLayout(title_v)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)

        outer.addWidget(header_widget)

        # SCROLL AREA → GRID
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
            self.empty_label = QLabel()
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.empty_label.setStyleSheet(
                "color: #6F767E; font-size: 15px; background: transparent;"
            )
            self.grid.addWidget(self.empty_label, 0, 0, 1, 3)
            return

        row = col = 0
        for course in courses:
            card = CourseCard(course, self.open_detail, self.delete_course)
            self.grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

    # ================= DELETE =================
    def delete_course(self, course: dict):
        name = course.get("name", "khóa học này")
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa khóa học\n\"{name}\" không?\n\nHành động này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        course_id = course.get("id") or course.get("course_id")
        success = self.controller.delete_course(course_id)

        if success:
            self.load_courses()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể xóa khóa học. Vui lòng thử lại.")

    # ================= ADD (2 bước) =================
    def add_course(self):

        dlg = CourseSelectDialog(self.controller, self)
        if dlg.exec() != QDialog.Accepted:
            return

        name = dlg.get_name()
        code = dlg.get_code()
        prof = dlg.get_prof()
        selected = dlg.get_selected()   

        if not name:
            return

        # Bước A: Lưu course vào DB
        course_id = self.controller.add_course(self.user_id, name, code, prof)

        if not course_id:
            QMessageBox.warning(self, tr("error"), tr("error_add_course"))
            return

        # Bước B: Tạo lessons từ course được chọn (nếu có)
        if selected:
            self.controller.generate_lessons_from_course(course_id, selected)

        self.load_courses()

    # ================= DETAIL =================
    def open_detail(self, course):
        try:
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

    def _retranslate(self):
        self.lbl_title.setText(tr("course_title"))
        self.lbl_sub.setText(tr("course_subtitle"))
        self.btn_add.setText(tr("course_add"))

        if hasattr(self, "empty_label"):
            self.empty_label.setText(tr("course_empty"))

        self.load_courses()