import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QFileDialog, QMessageBox,
    QTextEdit, QStackedWidget, QProgressBar, QDialog,
    QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
from src.ui.settings_widget import tr, LanguageManager


# ================================================================
# AI WORKER
# ================================================================
class AIWorker(QThread):
    finished = Signal(list)
    error    = Signal(str)

    def __init__(self, controller, mode: str, payload: str):
        super().__init__()
        self.controller = controller
        self.mode    = mode     # "file" | "topic"
        self.payload = payload

    def run(self):
        try:
            if self.mode == "file":
                cards = self.controller.generate_ai_from_text(self.payload)
            else:
                cards = self.controller.generate_ai_from_topic(self.payload)

            if not cards:
                self.error.emit("AI không tạo được flashcard.\nThử lại hoặc viết yêu cầu cụ thể hơn.")
            else:
                self.finished.emit(cards)
        except Exception as e:
            self.error.emit(str(e))


# ================================================================
# PROMPT DIALOG
# ================================================================
class PromptDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tạo Flashcard bằng AI")
        self.setFixedSize(500, 340)
        self.setStyleSheet("background: #FFFFFF;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)

        layout.addWidget(self._lbl("🤖 Nhập yêu cầu cho AI", 18, bold=True, color="#1E2328"))
        layout.addWidget(self._lbl("Mô tả chủ đề bạn muốn ôn tập.", 13, color="#6F767E"))

        ex = QLabel('💡  "Tạo flashcard về Python"  •  "Ôn tập Giải tích"  •  "Lý thuyết đồ thị"')
        ex.setWordWrap(True)
        ex.setStyleSheet(
            "background:#F0F4FF;color:#2D60FF;border-radius:8px;padding:8px 12px;font-size:12px;"
        )
        layout.addWidget(ex)

        lbl_title = QLabel("Tiêu đề bộ flashcard:")
        lbl_title.setStyleSheet("font-size:12px;font-weight:600;color:#374151;")
        layout.addWidget(lbl_title)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ví dụ: Python cơ bản")
        self.title_input.setFixedHeight(38)
        self.title_input.setStyleSheet(self._input_style())
        layout.addWidget(self.title_input)

        lbl_prompt = QLabel("Yêu cầu cho AI:")
        lbl_prompt.setStyleSheet("font-size:12px;font-weight:600;color:#374151;")
        layout.addWidget(lbl_prompt)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Nhập yêu cầu của bạn ở đây...")
        self.text_input.setFixedHeight(70)
        self.text_input.setStyleSheet(self._input_style())
        layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()
        btn_cancel = self._btn("Huỷ", "#F3F4F6", "#374151")
        btn_cancel.clicked.connect(self.reject)
        self.btn_ok = self._btn("✨  Tạo ngay", "#2D60FF", "white")
        self.btn_ok.clicked.connect(self._on_ok)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_ok)
        layout.addLayout(btn_row)

    def _on_ok(self):
        if self.text_input.toPlainText().strip():
            self.accept()

    def get_title(self):
        t = self.title_input.text().strip()
        return t if t else self.text_input.toPlainText().strip()[:40]

    def get_prompt(self):
        return self.text_input.toPlainText().strip()

    def _lbl(self, text, size=13, bold=False, color="#1E2328"):
        l = QLabel(text)
        l.setWordWrap(True)
        l.setStyleSheet(
            f"font-size:{size}px;{'font-weight:bold;' if bold else ''}color:{color};"
        )
        return l

    def _btn(self, text, bg, fg):
        b = QPushButton(text)
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedHeight(40)
        b.setStyleSheet(f"""
            QPushButton {{
                background:{bg};color:{fg};border-radius:8px;
                font-size:13px;font-weight:bold;border:none;padding:0 16px;
            }}
            QPushButton:hover {{ opacity:0.9; }}
        """)
        return b

    def _input_style(self):
        return """
            border:1.5px solid #E5E7EB;border-radius:8px;
            padding:8px 10px;font-size:13px;color:#1E2328;background:#F9FAFB;
        """


