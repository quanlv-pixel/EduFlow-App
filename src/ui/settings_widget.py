import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QFrame, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QObject


# ─────────────────────────────────────────────
#  TRANSLATIONS
# ─────────────────────────────────────────────
TRANSLATIONS = {
    "vi": {
        # Settings page
        "settings_title":       "⚙️ Cài đặt",
        "appearance_title":     "🎨 Giao diện",
        "appearance_desc":      "Chuyển đổi giữa chủ đề sáng và tối.",
        "dark_mode_on":         "🌙 Chế độ tối",
        "dark_mode_off":        "☀️ Chế độ sáng",
        "ai_title":             "🤖 Cài đặt AI",
        "ai_desc":              "Số lượng flashcard tối đa được tạo mỗi phiên AI.",
        "ai_limit_lbl":         "Giới hạn flashcard:",
        "ai_limit_placeholder": "Nhập số (VD: 10)",
        "data_title":           "🗂 Dữ liệu",
        "data_desc":            "Xuất hoặc nhập dữ liệu flashcard dạng JSON.",
        "export_btn":           "⬆ Xuất Flashcards",
        "import_btn":           "⬇ Nhập Flashcards",
        "save_btn":             "💾 Lưu cài đặt",
        "language_title":       "🌐 Ngôn ngữ",
        "language_desc":        "Chọn ngôn ngữ hiển thị cho toàn bộ ứng dụng.",
        
        # Dialogs
        "invalid_input":        "Đầu vào không hợp lệ",
        "invalid_input_msg":    "Giới hạn flashcard phải là số nguyên dương.",
        "saved_title":          "Đã lưu",
        "saved_msg":            "Đã lưu cài đặt!\n\n• Giới hạn AI: {limit}\n• Chế độ tối: {dark}",
        "dark_on":              "Bật",
        "dark_off":             "Tắt",
        "export_ok":            "Xuất thành công",
        "export_ok_msg":        "Đã xuất flashcards tới:\n{path}",
        "export_fail":          "Xuất thất bại",
        "import_ok":            "Nhập thành công",
        "import_ok_msg":        "Đã tải {count} flashcard(s) từ:\n{path}",
        "import_fail":          "Nhập thất bại",
        
        # Sidebar
        "menu_overview":        "Tổng quan",
        "menu_schedule":        "Thời khóa biểu",
        "menu_courses":         "Khóa học",
        "menu_flash":           "Flashcards",
        "menu_summary":         "Tóm tắt AI",
        "menu_todo":            "Todo List",
        "menu_settings":        "Cài đặt",
        "menu_grades":           "Bảng điểm",
        "logout":               "↪ Đăng xuất",
        
        # Summary
        "summary_title":        "🤖 Trợ lý Tóm tắt Tài liệu",
        "upload_btn":           "📂 Chọn file PDF/Word",
        "no_file":              "Chưa có tài liệu nào",
        "reading":              "⌛ Đang đọc: {file}",
        "processing":           "⏳ Đang xử lý...",
        "ai_working":           "🤖 AI đang tóm tắt...",
        "done":                 "✅ Hoàn thành: {file}",
        "failed":               "❌ Thất bại",
        "original":             "Nội dung gốc",
        "summary":              "Tóm tắt AI",

        # Todo List
        "todo_title":           "Todo List",
        "todo_placeholder":     "✏️ Thêm nhiệm vụ mới...",
        "todo_add":             "+ Thêm",
        "todo_today_list":      "Danh sách nhiệm vụ hôm nay",
        "todo_clear":           "🗑 Xóa hoàn thành",
        "todo_empty":           "Chưa có nhiệm vụ nào.\nHãy thêm nhiệm vụ đầu tiên! 🎯",
        "todo_total":           "Tổng nhiệm vụ",
        "todo_done":            "Hoàn thành",
        "todo_remain":          "Còn lại",

        # Flash Card
        "flash_title":          "📚 Flashcards AI",
        "flash_subtitle":       "Tạo flashcard từ tài liệu hoặc nội dung",
        "flash_from_file":      "📂 Tạo từ tài liệu",
        "flash_from_text":      "💬 Tạo từ nội dung",
        "flash_view":           "📖 Xem flashcards",
        "flash_back":           "← Quay lại",
        "flash_empty":          "Chưa có flashcard nào",
        "flash_loading_file":   "📂 Đang đọc file...",
        "flash_ai_generating":  "🤖 AI đang tạo flashcards...",
        "flash_error_load":     "Lỗi load",
        "flash_error_ai":       "Lỗi AI",
        "flash_error":          "Lỗi",
        "flash_input_title":    "Nhập nội dung",
        "flash_input_label":    "Nhập nội dung cần học:",
        "flash_show_answer":    "👁 Xem đáp án",
        "flash_back_answer":    "↩️ Quay lại",

        # DashBoard
        "greeting_morning":     "Chào buổi sáng",
        "greeting_afternoon":   "Chào buổi chiều",
        "greeting_evening":     "Chào buổi tối",

        "today_schedule":       "Lịch học hôm nay",
        "no_schedule":          "Không có lịch học nào hôm nay.",
        "study_progress":       "Tiến độ học tập",
        "courses_studying":     "Khóa học đang học",
        "semester":             "Học kỳ 2",
        "avg_progress":         "Tiến độ trung bình",

        # Schedule
        "schedule_title":       "📅 Thời khóa biểu",
        "schedule_subtitle":    "Quản lý lịch học của bạn",
        "schedule_add":         "+ Thêm lịch",
        "schedule_delete":      "🗑 Xóa",
        "schedule_delete_hint": "Nhấn vào lịch để xóa",

        "choose_day":           "Chọn thứ",
        "choose_day_label":     "Chọn ngày:",

        "input_course":         "Môn học",
        "input_course_label":   "Nhập tên môn:",
        # Days of week
        "mon":                  "Thứ Hai",
        "tue":                  "Thứ Ba",
        "wed":                  "Thứ Tư",
        "thu":                  "Thứ Năm",
        "fri":                  "Thứ Sáu",
        "sat":                  "Thứ Bảy",
        "sun":                  "Chủ Nhật",
        
        # COURSE
        # Course UI (bổ sung)
        "course_title":         "Khóa học của tôi",
        "course_subtitle":      "Quản lý danh sách các môn học trong học kỳ này.",
        "course_add":           "+ Thêm khóa học",
        "course_empty":         "Chưa có khóa học nào 😢",
        "course_status_learning": "Đang học",
        "progress":             "Tiến độ",

        # Input dialog
        "input_course":         "Tên môn",
        "input_course_label":   "Nhập tên môn học:",

        "input_code":           "Mã môn",
        "input_code_label":     "Nhập mã môn:",

        "input_prof":           "Giảng viên",
        "input_prof_label":     "Nhập tên giảng viên:",

        "error_add_course":     "Không thêm được khóa học!",

        # Course Detail
        "course_detail_back":   "Quay lại danh sách",
        "course_detail_content":"Nội dung học tập",
        "course_detail_no_data":"Không tìm thấy dữ liệu khóa học.",
        "course_detail_no_lessons": "Chưa có bài học nào.",
        "course_detail_description": "Mô tả khóa học",
        "course_detail_resources":   "Nguồn tài liệu",
        "course_detail_continue":    "Tiếp tục học",
        "course_detail_continue_desc": "Bạn đang dừng lại ở giai đoạn đầu của khóa học. Bắt đầu bài học đầu tiên ngay nhé!",
        "course_detail_open_latest": "Mở bài học mới nhất",
        "course_detail_flash_created": "Đã tạo {count} flashcard!",
        "course_detail_professor":   "Giảng viên:",
        "course_detail_completed":   "✅ Hoàn thành",
        "course_detail_no_ai":       "Không có AI để tạo flashcard.",
        "course_detail_this_course": "khóa học này",
        "badge_title":               "🎉 Hoàn thành khóa học!",
        "badge_congrats":            "Xuất sắc!",
        "badge_msg":                 "Bạn đã hoàn thành toàn bộ\nkhóa học <b>{course_name}</b>.\nHãy tiếp tục phát huy nhé!",
        "badge_certificate":         "✅  Đã nhận Chứng chỉ Hoàn thành",
        "badge_btn":                 "Tuyệt vời! 🎊",
        "lesson_open_btn":           "🔗 Mở",
        "lesson_flash_btn":          "⚡ Flashcard",
        "error": "Lỗi",
        "stat_lessons":         "BÀI GIẢNG",
        "stat_exercises":       "BÀI TẬP",
        "stat_progress":        "TIẾN ĐỘ",

        # Grades
        "grade_title":          "📊 Bảng điểm",
        "grade_add_subject":    "＋ Thêm môn",
        "grade_student":        "🎒 Học sinh",
        "grade_university":     "🎓 Sinh viên",

        "subject":              "Môn học",
        "credits":              "TC",
        "tx_score":             "Điểm TX",
        "gk_score":             "Điểm GK",
        "ck_score":             "Điểm CK",
        "avg_score":            "Điểm TB",
        "avg":                  "ĐTB",
        "rank":                 "Xếp loại",
        "letter":               "Chữ",
        "gpa4":                 "GPA 4.0",

        "edit":                 "Sửa",
        "delete":               "Xóa",
        "confirm":              "Xác nhận",
        "confirm_delete_msg":   "Bạn có chắc muốn xóa môn này?",
        "add_subject": "Thêm môn học",
        "subject_name": "Tên môn học",
        "hs_mode": "Học sinh",
        "sv_mode": "Sinh viên",

        "hs_subject_dialog_title": "Thêm môn học (Học sinh)",
        "sv_subject_dialog_title": "Thêm môn học (Sinh viên)",

        "tx_label": "Điểm TX (hệ số 1):",
        "gk_label": "Điểm GK (hệ số 2):",
        "ck_label": "Điểm CK (hệ số 3):",
        "attendance_label": "Chuyên cần – tùy chọn:",
        "assignment_label": "Bài tập – tùy chọn:",
        "midterm_label": "Giữa kỳ:",
        "final_label": "Cuối kỳ:",
        "tx_score_label": "Điểm TX (hệ số 1)",
        "gk_score_label": "Điểm GK (hệ số 2)",
        "ck_score_label": "Điểm CK (hệ số 3)",

        "cc_optional": "Chuyên cần – tùy chọn",
        "bt_optional": "Bài tập – tùy chọn",
        "gk_score": "Giữa kỳ",
        "ck_score": "Cuối kỳ",
        "save": "Lưu",
        "cancel": "Hủy",
        "credits": "Tín chỉ",

        # Flashcard extra
        "flash_click_answer":      "👆 Click để xem đáp án",
        "flash_click_question":    "👆 Click để xem câu hỏi",
        "flash_ai_error_empty":    "AI không tạo được flashcard.\nThử lại hoặc viết yêu cầu cụ thể hơn.",
        "flash_new_saved":         "✅  Đã tạo và lưu {saved} flashcard mới!",
        "flash_empty_msg":         "Chưa có flashcard nào.\nHãy tạo mới bằng 2 nút bên trên!",
        "flash_card_file_title":   "Tải lên tài liệu",
        "flash_card_file_desc":    "Upload file PDF hoặc DOCX.\nAI đọc nội dung và tự tạo flashcard.",
        "flash_card_file_btn":     "📂  Chọn file",
        "flash_card_topic_title":  "Nhập yêu cầu",
        "flash_card_topic_desc":   "Gõ chủ đề muốn ôn tập.\nVí dụ: \"Tạo flashcard về Python cơ bản\".",
        "flash_card_topic_btn":    "✍️  Nhập yêu cầu",
        "flash_saved_label":       "📚 Flashcard đã lưu",
        "flash_clear_all":         "🗑  Xóa tất cả",
        "flash_confirm_clear":     "Xác nhận xóa",
        "flash_confirm_clear_msg": "Xóa toàn bộ flashcard đã lưu?\nHành động này không thể hoàn tác.",
        "flash_choose_file":       "Chọn tài liệu học tập",
        "flash_file_error_title":  "Lỗi đọc file",
        "flash_file_error_msg":    "Không đọc được file.",
        "flash_prompt_title":      "Tạo Flashcard bằng AI",
        "flash_prompt_label":      "🤖 Nhập yêu cầu cho AI",
        "flash_prompt_subtitle":   "Mô tả chủ đề bạn muốn ôn tập. AI sẽ tự tạo flashcard phù hợp.",
        "flash_prompt_examples":   "💡  \"Tạo flashcard về Python cơ bản\"  •  \"Ôn tập Giải tích\"  •  \"Lý thuyết đồ thị\"",
        "flash_prompt_placeholder": "Nhập yêu cầu của bạn ở đây...",
        "flash_prompt_generate":   "✨  Tạo ngay",
    },
    "en": {
        # Settings page
        "settings_title":       "⚙️ Settings",
        "appearance_title":     "🎨 Appearance",
        "appearance_desc":      "Switch between light and dark theme.",
        "dark_mode_on":         "🌙 Toggle Dark Mode",
        "dark_mode_off":        "☀️ Light Mode",
        "ai_title":             "🤖 AI Settings",
        "ai_desc":              "Maximum number of flashcards generated per AI session.",
        "ai_limit_lbl":         "Flashcard limit:",
        "ai_limit_placeholder": "Enter number (e.g. 10)",
        "data_title":           "🗂 Data",
        "data_desc":            "Export or import your flashcard data as JSON.",
        "export_btn":           "⬆ Export Flashcards",
        "import_btn":           "⬇ Import Flashcards",
        "save_btn":             "💾 Save Settings",
        "language_title":       "🌐 Language",
        "language_desc":        "Select the display language for the entire application.",
        
        # Dialogs
        "invalid_input":        "Invalid Input",
        "invalid_input_msg":    "Flashcard limit must be a positive integer.",
        "saved_title":          "Saved",
        "saved_msg":            "Settings saved!\n\n• AI flashcard limit: {limit}\n• Dark mode: {dark}",
        "dark_on":              "On",
        "dark_off":             "Off",
        "export_ok":            "Export Successful",
        "export_ok_msg":        "Flashcards exported to:\n{path}",
        "export_fail":          "Export Failed",
        "import_ok":            "Import Successful",
        "import_ok_msg":        "Loaded {count} flashcard(s) from:\n{path}",
        "import_fail":          "Import Failed",
        
        # Sidebar
        "menu_overview":        "Overview",
        "menu_schedule":        "Schedule",
        "menu_courses":         "Courses",
        "menu_flash":           "Flashcards",
        "menu_summary":         "AI Summary",
        "menu_todo":            "Todo List",
        "menu_settings":        "Settings",
        "menu_grades":           "Transcript",
        "logout":               "↪ Logout",
        
        # Summary
        "summary_title":        "🤖 Document Summary Assistant",
        "upload_btn":           "📂 Upload PDF/Word",
        "no_file":              "No file selected",
        "reading":              "⌛ Reading: {file}",
        "processing":           "⏳ Processing...",
        "ai_working":           "🤖 AI is summarizing...",
        "done":                 "✅ Completed: {file}",
        "failed":               "❌ Failed",
        "original":             "Original Content",
        "summary":              "AI Summary",

        # Todo List
        "todo_title":           "Todo List",
        "todo_placeholder":     "✏️ Add new task...",
        "todo_add":             "+ Add",
        "todo_today_list":      "Today's Tasks",
        "todo_clear":           "🗑 Clear Completed",
        "todo_empty":           "No tasks yet.\nAdd your first task! 🎯",
        "todo_total":           "Total",
        "todo_done":            "Completed",
        "todo_remain":          "Remaining",

        # Flashcard
        "flash_title":          "📚 Flashcards AI",
        "flash_subtitle":       "Create flashcards from documents or text",
        "flash_from_file":      "📂 Generate from file",
        "flash_from_text":      "💬 Generate from text",
        "flash_view":           "📖 View flashcards",
        "flash_back":           "← Back",
        "flash_empty":          "No flashcards yet",
        "flash_loading_file":   "📂 Reading file...",
        "flash_ai_generating":  "🤖 AI is generating flashcards...",
        "flash_error_load":     "Load Error",
        "flash_error_ai":       "AI Error",
        "flash_error":          "Error",
        "flash_input_title":    "Enter Content",
        "flash_input_label":    "Enter content to study:",
        "flash_show_answer":    "👁 Show Answer",
        "flash_back_answer":    "↩️ Back",

        # Dashboard
        "greeting_morning":     "Good morning",
        "greeting_afternoon":   "Good afternoon",
        "greeting_evening":     "Good evening",

        "today_schedule":       "Today's Schedule",
        "no_schedule":          "No schedule today.",
        "study_progress":       "Study Progress",
        "courses_studying":     "Current Courses",
        "semester":             "Semester 2",
        "avg_progress":         "Average Progress",

        # Schedule
        "schedule_title":       "📅 Schedule",
        "schedule_subtitle":    "Manage your study schedule",
        "schedule_add":         "+ Add",
        "schedule_delete":      "🗑 Delete",
        "schedule_delete_hint": "Click a schedule to delete",

        "choose_day":           "Choose day",
        "choose_day_label":     "Select day:",

        "input_course":         "Course",
        "input_course_label":   "Enter course name:",
        # Days of week
        "mon":                  "Monday",
        "tue":                  "Tuesday",
        "wed":                  "Wednesday",
        "thu":                  "Thursday",
        "fri":                  "Friday",
        "sat":                  "Saturday",
        "sun":                  "Sunday",

        # COURSE
        # Course UI
        "course_title":         "My Courses",
        "course_subtitle":      "Manage your courses for this semester.",
        "course_add":           "+ Add Course",
        "course_empty":         "No courses yet 😢",
        "course_status_learning": "Learning",
        "progress":             "Progress",

        # Input dialog
        "input_course":         "Course Name",
        "input_course_label":   "Enter course name:",

        "input_code":           "Course Code",
        "input_code_label":     "Enter course code:",

        "input_prof":           "Professor",
        "input_prof_label":     "Enter professor name:",

        "error_add_course":     "Cannot add course!",

        # Course Detail
        "course_detail_back":   "Back to courses",
        "course_detail_content": "Course Content",
        "course_detail_no_data": "Course data not found.",
        "course_detail_no_lessons": "No lessons yet.",
        "course_detail_description": "Course Description",
        "course_detail_resources": "Resources",
        "course_detail_continue": "Continue Learning",
        "course_detail_continue_desc": "You're at the beginning of this course. Start your first lesson now!",
        "course_detail_open_latest": "Open latest lesson",
        "course_detail_flash_created": "Created {count} flashcards!",
        "course_detail_professor":   "Professor:",
        "course_detail_completed":   "✅ Completed",
        "course_detail_no_ai":       "No AI available to generate flashcards.",
        "course_detail_this_course": "this course",
        "badge_title":               "🎉 Course Completed!",
        "badge_congrats":            "Excellent!",
        "badge_msg":                 "You have completed the entire\ncourse <b>{course_name}</b>.\nKeep up the great work!",
        "badge_certificate":         "✅  Completion Certificate Earned",
        "badge_btn":                 "Awesome! 🎊",
        "lesson_open_btn":           "🔗 Open",
        "lesson_flash_btn":          "⚡ Flashcard",
        "error": "Error",
        "stat_lessons":         "LESSONS",
        "stat_exercises":       "EXERCISES",
        "stat_progress":        "PROGRESS",

        # Grades
        "grade_title":         "Grade Management",
        "hs_mode":              "🎒 High School",
        "sv_mode":              "🎓 University",
        "grade_add_subject":    "+ Add Subject",

        "subject":              "Subject",
        "subject_name":         "Subject Name",

        "tx_score":             "Regular Score",
        "gk_score":             "Midterm Score",
        "ck_score":             "Final Score",
        "avg_score":            "Average",
        "rank":                 "Rank",

        "cc":                   "Attendance",
        "bt":                   "Assignments",
        "avg":                  "Average",
        "letter":               "Letter Grade",
        "gpa4":                 "GPA (4.0)",

        "confirm":              "Confirm",
        "confirm_delete_msg":   "Are you sure you want to delete this subject?",

        "edit":                 "Edit",
        "delete":               "Delete",

        "invalid_input":        "Invalid Input",
        "add_subject": "Add Subject",

        "hs_subject_dialog_title": "Add Subject (High School)",
        "sv_subject_dialog_title": "Add Subject (University)",

        "tx_label": "Regular Score (Coefficient 1):",
        "gk_label": "Midterm Score (Coefficient 2):",
        "ck_label": "Final Score (Coefficient 3):",
        "attendance_label": "Attendance (optional):",
        "assignment_label": "Assignments (optional):",
        "midterm_label": "Midterm:",
        "final_label": "Final:",
        "grade_student": "School",
        "grade_university": "University",
        "tx_score_label": "Regular scores (weight 1)",
        "gk_score_label": "Midterm score (weight 2)",
        "ck_score_label": "Final score (weight 3)",

        "cc_optional": "Attendance (optional)",
        "bt_optional": "Assignments (optional)",
        "gk_score": "Midterm",
        "ck_score": "Final",
        "save": "Save",
        "cancel": "Cancel",
        "credits": "Credits",

        # Flashcard extra
        "flash_click_answer":      "👆 Click to see the answer",
        "flash_click_question":    "👆 Click to see the question",
        "flash_ai_error_empty":    "AI could not generate flashcards.\nPlease try again with a more specific prompt.",
        "flash_new_saved":         "✅  Created and saved {saved} new flashcard(s)!",
        "flash_empty_msg":         "No flashcards yet.\nCreate some using the buttons above!",
        "flash_card_file_title":   "Upload Document",
        "flash_card_file_desc":    "Upload a PDF or DOCX file.\nAI will read it and generate flashcards.",
        "flash_card_file_btn":     "📂  Choose file",
        "flash_card_topic_title":  "Enter Prompt",
        "flash_card_topic_desc":   "Type a topic to study.\nExample: \"Create flashcards about basic Python\".",
        "flash_card_topic_btn":    "✍️  Enter prompt",
        "flash_saved_label":       "📚 Saved Flashcards",
        "flash_clear_all":         "🗑  Clear All",
        "flash_confirm_clear":     "Confirm Delete",
        "flash_confirm_clear_msg": "Delete all saved flashcards?\nThis action cannot be undone.",
        "flash_choose_file":       "Choose Study Document",
        "flash_file_error_title":  "File Read Error",
        "flash_file_error_msg":    "Cannot read file.",
        "flash_prompt_title":      "Create Flashcards with AI",
        "flash_prompt_label":      "🤖 Enter prompt for AI",
        "flash_prompt_subtitle":   "Describe the topic you want to study. AI will generate flashcards for you.",
        "flash_prompt_examples":   "💡  \"Basic Python flashcards\"  •  \"Calculus review\"  •  \"Graph theory\"",
        "flash_prompt_placeholder": "Enter your prompt here...",
        "flash_prompt_generate":   "✨  Generate",
    },
    "cn": {
        # Settings page
        "settings_title":       "⚙️ 设置",
        "appearance_title":     "🎨 外观",
        "appearance_desc":      "在浅色和深色主题之间切换。",
        "dark_mode_on":         "🌙 深色模式",
        "dark_mode_off":        "☀️ 浅色模式",
        "ai_title":             "🤖 AI设置",
        "ai_desc":              "每个AI会话生成的闪卡最大数量。",
        "ai_limit_lbl":         "闪卡上限：",
        "ai_limit_placeholder": "输入数字（例如：10）",
        "data_title":           "🗂 数据",
        "data_desc":            "以 SON格式导出/导入闪卡数据。",
        "export_btn":           "⬆ 导出",
        "import_btn":           "⬇ 导入",
        "save_btn":             "💾 保存设置",
        "language_title":       "🌐 语言",
        "language_desc":        "选择应用程序的显示语言。",
        
        # Dialogs
        "invalid_input":        "无效输入",
        "invalid_input_msg":    "闪卡上限必须是正整数。",
        "saved_title":          "保存成功",
        "saved_msg":            "设置已保存！\n\n• AI上限: {limit}\n• 深色模式: {dark}",
        "dark_on":              "开启",
        "dark_off":             "关闭",
        "export_ok":            "导出成功",
        "export_ok_msg":        "导出位置：\n{path}",
        "export_fail":          "导出失败",
        "import_ok":            "导入成功",
        "import_ok_msg":        "已加载 {count} 张闪卡：\n{path}",
        "import_fail":          "导入失败",
        
        # Sidebar
        "menu_overview":        "概览",
        "menu_schedule":        "课程表",
        "menu_courses":         "课程",
        "menu_flash":           "闪卡",
        "menu_summary":         "AI总结",
        "menu_todo":            "待办事项",
        "menu_settings":        "设置",
        "menu_grades":           "成绩单",
        "logout":               "↪ 退出登录",

        # Summary 
        "summary_title":        "🤖 文档摘要助手",
        "upload_btn":           "📂 选择PDF/Word文件",
        "no_file":              "尚未选择文件",
        "reading":              "⌛ 正在读取：{file}",
        "processing":           "⏳ 处理中...",
        "ai_working":           "🤖 AI正在总结...",
        "done":                 "✅ 完成：{file}",
        "failed":               "❌ 失败",
        "original":             "原始内容",
        "summary":              "AI摘要",

        # Todo List
        "todo_title":           "待办事项",
        "todo_placeholder":     "✏️ 添加新任务...",
        "todo_add":             "+ 添加",
        "todo_today_list":      "今日任务",
        "todo_clear":           "🗑 清除已完成",
        "todo_empty":           "还没有任务。\n添加你的第一个任务吧！🎯",
        "todo_total":           "总任务",
        "todo_done":            "已完成",
        "todo_remain":          "剩余",

        # Flashcard
        "flash_title":          "📚 AI 闪卡",
        "flash_subtitle":       "从文档或文本创建闪卡",
        "flash_from_file":      "📂 从文件生成",
        "flash_from_text":      "💬 从文本生成",
        "flash_view":           "📖 查看闪卡",
        "flash_back":           "← 返回",
        "flash_empty":          "还没有闪卡",
        "flash_loading_file":   "📂 正在读取文件...",
        "flash_ai_generating":  "🤖 AI 正在生成闪卡...",
        "flash_error_load":     "加载错误",
        "flash_error_ai":       "AI错误",
        "flash_error":          "错误",
        "flash_input_title":    "输入内容",
        "flash_input_label":    "输入学习内容：",
        "flash_show_answer":    "👁 查看答案",
        "flash_back_answer":    "↩️ 返回",

        # DashBoard
        "greeting_morning":     "早上好",
        "greeting_afternoon":   "下午好",
        "greeting_evening":     "晚上好",

        "today_schedule":       "今日课程",
        "no_schedule":          "今天没有课程",
        "study_progress":       "学习进度",
        "courses_studying":     "正在学习的课程",
        "semester":             "第二学期",
        "avg_progress":         "平均进度",

        # Schedule
        "schedule_title":       "📅 课程表",
        "schedule_subtitle":    "管理你的课程安排",
        "schedule_add":         "+ 添加",
        "schedule_delete":      "🗑 删除",
        "schedule_delete_hint": "点击课程以删除",

        "choose_day":           "选择日期",
        "choose_day_label":     "选择一天:",

        "input_course":         "课程",
        "input_course_label":   "输入课程名称:",

        # Days of week
        "mon":                  "周一",
        "tue":                  "周二",
        "wed":                  "周三",
        "thu":                  "周四",
        "fri":                  "周五",
        "sat":                  "周六",
        "sun":                  "周日",

        # COURSE
        # Course UI
        "course_title":         "我的课程",
        "course_subtitle":      "管理本学期的课程列表。",
        "course_add":           "+ 添加课程",
        "course_empty":         "还没有课程 😢",
        "course_status_learning": "学习中",
        "progress":             "进度",

        # Input dialog
        "input_course":         "课程名称",
        "input_course_label":   "输入课程名称:",

        "input_code":           "课程代码",
        "input_code_label":     "输入课程代码:",

        "input_prof":           "教师",
        "input_prof_label":     "输入教师姓名:",

        "error_add_course":     "无法添加课程！",

        # Course Detail
        "course_detail_back": "返回课程列表",
        "course_detail_content": "学习内容",
        "course_detail_no_data": "未找到课程数据。",
        "course_detail_no_lessons": "暂无课程内容。",
        "course_detail_description": "课程描述",
        "course_detail_resources": "学习资源",
        "course_detail_continue": "继续学习",
        "course_detail_continue_desc": "你刚开始学习这门课程，现在就开始第一课吧！",
        "course_detail_open_latest": "打开最新课程",
        "course_detail_flash_created": "已创建 {count} 张闪卡！",
        "course_detail_professor":   "教师：",
        "course_detail_completed":   "✅ 已完成",
        "course_detail_no_ai":       "没有 AI 可以生成闪卡。",
        "course_detail_this_course": "这门课程",
        "badge_title":               "🎉 课程完成！",
        "badge_congrats":            "出色！",
        "badge_msg":                 "你已完成整个\n课程 <b>{course_name}</b>。\n请继续保持！",
        "badge_certificate":         "✅  已获得完成证书",
        "badge_btn":                 "太棒了！🎊",
        "lesson_open_btn":           "🔗 打开",
        "lesson_flash_btn":          "⚡ 闪卡",
        "error": "错误",
        "stat_lessons":         "课程",
        "stat_exercises":       "练习",
        "stat_progress":        "进度",

        # Grades
        "grade_title":          "成绩管理",
        "hs_mode":              "🎒 高中",
        "sv_mode":              "🎓 大学",
        "grade_add_subject":    "+ 添加课程",

        "subject":              "科目",
        "subject_name":         "科目名称",

        "tx_score":             "平时成绩",
        "gk_score":             "期中成绩",
        "ck_score":             "期末成绩",
        "avg_score":            "平均分",
        "rank":                 "等级",

        "cc":                   "考勤",
        "bt":                   "作业",
        "avg":                  "平均分",
        "letter":               "等级",
        "gpa4":                 "绩点 (4.0)",

        "confirm":              "确认",
        "confirm_delete_msg": "确定要删除该课程吗？",

        "edit":                 "编辑",
        "delete":               "删除",

        "invalid_input":        "输入无效",
        "add_subject": "添加课程",

        "hs_subject_dialog_title": "添加课程（高中）",
        "sv_subject_dialog_title": "添加课程（大学）",

        "tx_label": "平时成绩（系数1）：",
        "gk_label": "期中成绩（系数2）：",
        "ck_label": "期末成绩（系数3）：",
        "attendance_label": "考勤（可选）：",
        "assignment_label": "作业（可选）：",
        "midterm_label": "期中：",
        "final_label": "期末：",

        "invalid_input_msg": "输入无效，请输入有效数字",
        "grade_student": "学生",
        "grade_university": "大学生",
        "tx_score_label": "平时成绩（权重1）",
        "gk_score_label": "期中成绩（权重2）",
        "ck_score_label": "期末成绩（权重3）",

        "cc_optional": "考勤（可选）",
        "bt_optional": "作业（可选）",
        "gk_score": "期中",
        "ck_score": "期末",
        "save": "保存",
        "cancel": "取消",
        "credits": "学分",

        # Flashcard extra
        "flash_click_answer":      "👆 点击查看答案",
        "flash_click_question":    "👆 点击查看问题",
        "flash_ai_error_empty":    "AI 无法生成闪卡。\n请重试或输入更具体的要求。",
        "flash_new_saved":         "✅  已创建并保存 {saved} 张新闪卡！",
        "flash_empty_msg":         "还没有闪卡。\n请使用上方按钮创建！",
        "flash_card_file_title":   "上传文档",
        "flash_card_file_desc":    "上传 PDF 或 DOCX 文件。\nAI 将读取内容并生成闪卡。",
        "flash_card_file_btn":     "📂  选择文件",
        "flash_card_topic_title":  "输入提示词",
        "flash_card_topic_desc":   "输入你想复习的主题。\n例如：\"生成关于 Python 基础的闪卡\"。",
        "flash_card_topic_btn":    "✍️  输入提示词",
        "flash_saved_label":       "📚 已保存的闪卡",
        "flash_clear_all":         "🗑  清除全部",
        "flash_confirm_clear":     "确认删除",
        "flash_confirm_clear_msg": "删除所有已保存的闪卡？\n此操作无法撤销。",
        "flash_choose_file":       "选择学习文档",
        "flash_file_error_title":  "文件读取错误",
        "flash_file_error_msg":    "无法读取文件。",
        "flash_prompt_title":      "用 AI 创建闪卡",
        "flash_prompt_label":      "🤖 为 AI 输入提示词",
        "flash_prompt_subtitle":   "描述你想复习的主题，AI 将自动生成适合的闪卡。",
        "flash_prompt_examples":   "💡  \"Python 基础闪卡\"  •  \"微积分复习\"  •  \"图论\"",
        "flash_prompt_placeholder": "在此输入您的提示词...",
        "flash_prompt_generate":   "✨  立即生成",
    },
}

