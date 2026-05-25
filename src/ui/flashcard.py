import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QFileDialog, QMessageBox,
    QTextEdit, QStackedWidget, QProgressBar, QDialog,
    QLineEdit, QSizePolicy, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
from src.ui.settings_widget import tr, LanguageManager


# ================================================================
# WRAP OPTION BUTTON — Hỗ trợ xuống hàng tự động cho đáp án dài
# ================================================================
class WrapOptionButton(QFrame):
    """QFrame-based button that wraps long text instead of expanding horizontally."""
    clicked = Signal(int)   # emit index

    _STYLES = {
        "default": (
            "background:#F9FAFB;border:1.5px solid #E5E7EB;border-radius:12px;",
            "color:#1E2328;font-size:13px;font-weight:500;"
        ),
        "correct": (
            "background:#ECFDF5;border:1.5px solid #6EE7B7;border-radius:12px;",
            "color:#065F46;font-size:13px;font-weight:700;"
        ),
        "wrong": (
            "background:#FEF2F2;border:1.5px solid #FCA5A5;border-radius:12px;",
            "color:#991B1B;font-size:13px;font-weight:700;"
        ),
        "dim": (
            "background:#F3F4F6;border:1.5px solid #E5E7EB;border-radius:12px;",
            "color:#9BA3AF;font-size:13px;font-weight:500;"
        ),
    }

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self._index   = index
        self._enabled = True
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(52)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        inner = QVBoxLayout(self)
        inner.setContentsMargins(16, 10, 16, 10)
        inner.setSpacing(0)

        self._lbl = QLabel()
        self._lbl.setWordWrap(True)
        self._lbl.setAlignment(Qt.AlignCenter)
        self._lbl.setStyleSheet("background:transparent;border:none;")
        inner.addWidget(self._lbl)

        self.apply_style("default")

    def setText(self, text: str):
        self._lbl.setText(text)

    def text(self) -> str:
        return self._lbl.text()

    def setEnabled(self, v: bool):
        self._enabled = v
        super().setEnabled(v)
        self.setCursor(Qt.PointingHandCursor if v else Qt.ArrowCursor)

    def apply_style(self, state: str):
        frame_css, lbl_css = self._STYLES.get(state, self._STYLES["default"])
        self.setStyleSheet(frame_css)
        self._lbl.setStyleSheet(f"background:transparent;border:none;{lbl_css}")

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self._enabled:
            self.clicked.emit(self._index)


