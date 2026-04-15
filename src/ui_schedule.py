from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt

class ScheduleWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header của mục thời khóa biểu
        header_layout = QHBoxLayout()
        title_v = QVBoxLayout()
        title = QLabel("Thời khóa biểu")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        subtitle = QLabel("Xem và quản lý thời gian biểu hàng tuần.")
        subtitle.setStyleSheet("color: #6F767E;")
        title_v.addWidget(title)
        title_v.addWidget(subtitle)
        
        btn_add = QPushButton("+ Thêm lịch học")
        btn_add.setObjectName("BtnAddSchedule")
        btn_add.setCursor(Qt.PointingHandCursor)

        header_layout.addLayout(title_v)
        header_layout.addStretch()
        header_layout.addWidget(btn_add)
        layout.addLayout(header_layout)

        # Tạo bảng thời khóa biểu
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setRowCount(10) # 10 khung giờ/tiết học
        
        # Thiết lập tiêu đề cột (Thứ 2 - CN)
        days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        self.table.setHorizontalHeaderLabels(days)
        
        # Cho các cột tự động giãn đều
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False) # Ẩn số dòng bên trái
        
        # Dữ liệu mẫu (Quân có thể load từ database sau này)
        self.add_lesson(0, 0, "Cơ sở dữ liệu\nPhòng A101")
        self.add_lesson(1, 1, "Python AI\nPhòng B202")

        layout.addWidget(self.table)

    def add_lesson(self, row, col, text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, col, item)