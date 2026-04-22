import sys
from PySide6.QtWidgets import QApplication

# UI
from src.ui.login import LoginDialog
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
    # 👉 đóng dashboard nếu còn
        if self.dashboard:
            self.dashboard.hide()
            self.dashboard.deleteLater()
            self.dashboard = None

        self.login_window = LoginDialog(self.auth_controller)

        if self.login_window.exec():
            user = self.login_window.user_data
            self.show_dashboard(user)
        else:
            sys.exit()

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