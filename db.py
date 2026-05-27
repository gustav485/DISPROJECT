import os
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()


def get_db_config():
    """Database config inspired by GreenGroceries, but with safer defaults for Mac/Homebrew and Docker."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "football_shop"),
        "user": os.getenv("DB_USERNAME") or os.getenv("DB_USER") or os.getenv("USER"),
        "password": os.getenv("DB_PASSWORD", ""),
        "port": os.getenv("DB_PORT", "5432"),
    }


def get_connection():
    return psycopg2.connect(**get_db_config())


@contextmanager
def get_cursor(commit=False):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
            if commit:
                conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
