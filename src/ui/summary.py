import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QApplication, QMessageBox
)
from PySide6.QtCore import Qt


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
        self.btn_upload.setFixedSize(220, 45)
        self.btn_upload.clicked.connect(self.handle_upload)

        self.lbl_status = QLabel("Chưa có tài liệu nào")

        top_bar.addWidget(self.btn_upload)
        top_bar.addWidget(self.lbl_status)
        top_bar.addStretch()

        layout.addLayout(top_bar)

        # ===== DISPLAY =====
        display = QHBoxLayout()

        self.txt_original = QTextEdit()
        self.txt_summary = QTextEdit()

        self.txt_summary.setReadOnly(True)

        display.addWidget(self.txt_original)
        display.addWidget(self.txt_summary)

        layout.addLayout(display)

    # ================= HANDLE =================
    def handle_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file", "", "Files (*.pdf *.docx)"
        )

        if not file_path:
            return

        self.btn_upload.setEnabled(False)
        self.lbl_status.setText("⌛ Đang xử lý...")
        self.txt_summary.setText("🤖 AI đang xử lý...")

        QApplication.processEvents()

        try:
            # 1. đọc file
            content = self.controller.read_file(file_path)
            self.txt_original.setText(content)

            # 2. gọi AI
            summary = self.controller.summarize(content)
            self.txt_summary.setText(summary)

            # 3. lưu DB
            self.controller.save(
                self.user_id,
                os.path.basename(file_path),
                content,
                summary
            )

            self.lbl_status.setText("✅ Hoàn thành")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))

        finally:
            self.btn_upload.setEnabled(True)