# ================================================================
# DECK CARD — hiển thị trong danh sách
# ================================================================
class DeckCard(QFrame):
    def __init__(self, deck: dict, on_open, on_delete):
        super().__init__()
        self.deck = deck
        self.setObjectName("DeckCard")
        self.setFixedHeight(88)
        self.setCursor(Qt.PointingHandCursor)
        self._hover(False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 16, 0)
        layout.setSpacing(14)

        # Icon
        source = deck.get("source", "")
        icon = "📄" if source == "file" else "🤖"
        lbl_icon = QLabel(icon)
        lbl_icon.setFixedSize(44, 44)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet(
            "background:#EEF2FF;border-radius:12px;font-size:20px;"
        )

        # Info
        info = QVBoxLayout()
        info.setSpacing(4)

        lbl_title = QLabel(deck.get("title", "Bộ flashcard"))
        lbl_title.setStyleSheet(
            "font-size:15px;font-weight:bold;color:#1E2328;background:transparent;"
        )

        count = deck.get("card_count", 0)
        created = deck.get("created_at", "")[:10]
        lbl_meta = QLabel(f"{count} câu hỏi  •  {created}")
        lbl_meta.setStyleSheet("font-size:12px;color:#6F767E;background:transparent;")

        info.addWidget(lbl_title)
        info.addWidget(lbl_meta)

        # Nút xóa
        btn_del = QPushButton("🗑")
        btn_del.setFixedSize(34, 34)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setToolTip("Xóa bộ flashcard")
        btn_del.setStyleSheet("""
            QPushButton {
                background:transparent;color:#CBD5E1;
                border:none;font-size:15px;border-radius:8px;
            }
            QPushButton:hover { background:#FEE2E2;color:#EF4444; }
        """)
        btn_del.clicked.connect(lambda: on_delete(deck))

        layout.addWidget(lbl_icon)
        layout.addLayout(info, stretch=1)
        layout.addWidget(btn_del)

        self.mousePressEvent = lambda e: on_open(deck) if e.button() == Qt.LeftButton else None

    def _hover(self, h):
        self.setStyleSheet(f"""
            QFrame#DeckCard {{
                background:#FFFFFF;border-radius:16px;
                border:{'1.5px solid #2D60FF' if h else '1px solid #EDEDED'};
            }}
        """)

    def enterEvent(self, e): self._hover(True)
    def leaveEvent(self, e): self._hover(False)


