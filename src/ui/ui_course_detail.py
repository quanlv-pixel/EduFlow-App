from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar,
    QStackedLayout
)
from PySide6.QtCore import Qt


# ================= LESSON ITEM =================
class LessonItem(QFrame):
    def __init__(self, title, on_flashcard):
        super().__init__()

        self.setObjectName("CardWhite")
        layout = QHBoxLayout(self)

        name = QLabel(title)
        name.setStyleSheet("font-size:14px;")

        btn_view = QPushButton("Xem")
        btn_ex = QPushButton("Bài tập")

        btn_flash = QPushButton("⚡ Flashcard")
        btn_flash.setObjectName("BtnAddSchedule")
        btn_flash.clicked.connect(lambda: on_flashcard(title))

        layout.addWidget(name)
        layout.addStretch()
        layout.addWidget(btn_view)
        layout.addWidget(btn_ex)
        layout.addWidget(btn_flash)


# ================= MAIN =================
class CourseDetailWidget(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # ===== BACK =====
        back_btn = QPushButton("← Quay lại")
        back_btn.setFixedWidth(120)
        main_layout.addWidget(back_btn)

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

        self.page_lessons = self.create_lessons_page()
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

    # ================= LESSON PAGE =================
    def create_lessons_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)

        lessons = [
            "Bài 1: Giới thiệu",
            "Bài 2: Kiến thức cơ bản",
            "Bài 3: Thực hành"
        ]

        for l in lessons:
            item = LessonItem(l, self.handle_flashcard)
            layout.addWidget(item)

        layout.addStretch()
        return page

    # ================= DOC PAGE =================
    def create_docs_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        lbl = QLabel("📄 Tài liệu khóa học (PDF, DOCX...)")
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

        btn_manual = QPushButton("Tạo thủ công")
        btn_ai = QPushButton("Tạo bằng AI")

        btn_ai.setObjectName("BtnAddSchedule")

        layout.addWidget(btn_manual)
        layout.addWidget(btn_ai)
        layout.addStretch()

        return page

    # ================= DATA =================
    def set_course(self, name, code, prof, progress):
        self.lbl_title.setText(name)
        self.lbl_info.setText(f"{code} • {prof}")
        self.lbl_progress.setText(f"Tiến độ: {progress}%")
        self.bar.setValue(progress)

    # ================= ACTION =================
    def handle_flashcard(self, lesson_name):
        print(f"Tạo flashcard cho: {lesson_name}")