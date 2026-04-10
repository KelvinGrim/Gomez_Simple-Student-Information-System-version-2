import random
from database import connect_db, create_tables

FIRST_NAMES = [
    "John", "Maria", "Kelwin", "Chris", "Anne", "Mark", "Paolo", "Jessa", "Carl", "Rhea",
    "James", "Angela", "Nathan", "Kyle", "Joshua", "Bianca", "Diane", "Patrick", "Mika", "Aira",
    "Cedric", "Shane", "Lara", "Dan", "Marlon", "Bea", "Trisha", "Kevin", "Sean", "Faith"
]

LAST_NAMES = [
    "Gomez", "Dela Cruz", "Santos", "Reyes", "Torres", "Mendoza", "Aquino", "Garcia", "Flores",
    "Ramos", "Villanueva", "Castro", "Lopez", "Navarro", "Pineda", "Salazar", "Bautista",
    "Domingo", "Valdez", "Morales", "Fernandez", "Rivera", "Tan", "Uy", "Lim", "Asuncion"
]

GENDERS = ["Male", "Female"]

COLLEGES = [
    ("CCS", "College of Computer Studies"),
    ("COE", "College of Engineering"),
    ("CBA", "College of Business Administration"),
    ("CAS", "College of Arts and Sciences"),
    ("CED", "College of Education"),
    ("CON", "College of Nursing")
]

PROGRAMS = [
    ("BSCS", "Bachelor of Science in Computer Science", "CCS"),
    ("BSIT", "Bachelor of Science in Information Technology", "CCS"),
    ("BSIS", "Bachelor of Science in Information Systems", "CCS"),
    ("BSEMC", "Bachelor of Science in Entertainment and Multimedia Computing", "CCS"),
    ("BSSE", "Bachelor of Science in Software Engineering", "CCS"),

    ("BSCE", "Bachelor of Science in Civil Engineering", "COE"),
    ("BSEE", "Bachelor of Science in Electrical Engineering", "COE"),
    ("BSME", "Bachelor of Science in Mechanical Engineering", "COE"),
    ("BSCHE", "Bachelor of Science in Chemical Engineering", "COE"),
    ("BSECE", "Bachelor of Science in Electronics Engineering", "COE"),

    ("BSA", "Bachelor of Science in Accountancy", "CBA"),
    ("BSBA-MM", "Bachelor of Science in Business Administration major in Marketing Management", "CBA"),
    ("BSBA-FM", "Bachelor of Science in Business Administration major in Financial Management", "CBA"),
    ("BSENT", "Bachelor of Science in Entrepreneurship", "CBA"),
    ("BSHM", "Bachelor of Science in Hospitality Management", "CBA"),

    ("ABENG", "Bachelor of Arts in English", "CAS"),
    ("ABPOL", "Bachelor of Arts in Political Science", "CAS"),
    ("BSMATH", "Bachelor of Science in Mathematics", "CAS"),
    ("BSPHY", "Bachelor of Science in Physics", "CAS"),
    ("BSCHEM", "Bachelor of Science in Chemistry", "CAS"),

    ("BEED", "Bachelor of Elementary Education", "CED"),
    ("BSED-ENG", "Bachelor of Secondary Education major in English", "CED"),
    ("BSED-MATH", "Bachelor of Secondary Education major in Mathematics", "CED"),
    ("BSED-SCI", "Bachelor of Secondary Education major in Science", "CED"),
    ("BTLED", "Bachelor of Technology and Livelihood Education", "CED"),

    ("BSN", "Bachelor of Science in Nursing", "CON"),
    ("BSPH", "Bachelor of Science in Public Health", "CON"),
    ("BSPHAR", "Bachelor of Science in Pharmacy", "CON"),
    ("BSBIO", "Bachelor of Science in Biology", "CAS"),
    ("BSSTAT", "Bachelor of Science in Statistics", "CAS")
]


def insert_colleges():
    conn = connect_db()
    cursor = conn.cursor()

    for code, name in COLLEGES:
        cursor.execute(
            "INSERT OR IGNORE INTO college (code, name) VALUES (?, ?)",
            (code, name)
        )

    conn.commit()
    conn.close()


def insert_programs():
    conn = connect_db()
    cursor = conn.cursor()

    for code, name, college in PROGRAMS:
        cursor.execute(
            "INSERT OR IGNORE INTO program (code, name, college) VALUES (?, ?, ?)",
            (code, name, college)
        )

    conn.commit()
    conn.close()


def generate_student_id(existing_ids):
    while True:
        year = random.randint(2021, 2026)
        number = random.randint(1, 9999)
        student_id = f"{year}-{number:04d}"

        if student_id not in existing_ids:
            existing_ids.add(student_id)
            return student_id


def insert_students(total_students=5000):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM student")
    current_count = cursor.fetchone()["total"]

    if current_count >= total_students:
        print("Students already populated.")
        conn.close()
        return

    cursor.execute("SELECT code FROM program ORDER BY code")
    program_codes = [row["code"] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM student")
    existing_ids = set(row["id"] for row in cursor.fetchall())

    students_to_add = total_students - current_count

    for _ in range(students_to_add):
        student_id = generate_student_id(existing_ids)
        firstname = random.choice(FIRST_NAMES)
        lastname = random.choice(LAST_NAMES)
        course = random.choice(program_codes)
        year_level = random.randint(1, 4)
        gender = random.choice(GENDERS)

        cursor.execute("""
            INSERT INTO student (id, firstname, lastname, course, year, gender)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, firstname, lastname, course, year_level, gender))

    conn.commit()
    conn.close()
    print(f"{students_to_add} students inserted successfully.")


if __name__ == "__main__":
    create_tables()
    insert_colleges()
    insert_programs()
    insert_students(5000)
    print("Database seeding completed.")
