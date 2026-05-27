from db import get_connection, get_db_config

try:
    conn = get_connection()
    conn.close()
    print("Database connection OK")
    print(get_db_config())
except Exception as exc:
    print("Database connection failed")
    print(get_db_config())
    print(exc)
