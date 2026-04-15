import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QLabel, QFileDialog)
from PySide6.QtCore import Qt
from src.ai_engine import AIEngine

class SummaryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ai = AIEngine()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # 1. Tiêu đề trang
        title = QLabel("🤖 Trợ lý Tóm tắt Tài liệu")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2D60FF;")
        layout.addWidget(title)

        # 2. Thanh điều khiển (Chọn file)
        top_bar = QHBoxLayout()
        self.btn_upload = QPushButton("📂 Chọn file PDF/Word")
        self.btn_upload.setFixedSize(220, 45)
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        self.btn_upload.setStyleSheet("""
            QPushButton { background-color: #2D60FF; color: white; border-radius: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #1A4BDB; }
        """)
        self.btn_upload.clicked.connect(self.handle_upload)
        
        self.lbl_status = QLabel("Chưa có tài liệu nào được chọn")
        self.lbl_status.setStyleSheet("color: #6F767E;")
        
        top_bar.addWidget(self.btn_upload)
        top_bar.addWidget(self.lbl_status)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # 3. Vùng hiển thị nội dung (Chia làm 2 cột)
        display_layout = QHBoxLayout()
        
        # Cột trái: Nội dung gốc
        left_v = QVBoxLayout()
        left_v.addWidget(QLabel("<b>Nội dung gốc:</b>"))
        self.txt_original = QTextEdit()
        self.txt_original.setPlaceholderText("Văn bản từ tài liệu sẽ hiện ở đây...")
        self.txt_original.setStyleSheet("border-radius: 12px; border: 1px solid #DDD; background: white; padding: 10px;")
        left_v.addWidget(self.txt_original)
        
        # Cột phải: Bản tóm tắt
        right_v = QVBoxLayout()
        right_v.addWidget(QLabel("<b>AI Tóm tắt:</b>"))
        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        self.txt_summary.setPlaceholderText("Bản tóm tắt sẽ hiện ở đây...")
        self.txt_summary.setStyleSheet("border-radius: 12px; border: 1px solid #2D60FF; background: #F4F7FF; padding: 10px;")
        right_v.addWidget(self.txt_summary)
        
        display_layout.addLayout(left_v, 1)
        display_layout.addLayout(right_v, 1)
        layout.addLayout(display_layout)

    def handle_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn tài liệu", "", "Tài liệu (*.pdf *.docx)")
        
        if file_path:
            self.lbl_status.setText(f"⌛ Đang đọc: {os.path.basename(file_path)}")
            self.txt_summary.setText("🤖 Gemini đang suy nghĩ, Quân đợi xíu nhé...")
            
            try:
                # Đọc nội dung
                if file_path.endswith('.pdf'):
                    content = self.ai.read_pdf(file_path)
                else:
                    content = self.ai.read_docx(file_path)
                
                self.txt_original.setText(content)
                
                # Gọi AI tóm tắt
                summary = self.ai.get_summary(content)
                self.txt_summary.setText(summary)
                self.lbl_status.setText(f"✅ Đã tóm tắt xong: {os.path.basename(file_path)}")
                
            except Exception as e:
                self.txt_summary.setText(f"❌ Có lỗi xảy ra: {str(e)}")
                self.lbl_status.setText("❌ Lỗi xử lý")