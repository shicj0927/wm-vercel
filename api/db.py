import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL') or (
    f"postgresql://{os.getenv('DB_USER','')}:" \
    f"{os.getenv('DB_PASSWORD','')}@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}/{os.getenv('DB_NAME','')}")

# Create engine with reasonable defaults for serverless environments
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True
)


def fetchone(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        row = result.first()
        return dict(row) if row else None


def fetchall(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        rows = result.fetchall()
        return [dict(r) for r in rows]


def execute(query, params=None):
    # For UPDATE/DELETE statements
    with engine.begin() as conn:
        result = conn.execute(text(query), params or {})
        return result.rowcount


def insert_returning_id(query, params=None):
    # Expects query to include RETURNING id
    with engine.begin() as conn:
        result = conn.execute(text(query), params or {})
        # scalar() returns the first column of the first row
        try:
            return result.scalar()
        except Exception:
            return None
