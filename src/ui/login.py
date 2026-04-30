from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self, controller):
        super().__init__()

        # ================= CONTROLLER =================
        self.controller = controller
        self.user_data = None

        # ================= WINDOW =================
        self.setObjectName("LoginWindow")
        self.setWindowTitle("Đăng nhập EduFlow")
        self.setFixedSize(360, 460)
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint
        )

        # ================= LAYOUT =================
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(18)

        # ================= TITLE =================
        title = QLabel("Chào mừng bạn! 👋")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size:22px;font-weight:bold;color:#2D60FF;"
        )

        subtitle = QLabel("Đăng nhập để tiếp tục sử dụng EduFlow")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color:#6F767E;font-size:13px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # ================= EMAIL =================
        layout.addWidget(QLabel("Email:"))

        self.user_input = QLineEdit()
        self.user_input.setObjectName("LoginInput")
        self.user_input.setPlaceholderText("example@email.com")
        layout.addWidget(self.user_input)

        # ================= PASSWORD =================
        layout.addWidget(QLabel("Mật khẩu:"))

        self.pass_input = QLineEdit()
        self.pass_input.setObjectName("LoginInput")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("••••••••")
        layout.addWidget(self.pass_input)

        # ================= BUTTON =================
        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setObjectName("BtnLogin")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setFixedHeight(42)

        layout.addWidget(self.btn_login)

        # 👉 THÊM NÚT ĐĂNG KÝ
        self.btn_goto_register = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        self.btn_goto_register.setObjectName("BtnRegisterLink") # Đặt tên để có thể style riêng
        self.btn_goto_register.setCursor(Qt.PointingHandCursor)
        self.btn_goto_register.setStyleSheet("color:#2D60FF; border:none; background:none; font-size:13px;")
        layout.addWidget(self.btn_goto_register)

        layout.addStretch()

        # ================= EVENTS =================
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_goto_register.clicked.connect(self.handle_goto_register)
        self.is_register_mode = False

        layout.addStretch()

        # ================= EVENTS =================
        self.btn_login.clicked.connect(self.handle_login)

        # 👉 ENTER để login
        self.pass_input.returnPressed.connect(self.handle_login)
        self.user_input.returnPressed.connect(self.pass_input.setFocus)

    # ================= LOGIN =================
    def handle_login(self):
        email = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        # ===== VALIDATE =====
        if not email or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # ===== UI LOCK =====
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Đang đăng nhập...")

        try:
            # ===== CALL CONTROLLER =====
            user = self.controller.login(email, password)

            if user:
                self.user_data = user
                self.accept()
            else:
                QMessageBox.warning(self, "Lỗi", "Sai email hoặc mật khẩu!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))

        finally:
            # ===== UI UNLOCK =====
            self.btn_login.setEnabled(True)
            self.btn_login.setText("Đăng nhập")
    
    def handle_goto_register(self):
        self.is_register_mode = True  
        self.reject()                 
    