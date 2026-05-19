import smtplib
import ssl
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AuthController:
    def __init__(self, db):
        self.db = db
        self.otps = {}  # {email: otp_code}
        
        # Cấu hình Email (Sử dụng App Password của Gmail)
        self.EMAIL_SENDER = "EMAIL_SENDER"  # Thay bằng email của bạn
        self.EMAIL_PASSWORD = "APP_PASSWORD"   # Thay bằng mật khẩu ứng dụng

    def login(self, identifier: str, password: str):
        """Đăng nhập bằng email hoặc username."""
        return self.db.get_user(identifier.strip(), password)

    def register(self, name: str, username: str, email: str, password: str):
        """
        Đăng ký tài khoản mới.
        Trả về: True = OK | "email" = email trùng | "username" = username trùng
        """
        result = self.db.register_user(
            name.strip(),
            username.strip(),
            email.strip(),
            password
        )
        return result

    def get_user_email(self, identifier):
        """Kiểm tra user tồn tại và lấy email."""
        return self.db.get_user_email_by_identifier(identifier.strip())

    def generate_otp(self, email):
        """Tạo mã OTP 6 số và lưu tạm."""
        otp = "".join([secrets.choice("0123456789") for _ in range(6)])
        self.otps[email] = otp
        return otp

    def send_otp_email(self, target_email, otp_code):
        """Gửi email chứa mã OTP sử dụng smtplib."""
        msg = MIMEMultipart()
        msg["From"] = self.EMAIL_SENDER
        msg["To"] = target_email
        msg["Subject"] = "EduFlow - Mã OTP đặt lại mật khẩu"

        body = f"""
        <html>
        <body>
            <h2 style='color: #2D60FF;'>EduFlow Password Reset</h2>
            <p>Xin chào,</p>
            <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản EduFlow của mình.</p>
            <p>Mã OTP của bạn là: <b style='font-size: 20px; color: #2D60FF;'>{otp_code}</b></p>
            <p>Mã này có hiệu lực trong vòng 5 phút. Vui lòng không chia sẻ mã này với bất kỳ ai.</p>
            <br>
            <p>Trân trọng,<br>Đội ngũ EduFlow</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(self.EMAIL_SENDER, self.EMAIL_PASSWORD)
            server.send_message(msg)

    def verify_otp(self, email, code):
        """Xác thực mã OTP."""
        if email in self.otps and self.otps[email] == code:
            # Xóa OTP sau khi dùng xong (tùy chọn, ở đây ta giữ lại để reset_password biết email nào đang được reset)
            return True
        return False

    def reset_password(self, email, new_password):
        """Cập nhật mật khẩu mới vào DB."""
        if email not in self.otps:
            return False
        
        success = self.db.update_password(email, new_password)
        if success:
            del self.otps[email]
        return success