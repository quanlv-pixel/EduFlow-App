from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QApplication, QMessageBox,
    QListWidget, QListWidgetItem
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

        self.current_filename = None
        self.current_content = None
        self.current_summary = None

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
        self.btn_save = QPushButton("💾 Lưu")
        self.btn_save.setObjectName("BtnAddSchedule")
        self.btn_save.setFixedHeight(45)
        self.btn_save.hide()
        self.btn_save.clicked.connect(self.handle_save)
        top_bar.addWidget(self.btn_save)

        self.saved_label = QLabel("<b>Tài liệu đã lưu</b>")
        layout.addWidget(self.saved_label)

        self.saved_list = QListWidget()
        self.saved_list.itemClicked.connect(
            self.open_saved_document
        )

        self.saved_list.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.saved_list.customContextMenuRequested.connect(
            self.show_document_menu
        )
        layout.addWidget(self.saved_list)

        self.load_saved_files()
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
            self.current_filename = filename
            self.current_content = content
            self.current_summary = summary

            self.btn_save.show()

            self.lbl_status.setText(tr("done", file=filename))

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            self.lbl_status.setText(tr("failed"))
            self.txt_summary.setText("")

        finally:
            self.btn_upload.setEnabled(True)
    
    def handle_save(self):
        try:
            if not self.current_summary:
                return

            title = self.extract_title(
                self.current_content,
                self.current_filename
            )

            self.controller.save(
                self.user_id,
                title,
                self.current_content,
                self.current_summary
            )

            QMessageBox.information(
                self,
                "Thành công",
                "Đã lưu tài liệu"
            )

            self.btn_save.hide()

            self.current_filename = None
            self.current_content = None
            self.current_summary = None

            self.txt_original.clear()
            self.txt_summary.clear()

            self.load_saved_files()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                str(e)
            )


    def extract_title(self, content, filename):
        lines = content.split("\n")

        for line in lines[:5]:
            line = line.strip()

            if len(line) > 5:
                return line[:60]

        return filename


    def load_saved_files(self):
        self.saved_list.clear()

        docs = self.controller.get_documents(
            self.user_id
        )

        for doc in docs:

            item = QListWidgetItem(
                doc["filename"]
            )

            item.setData(
                Qt.UserRole,
                doc["id"]
            )

            self.saved_list.addItem(
                item
            )
    def open_saved_document(self,item):
        doc_id = item.data(
            Qt.UserRole
        )

        data = self.controller.get_document_detail(
            doc_id
        )

        if not data:
            return

        self.txt_original.setText(
            data["content"]
        )

        self.txt_summary.setText(
            data["summary_text"]
        )

        self.lbl_status.setText(
            f"Đã mở: {data['filename']}"
        )
    def show_document_menu(self,pos):
        item = self.saved_list.itemAt(pos)

        if not item:
            return

        from PySide6.QtWidgets import QMenu

        menu = QMenu()

        delete_action = menu.addAction(
            "🗑 Xóa"
        )

        action = menu.exec(
            self.saved_list.mapToGlobal(pos)
        )

        if action == delete_action:

            doc_id = item.data(
                Qt.UserRole
            )

            reply = QMessageBox.question(
                self,
                "Xác nhận",
                "Xóa tài liệu này?"
            )

            if reply == QMessageBox.Yes:

                self.controller.delete_document(
                    doc_id
                )

                self.load_saved_files()

                self.txt_original.clear()
                self.txt_summary.clear()

                self.lbl_status.setText(
                    "Đã xóa"
                )