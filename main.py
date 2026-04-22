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
    """Điều phối toàn bộ ứng dụng (App Level Controller)"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        # ===== LOAD STYLE =====
        try:
            with open("assets/style.qss", "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())
        except FileNotFoundError:
            print("⚠️ Không tìm thấy style.qss")

        # ===== CORE SERVICES =====
        self.db = Database()
        self.ai = AIEngine()

        # ===== CONTROLLERS =====
        self.auth_controller = AuthController(self.db)

        self.login_window = None
        self.dashboard_window = None

    # ================= LOGIN =================
    def show_login(self):
        if self.dashboard_window:
            self.dashboard_window.close()
            self.dashboard_window.deleteLater()

        self.login_window = LoginDialog(self.auth_controller)

        result = self.login_window.exec()

        if result == LoginDialog.Accepted:
            user = self.login_window.user_data
            self.show_dashboard(user)
        else:
            sys.exit(0)

    # ================= DASHBOARD =================
    def show_dashboard(self, user_data):
        self.dashboard_window = EduDashboard(
            user_info=user_data,
            db=self.db,
            ai=self.ai
        )

        self.dashboard_window.logout_signal.connect(self.show_login)
        self.dashboard_window.show()

        if self.login_window:
            self.login_window.deleteLater()

    # ================= RUN =================
    def run(self):
        self.show_login()
        return self.app.exec()


if __name__ == "__main__":
    controller = AppController()
    sys.exit(controller.run())