# ================================================================
# QUIZ WIDGET — câu hỏi + 4 đáp án
# ================================================================
class QuizWidget(QWidget):
    finished = Signal(int, int)  # (đúng, tổng)

    def __init__(self, cards: list, deck_title: str):
        super().__init__()
        self.deck_title = deck_title
        self.cards  = self._build_quiz(cards)
        self.index  = 0
        self.score  = 0
        self.answered = False

        self._setup_ui()
        self._show_question()

    def _build_quiz(self, cards: list) -> list:
        """Mỗi card thêm 3 đáp án sai ngẫu nhiên từ các card khác."""
        all_answers = [c.get("answer", c.get("a", "")) for c in cards]
        result = []
        for c in cards:
            q = c.get("question", c.get("q", ""))
            a = c.get("answer",   c.get("a", ""))
            wrongs = [x for x in all_answers if x != a]
            random.shuffle(wrongs)
            options = [a] + wrongs[:3]
            random.shuffle(options)
            result.append({"q": q, "a": a, "options": options})
        return result

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # ── Header ──
        header = QHBoxLayout()

        self.lbl_progress_text = QLabel()
        self.lbl_progress_text.setStyleSheet(
            "font-size:13px;color:#6F767E;background:transparent;"
        )

        self.lbl_score = QLabel()
        self.lbl_score.setStyleSheet(
            "font-size:13px;font-weight:600;color:#10B981;background:transparent;"
        )

        header.addWidget(self.lbl_progress_text)
        header.addStretch()
        header.addWidget(self.lbl_score)
        layout.addLayout(header)

        # Progress bar
        self.prog = QProgressBar()
        self.prog.setFixedHeight(6)
        self.prog.setTextVisible(False)
        self.prog.setStyleSheet("""
            QProgressBar { border:none;background:#EEF0F4;border-radius:3px; }
            QProgressBar::chunk { background:#2D60FF;border-radius:3px; }
        """)
        layout.addWidget(self.prog)

        # ── Câu hỏi ──
        q_card = QFrame()
        q_card.setObjectName("QCard")
        q_card.setMinimumHeight(120)
        q_card.setStyleSheet("""
            QFrame#QCard {
                background:#EEF2FF;border-radius:20px;border:none;
            }
        """)
        q_layout = QVBoxLayout(q_card)
        q_layout.setContentsMargins(32, 24, 32, 24)

        lbl_q_badge = QLabel("CÂU HỎI")
        lbl_q_badge.setStyleSheet(
            "font-size:10px;font-weight:700;color:#6366F1;"
            "letter-spacing:1.5px;background:transparent;"
        )

        self.lbl_question = QLabel()
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.lbl_question.setFont(font)
        self.lbl_question.setStyleSheet("color:#1E2328;background:transparent;")

        q_layout.addWidget(lbl_q_badge, alignment=Qt.AlignLeft)
        q_layout.addSpacing(8)
        q_layout.addWidget(self.lbl_question)

        layout.addWidget(q_card)

        # ── 4 Đáp án ──
        self.option_btns = []
        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(10)

        for i in range(4):
            btn = QPushButton()
            btn.setMinimumHeight(52)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(self._option_style("default"))
            btn.clicked.connect(lambda _, idx=i: self._on_answer(idx))
            self.option_btns.append(btn)
            self.options_layout.addWidget(btn)

        layout.addLayout(self.options_layout)

        # ── Feedback ──
        self.lbl_feedback = QLabel()
        self.lbl_feedback.setAlignment(Qt.AlignCenter)
        self.lbl_feedback.setFixedHeight(36)
        self.lbl_feedback.setStyleSheet("font-size:14px;font-weight:600;background:transparent;")
        layout.addWidget(self.lbl_feedback)

        # ── Nút tiếp theo ──
        self.btn_next = QPushButton("Câu tiếp theo →")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setFixedHeight(48)
        self.btn_next.setVisible(False)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background:#2D60FF;color:white;border-radius:12px;
                font-size:14px;font-weight:bold;border:none;
            }
            QPushButton:hover { background:#1A4FE0; }
        """)
        self.btn_next.clicked.connect(self._next_question)
        layout.addWidget(self.btn_next)

    def _show_question(self):
        if self.index >= len(self.cards):
            self.finished.emit(self.score, len(self.cards))
            return

        card = self.cards[self.index]
        total = len(self.cards)

        self.answered = False
        self.lbl_feedback.setText("")
        self.btn_next.setVisible(False)

        self.lbl_progress_text.setText(f"Câu {self.index + 1} / {total}")
        self.lbl_score.setText(f"✅ {self.score} đúng")
        self.prog.setMaximum(total)
        self.prog.setValue(self.index)

        self.lbl_question.setText(card["q"])

        for i, opt in enumerate(card["options"]):
            self.option_btns[i].setText(opt)
            self.option_btns[i].setStyleSheet(self._option_style("default"))
            self.option_btns[i].setEnabled(True)

    def _on_answer(self, idx: int):
        if self.answered:
            return
        self.answered = True

        card    = self.cards[self.index]
        chosen  = self.option_btns[idx].text()
        correct = card["a"]
        is_right = (chosen == correct)

        if is_right:
            self.score += 1
            self.lbl_feedback.setText("🎉 Chính xác!")
            self.lbl_feedback.setStyleSheet(
                "font-size:14px;font-weight:600;color:#10B981;background:transparent;"
            )
        else:
            self.lbl_feedback.setText(f"❌ Sai!  Đáp án: {correct}")
            self.lbl_feedback.setStyleSheet(
                "font-size:13px;font-weight:600;color:#EF4444;background:transparent;"
            )

        # Tô màu các nút
        for i, btn in enumerate(self.option_btns):
            btn.setEnabled(False)
            if btn.text() == correct:
                btn.setStyleSheet(self._option_style("correct"))
            elif i == idx and not is_right:
                btn.setStyleSheet(self._option_style("wrong"))
            else:
                btn.setStyleSheet(self._option_style("dim"))

        self.lbl_score.setText(f"✅ {self.score} đúng")

        # Câu cuối → đổi text nút
        if self.index + 1 >= len(self.cards):
            self.btn_next.setText("Xem kết quả 🏁")
        else:
            self.btn_next.setText("Câu tiếp theo →")
        self.btn_next.setVisible(True)

    def _next_question(self):
        self.index += 1
        self._show_question()

    def _option_style(self, state: str) -> str:
        base = "border-radius:12px;font-size:13px;font-weight:500;border:1.5px solid;"
        styles = {
            "default": f"{base}background:#F9FAFB;color:#1E2328;border-color:#E5E7EB;",
            "correct": f"{base}background:#ECFDF5;color:#065F46;border-color:#6EE7B7;font-weight:700;",
            "wrong":   f"{base}background:#FEF2F2;color:#991B1B;border-color:#FCA5A5;font-weight:700;",
            "dim":     f"{base}background:#F3F4F6;color:#9BA3AF;border-color:#E5E7EB;",
        }
        return styles.get(state, styles["default"])


# ================================================================
# RESULT WIDGET — hiển thị sau khi làm xong quiz
# ================================================================
class ResultWidget(QWidget):
    def __init__(self, score: int, total: int, on_retry, on_back):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        pct = int(score / total * 100) if total else 0

        emoji = "🏆" if pct == 100 else "🎉" if pct >= 70 else "📚"
        lbl_e = QLabel(emoji)
        lbl_e.setAlignment(Qt.AlignCenter)
        lbl_e.setStyleSheet("font-size:60px;background:transparent;")

        lbl_title = QLabel("Kết quả ôn tập")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(
            "font-size:22px;font-weight:bold;color:#1E2328;background:transparent;"
        )

        lbl_score = QLabel(f"{score} / {total}  ({pct}%)")
        lbl_score.setAlignment(Qt.AlignCenter)
        lbl_score.setStyleSheet(
            "font-size:36px;font-weight:bold;color:#2D60FF;background:transparent;"
        )

        msg = ("Xuất sắc! Bạn trả lời đúng tất cả! 🌟" if pct == 100
               else "Tốt lắm! Tiếp tục cố gắng nhé! 💪" if pct >= 70
               else "Hãy ôn tập thêm nhé! 📖")
        lbl_msg = QLabel(msg)
        lbl_msg.setAlignment(Qt.AlignCenter)
        lbl_msg.setStyleSheet("font-size:14px;color:#6F767E;background:transparent;")

        btn_retry = QPushButton("🔄  Làm lại")
        btn_retry.setCursor(Qt.PointingHandCursor)
        btn_retry.setFixedHeight(44)
        btn_retry.setFixedWidth(160)
        btn_retry.setStyleSheet("""
            QPushButton {
                background:#EEF2FF;color:#2D60FF;border-radius:10px;
                font-size:14px;font-weight:bold;border:none;
            }
            QPushButton:hover { background:#E0E7FF; }
        """)
        btn_retry.clicked.connect(on_retry)

        btn_back = QPushButton("← Quay lại")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setFixedHeight(44)
        btn_back.setFixedWidth(160)
        btn_back.setStyleSheet("""
            QPushButton {
                background:#2D60FF;color:white;border-radius:10px;
                font-size:14px;font-weight:bold;border:none;
            }
            QPushButton:hover { background:#1A4FE0; }
        """)
        btn_back.clicked.connect(on_back)

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_retry)
        btn_row.addWidget(btn_back)

        layout.addWidget(lbl_e)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_score)
        layout.addWidget(lbl_msg)
        layout.addSpacing(16)
        layout.addLayout(btn_row)


# ================================================================
# MAIN FLASHCARD WIDGET — 3 tầng: decks → quiz → result
# ================================================================
class FlashcardWidget(QWidget):
    def __init__(self, controller, user_id: int):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.controller = controller
        self.user_id    = user_id
        self._worker    = None
        self._pending_title  = ""
        self._pending_cards  = []
        self._current_deck   = None

        # Stack: 0=home(danh sách deck), 1=quiz, 2=result
        self.stack = QStackedWidget(self)
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(self.stack)

        self.page_home   = QWidget()
        self.page_quiz   = QWidget()
        self.page_result = QWidget()

        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_quiz)
        self.stack.addWidget(self.page_result)

        self._setup_home()
        self._retranslate()

    # ============================================================
    # HOME — danh sách deck
    # ============================================================
    def _setup_home(self):
        layout = QVBoxLayout(self.page_home)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet(
            "font-size:26px;font-weight:bold;color:#1E2328;background:transparent;"
        )
        self.lbl_sub = QLabel()
        self.lbl_sub.setStyleSheet("font-size:13px;color:#6F767E;background:transparent;")

        layout.addWidget(self.lbl_title)
        layout.addSpacing(4)
        layout.addWidget(self.lbl_sub)
        layout.addSpacing(24)

        # 2 nút tạo mới
        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)
        self.btn_file = self._action_btn(
            "📄", "Tải lên tài liệu",
            "Upload PDF/DOCX — AI tự tạo flashcard",
            self._on_upload_file
        )
        self.btn_topic = self._action_btn(
            "🤖", "Nhập yêu cầu",
            "Gõ chủ đề, AI tạo flashcard ngay",
            self._on_enter_prompt
        )
        btn_row.addWidget(self.btn_file)
        btn_row.addWidget(self.btn_topic)
        layout.addLayout(btn_row)
        layout.addSpacing(24)

        # ── Tab + Refresh ──────────────────────────────────────
        tab_row = QHBoxLayout()
        tab_row.setSpacing(8)

        self.btn_tab_mine = QPushButton("📚  Bộ đề của tôi")
        self.btn_tab_course = QPushButton("🎓  Từ khóa học")
        self.btn_refresh = QPushButton("🔄")

        for btn in [self.btn_tab_mine, self.btn_tab_course]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(34)
            btn.setCheckable(True)
            btn.setStyleSheet(self._tab_style(False))

        self.btn_tab_mine.setChecked(True)
        self.btn_tab_mine.setStyleSheet(self._tab_style(True))

        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setFixedSize(34, 34)
        self.btn_refresh.setToolTip("Làm mới danh sách")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background:#F3F4F6;color:#374151;border-radius:8px;
                font-size:15px;border:none;
            }
            QPushButton:hover { background:#E5E7EB; }
        """)

        self._current_tab = "mine"  # "mine" | "course"
        self.btn_tab_mine.clicked.connect(lambda: self._switch_tab("mine"))
        self.btn_tab_course.clicked.connect(lambda: self._switch_tab("course"))
        self.btn_refresh.clicked.connect(self._load_decks)

        tab_row.addWidget(self.btn_tab_mine)
        tab_row.addWidget(self.btn_tab_course)
        tab_row.addStretch()
        tab_row.addWidget(self.btn_refresh)
        layout.addLayout(tab_row)
        layout.addSpacing(10)

        # Scroll danh sách decks
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background:transparent;border:none;")

        self._deck_content = QWidget()
        self._deck_content.setStyleSheet("background:transparent;")
        self._deck_layout = QVBoxLayout(self._deck_content)
        self._deck_layout.setContentsMargins(0, 0, 4, 0)
        self._deck_layout.setSpacing(10)
        self._deck_layout.addStretch()

        self.scroll.setWidget(self._deck_content)
        layout.addWidget(self.scroll, stretch=1)

        self._load_decks()

    def _tab_style(self, active: bool) -> str:
        if active:
            return """
                QPushButton {
                    background:#EEF2FF;color:#2D60FF;border-radius:8px;
                    font-size:13px;font-weight:bold;border:1.5px solid #C7D7FF;
                    padding:0 14px;
                }
            """
        return """
            QPushButton {
                background:#F3F4F6;color:#6F767E;border-radius:8px;
                font-size:13px;border:none;padding:0 14px;
            }
            QPushButton:hover { background:#E5E7EB; }
        """

    def _switch_tab(self, tab: str):
        self._current_tab = tab
        self.btn_tab_mine.setChecked(tab == "mine")
        self.btn_tab_course.setChecked(tab == "course")
        self.btn_tab_mine.setStyleSheet(self._tab_style(tab == "mine"))
        self.btn_tab_course.setStyleSheet(self._tab_style(tab == "course"))
        self._load_decks()   # reload khi đổi tab

    def _action_btn(self, icon, title, desc, callback) -> QFrame:
        frame = QFrame()
        frame.setObjectName("ActionCard")
        frame.setStyleSheet("""
            QFrame#ActionCard {
                background:#FFFFFF;border-radius:16px;border:1.5px solid #EDEDED;
            }
            QFrame#ActionCard:hover { border:1.5px solid #2D60FF; }
        """)
        v = QVBoxLayout(frame)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(6)

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size:28px;background:transparent;")
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            "font-size:14px;font-weight:bold;color:#1E2328;background:transparent;"
        )
        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet("font-size:12px;color:#6F767E;background:transparent;")
        lbl_desc.setWordWrap(True)

        btn = QPushButton("Bắt đầu →")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(36)
        btn.setStyleSheet("""
            QPushButton {
                background:#2D60FF;color:white;border-radius:8px;
                font-size:12px;font-weight:bold;border:none;
            }
            QPushButton:hover { background:#1A4FE0; }
        """)
        btn.clicked.connect(callback)

        v.addWidget(lbl_icon)
        v.addWidget(lbl_title)
        v.addWidget(lbl_desc)
        v.addStretch()
        v.addWidget(btn)
        return frame

    # ── Load danh sách decks ──
    def _load_decks(self):
        # Xóa cũ (giữ stretch cuối)
        while self._deck_layout.count() > 1:
            item = self._deck_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        all_decks = self.controller.get_decks(self.user_id)

        # Filter theo tab hiện tại
        tab = getattr(self, "_current_tab", "mine")
        if tab == "mine":
            decks = [d for d in all_decks if d.get("source", "") != "course"]
            empty_msg = "Chưa có bộ flashcard nào.\nHãy tạo mới bằng 2 nút bên trên!"
        else:
            decks = [d for d in all_decks if d.get("source", "") == "course"]
            empty_msg = (
                "Chưa có flashcard nào từ khóa học.\n"
                "Vào Khóa học → Bài học → ⚡ Flashcard để tạo."
            )

        if not decks:
            empty = QLabel(empty_msg)
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            empty.setStyleSheet(
                "color:#9BA3AF;font-size:14px;background:transparent;padding:40px;"
            )
            self._deck_layout.insertWidget(0, empty)
            return

        for deck in decks:
            card = DeckCard(deck, self._open_deck, self._delete_deck)
            self._deck_layout.insertWidget(self._deck_layout.count() - 1, card)

    def _open_deck(self, deck: dict):
        """Bắt đầu quiz với bộ flashcard được chọn."""
        cards = self.controller.get_flashcards(self.user_id, deck["id"])
        if not cards:
            QMessageBox.information(self, "Trống", "Bộ flashcard này chưa có câu hỏi nào.")
            return

        if len(cards) < 2:
            QMessageBox.information(
                self, "Quá ít câu",
                "Cần ít nhất 2 câu hỏi để tạo bài quiz với 4 đáp án."
            )
            return

        self._current_deck  = deck
        self._current_cards = cards
        self._start_quiz(cards, deck.get("title", "Ôn tập"))

    def _delete_deck(self, deck: dict):
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Xóa bộ flashcard\n\"{deck.get('title','')}\"?\n"
            f"({deck.get('card_count', 0)} câu hỏi sẽ bị xóa)",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.controller.delete_deck(deck["id"])
            self._load_decks()

    # ============================================================
    # TẠO DECK MỚI
    # ============================================================
    def _on_upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn tài liệu học tập", "", "Documents (*.pdf *.docx)"
        )
        if not file_path:
            return

        content = self.controller.ai.read_file(file_path)
        if not content or content.startswith("❌"):
            QMessageBox.warning(self, "Lỗi đọc file", content or "Không đọc được file.")
            return

        import os
        self._pending_title = os.path.basename(file_path)
        self._run_ai("file", content)

    def _on_enter_prompt(self):
        dlg = PromptDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        prompt = dlg.get_prompt()
        if not prompt:
            return
        self._pending_title = dlg.get_title() or prompt[:40]
        self._run_ai("topic", prompt)

    def _run_ai(self, mode: str, payload: str):
        self._show_loading()
        self._worker = AIWorker(self.controller, mode, payload)
        self._worker.finished.connect(self._on_ai_done)
        self._worker.error.connect(self._on_ai_error)
        self._worker.start()

    def _on_ai_done(self, cards: list):
        source = "file" if self._worker and self._worker.mode == "file" else "topic"
        deck_id, saved = self.controller._save_deck(
            self.user_id, self._pending_title, cards, source=source
        )

        self._hide_loading()
        self._load_decks()

        QMessageBox.information(
            self, "✅ Tạo thành công",
            f"Đã tạo bộ flashcard\n\"{self._pending_title}\"\nvới {saved} câu hỏi.\n\n"
            "Nhấn vào bộ để bắt đầu ôn tập!"
        )

    def _on_ai_error(self, msg: str):
        self._hide_loading()
        QMessageBox.warning(self, "Lỗi AI", msg)

    # ── Loading overlay ──
    def _show_loading(self):
        self._loading = QLabel("⏳  AI đang tạo flashcard...")
        self._loading.setAlignment(Qt.AlignCenter)
        self._loading.setStyleSheet("""
            background:rgba(255,255,255,0.9);
            color:#2D60FF;font-size:15px;font-weight:600;
            border-radius:12px;
        """)
        self._loading.setGeometry(self.page_home.rect())
        self._loading.setParent(self.page_home)
        self._loading.show()
        self._loading.raise_()

    def _hide_loading(self):
        if hasattr(self, "_loading") and self._loading:
            self._loading.hide()
            self._loading.deleteLater()
            self._loading = None

    # ============================================================
    # QUIZ
    # ============================================================
    def _start_quiz(self, cards: list, title: str):
        # Xóa quiz cũ nếu có
        old = self.page_quiz.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old)

        layout = QVBoxLayout(self.page_quiz)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Back button
        btn_back = QPushButton("← Danh sách")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background:transparent;color:#6F767E;border:none;
                font-size:13px;font-weight:500;text-align:left;padding:0;
            }
            QPushButton:hover { color:#2D60FF; }
        """)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(btn_back)
        layout.addSpacing(16)

        # Tiêu đề
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            "font-size:18px;font-weight:bold;color:#1E2328;background:transparent;"
        )
        layout.addWidget(lbl_title)
        layout.addSpacing(16)

        self._quiz_widget = QuizWidget(cards, title)
        self._quiz_widget.finished.connect(self._on_quiz_finished)
        layout.addWidget(self._quiz_widget, stretch=1)

        self.stack.setCurrentIndex(1)

    def _on_quiz_finished(self, score: int, total: int):
        # Nếu là deck từ khóa học → đánh dấu lesson done + tính progress
        lesson_id   = None
        course_id   = None
        new_progress = None

        if self._current_deck and self._current_deck.get("source") == "course":
            lesson_id = self._current_deck.get("lesson_id")
            if lesson_id:
                # Đánh dấu bài học hoàn thành
                self.controller.db.set_lesson_completed(lesson_id, True)

                # Lấy course_id từ lesson để tính progress
                rows = self.controller.db.execute(
                    "SELECT course_id FROM lessons WHERE id=?",
                    (lesson_id,), fetch=True
                )
                if rows:
                    course_id  = rows[0]["course_id"]
                    new_progress = self.controller.db.get_course_progress(course_id)

        # Xóa result cũ
        old = self.page_result.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old)

        layout = QVBoxLayout(self.page_result)
        layout.setContentsMargins(0, 0, 0, 0)

        result = ResultWidget(
            score, total,
            course_progress = new_progress,   # None nếu không phải deck course
            on_retry = lambda: self._start_quiz(
                self._current_cards,
                self._current_deck.get("title", "Ôn tập") if self._current_deck else "Ôn tập"
            ),
            on_back = lambda: self.stack.setCurrentIndex(0)
        )
        layout.addWidget(result)
        self.stack.setCurrentIndex(2)

    # ============================================================
    # RETRANSLATE
    # ============================================================
    def _retranslate(self):
        self.lbl_title.setText(tr("flash_title"))
        self.lbl_sub.setText(tr("flash_subtitle"))

    def set_ai_limit(self, *args, **kwargs):
        """Stub — giữ tương thích với dashboard.py."""
        pass