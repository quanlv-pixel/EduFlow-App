from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QTextEdit,
    QStackedLayout
)
from PySide6.QtCore import Qt


# ================= FLASHCARD ITEM =================
class FlashcardItem(QFrame):
    def __init__(self, question, answer):
        super().__init__()

        self.setObjectName("CardWhite")
        self.question = question
        self.answer = answer
        self.showing_answer = False

        layout = QVBoxLayout(self)

        self.lbl = QLabel(question)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setStyleSheet("font-size:16px; padding:20px;")

        btn = QPushButton("Lật thẻ")
        btn.clicked.connect(self.flip)

        layout.addWidget(self.lbl)
        layout.addWidget(btn)

    def flip(self):
        if self.showing_answer:
            self.lbl.setText(self.question)
        else:
            self.lbl.setText(self.answer)

        self.showing_answer = not self.showing_answer


# ================= MAIN =================
class FlashcardWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.stack = QStackedLayout(self)

        # 3 page
        self.page_main = QWidget()
        self.page_create = QWidget()
        self.page_study = QWidget()

        self.stack.addWidget(self.page_main)
        self.stack.addWidget(self.page_create)
        self.stack.addWidget(self.page_study)

        self.setup_main()
        self.setup_create()
        self.setup_study()

    # ================= MAIN =================
    def setup_main(self):
        layout = QVBoxLayout(self.page_main)
        layout.setSpacing(20)

        title = QLabel("⚡ Flashcards")
        title.setStyleSheet("font-size:26px;font-weight:bold;")

        subtitle = QLabel("Tạo và học flashcard nhanh chóng.")
        subtitle.setStyleSheet("color:#6F767E;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Buttons
        btn_manual = QPushButton("➕ Tạo flashcard thủ công")
        btn_ai = QPushButton("🤖 Tạo flashcard bằng AI")

        btn_ai.setObjectName("BtnAddSchedule")

        btn_manual.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_ai.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(btn_manual)
        layout.addWidget(btn_ai)

        layout.addStretch()

    # ================= CREATE =================
    def setup_create(self):
        layout = QVBoxLayout(self.page_create)
        layout.setSpacing(15)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        title = QLabel("Tạo Flashcard")
        title.setStyleSheet("font-size:22px;font-weight:bold;")

        self.input_q = QLineEdit()
        self.input_q.setPlaceholderText("Nhập câu hỏi...")

        self.input_a = QLineEdit()
        self.input_a.setPlaceholderText("Nhập câu trả lời...")

        btn_add = QPushButton("Lưu flashcard")
        btn_add.setObjectName("BtnAddSchedule")

        btn_add.clicked.connect(self.add_flashcard)

        layout.addWidget(back)
        layout.addWidget(title)
        layout.addWidget(self.input_q)
        layout.addWidget(self.input_a)
        layout.addWidget(btn_add)

        layout.addStretch()

    # ================= STUDY =================
    def setup_study(self):
        layout = QVBoxLayout(self.page_study)
        layout.setSpacing(20)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        title = QLabel("Học Flashcard")
        title.setStyleSheet("font-size:22px;font-weight:bold;")

        self.card_container = QVBoxLayout()

        layout.addWidget(back)
        layout.addWidget(title)
        layout.addLayout(self.card_container)
        layout.addStretch()

    # ================= LOGIC =================
    def add_flashcard(self):
        q = self.input_q.text()
        a = self.input_a.text()

        if not q or not a:
            return

        card = FlashcardItem(q, a)
        self.card_container.addWidget(card)

        self.input_q.clear()
        self.input_a.clear()

        # chuyển sang học
        self.stack.setCurrentIndex(2)