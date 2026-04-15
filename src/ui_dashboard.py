import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QLineEdit, 
                             QProgressBar, QGridLayout, QStackedWidget)
from PySide6.QtCore import Qt, Signal
from src.ui_schedule import ScheduleWidget
from src.ui_summary import SummaryWidget
from src.ui_flashcard import FlashcardWidget
class DashMenuButton(QPushButton):
    def __init__(self, text, active=False):
        super().__init__(text)
        self.setObjectName("MenuBtn")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        if active:
            self.setChecked(True)
            self.setProperty("active", "true")

class EduDashboard(QMainWindow):
    # Tín hiệu phát đi khi nhấn Đăng xuất
    logout_signal = Signal()

    def __init__(self, user_info=None):
        super().__init__()
        
        self.user_info = user_info or {"name": "LÊ VĂN QUÂN", "email": "quanlv.25ai@vku.udn.vn"}
        self.setWindowTitle("EduFlow - Dashboard")
        self.resize(1300, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()

        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(35, 30, 35, 30)

        self.setup_header()

        self.pages = QStackedWidget()

        self.page_overview = self.create_overview_page()
        self.page_schedule = ScheduleWidget()
        self.page_flashcard = FlashcardWidget()
        self.page_summary = SummaryWidget()

        self.pages.addWidget(self.page_overview)
        self.pages.addWidget(self.page_schedule)
        self.pages.addWidget(self.page_flashcard)
        self.pages.addWidget(self.page_summary)
 
        self.content_layout.addWidget(self.pages)
        self.main_layout.addWidget(self.content_container)

    def setup_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(280)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(25, 40, 25, 25)

        logo = QLabel("📘 EduFlow")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D60FF; margin-bottom: 35px;")
        layout.addWidget(logo)

        self.btn_overview = DashMenuButton("  Tổng quan", active=True)
        self.btn_schedule = DashMenuButton("  Thời khóa biểu")
        self.btn_courses = DashMenuButton("  Khóa học")
        self.btn_flash = DashMenuButton("  Flashcards")
        self.btn_summary = DashMenuButton("  Tóm tắt AI")

        self.menu_group = [self.btn_overview, self.btn_schedule, self.btn_courses, self.btn_flash, self.btn_summary]
        for btn in self.menu_group:
            layout.addWidget(btn)
            btn.clicked.connect(self.handle_menu_click)

        layout.addStretch()

        # Phần User Info (Avatar + Tên)
        user_frame = QFrame()
        user_frame.setStyleSheet("border-top: 1px solid #F0F0F0; padding-top: 20px;")
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(0, 0, 0, 0)

        avatar_txt = self.user_info['name'][0].upper()
        lbl_avatar = QLabel(avatar_txt)
        lbl_avatar.setFixedSize(40, 40)
        lbl_avatar.setAlignment(Qt.AlignCenter)
        lbl_avatar.setStyleSheet("background-color: #535C67; color: white; border-radius: 20px; font-weight: bold;")

        info_v = QVBoxLayout()
        lbl_name = QLabel(self.user_info['name'])
        lbl_name.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E2328;")
        lbl_email = QLabel(self.user_info['email'])
        lbl_email.setStyleSheet("color: #6F767E; font-size: 11px;")
        info_v.addWidget(lbl_name)
        info_v.addWidget(lbl_email)
        info_v.setSpacing(2)

        user_layout.addWidget(lbl_avatar)
        user_layout.addLayout(info_v)
        layout.addWidget(user_frame)

        # Nút Đăng xuất màu đỏ
        self.btn_logout = QPushButton("↪ Đăng xuất")
        self.btn_logout.setStyleSheet("color: #FF4D4F; border: none; text-align: left; padding: 15px 0px; font-weight: bold;")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self.handle_logout) # Kết nối tới hàm logout
        layout.addWidget(self.btn_logout)

        self.main_layout.addWidget(sidebar)

    def setup_header(self):
        header_layout = QHBoxLayout()
        greeting_txt = "Chào mừng trở lại! 👋<br><span style='font-size: 12px; color: #6F767E;'>Hôm nay là Thứ Hai, ngày 6 tháng 4 năm 2026</span>"
        self.lbl_greeting = QLabel(greeting_txt)
        self.lbl_greeting.setTextFormat(Qt.RichText)
        self.lbl_greeting.setStyleSheet("font-size: 22px; font-weight: bold;")

        search_bar = QLineEdit()
        search_bar.setPlaceholderText(" 🔍 Tìm kiếm...")
        search_bar.setFixedWidth(280)
        search_bar.setStyleSheet("padding: 10px; border-radius: 10px; border: 1px solid #EAEAEA; background: white;")

        header_layout.addWidget(self.lbl_greeting)
        header_layout.addStretch()
        header_layout.addWidget(search_bar)
        self.content_layout.addLayout(header_layout)

    def create_overview_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(25)
        # (Giữ nguyên phần Card và Progress bar như cũ...)
        return page

    def handle_menu_click(self):
        sender = self.sender()
        for btn in self.menu_group:
            btn.setChecked(False)
            btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        sender.setChecked(True)
        sender.setProperty("active", "true")
        sender.style().unpolish(sender)
        sender.style().polish(sender)

        if sender == self.btn_overview: self.pages.setCurrentIndex(0)
        elif sender == self.btn_schedule: self.pages.setCurrentIndex(1)
        elif sender == self.btn_summary: self.pages.setCurrentIndex(2)
        elif sender == self.btn_flash:
            self.pages.setCurrentIndex(2)
        elif sender == self.btn_summary:
            self.pages.setCurrentIndex(3)

    def create_overview_page(self):
        """Tạo giao diện trang Tổng quan đầy đủ các thẻ trạng thái (Cards)"""
        page = QWidget()
        # Dùng QVBoxLayout để xếp hàng Thẻ Status lên trên, hàng Lịch học xuống dưới
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25) # Khoảng cách giữa các hàng

        # ---------------------------------------------------------
        # 1. HÀNG CARD TRẠNG THÁI (Màu xanh và màu trắng)
        # ---------------------------------------------------------
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20) # Khoảng cách giữa 2 Card

        # --- Thẻ "Khóa học đang học" (Màu xanh Royal) ---
        card_blue = QFrame()
        card_blue.setObjectName("CardBlue") # ID để QSS nhận diện màu xanh bo góc
        v1 = QVBoxLayout(card_blue)
        v1.setContentsMargins(20, 20, 20, 20)
        
        # Tiêu đề card
        lbl_c1_title = QLabel("📖 Khóa học đang học<br><b>Học kỳ 2</b>")
        lbl_c1_title.setTextFormat(Qt.RichText)
        lbl_c1_title.setStyleSheet("color: white; font-size: 14px;")
        v1.addWidget(lbl_c1_title)
        
        # Số liệu lớn
        lbl_c1_num = QLabel("3")
        lbl_c1_num.setStyleSheet("color: white; font-size: 48px; font-weight: bold; margin-top: 10px;")
        lbl_c1_num.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        v1.addWidget(lbl_c1_num)
        
        # --- Thẻ "Tiến độ trung bình" (Màu trắng) ---
        card_white = QFrame()
        card_white.setObjectName("CardWhite") # ID để QSS nhận diện màu trắng bo góc
        v2 = QVBoxLayout(card_white)
        v2.setContentsMargins(20, 20, 20, 20)
        
        # Tiêu đề card
        lbl_c2_title = QLabel("✅ Tiến độ trung bình")
        lbl_c2_title.setStyleSheet("color: #6F767E; font-size: 14px;")
        v2.addWidget(lbl_c2_title)
        
        # Số liệu lớn màu xanh
        lbl_c2_num = QLabel("78%")
        lbl_c2_num.setStyleSheet("color: #2D60FF; font-size: 48px; font-weight: bold; margin-top: 10px;")
        lbl_c2_num.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        v2.addWidget(lbl_c2_num)
        
        # Thêm 2 card vào layout hàng ngang
        cards_layout.addWidget(card_blue)
        cards_layout.addWidget(card_white)
        layout.addLayout(cards_layout)

        # ---------------------------------------------------------
        # 2. HÀNG NỘI DUNG CHI TIẾT (Lịch học và Tiến độ môn học)
        # ---------------------------------------------------------
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(20)
        
        # --- Card Lịch học hôm nay (Chiếm 2/3 chiều rộng) ---
        sch_card = QFrame()
        sch_card.setObjectName("CardWhite")
        sch_v = QVBoxLayout(sch_card)
        sch_v.setContentsMargins(20, 20, 20, 20)
        
        lbl_sch_title = QLabel("<b>Lịch học hôm nay</b>")
        lbl_sch_title.setStyleSheet("font-size: 16px;")
        sch_v.addWidget(lbl_sch_title)
        
        # Thông báo trống
        msg = QLabel("Không có lịch học nào hôm nay."); msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet("color: #999; font-size: 14px;")
        sch_v.addStretch(); sch_v.addWidget(msg); sch_v.addStretch()
        
        # --- Card Tiến độ học tập (Chiếm 1/3 chiều rộng) ---
        prog_card = QFrame()
        prog_card.setObjectName("CardWhite")
        prog_card.setFixedWidth(320) # Cố định chiều rộng giống ảnh
        prog_v = QVBoxLayout(prog_card)
        prog_v.setContentsMargins(20, 20, 20, 20)
        
        lbl_prog_title = QLabel("<b>Tiến độ học tập</b>")
        lbl_prog_title.setStyleSheet("font-size: 16px;")
        prog_v.addWidget(lbl_prog_title)
        
        # Danh sách môn học và Progress bar
        subjects = [("Cơ sở dữ liệu", 40), ("Lập trình Python", 65), ("Trí tuệ nhân tạo", 85)]
        for name, val in subjects:
            prog_v.addSpacing(15) # Khoảng cách
            
            # Tên môn và %
            lbl_sub = QLabel(f"{name} ({val}%)")
            lbl_sub.setStyleSheet("font-size: 13px; color: #1E2328;")
            prog_v.addWidget(lbl_sub)
            
            # Thanh tiến độ
            pb = QProgressBar()
            pb.setValue(val)
            pb.setFixedSize(280, 8) # Chiều dài và độ dày của thanh
            pb.setTextVisible(False) # Ẩn % chữ mặc định của QProgressBar
            prog_v.addWidget(pb)

        # Thêm 2 card dưới vào layout hàng ngang
        row2_layout.addWidget(sch_card, 2) # Tỷ lệ 2
        row2_layout.addWidget(prog_card, 1) # Tỷ lệ 1
        layout.addLayout(row2_layout)
        
        return page


    def handle_logout(self):
        """Phát tín hiệu logout và đóng cửa sổ hiện tại"""
        self.logout_signal.emit()
        self.close()