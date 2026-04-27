from PySide6.QtCore import QTimer
from datetime import datetime, date
from src.services.notifier import show_notification, send_email


class ScheduleNotifier:
    def __init__(self, controller, user_id):
        self.controller = controller
        self.user_id = user_id

        # chống spam
        self.sent_notifications = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_schedule)

        # check mỗi 30s (an toàn hơn 60s)
        self.timer.start(30000)

    def check_schedule(self):
        now = datetime.now()

        current_day = now.weekday()
        current_min = now.hour * 60 + now.minute

        schedules = self.controller.get_schedule(self.user_id) or []

        for s in schedules:
            if s.get("day") != current_day:
                continue

            start = s.get("start_time")
            if start is None:
                continue

            # tránh miss giờ
            if abs(start - current_min) <= 1:

                # key chống spam theo ngày
                key = (s["id"], date.today())

                if key in self.sent_notifications:
                    continue

                self.sent_notifications.add(key)
                self.notify(s)

    def notify(self, lesson):
        title = "📚 Đến giờ học!"
        message = f"{lesson.get('course', '')} - {lesson.get('room', '')}"

        # 🔔 popup
        show_notification(title, message)

        # 📧 email (có try để tránh crash)
        try:
            send_email(
                to_email="quanle19112007@gmail.com",
                subject="Nhắc lịch học",
                body=message
            )
        except Exception as e:
            print("❌ Send mail fail:", e)