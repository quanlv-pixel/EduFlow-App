class ScheduleController:
    def __init__(self, db):
        self.db = db

    def get_schedule(self, user_id):
        return self.db.get_schedule(user_id)

    def add_schedule(self, user_id, course, room, day, start, end):
        if end <= start:
            return False

        return self.db.add_schedule(user_id, course, room, day, start, end)
    
    def delete_schedule(self, user_id, day, start):
        return self.db.delete_schedule(user_id, day, start)