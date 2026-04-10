
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTabWidget, QComboBox, QGridLayout,
    QHeaderView, QAbstractItemView, QFrame, QSizePolicy
)


class EntityTab(QWidget):
    def __init__(self, title, columns, fields, search_placeholder):
        super().__init__()

        self.columns = columns
        self.fields = fields
        self.inputs = {}
        self.detail_labels = {}

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(16, 16, 16, 16)
        page_layout.setSpacing(12)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        # LEFT 
        self.input_frame = QFrame()
        self.input_frame.setObjectName("inputFrame")
        self.input_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(16, 14, 16, 14)
        input_layout.setSpacing(10)

        input_title = QLabel(f"{title} Input")
        input_title.setAlignment(Qt.AlignCenter)
        input_title.setObjectName("sectionTitle")

        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(10)
        form_grid.setVerticalSpacing(8)

        row = 0
        col = 0

        for field in fields:
            field_label = QLabel(field.capitalize() + ":")
            field_label.setObjectName("fieldLabel")

            if field == "gender":
                widget = QComboBox()
                widget.addItems(["Male", "Female"])
            elif field == "year":
                widget = QComboBox()
                widget.addItems(["1", "2", "3", "4", "5", "6"])
            elif field in ["course", "college"]:
                widget = QComboBox()
            else:
                widget = QLineEdit()

            widget.setMinimumHeight(36)

            one_field_layout = QVBoxLayout()
            one_field_layout.setSpacing(4)
            one_field_layout.addWidget(field_label)
            one_field_layout.addWidget(widget)

            self.inputs[field] = widget
            form_grid.addLayout(one_field_layout, row, col)

            col += 1
            if col == 2:
                col = 0
                row += 1

        button_row = QGridLayout()
        button_row.setHorizontalSpacing(10)
        button_row.setVerticalSpacing(8)

        self.add_btn = QPushButton("Add")
        self.add_btn.setObjectName("primaryButton")
        self.update_btn = QPushButton("Update")
        self.update_btn.setObjectName("secondaryButton")
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("dangerButton")
        self.clear_form_btn = QPushButton("Clear Form")
        self.clear_form_btn.setObjectName("ghostButton")
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("ghostButton")

        buttons = [self.add_btn, self.update_btn, self.delete_btn, self.clear_form_btn, self.refresh_btn]
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
        for btn, (r, c) in zip(buttons, positions):
            btn.setMinimumHeight(38)
            button_row.addWidget(btn, r, c)

        button_row.setColumnStretch(0, 1)
        button_row.setColumnStretch(1, 1)
        button_row.setColumnStretch(2, 1)

        input_layout.addWidget(input_title)
        input_layout.addLayout(form_grid)
        input_layout.addLayout(button_row)
        self.input_frame.setLayout(input_layout)

        # RIGHT 

        self.detail_frame = QFrame()
        self.detail_frame.setObjectName("detailFrame")
        self.detail_frame.setMinimumWidth(350)

        detail_layout = QVBoxLayout(self.detail_frame)
        detail_layout.setContentsMargins(16, 14, 16, 14)
        detail_layout.setSpacing(8)

        detail_title = QLabel("Selected Record")
        detail_title.setAlignment(Qt.AlignCenter)
        detail_title.setObjectName("sectionTitle")
        detail_layout.addWidget(detail_title)

        for field in fields:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)

            key = QLabel(field.capitalize() + ":")
            key.setObjectName("detailKey")
            key.setMinimumWidth(90)

            value = QLabel("—")
            value.setObjectName("detailLabel")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)

            self.detail_labels[field] = value

            row_layout.addWidget(key, 0, Qt.AlignTop)
            row_layout.addWidget(value, 1)
            detail_layout.addLayout(row_layout)

        detail_layout.addStretch()

        top_layout.addWidget(self.input_frame, 3)
        top_layout.addWidget(self.detail_frame, 2)

        # SEARCH 
        self.search_frame = QFrame()
        self.search_frame.setObjectName("searchFrame")

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(14, 12, 14, 12)
        search_layout.setSpacing(10)

        search_title = QLabel("Search & Sort")
        search_title.setObjectName("subSectionTitle")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(search_placeholder)
        self.search_input.setMinimumHeight(38)

        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("primaryButton")
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("ghostButton")

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(columns)
        self.sort_combo.setMinimumHeight(38)

        self.order_combo = QComboBox()
        self.order_combo.addItems(["ASC", "DESC"])
        self.order_combo.setMinimumHeight(38)

        self.search_btn.setMinimumHeight(38)
        self.clear_btn.setMinimumHeight(38)

        search_layout.addWidget(search_title)
        search_layout.addWidget(self.search_input, 6)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.clear_btn)
        search_layout.addWidget(QLabel("Sort by"))
        search_layout.addWidget(self.sort_combo)
        search_layout.addWidget(QLabel("Order"))
        search_layout.addWidget(self.order_combo)

        self.search_frame.setLayout(search_layout)

        # TABLE 
        self.table_frame = QFrame()
        self.table_frame.setObjectName("tableFrame")

        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(14, 14, 14, 12)
        table_layout.setSpacing(10)

        table_header_row = QHBoxLayout()
        table_header_row.setSpacing(10)

        table_title = QLabel(f"{title} Records")
        table_title.setObjectName("sectionTitleLeft")

        self.total_label = QLabel("Total: 0")
        self.total_label.setObjectName("statPill")

        table_header_row.addWidget(table_title)
        table_header_row.addStretch()
        table_header_row.addWidget(self.total_label)

        self.table = QTableWidget()
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([c.capitalize() for c in columns])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setMinimumHeight(40)

        page_row = QHBoxLayout()
        page_row.setSpacing(10)

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setObjectName("ghostButton")
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("ghostButton")
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setObjectName("pageInfo")

        self.prev_btn.setMinimumHeight(38)
        self.next_btn.setMinimumHeight(38)

        page_row.addWidget(self.prev_btn)
        page_row.addWidget(self.next_btn)
        page_row.addWidget(self.page_label)
        page_row.addStretch()

        table_layout.addLayout(table_header_row)
        table_layout.addWidget(self.table)
        table_layout.addLayout(page_row)

        self.table_frame.setLayout(table_layout)

        page_layout.addLayout(top_layout)
        page_layout.addWidget(self.search_frame)
        page_layout.addWidget(self.table_frame, 1)

    def get_form_data(self):
        data = {}
        for field, widget in self.inputs.items():
            if isinstance(widget, QComboBox):
                data[field] = widget.currentText().strip()
            else:
                data[field] = widget.text().strip()
        return data

    def set_form_data(self, data):
        for field, value in data.items():
            if field in self.inputs:
                widget = self.inputs[field]
                if isinstance(widget, QComboBox):
                    index = widget.findText(str(value))
                    if index >= 0:
                        widget.setCurrentIndex(index)
                else:
                    widget.setText(str(value))

    def clear_form(self):
        for field, widget in self.inputs.items():
            if isinstance(widget, QComboBox):
                if widget.count() > 0:
                    widget.setCurrentIndex(0)
            else:
                widget.clear()

    def set_combo_items(self, field, items):
        if field in self.inputs and isinstance(self.inputs[field], QComboBox):
            current_text = self.inputs[field].currentText()
            self.inputs[field].clear()
            self.inputs[field].addItems(items)

            index = self.inputs[field].findText(current_text)
            if index >= 0:
                self.inputs[field].setCurrentIndex(index)

    def show_details(self, data):
        for field in self.fields:
            value = data.get(field, "")
            self.detail_labels[field].setText(str(value) if value != "" else "—")

    def clear_details(self):
        for field in self.fields:
            self.detail_labels[field].setText("—")


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Information Management System")
        self.setGeometry(40, 40, 1600, 920)

        self.setStyleSheet("""
            QWidget {
                background: #f5f7fb;
                color: #172033;
                font-size: 13px;
                font-family: "Segoe UI", Arial, sans-serif;
            }

            QFrame#heroCard, QFrame#inputFrame, QFrame#detailFrame, QFrame#searchFrame, QFrame#tableFrame {
                background: white;
                border: 1px solid #e5e7ef;
                border-radius: 18px;
            }

            QLabel#heroTitle {
                font-size: 28px;
                font-weight: 800;
                color: #0f172a;
            }

            QLabel#heroSubtitle {
                font-size: 13px;
                color: #667085;
                padding-top: 2px;
            }

            QLabel#sectionTitle {
                font-size: 18px;
                font-weight: 700;
                color: #101828;
            }

            QLabel#sectionTitleLeft {
                font-size: 17px;
                font-weight: 700;
                color: #101828;
            }

            QLabel#subSectionTitle {
                font-size: 14px;
                font-weight: 700;
                color: #334155;
                padding-right: 8px;
            }

            QLabel#fieldLabel {
                font-size: 12px;
                font-weight: 700;
                color: #344054;
            }

            QLineEdit, QComboBox {
                background: #fbfcfe;
                border: 1px solid #d9deea;
                border-radius: 12px;
                padding: 8px 12px;
                selection-background-color: #dbeafe;
            }

            QLineEdit:hover, QComboBox:hover {
                border: 1px solid #bcc7de;
                background: white;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #7c93ff;
                background: white;
                padding: 7px 11px;
            }

            QPushButton {
                border-radius: 12px;
                font-weight: 700;
                padding: 8px 14px;
                border: 1px solid transparent;
            }

            QPushButton#primaryButton {
                background: #3b82f6;
                color: white;
            }

            QPushButton#primaryButton:hover {
                background: #2563eb;
            }

            QPushButton#secondaryButton {
                background: #eef2ff;
                color: #334155;
                border: 1px solid #d6dcff;
            }

            QPushButton#secondaryButton:hover {
                background: #e2e8ff;
            }

            QPushButton#dangerButton {
                background: #ef4444;
                color: white;
            }

            QPushButton#dangerButton:hover {
                background: #dc2626;
            }

            QPushButton#ghostButton {
                background: #f8fafc;
                color: #334155;
                border: 1px solid #d9deea;
            }

            QPushButton#ghostButton:hover {
                background: #eef2f7;
            }

            QTabWidget::pane {
                border: none;
                background: transparent;
            }

            QTabBar::tab {
                background: #e9eef8;
                color: #334155;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                margin-right: 8px;
                min-width: 110px;
                font-weight: 700;
            }

            QTabBar::tab:selected {
                background: #3b82f6;
                color: white;
            }

            QTabBar::tab:hover:!selected {
                background: #dde6f5;
            }

            QTableWidget {
                background: white;
                alternate-background-color: #f8fbff;
                border: 1px solid #e6eaf2;
                border-radius: 14px;
                gridline-color: transparent;
                padding: 4px;
            }

            QTableWidget::item {
                border-bottom: 1px solid #edf1f7;
                padding: 8px;
            }

            QTableWidget::item:selected {
                background: #dbeafe;
                color: #0f172a;
            }

            QTableWidget::item:hover {
                background: #f1f5ff;
            }

            QHeaderView::section {
                background: #f8fafc;
                color: #475467;
                border: none;
                border-bottom: 1px solid #e5e7ef;
                padding: 10px 8px;
                font-size: 12px;
                font-weight: 800;
            }

            QLabel#detailKey {
                font-size: 12px;
                font-weight: 700;
                color: #667085;
            }

            QLabel#detailLabel {
                font-size: 13px;
                font-weight: 600;
                color: #101828;
            }

            QLabel#statPill {
                background: #eef4ff;
                color: #2757c5;
                border: 1px solid #d6e4ff;
                border-radius: 999px;
                padding: 8px 14px;
                font-weight: 700;
            }

            QLabel#pageInfo {
                color: #667085;
                font-weight: 700;
                padding-left: 6px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        hero_card = QFrame()
        hero_card.setObjectName("heroCard")

        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(20, 14, 20, 14)
        hero_layout.setSpacing(2)

        header = QLabel("Student Information Management System")
        header.setObjectName("heroTitle")
        header.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Manage students, programs, and colleges in one clean workspace.")
        subtitle.setObjectName("heroSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        hero_layout.addWidget(header)
        hero_layout.addWidget(subtitle)

        self.tabs = QTabWidget()

        self.student_tab = EntityTab(
            "Student",
            ["id", "firstname", "lastname", "course", "year", "gender"],
            ["id", "firstname", "lastname", "course", "year", "gender"],
            "Search student..."
        )

        self.program_tab = EntityTab(
            "Program",
            ["code", "name", "college"],
            ["code", "name", "college"],
            "Search program..."
        )

        self.college_tab = EntityTab(
            "College",
            ["code", "name"],
            ["code", "name"],
            "Search college..."
        )

        self.tabs.addTab(self.student_tab, "Students")
        self.tabs.addTab(self.program_tab, "Programs")
        self.tabs.addTab(self.college_tab, "Colleges")

        main_layout.addWidget(hero_card)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
