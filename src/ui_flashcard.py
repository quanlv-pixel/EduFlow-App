import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter, QPen, QBrush

class CourseCard(QWidget):
    def __init__(self, name, code, professor, progress):
        super().__init__()
        self.setFixedHeight(220)
        self.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
            QWidget:hover {
                border: 1px solid #3b82f6;
                box-shadow: 0 10px 15px rgba(0, 0, 0, 0.08);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header card
        header = QHBoxLayout()
        icon = QLabel("📘")
        icon.setFont(QFont("", 32))
        header.addWidget(icon)

        status = QLabel("Đang học")
        status.setStyleSheet("""
            background: #ecfdf5; 
            color: #10b981; 
            padding: 4px 14px; 
            border-radius: 9999px; 
            font-size: 12px;
        """)
        header.addStretch()
        header.addWidget(status)
        layout.addLayout(header)

        # Title & info
        title = QLabel(name)
        title.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(title)

        info = QLabel(f"{code} • {professor}")
        info.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(info)

        layout.addStretch()

        # Progress
        prog_layout = QHBoxLayout()
        prog_label = QLabel("Tiến độ")
        prog_label.setStyleSheet("color: #475569;")
        prog_layout.addWidget(prog_label)

        percent = QLabel(f"{progress}%")
        percent.setStyleSheet("font-weight: bold;")
        prog_layout.addStretch()
        prog_layout.addWidget(percent)
        layout.addLayout(prog_layout)

        # Progress bar
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            background: #e2e8f0;
            border-radius: 3px;
        """)
        layout.addWidget(self.progress_bar)

        # Vẽ progress thật (sử dụng paintEvent)
        self.progress = progress

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.progress_bar)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background đã có trong stylesheet
        # Vẽ phần tiến độ
        rect = self.progress_bar.rect()
        fill_width = int(rect.width() * self.progress / 100)

        painter.setBrush(QBrush(QColor("#3b82f6")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, fill_width, rect.height(), 3, 3)


class FlashcardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f8fafc; font-family: 'Segoe UI', Arial;")
        self.setStyleSheet("background: #f8fafc; font-family: 'Segoe UI', Arial;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        title = QLabel("📚 FlashCards")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #1E2328;"
        )
        main_layout.addWidget(title)

        subtitle = QLabel("Danh sách các môn học trong học kỳ này")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px;")
        main_layout.addWidget(subtitle)
       