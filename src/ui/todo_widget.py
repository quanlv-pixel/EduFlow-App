import json
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


TODO_FILE = "assets/todos.json"


def load_todos() -> dict:
    """Load all todos from JSON file."""
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_todos(data: dict):
    """Save all todos to JSON file."""
    os.makedirs(os.path.dirname(TODO_FILE), exist_ok=True)
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def today_key() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ──────────────────────────────────────────────
class TodoItemWidget(QFrame):
    """One todo row: [ ☐ ] task text  [×]"""

    def __init__(self, task_id: str, text: str, done: bool, on_toggle, on_delete):
        super().__init__()
        self.task_id   = task_id
        self.on_toggle = on_toggle
        self.on_delete = on_delete
        self.setObjectName("TodoItem")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # ── Checkbox ──
        self.chk = QCheckBox()
        self.chk.setObjectName("TodoCheck")
        self.chk.setChecked(done)
        self.chk.setCursor(Qt.PointingHandCursor)
        self.chk.stateChanged.connect(self._on_check)
        layout.addWidget(self.chk)

        # ── Task label ──
        self.lbl = QLabel(text)
        self.lbl.setObjectName("TodoLabel")
        self.lbl.setWordWrap(True)
        self.lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._update_style(done)
        layout.addWidget(self.lbl)

        # ── Delete button ──
        btn_del = QPushButton("×")
        btn_del.setObjectName("TodoDeleteBtn")
        btn_del.setFixedSize(28, 28)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.clicked.connect(lambda: self.on_delete(self.task_id))
        layout.addWidget(btn_del)

    def _on_check(self, state):
        done = (state == Qt.Checked)
        self._update_style(done)
        self.on_toggle(self.task_id, done)

    def _update_style(self, done: bool):
        font = self.lbl.font()
        font.setStrikeOut(done)
        self.lbl.setFont(font)
        self.lbl.setProperty("done", done)
        # Force QSS re-evaluation
        self.lbl.style().unpolish(self.lbl)
        self.lbl.style().polish(self.lbl)


