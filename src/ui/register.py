from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class RegisterDialog(QDialog):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.setObjectName("LoginWindow")
        self.setWindowTitle("Đăng ký EduFlow")
        self.setFixedSize(360, 680)
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(12)

        # ── TITLE ──
        title = QLabel("Tạo tài khoản mới ✨")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:bold;color:#2D60FF;")

        subtitle = QLabel("Tham gia cộng đồng học tập EduFlow")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color:#6F767E;font-size:13px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        # ── HỌ VÀ TÊN ──
        layout.addWidget(QLabel("Họ và tên:"))
        self.name_input = QLineEdit()
        self.name_input.setObjectName("LoginInput")
        self.name_input.setPlaceholderText("Nguyễn Văn A")
        self.name_input.setFixedHeight(42)
        layout.addWidget(self.name_input)

        # ── TÊN TÀI KHOẢN ──
        layout.addWidget(QLabel("Tên tài khoản:"))
        self.username_input = QLineEdit()
        self.username_input.setObjectName("LoginInput")
        self.username_input.setPlaceholderText("nguyenvana123  (không dấu, không khoảng trắng)")
        self.username_input.setFixedHeight(42)
        layout.addWidget(self.username_input)

        # ── EMAIL ──
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setObjectName("LoginInput")
        self.email_input.setPlaceholderText("example@email.com")
        self.email_input.setFixedHeight(42)
        layout.addWidget(self.email_input)

        # ── MẬT KHẨU ──
        layout.addWidget(QLabel("Mật khẩu:"))
        self.pass_input = QLineEdit()
        self.pass_input.setObjectName("LoginInput")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("••••••••  (ít nhất 6 ký tự)")
        self.pass_input.setFixedHeight(42)
        layout.addWidget(self.pass_input)

        # ── XÁC NHẬN MẬT KHẨU ──
        layout.addWidget(QLabel("Xác nhận mật khẩu:"))
        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setObjectName("LoginInput")
        self.confirm_pass_input.setEchoMode(QLineEdit.Password)
        self.confirm_pass_input.setPlaceholderText("••••••••")
        self.confirm_pass_input.setFixedHeight(42)
        layout.addWidget(self.confirm_pass_input)

        layout.addSpacing(4)

        # ── NÚT ĐĂNG KÝ ──
        self.btn_register = QPushButton("Đăng ký ngay")
        self.btn_register.setObjectName("BtnLogin")
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.setFixedHeight(42)
        layout.addWidget(self.btn_register)

        # ── BACK TO LOGIN ──
        self.btn_back = QPushButton("Đã có tài khoản? Đăng nhập")
        self.btn_back.setStyleSheet(
            "color:#2D60FF; border:none; background:none; font-size:13px;"
        )
        self.btn_back.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.btn_back)

        layout.addStretch()

        # ── EVENTS ──
        self.btn_register.clicked.connect(self.handle_register)
        self.btn_back.clicked.connect(self.reject)
        self.confirm_pass_input.returnPressed.connect(self.handle_register)

    def handle_register(self):
        name     = self.name_input.text().strip()
        username = self.username_input.text().strip()
        email    = self.email_input.text().strip()
        password = self.pass_input.text()
        confirm  = self.confirm_pass_input.text()

        # ── VALIDATE ──
        if not all([name, username, email, password, confirm]):
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng điền đầy đủ tất cả các trường!")
            return

        if " " in username:
            QMessageBox.warning(self, "Tên tài khoản không hợp lệ",
                                "Tên tài khoản không được chứa khoảng trắng!")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Tên tài khoản không hợp lệ",
                                "Tên tài khoản phải có ít nhất 3 ký tự!")
            return

        if "@" not in email:
            QMessageBox.warning(self, "Email không hợp lệ", "Vui lòng nhập đúng định dạng email!")
            return

        if password != confirm:
            QMessageBox.warning(self, "Mật khẩu không khớp",
                                "Mật khẩu xác nhận không khớp!")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Mật khẩu quá ngắn",
                                "Mật khẩu phải có ít nhất 6 ký tự!")
            return

        # ── UI LOCK ──
        self.btn_register.setEnabled(False)
        self.btn_register.setText("Đang xử lý...")

        try:
            result = self.controller.register(name, username, email, password)

            if result is True:
                QMessageBox.information(self, "Thành công 🎉",
                                        "Đăng ký tài khoản thành công!\nHãy đăng nhập để tiếp tục.")
                self.accept()
            elif result == "email":
                QMessageBox.warning(self, "Email đã tồn tại",
                                    f"Email «{email}» đã được đăng ký.\nVui lòng dùng email khác.")
                self.email_input.setFocus()
                self.email_input.selectAll()
            elif result == "username":
                QMessageBox.warning(self, "Tên tài khoản đã tồn tại",
                                    f"Tên tài khoản «{username}» đã được sử dụng.\nVui lòng chọn tên khác.")
                self.username_input.setFocus()
                self.username_input.selectAll()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể tạo tài khoản. Vui lòng thử lại.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))

        finally:
            self.btn_register.setEnabled(True)
            self.btn_register.setText("Đăng ký ngay")