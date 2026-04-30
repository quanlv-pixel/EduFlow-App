from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class RegisterDialog(QDialog):
    def __init__(self, controller):
        super().__init__()

        # ================= CONTROLLER =================
        self.controller = controller

        # ================= WINDOW =================
        self.setObjectName("LoginWindow")  # Dùng chung style với Login
        self.setWindowTitle("Đăng ký EduFlow")
        self.setFixedSize(360, 620)
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
        )

        # ================= LAYOUT =================
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(15)

        # ================= TITLE =================
        title = QLabel("Tạo tài khoản mới ✨")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size:22px;font-weight:bold;color:#2D60FF;"
        )

        subtitle = QLabel("Tham gia cộng đồng học tập EduFlow")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color:#6F767E;font-size:13px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # ================= NAME =================
        layout.addWidget(QLabel("Họ và tên:"))
        self.name_input = QLineEdit()
        self.name_input.setObjectName("LoginInput")
        self.name_input.setPlaceholderText("Nguyễn Văn A")
        self.name_input.setFixedHeight(42)
        layout.addWidget(self.name_input)

        # ================= EMAIL =================
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setObjectName("LoginInput")
        self.email_input.setPlaceholderText("example@email.com")
        self.email_input.setFixedHeight(42)
        layout.addWidget(self.email_input)

        # ================= PASSWORD =================
        layout.addWidget(QLabel("Mật khẩu:"))
        self.pass_input = QLineEdit()
        self.pass_input.setObjectName("LoginInput")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("••••••••")
        self.pass_input.setFixedHeight(42)
        layout.addWidget(self.pass_input)

        # ================= CONFIRM PASSWORD =================
        layout.addWidget(QLabel("Xác nhận mật khẩu:"))
        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setObjectName("LoginInput")
        self.confirm_pass_input.setEchoMode(QLineEdit.Password)
        self.confirm_pass_input.setPlaceholderText("••••••••")
        self.confirm_pass_input.setFixedHeight(42)
        layout.addWidget(self.confirm_pass_input)

        # ================= BUTTON REGISTER =================
        self.btn_register = QPushButton("Đăng ký ngay")
        self.btn_register.setObjectName("BtnLogin") # Dùng chung style xanh dương
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.setFixedHeight(42)
        layout.addWidget(self.btn_register)

        # ================= BACK TO LOGIN =================
        self.btn_back = QPushButton("Đã có tài khoản? Đăng nhập")
        self.btn_back.setStyleSheet("color:#2D60FF; border:none; background:none; font-size:13px;")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.btn_back)

        layout.addStretch()

        # ================= EVENTS =================
        self.btn_register.clicked.connect(self.handle_register)
        self.btn_back.clicked.connect(self.reject) # Đóng dialog để quay lại login

    def handle_register(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_input.text().strip()
        confirm_password = self.confirm_pass_input.text().strip()

        # ===== VALIDATE =====
        if not all([name, email, password, confirm_password]):
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
            return

        # ===== UI LOCK =====
        self.btn_register.setEnabled(False)
        self.btn_register.setText("Đang xử lý...")

        try:
            # Giả sử controller có hàm register(name, email, password)
            # Hàm này gọi db.register_user(...)
            success = self.controller.register(name, email, password)

            if success:
                QMessageBox.information(self, "Thành công", "Đăng ký tài khoản thành công!")
                self.accept()
            else:
                QMessageBox.warning(self, "Lỗi", "Email này đã được sử dụng!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))

        finally:
            self.btn_register.setEnabled(True)
            self.btn_register.setText("Đăng ký ngay")