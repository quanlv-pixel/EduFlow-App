import sys
from PySide6.QtWidgets import QApplication
from src.ui_login import LoginDialog
from src.ui_dashboard import EduDashboard

class AppController:
    """Điều phối luồng chạy giữa Login và Dashboard"""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        
        # Nạp stylesheet chung
        try:
            with open("assets/style.qss", "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Cảnh báo: Không tìm thấy file style.qss")

        self.current_window = None

    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        self.login_window = LoginDialog()
        # exec() trả về Accepted nếu người dùng login thành công
        if self.login_window.exec() == LoginDialog.Accepted:
            self.show_dashboard(self.login_window.user_data)
        else:
            sys.exit(0) # Thoát nếu người dùng đóng cửa sổ login

    def show_dashboard(self, user_data):
        """Hiển thị dashboard và lắng nghe tín hiệu logout"""
        self.dashboard_window = EduDashboard(user_data)
        # Khi Dashboard phát tín hiệu logout, gọi lại hàm show_login
        self.dashboard_window.logout_signal.connect(self.show_login)
        self.dashboard_window.show()

    def run(self):
        self.show_login()
        return self.app.exec()

if __name__ == "__main__":
    controller = AppController()
    sys.exit(controller.run())