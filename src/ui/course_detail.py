from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar,
    QStackedLayout, QMessageBox
)
from PySide6.QtCore import Qt


# ================= LESSON ITEM =================
class LessonItem(QFrame):
    def __init__(self, lesson, on_flashcard):
        super().__init__()

        self.setObjectName("CardWhite")
        layout = QHBoxLayout(self)

        self.lesson = lesson

        name = QLabel(lesson["title"])
        name.setStyleSheet("font-size:14px;")

        btn_view = QPushButton("Xem")
        btn_ex = QPushButton("Bài tập")

        btn_flash = QPushButton("⚡ Flashcard")
        btn_flash.setObjectName("BtnAddSchedule")
        btn_flash.clicked.connect(lambda: on_flashcard(self.lesson))

        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(btn_view)
        layout.addWidget(btn_ex)
        layout.addWidget(btn_flash)


# ================= MAIN =================
class CourseDetailWidget(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.course_id = None

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # ===== BACK =====
        self.back_btn = QPushButton("← Quay lại")
        self.back_btn.setFixedWidth(120)
        main_layout.addWidget(self.back_btn)

        # ===== TITLE =====
        self.lbl_title = QLabel("Tên khóa học")
        self.lbl_title.setStyleSheet("font-size:26px;font-weight:bold;")

        self.lbl_info = QLabel("Mã môn • Giảng viên")
        self.lbl_info.setStyleSheet("color:#6F767E;")

        main_layout.addWidget(self.lbl_title)
        main_layout.addWidget(self.lbl_info)

        # ===== PROGRESS =====
        prog_card = QFrame()
        prog_card.setObjectName("CardWhite")

        v = QVBoxLayout(prog_card)

        self.lbl_progress = QLabel("Tiến độ: 0%")
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)

        v.addWidget(self.lbl_progress)
        v.addWidget(self.bar)

        main_layout.addWidget(prog_card)

        # ===== TABS =====
        tab_layout = QHBoxLayout()

        self.btn_lessons = QPushButton("Bài học")
        self.btn_docs = QPushButton("Tài liệu")
        self.btn_flash = QPushButton("Flashcards")

        for b in [self.btn_lessons, self.btn_docs, self.btn_flash]:
            b.setCheckable(True)

        self.btn_lessons.setChecked(True)

        tab_layout.addWidget(self.btn_lessons)
        tab_layout.addWidget(self.btn_docs)
        tab_layout.addWidget(self.btn_flash)
        tab_layout.addStretch()

        main_layout.addLayout(tab_layout)

        # ===== STACK =====
        self.stack = QStackedLayout()

        self.page_lessons = QWidget()
        self.layout_lessons = QVBoxLayout(self.page_lessons)

        self.page_docs = self.create_docs_page()
        self.page_flash = self.create_flash_page()

        self.stack.addWidget(self.page_lessons)
        self.stack.addWidget(self.page_docs)
        self.stack.addWidget(self.page_flash)

        main_layout.addLayout(self.stack)

        # ===== EVENTS =====
        self.btn_lessons.clicked.connect(lambda: self.switch_tab(0))
        self.btn_docs.clicked.connect(lambda: self.switch_tab(1))
        self.btn_flash.clicked.connect(lambda: self.switch_tab(2))

    # ================= SWITCH TAB =================
    def switch_tab(self, index):
        self.btn_lessons.setChecked(index == 0)
        self.btn_docs.setChecked(index == 1)
        self.btn_flash.setChecked(index == 2)

        self.stack.setCurrentIndex(index)

    # ================= LOAD DATA =================
    def load_course(self, course):
        """
        course = {
            id, name, code, professor, progress
        }
        """
        self.course_id = course["id"]

        self.lbl_title.setText(course["name"])
        self.lbl_info.setText(f"{course['code']} • {course['professor']}")
        self.lbl_progress.setText(f"Tiến độ: {course['progress']}%")
        self.bar.setValue(course["progress"])

        # Load lessons từ controller
        self.load_lessons()

    def load_lessons(self):
        # clear layout cũ
        for i in reversed(range(self.layout_lessons.count())):
            widget = self.layout_lessons.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        lessons = self.controller.get_lessons(self.course_id)

        for l in lessons:
            item = LessonItem(l, self.handle_flashcard)
            self.layout_lessons.addWidget(item)

        self.layout_lessons.addStretch()

    # ================= DOC PAGE =================
    def create_docs_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        lbl = QLabel("📄 Tài liệu khóa học")
        layout.addWidget(lbl)

        btn = QPushButton("+ Thêm tài liệu")
        btn.setObjectName("BtnAddSchedule")

        layout.addWidget(btn)
        layout.addStretch()

        return page

    # ================= FLASH PAGE =================
    def create_flash_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        lbl = QLabel("⚡ Flashcards của khóa học")
        layout.addWidget(lbl)

        self.btn_ai = QPushButton("Tạo bằng AI")
        self.btn_ai.setObjectName("BtnAddSchedule")
        self.btn_ai.clicked.connect(self.generate_flashcards_ai)

        layout.addWidget(self.btn_ai)
        layout.addStretch()

        return page

    # ================= ACTION =================
    def handle_flashcard(self, lesson):
        """Tạo flashcard cho 1 bài"""
        try:
            cards = self.controller.generate_flashcard_for_lesson(lesson)

            QMessageBox.information(
                self,
                "Flashcard",
                f"Đã tạo {len(cards)} flashcard!"
            )

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    def generate_flashcards_ai(self):
        """Tạo flashcard cho toàn bộ course"""
        try:
            cards = self.controller.generate_flashcard_for_course(self.course_id)

            QMessageBox.information(
                self,
                "AI Flashcard",
                f"Đã tạo {len(cards)} flashcard từ toàn bộ khóa học!"
            )

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))