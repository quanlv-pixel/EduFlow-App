from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QInputDialog,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QRect, QTimer, QSize, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen

# ================================================================
#  Hằng số layout
# ================================================================
PX_PER_MIN  = 1.2                        # pixel / phút
HOUR_H      = int(60 * PX_PER_MIN)      # 72px / giờ
TOTAL_H     = 24 * HOUR_H               # 1728px tổng chiều cao
TIME_W      = 64                         # chiều rộng cột giờ bên trái
EVENT_PAD   = 3                          # khoảng cách giữa event và viền cột
CORNER_R    = 6                          # bo góc event

DAYS_SHORT     = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
MINUTE_OPTIONS = ["00", "15", "30", "45"]

# ─── Màu sắc ─────────────────────────────────────────────────────
C_EVENT_BG  = QColor("#2D60FF")
C_EVENT_FG  = QColor("#FFFFFF")
C_GRID_HOUR = QColor("#DEDEDE")
C_GRID_HALF = QColor("#F2F2F2")
C_TIME_LBL  = QColor("#9099A3")
C_DAY_LBL   = QColor("#1E2328")
C_DAY_SEP   = QColor("#EDEDED")


# ================================================================
#  Canvas — vẽ lưới + event bằng QPainter
# ================================================================
class ScheduleCanvas(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schedules: list[dict] = []
        self.setMinimumHeight(TOTAL_H)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # Signal phát ra khi click vào event — trả về dict schedule hoặc None
    clicked = Signal(object)

    def set_schedules(self, schedules: list[dict]):
        self._schedules = schedules
        self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        w     = self.width()
        col_w = (w - TIME_W) / 7
        px, py = event.position().x(), event.position().y()

        # Tìm xem click trúng event nào không
        for s in self._schedules:
            start_min = s.get("start_time")
            end_min   = s.get("end_time")
            col       = s.get("day")
            if start_min is None or end_min is None or col is None:
                continue

            x  = self._col_x(col, col_w) + EVENT_PAD
            y  = self._min_y(start_min) + 1
            cw = int(col_w) - EVENT_PAD * 2
            ch = self._min_y(end_min) - y - 1

            if x <= px <= x + cw and y <= py <= y + ch:
                self.clicked.emit(s)
                return

        # Click vào vùng trống
        self.clicked.emit(None)

    def sizeHint(self) -> QSize:
        return QSize(800, TOTAL_H)

    def _col_x(self, col: int, col_w: float) -> int:
        return int(TIME_W + col * col_w)

    def _min_y(self, minutes: int) -> int:
        return int(minutes * PX_PER_MIN)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w     = self.width()
        col_w = (w - TIME_W) / 7

        # ── Nền trắng ──────────────────────────────────────────
        painter.fillRect(0, 0, w, TOTAL_H, Qt.white)

        # ── Đường kẻ ngang ─────────────────────────────────────
        for h in range(25):
            y = self._min_y(h * 60)
            painter.setPen(QPen(C_GRID_HOUR, 1))
            painter.drawLine(TIME_W, y, w, y)
            if h < 24:
                y30 = self._min_y(h * 60 + 30)
                painter.setPen(QPen(C_GRID_HALF, 1, Qt.DashLine))
                painter.drawLine(TIME_W, y30, w, y30)

        # ── Đường kẻ dọc phân cột ──────────────────────────────
        painter.setPen(QPen(C_DAY_SEP, 1))
        for d in range(8):
            x = int(TIME_W + d * col_w)
            painter.drawLine(x, 0, x, TOTAL_H)

        # ── Nhãn giờ bên trái ──────────────────────────────────
        font_time = QFont("Segoe UI", 8)
        painter.setFont(font_time)
        painter.setPen(C_TIME_LBL)
        for h in range(1, 24):
            y = self._min_y(h * 60)
            painter.drawText(0, y - 10, TIME_W - 8, 20,
                             Qt.AlignRight | Qt.AlignVCenter,
                             f"{h:02d}:00")

        # ── Event blocks ────────────────────────────────────────
        for s in self._schedules:
            start_min = s.get("start_time")
            end_min   = s.get("end_time")
            col       = s.get("day")
            if start_min is None or end_min is None or col is None:
                continue
            if end_min <= start_min or not (0 <= col <= 6):
                continue

            x  = self._col_x(col, col_w) + EVENT_PAD
            y  = self._min_y(start_min) + 1
            cw = int(col_w) - EVENT_PAD * 2
            ch = self._min_y(end_min) - y - 1
            if ch < 4:
                continue

            rect = QRect(x, y, cw, ch)

            # Nền xanh bo góc
            painter.setPen(Qt.NoPen)
            painter.setBrush(C_EVENT_BG)
            painter.drawRoundedRect(rect, CORNER_R, CORNER_R)

            # Thanh sáng trái (Google Calendar accent)
            painter.setBrush(QColor(255, 255, 255, 55))
            painter.drawRoundedRect(QRect(x, y, 4, ch), 2, 2)

            # Text
            painter.setPen(C_EVENT_FG)
            inner = rect.adjusted(10, 5, -5, -5)

            course   = s.get("course", "")
            room     = s.get("room",   "")
            sh, sm   = start_min // 60, start_min % 60
            eh, em   = end_min   // 60, end_min   % 60
            time_str = f"{sh:02d}:{sm:02d} – {eh:02d}:{em:02d}"

            # Tên môn (bold)
            f_bold = QFont("Segoe UI", 9)
            f_bold.setBold(True)
            painter.setFont(f_bold)
            painter.drawText(inner, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap,
                             course)

            # Chi tiết (phòng + giờ) — chỉ hiện khi ô đủ cao
            if ch > 38:
                f_detail = QFont("Segoe UI", 8)
                painter.setFont(f_detail)
                fm = painter.fontMetrics()
                detail_rect = QRect(inner.left(),
                                    inner.top() + fm.height() + 4,
                                    inner.width(), inner.height())
                detail = (room + "  •  " if room else "") + time_str
                painter.drawText(detail_rect,
                                 Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap,
                                 detail)

        painter.end()


# ================================================================
#  DayHeaderWidget — hàng tên ngày cố định (không cuộn)
# ================================================================
class DayHeaderWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)

    def paintEvent(self, _event):
        painter = QPainter(self)
        w     = self.width()
        col_w = (w - TIME_W) / 7

        painter.fillRect(0, 0, w, self.height(), Qt.white)

        # Viền dưới
        painter.setPen(QPen(C_GRID_HOUR, 1))
        painter.drawLine(TIME_W, self.height() - 1, w, self.height() - 1)

        font = QFont("Segoe UI", 9)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(C_DAY_LBL)

        for i, day in enumerate(DAYS_SHORT):
            x  = int(TIME_W + i * col_w)
            cw = int(col_w)
            painter.drawText(x, 0, cw, self.height(), Qt.AlignCenter, day)

        painter.end()


