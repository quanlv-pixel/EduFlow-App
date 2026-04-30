import sys
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

# UI
from src.ui.login import LoginDialog
from src.ui.register import RegisterDialog
from src.ui.dashboard import EduDashboard

# SERVICES
from src.models.database import Database
from src.services.ai_engine import AIEngine

# CONTROLLERS
from src.controllers.auth_controller import AuthController


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        # load style
        try:
            with open("assets/style.qss", "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())
        except:
            pass

        # 👉 INIT CORE
        self.db = Database()
        self.ai = AIEngine()

        # 👉 CONTROLLER
        self.auth_controller = AuthController(self.db)

        self.dashboard = None 
        self.login_window = None

    def show_login(self):
            if self.dashboard:
                self.dashboard.hide()
                self.dashboard.deleteLater()
                self.dashboard = None

            self.login_window = LoginDialog(self.auth_controller)

            # Thực thi Dialog
            result = self.login_window.exec()

            if result == QDialog.Accepted:
                user = self.login_window.user_data
                self.show_dashboard(user)
            elif self.login_window.is_register_mode:
                self.show_register() 
                sys.exit()
    
    def show_register(self):
        # Tạo cửa sổ đăng ký
        self.register_window = RegisterDialog(self.auth_controller) #[cite: 1]
        
        if self.register_window.exec():
            QMessageBox.information(None, "Thành công", "Đăng ký thành công! Hãy đăng nhập.")
            self.show_login()
        else:
           
            self.show_login()

    def show_dashboard(self, user):
    # 👉 đóng login trước
        if self.login_window:
            self.login_window.hide()
            self.login_window.deleteLater()
            self.login_window = None

        self.dashboard = EduDashboard(user, self.db, self.ai)
        self.dashboard.logout_signal.connect(self.show_login)
        self.dashboard.show()

    def run(self):
        self.show_login()
        return self.app.exec()


if __name__ == "__main__":
    controller = AppController()
    sys.exit(controller.run())