# ─────────────────────────────────────────────
#  LANGUAGE MANAGER  (singleton-style QObject)
# ─────────────────────────────────────────────
class LanguageManager(QObject):
    """Emits language_changed whenever the active locale is swapped."""
    language_changed = Signal(str)          # emits new lang code, e.g. "en"

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._lang = "vi"                   # default

    # ── public API ──────────────────────────
    @property
    def lang(self) -> str:
        return self._lang

    def set_lang(self, code: str):
        if code != self._lang and code in TRANSLATIONS:
            self._lang = code
            self.language_changed.emit(code)

    def tr(self, key: str, **fmt) -> str:
        """Return translated string, falling back to key if missing."""
        text = TRANSLATIONS.get(self._lang, {}).get(key, key)
        return text.format(**fmt) if fmt else text


# Convenience shortcut used throughout the app:
#   from src.ui.settings_widget import tr
def tr(key: str, **fmt) -> str:
    return LanguageManager.instance().tr(key, **fmt)


# ─────────────────────────────────────────────
#  DARK / LIGHT STYLESHEETS  (unchanged)
# ─────────────────────────────────────────────
DARK_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #1E1E2E;
        color: #CDD6F4;
    }
    QFrame#Sidebar {
        background-color: #181825;
        border-right: 1px solid #313244;
    }
    QPushButton#MenuBtn {
        background: transparent;
        color: #CDD6F4;
        border: none;
        text-align: left;
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 14px;
    }
    QPushButton#MenuBtn:checked {
        background: #313244;
        color: #89B4FA;
        font-weight: bold;
    }
    QPushButton#MenuBtn:hover { background: #2A2A3D; }
    QPushButton#LogoutBtn {
        background: transparent;
        color: #F38BA8;
        border: none;
        text-align: left;
        padding: 8px;
        font-size: 13px;
    }
    QFrame#CardBlue {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #2D60FF,stop:1 #539BFF);
        border-radius: 16px;
        padding: 20px;
        color: white;
    }
    QFrame#CardWhite {
        background: #313244;
        border-radius: 16px;
        padding: 20px;
        color: #CDD6F4;
    }
    QFrame#SettingsSection {
        background: #313244;
        border-radius: 12px;
        padding: 16px;
    }
    QLineEdit {
        background: #45475A;
        border: 1px solid #585B70;
        border-radius: 8px;
        padding: 8px 12px;
        color: #CDD6F4;
        font-size: 13px;
    }
    QProgressBar { background: #45475A; border-radius: 3px; }
    QProgressBar::chunk { background: #89B4FA; border-radius: 3px; }
"""

LIGHT_STYLESHEET = ""


# ─────────────────────────────────────────────
#  LANGUAGE BUTTON  (one flag-pill per locale)
# ─────────────────────────────────────────────
class LangButton(QPushButton):
    """A toggleable pill button for one language option."""

    # Map locale code → display label
    _LABELS = {"vi": "🇻🇳  Tiếng Việt", "en": "🇬🇧  English", "cn": "cn  中國人"}

    def __init__(self, code: str, parent=None):
        super().__init__(self._LABELS.get(code, code), parent)
        self.code = code
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(38)
        self._refresh_style(False)

    def _refresh_style(self, active: bool):
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background: #2D60FF;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 20px;
                    font-size: 13px;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    border: 1.5px solid #2D60FF;
                    color: #2D60FF;
                    background: transparent;
                    border-radius: 8px;
                    padding: 0 20px;
                    font-size: 13px;
                }
                QPushButton:hover { background: #EEF2FF; }
                QPushButton:pressed { background: #DDE4FF; }
            """)

    def set_active(self, active: bool):
        self.setChecked(active)
        self._refresh_style(active)


# ─────────────────────────────────────────────
#  SETTINGS WIDGET
# ─────────────────────────────────────────────
class SettingsWidget(QWidget):
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        self.settings = {"ai_limit": 10, "dark_mode": False}

        app = QApplication.instance()
        self.light_stylesheet = app.styleSheet()

        self._lm = LanguageManager.instance()
        self._lang_buttons: dict[str, LangButton] = {}

        self.setup_ui()
        self.connect_signals()

        # Re-render text whenever language changes
        self._lm.language_changed.connect(self._retranslate)

    # ══════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════
    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # Title
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size:22px; font-weight:bold;")
        root.addWidget(self.lbl_title)

        # ── (1) Language ─────────────────────────────────────────
        lang_content, self._lang_buttons = self._language_content()
        self._section_language = self._section("", lang_content)
        root.addWidget(self._section_language)

        # ── (2) Appearance ───────────────────────────────────────
        self._section_appear = self._section("", self._appearance_content())
        root.addWidget(self._section_appear)

        # ── (3) AI Settings ──────────────────────────────────────
        ai_content, self.ai_limit_input = self._ai_content()
        self._section_ai = self._section("", ai_content)
        root.addWidget(self._section_ai)

        # ── (4) Data ─────────────────────────────────────────────
        self._section_data = self._section("", self._data_content())
        root.addWidget(self._section_data)

        root.addStretch()

        # Save button
        self.save_btn = QPushButton()
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setFixedHeight(44)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #2D60FF;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover   { background: #1A4FE0; }
            QPushButton:pressed { background: #1440C0; }
        """)
        root.addWidget(self.save_btn)

        # Translate everything on first render
        self._retranslate()

    # ──────────────────────────────────────────
    #  Section wrapper
    # ──────────────────────────────────────────
    def _section(self, heading: str, content_widget: QWidget) -> QFrame:
        frame = QFrame()
        frame.setObjectName("SettingsSection")

        layout = QVBoxLayout(frame)
        layout.setSpacing(12)

        lbl = QLabel(heading)
        lbl.setObjectName("SectionHeading")
        lbl.setStyleSheet("font-size:15px; font-weight:bold; color:#2D60FF;")
        layout.addWidget(lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#E8ECF0;")
        layout.addWidget(sep)

        layout.addWidget(content_widget)
        return frame

    def _get_section_heading(self, frame: QFrame) -> QLabel:
        return frame.findChild(QLabel, "SectionHeading")

    # ──────────────────────────────────────────
    #  Language section
    # ──────────────────────────────────────────
    def _language_content(self):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self._lang_desc = QLabel()
        self._lang_desc.setStyleSheet("color:#6F767E; font-size:13px;")

        layout.addWidget(self._lang_desc)
        layout.addStretch()

        buttons: dict[str, LangButton] = {}
        current = self._lm.lang

        for code in ("vi", "en", "cn"):
            btn = LangButton(code)
            btn.set_active(code == current)
            btn.clicked.connect(lambda _, c=code: self._select_language(c))
            layout.addWidget(btn)
            buttons[code] = btn

        return w, buttons

    # ──────────────────────────────────────────
    #  Appearance section
    # ──────────────────────────────────────────
    def _appearance_content(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)

        self._appear_desc = QLabel()
        self._appear_desc.setStyleSheet("color:#6F767E; font-size:13px;")

        self.dark_mode_btn = QPushButton()
        self.dark_mode_btn.setCursor(Qt.PointingHandCursor)
        self.dark_mode_btn.setFixedHeight(38)
        self.dark_mode_btn.setStyleSheet(self._ghost_btn_style())

        layout.addWidget(self._appear_desc)
        layout.addStretch()
        layout.addWidget(self.dark_mode_btn)
        return w

    # ──────────────────────────────────────────
    #  AI section
    # ──────────────────────────────────────────
    def _ai_content(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._ai_desc = QLabel()
        self._ai_desc.setStyleSheet("color:#6F767E; font-size:13px;")
        layout.addWidget(self._ai_desc)

        row = QHBoxLayout()
        self._ai_limit_lbl = QLabel()
        self._ai_limit_lbl.setFixedWidth(140)

        inp = QLineEdit()
        inp.setFixedWidth(200)
        inp.setFixedHeight(36)

        row.addWidget(self._ai_limit_lbl)
        row.addWidget(inp)
        row.addStretch()
        layout.addLayout(row)

        return w, inp

    # ──────────────────────────────────────────
    #  Data section
    # ──────────────────────────────────────────
    def _data_content(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._data_desc = QLabel()
        self._data_desc.setStyleSheet("color:#6F767E; font-size:13px;")

        self.export_btn = QPushButton()
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setFixedHeight(38)
        self.export_btn.setStyleSheet(self._ghost_btn_style())

        self.import_btn = QPushButton()
        self.import_btn.setCursor(Qt.PointingHandCursor)
        self.import_btn.setFixedHeight(38)
        self.import_btn.setStyleSheet(self._ghost_btn_style())

        layout.addWidget(self._data_desc)
        layout.addStretch()
        layout.addWidget(self.export_btn)
        layout.addWidget(self.import_btn)
        return w

    @staticmethod
    def _ghost_btn_style() -> str:
        return """
            QPushButton {
                border: 1.5px solid #2D60FF;
                color: #2D60FF;
                background: transparent;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 13px;
            }
            QPushButton:hover   { background: #EEF2FF; }
            QPushButton:pressed { background: #DDE4FF; }
        """

    # ══════════════════════════════════════════
    #  SIGNALS
    # ══════════════════════════════════════════
    def connect_signals(self):
        self.dark_mode_btn.clicked.connect(self.toggle_dark_mode)
        self.export_btn.clicked.connect(self.export_flashcards)
        self.import_btn.clicked.connect(self.import_flashcards)
        self.save_btn.clicked.connect(self.save_settings)

    # ══════════════════════════════════════════
    #  RETRANSLATE  — called on every lang change
    # ══════════════════════════════════════════
    def _retranslate(self, _lang: str = ""):
        t = self._lm.tr          # shortcut

        # Page title
        self.lbl_title.setText(t("settings_title"))

        # Section headings
        self._get_section_heading(self._section_language).setText(t("language_title"))
        self._get_section_heading(self._section_appear).setText(t("appearance_title"))
        self._get_section_heading(self._section_ai).setText(t("ai_title"))
        self._get_section_heading(self._section_data).setText(t("data_title"))

        # Descriptions
        self._lang_desc.setText(t("language_desc"))
        self._appear_desc.setText(t("appearance_desc"))
        self._ai_desc.setText(t("ai_desc"))
        self._data_desc.setText(t("data_desc"))

        # Buttons & inputs
        dark_key = "dark_mode_off" if self.settings["dark_mode"] else "dark_mode_on"
        self.dark_mode_btn.setText(t(dark_key))
        self._ai_limit_lbl.setText(t("ai_limit_lbl"))
        self.ai_limit_input.setPlaceholderText(t("ai_limit_placeholder"))
        self.export_btn.setText(t("export_btn"))
        self.import_btn.setText(t("import_btn"))
        self.save_btn.setText(t("save_btn"))

        # Mark active language button
        for code, btn in self._lang_buttons.items():
            btn.set_active(code == self._lm.lang)

        # Propagate to dashboard sidebar (optional hook)
        if hasattr(self.dashboard, "retranslate_ui"):
            self.dashboard.retranslate_ui()

    # ══════════════════════════════════════════
    #  HANDLERS
    # ══════════════════════════════════════════
    def _select_language(self, code: str):
        """Switch active language and update button states immediately."""
        self._lm.set_lang(code)          # triggers language_changed → _retranslate

    def toggle_dark_mode(self):
        self.settings["dark_mode"] = not self.settings["dark_mode"]
        self.dashboard.apply_theme("dark" if self.settings["dark_mode"] else "light")
        self._retranslate()              # update button text after toggle

    def save_settings(self):
        raw = self.ai_limit_input.text().strip()
        if raw:
            if not raw.isdigit() or int(raw) <= 0:
                QMessageBox.warning(self, tr("invalid_input"), tr("invalid_input_msg"))
                return
            self.settings["ai_limit"] = int(raw)

        dark_str = tr("dark_on") if self.settings["dark_mode"] else tr("dark_off")
        QMessageBox.information(
            self,
            tr("saved_title"),
            tr("saved_msg", limit=self.settings["ai_limit"], dark=dark_str),
        )

    def export_flashcards(self):
        path, _ = QFileDialog.getSaveFileName(
            self, tr("export_btn"), "flashcards_export.json", "JSON Files (*.json)"
        )
        if not path:
            return

        dummy_data = {
            "exported_at": "2025-01-01T00:00:00",
            "flashcards": [
                {"id": 1, "front": "What is Python?", "back": "A programming language."},
                {"id": 2, "front": "What is PySide6?", "back": "Qt bindings for Python."},
            ],
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dummy_data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, tr("export_ok"), tr("export_ok_msg", path=path))
        except Exception as e:
            QMessageBox.critical(self, tr("export_fail"), str(e))

    def import_flashcards(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("import_btn"), "", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data.get("flashcards", []))
            QMessageBox.information(
                self, tr("import_ok"), tr("import_ok_msg", count=count, path=path)
            )
        except Exception as e:
            QMessageBox.critical(self, tr("import_fail"), str(e))