import json

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QDoubleSpinBox, QSpinBox, QAbstractItemView,
    QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from src.ui.settings_widget import LanguageManager, tr
from src.controllers.grade_controller import GradeController


# =====================================================
#  DIALOG – THÊM / SỬA MÔN (HỌC SINH)
# =====================================================
class HSSubjectDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
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
        self.inp_name.setPlaceholderText("VD: Toán, Văn, Anh …")
        form.addRow(tr("subject_name"), self.inp_name)

        # Điểm thường xuyên (tối đa 4)
        tx_frame = QFrame()
        tx_lay   = QHBoxLayout(tx_frame)
        tx_lay.setContentsMargins(0, 0, 0, 0)
        tx_lay.setSpacing(6)
        self.tx_spins = []
        for i in range(4):
            sp = QDoubleSpinBox()
            sp.setRange(-1, 10)
            sp.setValue(-1)
            sp.setSpecialValueText("–")
            sp.setSingleStep(0.1)
            sp.setDecimals(1)
            sp.setFixedWidth(70)
            sp.setObjectName("GradeSpinBox")
            tx_lay.addWidget(sp)
            self.tx_spins.append(sp)
        form.addRow(tr("tx_score_label"), tx_frame)

        self.sp_gk = QDoubleSpinBox()
        self.sp_gk.setRange(-1, 10)
        self.sp_gk.setValue(-1)
        self.sp_gk.setSpecialValueText("–")
        self.sp_gk.setSingleStep(0.1)
        self.sp_gk.setDecimals(1)
        self.sp_gk.setObjectName("GradeSpinBox")
        form.addRow(tr("gk_score_label"), self.sp_gk)

        self.sp_ck = QDoubleSpinBox()
        self.sp_ck.setRange(-1, 10)
        self.sp_ck.setValue(-1)
        self.sp_ck.setSpecialValueText("–")
        self.sp_ck.setSingleStep(0.1)
        self.sp_ck.setDecimals(1)
        self.sp_ck.setObjectName("GradeSpinBox")
        form.addRow(tr("ck_score_label"), self.sp_ck)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.Ok).setText("Lưu")
        btns.button(QDialogButtonBox.Cancel).setText("Hủy")
        btns.button(QDialogButtonBox.Ok).setStyleSheet(
            "background:#2D60FF;color:white;border-radius:8px;padding:8px 20px;font-weight:bold;border:none;"
        )
        layout.addWidget(btns)

        if data:
            self._fill(data)

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
            QMessageBox.warning(
                self,
                tr("invalid_input"),
                tr("invalid_input_msg")
            )
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


# =====================================================
#  DIALOG – THÊM / SỬA MÔN (SINH VIÊN)
# =====================================================
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
        self.inp_name.setPlaceholderText("VD: Giải tích, CTDL&GT …")
        form.addRow(tr("subject_name"), self.inp_name)

        self.sp_credits = QSpinBox()
        self.sp_credits.setRange(1, 10)
        self.sp_credits.setValue(3)
        self.sp_credits.setObjectName("GradeSpinBox")
        form.addRow("Số tín chỉ:", self.sp_credits)

        def score_spin(optional=True):
            sp = QDoubleSpinBox()
            sp.setRange(-1 if optional else 0, 10)
            sp.setValue(-1 if optional else 0)
            if optional:
                sp.setSpecialValueText("Không có")
            sp.setSingleStep(0.1)
            sp.setDecimals(1)
            sp.setObjectName("GradeSpinBox")
            return sp

        self.sp_cc  = score_spin(optional=True)
        self.sp_bt  = score_spin(optional=True)
        self.sp_gk  = score_spin(optional=True)
        self.sp_ck  = score_spin(optional=True)

        form.addRow(tr("cc_optional"), self.sp_cc)
        form.addRow(tr("bt_optional"), self.sp_bt)
        form.addRow(tr("gk_score"), self.sp_gk)
        form.addRow(tr("ck_score"), self.sp_ck)

        layout.addLayout(form)

        note = QLabel("💡 Nếu không có CC/BT, trọng số tự động điều chỉnh.")
        note.setObjectName("GradeNote")
        layout.addWidget(note)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.Ok).setText("Lưu")
        btns.button(QDialogButtonBox.Cancel).setText("Hủy")
        btns.button(QDialogButtonBox.Ok).setStyleSheet(
            "background:#2D60FF;color:white;border-radius:8px;padding:8px 20px;font-weight:bold;border:none;"
        )
        layout.addWidget(btns)

        if data:
            self._fill(data)

    def _fill(self, data):
        self.inp_name.setText(data.get("subject_name", ""))
        self.sp_credits.setValue(data.get("credits", 3))
        s = data.get("scores", {})
        self.sp_cc.setValue(s["cc"]  if s.get("cc")  is not None else -1)
        self.sp_bt.setValue(s["bt"]  if s.get("bt")  is not None else -1)
        self.sp_gk.setValue(s["gk"]  if s.get("gk")  is not None else -1)
        self.sp_ck.setValue(s["ck"]  if s.get("ck")  is not None else -1)

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
                "cc": val(self.sp_cc),
                "bt": val(self.sp_bt),
                "gk": val(self.sp_gk),
                "ck": val(self.sp_ck),
            },
        }


