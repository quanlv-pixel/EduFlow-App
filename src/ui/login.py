from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QStackedWidget, QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt, QThread, Signal


class EmailWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, controller, email, otp):
        super().__init__()
        self.controller = controller
        self.email = email
        self.otp = otp

    def run(self):
        try:
            self.controller.send_otp_email(self.email, self.otp)
            self.finished.emit(True, "Mã OTP đã được gửi đến email của bạn!")
        except Exception as e:
            self.finished.emit(False, str(e))


class ForgotPasswordDialog(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.target_email = None

        self.setWindowTitle("Quên mật khẩu")
        self.setFixedSize(380, 420)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)

        # Title
        self.title = QLabel("Khôi phục mật khẩu")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2D60FF;")
        self.layout.addWidget(self.title)

        # Stacked Widget for Steps
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        self.init_step1()
        self.init_step2()
        self.init_step3()

    def init_step1(self):
        # Step 1: Nhập Email/Username
        self.step1_widget = QWidget()
        layout = QVBoxLayout(self.step1_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        desc = QLabel("Nhập email hoặc tên đăng nhập để nhận mã OTP.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #6F767E; font-size: 13px;")
        layout.addWidget(desc)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Email hoặc Username")
        self.id_input.setObjectName("LoginInput")
        layout.addWidget(self.id_input)

        self.btn_send_otp = QPushButton("Gửi mã OTP")
        self.btn_send_otp.setObjectName("BtnLogin")
        self.btn_send_otp.setCursor(Qt.PointingHandCursor)
        self.btn_send_otp.clicked.connect(self.handle_send_otp)
        layout.addWidget(self.btn_send_otp)

        layout.addStretch()
        self.stack.addWidget(self.step1_widget)

    def init_step2(self):
        # Step 2: Nhập OTP
        self.step2_widget = QWidget()
        layout = QVBoxLayout(self.step2_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.otp_desc = QLabel("Vui lòng nhập mã 6 số đã gửi tới email của bạn.")
        self.otp_desc.setWordWrap(True)
        self.otp_desc.setStyleSheet("color: #6F767E; font-size: 13px;")
        layout.addWidget(self.otp_desc)

        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Mã OTP (6 chữ số)")
        self.otp_input.setObjectName("LoginInput")
        self.otp_input.setAlignment(Qt.AlignCenter)
        self.otp_input.setMaxLength(6)
        layout.addWidget(self.otp_input)

        self.btn_verify_otp = QPushButton("Xác thực")
        self.btn_verify_otp.setObjectName("BtnLogin")
        self.btn_verify_otp.setCursor(Qt.PointingHandCursor)
        self.btn_verify_otp.clicked.connect(self.handle_verify_otp)
        layout.addWidget(self.btn_verify_otp)

        layout.addStretch()
        self.stack.addWidget(self.step2_widget)

    def init_step3(self):
        # Step 3: Đặt lại mật khẩu
        self.step3_widget = QWidget()
        layout = QVBoxLayout(self.step3_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        desc = QLabel("Nhập mật khẩu mới cho tài khoản của bạn.")
        desc.setStyleSheet("color: #6F767E; font-size: 13px;")
        layout.addWidget(desc)

        self.new_pass = QLineEdit()
        self.new_pass.setPlaceholderText("Mật khẩu mới")
        self.new_pass.setEchoMode(QLineEdit.Password)
        self.new_pass.setObjectName("LoginInput")
        layout.addWidget(self.new_pass)

        self.confirm_pass = QLineEdit()
        self.confirm_pass.setPlaceholderText("Xác nhận mật khẩu")
        self.confirm_pass.setEchoMode(QLineEdit.Password)
        self.confirm_pass.setObjectName("LoginInput")
        layout.addWidget(self.confirm_pass)

        self.btn_reset = QPushButton("Đặt lại mật khẩu")
        self.btn_reset.setObjectName("BtnLogin")
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.clicked.connect(self.handle_reset_password)
        layout.addWidget(self.btn_reset)

        layout.addStretch()
        self.stack.addWidget(self.step3_widget)

    def handle_send_otp(self):
            email = self.id_input.text().strip()
            if not email or "@" not in email:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập định dạng Email hợp lệ!")
                return

            self.target_email = email
            
            # FIX TẠI ĐÂY: Tự tạo chuỗi OTP 6 số ngẫu nhiên từ 100000 đến 999999
            import secrets
            otp = str(secrets.randbelow(900000) + 100000)

            self.btn_send_otp.setEnabled(False)
            self.btn_send_otp.setText("Đang gửi...")

            # Chạy Thread gửi mail ngầm
            self.worker = EmailWorker(self.controller, self.target_email, otp)
            self.worker.finished.connect(self.on_otp_sent)
            self.worker.start()
            
    def on_otp_sent(self, success, message):
        self.btn_send_otp.setEnabled(True)
        self.btn_send_otp.setText("Gửi mã OTP")
        if success:
            QMessageBox.information(self, "Thành công", message)
            # Dòng này sẽ kích hoạt QStackedWidget chuyển sang màn hình nhập mã OTP (Index 1)
            self.stack.setCurrentIndex(1) 
        else:
            QMessageBox.critical(self, "Lỗi kết nối", f"Không thể gửi mail: {message}")

    def on_email_sent(self, success, message):
        self.btn_send_otp.setEnabled(True)
        self.btn_send_otp.setText("Gửi mã OTP")

        if success:
            QMessageBox.information(self, "Thành công", message)
            self.otp_desc.setText(f"Mã OTP đã được gửi đến:\n{self.target_email}")
            self.stack.setCurrentIndex(1)
        else:
            QMessageBox.critical(self, "Lỗi", f"Không thể gửi email: {message}")

    def handle_verify_otp(self):
        code = self.otp_input.text().strip()
        if self.controller.verify_otp(self.target_email, code):
            self.stack.setCurrentIndex(2)
        else:
            QMessageBox.warning(self, "Lỗi", "Mã OTP không chính xác hoặc đã hết hạn!")

    def handle_reset_password(self):
        p1 = self.new_pass.text().strip()
        p2 = self.confirm_pass.text().strip()

        if not p1 or not p2:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ mật khẩu!")
            return
        if p1 != p2:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        if self.controller.reset_password(self.target_email, p1):
            QMessageBox.information(self, "Thành công", "Mật khẩu của bạn đã được thay đổi!")
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", "Có lỗi xảy ra khi đặt lại mật khẩu.")


class LoginDialog(QDialog):
    def __init__(self, controller):
        super().__init__()

        # ================= CONTROLLER =================
        self.controller = controller
        self.user_data = None

        # ================= WINDOW =================
        self.setObjectName("LoginWindow")
        self.setWindowTitle("Đăng nhập EduFlow")
        self.setFixedSize(360, 520) # Tăng chiều cao để chứa thêm nút
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

        # ================= EMAIL / USERNAME =================
        layout.addWidget(QLabel("Email hoặc tên tài khoản:"))

        self.user_input = QLineEdit()
        self.user_input.setObjectName("LoginInput")
        self.user_input.setPlaceholderText("example@email.com  hoặc  nguyenvana123")
        layout.addWidget(self.user_input)

        # ================= PASSWORD =================
        layout.addWidget(QLabel("Mật khẩu:"))

        self.pass_input = QLineEdit()
        self.pass_input.setObjectName("LoginInput")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("••••••••")
        layout.addWidget(self.pass_input)

        # 👉 THÊM NÚT QUÊN MẬT KHẨU
        forgot_layout = QHBoxLayout()
        forgot_layout.addStretch()
        self.btn_forgot = QPushButton("Quên mật khẩu?")
        self.btn_forgot.setCursor(Qt.PointingHandCursor)
        self.btn_forgot.setStyleSheet("color:#2D60FF; border:none; background:none; font-size:12px; font-weight:500;")
        
        # CHẶN KHÔNG CHO NÚT NÀY TỰ KÍCH HOẠT KHI NHẤN ENTER
        self.btn_forgot.setAutoDefault(False)
        self.btn_forgot.setDefault(False)
        
        # (Xóa dòng clicked.connect ở đây vì đã có ở phía dưới)
        forgot_layout.addWidget(self.btn_forgot)
        layout.addLayout(forgot_layout)

        # ================= BUTTON ĐĂNG NHẬP =================
        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setObjectName("BtnLogin")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setFixedHeight(42)
        
        # ĐẶT NÚT ĐĂNG NHẬP LÀM NÚT MẶC ĐỊNH DUY NHẤT KHI NHẤN ENTER
        self.btn_login.setDefault(True)

        layout.addWidget(self.btn_login)

        # 👉 THÊM NÚT ĐĂNG KÝ
        self.btn_goto_register = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        self.btn_goto_register.setObjectName("BtnRegisterLink") 
        self.btn_goto_register.setCursor(Qt.PointingHandCursor)
        self.btn_goto_register.setStyleSheet("color:#2D60FF; border:none; background:none; font-size:13px;")
        
        # CHẶN KHÔNG CHO NÚT ĐĂNG KÝ TỰ KÍCH HOẠT KHI NHẤN ENTER
        self.btn_goto_register.setAutoDefault(False)
        
        layout.addWidget(self.btn_goto_register)

        # ================= EVENTS =================
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_goto_register.clicked.connect(self.handle_goto_register)
        self.btn_forgot.clicked.connect(self.handle_forgot_password)
        self.is_register_mode = False

        layout.addStretch()

        # 👉 ENTER để login
        
        self.user_input.returnPressed.connect(self.pass_input.setFocus)

    # ================= FORGOT PASSWORD =================
    def handle_forgot_password(self):
        dialog = ForgotPasswordDialog(self.controller)
        dialog.exec()

    def open_forgot_password_dialog(self):
        """Hàm xử lý hiển thị cửa sổ Quên mật khẩu"""
        dialog = ForgotPasswordDialog(self.controller)
        dialog.exec()

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
                msgBox = QMessageBox(self)
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setWindowTitle("Lỗi")
                msgBox.setText("Sai email hoặc mật khẩu!")
                # Ép màu chữ thành trắng để nổi bật trên nền tối
                msgBox.setStyleSheet("QLabel { color: black; text-align: center; font-weight: bold;}") 
                msgBox.exec()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", str(e))

        finally:
            # ===== UI UNLOCK =====
            self.btn_login.setEnabled(True)
            self.btn_login.setText("Đăng nhập")
    
    def handle_goto_register(self):
        self.is_register_mode = True  
        self.reject()