# ================================================================
#  ScheduleWidget — widget chính
# ================================================================
class ScheduleWidget(QWidget):

    def __init__(self, controller, user_id):
        super().__init__()
        self.controller = controller
        self.user_id    = user_id

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # ─── Tiêu đề + nút thêm ───────────────────────────────
        header_layout = QHBoxLayout()

        title_v  = QVBoxLayout()
        title    = QLabel("Thời khóa biểu")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        subtitle = QLabel("Quản lý lịch học theo tuần.")
        subtitle.setStyleSheet("color: #6F767E;")
        title_v.addWidget(title)
        title_v.addWidget(subtitle)

        self.btn_add = QPushButton("+ Thêm lịch học")
        self.btn_add.setObjectName("BtnAddSchedule")
        self.btn_add.setFixedHeight(40)
        self.btn_add.clicked.connect(self.add_schedule)

        self.btn_delete = QPushButton("🗑 Xóa lịch học")
        self.btn_delete.setObjectName("BtnDeleteSchedule")
        self.btn_delete.setFixedHeight(40)
        self.btn_delete.setCheckable(True)
        self.btn_delete.clicked.connect(self.toggle_delete_mode)

        header_layout.addLayout(title_v)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        header_layout.addWidget(self.btn_delete)
        main_layout.addLayout(header_layout)

        # Nhãn gợi ý khi đang ở chế độ xóa
        self.lbl_hint = QLabel("🗑 Đang ở chế độ xóa — bấm vào lịch học để xóa")
        self.lbl_hint.setStyleSheet(
            "color: #EF4444; font-size: 13px; padding: 6px 12px;"
            "background: #FEE2E2; border-radius: 8px;"
        )
        self.lbl_hint.setAlignment(Qt.AlignCenter)
        self.lbl_hint.hide()
        main_layout.addWidget(self.lbl_hint)

        # ─── Card chứa calendar ───────────────────────────────
        card = QFrame()
        card.setObjectName("CardWhite")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Hàng ngày cố định (không cuộn)
        self.day_header = DayHeaderWidget()
        card_layout.addWidget(self.day_header)

        # Scroll area chứa canvas lưới + event
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.canvas = ScheduleCanvas()
        self.canvas.clicked.connect(self.handle_canvas_click)
        self.scroll.setWidget(self.canvas)
        card_layout.addWidget(self.scroll)

        self._delete_mode = False

        main_layout.addWidget(card)

        # Mở đầu scroll tại 6:00 sáng
        QTimer.singleShot(120, lambda: self.scroll.verticalScrollBar().setValue(
            int(6 * HOUR_H)
        ))

        self.load_schedule()

    # ─── DELETE MODE ──────────────────────────────────────────
    def toggle_delete_mode(self):
        self._delete_mode = self.btn_delete.isChecked()
        if self._delete_mode:
            self.btn_delete.setStyleSheet(
                "background:#EF4444; color:white; border-radius:8px;"
                "padding:0 14px; font-weight:bold;"
            )
            self.lbl_hint.show()
            self.canvas.setCursor(Qt.ForbiddenCursor)
        else:
            self.btn_delete.setStyleSheet("")   # trả về style QSS gốc
            self.lbl_hint.hide()
            self.canvas.setCursor(Qt.ArrowCursor)

    def handle_canvas_click(self, schedule: object):
        if not self._delete_mode:
            return

        if schedule is None:
            QMessageBox.warning(self, "Không có lịch học",
                                "Không có lịch học để xóa tại vị trí này!")
            return

        course = schedule.get("course", "")
        sh, sm = schedule["start_time"] // 60, schedule["start_time"] % 60
        eh, em = schedule["end_time"]   // 60, schedule["end_time"]   % 60
        confirm = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa lịch học này không?\n\n"
            f"📘 {course}\n"
            f"🕐 {sh:02d}:{sm:02d} – {eh:02d}:{em:02d}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            ok = self.controller.delete_schedule(schedule["id"])
            if ok:
                self.load_schedule()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xóa lịch học!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))

    # ─── LOAD ─────────────────────────────────────────────────
    def load_schedule(self):
        try:
            schedules = self.controller.get_schedule(self.user_id) or []
        except Exception as e:
            QMessageBox.critical(self, "Lỗi DB", str(e))
            schedules = []
        self.canvas.set_schedules(schedules)

    # ─── ADD ──────────────────────────────────────────────────
    def add_schedule(self):
        course, ok = QInputDialog.getText(self, "Môn học", "Nhập tên môn:")
        if not ok or not course.strip():
            return

        room, ok = QInputDialog.getText(self, "Phòng", "Nhập phòng:")
        if not ok or not room.strip():
            return

        day, ok = QInputDialog.getItem(
            self, "Chọn thứ", "Chọn ngày:", DAYS_SHORT, 0, False
        )
        if not ok:
            return
        col = DAYS_SHORT.index(day)

        start_h, ok = QInputDialog.getInt(
            self, "Giờ bắt đầu", "Giờ bắt đầu (0 – 23):", 7, 0, 23
        )
        if not ok:
            return

        start_m_str, ok = QInputDialog.getItem(
            self, "Phút bắt đầu", "Phút bắt đầu:", MINUTE_OPTIONS, 0, False
        )
        if not ok:
            return
        start_m = int(start_m_str)

        end_h, ok = QInputDialog.getInt(
            self, "Giờ kết thúc", "Giờ kết thúc (0 – 24):", start_h + 1, 0, 24
        )
        if not ok:
            return

        end_m_str, ok = QInputDialog.getItem(
            self, "Phút kết thúc", "Phút kết thúc:", MINUTE_OPTIONS, 0, False
        )
        if not ok:
            return
        end_m = int(end_m_str)

        start_total = start_h * 60 + start_m
        end_total   = end_h   * 60 + end_m

        if end_total <= start_total:
            QMessageBox.warning(
                self, "Giờ không hợp lệ",
                f"Giờ kết thúc ({end_h:02d}:{end_m:02d}) "
                f"phải sau giờ bắt đầu ({start_h:02d}:{start_m:02d})!"
            )
            return

        try:
            success = self.controller.add_schedule(
                self.user_id, course.strip(), room.strip(),
                col, start_total, end_total
            )
            if success:
                self.load_schedule()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm lịch!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))