# ──────────────────────────────────────────────
class TodoWidget(QWidget):
    """Full Todo-List page."""

    def __init__(self):
        super().__init__()
        self._todos: dict = {}   # {task_id: {text, done}}
        self._build_ui()
        self._load_today()

    # ── UI ────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # ── Header card ──
        header_card = QFrame()
        header_card.setObjectName("CardWhite")
        hc_lay = QVBoxLayout(header_card)
        hc_lay.setContentsMargins(20, 18, 20, 18)
        hc_lay.setSpacing(14)

        # Title row
        title_row = QHBoxLayout()
        icon = QLabel("✅")
        icon.setStyleSheet("font-size:22px;")
        title = QLabel("Todo List")
        title.setObjectName("TodoTitle")
        title.setStyleSheet("font-size:20px; font-weight:bold;")

        today_str = datetime.now().strftime("%d/%m/%Y")
        date_lbl = QLabel(today_str)
        date_lbl.setObjectName("TodoDate")

        title_row.addWidget(icon)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(date_lbl)
        hc_lay.addLayout(title_row)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.input = QLineEdit()
        self.input.setObjectName("TodoInput")
        self.input.setPlaceholderText("✏️  Thêm nhiệm vụ mới...")
        self.input.returnPressed.connect(self._add_task)

        btn_add = QPushButton("+ Thêm")
        btn_add.setObjectName("TodoAddBtn")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._add_task)

        input_row.addWidget(self.input)
        input_row.addWidget(btn_add)
        hc_lay.addLayout(input_row)

        root.addWidget(header_card)

        # ── Stats row ──
        self.stat_total  = self._stat_box("📋", "0", "Tổng nhiệm vụ")
        self.stat_done   = self._stat_box("✅", "0", "Hoàn thành")
        self.stat_remain = self._stat_box("⏳", "0", "Còn lại")

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        for w in (self.stat_total, self.stat_done, self.stat_remain):
            stats_row.addWidget(w)
        root.addLayout(stats_row)

        # ── Task list ──
        list_card = QFrame()
        list_card.setObjectName("CardWhite")
        list_lay = QVBoxLayout(list_card)
        list_lay.setContentsMargins(16, 16, 16, 16)
        list_lay.setSpacing(0)

        list_header = QHBoxLayout()
        list_lbl = QLabel("Danh sách nhiệm vụ hôm nay")
        list_lbl.setObjectName("TodoSectionLabel")

        self.btn_clear = QPushButton("🗑  Xóa hoàn thành")
        self.btn_clear.setObjectName("TodoClearBtn")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear_done)

        list_header.addWidget(list_lbl)
        list_header.addStretch()
        list_header.addWidget(self.btn_clear)
        list_lay.addLayout(list_header)
        list_lay.addSpacing(10)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch()

        scroll.setWidget(self.list_container)
        list_lay.addWidget(scroll)

        # Empty state
        self.empty_lbl = QLabel("Chưa có nhiệm vụ nào.\nHãy thêm nhiệm vụ đầu tiên! 🎯")
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        self.empty_lbl.setObjectName("TodoEmptyLabel")

        root.addWidget(list_card, 1)

    def _stat_box(self, icon: str, value: str, label: str) -> QFrame:
        box = QFrame()
        box.setObjectName("TodoStatBox")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)

        row = QHBoxLayout()
        ico = QLabel(icon)
        ico.setStyleSheet("font-size:18px;")
        val = QLabel(value)
        val.setObjectName("TodoStatValue")
        row.addWidget(ico)
        row.addWidget(val)
        row.addStretch()

        lbl = QLabel(label)
        lbl.setObjectName("TodoStatLabel")

        lay.addLayout(row)
        lay.addWidget(lbl)

        # Store reference to value label for updating
        box._value_lbl = val
        return box

    # ── Data ──────────────────────────────────
    def _load_today(self):
        all_data = load_todos()
        self._todos = all_data.get(today_key(), {})
        self._rebuild_list()

    def _save(self):
        all_data = load_todos()
        all_data[today_key()] = self._todos
        save_todos(all_data)

    def _add_task(self):
        text = self.input.text().strip()
        if not text:
            return
        task_id = datetime.now().strftime("%H%M%S%f")
        self._todos[task_id] = {"text": text, "done": False}
        self._save()
        self.input.clear()
        self._rebuild_list()

    def _toggle(self, task_id: str, done: bool):
        if task_id in self._todos:
            self._todos[task_id]["done"] = done
            self._save()
            self._update_stats()

    def _delete(self, task_id: str):
        self._todos.pop(task_id, None)
        self._save()
        self._rebuild_list()

    def _clear_done(self):
        self._todos = {k: v for k, v in self._todos.items() if not v["done"]}
        self._save()
        self._rebuild_list()

    # ── Render ────────────────────────────────
    def _rebuild_list(self):
        # Remove all except stretch
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._todos:
            self.list_layout.insertWidget(0, self.empty_lbl)
            self.empty_lbl.show()
        else:
            self.empty_lbl.hide()
            # Sort: undone first, then done
            sorted_tasks = sorted(
                self._todos.items(),
                key=lambda x: (x[1]["done"], x[0])
            )
            for idx, (task_id, task) in enumerate(sorted_tasks):
                row = TodoItemWidget(
                    task_id  = task_id,
                    text     = task["text"],
                    done     = task["done"],
                    on_toggle= self._toggle,
                    on_delete= self._delete,
                )
                self.list_layout.insertWidget(idx, row)

        self._update_stats()

    def _update_stats(self):
        total  = len(self._todos)
        done   = sum(1 for t in self._todos.values() if t["done"])
        remain = total - done

        self.stat_total._value_lbl.setText(str(total))
        self.stat_done._value_lbl.setText(str(done))
        self.stat_remain._value_lbl.setText(str(remain))