# ================================================================
# AI WORKER
# ================================================================
class AIWorker(QThread):
    finished = Signal(list)
    error    = Signal(str)

    def __init__(self, controller, mode: str, payload: str, lang: str = "vi"):
        super().__init__()
        self.controller = controller
        self.mode    = mode     # "file" | "topic"
        self.payload = payload
        self.lang    = lang

    def run(self):
        try:
            if self.mode == "file":
                cards = self.controller.generate_ai_from_text(self.payload, lang=self.lang)
            else:
                cards = self.controller.generate_ai_from_topic(self.payload, lang=self.lang)

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
        self.setWindowTitle(tr("flash_prompt_title"))
        self.setFixedSize(500, 340)
        self.setStyleSheet("background: #FFFFFF;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)

        layout.addWidget(self._lbl(tr("flash_prompt_label"), 18, bold=True, color="#1E2328"))
        layout.addWidget(self._lbl(tr("flash_prompt_subtitle"), 13, color="#6F767E"))

        ex = QLabel(tr("flash_prompt_examples"))
        ex.setWordWrap(True)
        ex.setStyleSheet("background:#F0F4FF;color:#2D60FF;border-radius:8px;padding:8px 12px;font-size:12px;")
        layout.addWidget(ex)

        lbl_title = QLabel(tr("flash_prompt_deck_title"))
        lbl_title.setStyleSheet("font-size:12px;font-weight:600;color:#374151;")
        layout.addWidget(lbl_title)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(tr("flash_prompt_deck_title_ph"))
        self.title_input.setFixedHeight(38)
        self.title_input.setStyleSheet(self._input_style())
        layout.addWidget(self.title_input)

        lbl_prompt = QLabel(tr("flash_prompt_req"))
        lbl_prompt.setStyleSheet("font-size:12px;font-weight:600;color:#374151;")
        layout.addWidget(lbl_prompt)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(tr("flash_prompt_placeholder"))
        self.text_input.setFixedHeight(70)
        self.text_input.setStyleSheet(self._input_style())
        layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()
        btn_cancel = self._btn(tr("cancel"), "#F3F4F6", "#374151")
        btn_cancel.clicked.connect(self.reject)

        self.btn_ok = self._btn(tr("flash_prompt_generate"), "#2D60FF", "white")
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
        l.setStyleSheet(f"font-size:{size}px;{'font-weight:bold;' if bold else ''}color:{color};")
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
# DECK CARD — Widget hiển thị thông tin từng bộ Deck
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

        source = deck.get("source", "")
        icon = "📚" if source == "course" else ("📄" if source == "file" else "🤖")
        lbl_icon = QLabel(icon)
        lbl_icon.setFixedSize(44, 44)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet("background:#EEF2FF;border-radius:12px;font-size:20px;")

        info = QVBoxLayout()
        info.setSpacing(4)

        lbl_title = QLabel(deck.get("title", "Bộ flashcard"))
        lbl_title.setStyleSheet("font-size:15px;font-weight:bold;color:#1E2328;background:transparent;")

        count = deck.get("card_count", 0)
        done = bool(deck.get("is_completed", 0))

        status_text = "✅ Đã hoàn thành" if done else "⏳ Chưa hoàn thành"
        status_color = "#10B981" if done else "#F59E0B"

        lbl_meta = QLabel(f"{count} câu hỏi")
        lbl_meta.setStyleSheet("font-size:12px;color:#6F767E;background:transparent;")

        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"font-size:12px;font-weight:600;color:{status_color};background:transparent;")

        info.addWidget(lbl_title)
        info.addWidget(lbl_meta)
        info.addWidget(lbl_status)

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

        if done:
            lbl_done = QLabel("✅")
            lbl_done.setFixedWidth(30)
            lbl_done.setAlignment(Qt.AlignCenter)
            lbl_done.setStyleSheet("font-size:18px;color:#10B981;background:transparent;")
            lbl_done.setToolTip("Đã hoàn thành")
            layout.addWidget(lbl_done)

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
# QUIZ WIDGET — Luồng hiển thị trắc nghiệm + bóc tách dữ liệu
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
        """Nhận diện chuỗi đóng gói ||options|| hoặc tự tạo đáp án nhiễu ngẫu nhiên."""
        all_answers = [
            c.get("answer", c.get("a", ""))
            for c in cards
            if "||options||" not in (c.get("question") or c.get("q", ""))
        ]
        result = []

        for c in cards:
            q = c.get("question") or c.get("q", "")
            a = c.get("answer") or c.get("a", "")

            # TRƯỜNG HỢP 1: Cấu trúc trắc nghiệm đóng gói sẵn
            if "||options||" in q:
                parts = q.split("||options||")
                question_text = parts[0]
                options_list = parts[1].split("|")

                try:
                    correct_idx = int(a)
                except (ValueError, TypeError):
                    correct_idx = 0
                    if a in options_list:
                        correct_idx = options_list.index(a)

                result.append({
                    "q": question_text,
                    "a_text": options_list[correct_idx] if correct_idx < len(options_list) else str(a),
                    "options": options_list,
                    "correct_index": correct_idx
                })

            # TRƯỜNG HỢP 2: Flashcard 2 mặt truyền thống → Tự sinh đáp án gây nhiễu
            else:
                wrongs = [x for x in all_answers if x != a]
                random.shuffle(wrongs)
                options = [a] + wrongs[:3]
                while len(options) < 4:
                    options.append(tr("flash_empty_option") or "Đáp án khác")
                random.shuffle(options)

                result.append({
                    "q": q,
                    "a_text": a,
                    "options": options,
                    "correct_index": options.index(a)
                })
        return result

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        header = QHBoxLayout()
        self.lbl_progress_text = QLabel()
        self.lbl_progress_text.setStyleSheet("font-size:13px;color:#6F767E;background:transparent;")
        self.lbl_score = QLabel()
        self.lbl_score.setStyleSheet("font-size:13px;font-weight:600;color:#10B981;background:transparent;")
        header.addWidget(self.lbl_progress_text)
        header.addStretch()
        header.addWidget(self.lbl_score)
        layout.addLayout(header)

        self.prog = QProgressBar()
        self.prog.setFixedHeight(6)
        self.prog.setTextVisible(False)
        self.prog.setStyleSheet("""
            QProgressBar { border:none;background:#EEF0F4;border-radius:3px; }
            QProgressBar::chunk { background:#2D60FF;border-radius:3px; }
        """)
        layout.addWidget(self.prog)

        q_card = QFrame()
        q_card.setObjectName("QCard")
        q_card.setMinimumHeight(120)
        q_card.setStyleSheet("QFrame#QCard { background:#EEF2FF;border-radius:20px;border:none; }")

        q_layout = QVBoxLayout(q_card)
        q_layout.setContentsMargins(32, 24, 32, 24)
        lbl_q_badge = QLabel("CÂU HỎI")
        lbl_q_badge.setStyleSheet("font-size:10px;font-weight:700;color:#6366F1;letter-spacing:1.5px;background:transparent;")

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

        self.option_btns = []
        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(10)
        for i in range(4):
            btn = WrapOptionButton(i)
            btn.clicked.connect(self._on_answer)
            self.option_btns.append(btn)
            self.options_layout.addWidget(btn)
        layout.addLayout(self.options_layout)

        self.lbl_feedback = QLabel()
        self.lbl_feedback.setAlignment(Qt.AlignCenter)
        self.lbl_feedback.setFixedHeight(36)
        self.lbl_feedback.setStyleSheet("font-size:14px;font-weight:600;background:transparent;")
        layout.addWidget(self.lbl_feedback)

        self.btn_next = QPushButton("Câu tiếp theo →")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setFixedHeight(48)
        self.btn_next.setVisible(False)
        self.btn_next.setStyleSheet("""
            QPushButton {
                background:#2D60FF;color:white;border-radius:12px;
                font-size:14px;font-weight:bold;border:none;
            }
            QPushButton:hover { background:#1A4BDB; }
        """)
        self.btn_next.clicked.connect(self._on_next)
        layout.addWidget(self.btn_next)

    def _show_question(self):
        if self.index >= len(self.cards):
            self.finished.emit(self.score, len(self.cards))
            return

        self.answered = False
        self.btn_next.setVisible(False)
        self.lbl_feedback.setText("")

        c = self.cards[self.index]
        self.lbl_question.setText(c["q"])

        self.lbl_progress_text.setText(f"Câu hỏi {self.index + 1} trên {len(self.cards)}")
        self.lbl_score.setText(f"Đúng: {self.score}")
        percent = int((self.index / len(self.cards)) * 100)
        self.prog.setValue(percent)

        for i, btn in enumerate(self.option_btns):
            if i < len(c["options"]):
                btn.setText(c["options"][i])
                btn.apply_style("default")
                btn.setEnabled(True)
                btn.setVisible(True)
            else:
                btn.setVisible(False)

    def _on_answer(self, idx: int):
        if self.answered:
            return
        self.answered = True

        c = self.cards[self.index]
        correct = c["correct_index"]

        if idx == correct:
            self.score += 1
            self.option_btns[idx].apply_style("correct")
            self.lbl_feedback.setText("🎉 Chính xác! Tuyệt vời lắm.")
            self.lbl_feedback.setStyleSheet("color:#10B981;font-size:14px;font-weight:600;")
        else:
            self.option_btns[idx].apply_style("wrong")
            self.option_btns[correct].apply_style("correct")
            self.lbl_feedback.setText("❌ Chưa đúng rồi, cố gắng lên nhé!")
            self.lbl_feedback.setStyleSheet("color:#EF4444;font-size:14px;font-weight:600;")

        for i, btn in enumerate(self.option_btns):
            if i != idx and i != correct:
                btn.apply_style("dim")
            btn.setEnabled(False)

        self.lbl_score.setText(f"Đúng: {self.score}")
        self.btn_next.setVisible(True)

    def _on_next(self):
        self.index += 1
        self._show_question()


