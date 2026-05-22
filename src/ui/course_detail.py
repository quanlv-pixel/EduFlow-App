from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar,
    QStackedLayout, QMessageBox, QScrollArea,
    QSizePolicy, QGridLayout, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, QSize, Signal, QUrl, QThread
from PySide6.QtGui import QFont, QCursor, QDesktopServices
from src.ui.settings_widget import LanguageManager, tr


# ================================================================
# WORKER 1 — Tải bài học YouTube từ playlist (chạy ngầm)
# ================================================================
class LessonLoaderWorker(QThread):
    finished = Signal(list)
    error    = Signal(str)

    def __init__(self, controller, course_id):
        super().__init__()
        self.controller = controller
        self.course_id  = course_id

    def run(self):
        try:
            lessons = self.controller.get_lessons(self.course_id)
            self.finished.emit(lessons or [])
        except Exception as e:
            self.error.emit(str(e))


# ================================================================
# WORKER 2 — Gọi Gemini AI sinh cẩm nang học Web (chạy ngầm)
# ================================================================
class WebTutorialWorker(QThread):
    finished = Signal(str)
    error    = Signal(str)

    def __init__(self, controller, source_platform, course_name):
        super().__init__()
        self.controller      = controller
        self.source_platform = source_platform
        self.course_name     = course_name

    def run(self):
        try:
            text = self.controller.get_course_tutorial(
                self.source_platform, self.course_name
            )
            self.finished.emit(text or "")
        except Exception as e:
            self.error.emit(str(e))


