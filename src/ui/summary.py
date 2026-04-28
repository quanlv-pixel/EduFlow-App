from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QApplication, QMessageBox
)
from PySide6.QtCore import Qt
import os
from src.ui.settings_widget import tr, LanguageManager


class SummaryWidget(QWidget):
    def __init__(self, controller, user_id):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.controller = controller
        self.user_id = user_id

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # ===== TITLE =====
        self.title = QLabel()
        self.title.setStyleSheet("font-size:22px;font-weight:bold;color:#2D60FF;")
        layout.addWidget(self.title)

        top_bar = QHBoxLayout()

        self.btn_upload = QPushButton()
        self.btn_upload.setObjectName("BtnAddSchedule")
        self.btn_upload.setFixedHeight(45)
        self.btn_upload.clicked.connect(self.handle_upload)

        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color:#6F767E;")

        top_bar.addWidget(self.btn_upload)
        top_bar.addWidget(self.lbl_status)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        # ===== LEFT =====
        self.lbl_original = QLabel()
        self.txt_original = QTextEdit()
        self.txt_original.setObjectName("SummaryOriginal")

        # ===== RIGHT =====
        self.lbl_summary = QLabel()
        self.txt_summary = QTextEdit()
        self.txt_summary.setObjectName("SummaryResult")
        self.txt_summary.setReadOnly(True)

        display = QHBoxLayout()

        left = QVBoxLayout()
        left.addWidget(self.lbl_original)
        left.addWidget(self.txt_original)

        right = QVBoxLayout()
        right.addWidget(self.lbl_summary)
        right.addWidget(self.txt_summary)

        display.addLayout(left)
        display.addLayout(right)
        layout.addLayout(display)

        # 👉 set text lần đầu
        self._retranslate()

    def _retranslate(self):
        self.title.setText(tr("summary_title"))
        self.btn_upload.setText(tr("upload_btn"))
        self.lbl_status.setText(tr("no_file"))

        self.lbl_original.setText(f"<b>{tr('original')}</b>")
        self.lbl_summary.setText(f"<b>{tr('summary')}</b>")

        self.txt_original.setPlaceholderText(tr("original_placeholder"))
        self.txt_summary.setPlaceholderText(tr("summary_placeholder"))

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

        # RESET UI
        self.txt_original.clear()
        self.txt_summary.clear()

        self.btn_upload.setEnabled(False)
        self.lbl_status.setText(tr("reading", file=filename))
        self.txt_summary.setText(tr("processing"))

        QApplication.processEvents()

        try:
            # ===== READ FILE =====
            content = self.controller.read_file(file_path)

            if not content or content.startswith("❌") or len(content.strip()) < 10:
                raise ValueError(content or "File không hợp lệ!")

            # 🔥 GIỚI HẠN TEXT (tránh AI chết)
            content = content[:20000]

            self.txt_original.setText(content)

            # ===== AI =====
            self.lbl_status.setText(tr("ai_working"))
            QApplication.processEvents()

            # 🔥 RETRY LOGIC (QUAN TRỌNG)
            summary = None
            for i in range(3):
                summary = self.controller.summarize(content)

                if summary and not summary.startswith("❌"):
                    break

                QApplication.processEvents()

            # Nếu vẫn lỗi sau 3 lần
            if not summary or summary.startswith("❌"):
                summary = "⚠️ AI đang quá tải, vui lòng thử lại sau!"

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

            self.lbl_status.setText(tr("done", file=filename))

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            self.lbl_status.setText(tr("failed"))
            self.txt_summary.setText("")

        finally:
            self.btn_upload.setEnabled(True)