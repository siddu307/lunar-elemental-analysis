
import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "cleaned_al_si_pixels.csv"
DATABASE_PATH = BASE_DIR / "lunar_analysis.db"
EXPECTED_ROWS = 2_064_603
BATCH_SIZE = 10_000


def import_pixels():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        connection.execute("PRAGMA busy_timeout = 30000")

        columns = [
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(observations)"
            ).fetchall()
        ]

        required_columns = {
            "id", "pixel_x", "pixel_y", "band_1", "band_2"
        }

        if not required_columns.issubset(columns):
            raise RuntimeError(
                "The observations table does not have the expected schema."
            )

        existing_count = connection.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0]

        if existing_count != 0:
            raise RuntimeError(
                f"Import stopped: observations already contains "
                f"{existing_count} records. No rows were imported."
            )

        connection.execute("BEGIN")

        insert_sql = """
            INSERT INTO observations
                (pixel_x, pixel_y, band_1, band_2)
            VALUES (?, ?, ?, ?)
        """

        count = 0
        batch = []

        with CSV_PATH.open(
            "r", newline="", encoding="utf-8-sig"
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            expected_columns = {
                "Pixel_Row", "Pixel_Column", "Band_1", "Band_2"
            }

            if not expected_columns.issubset(reader.fieldnames or []):
                raise RuntimeError(
                    f"Unexpected CSV columns: {reader.fieldnames}"
                )

            for row in reader:
                batch.append((
                    int(row["Pixel_Column"]),
                    int(row["Pixel_Row"]),
                    float(row["Band_1"]),
                    float(row["Band_2"])
                ))

                count += 1

                if len(batch) >= BATCH_SIZE:
                    connection.executemany(insert_sql, batch)
                    batch.clear()

            if batch:
                connection.executemany(insert_sql, batch)

        if count != EXPECTED_ROWS:
            raise RuntimeError(
                f"Expected {EXPECTED_ROWS} rows but read {count}."
            )

        connection.commit()

        imported_count = connection.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0]

        print("CSV rows read:", count)
        print("Database rows after import:", imported_count)
        print("Import status:", "SUCCESS" if imported_count == count else "CHECK REQUIRED")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    import_pixels()