# ================= BADGE DIALOG (hiện khi đạt 100%) =================
class BadgeDialog(QDialog):

    def __init__(self, course_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("badge_title"))
        self.setFixedSize(420, 360)
        self.setStyleSheet("background: #FFFFFF; border-radius: 20px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignCenter)

        medal = QLabel("🏅")
        medal.setAlignment(Qt.AlignCenter)
        medal.setStyleSheet("font-size: 72px; background: transparent;")
        layout.addWidget(medal)

        title = QLabel(tr("badge_congrats"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px; font-weight: bold;
            color: #1E2328; background: transparent;
        """)
        layout.addWidget(title)

        msg = QLabel(tr("badge_msg", course_name=course_name))
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("""
            font-size: 14px; color: #6F767E;
            background: transparent; line-height: 1.6;
        """)
        layout.addWidget(msg)

        badge = QLabel(tr("badge_certificate"))
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet("""
            background: #ECFDF5; color: #10B981;
            border-radius: 12px; padding: 8px 20px;
            font-size: 13px; font-weight: 600;
        """)
        layout.addWidget(badge)

        layout.addSpacing(6)

        btn_close = QPushButton(tr("badge_btn"))
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setFixedHeight(44)
        btn_close.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2D60FF, stop:1 #5B8BFF);
                color: white; border-radius: 12px;
                font-size: 15px; font-weight: bold; border: none;
            }
            QPushButton:hover { background: #1A4FE0; }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


# ================= LESSON ITEM =================
class LessonItem(QFrame):
    completed_changed = Signal(int, bool)   # (lesson_id, is_done)

    def __init__(self, lesson: dict, on_flashcard):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.lesson   = lesson
        self.is_done  = bool(lesson.get("completed", False))
        self._on_flashcard = on_flashcard   # lưu callback để không bị None

        self._is_youtube = lesson.get("is_youtube", False) or (
            "youtube" in lesson.get("url", "").lower() or
            "youtube" in lesson.get("source", "").lower()
        )
        self._video_id = lesson.get("video_id")
        self._url      = lesson.get("url", "")
        self._source   = lesson.get("source", "")

        self.setObjectName("LessonCard")
        self.setFixedHeight(72 if not self._is_youtube else 64)
        self._apply_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # ── Checkbox toggle ──────────────────────────────────────
        self.check_btn = QPushButton()
        self.check_btn.setFixedSize(28, 28)
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self.check_btn.setStyleSheet(
            "border: none; background: transparent; font-size: 18px;"
        )
        self.check_btn.clicked.connect(self._toggle_done)
        self._update_check_icon()

        # ── Title + meta ─────────────────────────────────────────
        info_v = QVBoxLayout()
        info_v.setSpacing(2)
        info_v.setContentsMargins(0, 0, 0, 0)

        self.lbl_title = QLabel(self._build_title())
        self.lbl_title.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #1E2328; background: transparent;"
        )

        self.lbl_meta = QLabel(self._build_meta())
        self.lbl_meta.setStyleSheet(
            "font-size: 11px; color: #9BA3AF; background: transparent;"
        )

        info_v.addWidget(self.lbl_title)
        info_v.addWidget(self.lbl_meta)

        if not self._is_youtube:
            chapter = lesson.get("web_chapter", "")
            if chapter:
                lbl_chapter = QLabel(chapter)
                lbl_chapter.setStyleSheet(
                    "font-size: 11px; color: #2D60FF; "
                    "background: transparent; font-weight: 500;"
                )
                info_v.addWidget(lbl_chapter)

        layout.addWidget(self.check_btn)
        layout.addLayout(info_v)
        layout.addStretch()

        # ── Nút hành động chính ──────────────────────────────────
        if self._is_youtube:
            self.btn_play = QPushButton(f"▶  {tr('lesson_watch_youtube')}")
            self.btn_play.setCursor(Qt.PointingHandCursor)
            self.btn_play.setFixedHeight(32)
            self.btn_play.setStyleSheet("""
                QPushButton {
                    background: #FF0000; color: white;
                    border-radius: 8px; padding: 0 14px;
                    font-size: 12px; font-weight: bold; border: none;
                }
                QPushButton:hover { background: #CC0000; }
            """)
            self.btn_play.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(self._url))
            )
            layout.addWidget(self.btn_play)

        elif self._url:
            source_short = self._source or "Web"
            self.btn_open = QPushButton(
                f"🔗  {tr('lesson_learn_on', source=source_short)}"
            )
            self.btn_open.setCursor(Qt.PointingHandCursor)
            self.btn_open.setFixedHeight(32)
            self.btn_open.setStyleSheet("""
                QPushButton {
                    background: #F3F4F6; color: #374151;
                    border-radius: 8px; padding: 0 12px;
                    font-size: 12px; font-weight: 600; border: none;
                }
                QPushButton:hover { background: #E5E7EB; }
            """)
            self.btn_open.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(self._url))
            )
            layout.addWidget(self.btn_open)

        # ── Nút Flashcard ────────────────────────────────────────
        btn_flash = QPushButton(tr("lesson_flash_btn"))
        btn_flash.setCursor(Qt.PointingHandCursor)
        btn_flash.setFixedHeight(32)
        btn_flash.setStyleSheet("""
            QPushButton {
                background-color: #2D60FF; color: white;
                border-radius: 8px; padding: 0 14px;
                font-size: 12px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #1A4FE0; }
        """)
        # FIX: không để None — dùng self._on_flashcard đã lưu
        btn_flash.clicked.connect(lambda: self._on_flashcard(self.lesson))
        layout.addWidget(btn_flash)

    # ── Toggle done / undone ─────────────────────────────────────
    def _toggle_done(self):
        self.is_done = not self.is_done
        self._update_check_icon()
        self._apply_style()
        lesson_id = self.lesson.get("id")
        if lesson_id is not None:
            self.completed_changed.emit(lesson_id, self.is_done)

    def _update_check_icon(self):
        self.check_btn.setText("✅" if self.is_done else "⬜")

    def _apply_style(self):
        bg     = "#F0FDF4" if self.is_done else "#FFFFFF"
        border = "#6EE7B7" if self.is_done else "#EDEDED"
        self.setStyleSheet(f"""
            QFrame#LessonCard {{
                background: {bg};
                border-radius: 12px;
                border: 1px solid {border};
            }}
        """)

    def _build_title(self) -> str:
        key          = self.lesson.get("topic_key")
        course_title = self.lesson.get("course_title", "")
        if key:
            text = tr(key)
        else:
            title = self.lesson.get("title", "")
            mapping = {
                "lesson intro":         "lesson_intro",
                "lesson basic":         "lesson_basic",
                "lesson core":          "lesson_core",
                "lesson examples":      "lesson_examples",
                "lesson demo":          "lesson_demo",
                "lesson exercise":      "lesson_exercise",
                "lesson advanced":      "lesson_advanced",
                "lesson debug":         "lesson_debug",
                "lesson best practice": "lesson_best_practice",
                "lesson summary":       "lesson_summary",
            }
            text = tr(mapping.get(title, title))
        return f"{text} — {course_title}" if course_title else text

    def _build_meta(self) -> str:
        minutes  = self.lesson.get("minutes")
        duration = tr("lesson_duration", minutes=minutes) if minutes is not None else self.lesson.get("duration", "")
        type_lbl = self.lesson.get("type", "Online")
        source   = self.lesson.get("source", "")
        meta     = f"{duration}  •  {type_lbl}"
        if source:
            meta += f"  •  {source}"
        return meta

    def _retranslate(self):
        self.lbl_title.setText(self._build_title())
        self.lbl_meta.setText(self._build_meta())
        if hasattr(self, "btn_play"):
            self.btn_play.setText(f"▶  {tr('lesson_watch_youtube')}")
        if hasattr(self, "btn_open"):
            source_short = self._source or "Web"
            self.btn_open.setText(f"🔗  {tr('lesson_learn_on', source=source_short)}")


# ================= RESOURCE LINK ITEM =================
class ResourceItem(QWidget):
    def __init__(self, title, url):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(2)

        top = QHBoxLayout()
        icon = QLabel("🔗")
        icon.setStyleSheet("font-size: 13px; background: transparent;")

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #2D60FF; background: transparent;"
        )
        lbl_title.setCursor(Qt.PointingHandCursor)
        lbl_title.mousePressEvent = lambda _: QDesktopServices.openUrl(QUrl(url))

        top.addWidget(icon)
        top.addWidget(lbl_title)
        top.addStretch()

        lbl_url = QLabel(url)
        lbl_url.setStyleSheet("font-size: 11px; color: #6F767E; background: transparent;")

        layout.addLayout(top)
        layout.addWidget(lbl_url)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #EDEDED; background: #EDEDED; border: none; max-height: 1px;")
        layout.addWidget(sep)


# ================= COURSE DETAIL =================
class CourseDetailWidget(QWidget):
    def __init__(self, controller, user_id=None):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.controller  = controller
        self.user_id     = user_id
        self.course_id   = None
        self.course_data = None

        # Giữ reference Worker để không bị garbage collected
        self._lesson_worker   = None
        self._tutorial_worker = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── BACK BUTTON ──
        self.back_btn = QPushButton()
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #6F767E;
                border: none; font-size: 13px; font-weight: 500;
                text-align: left; padding: 0 0 18px 0;
            }
            QPushButton:hover { color: #2D60FF; }
        """)
        main_layout.addWidget(self.back_btn)

        # ── BODY: 2-COLUMN ──
        body = QHBoxLayout()
        body.setSpacing(24)
        body.setContentsMargins(0, 0, 0, 0)

        # ── LEFT COLUMN ──
        left = QVBoxLayout()
        left.setSpacing(18)

        # Course header card
        self.header_card = QFrame()
        self.header_card.setObjectName("CardWhite")
        self.header_card.setStyleSheet("""
            QFrame#CardWhite {
                background: #FFFFFF; border-radius: 20px;
                border: 1px solid #EDEDED;
            }
        """)
        header_card_layout = QVBoxLayout(self.header_card)
        header_card_layout.setContentsMargins(28, 24, 28, 24)
        header_card_layout.setSpacing(10)

        title_row = QHBoxLayout()
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("""
            font-size: 26px; font-weight: bold;
            color: #1E2328; background: transparent;
        """)

        self.lbl_code_badge = QLabel()
        self.lbl_code_badge.setStyleSheet("""
            background: #EEF2FF; color: #2D60FF;
            border-radius: 8px; padding: 3px 12px;
            font-size: 12px; font-weight: 600;
        """)

        self.lbl_status_badge = QLabel()
        self.lbl_status_badge.setStyleSheet("""
            background: #ECFDF5; color: #10B981;
            border-radius: 12px; padding: 4px 14px;
            font-size: 12px; font-weight: 600;
        """)

        title_row.addWidget(self.lbl_title)
        title_row.addWidget(self.lbl_code_badge)
        title_row.addStretch()
        title_row.addWidget(self.lbl_status_badge)

        self.lbl_prof = QLabel()
        self.lbl_prof.setStyleSheet(
            "color: #6F767E; font-size: 13px; font-style: italic; background: transparent;"
        )

        self.lbl_desc_title = QLabel()
        self.lbl_desc_title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #1E2328; background: transparent;"
        )

        self.lbl_desc = QLabel()
        self.lbl_desc.setStyleSheet("color: #6F767E; font-size: 13px; background: transparent;")
        self.lbl_desc.setWordWrap(True)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(30)
        self.stat_lessons   = self._make_stat("lessons",   "📺", tr("stat_lessons"),   "0")
        self.stat_exercises = self._make_stat("exercises", "✅", tr("stat_exercises"), "0")
        self.stat_progress  = self._make_stat("progress",  "🔵", tr("stat_progress"),  "0%")
        stats_row.addLayout(self.stat_lessons)
        stats_row.addLayout(self.stat_exercises)
        stats_row.addLayout(self.stat_progress)
        stats_row.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: none; background-color: #EEF0F4; border-radius: 4px; }
            QProgressBar::chunk { background-color: #2D60FF; border-radius: 4px; }
        """)

        header_card_layout.addLayout(title_row)
        header_card_layout.addWidget(self.lbl_prof)
        header_card_layout.addSpacing(4)
        header_card_layout.addWidget(self.lbl_desc_title)
        header_card_layout.addWidget(self.lbl_desc)
        header_card_layout.addSpacing(8)
        header_card_layout.addLayout(stats_row)
        header_card_layout.addWidget(self.progress_bar)
        left.addWidget(self.header_card)

        # Lessons card
        lessons_card = QFrame()
        lessons_card.setObjectName("CardWhite")
        lessons_card.setStyleSheet("""
            QFrame#CardWhite {
                background: #FFFFFF; border-radius: 20px;
                border: 1px solid #EDEDED;
            }
        """)
        lessons_card_layout = QVBoxLayout(lessons_card)
        lessons_card_layout.setContentsMargins(20, 18, 20, 18)
        lessons_card_layout.setSpacing(10)

        self.lbl_content = QLabel()
        self.lbl_content.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #1E2328; background: transparent;"
        )
        lessons_card_layout.addWidget(self.lbl_content)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")

        self.layout_lessons = QVBoxLayout(scroll_content)
        self.layout_lessons.setContentsMargins(0, 0, 0, 0)
        self.layout_lessons.setSpacing(8)
        self.layout_lessons.addStretch()

        scroll.setWidget(scroll_content)
        lessons_card_layout.addWidget(scroll)
        left.addWidget(lessons_card, stretch=1)

        # ── RIGHT COLUMN ──
        right = QVBoxLayout()
        right.setSpacing(18)
        right.setAlignment(Qt.AlignTop)

        res_card = QFrame()
        res_card.setObjectName("CardWhite")
        res_card.setFixedWidth(280)
        res_card.setStyleSheet("""
            QFrame#CardWhite {
                background: #FFFFFF; border-radius: 20px;
                border: 1px solid #EDEDED;
            }
        """)
        res_layout = QVBoxLayout(res_card)
        res_layout.setContentsMargins(20, 18, 20, 18)
        res_layout.setSpacing(0)

        lbl_ext = QLabel("🔗")
        lbl_ext.setStyleSheet("font-size: 18px; background: transparent;")
        res_layout.addWidget(lbl_ext)
        res_layout.addSpacing(8)

        self.res_container = QVBoxLayout()
        res_layout.addLayout(self.res_container)

        self.lbl_pop = QLabel()
        self.lbl_pop.setStyleSheet(
            "font-size: 10px; color: #9BA3AF; font-weight: 700; "
            "letter-spacing: 1px; background: transparent;"
        )
        res_layout.addSpacing(12)
        res_layout.addWidget(self.lbl_pop)

        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(6)
        for tag in ["W3Schools", "Coursera", "Study4", "EdX"]:
            t = QLabel(tag)
            t.setStyleSheet("""
                background: #F3F4F6; color: #6F767E;
                border-radius: 6px; padding: 3px 8px; font-size: 11px;
            """)
            tags_layout.addWidget(t)
        tags_layout.addStretch()
        res_layout.addLayout(tags_layout)

        cta_card = QFrame()
        cta_card.setFixedWidth(280)
        cta_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2D60FF, stop:1 #5B8BFF);
                border-radius: 20px;
            }
        """)
        cta_layout = QVBoxLayout(cta_card)
        cta_layout.setContentsMargins(20, 20, 20, 20)
        cta_layout.setSpacing(10)

        self.lbl_cta_title = QLabel()
        self.lbl_cta_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: white; background: transparent;"
        )
        self.lbl_cta_desc = QLabel()
        self.lbl_cta_desc.setStyleSheet(
            "font-size: 12px; color: rgba(255,255,255,0.85); background: transparent;"
        )
        self.lbl_cta_desc.setWordWrap(True)

        self.btn_cta = QPushButton()
        self.btn_cta.setCursor(Qt.PointingHandCursor)
        self.btn_cta.setStyleSheet("""
            QPushButton {
                background: white; color: #2D60FF;
                border-radius: 10px; padding: 10px 16px;
                font-size: 13px; font-weight: bold; border: none;
            }
            QPushButton:hover { background: #F0F4FF; }
        """)

        cta_layout.addWidget(self.lbl_cta_title)
        cta_layout.addWidget(self.lbl_cta_desc)
        cta_layout.addWidget(self.btn_cta)

        right.addWidget(res_card)
        right.addWidget(cta_card)

        body.addLayout(left, stretch=1)
        body.addLayout(right)
        main_layout.addLayout(body)

        self._retranslate()

    # ================================================================
    # HELPERS
    # ================================================================
    def _make_stat(self, key, icon_text, label, value):
        lay = QVBoxLayout()
        lay.setSpacing(2)
        row = QHBoxLayout()
        icon = QLabel(icon_text)
        icon.setStyleSheet("font-size: 18px; background: transparent;")
        lbl_label = QLabel(label)
        lbl_label.setStyleSheet(
            "font-size: 10px; color: #9BA3AF; font-weight: 700; "
            "letter-spacing: 0.8px; background: transparent;"
        )
        row.addWidget(icon)
        row.addWidget(lbl_label)
        row.addStretch()
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1E2328; background: transparent;"
        )
        lay.addLayout(row)
        lay.addWidget(lbl_val)
        setattr(self, f"_stat_label_{key}", lbl_label)
        setattr(self, f"_stat_val_{key}",   lbl_val)
        return lay

    def _set_stat(self, key, value):
        w = getattr(self, f"_stat_val_{key}", None)
        if w:
            w.setText(str(value))

    def _clear_lessons(self):
        """Xóa toàn bộ widget bài học, giữ lại stretch cuối."""
        for i in reversed(range(self.layout_lessons.count())):
            item = self.layout_lessons.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

    # ================================================================
    # LOAD COURSE — entry point duy nhất
    # ================================================================
    def load_course(self, course: dict):
        self.course_id   = course.get("id") or course.get("course_id") or course.get("_id")
        self.course_data = course

        self.lbl_title.setText(course.get("name", ""))
        self.lbl_code_badge.setText(course.get("code", ""))
        self.lbl_prof.setText(
            f"{tr('course_detail_professor')} {course.get('professor', '')}"
        )

        desc_key = course.get("description_key")
        self.lbl_desc.setText(tr(desc_key) if desc_key else "")

        # Resources
        for i in reversed(range(self.res_container.count())):
            item = self.res_container.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        for r in course.get("resources", []):
            self.res_container.addWidget(ResourceItem(r["title"], r["url"]))

        self._load_lessons_async()

    # ================================================================
    # LOAD LESSONS — rẽ nhánh Web / YouTube, đều dùng Worker
    # ================================================================
    def _load_lessons_async(self):
        if self.course_id is None:
            return

        self._clear_lessons()

        # Lấy nhanh 1 lesson để biết loại course (Web hay YouTube)
        # Không gọi toàn bộ — chỉ peek row đầu tiên từ DB
        try:
            first_lessons = self.controller.get_lessons(self.course_id)
        except Exception:
            first_lessons = []

        if not first_lessons:
            # Chưa có bài học nào trong DB
            lbl = QLabel(tr("course_detail_no_lessons"))
            lbl.setStyleSheet("color: #9BA3AF; font-size: 13px; background: transparent;")
            self.layout_lessons.insertWidget(0, lbl)
            self._update_stats([])
            return

        url        = first_lessons[0].get("url", "")
        is_youtube = "youtube.com" in url.lower() or "youtu.be" in url.lower()
        is_web     = first_lessons[0].get("is_web_course", False) or (
            "web_route" in str(first_lessons[0].get("topic_key", "")) or
            not is_youtube
        )

        if is_web:
            self._render_web_course(first_lessons[0])
        else:
            self._render_youtube_loading(first_lessons)

    # ── WEB COURSE ────────────────────────────────────────────────
    def _render_web_course(self, lesson: dict):
        if hasattr(self, "btn_cta") and self.btn_cta:
            self.btn_cta.hide()

        source_platform = lesson.get("source", "Web")
        url             = lesson.get("url", "")

        # Frame link
        web_frame = QFrame()
        web_frame.setStyleSheet(
            "background: #F4F7FF; border: 1px dashed #2D60FF; border-radius: 12px;"
        )
        web_box = QVBoxLayout(web_frame)
        web_box.setContentsMargins(16, 16, 16, 16)

        lbl_info = QLabel(
            f"🎯 Khóa học này được tổ chức trực tiếp trên <b>{source_platform}</b>. "
            f"Bạn sẽ học lý thuyết và làm bài tập trực tiếp tại website hệ thống."
        )
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet(
            "font-size: 13px; color: #1E2328; font-weight: 500; background: transparent;"
        )
        web_box.addWidget(lbl_info)

        btn_launch = QPushButton(f"Truy cập khóa học trên {source_platform} 🌐")
        btn_launch.setCursor(Qt.PointingHandCursor)
        btn_launch.setFixedHeight(40)
        btn_launch.setStyleSheet("""
            QPushButton {
                background: #2D60FF; color: white; font-weight: bold;
                border-radius: 8px; border: none; font-size: 13px;
            }
            QPushButton:hover { background: #1A4BDB; }
        """)
        btn_launch.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        web_box.addWidget(btn_launch)

        self.layout_lessons.insertWidget(self.layout_lessons.count() - 1, web_frame)

        # Cẩm nang AI
        lbl_guide_title = QLabel("💡 Cẩm nang hướng dẫn tự học hiệu quả (EduFlow AI):")
        lbl_guide_title.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1E2328; "
            "margin-top: 16px; background: transparent;"
        )
        self.layout_lessons.insertWidget(self.layout_lessons.count() - 1, lbl_guide_title)

        txt_guide = QTextEdit()
        txt_guide.setReadOnly(True)
        txt_guide.setHtml(
            "<i style='color:#6F767E;'>⏳ EduFlow AI đang soạn cẩm nang học tập...</i>"
        )
        txt_guide.setMinimumHeight(200)
        txt_guide.setStyleSheet("""
            QTextEdit {
                background: #FAFAFA; border: 1px solid #E5E7EB;
                border-radius: 10px; padding: 12px;
                font-size: 13px; color: #1E2328;
            }
        """)
        self.layout_lessons.insertWidget(self.layout_lessons.count() - 1, txt_guide)

        # Worker gọi AI ngầm — không đứng hình
        self._tutorial_worker = WebTutorialWorker(
            self.controller,
            source_platform,
            (self.course_data or {}).get("name", "")
        )
        self._tutorial_worker.finished.connect(
            lambda text: txt_guide.setMarkdown(text) if text else None
        )
        self._tutorial_worker.error.connect(
            lambda err: txt_guide.setHtml(
                f"<span style='color:#EF4444;'>Không thể kết nối AI ({err}). "
                f"Hãy bấm nút trên để vào học trực tiếp.</span>"
            )
        )
        self._tutorial_worker.start()

        self._update_stats([lesson])

    # ── YOUTUBE COURSE ────────────────────────────────────────────
    def _render_youtube_loading(self, lessons: list):
        if hasattr(self, "btn_cta") and self.btn_cta:
            self.btn_cta.show()

        # Hiện loading spinner
        lbl_loading = QLabel("⏳ Đang tải danh sách bài học từ YouTube...")
        lbl_loading.setStyleSheet(
            "color: #6F767E; font-size: 13px; font-style: italic; background: transparent;"
        )
        self.layout_lessons.insertWidget(self.layout_lessons.count() - 1, lbl_loading)

        self._update_stats(lessons)

        # Render ngay những gì đã có trong DB (tải nhanh)
        self._render_lesson_list(lessons, lbl_loading)

    def _render_lesson_list(self, lessons: list, lbl_loading=None):
        """Render danh sách LessonItem lên UI."""
        if lbl_loading:
            lbl_loading.deleteLater()

        if not lessons:
            lbl_empty = QLabel(tr("course_detail_no_lessons"))
            lbl_empty.setStyleSheet(
                "color: #9BA3AF; font-size: 13px; background: transparent;"
            )
            self.layout_lessons.insertWidget(self.layout_lessons.count() - 1, lbl_empty)
            return

        for lesson in lessons:
            item = LessonItem(lesson, self.handle_flashcard)
            item.completed_changed.connect(self._on_lesson_completed)
            self.layout_lessons.insertWidget(self.layout_lessons.count() - 1, item)

    def _update_stats(self, lessons: list):
        total     = len(lessons)
        exercises = sum(1 for l in lessons if l.get("has_exercise", False))
        progress  = self.controller.get_progress(self.course_id) if total > 0 else 0

        self._set_stat("lessons",   total)
        self._set_stat("exercises", exercises)
        self._set_stat("progress",  f"{progress}%")
        self.progress_bar.setValue(progress)

        if progress == 100:
            self.lbl_status_badge.setText(tr("course_detail_completed"))
            self.lbl_status_badge.setStyleSheet("""
                background: #ECFDF5; color: #10B981;
                border-radius: 12px; padding: 4px 14px;
                font-size: 12px; font-weight: 600;
            """)
        else:
            self.lbl_status_badge.setText(tr("course_status_learning"))
            self.lbl_status_badge.setStyleSheet("""
                background: #EEF2FF; color: #2D60FF;
                border-radius: 12px; padding: 4px 14px;
                font-size: 12px; font-weight: 600;
            """)

    # ================================================================
    # ACTIONS
    # ================================================================
    def _on_lesson_completed(self, lesson_id: int, is_done: bool):
        self.controller.mark_lesson_done(lesson_id, is_done)
        progress = self.controller.get_progress(self.course_id)
        self._set_stat("progress", f"{progress}%")
        self.progress_bar.setValue(progress)

        if progress == 100:
            self.lbl_status_badge.setText(tr("course_detail_completed"))
            self.lbl_status_badge.setStyleSheet("""
                background: #ECFDF5; color: #10B981;
                border-radius: 12px; padding: 4px 14px;
                font-size: 12px; font-weight: 600;
            """)
            course_name = (self.course_data or {}).get(
                "name", tr("course_detail_this_course")
            )
            BadgeDialog(course_name, self).exec()

    def handle_flashcard(self, lesson: dict):
        """Xử lý tạo Flashcard từ 1 bài học — dùng AI đọc transcript YouTube."""
        if not self.user_id:
            QMessageBox.warning(self, "Lỗi", "Không xác định được người dùng.")
            return

        lesson_title = lesson.get("title", "bài này")
        course_name  = (self.course_data or {}).get("name", "")
        deck_title   = f"{lesson_title}" + (f" — {course_name}" if course_name else "")

        # Kiểm tra deck đã tồn tại chưa
        existing = self.controller.db.execute(
            "SELECT id FROM flashcard_decks WHERE user_id=? AND title=? AND source='course'",
            (self.user_id, deck_title),
            fetch=True
        )
        if existing:
            reply = QMessageBox.question(
                self, "Flashcard đã tồn tại",
                f"Bạn đã tạo flashcard cho bài\n\"{lesson_title}\" rồi.\n\n"
                "Tạo thêm bộ mới hay bỏ qua?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        try:
            cards = self.controller.generate_flashcard_for_lesson(lesson)
            if not cards:
                QMessageBox.information(
                    self, "Flashcard",
                    "Không tạo được flashcard. Vui lòng thử lại."
                )
                return

            lesson_id = lesson.get("id")
            deck_id   = self.controller.db.create_deck(
                self.user_id, deck_title, source="course", lesson_id=lesson_id
            )

            saved = 0
            for c in cards:
                q = c.get("q") or c.get("question", "")
                a = c.get("a") or c.get("answer", "")
                if q and a:
                    self.controller.db.add_flashcard(self.user_id, q, a, deck_id)
                    saved += 1

            QMessageBox.information(
                self, "✅ Đã tạo Flashcard",
                f"Đã tạo {saved} flashcard cho bài\n\"{lesson_title}\".\n\n"
                "Vào mục Khóa học → bài học này để ôn tập,\n"
                "hoặc vào mục Flashcard → 'Từ khóa học' để xem tất cả."
            )

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    # Legacy compat
    def set_course(self, name, code, professor, progress=0):
        self.load_course({
            "id":        getattr(self, "course_id", None),
            "name":      name,
            "code":      code,
            "professor": professor,
            "progress":  progress,
        })

    def _retranslate(self):
        self.back_btn.setText("← " + tr("course_detail_back"))
        self.lbl_content.setText(tr("course_detail_content"))
        self.lbl_status_badge.setText(tr("course_status_learning"))
        self.lbl_cta_desc.setText(tr("course_detail_continue_desc"))
        self.lbl_cta_title.setText(tr("course_detail_continue"))
        self.btn_cta.setText(tr("course_detail_open_latest"))
        self.lbl_pop.setText(tr("course_detail_resources"))
        self.lbl_desc_title.setText(tr("course_detail_description"))
        self._stat_label_lessons.setText(tr("stat_lessons"))
        self._stat_label_exercises.setText(tr("stat_exercises"))
        self._stat_label_progress.setText(tr("stat_progress"))

        if self.course_data:
            self.lbl_prof.setText(
                f"{tr('course_detail_professor')} {self.course_data.get('professor', '')}"
            )
            self._load_lessons_async()