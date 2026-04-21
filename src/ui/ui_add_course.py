from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel
)

class AddCourseDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thêm khóa học")
        self.setFixedSize(300, 250)

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Tên môn")

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Mã môn")

        self.prof_input = QLineEdit()
        self.prof_input.setPlaceholderText("Giảng viên")

        self.progress_input = QLineEdit()
        self.progress_input.setPlaceholderText("Tiến độ (%)")

        btn_add = QPushButton("Thêm")
        btn_add.clicked.connect(self.accept)

        layout.addWidget(QLabel("Nhập thông tin khóa học"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.code_input)
        layout.addWidget(self.prof_input)
        layout.addWidget(self.progress_input)
        layout.addWidget(btn_add)

    def get_data(self):
        return (
            self.name_input.text(),
            self.code_input.text(),
            self.prof_input.text(),
            int(self.progress_input.text() or 0)
        )