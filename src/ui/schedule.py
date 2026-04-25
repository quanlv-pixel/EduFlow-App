from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QInputDialog,
    QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem
)
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QColor, QFont, QBrush, QPainter


# ============================================================
#  Custom Delegate — giữ màu xanh + trắng bất kể theme
# ============================================================
class ScheduleCellDelegate(QStyledItemDelegate):
    """
    Với ô nào được đánh dấu Qt.UserRole == True (ô lịch học),
    delegate tự vẽ nền xanh + chữ trắng, bỏ qua stylesheet theme.
    Ô trống vẫn render bình thường theo QSS.
    """

    CELL_BG    = QColor("#2D60FF")
    CELL_FG    = QColor("#FFFFFF")
    CELL_RADIUS = 8  # bo góc nhẹ

    def paint(self, painter: QPainter,
              option: QStyleOptionViewItem,
              index):

        is_schedule = index.data(Qt.UserRole)

        if not is_schedule:
            super().paint(painter, option, index)
            return

        painter.save()

        # --- Nền xanh bo góc ---
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.CELL_BG)
        rect = option.rect.adjusted(2, 2, -2, -2)   # margin nhỏ để thấy lưới
        painter.drawRoundedRect(rect, self.CELL_RADIUS, self.CELL_RADIUS)

        # --- Chữ trắng, căn giữa ---
        painter.setPen(self.CELL_FG)

        font = QFont()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)

        text = index.data(Qt.DisplayRole) or ""
        painter.drawText(rect, Qt.AlignCenter | Qt.AlignVCenter | Qt.TextWordWrap, text)

        painter.restore()


# ============================================================
#  ScheduleWidget
# ============================================================
class ScheduleWidget(QWidget):
    DAYS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

    def __init__(self, controller, user_id):
        super().__init__()
        self.controller = controller
        self.user_id    = user_id

        self.course_colors = {}

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # ─── HEADER ───────────────────────────────────────
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

        header_layout.addLayout(title_v)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)

        main_layout.addLayout(header_layout)

        # ─── TABLE ────────────────────────────────────────
        card = QFrame()
        card.setObjectName("CardWhite")
        card_layout = QVBoxLayout(card)

        self.table = QTableWidget(24, 7)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setHorizontalHeaderLabels(self.DAYS)

        time_labels = [f"{h:02d}:00" for h in range(24)]
        self.table.setVerticalHeaderLabels(time_labels)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(True)

        for i in range(24):
            self.table.setRowHeight(i, 50)

        # 👇 GẮN DELEGATE — đây là điểm mấu chốt
        self.delegate = ScheduleCellDelegate(self.table)
        self.table.setItemDelegate(self.delegate)

        card_layout.addWidget(self.table)
        main_layout.addWidget(card)

        self.load_schedule()

    # ─── COLOR GENERATOR ──────────────────────────────────
    def get_color_for_course(self, course):
        if course in self.course_colors:
            return self.course_colors[course]
        palette = [
            "#DCEBFF", "#E8F8F5", "#FFF4E5",
            "#FDEDEC", "#F5EEF8", "#FEF9E7",
            "#EAF2F8"
        ]
        color = palette[len(self.course_colors) % len(palette)]
        self.course_colors[course] = color
        return color

    # ─── LOAD ─────────────────────────────────────────────
    def load_schedule(self):
        self.table.clearContents()
        self.table.clearSpans()

        try:
            schedules = self.controller.get_schedule(self.user_id)
            if not schedules:
                return
        except Exception as e:
            QMessageBox.critical(self, "Lỗi DB", str(e))
            return

        for s in schedules:
            start = s.get("start_time")
            end   = s.get("end_time")
            col   = s.get("day")

            if start is None or end is None or col is None:
                continue

            course = s.get("course", "")
            room   = s.get("room",   "")

            # Gộp ô
            self.table.setSpan(start, col, end - start, 1)

            item = QTableWidgetItem(f"{course}\n{room}")
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            item.setFlags(Qt.ItemIsEnabled)   # không highlight khi click

            # 👇 Đánh dấu để delegate nhận biết đây là ô lịch học
            item.setData(Qt.UserRole, True)

            self.table.setItem(start, col, item)

        self.table.setWordWrap(True)
        self.table.viewport().update()
        QTimer.singleShot(0,  self.table.viewport().update)
        QTimer.singleShot(50, self.table.viewport().update)

    # ─── ADD ──────────────────────────────────────────────
    def add_schedule(self):
        course, ok = QInputDialog.getText(self, "Môn học", "Nhập tên môn:")
        if not ok or not course.strip():
            return

        room, ok = QInputDialog.getText(self, "Phòng", "Nhập phòng:")
        if not ok or not room.strip():
            return

        day, ok = QInputDialog.getItem(
            self, "Chọn thứ", "Chọn ngày:", self.DAYS, 0, False
        )
        if not ok:
            return
        col = self.DAYS.index(day)

        start, ok = QInputDialog.getInt(
            self, "Giờ bắt đầu", "Nhập giờ bắt đầu (0-23):", 7, 0, 23
        )
        if not ok:
            return

        end, ok = QInputDialog.getInt(
            self, "Giờ kết thúc", "Nhập giờ kết thúc (1-24):", start + 1, 1, 24
        )
        if not ok:
            return

        try:
            success = self.controller.add_schedule(
                self.user_id,
                course.strip(),
                room.strip(),
                col,
                start,
                end
            )
            if success:
                self.load_schedule()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm lịch!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))