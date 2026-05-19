import smtplib
import ssl
import secrets
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AuthController:
    def __init__(self, db):
        self.db = db
        # Cấu trúc lưu trữ OTP: { email: {"code": str, "timestamp": float} }
        self.otps = {}  
        
        # Đồng bộ cấu hình Gmail gửi OTP
        self.EMAIL_SENDER = os.getenv("EMAIL_SENDER")
        self.EMAIL_PASSWORD = os.getenv("APP_PASSWORD")

    def login(self, identifier: str, password: str):
        """Đăng nhập bằng email hoặc username."""
        return self.db.get_user(identifier.strip(), password)

    def register(self, name: str, username: str, email: str, password: str):
        """Đăng ký tài khoản mới."""
        result = self.db.register_user(
            name.strip(),
            username.strip(),
            email.strip(),
            password
        )
        return result

    def get_user_email(self, identifier):
        """Kiểm tra user tồn tại và trả về email chính xác từ DB."""
        # Phương thức này giả định db có hàm check hoặc trả về email từ username/email nhập vào
        # Để tạm thời hoạt động, ta coi identifier chính là email hoặc gọi hàm tương ứng từ DB của bạn
        try:
            if hasattr(self.db, "get_user_email_by_identifier"):
                return self.db.get_user_email_by_identifier(identifier.strip())
            return identifier.strip() # Fallback nếu nhập thẳng email
        except:
            return identifier.strip()

    def send_otp_email(self, target_email, otp_code):
        """Tạo giao diện HTML và tiến hành gửi mã OTP qua Gmail."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 Mã Xác Thực EduFlow: {otp_code}"
        msg["From"] = self.EMAIL_SENDER
        msg["To"] = target_email

        html = f"""
        <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; padding: 20px;">
                <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                    <h2 style="color: #2D60FF; margin-top: 0; text-align: center;">EduFlow</h2>
                    <p style="color: #4A5568; font-size: 16px;">Chào bạn,</p>
                    <p style="color: #4A5568; font-size: 14px; line-height: 1.6;">Bạn đã yêu cầu khôi phục mật khẩu tài khoản EduFlow. Vui lòng sử dụng mã xác thực OTP dưới đây để tiến hành thiết lập lại mật khẩu mới:</p>
                    <div style="background: #edf2f7; border-radius: 8px; padding: 15px; text-align: center; margin: 25px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #1a202c;">{otp_code}</span>
                    </div>
                    <p style="color: #e53e3e; font-size: 12px; font-style: italic; text-align: center;">Lưu ý: Mã OTP này có hiệu lực trong vòng 5 phút và chỉ sử dụng được 1 lần.</p>
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 25px 0;">
                    <p style="color: #a0aec0; font-size: 12px; text-align: center; margin-bottom: 0;">Đây là email tự động, vui lòng không phản hồi email này.</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))
        context = ssl.create_default_context()

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(self.EMAIL_SENDER, self.EMAIL_PASSWORD)
            server.send_message(msg)

        # Lưu lại vào bộ nhớ để xác thực
        self.otps[target_email.strip()] = {
            "code": str(otp_code),
            "timestamp": time.time()
        }

    def verify_otp(self, email, code):
        """Xác thực mã OTP kèm theo kiểm tra thời gian hết hạn (5 phút)."""
        email_key = email.strip()
        if email_key not in self.otps:
            return False
            
        otp_data = self.otps[email_key]
        if not isinstance(otp_data, dict):
            return False
            
        saved_code = otp_data.get("code")
        timestamp = otp_data.get("timestamp", 0)
        
        if saved_code == str(code).strip() and (time.time() - timestamp <= 300):
            return True
        return False

    def reset_password(self, email, new_password):
        """Tiến hành cập nhật mật khẩu mới vào Database và xóa mã OTP."""
        email_key = email.strip()
        success = self.db.update_password(email_key, new_password)
        if success and email_key in self.otps:
            del self.otps[email_key]
        return success