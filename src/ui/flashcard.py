from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os


# ================= FLASHCARD ITEM =================
class FlashcardItem(QFrame):
    def __init__(self, question, answer):
        super().__init__()

        self.setObjectName("Flashcard")
        self.setMinimumHeight(140)

        self.q = question
        self.a = answer
        self.is_answer = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel(question)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)

        self.btn = QPushButton("👁 Xem đáp án")
        self.btn.setObjectName("BtnSecondary")
        self.btn.clicked.connect(self.flip)

        layout.addStretch()
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.btn)

    def flip(self):
        self.is_answer = not self.is_answer
        self.label.setText(self.a if self.is_answer else self.q)
        self.btn.setText("↩️ Quay lại" if self.is_answer else "👁 Xem đáp án")


# ================= MAIN =================
class FlashcardWidget(QWidget):
    def __init__(self, controller, user_id):
        super().__init__()

        self.controller = controller
        self.user_id = user_id

        self.stack = QStackedLayout(self)

        self.page_home = QWidget()
        self.page_study = QWidget()

        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_study)

        self.setup_home()
        self.setup_study()

    # ================= HOME =================
    def setup_home(self):
        layout = QVBoxLayout(self.page_home)
        layout.setSpacing(20)

        title = QLabel("📚 Flashcards AI")
        title.setStyleSheet("font-size:26px;font-weight:bold;")

        subtitle = QLabel("Tạo flashcard từ tài liệu hoặc nội dung")
        subtitle.setStyleSheet("color:#6F767E;")

        card = QFrame()
        card.setObjectName("CardWhite")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        # ===== BUTTONS =====
        btn_file = QPushButton("📂 Tạo từ tài liệu")
        btn_file.setObjectName("BtnAddSchedule")
        btn_file.setFixedHeight(45)
        btn_file.clicked.connect(self.generate_from_file)

        btn_text = QPushButton("💬 Tạo từ nội dung")
        btn_text.setObjectName("BtnSecondary")
        btn_text.setFixedHeight(45)
        btn_text.clicked.connect(self.generate_from_text)

        btn_view = QPushButton("📖 Xem flashcards")
        btn_view.clicked.connect(self.open_study)

        card_layout.addWidget(btn_file)
        card_layout.addWidget(btn_text)
        card_layout.addWidget(btn_view)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(card)
        layout.addStretch()

    # ================= STUDY =================
    def setup_study(self):
        layout = QVBoxLayout(self.page_study)

        back = QPushButton("← Quay lại")
        back.setObjectName("BtnSecondary")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        self.container = QVBoxLayout(content)
        self.container.setSpacing(15)

        scroll.setWidget(content)

        layout.addWidget(back)
        layout.addWidget(scroll)

    # ================= LOAD =================
    def render_flashcards(self):
        self.clear_container()

        try:
            data = self.controller.get_flashcards(self.user_id)

            if not data:
                self.container.addWidget(QLabel("Chưa có flashcard nào"))
                return

            for item in data:
                card = FlashcardItem(item["question"], item["answer"])
                self.container.addWidget(card)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi load", str(e))

    def open_study(self):
        self.stack.setCurrentIndex(1)
        self.render_flashcards()

    # ================= FILE =================
    def generate_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file",
            "",
            "Documents (*.pdf *.docx)"
        )

        if not file_path:
            return

        self.stack.setCurrentIndex(1)
        self.clear_container()
        self.container.addWidget(QLabel("📂 Đang đọc file..."))
        QApplication.processEvents()

        try:
            content = self.controller.ai.read_file(file_path)

            if not content or content.startswith("❌"):
                raise ValueError(content)

            self.container.addWidget(QLabel("🤖 AI đang tạo flashcards..."))
            QApplication.processEvents()

            cards = self.controller.generate_ai(content)

            if not cards:
                raise ValueError("AI không trả dữ liệu")

            for c in cards[:15]:
                self.controller.add_flashcard(self.user_id, c["q"], c["a"])

            self.render_flashcards()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # ================= TEXT =================
    def generate_from_text(self):
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Nhập nội dung",
            "Nhập nội dung cần học:"
        )

        if not ok or not text.strip():
            return

        self.stack.setCurrentIndex(1)
        self.clear_container()
        self.container.addWidget(QLabel("🤖 AI đang tạo flashcards..."))
        QApplication.processEvents()

        try:
            cards = self.controller.generate_ai(text)

            if not cards:
                raise ValueError("AI không trả dữ liệu")

            for c in cards[:15]:
                self.controller.add_flashcard(self.user_id, c["q"], c["a"])

            self.render_flashcards()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi AI", str(e))

    # ================= CLEAR =================
    def clear_container(self):
        for i in reversed(range(self.container.count())):
            widget = self.container.itemAt(i).widget()
            if widget:
                widget.deleteLater()