# ================================================================
# MAIN FLASHCARD WIDGET
# Stack index:
#   0 — Trang chính (tab Flashcard cá nhân / Từ khóa học)
#   1 — QuizWidget đang làm bài
#   2 — Loading AI
# ================================================================
class FlashcardWidget(QWidget):
    def __init__(self, controller, user_id: int):
        super().__init__()
        self.controller = controller
        self.user_id = user_id
        self.current_deck_id = None
        self._current_parent_deck_id = None   # deck cha đang xem (màn lesson list)

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.stack = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)

        self._init_page_main()       # index 0 — trang chính có 2 tab
        self._init_page_loading()    # index 1 — loading AI (di chuyển lên 1)

        self.stack.setCurrentIndex(0)
        self._load_my_decks()

    # ================================================================
    # PAGE 0 — TRANG CHÍNH (2 tab)
    # ================================================================
    def _init_page_main(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(32, 24, 32, 24)
        outer.setSpacing(0)

        # ── Tiêu đề ──
        self.lbl_title = QLabel(tr("flash_title"))
        self.lbl_title.setStyleSheet("font-size:24px;font-weight:bold;color:#1E2328;")
        self.lbl_sub = QLabel(tr("flash_subtitle"))
        self.lbl_sub.setStyleSheet("font-size:14px;color:#6F767E;margin-bottom:16px;")
        outer.addWidget(self.lbl_title)
        outer.addWidget(self.lbl_sub)

        # ── Tab bar ──
        tab_bar = QHBoxLayout()
        tab_bar.setSpacing(0)
        tab_bar.setContentsMargins(0, 0, 0, 0)

        self.btn_tab_my = QPushButton("📝  Flashcard của tôi")
        self.btn_tab_course = QPushButton("📚  Từ khóa học")
        for btn in (self.btn_tab_my, self.btn_tab_course):
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
        self.btn_tab_my.clicked.connect(lambda: self._switch_tab(0))
        self.btn_tab_course.clicked.connect(lambda: self._switch_tab(1))

        tab_bar.addWidget(self.btn_tab_my)
        tab_bar.addWidget(self.btn_tab_course)
        tab_bar.addStretch()
        outer.addLayout(tab_bar)

        # ── Tab content stack ──
        self.tab_stack = QStackedWidget()
        outer.addWidget(self.tab_stack, stretch=1)

        self._init_tab_my_decks()       # tab_stack index 0
        self._init_tab_course_decks()   # tab_stack index 1

        self._switch_tab(0)
        self.stack.addWidget(page)

    def _tab_btn_style(self, active: bool) -> str:
        if active:
            return """
                QPushButton {
                    background:#2D60FF;color:white;
                    border-radius:0;border-bottom:3px solid #1A4FE0;
                    font-size:13px;font-weight:bold;padding:0 20px;
                }
            """
        return """
            QPushButton {
                background:transparent;color:#6F767E;
                border-radius:0;border-bottom:2px solid #EDEDED;
                font-size:13px;font-weight:500;padding:0 20px;
            }
            QPushButton:hover { color:#2D60FF; }
        """

    def _switch_tab(self, idx: int):
        self.tab_stack.setCurrentIndex(idx)
        self.btn_tab_my.setStyleSheet(self._tab_btn_style(idx == 0))
        self.btn_tab_course.setStyleSheet(self._tab_btn_style(idx == 1))
        if idx == 0:
            self._load_my_decks()
        else:
            self._load_course_decks()

    # ── TAB 0: Flashcard của tôi ──────────────────────────────────
    def _init_tab_my_decks(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)

        # Nút tạo mới
        actions = QHBoxLayout()
        actions.setSpacing(12)
        self.btn_file = QPushButton("📁 Tạo từ File (PDF/Docx)")
        self.btn_file.setFixedHeight(44)
        self.btn_file.setCursor(Qt.PointingHandCursor)
        self.btn_file.setStyleSheet(self._action_btn_style("#2D60FF", "white"))
        self.btn_file.clicked.connect(self._on_create_from_file)

        self.btn_topic = QPushButton("💡 Tạo từ Chủ đề/Prompt")
        self.btn_topic.setFixedHeight(44)
        self.btn_topic.setCursor(Qt.PointingHandCursor)
        self.btn_topic.setStyleSheet(self._action_btn_style("#F0F4FF", "#2D60FF"))
        self.btn_topic.clicked.connect(self._on_create_from_topic)

        actions.addWidget(self.btn_file)
        actions.addWidget(self.btn_topic)
        layout.addLayout(actions)

        # Danh sách deck
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none;background:transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background:transparent;")
        self.my_decks_layout = QVBoxLayout(scroll_content)
        self.my_decks_layout.setContentsMargins(0, 4, 0, 4)
        self.my_decks_layout.setSpacing(12)
        self.my_decks_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, stretch=1)

        self.no_deck_label = QLabel("Chưa có bộ câu hỏi nào. Hãy tạo mới bằng AI ở trên nhé!")
        self.no_deck_label.setAlignment(Qt.AlignCenter)
        self.no_deck_label.setStyleSheet("color:#9BA3AF;font-size:14px;margin-top:40px;")
        self.my_decks_layout.insertWidget(0, self.no_deck_label)

        self.tab_stack.addWidget(page)

    def _load_my_decks(self):
        """
        Tải decks từ mục Flashcard cá nhân (file + AI).
        FIX: Chỉ hiển thị source != 'course' — không lẫn với deck khóa học.
        """
        # Xóa decks cũ
        for i in range(self.my_decks_layout.count() - 1, -1, -1):
            item = self.my_decks_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.no_deck_label:
                item.widget().deleteLater()

        # FIX: Dùng get_user_decks thay vì get_decks để lọc đúng
        if hasattr(self.controller, 'get_user_decks'):
            decks = self.controller.get_user_decks(self.user_id) or []
        else:
            # Fallback nếu controller cũ chưa có hàm này
            all_decks = self.controller.get_decks(self.user_id) or []
            decks = [d for d in all_decks if d.get("source") != "course"]

        if not decks:
            self.no_deck_label.show()
            return

        self.no_deck_label.hide()
        for d in decks:
            card = DeckCard(d, on_open=self._on_open_my_deck, on_delete=self._on_delete_deck)
            self.my_decks_layout.insertWidget(self.my_decks_layout.count() - 1, card)

    def _on_open_my_deck(self, deck: dict):
        self.current_deck_id = deck.get("id")
        cards = self.controller.get_flashcards(self.user_id, self.current_deck_id)

        if not cards:
            QMessageBox.warning(self, "Thông báo", "Bộ câu hỏi này hiện tại chưa có dữ liệu thẻ.")
            return

        self._open_quiz(cards, deck.get("title", "Luyện tập"))

    # ── TAB 1: Từ khóa học ───────────────────────────────────────
    def _init_tab_course_decks(self):
        """
        Tab này có 2 màn xếp chồng:
          inner_stack index 0 — Danh sách khóa học (deck cha)
          inner_stack index 1 — Danh sách bài học (deck con) của khóa học đã chọn
        """
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 16, 0, 0)
        outer.setSpacing(0)

        self.course_inner_stack = QStackedWidget()
        outer.addWidget(self.course_inner_stack, stretch=1)

        # Inner 0: danh sách khóa học
        self._init_course_list_page()
        # Inner 1: danh sách bài học của khóa học đã chọn
        self._init_lesson_list_page()

        self.tab_stack.addWidget(page)

    def _init_course_list_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        lbl = QLabel("Chọn khóa học để ôn tập flashcard:")
        lbl.setStyleSheet("font-size:14px;color:#374151;font-weight:600;")
        layout.addWidget(lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none;background:transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background:transparent;")
        self.course_decks_layout = QVBoxLayout(scroll_content)
        self.course_decks_layout.setContentsMargins(0, 4, 0, 4)
        self.course_decks_layout.setSpacing(12)
        self.course_decks_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, stretch=1)

        self.no_course_deck_label = QLabel(
            "Chưa có flashcard từ khóa học nào.\n"
            "Vào mục Khóa học → chọn bài học → nhấn nút Flashcard để tạo."
        )
        self.no_course_deck_label.setAlignment(Qt.AlignCenter)
        self.no_course_deck_label.setWordWrap(True)
        self.no_course_deck_label.setStyleSheet("color:#9BA3AF;font-size:13px;margin-top:40px;")
        self.course_decks_layout.insertWidget(0, self.no_course_deck_label)

        self.course_inner_stack.addWidget(page)

    def _init_lesson_list_page(self):
        """Màn hiển thị các bài học (sub-deck) của 1 khóa học đã chọn."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header với nút Back
        header = QHBoxLayout()
        self.btn_back_to_courses = QPushButton("← Quay lại")
        self.btn_back_to_courses.setCursor(Qt.PointingHandCursor)
        self.btn_back_to_courses.setStyleSheet("""
            QPushButton {
                background:transparent;color:#2D60FF;
                border:none;font-size:13px;font-weight:600;
            }
            QPushButton:hover { color:#1A4FE0; }
        """)
        self.btn_back_to_courses.clicked.connect(
            lambda: self.course_inner_stack.setCurrentIndex(0)
        )

        self.lbl_course_deck_title = QLabel()
        self.lbl_course_deck_title.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#1E2328;"
        )

        header.addWidget(self.btn_back_to_courses)
        header.addSpacing(8)
        header.addWidget(self.lbl_course_deck_title)
        header.addStretch()
        layout.addLayout(header)

        lbl_hint = QLabel("Chọn bài học để bắt đầu làm bài:")
        lbl_hint.setStyleSheet("font-size:13px;color:#6F767E;")
        layout.addWidget(lbl_hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none;background:transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background:transparent;")
        self.lesson_decks_layout = QVBoxLayout(scroll_content)
        self.lesson_decks_layout.setContentsMargins(0, 4, 0, 4)
        self.lesson_decks_layout.setSpacing(12)
        self.lesson_decks_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, stretch=1)

        self.no_lesson_deck_label = QLabel("Chưa có bài học nào trong khóa học này.")
        self.no_lesson_deck_label.setAlignment(Qt.AlignCenter)
        self.no_lesson_deck_label.setStyleSheet("color:#9BA3AF;font-size:13px;margin-top:40px;")
        self.lesson_decks_layout.insertWidget(0, self.no_lesson_deck_label)

        self.course_inner_stack.addWidget(page)

    def _load_course_decks(self):
        """Tải danh sách deck cha (đại diện cho từng khóa học)."""
        for i in range(self.course_decks_layout.count() - 1, -1, -1):
            item = self.course_decks_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.no_course_deck_label:
                item.widget().deleteLater()

        # FIX: Dùng get_course_decks (chỉ lấy deck cha source='course', parent_id IS NULL)
        if hasattr(self.controller, 'get_course_decks'):
            decks = self.controller.get_course_decks(self.user_id) or []
        else:
            all_decks = self.controller.get_decks(self.user_id) or []
            decks = [
                d for d in all_decks
                if d.get("source") == "course" and d.get("parent_id") is None
            ]

        if not decks:
            self.no_course_deck_label.show()
            self.course_inner_stack.setCurrentIndex(0)
            return

        self.no_course_deck_label.hide()
        for d in decks:
            card = DeckCard(
                d,
                on_open=self._on_open_course_deck,
                on_delete=self._on_delete_deck
            )
            self.course_decks_layout.insertWidget(
                self.course_decks_layout.count() - 1, card
            )

    def _on_open_course_deck(self, deck: dict):
        """Nhấn vào khóa học → hiển thị danh sách bài học (sub-deck)."""
        parent_id = deck.get("id")
        self._current_parent_deck_id = parent_id
        self.lbl_course_deck_title.setText(deck.get("title", "Khóa học"))

        # Xóa bài học cũ
        for i in range(self.lesson_decks_layout.count() - 1, -1, -1):
            item = self.lesson_decks_layout.itemAt(i)
            if item and item.widget() and item.widget() != self.no_lesson_deck_label:
                item.widget().deleteLater()

        # Lấy sub-decks (bài học)
        if hasattr(self.controller, 'get_sub_decks'):
            sub_decks = self.controller.get_sub_decks(self.user_id, parent_id) or []
        else:
            sub_decks = []

        if not sub_decks:
            self.no_lesson_deck_label.show()
        else:
            self.no_lesson_deck_label.hide()
            for sd in sub_decks:
                card = DeckCard(
                    sd,
                    on_open=self._on_open_lesson_deck,
                    on_delete=self._on_delete_deck
                )
                self.lesson_decks_layout.insertWidget(
                    self.lesson_decks_layout.count() - 1, card
                )

        self.course_inner_stack.setCurrentIndex(1)

    def _on_open_lesson_deck(self, deck: dict):
        """Nhấn vào bài học → mở QuizWidget với flashcard của bài học đó."""
        self.current_deck_id = deck.get("id")
        cards = self.controller.get_flashcards(self.user_id, self.current_deck_id)

        if not cards:
            QMessageBox.warning(
                self, "Thông báo",
                "Bài học này chưa có flashcard.\n"
                "Vào Khóa học → bài học đó → nhấn nút Flashcard để tạo."
            )
            return

        self._open_quiz(cards, deck.get("title", "Luyện tập"))

    # ================================================================
    # QUIZ — dùng chung cho cả 2 tab
    # ================================================================
    def _open_quiz(self, cards: list, title: str):
        quiz = QuizWidget(cards, title)
        quiz.finished.connect(self._on_quiz_finished)

        # Dọn dẹp widget cũ ở slot index 1
        if self.stack.count() > 1:
            old_w = self.stack.widget(1)
            self.stack.removeWidget(old_w)
            old_w.deleteLater()

        self.stack.insertWidget(1, quiz)
        self.stack.setCurrentIndex(1)

    def _on_quiz_finished(self, score: int, total: int):
        if self.current_deck_id:
            if hasattr(self.controller, 'complete_sub_deck'):
                self.controller.complete_sub_deck(self.current_deck_id)
            elif hasattr(self.controller, 'set_deck_completed'):
                self.controller.set_deck_completed(self.current_deck_id)

        QMessageBox.information(
            self, "Kết quả học tập",
            f"🎉 Chúc mừng bạn đã hoàn thành!\nKết quả: {score}/{total} câu trả lời đúng."
        )
        self.stack.setCurrentIndex(0)
        # Reload tab đang hiển thị
        if self.tab_stack.currentIndex() == 0:
            self._load_my_decks()
        else:
            self._load_course_decks()

    # ================================================================
    # PAGE 1 — LOADING AI
    # ================================================================
    def _init_page_loading(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        lbl_loading = QLabel("🤖")
        lbl_loading.setStyleSheet("font-size:48px;background:transparent;")
        self.lbl_loading_text = QLabel("EduFlow AI đang phân tích dữ liệu và đóng gói câu hỏi...")
        self.lbl_loading_text.setStyleSheet("font-size:15px;font-weight:600;color:#1E2328;")

        layout.addWidget(lbl_loading, alignment=Qt.AlignCenter)
        layout.addWidget(self.lbl_loading_text, alignment=Qt.AlignCenter)
        self.stack.addWidget(page)  # index 1 (sau page_main)

    # ================================================================
    # TẠO FLASHCARD TỪ FILE / TOPIC
    # ================================================================
    def _on_create_from_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Chọn tài liệu học tập", "", "Tài liệu (*.pdf *.docx)"
        )
        if not path:
            return

        title, ok = QInputDialog.getText(
            self, "Đặt tên bộ học tập", "Nhập tên cho bộ câu hỏi mới:"
        )
        if not ok or not title.strip():
            title = "Tài liệu từ File"

        self.stack.setCurrentIndex(1)  # loading page

        try:
            from src.services.ai_engine import AIEngine
            engine = AIEngine()
            text_content = engine.read_file(path)
            if "❌" in text_content:
                raise ValueError(text_content)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi đọc file", f"Không thể trích xuất văn bản:\n{e}")
            self.stack.setCurrentIndex(0)
            return

        self.worker = AIWorker(self.controller, "file", text_content)
        self.worker.finished.connect(lambda cards: self._save_ai_deck(title, cards))
        self.worker.error.connect(self._on_ai_error)
        self.worker.start()

    def _on_create_from_topic(self):
        dialog = PromptDialog(self)
        if dialog.exec() == QDialog.Accepted:
            title = dialog.get_title()
            prompt = dialog.get_prompt()

            self.stack.setCurrentIndex(1)  # loading page
            self.worker = AIWorker(self.controller, "topic", prompt)
            self.worker.finished.connect(lambda cards: self._save_ai_deck(title, cards))
            self.worker.error.connect(self._on_ai_error)
            self.worker.start()

    def _save_ai_deck(self, title: str, cards: list):
        deck_id, saved_count = self.controller._save_deck(
            self.user_id, title, cards, source="ai"
        )
        QMessageBox.information(
            self, "Thành công",
            f"Đã khởi tạo bộ bài '{title}' với {saved_count} câu hỏi trắc nghiệm."
        )
        self.stack.setCurrentIndex(0)
        self._load_my_decks()

    def _on_ai_error(self, err_msg: str):
        QMessageBox.critical(self, "Lỗi kết nối AI", f"Không thể sinh câu hỏi tự động:\n{err_msg}")
        self.stack.setCurrentIndex(0)

    # ================================================================
    # DELETE (dùng chung)
    # ================================================================
    def _on_delete_deck(self, deck: dict):
        ans = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa bộ câu hỏi '{deck.get('title')}' không?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            self.controller.delete_deck(deck.get("id"))
            # Reload tab hiện tại
            if self.tab_stack.currentIndex() == 0:
                self._load_my_decks()
            else:
                # Nếu đang ở màn bài học, reload lại màn đó
                if self.course_inner_stack.currentIndex() == 1 and self._current_parent_deck_id:
                    # Reload sub-decks của khóa học cha
                    fake_deck = {"id": self._current_parent_deck_id}
                    self._on_open_course_deck(fake_deck)
                else:
                    self._load_course_decks()

    # ================================================================
    # MISC
    # ================================================================
    def _action_btn_style(self, bg: str, fg: str) -> str:
        return f"""
            QPushButton {{
                background:{bg}; color:{fg}; border-radius:12px;
                font-size:13px; font-weight:bold; border:none; padding:0 16px;
            }}
            QPushButton:hover {{ opacity:0.85; }}
        """

    def _retranslate(self):
        self.lbl_title.setText(tr("flash_title"))
        self.lbl_sub.setText(tr("flash_subtitle"))

    def set_ai_limit(self, limit: int):
        self.ai_limit = limit
        print(f"⚙️ FlashcardWidget updated AI limit to: {limit}")