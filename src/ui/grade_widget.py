"""
grade_widget.py  –  Màn hình Quản lý Điểm
Refactored: mỗi học kỳ là một SemesterBlock độc lập bên trong QScrollArea.
"""

import json

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QDoubleSpinBox, QSpinBox, QAbstractItemView,
    QSizePolicy, QInputDialog, QMenu, QSpacerItem,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont, QCursor

from src.ui.settings_widget import LanguageManager, tr
from src.controllers.grade_controller import GradeController


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def _parse_scores(raw) -> dict:
    if isinstance(raw, str):
        return json.loads(raw)
    return raw or {}


# ─────────────────────────────────────────────────────────────
#  DIALOG – THÊM / SỬA MÔN (HỌC SINH)
# ─────────────────────────────────────────────────────────────
class HSSubjectDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.setWindowTitle(tr("add_subject"))
        self.setMinimumWidth(400)
        self.setObjectName("LoginWindow")

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        self.title = QLabel()
        self.title.setObjectName("GradeDialogTitle")
        layout.addWidget(self.title)

        form = QFormLayout()
        form.setSpacing(10)

        self.inp_name = QLineEdit()
        self.inp_name.setObjectName("LoginInput")
        form.addRow(tr("subject_name"), self.inp_name)

        tx_frame = QFrame()
        tx_lay   = QHBoxLayout(tx_frame)
        tx_lay.setContentsMargins(0, 0, 0, 0)
        tx_lay.setSpacing(6)
        self.tx_spins = []
        for _ in range(4):
            sp = QDoubleSpinBox()
            sp.setRange(-1, 10); sp.setValue(-1)
            sp.setSpecialValueText("–"); sp.setSingleStep(0.1)
            sp.setDecimals(1); sp.setFixedWidth(70)
            sp.setObjectName("GradeSpinBox")
            tx_lay.addWidget(sp)
            self.tx_spins.append(sp)
        form.addRow(tr("tx_score_label"), tx_frame)

        self.sp_gk = self._make_spin()
        self.sp_ck = self._make_spin()
        form.addRow(tr("gk_score_label"), self.sp_gk)
        form.addRow(tr("ck_score_label"), self.sp_ck)

        layout.addLayout(form)

        self.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btns.accepted.connect(self._validate)
        self.btns.rejected.connect(self.reject)
        self.btns.button(QDialogButtonBox.Ok).setText(tr("save"))
        self.btns.button(QDialogButtonBox.Cancel).setText(tr("cancel"))
        self.btns.button(QDialogButtonBox.Ok).setStyleSheet(
            "background:#2D60FF;color:white;border-radius:8px;padding:8px 20px;font-weight:bold;border:none;"
        )
        layout.addWidget(self.btns)

        if data:
            self._fill(data)
        self._retranslate()

    @staticmethod
    def _make_spin():
        sp = QDoubleSpinBox()
        sp.setRange(-1, 10); sp.setValue(-1)
        sp.setSpecialValueText("–"); sp.setSingleStep(0.1)
        sp.setDecimals(1); sp.setObjectName("GradeSpinBox")
        return sp

    def _fill(self, data):
        self.inp_name.setText(data.get("subject_name", ""))
        scores = data.get("scores", {})
        tx = scores.get("tx", [])
        for i, sp in enumerate(self.tx_spins):
            sp.setValue(tx[i] if i < len(tx) else -1)
        self.sp_gk.setValue(scores.get("gk", -1) if scores.get("gk") is not None else -1)
        self.sp_ck.setValue(scores.get("ck", -1) if scores.get("ck") is not None else -1)

    def _validate(self):
        if not self.inp_name.text().strip():
            QMessageBox.warning(self, tr("invalid_input"), tr("invalid_input_msg"))
            return
        self.accept()

    def get_data(self) -> dict:
        tx = [sp.value() for sp in self.tx_spins if sp.value() >= 0]
        gk = self.sp_gk.value() if self.sp_gk.value() >= 0 else None
        ck = self.sp_ck.value() if self.sp_ck.value() >= 0 else None
        return {
            "subject_name": self.inp_name.text().strip(),
            "credits": 1,
            "scores": {"tx": tx, "gk": gk, "ck": ck},
        }

    def _retranslate(self):
        self.setWindowTitle(tr("add_subject"))
        self.title.setText(tr("add_subject"))
        self.btns.button(QDialogButtonBox.Ok).setText(tr("save"))
        self.btns.button(QDialogButtonBox.Cancel).setText(tr("cancel"))


