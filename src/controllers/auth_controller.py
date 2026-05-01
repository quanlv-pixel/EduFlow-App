class AuthController:
    def __init__(self, db):
        self.db = db

    def login(self, identifier: str, password: str):
        """Đăng nhập bằng email hoặc username."""
        return self.db.get_user(identifier.strip(), password)

    def register(self, name: str, username: str, email: str, password: str):
        """
        Đăng ký tài khoản mới.
        Trả về: True = OK | "email" = email trùng | "username" = username trùng
        """
        result = self.db.register_user(
            name.strip(),
            username.strip(),
            email.strip(),
            password
        )
        return result