class ScheduleController:
    def __init__(self, db):
        self.db = db

    def get_schedule(self, user_id):
        return self.db.get_schedule(user_id)

    def add_schedule(self, user_id, course, room, day, start, end):
        """
        start / end: phút tính từ 0:00
        Ví dụ: 7:30 → 450,  8:30 → 510
        """
        if end <= start:
            return False

        # Tối thiểu 15 phút
        if (end - start) < 15:
            return False

        return self.db.add_schedule(user_id, course, room, day, start, end)
    def delete_schedule(self, schedule_id):
        return self.db.delete_schedule(schedule_id)