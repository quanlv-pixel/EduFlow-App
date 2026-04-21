from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox)
from PySide6.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setObjectName("LoginWindow")
        self.setWindowTitle("Đăng nhập EduFlow")
        self.setFixedSize(350, 450)
        self.setWindowFlags(
    Qt.Window 
    | Qt.WindowTitleHint 
    | Qt.WindowCloseButtonHint
    )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(20)

        # Logo/Title
        title = QLabel("Chào mừng bạn! 👋")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2D60FF;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Ô nhập tài khoản (Email/Username)
        self.user_input = QLineEdit()
        self.user_input.setObjectName("LoginInput")
        self.user_input.setPlaceholderText("Email hoặc tên đăng nhập")
        layout.addWidget(QLabel("Tài khoản:"))
        layout.addWidget(self.user_input)

        # Ô nhập mật khẩu
        self.pass_input = QLineEdit()
        self.pass_input.setObjectName("LoginInput")
        self.pass_input.setPlaceholderText("Mật khẩu")
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Mật khẩu:"))
        layout.addWidget(self.pass_input)

        # Nút đăng nhập
        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setObjectName("BtnLogin")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.clicked.connect(self.check_login)
        layout.addWidget(self.btn_login)

        # Biến lưu thông tin người dùng sau khi đăng nhập thành công
        self.user_data = None

    def check_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        # Giả lập tài khoản mặc định
        if username == "admin" and password == "123":
            self.user_data = {"name": "QUẢN TRỊ VIÊN", "email": "admin@eduflow.com"}
            self.accept()
        # Giả lập đăng nhập bằng tài khoản của Quân
        elif username == "quanlv.25ai" or "quanlv" in username:
            self.user_data = {"name": "LÊ VĂN QUÂN", "email": "quanlv.25ai@vku.udn.vn"}
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", "Tài khoản hoặc mật khẩu không đúng!")