from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QInputDialog,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QBrush


class ScheduleWidget(QWidget):
    DAYS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

    def __init__(self, controller, user_id):
        super().__init__()
        self.controller = controller
        self.user_id = user_id

        # 👉 lưu màu theo môn
        self.course_colors = {}

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # ================= HEADER =================
        header_layout = QHBoxLayout()

        title_v = QVBoxLayout()
        title = QLabel("Thời khóa biểu")
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

        # ================= TABLE =================
        card = QFrame()
        card.setObjectName("CardWhite")

        card_layout = QVBoxLayout(card)

        # 👉 24h x 7 ngày
        self.table = QTableWidget(24, 7)
        
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        # header ngang (ngày)
        self.table.setHorizontalHeaderLabels(self.DAYS)

        # header dọc (giờ)
        time_labels = [f"{h:02d}:00" for h in range(24)]
        self.table.setVerticalHeaderLabels(time_labels)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(True)

        # chiều cao row
        for i in range(24):
            self.table.setRowHeight(i, 50)

        card_layout.addWidget(self.table)
        main_layout.addWidget(card)

        # load data
        self.load_schedule()

    # ================= COLOR GENERATOR =================
    def get_color_for_course(self, course):
        if course in self.course_colors:
            return self.course_colors[course]

        # 🎨 palette đẹp
        palette = [
            "#DCEBFF", "#E8F8F5", "#FFF4E5",
            "#FDEDEC", "#F5EEF8", "#FEF9E7",
            "#EAF2F8"
        ]

        color = palette[len(self.course_colors) % len(palette)]
        self.course_colors[course] = color
        return color

    # ================= LOAD =================
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
            end = s.get("end_time")
            col = s.get("day")


            if start is None or end is None or col is None:
                continue

            course = s.get("course", "")
            room = s.get("room", "")

            # 🔥 gộp ô (quan trọng nhất)
            self.table.setSpan(start, col, end - start, 1)

            # chỉ tạo 1 item duy nhất
            text = f"{course}\n{room}"

            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            item.setFlags(Qt.ItemIsEnabled)  # Bỏ ItemIsSelectable để tránh highlight đỏ khi click

            # 🎨 màu
            item.setBackground(QColor("#2D60FF"))
            item.setForeground(QColor("#FFFFFF"))

            # font
            font = QFont()
            font.setBold(True)
            item.setFont(font)

            # đặt vào ô đầu tiên
            self.table.setItem(start, col, item)

        # 🔄 Force repaint toàn bảng sau khi set xong tất cả item
        self.table.setWordWrap(True)
        self.table.viewport().update()
        self.table.update()

        # ⚡ Qt bug: spanned cell không render text ngay — QTimer force repaint sau khi widget show
        QTimer.singleShot(0, self.table.viewport().update)
        QTimer.singleShot(50, self.table.viewport().update)

    # ================= ADD =================
    def add_schedule(self):
        # ===== COURSE =====
        course, ok = QInputDialog.getText(self, "Môn học", "Nhập tên môn:")
        if not ok or not course.strip():
            return

        # ===== ROOM =====
        room, ok = QInputDialog.getText(self, "Phòng", "Nhập phòng:")
        if not ok or not room.strip():
            return

        # ===== DAY =====
        day, ok = QInputDialog.getItem(
            self,
            "Chọn thứ",
            "Chọn ngày:",
            self.DAYS,
            0,
            False
        )
        if not ok:
            return

        col = self.DAYS.index(day)

        # ===== HOUR =====
        # ===== START =====
        start, ok = QInputDialog.getInt(
            self,
            "Giờ bắt đầu",
            "Nhập giờ bắt đầu (0-23):",
            7,
            0,
            23
        )
        if not ok:
            return

        # ===== END =====
        end, ok = QInputDialog.getInt(
            self,
            "Giờ kết thúc",
            "Nhập giờ kết thúc (1-24):",
            start + 1,
            1,
            24
        )
        if not ok:
            return

        # ===== SAVE =====
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