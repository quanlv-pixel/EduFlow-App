from PySide6.QtCore import QTimer
from datetime import datetime, date

from src.services.notifier import (
    show_notification,
    send_email
)


class ScheduleNotifier:

    def __init__(self, controller, user_id, user_email=None):
        self.controller = controller
        self.user_id = user_id
        self.user_email = user_email

        # chống spam
        self.sent_notifications = set()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_schedule)

        # check mỗi 30 giây
        self.timer.start(30000)

        print("✅ ScheduleNotifier started")

    def check_schedule(self):

        try:
            now = datetime.now()

            current_day = now.weekday()
            current_min = now.hour * 60 + now.minute

            print(f"🕒 Checking schedules... {current_day} - {current_min}")

            schedules = self.controller.get_schedule(self.user_id) or []

            # reset cache mỗi ngày
            self._cleanup_old_notifications()

            for s in schedules:

                # FIX: convert day về int
                try:
                    lesson_day = int(s.get("day"))
                except:
                    continue

                # check đúng thứ
                if lesson_day != current_day:
                    continue

                start = s.get("start_time")

                if not start:
                    continue

                # convert HH:MM hoặc HH:MM:SS -> phút
                start_min = self._parse_time(start)

                if start_min is None:
                    continue

                # lệch tối đa 1 phút
                if abs(start_min - current_min) <= 1:

                    key = (
                        s.get("id"),
                        date.today()
                    )

                    if key in self.sent_notifications:
                        continue

                    self.sent_notifications.add(key)

                    self.notify(s)

        except Exception as e:
            print(f"❌ check_schedule error: {e}")

    def _parse_time(self, value):
        """Convert HH:MM hoặc HH:MM:SS -> phút"""

        try:

            if isinstance(value, str):

                parts = value.split(":")

                if len(parts) >= 2:
                    h = int(parts[0])
                    m = int(parts[1])

                    return h * 60 + m

            return int(value)

        except Exception:
            return None

    def _cleanup_old_notifications(self):
        """Xóa cache thông báo cũ"""

        today = date.today()

        self.sent_notifications = {
            k for k in self.sent_notifications
            if k[1] == today
        }

    def notify(self, lesson):

        title = "📚 Đến giờ học!"

        course = lesson.get("course", "Môn học")
        room = lesson.get("room", "Phòng học")

        message = f"{course} - {room}"

        print(f"🔔 Notify: {message}")

        # popup
        show_notification(title, message)

