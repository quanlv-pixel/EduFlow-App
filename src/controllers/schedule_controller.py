class ScheduleController:
    def __init__(self, db):
        self.db = db

    def get_schedule(self, user_id):
        return self.db.get_schedule(user_id)

    def add_schedule(self, user_id, course, room, day, start, end):
        """
        start / end: phút tính từ 0:00
        Trả về: (bool, str) -> (Thành công/Thất bại, Lời nhắn)
        """
        if end <= start:
            return False, "Giờ kết thúc phải sau giờ bắt đầu!"

        # Tối thiểu 15 phút
        if (end - start) < 15:
            return False, "Lịch học phải kéo dài tối thiểu 15 phút!"

        # 1. KIỂM TRA TRÙNG LỊCH
        overlaps = self.db.check_schedule_overlap(user_id, day, start, end)
        if overlaps:
            overlap = overlaps[0] # Lấy môn học đầu tiên bị trùng
            c_name = overlap["course"]
            s_h, s_m = overlap["start_time"] // 60, overlap["start_time"] % 60
            e_h, e_m = overlap["end_time"] // 60, overlap["end_time"] % 60
            
            msg = (f"Khung giờ này bị trùng với môn {c_name} "
                   f"({s_h:02d}:{s_m:02d} - {e_h:02d}:{e_m:02d}).\n\n"
                   f"Vui lòng chọn khung giờ khác!")
            return False, msg

        # 2. NẾU KHÔNG TRÙNG, TIẾN HÀNH THÊM LỊCH
        success = self.db.add_schedule(user_id, course, room, day, start, end)
        if success:
            return True, "Thêm lịch thành công!"
        else:
            return False, "Lỗi hệ thống: Không thể ghi vào cơ sở dữ liệu!"

    def delete_schedule(self, schedule_id):
        return self.db.delete_schedule(schedule_id)
    
    def delete_all_schedules(self, user_id):
        """Gọi hàm xóa toàn bộ lịch từ Database."""
        return self.db.delete_all_schedules(user_id)