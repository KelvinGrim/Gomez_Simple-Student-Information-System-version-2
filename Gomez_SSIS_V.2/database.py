import sqlite3

DB_NAME = "school.db"


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS college (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS program (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            college TEXT NOT NULL,
            FOREIGN KEY (college) REFERENCES college(code)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            id TEXT PRIMARY KEY,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            course TEXT NOT NULL,
            year INTEGER NOT NULL,
            gender TEXT NOT NULL,
            FOREIGN KEY (course) REFERENCES program(code)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")
