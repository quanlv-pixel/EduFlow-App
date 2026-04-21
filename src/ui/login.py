from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.user_data = None

        self.setObjectName("LoginWindow")
        self.setWindowTitle("Đăng nhập EduFlow")
        self.setFixedSize(350, 450)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel("Chào mừng bạn! 👋")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:bold;color:#2D60FF;")

        layout.addWidget(title)

        # Email
        layout.addWidget(QLabel("Email:"))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Nhập email...")
        layout.addWidget(self.user_input)

        # Password
        layout.addWidget(QLabel("Mật khẩu:"))
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Nhập mật khẩu...")
        layout.addWidget(self.pass_input)

        # Button
        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setObjectName("BtnLogin")
        self.btn_login.clicked.connect(self.handle_login)

        layout.addWidget(self.btn_login)

    # ================= LOGIN =================
    def handle_login(self):
        email = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        # validate
        if not email or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # call controller
        user = self.controller.login(email, password)

        if user:
            self.user_data = user
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", "Sai email hoặc mật khẩu!")