
import sqlite3
from pathlib import Path


# Database file location
MEMORY_DIR = Path(__file__).resolve().parent
DATABASE_PATH = MEMORY_DIR / "veriagent.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """
    Create the required database tables if they do not exist.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # Table 1: Store submitted claims and their final decisions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claim_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim TEXT NOT NULL,
            verdict TEXT NOT NULL,
            confidence TEXT,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table 2: Store research publications and their evaluations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            publication_id TEXT,
            title TEXT,
            year INTEGER,
            doi TEXT,
            classification TEXT,
            relevance TEXT,
            study_type TEXT,
            findings_status TEXT,
            evidence_strength TEXT,
            explanation TEXT,

            FOREIGN KEY (claim_id)
                REFERENCES claim_history(id)
                ON DELETE CASCADE
        )
    """)

    # Table 3: Store user feedback about verification decisions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            user_feedback TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (claim_id)
                REFERENCES claim_history(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()

    return DATABASE_PATH


if __name__ == "__main__":
    database = initialize_database()

    print("VERIAGENT DATABASE")
    print("=" * 40)
    print("Database initialized successfully!")
    print("Database location:", database)
