class AuthController:
    def __init__(self, db):
        self.db = db

    def login(self, email, password):
        return self.db.get_user(email, password)