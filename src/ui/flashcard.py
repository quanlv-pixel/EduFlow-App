from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit,
    QStackedLayout, QMessageBox,
    QScrollArea, QApplication
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
        self.lbl.setText(self.answer if not self.showing_answer else self.question)
        self.showing_answer = not self.showing_answer


# ================= MAIN =================
class FlashcardWidget(QWidget):
    def __init__(self, controller=None, user_id=None):
        super().__init__()

        self.controller = controller
        self.user_id = user_id

        self.stack = QStackedLayout(self)

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

        title = QLabel("⚡ Flashcards")
        title.setStyleSheet("font-size:26px;font-weight:bold;")

        btn_manual = QPushButton("➕ Tạo thủ công")
        btn_ai = QPushButton("🤖 Tạo bằng AI")
        btn_ai.setObjectName("BtnAddSchedule")

        btn_manual.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        btn_ai.clicked.connect(self.generate_ai_flashcards)

        layout.addWidget(title)
        layout.addWidget(btn_manual)
        layout.addWidget(btn_ai)
        layout.addStretch()

    # ================= CREATE =================
    def setup_create(self):
        layout = QVBoxLayout(self.page_create)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.input_q = QLineEdit()
        self.input_q.setPlaceholderText("Câu hỏi...")

        self.input_a = QLineEdit()
        self.input_a.setPlaceholderText("Câu trả lời...")

        btn_add = QPushButton("Lưu")
        btn_add.setObjectName("BtnAddSchedule")
        btn_add.clicked.connect(self.add_flashcard)

        layout.addWidget(back)
        layout.addWidget(self.input_q)
        layout.addWidget(self.input_a)
        layout.addWidget(btn_add)

    # ================= STUDY =================
    def setup_study(self):
        layout = QVBoxLayout(self.page_study)

        back = QPushButton("← Quay lại")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        # scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        self.container = QVBoxLayout(content)

        scroll.setWidget(content)

        layout.addWidget(back)
        layout.addWidget(scroll)

    # ================= ADD =================
    def add_flashcard(self):
        q = self.input_q.text().strip()
        a = self.input_a.text().strip()

        if not q or not a:
            QMessageBox.warning(self, "Lỗi", "Nhập đầy đủ!")
            return

        try:
            if self.controller:
                self.controller.add_flashcard(self.user_id, q, a)

            self.input_q.clear()
            self.input_a.clear()

            self.render_flashcards()
            self.stack.setCurrentIndex(2)

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    # ================= LOAD =================
    def render_flashcards(self):
        # clear
        for i in reversed(range(self.container.count())):
            widget = self.container.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not self.controller:
            return

        try:
            data = self.controller.get_flashcards(self.user_id)

            for item in data:
                card = FlashcardItem(item["question"], item["answer"])
                self.container.addWidget(card)

        except Exception as e:
            QMessageBox.warning(self, "Lỗi load", str(e))

    # ================= AI =================
    def generate_ai_flashcards(self):
        if not self.controller:
            return

        self.stack.setCurrentIndex(2)

        # loading UI
        self.clear_container()
        self.container.addWidget(QLabel("🤖 Đang tạo flashcard bằng AI..."))
        QApplication.processEvents()

        try:
            cards = self.controller.generate_ai(self.user_id)

            # limit tránh overload UI
            cards = cards[:10]

            for c in cards:
                self.controller.add_flashcard(self.user_id, c["q"], c["a"])

            self.render_flashcards()

        except Exception as e:
            QMessageBox.warning(self, "Lỗi AI", str(e))

    # ================= HELPER =================
    def clear_container(self):
        for i in reversed(range(self.container.count())):
            widget = self.container.itemAt(i).widget()
            if widget:
                widget.deleteLater()