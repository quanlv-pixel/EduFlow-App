import sys
from PySide6.QtWidgets import QApplication
from src.ui.login import LoginDialog
from src.ui.dashboard import EduDashboard

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
        if hasattr(self, 'dashboard_window') and self.dashboard_window:
            self.dashboard_window.close()
            self.dashboard_window.deleteLater()

        self.login_window = LoginDialog()
        
        result = self.login_window.exec()
        
        if result == LoginDialog.Accepted:
            user_data = self.login_window.user_data
            self.show_dashboard(user_data)
        else:
            sys.exit(0)

    def show_dashboard(self, user_data):
        self.dashboard_window = EduDashboard(user_data)
        self.dashboard_window.logout_signal.connect(self.show_login)
        self.dashboard_window.show()
        if hasattr(self, 'login_window'):
            self.login_window.deleteLater()

    def run(self):
        self.show_login()
        return self.app.exec()

if __name__ == "__main__":
    controller = AppController()
    sys.exit(controller.run())