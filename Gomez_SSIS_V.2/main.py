import re
import sys
import sqlite3

from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem

from database import connect_db, create_tables
from gui import MainUI


class MainWindow(MainUI):
    def __init__(self):
        super().__init__()

        create_tables()
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

        self.page_size = 20

        self.student_page = 1
        self.program_page = 1
        self.college_page = 1

        self.student_sort_column = "id"
        self.student_sort_order = "ASC"

        self.program_sort_column = "code"
        self.program_sort_order = "ASC"

        self.college_sort_column = "code"
        self.college_sort_order = "ASC"

        self.load_reference_combos()

        self.connect_student_signals()
        self.connect_program_signals()
        self.connect_college_signals()

        self.load_students()
        self.load_programs()
        self.load_colleges()

    def closeEvent(self, event):
        try:
            self.conn.close()
        except Exception:
            pass
        event.accept()

    def get_total_pages(self, total_count):
        if total_count == 0:
            return 1
        return (total_count + self.page_size - 1) // self.page_size

    def toggle_sort_order(self, current_order):
        if current_order == "ASC":
            return "DESC"
        return "ASC"

    def get_selected_row_indexes(self, table_widget):
        rows = table_widget.selectionModel().selectedRows()
        return sorted([row.row() for row in rows], reverse=True)

    def get_program_codes(self):
        self.cursor.execute("SELECT code FROM program ORDER BY code")
        return [row["code"] for row in self.cursor.fetchall()]

    def get_college_codes(self):
        self.cursor.execute("SELECT code FROM college ORDER BY code")
        return [row["code"] for row in self.cursor.fetchall()]

    def get_program_display(self, code):
        self.cursor.execute("SELECT name FROM program WHERE code = ?", (code,))
        row = self.cursor.fetchone()
        if row:
            return f"{code} - {row['name']}"
        return code

    def load_reference_combos(self):
        self.student_tab.set_combo_items("course", self.get_program_codes())
        self.program_tab.set_combo_items("college", self.get_college_codes())

 #========================================#

    def connect_student_signals(self):
        self.student_tab.search_btn.clicked.connect(self.search_students)
        self.student_tab.clear_btn.clicked.connect(self.clear_student_search)
        self.student_tab.refresh_btn.clicked.connect(self.load_students)
        self.student_tab.add_btn.clicked.connect(self.add_student)
        self.student_tab.update_btn.clicked.connect(self.update_student)
        self.student_tab.delete_btn.clicked.connect(self.delete_student)
        self.student_tab.clear_form_btn.clicked.connect(self.student_tab.clear_form)
        self.student_tab.prev_btn.clicked.connect(self.prev_student_page)
        self.student_tab.next_btn.clicked.connect(self.next_student_page)
        self.student_tab.sort_combo.currentTextChanged.connect(self.student_combo_sort_changed)
        self.student_tab.order_combo.currentTextChanged.connect(self.student_combo_sort_changed)
        self.student_tab.table.horizontalHeader().sectionClicked.connect(self.student_header_clicked)
        self.student_tab.search_input.textChanged.connect(self.search_students)
        self.student_tab.table.itemSelectionChanged.connect(self.student_row_selected)

    def valid_student_id(self, student_id):
        return re.fullmatch(r"\d{4}-\d{4}", student_id) is not None

    def student_row_selected(self):
        selected_rows = self.get_selected_row_indexes(self.student_tab.table)

        if len(selected_rows) == 1:
            row = selected_rows[0]
            course_code = self.student_tab.table.item(row, 3).data(1000)
            if course_code is None:
                course_code = self.student_tab.table.item(row, 3).text()

            data = {
                "id": self.student_tab.table.item(row, 0).text(),
                "firstname": self.student_tab.table.item(row, 1).text(),
                "lastname": self.student_tab.table.item(row, 2).text(),
                "course": course_code,
                "year": self.student_tab.table.item(row, 4).text(),
                "gender": self.student_tab.table.item(row, 5).text()
            }

            display_data = dict(data)
            display_data["course"] = self.get_program_display(course_code)

            self.student_tab.set_form_data(data)
            self.student_tab.show_details(display_data)
        else:
            self.student_tab.clear_details()

    def student_combo_sort_changed(self):
        self.student_sort_column = self.student_tab.sort_combo.currentText()
        self.student_sort_order = self.student_tab.order_combo.currentText()
        self.student_page = 1
        self.load_students()

    def student_header_clicked(self, index):
        clicked_column = self.student_tab.columns[index]

        if self.student_sort_column == clicked_column:
            self.student_sort_order = self.toggle_sort_order(self.student_sort_order)
        else:
            self.student_sort_column = clicked_column
            self.student_sort_order = "ASC"

        self.student_tab.sort_combo.setCurrentText(self.student_sort_column)
        self.student_tab.order_combo.setCurrentText(self.student_sort_order)
        self.student_page = 1
        self.load_students()

    def search_students(self):
        self.student_page = 1
        self.load_students()

    def clear_student_search(self):
        self.student_tab.search_input.clear()
        self.student_page = 1
        self.load_students()

    def prev_student_page(self):
        if self.student_page > 1:
            self.student_page -= 1
            self.load_students()

    def next_student_page(self):
        total = self.count_students()
        total_pages = self.get_total_pages(total)
        if self.student_page < total_pages:
            self.student_page += 1
            self.load_students()

    def count_students(self):
        text = self.student_tab.search_input.text().strip()

        if text:
            self.cursor.execute("""
                SELECT COUNT(*) AS total
                FROM student s
                LEFT JOIN program p ON s.course = p.code
                WHERE s.id LIKE ?
                   OR s.firstname LIKE ?
                   OR s.lastname LIKE ?
                   OR s.course LIKE ?
                   OR s.gender LIKE ?
                   OR p.name LIKE ?
            """, (f"%{text}%", f"%{text}%", f"%{text}%", f"%{text}%", f"%{text}%", f"%{text}%"))
        else:
            self.cursor.execute("SELECT COUNT(*) AS total FROM student")

        return self.cursor.fetchone()["total"]

    def load_students(self):
        text = self.student_tab.search_input.text().strip()
        sort_col = self.student_sort_column
        sort_order = self.student_sort_order
        offset = (self.student_page - 1) * self.page_size

        valid_sort_map = {
            "id": "s.id",
            "firstname": "s.firstname",
            "lastname": "s.lastname",
            "course": "s.course",
            "year": "s.year",
            "gender": "s.gender"
        }
        sort_sql = valid_sort_map.get(sort_col, "s.id")

        if text:
            self.cursor.execute(f"""
                SELECT s.*, p.name AS program_name
                FROM student s
                LEFT JOIN program p ON s.course = p.code
                WHERE s.id LIKE ?
                   OR s.firstname LIKE ?
                   OR s.lastname LIKE ?
                   OR s.course LIKE ?
                   OR s.gender LIKE ?
                   OR p.name LIKE ?
                ORDER BY {sort_sql} {sort_order}
                LIMIT ? OFFSET ?
            """, (
                f"%{text}%", f"%{text}%", f"%{text}%",
                f"%{text}%", f"%{text}%", f"%{text}%",
                self.page_size, offset
            ))
        else:
            self.cursor.execute(f"""
                SELECT s.*, p.name AS program_name
                FROM student s
                LEFT JOIN program p ON s.course = p.code
                ORDER BY {sort_sql} {sort_order}
                LIMIT ? OFFSET ?
            """, (self.page_size, offset))

        rows = self.cursor.fetchall()
        self.student_tab.table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            course_display = row_data["course"]
            if row_data["program_name"]:
                course_display = f"{row_data['course']} - {row_data['program_name']}"

            values = [
                row_data["id"],
                row_data["firstname"],
                row_data["lastname"],
                course_display,
                row_data["year"],
                row_data["gender"]
            ]

            for col_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col_index == 3:
                    item.setData(1000, row_data["course"])
                self.student_tab.table.setItem(row_index, col_index, item)

        total = self.count_students()
        total_pages = self.get_total_pages(total)

        if self.student_page > total_pages:
            self.student_page = total_pages

        self.student_tab.page_label.setText(f"Page {self.student_page} of {total_pages}")
        self.student_tab.total_label.setText(f"Total: {total}")

    def add_student(self):
        self.load_reference_combos()
        data = self.student_tab.get_form_data()

        if not all(data.values()):
            QMessageBox.warning(self, "Error", "Please complete all student fields.")
            return

        if not self.valid_student_id(data["id"]):
            QMessageBox.warning(self, "Error", "Student ID must be in YYYY-NNNN format.")
            return

        try:
            year_value = int(data["year"])
        except ValueError:
            QMessageBox.warning(self, "Error", "Year must be a number.")
            return

        if year_value < 1 or year_value > 6:
            QMessageBox.warning(self, "Error", "Year must be from 1 to 6 only.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO student (id, firstname, lastname, course, year, gender)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["id"], data["firstname"], data["lastname"],
                data["course"], year_value, data["gender"]
            ))
            self.conn.commit()
            self.student_tab.clear_form()
            self.student_tab.clear_details()
            self.load_students()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Student ID already exists.")

    def update_student(self):
        selected_rows = self.get_selected_row_indexes(self.student_tab.table)

        if len(selected_rows) != 1:
            QMessageBox.warning(self, "Error", "Please select only one student to update.")
            return

        old_id = self.student_tab.table.item(selected_rows[0], 0).text()
        data = self.student_tab.get_form_data()

        if not all(data.values()):
            QMessageBox.warning(self, "Error", "Please complete all student fields.")
            return

        if not self.valid_student_id(data["id"]):
            QMessageBox.warning(self, "Error", "Student ID must be in YYYY-NNNN format.")
            return

        try:
            year_value = int(data["year"])
        except ValueError:
            QMessageBox.warning(self, "Error", "Year must be a number.")
            return

        if year_value < 1 or year_value > 6:
            QMessageBox.warning(self, "Error", "Year must be from 1 to 6 only.")
            return

        try:
            self.cursor.execute("""
                UPDATE student
                SET id = ?, firstname = ?, lastname = ?, course = ?, year = ?, gender = ?
                WHERE id = ?
            """, (
                data["id"], data["firstname"], data["lastname"],
                data["course"], year_value, data["gender"], old_id
            ))
            self.conn.commit()
            self.load_students()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Could not update student.")

    def delete_student(self):
        selected_rows = self.get_selected_row_indexes(self.student_tab.table)

        if not selected_rows:
            QMessageBox.warning(self, "Error", "Please select at least one student first.")
            return

        answer = QMessageBox.question(
            self,
            "Delete Student",
            f"Are you sure you want to delete {len(selected_rows)} selected student(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if answer == QMessageBox.Yes:
            for row in selected_rows:
                student_id = self.student_tab.table.item(row, 0).text()
                self.cursor.execute("DELETE FROM student WHERE id = ?", (student_id,))
            self.conn.commit()
            self.student_tab.clear_form()
            self.student_tab.clear_details()
            self.load_students()

 #========================================#

    def connect_program_signals(self):
        self.program_tab.search_btn.clicked.connect(self.search_programs)
        self.program_tab.clear_btn.clicked.connect(self.clear_program_search)
        self.program_tab.refresh_btn.clicked.connect(self.load_programs)
        self.program_tab.add_btn.clicked.connect(self.add_program)
        self.program_tab.update_btn.clicked.connect(self.update_program)
        self.program_tab.delete_btn.clicked.connect(self.delete_program)
        self.program_tab.clear_form_btn.clicked.connect(self.program_tab.clear_form)
        self.program_tab.prev_btn.clicked.connect(self.prev_program_page)
        self.program_tab.next_btn.clicked.connect(self.next_program_page)
        self.program_tab.sort_combo.currentTextChanged.connect(self.program_combo_sort_changed)
        self.program_tab.order_combo.currentTextChanged.connect(self.program_combo_sort_changed)
        self.program_tab.table.horizontalHeader().sectionClicked.connect(self.program_header_clicked)
        self.program_tab.search_input.textChanged.connect(self.search_programs)
        self.program_tab.table.itemSelectionChanged.connect(self.program_row_selected)

    def program_row_selected(self):
        selected_rows = self.get_selected_row_indexes(self.program_tab.table)

        if len(selected_rows) == 1:
            row = selected_rows[0]
            data = {
                "code": self.program_tab.table.item(row, 0).text(),
                "name": self.program_tab.table.item(row, 1).text(),
                "college": self.program_tab.table.item(row, 2).text()
            }
            self.program_tab.set_form_data(data)
            self.program_tab.show_details(data)
        else:
            self.program_tab.clear_details()

    def program_combo_sort_changed(self):
        self.program_sort_column = self.program_tab.sort_combo.currentText()
        self.program_sort_order = self.program_tab.order_combo.currentText()
        self.program_page = 1
        self.load_programs()

    def program_header_clicked(self, index):
        clicked_column = self.program_tab.columns[index]

        if self.program_sort_column == clicked_column:
            self.program_sort_order = self.toggle_sort_order(self.program_sort_order)
        else:
            self.program_sort_column = clicked_column
            self.program_sort_order = "ASC"

        self.program_tab.sort_combo.setCurrentText(self.program_sort_column)
        self.program_tab.order_combo.setCurrentText(self.program_sort_order)
        self.program_page = 1
        self.load_programs()

    def search_programs(self):
        self.program_page = 1
        self.load_programs()

    def clear_program_search(self):
        self.program_tab.search_input.clear()
        self.program_page = 1
        self.load_programs()

    def prev_program_page(self):
        if self.program_page > 1:
            self.program_page -= 1
            self.load_programs()

    def next_program_page(self):
        total = self.count_programs()
        total_pages = self.get_total_pages(total)
        if self.program_page < total_pages:
            self.program_page += 1
            self.load_programs()

    def count_programs(self):
        text = self.program_tab.search_input.text().strip()

        if text:
            self.cursor.execute("""
                SELECT COUNT(*) AS total
                FROM program
                WHERE code LIKE ?
                   OR name LIKE ?
                   OR college LIKE ?
            """, (f"%{text}%", f"%{text}%", f"%{text}%"))
        else:
            self.cursor.execute("SELECT COUNT(*) AS total FROM program")

        return self.cursor.fetchone()["total"]

    def load_programs(self):
        text = self.program_tab.search_input.text().strip()
        sort_col = self.program_sort_column
        sort_order = self.program_sort_order
        offset = (self.program_page - 1) * self.page_size

        if text:
            self.cursor.execute(f"""
                SELECT * FROM program
                WHERE code LIKE ?
                   OR name LIKE ?
                   OR college LIKE ?
                ORDER BY {sort_col} {sort_order}
                LIMIT ? OFFSET ?
            """, (f"%{text}%", f"%{text}%", f"%{text}%", self.page_size, offset))
        else:
            self.cursor.execute(f"""
                SELECT * FROM program
                ORDER BY {sort_col} {sort_order}
                LIMIT ? OFFSET ?
            """, (self.page_size, offset))

        rows = self.cursor.fetchall()
        self.program_tab.table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            values = [row_data["code"], row_data["name"], row_data["college"]]
            for col_index, value in enumerate(values):
                self.program_tab.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        total = self.count_programs()
        total_pages = self.get_total_pages(total)

        if self.program_page > total_pages:
            self.program_page = total_pages

        self.program_tab.page_label.setText(f"Page {self.program_page} of {total_pages}")
        self.program_tab.total_label.setText(f"Total: {total}")

    def add_program(self):
        self.load_reference_combos()
        data = self.program_tab.get_form_data()

        if not all(data.values()):
            QMessageBox.warning(self, "Error", "Please complete all program fields.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO program (code, name, college)
                VALUES (?, ?, ?)
            """, (data["code"], data["name"], data["college"]))
            self.conn.commit()
            self.load_reference_combos()
            self.program_tab.clear_form()
            self.program_tab.clear_details()
            self.load_programs()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Program code already exists.")

    def update_program(self):
        selected_rows = self.get_selected_row_indexes(self.program_tab.table)

        if len(selected_rows) != 1:
            QMessageBox.warning(self, "Error", "Please select only one program to update.")
            return

        old_code = self.program_tab.table.item(selected_rows[0], 0).text()
        data = self.program_tab.get_form_data()

        if not all(data.values()):
            QMessageBox.warning(self, "Error", "Please complete all program fields.")
            return

        try:
            self.cursor.execute("""
                UPDATE program
                SET code = ?, name = ?, college = ?
                WHERE code = ?
            """, (data["code"], data["name"], data["college"], old_code))
            self.conn.commit()
            self.load_reference_combos()
            self.load_programs()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Could not update program.")

    def delete_program(self):
        selected_rows = self.get_selected_row_indexes(self.program_tab.table)

        if not selected_rows:
            QMessageBox.warning(self, "Error", "Please select at least one program first.")
            return

        answer = QMessageBox.question(
            self,
            "Delete Program",
            f"Are you sure you want to delete {len(selected_rows)} selected program(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if answer == QMessageBox.Yes:
            try:
                for row in selected_rows:
                    code = self.program_tab.table.item(row, 0).text()
                    self.cursor.execute("DELETE FROM program WHERE code = ?", (code,))
                self.conn.commit()
                self.load_reference_combos()
                self.program_tab.clear_form()
                self.program_tab.clear_details()
                self.load_programs()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "One or more selected programs are still used by students.")

 #========================================#

    def connect_college_signals(self):
        self.college_tab.search_btn.clicked.connect(self.search_colleges)
        self.college_tab.clear_btn.clicked.connect(self.clear_college_search)
        self.college_tab.refresh_btn.clicked.connect(self.load_colleges)
        self.college_tab.add_btn.clicked.connect(self.add_college)
        self.college_tab.update_btn.clicked.connect(self.update_college)
        self.college_tab.delete_btn.clicked.connect(self.delete_college)
        self.college_tab.clear_form_btn.clicked.connect(self.college_tab.clear_form)
        self.college_tab.prev_btn.clicked.connect(self.prev_college_page)
        self.college_tab.next_btn.clicked.connect(self.next_college_page)
        self.college_tab.sort_combo.currentTextChanged.connect(self.college_combo_sort_changed)
        self.college_tab.order_combo.currentTextChanged.connect(self.college_combo_sort_changed)
        self.college_tab.table.horizontalHeader().sectionClicked.connect(self.college_header_clicked)
        self.college_tab.search_input.textChanged.connect(self.search_colleges)
        self.college_tab.table.itemSelectionChanged.connect(self.college_row_selected)

    def college_row_selected(self):
        selected_rows = self.get_selected_row_indexes(self.college_tab.table)

        if len(selected_rows) == 1:
            row = selected_rows[0]
            data = {
                "code": self.college_tab.table.item(row, 0).text(),
                "name": self.college_tab.table.item(row, 1).text()
            }
            self.college_tab.set_form_data(data)
            self.college_tab.show_details(data)
        else:
            self.college_tab.clear_details()

    def college_combo_sort_changed(self):
        self.college_sort_column = self.college_tab.sort_combo.currentText()
        self.college_sort_order = self.college_tab.order_combo.currentText()
        self.college_page = 1
        self.load_colleges()

    def college_header_clicked(self, index):
        clicked_column = self.college_tab.columns[index]

        if self.college_sort_column == clicked_column:
            self.college_sort_order = self.toggle_sort_order(self.college_sort_order)
        else:
            self.college_sort_column = clicked_column
            self.college_sort_order = "ASC"

        self.college_tab.sort_combo.setCurrentText(self.college_sort_column)
        self.college_tab.order_combo.setCurrentText(self.college_sort_order)
        self.college_page = 1
        self.load_colleges()

    def search_colleges(self):
        self.college_page = 1
        self.load_colleges()

    def clear_college_search(self):
        self.college_tab.search_input.clear()
        self.college_page = 1
        self.load_colleges()

    def prev_college_page(self):
        if self.college_page > 1:
            self.college_page -= 1
            self.load_colleges()

    def next_college_page(self):
        total = self.count_colleges()
        total_pages = self.get_total_pages(total)
        if self.college_page < total_pages:
            self.college_page += 1
            self.load_colleges()

    def count_colleges(self):
        text = self.college_tab.search_input.text().strip()

        if text:
            self.cursor.execute("""
                SELECT COUNT(*) AS total
                FROM college
                WHERE code LIKE ?
                   OR name LIKE ?
            """, (f"%{text}%", f"%{text}%"))
        else:
            self.cursor.execute("SELECT COUNT(*) AS total FROM college")

        return self.cursor.fetchone()["total"]

    def load_colleges(self):
        text = self.college_tab.search_input.text().strip()
        sort_col = self.college_sort_column
        sort_order = self.college_sort_order
        offset = (self.college_page - 1) * self.page_size

        if text:
            self.cursor.execute(f"""
                SELECT * FROM college
                WHERE code LIKE ?
                   OR name LIKE ?
                ORDER BY {sort_col} {sort_order}
                LIMIT ? OFFSET ?
            """, (f"%{text}%", f"%{text}%", self.page_size, offset))
        else:
            self.cursor.execute(f"""
                SELECT * FROM college
                ORDER BY {sort_col} {sort_order}
                LIMIT ? OFFSET ?
            """, (self.page_size, offset))

        rows = self.cursor.fetchall()
        self.college_tab.table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            values = [row_data["code"], row_data["name"]]
            for col_index, value in enumerate(values):
                self.college_tab.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        total = self.count_colleges()
        total_pages = self.get_total_pages(total)

        if self.college_page > total_pages:
            self.college_page = total_pages

        self.college_tab.page_label.setText(f"Page {self.college_page} of {total_pages}")
        self.college_tab.total_label.setText(f"Total: {total}")

    def add_college(self):
        data = self.college_tab.get_form_data()

        if not all(data.values()):
            QMessageBox.warning(self, "Error", "Please complete all college fields.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO college (code, name)
                VALUES (?, ?)
            """, (data["code"], data["name"]))
            self.conn.commit()
            self.load_reference_combos()
            self.college_tab.clear_form()
            self.college_tab.clear_details()
            self.load_colleges()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "College code already exists.")

    def update_college(self):
        selected_rows = self.get_selected_row_indexes(self.college_tab.table)

        if len(selected_rows) != 1:
            QMessageBox.warning(self, "Error", "Please select only one college to update.")
            return

        old_code = self.college_tab.table.item(selected_rows[0], 0).text()
        data = self.college_tab.get_form_data()

        if not all(data.values()):
            QMessageBox.warning(self, "Error", "Please complete all college fields.")
            return

        try:
            self.cursor.execute("""
                UPDATE college
                SET code = ?, name = ?
                WHERE code = ?
            """, (data["code"], data["name"], old_code))
            self.conn.commit()
            self.load_reference_combos()
            self.load_colleges()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Could not update college.")

    def delete_college(self):
        selected_rows = self.get_selected_row_indexes(self.college_tab.table)

        if not selected_rows:
            QMessageBox.warning(self, "Error", "Please select at least one college first.")
            return

        answer = QMessageBox.question(
            self,
            "Delete College",
            f"Are you sure you want to delete {len(selected_rows)} selected college(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if answer == QMessageBox.Yes:
            try:
                for row in selected_rows:
                    code = self.college_tab.table.item(row, 0).text()
                    self.cursor.execute("DELETE FROM college WHERE code = ?", (code,))
                self.conn.commit()
                self.load_reference_combos()
                self.college_tab.clear_form()
                self.college_tab.clear_details()
                self.load_colleges()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "One or more selected colleges are still used by programs.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