# =====================================================
#  SUMMARY BANNER
# =====================================================
class SummaryBanner(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("CardBlue")
        self.setFixedHeight(110)
        lay = QHBoxLayout(self)
        lay.setSpacing(40)

        self.lbl_main  = QLabel("–")
        self.lbl_main.setStyleSheet("font-size:38px;font-weight:bold;color:white;")

        self.lbl_sub   = QLabel("")
        self.lbl_sub.setStyleSheet("font-size:13px;color:rgba(255,255,255,0.75);")

        self.lbl_rank  = QLabel("–")
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


# =====================================================
#  MAIN WIDGET
# =====================================================
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
        self._editing_id = None  # subject id being edited

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # ── HEADER ──
        header = QHBoxLayout()
        title  = QLabel(tr("grade_title"))
        title.setObjectName("GradeTitle")
        header.addWidget(title)
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

        # Add button
        self.btn_add = QPushButton(tr("grade_add_subject"))
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setObjectName("BtnAddSchedule")
        self.btn_add.clicked.connect(self._open_add_dialog)
        header.addWidget(self.btn_add)

        root.addLayout(header)

        # ── SUMMARY BANNER ──
        self.banner = SummaryBanner()
        root.addWidget(self.banner)

        # ── TABLE ──
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        root.addWidget(self.table)

        self._refresh()

    # ── MODE SWITCH ──
    def _switch_mode(self, mode):
        self.mode = mode
        self.btn_hs.setChecked(mode == self.MODE_HS)
        self.btn_sv.setChecked(mode == self.MODE_SV)
        self._retranslate()
        self._refresh()

    # ── OPEN DIALOG ──
    def _open_add_dialog(self, edit_data=None):
        if self.mode == self.MODE_HS:
            dlg = HSSubjectDialog(self, edit_data)
        else:
            dlg = SVSubjectDialog(self, edit_data)

        if dlg.exec() != QDialog.Accepted:
            return

        d = dlg.get_data()

        if edit_data and self._editing_id:
            self.ctrl.update_subject(
                self._editing_id, d["subject_name"],
                d["credits"], d["scores"]
            )
            self._editing_id = None
        else:
            self.ctrl.add_subject(
                self.user_id, self.mode,
                d["subject_name"], d["credits"], d["scores"]
            )

        self._refresh()

    def _open_edit_dialog(self, subject_id, row_data):
        self._editing_id = subject_id
        self._open_add_dialog(edit_data=row_data)

    # ── DELETE ──
    def _delete_subject(self, subject_id):
        reply = QMessageBox.question(
            self, tr("confirm"), tr("confirm_delete_msg"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ctrl.delete_subject(subject_id)
            self._refresh()

    # ── REFRESH TABLE ──
    def _refresh(self):
        subjects = self.ctrl.get_subjects(self.user_id, self.mode)

        if self.mode == self.MODE_HS:
            self._build_hs_table(subjects)
            self._update_banner_hs(subjects)
        else:
            self._build_sv_table(subjects)
            self._update_banner_sv(subjects)

    # ── HỌC SINH TABLE ──
    def _build_hs_table(self, subjects):
        headers = [
            tr("subject"),
            tr("tx_score"),
            tr("gk_score"),
            tr("ck_score"),
            tr("avg_score"),
            tr("rank"),
            ""
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(subjects))

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 6):
            hh.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 100)

        for row, s in enumerate(subjects):
            scores = json.loads(s["scores_data"]) if isinstance(s["scores_data"], str) else s["scores_data"]
            avg    = GradeController.calc_hs_average(scores)
            rank, color = GradeController.hs_rank(avg)

            tx_list = scores.get("tx") or []
            tx_str  = " / ".join(f"{x:.1f}" for x in tx_list) if tx_list else "–"
            gk_str  = f"{scores['gk']:.1f}" if scores.get("gk") is not None else "–"
            ck_str  = f"{scores['ck']:.1f}" if scores.get("ck") is not None else "–"

            row_data = [
                s["subject_name"],
                tx_str,
                gk_str,
                ck_str,
                f"{avg:.2f}" if avg else "–",
                rank,
            ]

            for col, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 4 and avg:
                    item.setForeground(QColor("#2D60FF"))
                    item.setFont(QFont("", -1, QFont.Bold))
                if col == 5:
                    item.setForeground(QColor(color))
                    item.setFont(QFont("", -1, QFont.Bold))
                self.table.setItem(row, col, item)

            self._add_action_buttons(
                row, 6, s["id"],
                edit_data={"subject_name": s["subject_name"], "credits": s["credits"], "scores": scores}
            )
            self.table.setRowHeight(row, 46)

    # ── SINH VIÊN TABLE ──
    def _build_sv_table(self, subjects):
        headers = [
            tr("subject"),
            tr("credits"),
            tr("cc"),
            tr("bt"),
            tr("gk"),
            tr("ck"),
            tr("avg"),
            tr("letter"),
            tr("gpa4"),
            ""
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(subjects))

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        for c in range(1, 9):
            hh.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(9, QHeaderView.Fixed)
        self.table.setColumnWidth(9, 100)

        for row, s in enumerate(subjects):
            scores  = json.loads(s["scores_data"]) if isinstance(s["scores_data"], str) else s["scores_data"]
            avg10   = GradeController.calc_sv_average(scores)
            letter  = GradeController.score_to_letter(avg10) if avg10 else "–"
            gpa4    = GradeController.letter_to_gpa4(letter) if letter != "–" else 0.0
            l_color = GradeController.letter_color(letter)

            def fmt(k): return f"{scores[k]:.1f}" if scores.get(k) is not None else "–"

            row_data = [
                s["subject_name"],
                str(s["credits"]),
                fmt("cc"), fmt("bt"), fmt("gk"), fmt("ck"),
                f"{avg10:.2f}" if avg10 else "–",
                letter,
                f"{gpa4:.1f}",
            ]

            for col, val in enumerate(row_data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if col == 6 and avg10:
                    item.setForeground(QColor("#2D60FF"))
                    item.setFont(QFont("", -1, QFont.Bold))
                if col == 7:
                    item.setForeground(QColor(l_color))
                    item.setFont(QFont("", -1, QFont.Bold))
                if col == 8:
                    item.setForeground(QColor("#1E2328"))
                self.table.setItem(row, col, item)

            self._add_action_buttons(
                row, 9, s["id"],
                edit_data={"subject_name": s["subject_name"], "credits": s["credits"], "scores": scores}
            )
            self.table.setRowHeight(row, 46)

    # ── ACTION BUTTONS (edit / delete) ──
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
        btn_edit.clicked.connect(lambda _, sid=subject_id, ed=edit_data: self._open_edit_dialog(sid, ed))

        btn_del = QPushButton("🗑️")
        btn_del.setFixedSize(30, 30)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setToolTip(tr("delete"))
        btn_del.setObjectName("GradeDeleteBtn")
        btn_del.clicked.connect(lambda _, sid=subject_id: self._delete_subject(sid))

        lay.addWidget(btn_edit)
        lay.addWidget(btn_del)
        self.table.setCellWidget(row, col, cell)

    # ── BANNER UPDATE ──
    def _update_banner_hs(self, subjects):
        if not subjects:
            self.banner.lbl_main.setText("–")
            self.banner.lbl_sub.setText("Chưa có môn học nào")
            self.banner.lbl_rank.setText("–")
            return

        avgs = []
        for s in subjects:
            scores = json.loads(s["scores_data"]) if isinstance(s["scores_data"], str) else s["scores_data"]
            avg = GradeController.calc_hs_average(scores)
            if avg:
                avgs.append(avg)

        if not avgs:
            return

        overall = GradeController.hs_overall(avgs)
        rank, _ = GradeController.hs_rank(overall)
        self.banner.update_hs(overall, rank)

    def _update_banner_sv(self, subjects):
        if not subjects:
            self.banner.lbl_main.setText("–")
            self.banner.lbl_sub.setText("Chưa có môn học nào")
            self.banner.lbl_rank.setText("–")
            return

        sv_list = []
        for s in subjects:
            scores = json.loads(s["scores_data"]) if isinstance(s["scores_data"], str) else s["scores_data"]
            avg10  = GradeController.calc_sv_average(scores)
            if avg10:
                sv_list.append({"avg10": avg10, "credits": s["credits"]})

        if not sv_list:
            return

        gpa4  = GradeController.calc_gpa4(sv_list)
        gpa10 = GradeController.calc_gpa10(sv_list)
        rank, _ = GradeController.gpa4_rank(gpa4)
        self.banner.update_sv(gpa4, gpa10, rank)

    def _retranslate(self):
        # title
        title = self.findChild(QLabel, "GradeTitle")
        if title:
            title.setText(tr("grade_title"))

        # buttons
        self.btn_add.setText(tr("grade_add_subject"))
        self.btn_hs.setText(tr("grade_student"))
        self.btn_sv.setText(tr("grade_university"))

        # table headers reload luôn theo mode
        self._refresh()