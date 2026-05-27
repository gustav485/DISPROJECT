import csv
import os

from dotenv import load_dotenv

from db import get_connection

load_dotenv()

BASE_DIR = os.path.dirname(__file__)


def run_sql_file(cur, filename):
    with open(os.path.join(BASE_DIR, "utils", filename), encoding="utf-8") as db_file:
        cur.execute(db_file.read())


def import_shirts(cur):
    csv_path = os.path.join(BASE_DIR, "shirts.csv")
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        shirts = []
        for row in reader:
            pid = int(row["pid"])
            shirts.append((
                pid,
                row["name"].strip(),
                float(row["price"]),
                row["team"].strip(),
                row["season"].strip(),
                row["condition"].strip(),
                row["size"].strip(),
                f"/pictures/pid{pid}.png",
                True,
            ))

    args_str = ",".join(
        cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s)", shirt).decode("utf-8")
        for shirt in shirts
    )
    cur.execute(
        """
        INSERT INTO Products(original_pid, name, price, team, season, condition, size, image, available)
        VALUES
        """ + args_str
    )
    return len(shirts)


if __name__ == "__main__":
    conn = get_connection()
    with conn.cursor() as cur:
        run_sql_file(cur, "users.sql")
        run_sql_file(cur, "products.sql")
        count = import_shirts(cur)
        conn.commit()
    conn.close()
    print(f"Database initialized successfully. Imported {count} shirts from shirts.csv")
