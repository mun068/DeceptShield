"""Database readiness without logging secrets or database connection strings."""

import psycopg


def database_is_ready() -> bool:
    """Return whether a short, read-only PostgreSQL health query succeeds."""
    try:
        # Uses PGHOST, PGPORT, PGDATABASE, PGUSER and PGPASSWORD supplied by runtime.
        with psycopg.connect(connect_timeout=2) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() == (1,)
    except (psycopg.Error, OSError):
        return False
