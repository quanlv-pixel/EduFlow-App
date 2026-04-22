from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QApplication, QMessageBox
)
from PySide6.QtCore import Qt
import os


class SummaryWidget(QWidget):
    def __init__(self, controller, user_id):
        super().__init__()

        self.controller = controller
        self.user_id = user_id

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # ===== TITLE =====
        title = QLabel("🤖 Trợ lý Tóm tắt Tài liệu")
        title.setStyleSheet("font-size:22px;font-weight:bold;color:#2D60FF;")
        layout.addWidget(title)

        # ===== TOP BAR =====
        top_bar = QHBoxLayout()

        self.btn_upload = QPushButton("📂 Chọn file PDF/Word")
        self.btn_upload.setObjectName("BtnAddSchedule")
        self.btn_upload.setFixedHeight(45)
        self.btn_upload.clicked.connect(self.handle_upload)

        self.lbl_status = QLabel("Chưa có tài liệu nào")
        self.lbl_status.setStyleSheet("color:#6F767E;")

        top_bar.addWidget(self.btn_upload)
        top_bar.addWidget(self.lbl_status)
        top_bar.addStretch()

        layout.addLayout(top_bar)

        # ===== DISPLAY =====
        display = QHBoxLayout()

        # LEFT
        left = QVBoxLayout()
        left.addWidget(QLabel("<b>Nội dung gốc</b>"))

        self.txt_original = QTextEdit()
        self.txt_original.setPlaceholderText("Nội dung file sẽ hiển thị ở đây...")
        left.addWidget(self.txt_original)

        # RIGHT
        right = QVBoxLayout()
        right.addWidget(QLabel("<b>Tóm tắt AI</b>"))

        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        self.txt_summary.setPlaceholderText("Kết quả AI...")
        right.addWidget(self.txt_summary)

        display.addLayout(left)
        display.addLayout(right)

        layout.addLayout(display)

    # ================= HANDLE =================
    def handle_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file",
            "",
            "Tài liệu (*.pdf *.docx)"
        )

        if not file_path:
            return

        filename = os.path.basename(file_path)

        # ===== RESET UI =====
        self.txt_original.clear()
        self.txt_summary.clear()

        self.btn_upload.setEnabled(False)
        self.lbl_status.setText(f"⌛ Đang đọc: {filename}")

        QApplication.processEvents()

        try:
            # ===== READ FILE =====
            content = self.controller.read_file(file_path)

            if not content or len(content.strip()) < 10:
                raise ValueError("File không có nội dung hợp lệ!")

            self.txt_original.setText(content)

            # ===== AI =====
            self.lbl_status.setText("🤖 AI đang xử lý...")
            QApplication.processEvents()

            summary = self.controller.summarize(content)

            if not summary:
                raise ValueError("AI không trả về kết quả!")

            self.txt_summary.setText(summary)

            # ===== SAVE =====
            try:
                self.controller.save(
                    self.user_id,
                    filename,
                    content,
                    summary
                )
            except Exception as e:
                print("⚠️ Lỗi lưu DB:", e)

            self.lbl_status.setText(f"✅ Hoàn thành: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            self.lbl_status.setText("❌ Thất bại")

        finally:
            self.btn_upload.setEnabled(True)