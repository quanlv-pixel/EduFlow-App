from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar,
    QStackedLayout, QMessageBox, QScrollArea,
    QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QCursor
from src.ui.settings_widget import LanguageManager, tr

# ================= LESSON ITEM =================
class LessonItem(QFrame):
    def __init__(self, lesson, on_flashcard):
        super().__init__()

        self.lesson = lesson
        self.setObjectName("CardWhite")
        self.setStyleSheet("""
            QFrame#CardWhite {
                background: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #EDEDED;
            }
        """)
        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # Check icon
        check = QLabel("✅")
        check.setStyleSheet("font-size: 16px; background: transparent;")
        check.setFixedWidth(28)

        # Title + meta
        info_v = QVBoxLayout()
        info_v.setSpacing(2)

        name = QLabel(lesson["title"])
        name.setStyleSheet("font-size: 14px; font-weight: 600; color: #1E2328; background: transparent;")

        duration = lesson.get("duration", "")
        type_lbl = lesson.get("type", "Video bài giảng")
        meta = QLabel(f"{duration}  •  {type_lbl}" if duration else type_lbl)
        meta.setStyleSheet("font-size: 11px; color: #6F767E; background: transparent;")

        info_v.addWidget(name)
        info_v.addWidget(meta)

        layout.addWidget(check)
        layout.addLayout(info_v)
        layout.addStretch()

        btn_flash = QPushButton("⚡ Flashcard")
        btn_flash.setCursor(Qt.PointingHandCursor)
        btn_flash.setStyleSheet("""
            QPushButton {
                background-color: #2D60FF;
                color: white;
                border-radius: 8px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #1A4FE0; }
        """)
        btn_flash.clicked.connect(lambda: on_flashcard(self.lesson))

        layout.addWidget(btn_flash)


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
        lbl_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #2D60FF; background: transparent;")

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

        # ── BODY: 2-COLUMN ──────────────────────
        body = QHBoxLayout()
        body.setSpacing(24)
        body.setContentsMargins(0, 0, 0, 0)

        # LEFT COLUMN
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
        self.lbl_title = QLabel(tr("course_detail_title"))
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

        self.lbl_status_badge = QLabel(tr("course_status_learning"))
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
        self.lbl_prof.setStyleSheet("color: #6F767E; font-size: 13px; font-style: italic; background: transparent;")

        # Description
        self.lbl_desc_title = QLabel()
        self.lbl_desc_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1E2328; background: transparent;")

        self.lbl_desc = QLabel("Thiết kế và quản trị cơ sở dữ liệu quan hệ với trọng tâm là SQL.")
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

        header_card_layout.addLayout(title_row)
        header_card_layout.addWidget(self.lbl_prof)
        header_card_layout.addSpacing(6)
        header_card_layout.addWidget(self.lbl_desc_title)
        header_card_layout.addWidget(self.lbl_desc)
        header_card_layout.addSpacing(8)
        header_card_layout.addLayout(stats_row)

        # Content card (Nội dung học tập)
        content_card = QFrame()
        content_card.setObjectName("CardWhite")
        content_card.setStyleSheet("""
            QFrame#CardWhite {
                background: #FFFFFF;
                border-radius: 20px;
                border: 1px solid #EDEDED;
            }
        """)
        content_card_layout = QVBoxLayout(content_card)
        content_card_layout.setContentsMargins(24, 20, 24, 20)
        content_card_layout.setSpacing(10)

        self.lbl_content = QLabel()
        self.lbl_content.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E2328; background: transparent;")
        content_card_layout.addWidget(self.lbl_content)

        self.layout_lessons = QVBoxLayout()
        self.layout_lessons.setSpacing(8)
        content_card_layout.addLayout(self.layout_lessons)

        left.addWidget(self.header_card)
        left.addWidget(content_card)
        left.addStretch()

        # RIGHT COLUMN
        right = QVBoxLayout()
        right.setSpacing(18)
        right.setAlignment(Qt.AlignTop)

        # Resources card
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
        self.lbl_pop.setStyleSheet("font-size: 10px; color: #9BA3AF; font-weight: 700; letter-spacing: 1px; background: transparent;")
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
        self.lbl_cta_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background: transparent;")

        self.lbl_cta_desc = QLabel("Bạn đang dừng lại ở giai đoạn đầu của khóa học. Bắt đầu bài học đầu tiên ngay nhé!")
        self.lbl_cta_desc.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.85); background: transparent;")
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
        lbl_label.setStyleSheet("font-size: 10px; color: #9BA3AF; font-weight: 700; letter-spacing: 0.8px; background: transparent;")
        row.addWidget(icon)
        row.addWidget(lbl_label)
        row.addStretch()

        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E2328; background: transparent;")

        lay.addLayout(row)
        lay.addWidget(lbl_val)

        # store reference for update
        setattr(self, f"_stat_label_{key}", lbl_label)
        setattr(self, f"_stat_val_{key}", lbl_val)
        return lay

    def _set_stat(self, label, value):
        w = getattr(self, f"_stat_val_{label}", None)
        if w:
            w.setText(str(value))

    # ================= LOAD DATA =================
    def load_course(self, course):
        # Lấy id linh hoạt: hỗ trợ "id", "course_id", "_id"
        self.course_id = course.get("id") or course.get("course_id") or course.get("_id")
        self.course_data = course

        self.lbl_title.setText(course.get("name", ""))
        self.lbl_code_badge.setText(course.get("code", ""))
        self.lbl_prof.setText(f"{tr('course_detail_professor')} {course.get('professor', '')}")

        desc = course.get("description", "")
        self.lbl_desc.setText(desc)

        progress = course.get("progress", 0)
        self._set_stat("stat_progress", f"{progress}%")

        # Resources — xóa cũ
        for i in reversed(range(self.res_container.count())):
            item = self.res_container.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        resources = course.get("resources", [])
        for r in resources:
            self.res_container.addWidget(ResourceItem(r["title"], r["url"]))

        self.load_lessons()

    def load_lessons(self):
        for i in reversed(range(self.layout_lessons.count())):
            item = self.layout_lessons.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        # Nếu chưa có course_id thì không load
        if self.course_id is None:
            empty = QLabel("Không tìm thấy dữ liệu khóa học.")
            empty.setStyleSheet("color: #9BA3AF; font-size: 13px; background: transparent;")
            self.layout_lessons.addWidget(empty)
            return

        try:
            lessons = self.controller.get_lessons(self.course_id)
        except Exception as e:
            print(f"[CourseDetail] Lỗi load_lessons: {e}")
            lessons = []

        self._set_stat("stat_lessons", len(lessons))
        exercises = sum(1 for l in lessons if l.get("has_exercise", False))
        self._set_stat("stat_exercises", exercises)

        for l in lessons:
            item = LessonItem(l, self.handle_flashcard)
            self.layout_lessons.addWidget(item)

        if not lessons:
            self.empty_label = QLabel()
            self.empty_label.setStyleSheet("color: #9BA3AF; font-size: 13px; background: transparent;")
            self.layout_lessons.addWidget(self.empty_label)

    # ================= ACTIONS =================
    def handle_flashcard(self, lesson):
        try:
            cards = self.controller.generate_flashcard_for_lesson(lesson)
            QMessageBox.information(self, "Flashcard", f"Đã tạo {len(cards)} flashcard!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

    # ── Legacy compat: some callers use set_course() ──
    def set_course(self, name, code, professor, progress=0):
        self.load_course({
            "id": getattr(self, "course_id", None),
            "name": name,
            "code": code,
            "professor": professor,
            "progress": progress,
        })

    def _retranslate(self):
        self.back_btn.setText("← " + tr("flash_back"))

        self.lbl_content.setText(tr("course_detail_content"))

        # header
        self.lbl_status_badge.setText(tr("course_status_learning"))

        # CTA
        self.lbl_cta_desc.setText(tr("course_detail_cta_desc"))
        self.lbl_cta_title.setText(tr("course_detail_continue"))
        self.btn_cta.setText(tr("course_detail_open_latest"))
        self.lbl_pop.setText(tr("course_detail_resources"))

        self.lbl_cta_desc.setText(tr("course_detail_cta_desc"))

        self._stat_label_lessons.setText(tr("stat_lessons"))
        self._stat_label_exercises.setText(tr("stat_exercises"))
        self._stat_label_progress.setText(tr("stat_progress"))
        self.lbl_desc_title.setText(tr("course_detail_description"))
        # resource
        # nếu bạn có label resource title thì thêm

        # empty lessons
        if hasattr(self, "empty_label"):
            self.empty_label.setText(tr("course_detail_empty"))