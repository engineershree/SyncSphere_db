"""
One-shot migration: creates the blacklisted_tokens table if it doesn't exist.
Run once: python create_blacklist_table.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base

# Must import the model so it registers on Base.metadata
from app.models.blacklisted_token import BlacklistedToken  # noqa

def run():
    print("Creating blacklisted_tokens table...")
    try:
        # Use CREATE TABLE IF NOT EXISTS via SQLAlchemy metadata
        Base.metadata.create_all(bind=engine, tables=[BlacklistedToken.__table__])
        print("✅  blacklisted_tokens table created successfully.")
    except Exception as e:
        # Fallback: raw SQL
        print(f"SQLAlchemy create_all failed ({e}), trying raw SQL...")
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS blacklisted_tokens (
                    id SERIAL PRIMARY KEY,
                    token VARCHAR(512) NOT NULL UNIQUE,
                    blacklisted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMPTZ NOT NULL
                );
                CREATE INDEX IF NOT EXISTS ix_blacklisted_tokens_token
                    ON blacklisted_tokens (token);
            """))
            conn.commit()
        print("✅  blacklisted_tokens table created via raw SQL.")

if __name__ == "__main__":
    run()
