from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt


class ScheduleWidget(QWidget):
    def __init__(self, controller, user_id):
        super().__init__()

        self.controller = controller
        self.user_id = user_id

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # ================= HEADER =================
        header_layout = QHBoxLayout()

        title_v = QVBoxLayout()
        title = QLabel("Thời khóa biểu")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")

        subtitle = QLabel("Xem và quản lý thời gian biểu hàng tuần.")
        subtitle.setStyleSheet("color: #6F767E; font-size: 13px;")

        title_v.addWidget(title)
        title_v.addWidget(subtitle)

        self.btn_add = QPushButton("+ Thêm lịch học")
        self.btn_add.setObjectName("BtnAddSchedule")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(40)
        self.btn_add.clicked.connect(self.add_schedule)

        header_layout.addLayout(title_v)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)

        main_layout.addLayout(header_layout)

        # ================= CARD =================
        card = QFrame()
        card.setObjectName("CardWhite")
        card_layout = QVBoxLayout(card)

        lbl = QLabel("<b>Lịch học chi tiết</b>")
        card_layout.addWidget(lbl)

        # ================= TABLE =================
        self.table = QTableWidget(10, 7)
        self.table.setHorizontalHeaderLabels(["T2", "T3", "T4", "T5", "T6", "T7", "CN"])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        for i in range(10):
            self.table.setRowHeight(i, 70)

        card_layout.addWidget(self.table)
        main_layout.addWidget(card)

        # load data
        self.load_schedule()

    # ================= LOAD =================
    def load_schedule(self):
        self.table.clearContents()

        schedules = self.controller.get_schedule(self.user_id)

        for s in schedules:
            row = s["row"]
            col = s["col"]

            text = f"{s['course']}\n{s['room']}"
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row, col, item)

    # ================= ADD =================
    def add_schedule(self):
        course, ok1 = QInputDialog.getText(self, "Tên môn", "Nhập tên môn:")
        if not ok1 or not course:
            return

        room, ok2 = QInputDialog.getText(self, "Phòng", "Nhập phòng:")
        if not ok2 or not room:
            return

        day, ok3 = QInputDialog.getInt(self, "Thứ", "Nhập cột (0-6):", 0, 0, 6)
        if not ok3:
            return

        slot, ok4 = QInputDialog.getInt(self, "Tiết", "Nhập hàng (0-9):", 0, 0, 9)
        if not ok4:
            return

        success = self.controller.add_schedule(
            self.user_id, course, room, day, slot
        )

        if success:
            self.load_schedule()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể thêm lịch!")