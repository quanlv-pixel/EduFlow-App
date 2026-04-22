from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt


class ScheduleWidget(QWidget):
    DAYS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

    def __init__(self, controller, user_id):
        super().__init__()

        self.controller = controller
        self.user_id = user_id

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

        self.table = QTableWidget(10, 7)
        self.table.setHorizontalHeaderLabels(self.DAYS)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        for i in range(10):
            self.table.setRowHeight(i, 70)

        card_layout.addWidget(self.table)
        main_layout.addWidget(card)

        # load
        self.load_schedule()

    # ================= LOAD =================
    def load_schedule(self):
        self.table.clearContents()

        try:
            schedules = self.controller.get_schedule(self.user_id)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi DB", str(e))
            return

        for s in schedules:
            row = s.get("row")
            col = s.get("col")

            if row is None or col is None:
                continue

            text = f"{s.get('course', '')}\n{s.get('room', '')}"

            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)

            # 👉 highlight nhẹ
            item.setBackground(Qt.lightGray)

            self.table.setItem(row, col, item)

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

        # ===== DAY (UX tốt hơn) =====
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

        # ===== SLOT =====
        slot, ok = QInputDialog.getInt(
            self,
            "Tiết học",
            "Chọn tiết (0-9):",
            0,
            0,
            9
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
                slot
            )

            if success:
                self.load_schedule()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm lịch!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))