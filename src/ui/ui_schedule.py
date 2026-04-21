from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)
from PySide6.QtCore import Qt


class ScheduleWidget(QWidget):
    def __init__(self):
        super().__init__()

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

        btn_add = QPushButton("+ Thêm lịch học")
        btn_add.setObjectName("BtnAddSchedule")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFixedHeight(40)

        header_layout.addLayout(title_v)
        header_layout.addStretch()
        header_layout.addWidget(btn_add)

        main_layout.addLayout(header_layout)

        # ================= CARD =================
        card = QFrame()
        card.setObjectName("CardWhite")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)

        # Title nhỏ trong card
        lbl = QLabel("<b>Lịch học chi tiết</b>")
        lbl.setStyleSheet("font-size: 15px;")
        card_layout.addWidget(lbl)

        # ================= TABLE =================
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setRowCount(10)

        # Header
        days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        self.table.setHorizontalHeaderLabels(days)

        # Style table
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)

        self.table.setShowGrid(True)
        self.table.setStyleSheet("""
            QTableWidget::item {
                padding: 10px;
            }
        """)

        # Tăng chiều cao dòng cho giống UI
        for i in range(10):
            self.table.setRowHeight(i, 70)

        card_layout.addWidget(self.table)
        main_layout.addWidget(card)

        # ================= DATA =================
        self.load_sample_data()

    # ================= LOGIC =================
    def load_sample_data(self):
        lessons = [
            (0, 0, "Cơ sở dữ liệu", "A101"),
            (1, 1, "Python AI", "B202"),
        ]

        for row, col, name, room in lessons:
            self.add_lesson(row, col, name, room)

    def add_lesson(self, row, col, name, room):
        text = f"{name}\n{room}"

        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)

        # Style riêng từng cell
        item.setBackground(Qt.white)

        self.table.setItem(row, col, item)