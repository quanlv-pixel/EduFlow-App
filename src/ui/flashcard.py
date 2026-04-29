from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QFileDialog, QMessageBox,
    QTextEdit, QStackedWidget, QApplication, QSizePolicy,
    QProgressBar, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from src.ui.settings_widget import tr, LanguageManager


# ================= AI WORKER =================
class AIWorker(QThread):
    finished = Signal(list)
    error    = Signal(str)

    def __init__(self, controller, mode: str, payload: str):
        super().__init__()
        self.controller = controller
        self.mode = mode      # "file" hoặc "topic"
        self.payload = payload

    def run(self):
        try:
            if self.mode == "file":
                cards = self.controller.generate_ai_from_text(self.payload)
            else:
                cards = self.controller.generate_ai_from_topic(self.payload)

            if not cards:
                self.error.emit(tr("flash_ai_error_empty"))
            else:
                self.finished.emit(cards)
        except Exception as e:
            self.error.emit(str(e))


# ================= FLASHCARD ITEM =================
class FlashcardItem(QFrame):
    """Card lật được — click vào card để lật."""
    deleted = Signal(int)   # phát ra card_id khi user xoá

    def __init__(self, card_id: int, question: str, answer: str):
        super().__init__()

        self.card_id = card_id
        self.q = question
        self.a = answer
        self.is_answer = False

        self.setObjectName("FlashcardItem")
        self.setMinimumHeight(150)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style(False)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(10)

        # ── Top bar: badge + nút xoá ──
        top = QHBoxLayout()
        top.setSpacing(0)

        self.badge = QLabel("Q")
        self.badge.setFixedSize(32, 32)
        self.badge.setAlignment(Qt.AlignCenter)
        self._apply_badge(False)

        top.addWidget(self.badge)
        top.addStretch()

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(28, 28)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setToolTip("Xoá flashcard này")
        btn_del.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #CBD5E1;
                border: none;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #FEE2E2;
                color: #EF4444;
            }
        """)
        btn_del.clicked.connect(self._on_delete)
        top.addWidget(btn_del)

        # ── Nội dung chính ──
        self.lbl = QLabel(question)
        self.lbl.setWordWrap(True)
        self.lbl.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.lbl.setFont(font)
        self.lbl.setStyleSheet("color: #1E2328; background: transparent;")

        # ── Hint ──
        self.hint = QLabel(tr("flash_click_answer"))
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setStyleSheet(
            "color: #9BA3AF; font-size: 11px; background: transparent;"
        )

        root.addLayout(top)
        root.addStretch()
        root.addWidget(self.lbl)
        root.addStretch()
        root.addWidget(self.hint)

    # ── Click lật card ──
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._flip()

    def _flip(self):
        self.is_answer = not self.is_answer
        self.lbl.setText(self.a if self.is_answer else self.q)
        self.hint.setText(
            tr("flash_click_question") if self.is_answer
            else tr("flash_click_answer")
        )
        self._apply_style(self.is_answer)
        self._apply_badge(self.is_answer)

    def _apply_style(self, flipped: bool):
        bg     = "#F0FDF4" if flipped else "#FFFFFF"
        border = "#6EE7B7" if flipped else "#EDEDED"
        self.setStyleSheet(f"""
            QFrame#FlashcardItem {{
                background: {bg};
                border-radius: 16px;
                border: 1.5px solid {border};
            }}
        """)

    def _apply_badge(self, flipped: bool):
        text  = "A"      if flipped else "Q"
        bg    = "#ECFDF5" if flipped else "#EEF2FF"
        color = "#10B981" if flipped else "#2D60FF"
        self.badge.setText(text)
        self.badge.setStyleSheet(f"""
            background: {bg};
            color: {color};
            border-radius: 10px;
            font-size: 13px;
            font-weight: bold;
        """)

    def _on_delete(self):
        self.deleted.emit(self.card_id)


# ================= OPTION CARD =================
class OptionCard(QFrame):
    def __init__(self, icon: str, title: str, desc: str, btn_text: str, on_click):
        super().__init__()
        self.setObjectName("OptionCard")
        self.setStyleSheet("""
            QFrame#OptionCard {
                background: #FFFFFF;
                border-radius: 20px;
                border: 1.5px solid #EDEDED;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(10)

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 36px; background: transparent;")

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #1E2328; background: transparent;"
        )

        self.lbl_desc = QLabel(desc)
        self.lbl_desc.setStyleSheet(
            "font-size: 13px; color: #6F767E; background: transparent;"
        )
        self.lbl_desc.setWordWrap(True)

        self.btn = QPushButton(btn_text)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setFixedHeight(42)
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: #2D60FF;
                color: white;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #1A4FE0; }
        """)
        self.btn.clicked.connect(on_click)

        layout.addWidget(lbl_icon)
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_desc)
        layout.addStretch()
        layout.addWidget(self.btn)

    def retranslate(self, title: str, desc: str, btn_text: str):
        self.lbl_title.setText(title)
        self.lbl_desc.setText(desc)
        self.btn.setText(btn_text)


# ================= PROMPT DIALOG =================
class PromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("flash_prompt_title"))
        self.setFixedSize(480, 300)
        self.setStyleSheet("background: #FFFFFF;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)

        title = QLabel(tr("flash_prompt_label"))
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1E2328;"
        )
        layout.addWidget(title)

        subtitle = QLabel(tr("flash_prompt_subtitle"))
        subtitle.setStyleSheet("font-size: 13px; color: #6F767E;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        examples = QLabel(tr("flash_prompt_examples"))
        examples.setStyleSheet("""
            background: #F0F4FF;
            color: #2D60FF;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
        """)
        examples.setWordWrap(True)
        layout.addWidget(examples)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(tr("flash_prompt_placeholder"))
        self.text_input.setFixedHeight(72)
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 1.5px solid #E5E7EB;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
                color: #1E2328;
                background: #F9FAFB;
            }
            QTextEdit:focus {
                border: 1.5px solid #2D60FF;
                background: #FFFFFF;
            }
        """)
        layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()

        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFixedHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: transparent; color: #6F767E;
                border: 1px solid #EDEDED; border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover { background: #F9FAFB; }
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton(tr("flash_prompt_generate"))
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.setFixedHeight(40)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #2D60FF; color: white;
                border-radius: 8px; font-size: 13px;
                font-weight: bold; border: none; padding: 0 20px;
            }
            QPushButton:hover { background-color: #1A4FE0; }
        """)
        self.btn_ok.clicked.connect(self._on_ok)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_ok)
        layout.addLayout(btn_row)

    def _on_ok(self):
        if self.text_input.toPlainText().strip():
            self.accept()
        else:
            self.text_input.setStyleSheet("""
                QTextEdit {
                    border: 1.5px solid #EF4444; border-radius: 10px;
                    padding: 10px; font-size: 13px; background: #FFF5F5;
                }
            """)

    def get_prompt(self) -> str:
        return self.text_input.toPlainText().strip()


# ================= LOADING WIDGET =================
class LoadingWidget(QFrame):
    def __init__(self, message: str = ""):
        super().__init__()
        if not message:
            message = tr("flash_ai_generating")
        self.setStyleSheet("background: transparent;")
        self.setObjectName("LoadingWidget")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        spinner = QLabel("⏳")
        spinner.setAlignment(Qt.AlignCenter)
        spinner.setStyleSheet("font-size: 40px; background: transparent;")

        msg = QLabel(message)
        msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet(
            "font-size: 14px; color: #6F767E; background: transparent;"
        )

        bar = QProgressBar()
        bar.setRange(0, 0)
        bar.setFixedHeight(6)
        bar.setFixedWidth(200)
        bar.setTextVisible(False)
        bar.setStyleSheet("""
            QProgressBar {
                border: none; background: #EEF0F4; border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #2D60FF; border-radius: 3px;
            }
        """)

        layout.addWidget(spinner)
        layout.addWidget(msg)
        layout.addWidget(bar, alignment=Qt.AlignCenter)


# ================= MAIN FLASHCARD WIDGET =================
class FlashcardWidget(QWidget):
    def __init__(self, controller, user_id):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.controller = controller
        self.user_id = user_id
        self._worker = None

        self.stack = QStackedWidget(self)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)

        self.page_home  = QWidget()
        self.page_study = QWidget()

        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_study)

        self._setup_home()
        self._setup_study()
        self._retranslate()

    # ================================================================
    # HOME PAGE
    # ================================================================
    def _setup_home(self):
        layout = QVBoxLayout(self.page_home)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #1E2328; background: transparent;"
        )
        self.lbl_sub = QLabel()
        self.lbl_sub.setStyleSheet(
            "font-size: 13px; color: #6F767E; background: transparent;"
        )

        layout.addWidget(self.lbl_title)
        layout.addSpacing(4)
        layout.addWidget(self.lbl_sub)
        layout.addSpacing(28)

        # 2 option cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)

        self.card_file = OptionCard(
            icon="📄",
            title=tr("flash_card_file_title"),
            desc=tr("flash_card_file_desc"),
            btn_text=tr("flash_card_file_btn"),
            on_click=self._on_upload_file
        )
        self.card_topic = OptionCard(
            icon="🤖",
            title=tr("flash_card_topic_title"),
            desc=tr("flash_card_topic_desc"),
            btn_text=tr("flash_card_topic_btn"),
            on_click=self._on_enter_prompt
        )

        cards_row.addWidget(self.card_file)
        cards_row.addWidget(self.card_topic)
        layout.addLayout(cards_row)

        layout.addSpacing(20)

        self.btn_view = QPushButton()
        self.btn_view.setCursor(Qt.PointingHandCursor)
        self.btn_view.setFixedHeight(44)
        self.btn_view.setStyleSheet("""
            QPushButton {
                background: #F3F4F6; color: #374151;
                border-radius: 10px; font-size: 14px;
                font-weight: 600; border: none;
            }
            QPushButton:hover { background: #E5E7EB; }
        """)
        self.btn_view.clicked.connect(self._open_saved)
        layout.addWidget(self.btn_view)
        layout.addStretch()

    # ================================================================
    # STUDY PAGE
    # ================================================================
    def _setup_study(self):
        layout = QVBoxLayout(self.page_study)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ──
        header = QHBoxLayout()
        header.setSpacing(8)

        self.btn_back = QPushButton()
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background: transparent; color: #6F767E;
                border: none; font-size: 13px; font-weight: 500;
                text-align: left; padding: 0;
            }
            QPushButton:hover { color: #2D60FF; }
        """)
        self.btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.lbl_study_title = QLabel()
        self.lbl_study_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1E2328; background: transparent;"
        )

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet(
            "font-size: 13px; color: #6F767E; background: transparent;"
        )

        # Nút xoá tất cả
        self.btn_clear_all = QPushButton(tr("flash_clear_all"))
        self.btn_clear_all.setCursor(Qt.PointingHandCursor)
        self.btn_clear_all.setFixedHeight(34)
        self.btn_clear_all.setStyleSheet("""
            QPushButton {
                background: #FEF2F2; color: #EF4444;
                border: 1px solid #FECACA; border-radius: 8px;
                font-size: 12px; font-weight: 600; padding: 0 14px;
            }
            QPushButton:hover { background: #FEE2E2; }
        """)
        self.btn_clear_all.clicked.connect(self._clear_all_flashcards)

        header.addWidget(self.btn_back)
        header.addStretch()
        header.addWidget(self.lbl_study_title)
        header.addStretch()
        header.addWidget(self.lbl_count)
        header.addSpacing(8)
        header.addWidget(self.btn_clear_all)

        layout.addLayout(header)
        layout.addSpacing(16)

        # ── Scroll area ──
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self._scroll_content = QWidget()
        self._scroll_content.setStyleSheet("background: transparent;")

        self.container = QVBoxLayout(self._scroll_content)
        self.container.setContentsMargins(0, 0, 4, 0)
        self.container.setSpacing(12)
        self.container.addStretch()   # stretch luôn ở cuối

        self.scroll.setWidget(self._scroll_content)
        layout.addWidget(self.scroll)

    # ================================================================
    # ACTIONS
    # ================================================================
    def _on_upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("flash_choose_file"), "", "Documents (*.pdf *.docx)"
        )
        if not file_path:
            return

        content = self.controller.ai.read_file(file_path)
        if not content or content.startswith("❌"):
            QMessageBox.warning(
                self, tr("flash_file_error_title"),
                content or tr("flash_file_error_msg")
            )
            return

        import os
        self.lbl_study_title.setText(os.path.basename(file_path))
        self._start_ai(mode="file", payload=content)

    def _on_enter_prompt(self):
        dlg = PromptDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        prompt = dlg.get_prompt()
        if not prompt:
            return

        self.lbl_study_title.setText(
            prompt[:50] + ("..." if len(prompt) > 50 else "")
        )
        self._start_ai(mode="topic", payload=prompt)

    def _open_saved(self):
        self.lbl_study_title.setText(tr("flash_saved_label"))
        self.stack.setCurrentIndex(1)
        self._render_from_db()

    # ================================================================
    # AI WORKER
    # ================================================================
    def _start_ai(self, mode: str, payload: str):
        self.stack.setCurrentIndex(1)
        self._show_loading()

        self._worker = AIWorker(self.controller, mode, payload)
        self._worker.finished.connect(self._on_ai_done)
        self._worker.error.connect(self._on_ai_error)
        self._worker.start()

    def _on_ai_done(self, cards: list):
        saved = 0
        for c in cards[:15]:
            q = c.get("q", "").strip()
            a = c.get("a", "").strip()
            if q and a:
                self.controller.add_flashcard(self.user_id, q, a)
                saved += 1

        self._render_from_db()

        if saved > 0:
            # Thông báo nhỏ màu xanh lá ở đầu
            msg = QLabel(tr("flash_new_saved", saved=saved))
            msg.setAlignment(Qt.AlignCenter)
            msg.setFixedHeight(42)
            msg.setStyleSheet("""
                background: #ECFDF5; color: #10B981;
                border-radius: 10px; font-size: 13px; font-weight: 600;
            """)
            self.container.insertWidget(0, msg)

    def _on_ai_error(self, msg: str):
        self._clear_container()
        err = QLabel(f"❌  {msg}")
        err.setAlignment(Qt.AlignCenter)
        err.setWordWrap(True)
        err.setStyleSheet(
            "color: #EF4444; font-size: 13px; background: transparent; padding: 20px;"
        )
        self.container.insertWidget(0, err)

    # ================================================================
    # RENDER
    # ================================================================
    def _render_from_db(self):
        self._clear_container()

        data = self.controller.get_flashcards(self.user_id)

        if not data:
            empty = QLabel(tr("flash_empty_msg"))
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            empty.setStyleSheet(
                "color: #9BA3AF; font-size: 14px; background: transparent; padding: 40px;"
            )
            self.container.insertWidget(0, empty)
            self.lbl_count.setText("")
            return

        self.lbl_count.setText(f"{len(data)} cards")

        # Chèn mỗi card trước stretch cuối
        for item in data:
            card_id  = item.get("id", -1)
            question = item.get("question", "")
            answer   = item.get("answer", "")

            # Bỏ qua card rác từ lần chạy cũ (question là "Bài X" hoặc quá ngắn)
            if not question or not answer or len(question) < 5:
                continue

            card = FlashcardItem(card_id, question, answer)
            card.deleted.connect(self._on_card_deleted)
            self.container.insertWidget(
                self.container.count() - 1, card
            )

        # Cập nhật count sau khi lọc
        real_count = self.container.count() - 1  # trừ stretch
        self.lbl_count.setText(f"{real_count} cards")

    def _show_loading(self):
        self._clear_container()
        self.container.insertWidget(0, LoadingWidget())

    def _clear_container(self):
        """Xoá hết widget trong container, giữ lại stretch cuối."""
        while self.container.count() > 1:
            item = self.container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ================================================================
    # DELETE
    # ================================================================
    def _on_card_deleted(self, card_id: int):
        """Xoá 1 card khỏi DB và re-render."""
        try:
            self.controller.db.execute(
                "DELETE FROM flashcards WHERE id=?", (card_id,)
            )
        except Exception as e:
            QMessageBox.warning(self, tr("flash_error"), str(e))
            return
        self._render_from_db()

    def _clear_all_flashcards(self):
        """Xoá toàn bộ flashcard của user."""
        reply = QMessageBox.question(
            self, tr("flash_confirm_clear"),
            tr("flash_confirm_clear_msg"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self.controller.db.execute(
                "DELETE FROM flashcards WHERE user_id=?", (self.user_id,)
            )
        except Exception as e:
            QMessageBox.warning(self, tr("flash_error"), str(e))
            return

        self._render_from_db()

    # ================================================================
    # RETRANSLATE
    # ================================================================
    def _retranslate(self):
        self.lbl_title.setText(tr("flash_title"))
        self.lbl_sub.setText(tr("flash_subtitle"))
        self.btn_view.setText("📖  " + tr("flash_view"))
        self.btn_back.setText("← " + tr("flash_back"))
        self.btn_clear_all.setText(tr("flash_clear_all"))

        # Option cards on home page
        self.card_file.retranslate(
            title=tr("flash_card_file_title"),
            desc=tr("flash_card_file_desc"),
            btn_text=tr("flash_card_file_btn"),
        )
        self.card_topic.retranslate(
            title=tr("flash_card_topic_title"),
            desc=tr("flash_card_topic_desc"),
            btn_text=tr("flash_card_topic_btn"),
        )