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
        # Cấu trúc lưu trữ OTP an toàn: { email: {"code": str, "timestamp": float} }
        self.otps = {}  
        
        # Cấu hình Email (Sử dụng App Password của Gmail)
        self.EMAIL_SENDER = os.getenv("EMAIL_SENDER")  # Thay bằng email của bạn hoặc cấu hình đọc từ .env
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")   # Thay bằng mật khẩu ứng dụng hoặc cấu hình đọc từ .env

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
        """Tạo mã OTP ngẫu nhiên gồm 6 chữ số và lưu trữ kèm timestamp."""
        otp_code = "".join([secrets.choice("0123456789") for _ in range(6)])
        # Lưu rõ ràng dưới dạng dictionary để tránh lỗi AttributeError khi truy xuất
        self.otps[email.strip()] = {
            "code": otp_code,
            "timestamp": time.time()
        }
        return otp_code

    def send_otp_email(self, target_email, otp_code):
        """Gửi mã OTP thật qua Email sử dụng luồng kết nối SMTP bảo mật."""
        msg = MIMEMultipart()
        msg["From"] = self.EMAIL_SENDER
        msg["To"] = target_email.strip()
        msg["Subject"] = f"[{otp_code}] - Mã OTP đặt lại mật khẩu"

        body = f"""
        <html>
        <body>
            <h2 style='color: #2D60FF;'>EduFlow Password Reset</h2>
            <p>Xin chào,</p>
            <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản EduFlow của mình.</p>
            <p>Mã OTP của bạn là: <b style='font-size: 20px; color: #2D60FF;'>{otp_code}</b></p>
            <p>Mã này có hiệu lực trong vòng 5 phút (300 giây). Vui lòng không chia sẻ mã này với bất kỳ ai.</p>
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
        """Xác thực mã OTP kèm theo kiểm tra thời gian hết hạn (5 phút)."""
        email_key = email.strip()
        
        # Kiểm tra xem email có tồn tại trong kho lưu trữ OTP không
        if email_key not in self.otps:
            return False
            
        otp_data = self.otps[email_key]
        
        # Kiểm tra tính toàn vẹn dữ liệu đề phòng nhận diện nhầm kiểu dữ liệu tuple
        if not isinstance(otp_data, dict):
            return False
            
        saved_code = otp_data.get("code")
        timestamp = otp_data.get("timestamp", 0)
        
        # Kiểm tra mã OTP có khớp không và thời gian hiệu lực trong vòng 5 phút (300 giây)
        if saved_code == str(code).strip() and (time.time() - timestamp <= 300):
            return True
            
        return False

    def reset_password(self, email, new_password):
        """Tiến hành cập nhật mật khẩu mới vào Database và xóa mã OTP."""
        email_key = email.strip()
        
        # Tiến hành cập nhật mật khẩu mới vào cơ sở dữ liệu
        success = self.db.update_password(email_key, new_password)
        
        # Xóa mã OTP khỏi hàng đợi sau khi đổi mật khẩu thành công để bảo mật
        if success and email_key in self.otps:
            del self.otps[email_key]
            
        return success