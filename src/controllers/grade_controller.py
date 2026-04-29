import json


class GradeController:
    def __init__(self, db):
        self.db = db

    # ================= CRUD =================
    def get_subjects(self, user_id, mode):
        return self.db.execute(
            "SELECT * FROM grade_subjects WHERE user_id=? AND mode=?",
            (user_id, mode), True
        ) or []

    def add_subject(self, user_id, mode, subject_name, credits, scores_data):
        return self.db.execute(
            """INSERT INTO grade_subjects
               (user_id, mode, subject_name, credits, scores_data)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, mode, subject_name, credits, json.dumps(scores_data))
        )

    def update_subject(self, subject_id, subject_name, credits, scores_data):
        return self.db.execute(
            """UPDATE grade_subjects
               SET subject_name=?, credits=?, scores_data=?
               WHERE id=?""",
            (subject_name, credits, json.dumps(scores_data), subject_id)
        )

    def delete_subject(self, subject_id):
        return self.db.execute(
            "DELETE FROM grade_subjects WHERE id=?",
            (subject_id,)
        )

    # ================= HỌC SINH =================
    @staticmethod
    def calc_hs_average(scores: dict) -> float:
        """
        tx: list[float]  – hệ số 1 mỗi điểm
        gk: float        – hệ số 2
        ck: float        – hệ số 3
        """
        tx = scores.get("tx") or []
        gk = scores.get("gk")
        ck = scores.get("ck")

        total = sum(float(x) for x in tx)
        weight = len(tx)

        if gk is not None:
            total += float(gk) * 2
            weight += 2
        if ck is not None:
            total += float(ck) * 3
            weight += 3

        return round(total / weight, 2) if weight else 0.0

    @staticmethod
    def hs_rank(avg: float) -> tuple[str, str]:
        """Trả về (xếp loại, màu hex)"""
        if avg >= 9.0:
            return "Xuất sắc", "#10B981"
        elif avg >= 8.0:
            return "Giỏi", "#2D60FF"
        elif avg >= 6.5:
            return "Khá", "#F59E0B"
        elif avg >= 5.0:
            return "Trung bình", "#F97316"
        else:
            return "Yếu", "#EF4444"

    @staticmethod
    def hs_overall(subjects_avg: list[float]) -> float:
        if not subjects_avg:
            return 0.0
        return round(sum(subjects_avg) / len(subjects_avg), 2)

    # ================= SINH VIÊN =================
    @staticmethod
    def calc_sv_average(scores: dict) -> float:
        """
        Tính điểm trung bình theo hệ số cộng dồn:
            CC  : hệ số 3  (bắt buộc nếu có)
            BT  : hệ số 2  (tuỳ chọn — môn không có BT thì bỏ qua)
            GK  : hệ số 3  (bắt buộc)
            CK  : hệ số 9  (bắt buộc)

        Ví dụ kiểm chứng:
          CC=10, GK=6, CK=8.5, không có BT:
              (10×3 + 6×3 + 8.5×9) / (3+3+9) = 124.5 / 15 = 8.30 ✓
          CC=10, BT=10, GK=6, CK=8.5:
              (10×3 + 10×2 + 6×3 + 8.5×9) / (3+2+3+9) = 144.5 / 17 = 8.50 ✓

        → Khi thiếu thành phần nào, mẫu số tự giảm theo hệ số tương ứng,
          không cần viết lại công thức cho từng trường hợp.
        """
        cc = scores.get("cc")
        bt = scores.get("bt")
        gk = scores.get("gk")
        ck = scores.get("ck")

        # GK và CK là bắt buộc; thiếu một trong hai thì chưa tính được
        if gk is None or ck is None:
            return 0.0

        total  = float(gk) * 3 + float(ck) * 9
        weight = 3 + 9                           # = 12 (GK + CK)

        if cc is not None:
            total  += float(cc) * 3
            weight += 3

        if bt is not None:
            total  += float(bt) * 2
            weight += 2

        return round(total / weight, 2)

    @staticmethod
    def score_to_letter(score: float) -> str:
        if score >= 8.5:  return "A"
        elif score >= 8.0: return "B+"
        elif score >= 7.0: return "B"
        elif score >= 6.5: return "C+"
        elif score >= 5.5: return "C"
        elif score >= 5.0: return "D+"
        elif score >= 4.0: return "D"
        else:              return "F"

    @staticmethod
    def letter_to_gpa4(letter: str) -> float:
        return {"A": 4.0, "B+": 3.5, "B": 3.0,
                "C+": 2.5, "C": 2.0, "D+": 1.5,
                "D": 1.0, "F": 0.0}.get(letter, 0.0)

    @staticmethod
    def calc_gpa4(subjects: list[dict]) -> float:
        """subjects: list of {avg10, credits}"""
        total_pts = 0.0
        total_credits = 0
        for s in subjects:
            letter = GradeController.score_to_letter(s["avg10"])
            gpa4   = GradeController.letter_to_gpa4(letter)
            c      = int(s.get("credits", 3))
            total_pts    += gpa4 * c
            total_credits += c
        return round(total_pts / total_credits, 2) if total_credits else 0.0

    @staticmethod
    def calc_gpa10(subjects: list[dict]) -> float:
        total = sum(s["avg10"] * int(s.get("credits", 3)) for s in subjects)
        credits = sum(int(s.get("credits", 3)) for s in subjects)
        return round(total / credits, 2) if credits else 0.0

    @staticmethod
    def gpa4_rank(gpa: float) -> tuple[str, str]:
        if gpa >= 3.6:  return "Xuất sắc", "#10B981"
        elif gpa >= 3.2: return "Giỏi",    "#2D60FF"
        elif gpa >= 2.5: return "Khá",     "#F59E0B"
        elif gpa >= 2.0: return "Trung bình","#F97316"
        elif gpa >= 1.0: return "Yếu",     "#EF4444"
        else:            return "Kém",     "#DC2626"

    @staticmethod
    def letter_color(letter: str) -> str:
        return {
            "A":  "#10B981",
            "B+": "#2D60FF",
            "B":  "#3B82F6",
            "C+": "#F59E0B",
            "C":  "#F97316",
            "D+": "#EF4444",
            "D":  "#DC2626",
            "F":  "#991B1B",
        }.get(letter, "#6F767E")