# ─────────────────────────────────────────────────────────────
#  DIALOG – THÊM / SỬA MÔN (SINH VIÊN)
# ─────────────────────────────────────────────────────────────
class SVSubjectDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm môn học")
        self.setMinimumWidth(400)
        self.setObjectName("LoginWindow")

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("🎓  Thêm môn học (Sinh viên)")
        title.setObjectName("GradeDialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.inp_name = QLineEdit()
        self.inp_name.setObjectName("LoginInput")
        form.addRow(tr("subject_name"), self.inp_name)

        self.sp_credits = QSpinBox()
        self.sp_credits.setRange(1, 10); self.sp_credits.setValue(3)
        self.sp_credits.setObjectName("GradeSpinBox")
        form.addRow(tr("credits"), self.sp_credits)

        def score_spin(optional=True):
            sp = QDoubleSpinBox()
            sp.setRange(-1 if optional else 0, 10)
            sp.setValue(-1 if optional else 0)
            if optional:
                sp.setSpecialValueText("Không có")
            sp.setSingleStep(0.1); sp.setDecimals(1)
            sp.setObjectName("GradeSpinBox")
            return sp

        self.sp_cc = score_spin(); self.sp_bt = score_spin()
        self.sp_gk = score_spin(); self.sp_ck = score_spin()

        form.addRow(tr("cc_optional"), self.sp_cc)
        form.addRow(tr("bt_optional"), self.sp_bt)
        form.addRow(tr("gk_score"),    self.sp_gk)
        form.addRow(tr("ck_score"),    self.sp_ck)

        layout.addLayout(form)

        note = QLabel("💡 Nếu không có CC/BT, trọng số tự động điều chỉnh.")
        note.setObjectName("GradeNote")
        layout.addWidget(note)

        self.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btns.accepted.connect(self._validate)
        self.btns.rejected.connect(self.reject)
        self.btns.button(QDialogButtonBox.Ok).setText("Lưu")
        self.btns.button(QDialogButtonBox.Cancel).setText("Hủy")
        self.btns.button(QDialogButtonBox.Ok).setStyleSheet(
            "background:#2D60FF;color:white;border-radius:8px;padding:8px 20px;font-weight:bold;border:none;"
        )
        layout.addWidget(self.btns)

        if data:
            self._fill(data)

    def _fill(self, data):
        self.inp_name.setText(data.get("subject_name", ""))
        self.sp_credits.setValue(data.get("credits", 3))
        s = data.get("scores", {})
        self.sp_cc.setValue(s["cc"] if s.get("cc") is not None else -1)
        self.sp_bt.setValue(s["bt"] if s.get("bt") is not None else -1)
        self.sp_gk.setValue(s["gk"] if s.get("gk") is not None else -1)
        self.sp_ck.setValue(s["ck"] if s.get("ck") is not None else -1)

    def _validate(self):
        if not self.inp_name.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên môn học.")
            return
        self.accept()

    def get_data(self) -> dict:
        def val(sp): return sp.value() if sp.value() >= 0 else None
        return {
            "subject_name": self.inp_name.text().strip(),
            "credits": self.sp_credits.value(),
            "scores": {
                "cc": val(self.sp_cc), "bt": val(self.sp_bt),
                "gk": val(self.sp_gk), "ck": val(self.sp_ck),
            },
        }


# ─────────────────────────────────────────────────────────────
#  SUMMARY BANNER  (tích lũy toàn bộ học kỳ)
# ─────────────────────────────────────────────────────────────
class SummaryBanner(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("CardBlue")
        self.setFixedHeight(140)
        lay = QHBoxLayout(self)
        lay.setSpacing(40)

        self.lbl_main = QLabel("–")
        self.lbl_main.setStyleSheet("font-size:38px;font-weight:bold;color:white;")

        self.lbl_sub = QLabel("")
        self.lbl_sub.setStyleSheet("font-size:13px;color:rgba(255,255,255,0.75);")

        self.lbl_rank = QLabel("–")
        self.lbl_rank.setStyleSheet(
            "font-size:15px;font-weight:bold;padding:6px 16px;"
            "background:rgba(255,255,255,0.2);border-radius:12px;color:white;"
        )

        left = QVBoxLayout()
        left.addWidget(self.lbl_main)
        left.addWidget(self.lbl_sub)

        lay.addLayout(left)
        lay.addStretch()
        lay.addWidget(self.lbl_rank, alignment=Qt.AlignVCenter)

    def update_hs(self, avg: float, rank: str):
        self.lbl_main.setText(f"{avg:.2f} / 10")
        self.lbl_sub.setText("Điểm trung bình tất cả môn")
        self.lbl_rank.setText(f"🏅 {rank}")

    def update_sv(self, gpa4: float, gpa10: float, rank: str):
        self.lbl_main.setText(f"GPA {gpa4:.2f} / 4.0")
        self.lbl_sub.setText(f"Quy đổi hệ 10: {gpa10:.2f}   •   Xếp loại: {rank}")
        self.lbl_rank.setText(f"🎓 {rank}")


# ─────────────────────────────────────────────────────────────
#  SEMESTER BLOCK  – một khối học kỳ
# ─────────────────────────────────────────────────────────────
class SemesterBlock(QFrame):
    """
    Một khối UI đại diện cho một học kỳ:
      • Header: tên + stats + nút menu (⋮)
      • QTableWidget các môn (auto-height, không scroll dọc)
      • Nút "+ Thêm môn học" dashed
    """

    # Chiều cao mỗi dòng bảng (px)
    ROW_H   = 46
    # Chiều cao header bảng (px)
    HEADER_H = 36

    def __init__(self, semester: dict, mode: str,
                 ctrl: GradeController, user_id: int,
                 parent_widget: "GradeWidget"):
        super().__init__()
        self.semester      = semester
        self.semester_id   = semester["id"]
        self.mode          = mode
        self.ctrl          = ctrl
        self.user_id       = user_id
        self.parent_widget = parent_widget   # GradeWidget – để gọi refresh banner

        self.setObjectName("SemesterBlock")
        self.setStyleSheet("""
            QFrame#SemesterBlock {
                background: transparent;
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 12px;
                margin-bottom: 8px;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── HEADER ──
        root.addWidget(self._build_header())

        # ── TABLE ──
        self.table = self._make_table()
        root.addWidget(self.table)

        # ── ADD BUTTON (dashed) ──
        root.addWidget(self._build_add_btn())

        self._refresh_table()

    # ── BUILD HEADER ──────────────────────────────────────────
    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("SemesterHeader")
        header.setStyleSheet("""
            QWidget#SemesterHeader {
                background: transparent;
                border-bottom: 1px solid rgba(0,0,0,0.07);
            }
        """)

        lay = QHBoxLayout(header)
        lay.setContentsMargins(16, 12, 12, 12)
        lay.setSpacing(12)

        self.lbl_name = QLabel(self.semester.get("name", "Học kỳ"))
        self.lbl_name.setStyleSheet(
            "font-size:15px;font-weight:bold;color:#1E2328;"
        )
        lay.addWidget(self.lbl_name)
        lay.addStretch()

        self.lbl_stats = QLabel()
        self.lbl_stats.setStyleSheet("font-size:12px;color:#9095A0;")
        lay.addWidget(self.lbl_stats)

        # ⋮ menu
        btn_menu = QPushButton("⋮")
        btn_menu.setFixedSize(28, 28)
        btn_menu.setCursor(Qt.PointingHandCursor)
        btn_menu.setStyleSheet(
            "QPushButton{background:transparent;border:none;font-size:16px;color:#6F767E;border-radius:6px;}"
            "QPushButton:hover{background:rgba(0,0,0,0.07);}"
        )
        btn_menu.clicked.connect(self._show_menu)
        lay.addWidget(btn_menu)

        return header

    # ── BUILD TABLE ───────────────────────────────────────────
    def _make_table(self) -> QTableWidget:
        tbl = QTableWidget()
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setAlternatingRowColors(False)
        tbl.verticalHeader().setVisible(False)
        tbl.setShowGrid(False)
        tbl.setFocusPolicy(Qt.NoFocus)
        # Tắt scroll dọc – chiều cao được điều chỉnh thủ công
        tbl.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        tbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return tbl

    def _adjust_table_height(self):
        """Tự điều chỉnh height để không sinh ra scrollbar dọc thừa."""
        rows  = self.table.rowCount()
        total = self.HEADER_H + rows * self.ROW_H + 2   # +2 border
        self.table.setFixedHeight(total)

    # ── BUILD ADD BUTTON ──────────────────────────────────────
    def _build_add_btn(self) -> QPushButton:
        btn = QPushButton("+ Thêm môn học")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1.5px dashed #B0B7C3;
                border-radius: 8px;
                color: #6F767E;
                font-size: 13px;
                margin: 8px 16px 12px 16px;
            }
            QPushButton:hover {
                border-color: #2D60FF;
                color: #2D60FF;
                background: rgba(45,96,255,0.04);
            }
        """)
        btn.clicked.connect(self._open_add_dialog)
        return btn

    # ── CONTEXT MENU (⋮) ──────────────────────────────────────
    def _show_menu(self):
        menu = QMenu(self)
        act_rename = menu.addAction("✏️  Đổi tên học kỳ")
        act_delete = menu.addAction("🗑️  Xóa học kỳ")
        act_delete.setStyleSheet("color:#EF4444;")
        chosen = menu.exec(QCursor.pos())

        if chosen == act_rename:
            self._rename_semester()
        elif chosen == act_delete:
            self._delete_semester()

    def _rename_semester(self):
        name, ok = QInputDialog.getText(
            self.window(), "Đổi tên học kỳ", "Tên mới:",
            text=self.semester.get("name", "")
        )
        if ok and name.strip():
            self.ctrl.rename_semester(self.semester_id, name.strip())
            self.semester["name"] = name.strip()
            self.lbl_name.setText(name.strip())

    def _delete_semester(self):
        reply = QMessageBox.question(
            self.window(), "Xác nhận",
            f"Xóa học kỳ '{self.semester.get('name')}' và toàn bộ môn học?\nHành động này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ctrl.delete_semester(self.semester_id)
            self.parent_widget._refresh()   # rebuild toàn bộ

    # ── OPEN DIALOG ───────────────────────────────────────────
    def _open_add_dialog(self, edit_data=None, editing_id=None):
        if self.mode == GradeWidget.MODE_HS:
            dlg = HSSubjectDialog(self.window(), edit_data)
        else:
            dlg = SVSubjectDialog(self.window(), edit_data)

        if dlg.exec() != QDialog.Accepted:
            return

        d = dlg.get_data()
        if editing_id is not None:
            self.ctrl.update_subject(
                editing_id, d["subject_name"],
                d["credits"], d["scores"],
                semester_id=self.semester_id
            )
        else:
            self.ctrl.add_subject(
                self.user_id, self.mode,
                d["subject_name"], d["credits"], d["scores"],
                semester_id=self.semester_id
            )

        self._refresh_table()
        self.parent_widget._refresh_banner()

    def _open_edit_dialog(self, subject_id, row_data):
        self._open_add_dialog(edit_data=row_data, editing_id=subject_id)

    # ── DELETE SUBJECT ────────────────────────────────────────
    def _delete_subject(self, subject_id):
        reply = QMessageBox.question(
            self, tr("confirm"), tr("confirm_delete_msg"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ctrl.delete_subject(subject_id)
            self._refresh_table()
            self.parent_widget._refresh_banner()

    # ── REFRESH ───────────────────────────────────────────────
    def _refresh_table(self):
        subjects = self.ctrl.get_subjects_by_semester(self.semester_id)
        if self.mode == GradeWidget.MODE_HS:
            self._build_hs_table(subjects)
            self._update_stats_hs(subjects)
        else:
            self._build_sv_table(subjects)
            self._update_stats_sv(subjects)
        self._adjust_table_height()

    # ── STATS LABEL ───────────────────────────────────────────
    def _update_stats_hs(self, subjects):
        count = len(subjects)
        avgs  = []
        for s in subjects:
            avg = GradeController.calc_hs_average(_parse_scores(s["scores_data"]))
            if avg:
                avgs.append(avg)
        overall = GradeController.hs_overall(avgs) if avgs else 0.0
        self.lbl_stats.setText(
            f"Số môn: {count}   •   ĐTB: {overall:.2f}" if count else "Chưa có môn học"
        )

    def _update_stats_sv(self, subjects):
        count   = len(subjects)
        sv_list = []
        total_credits = 0
        for s in subjects:
            avg10 = GradeController.calc_sv_average(_parse_scores(s["scores_data"]))
            c = int(s.get("credits", 3))
            total_credits += c
            if avg10:
                sv_list.append({"avg10": avg10, "credits": c})

        if sv_list:
            gpa4  = GradeController.calc_gpa4(sv_list)
            gpa10 = GradeController.calc_gpa10(sv_list)
            self.lbl_stats.setText(
                f"Số môn: {count}   •   TC: {total_credits}   •   "
                f"GPA 10: {gpa10:.2f}   •   GPA 4: {gpa4:.2f}"
            )
        else:
            self.lbl_stats.setText(
                f"Số môn: {count}   •   TC: {total_credits}" if count else "Chưa có môn học"
            )

    # ── HỌC SINH TABLE ────────────────────────────────────────
    def _build_hs_table(self, subjects):
        headers = [
            tr("subject"), tr("tx_score"), tr("gk_score"),
            tr("ck_score"), tr("avg_score"), tr("rank"), ""
        ]
        tbl = self.table
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.setRowCount(len(subjects))

        hh = tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 6):
            hh.setSectionResizeMode(c, QHeaderView.ResizeToContents if c != 4
                                       else QHeaderView.Stretch)
        hh.setSectionResizeMode(6, QHeaderView.Fixed)
        tbl.setColumnWidth(6, 100)

        for row, s in enumerate(subjects):
            scores = _parse_scores(s["scores_data"])
            avg    = GradeController.calc_hs_average(scores)
            rank, color = GradeController.hs_rank(avg)

            tx_list = scores.get("tx") or []
            tx_str  = " / ".join(f"{x:.1f}" for x in tx_list) if tx_list else "–"
            gk_str  = f"{scores['gk']:.1f}" if scores.get("gk") is not None else "–"
            ck_str  = f"{scores['ck']:.1f}" if scores.get("ck") is not None else "–"

            row_data = [
                s["subject_name"], tx_str, gk_str, ck_str,
                f"{avg:.2f}" if avg else "–", rank,
            ]
            for col, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 4 and avg:
                    item.setForeground(QColor("#2D60FF"))
                    f = item.font(); f.setPointSize(11); f.setBold(True); item.setFont(f)
                if col == 5:
                    item.setForeground(QColor(color))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                tbl.setItem(row, col, item)

            self._add_action_buttons(
                row, 6, s["id"],
                edit_data={"subject_name": s["subject_name"],
                           "credits": s["credits"], "scores": scores}
            )
            tbl.setRowHeight(row, self.ROW_H)

    # ── SINH VIÊN TABLE ───────────────────────────────────────
    def _build_sv_table(self, subjects):
        headers = [
            tr("subject"), tr("credits"), tr("cc"), tr("bt"),
            tr("gk"), tr("ck"), tr("avg"), tr("letter"), tr("gpa4"), ""
        ]
        tbl = self.table
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.setRowCount(len(subjects))

        hh = tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 9):
            hh.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(9, QHeaderView.Fixed)
        tbl.setColumnWidth(9, 100)

        for row, s in enumerate(subjects):
            scores  = _parse_scores(s["scores_data"])
            avg10   = GradeController.calc_sv_average(scores)
            letter  = GradeController.score_to_letter(avg10) if avg10 else "–"
            gpa4    = GradeController.letter_to_gpa4(letter) if letter != "–" else 0.0
            l_color = GradeController.letter_color(letter)

            def fmt(k): return f"{scores[k]:.1f}" if scores.get(k) is not None else "–"

            row_data = [
                s["subject_name"], str(s["credits"]),
                fmt("cc"), fmt("bt"), fmt("gk"), fmt("ck"),
                f"{avg10:.2f}" if avg10 else "–",
                letter, f"{gpa4:.1f}",
            ]
            for col, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 6 and avg10:
                    item.setForeground(QColor("#2D60FF"))
                    f = item.font(); f.setPointSize(11); f.setBold(True); item.setFont(f)
                if col == 7:
                    item.setForeground(QColor(l_color))
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                if col == 8:
                    item.setForeground(QColor("#1E2328"))
                tbl.setItem(row, col, item)

            self._add_action_buttons(
                row, 9, s["id"],
                edit_data={"subject_name": s["subject_name"],
                           "credits": s["credits"], "scores": scores}
            )
            tbl.setRowHeight(row, self.ROW_H)

    # ── ACTION BUTTONS ────────────────────────────────────────
    def _add_action_buttons(self, row, col, subject_id, edit_data):
        cell = QWidget()
        lay  = QHBoxLayout(cell)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(4)

        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(30, 30)
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setToolTip(tr("edit"))
        btn_edit.setObjectName("GradeEditBtn")
        btn_edit.clicked.connect(
            lambda _, sid=subject_id, ed=edit_data: self._open_edit_dialog(sid, ed)
        )

        btn_del = QPushButton("🗑️")
        btn_del.setFixedSize(30, 30)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setToolTip(tr("delete"))
        btn_del.setObjectName("GradeDeleteBtn")
        btn_del.clicked.connect(
            lambda _, sid=subject_id: self._delete_subject(sid)
        )

        lay.addWidget(btn_edit)
        lay.addWidget(btn_del)
        self.table.setCellWidget(row, col, cell)


# ─────────────────────────────────────────────────────────────
#  MAIN WIDGET
# ─────────────────────────────────────────────────────────────
class GradeWidget(QWidget):
    MODE_HS = "student"
    MODE_SV = "university"

    def __init__(self, grade_controller: GradeController, user_id: int):
        super().__init__()

        self._lm = LanguageManager.instance()
        self._lm.language_changed.connect(self._retranslate)

        self.ctrl    = grade_controller
        self.user_id = user_id
        self.mode    = self.MODE_HS

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # ── HEADER ──────────────────────────────────────────
        header = QHBoxLayout()

        self.lbl_title = QLabel(tr("grade_title"))
        self.lbl_title.setObjectName("GradeTitle")
        header.addWidget(self.lbl_title)
        header.addStretch()

        # Mode toggle
        toggle = QFrame()
        toggle.setObjectName("GradeModeToggle")
        t_lay = QHBoxLayout(toggle)
        t_lay.setContentsMargins(4, 4, 4, 4)
        t_lay.setSpacing(4)

        self.btn_hs = QPushButton(tr("hs_mode"))
        self.btn_sv = QPushButton(tr("sv_mode"))
        for b in (self.btn_hs, self.btn_sv):
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setObjectName("GradeModeBtn")
        self.btn_hs.setChecked(True)
        self.btn_hs.clicked.connect(lambda: self._switch_mode(self.MODE_HS))
        self.btn_sv.clicked.connect(lambda: self._switch_mode(self.MODE_SV))
        t_lay.addWidget(self.btn_hs)
        t_lay.addWidget(self.btn_sv)
        header.addWidget(toggle)

        # "+ Thêm học kỳ"
        self.btn_add_semester = QPushButton("+ Thêm học kỳ")
        self.btn_add_semester.setCursor(Qt.PointingHandCursor)
        self.btn_add_semester.setObjectName("BtnAddSchedule")
        self.btn_add_semester.clicked.connect(self._add_semester)
        header.addWidget(self.btn_add_semester)

        root.addLayout(header)

        # ── SUMMARY BANNER ───────────────────────────────────
        self.banner = SummaryBanner()
        root.addWidget(self.banner)

        # ── SCROLL AREA chứa các SemesterBlock ──────────────
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea{background:transparent;}")

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background:transparent;")
        self.scroll_layout  = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 8, 0)
        self.scroll_layout.setSpacing(16)
        self.scroll_layout.addStretch()   # placeholder stretch ở cuối

        self.scroll.setWidget(self.scroll_content)
        root.addWidget(self.scroll)

        self._refresh()

    # ── MODE SWITCH ──────────────────────────────────────────
    def _switch_mode(self, mode):
        self.mode = mode
        self.btn_hs.setChecked(mode == self.MODE_HS)
        self.btn_sv.setChecked(mode == self.MODE_SV)
        self._refresh()

    # ── ADD SEMESTER ─────────────────────────────────────────
    def _add_semester(self):
        name, ok = QInputDialog.getText(
            self, "Thêm học kỳ", "Tên học kỳ (ví dụ: Học kỳ 1 – 2024/2025):"
        )
        if ok and name.strip():
            self.ctrl.add_semester(self.user_id, self.mode, name.strip())
            self._refresh()

    # ── FULL REFRESH (rebuild toàn bộ scroll area) ───────────
    def _refresh(self):
        # Xóa tất cả SemesterBlock cũ (giữ lại stretch cuối)
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        semesters = self.ctrl.get_semesters(self.user_id, self.mode)
        for sem in semesters:
            block = SemesterBlock(
                semester=sem, mode=self.mode,
                ctrl=self.ctrl, user_id=self.user_id,
                parent_widget=self
            )
            # Chèn trước stretch
            self.scroll_layout.insertWidget(
                self.scroll_layout.count() - 1, block
            )

        if not semesters:
            self._show_empty_hint()

        self._refresh_banner()

    def _show_empty_hint(self):
        """Hiển thị gợi ý khi chưa có học kỳ nào."""
        hint = QLabel("Nhấn \"+ Thêm học kỳ\" để bắt đầu quản lý điểm theo từng kỳ.")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color:#9095A0;font-size:14px;padding:40px 0;")
        self.scroll_layout.insertWidget(0, hint)

    # ── REFRESH BANNER ONLY (không rebuild blocks) ───────────
    def _refresh_banner(self):
        subjects = self.ctrl.get_subjects(self.user_id, self.mode)
        if self.mode == self.MODE_HS:
            self._update_banner_hs(subjects)
        else:
            self._update_banner_sv(subjects)

    # ── BANNER UPDATE ─────────────────────────────────────────
    def _update_banner_hs(self, subjects):
        avgs = []
        for s in subjects:
            avg = GradeController.calc_hs_average(_parse_scores(s["scores_data"]))
            if avg:
                avgs.append(avg)
                
        # Thêm đoạn này: Nếu không có môn nào hoặc tất cả các môn đều chưa có điểm
        if not subjects or not avgs:
            self.banner.lbl_main.setText("–")
            self.banner.lbl_sub.setText(tr("no_subject"))
            self.banner.lbl_rank.setText("–")
            return
            
        overall = GradeController.hs_overall(avgs)
        rank, _ = GradeController.hs_rank(overall)
        self.banner.update_hs(overall, rank)

    def _update_banner_sv(self, subjects):
        sv_list = []
        for s in subjects:
            avg10 = GradeController.calc_sv_average(_parse_scores(s["scores_data"]))
            if avg10:
                sv_list.append({"avg10": avg10, "credits": s["credits"]})
                
        # Thêm đoạn này: Nếu không có môn nào hoặc tất cả các môn đều chưa có điểm
        if not subjects or not sv_list:
            self.banner.lbl_main.setText("–")
            self.banner.lbl_sub.setText(tr("no_subject"))
            self.banner.lbl_rank.setText("–")
            return
            
        gpa4  = GradeController.calc_gpa4(sv_list)
        gpa10 = GradeController.calc_gpa10(sv_list)
        rank, _ = GradeController.gpa4_rank(gpa4)
        self.banner.update_sv(gpa4, gpa10, rank)

    # ── RETRANSLATE ───────────────────────────────────────────
    def _retranslate(self):
        self.lbl_title.setText(tr("grade_title"))
        self.btn_hs.setText(tr("grade_student"))
        self.btn_sv.setText(tr("grade_university"))
        self._refresh()