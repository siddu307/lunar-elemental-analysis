
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "lunar_analysis.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def get_ml_connection():
    ml_database_path = BASE_DIR / "lunar_ml_integration.db"
    connection = sqlite3.connect(ml_database_path)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY,
            pixel_x INTEGER,
            pixel_y INTEGER,
            band_1 REAL,
            band_2 REAL,
            band_3 REAL,
            band_4 REAL,
            latitude REAL,
            longitude REAL,
            metadata TEXT
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database created at: {DATABASE_PATH}")
