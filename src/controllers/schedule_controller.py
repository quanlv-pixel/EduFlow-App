class ScheduleController:
    def __init__(self, db):
        self.db = db

    def get_schedule(self, user_id):
        query = "SELECT * FROM schedule WHERE user_id=%s"
        return self.db.execute(query, (user_id,), fetch=True)

    def add_schedule(self, user_id, course, room, day, slot):
        query = """
        INSERT INTO schedule (user_id, course, room, col, row)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute(query, (user_id, course, room, day, slot))