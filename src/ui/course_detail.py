from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar,
    QStackedLayout, QMessageBox, QScrollArea,
    QSizePolicy, QGridLayout, QDialog
)
from PySide6.QtCore import Qt, QSize, Signal, QUrl
from PySide6.QtGui import QFont, QCursor, QDesktopServices
from src.ui.settings_widget import LanguageManager, tr




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

        # Medal emoji lớn
        medal = QLabel("🏅")
        medal.setAlignment(Qt.AlignCenter)
        medal.setStyleSheet("font-size: 72px; background: transparent;")
        layout.addWidget(medal)

        # Tiêu đề
        title = QLabel(tr("badge_congrats"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #1E2328;
            background: transparent;
        """)
        layout.addWidget(title)

        # Nội dung
        msg = QLabel(tr("badge_msg", course_name=course_name))
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("""
            font-size: 14px;
            color: #6F767E;
            background: transparent;
            line-height: 1.6;
        """)
        layout.addWidget(msg)

        # Badge label
        badge = QLabel(tr("badge_certificate"))
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet("""
            background: #ECFDF5;
            color: #10B981;
            border-radius: 12px;
            padding: 8px 20px;
            font-size: 13px;
            font-weight: 600;
        """)
        layout.addWidget(badge)

        layout.addSpacing(6)

        # Nút đóng
        btn_close = QPushButton(tr("badge_btn"))
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setFixedHeight(44)
        btn_close.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2D60FF, stop:1 #5B8BFF);
                color: white;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background: #1A4FE0; }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)



# ================= LESSON ITEM =================
class LessonItem(QFrame):
    completed_changed = Signal(int, bool)  # (lesson_id, is_done)

    def __init__(self, lesson: dict, on_flashcard):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.lesson = lesson
        self.is_done = bool(lesson.get("completed", False))

        # Phát hiện loại nguồn
        self._is_youtube = lesson.get("is_youtube", False) or (
            "youtube" in lesson.get("url", "").lower() or
            "youtube" in lesson.get("source", "").lower()
        )
        self._video_id   = lesson.get("video_id")
        self._url        = lesson.get("url", "")
        self._source     = lesson.get("source", "")

        self.setObjectName("LessonCard")
        # Chiều cao lớn hơn một chút để chứa dòng chú thích
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
        # Dòng meta cơ bản: duration • type
        duration = lesson.get("duration", "")
        type_lbl = lesson.get("type", "")
        meta_parts = [p for p in [duration, type_lbl] if p]
        meta_basic = "  •  ".join(meta_parts)

        self.lbl_meta = QLabel(self._build_meta())
        self.lbl_meta.setStyleSheet(
            "font-size: 11px; color: #9BA3AF; background: transparent;"
        )

        info_v.addWidget(self.lbl_title)
        info_v.addWidget(self.lbl_meta)

        # Dòng chú thích bài học — chỉ hiện với web source
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
            # YouTube → mở trình duyệt
            self.btn_play = QPushButton(f"▶  {tr('lesson_watch_youtube')}")
            self.btn_play.setCursor(Qt.PointingHandCursor)
            self.btn_play.setFixedHeight(32)
            self.btn_play.setStyleSheet("""
                QPushButton {
                    background: #FF0000;
                    color: white;
                    border-radius: 8px;
                    padding: 0 14px;
                    font-size: 12px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover { background: #CC0000; }
            """)
            self.btn_play.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(self._url))
            )
            layout.addWidget(self.btn_play)

        elif self._url:
            # Web source → nút mở browser
            source_short = self._source or "Web"
            self.btn_open = QPushButton(
                f"🔗  {tr('lesson_learn_on', source=source_short)}"
            )
            self.btn_open.setCursor(Qt.PointingHandCursor)
            self.btn_open.setFixedHeight(32)
            self.btn_open.setStyleSheet("""
                QPushButton {
                    background: #F3F4F6;
                    color: #374151;
                    border-radius: 8px;
                    padding: 0 12px;
                    font-size: 12px;
                    font-weight: 600;
                    border: none;
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
                background-color: #2D60FF;
                color: white;
                border-radius: 8px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #1A4FE0; }
        """)
        btn_flash.clicked.connect(lambda: on_flashcard(self.lesson))
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

    # ── Dịch tiêu đề từ topic_key (nếu có), fallback về title đã lưu ──
    def _build_title(self) -> str:
        key = self.lesson.get("topic_key")
        course_title = self.lesson.get("course_title", "")

        # ✅ Ưu tiên topic_key
        if key:
            text = tr(key)
        else:
            # fallback: map từ title sang key
            text = self.lesson.get("title", "")
            mapping = {
                "lesson intro": "lesson_intro",
                "lesson basic": "lesson_basic",
                "lesson core": "lesson_core",
                "lesson examples": "lesson_examples",
                "lesson demo": "lesson_demo",
                "lesson exercise": "lesson_exercise",
                "lesson advanced": "lesson_advanced",
                "lesson debug": "lesson_debug",
                "lesson best practice": "lesson_best_practice",
                "lesson summary": "lesson_summary",
            }
            text = tr(mapping.get(title, title))

        return f"{text} — {course_title}" if course_title else text

    # ── Dịch dòng meta: duration + type + source ────────────────────
    def _build_meta(self) -> str:
        # Hỗ trợ cả '_minutes' (từ lesson_mapper) và 'minutes' (từ DB)
        minutes = self.lesson.get("minutes")

        if minutes is not None:
            duration = tr("lesson_duration", minutes=minutes)
        else:
            duration = self.lesson.get("duration", "")
        type_lbl = self.lesson.get("type", "Online")
        source   = self.lesson.get("source", "")
        meta     = f"{duration}  •  {type_lbl}"
        if source:
            meta += f"  •  {source}"
        return meta
    
    def _retranslate(self):
        # update title
        self.lbl_title.setText(self._build_title())
        self.lbl_meta.setText(self._build_meta())

         # update title + meta
        self.lbl_title.setText(self._build_title())
        self.lbl_meta.setText(self._build_meta())

        # update nút YouTube
        if hasattr(self, "btn_play"):
            self.btn_play.setText(f"▶  {tr('lesson_watch_youtube')}")

        # update nút web source
        if hasattr(self, "btn_open"):
            source_short = self._source or "Web"
            self.btn_open.setText(
                f"🔗  {tr('lesson_learn_on', source=source_short)}"
            )


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
    def __init__(self, controller):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.controller = controller
        self.course_id = None
        self.course_data = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── BACK BUTTON ──
        self.back_btn = QPushButton()
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6F767E;
                border: none;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
                padding: 0 0 18px 0;
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
                background: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #EDEDED;
            }
        """)
        header_card_layout = QVBoxLayout(self.header_card)
        header_card_layout.setContentsMargins(28, 24, 28, 24)
        header_card_layout.setSpacing(10)

        # Title row
        title_row = QHBoxLayout()
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #1E2328;
            background: transparent;
        """)

        self.lbl_code_badge = QLabel()
        self.lbl_code_badge.setStyleSheet("""
            background: #EEF2FF;
            color: #2D60FF;
            border-radius: 8px;
            padding: 3px 12px;
            font-size: 12px;
            font-weight: 600;
        """)

        self.lbl_status_badge = QLabel()
        self.lbl_status_badge.setStyleSheet("""
            background: #ECFDF5;
            color: #10B981;
            border-radius: 12px;
            padding: 4px 14px;
            font-size: 12px;
            font-weight: 600;
        """)

        title_row.addWidget(self.lbl_title)
        title_row.addWidget(self.lbl_code_badge)
        title_row.addStretch()
        title_row.addWidget(self.lbl_status_badge)

        # Professor
        self.lbl_prof = QLabel()
        self.lbl_prof.setStyleSheet(
            "color: #6F767E; font-size: 13px; font-style: italic; background: transparent;"
        )

        # Description
        self.lbl_desc_title = QLabel()
        self.lbl_desc_title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #1E2328; background: transparent;"
        )

        self.lbl_desc = QLabel()
        self.lbl_desc.setStyleSheet("color: #6F767E; font-size: 13px; background: transparent;")
        self.lbl_desc.setWordWrap(True)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(30)

        self.stat_lessons = self._make_stat("lessons", "📺", tr("stat_lessons"), "0")
        self.stat_exercises = self._make_stat("exercises", "✅", tr("stat_exercises"), "0")
        self.stat_progress = self._make_stat("progress", "🔵", tr("stat_progress"), "0%")

        stats_row.addLayout(self.stat_lessons)
        stats_row.addLayout(self.stat_exercises)
        stats_row.addLayout(self.stat_progress)
        stats_row.addStretch()

        # Progress bar tổng thể
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #EEF0F4;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #2D60FF;
                border-radius: 4px;
            }
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
                background: #FFFFFF;
                border-radius: 20px;
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

        # Resource card
        res_card = QFrame()
        res_card.setObjectName("CardWhite")
        res_card.setFixedWidth(280)
        res_card.setStyleSheet("""
            QFrame#CardWhite {
                background: #FFFFFF;
                border-radius: 20px;
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
                background: #F3F4F6;
                color: #6F767E;
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 11px;
            """)
            tags_layout.addWidget(t)
        tags_layout.addStretch()
        res_layout.addLayout(tags_layout)

        # CTA card
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
                background: white;
                color: #2D60FF;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: bold;
                border: none;
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
        setattr(self, f"_stat_val_{key}", lbl_val)
        return lay

    def _set_stat(self, key, value):
        w = getattr(self, f"_stat_val_{key}", None)
        if w:
            w.setText(str(value))

    # ================= LOAD DATA =================
    def load_course(self, course: dict):
        self.course_id = course.get("id") or course.get("course_id") or course.get("_id")
        self.course_data = course

        self.lbl_title.setText(course.get("name", ""))
        self.lbl_code_badge.setText(course.get("code", ""))
        self.lbl_prof.setText(f"{tr('course_detail_professor')} {course.get('professor', '')}")

        desc_key = course.get("description_key")
        self.lbl_desc.setText(tr(desc_key) if desc_key else "")

        # Resources
        for i in reversed(range(self.res_container.count())):
            item = self.res_container.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        resources = course.get("resources", [])
        for r in resources:
            self.res_container.addWidget(ResourceItem(r["title"], r["url"]))

        self.load_lessons()

    def load_lessons(self):
        # Xóa lessons cũ khỏi UI (bỏ qua stretch ở cuối)
        for i in reversed(range(self.layout_lessons.count())):
            item = self.layout_lessons.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        if self.course_id is None:
            empty = QLabel(tr("course_detail_no_data"))
            empty.setStyleSheet("color: #9BA3AF; font-size: 13px; background: transparent;")
            self.layout_lessons.insertWidget(0, empty)
            return

        try:
            lessons = self.controller.get_lessons(self.course_id)
        except Exception as e:
            print(f"[CourseDetail] Lỗi load_lessons: {e}")
            lessons = []

        total = len(lessons)
        exercises = sum(1 for l in lessons if l.get("has_exercise", False))
        progress = self.controller.get_progress(self.course_id) if total > 0 else 0

        self._set_stat("lessons", total)
        self._set_stat("exercises", exercises)
        self._set_stat("progress", f"{progress}%")
        self.progress_bar.setValue(progress)

        # Cập nhật status badge
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

        for l in lessons:
            item = LessonItem(l, self.handle_flashcard)
            # FIX: Kết nối signal để cập nhật progress khi user tick
            item.completed_changed.connect(self._on_lesson_completed)
            # Chèn trước stretch
            self.layout_lessons.insertWidget(self.layout_lessons.count() - 1, item)

        if not lessons:
            empty = QLabel(tr("course_detail_no_lessons"))
            empty.setStyleSheet("color: #9BA3AF; font-size: 13px; background: transparent;")
            self.layout_lessons.insertWidget(0, empty)

    # ================= ACTIONS =================
    # FIX: Mới — xử lý khi user tick/untick 1 lesson
    def _on_lesson_completed(self, lesson_id: int, is_done: bool):
        self.controller.mark_lesson_done(lesson_id, is_done)

        # Tính lại progress
        progress = self.controller.get_progress(self.course_id)
        self._set_stat("progress", f"{progress}%")
        self.progress_bar.setValue(progress)

        # Cập nhật status badge
        if progress == 100:
            self.lbl_status_badge.setText(tr("course_detail_completed"))
            self.lbl_status_badge.setStyleSheet("""
                background: #ECFDF5; color: #10B981;
                border-radius: 12px; padding: 4px 14px;
                font-size: 12px; font-weight: 600;
            """)
            # Hiển thị badge/certificate dialog
            course_name = (self.course_data.get("name", tr("course_detail_this_course"))
                           if self.course_data else tr("course_detail_this_course"))
            dlg = BadgeDialog(course_name, self)
            dlg.exec()

    def handle_flashcard(self, lesson: dict):
        try:
            cards = self.controller.generate_flashcard_for_lesson(lesson)
            if cards:
                QMessageBox.information(
                    self, tr("lesson_flash_btn"),
                    tr("course_detail_flash_created", count=len(cards))
                )
            else:
                QMessageBox.information(
                    self, tr("lesson_flash_btn"),
                    tr("course_detail_no_ai")
                )
        except Exception as e:
            QMessageBox.warning(self, tr("flash_error"), str(e))

    # Legacy compat
    def set_course(self, name, code, professor, progress=0):
        self.load_course({
            "id": getattr(self, "course_id", None),
            "name": name,
            "code": code,
            "professor": professor,
            "progress": progress,
        })

    def _retranslate(self):
        self._retranslated = True
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

        # Re-render professor label and lessons list when language changes
        if self.course_data:
            self.lbl_prof.setText(
                f"{tr('course_detail_professor')} {self.course_data.get('professor', '')}"
            )
            self.load_lessons()