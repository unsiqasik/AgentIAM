"""
Migration script to add expires_at field to Policy table.

Run this script to add expires_at column to the policies table.
"""

from sqlalchemy import text
from app.db.session import SessionLocal


def upgrade():
    """Add expires_at field to Policy table."""
    db = SessionLocal()
    try:
        # Add expires_at column
        db.execute(text("""
            ALTER TABLE policies 
            ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE NULL
        """))

        db.commit()
        print("Successfully added expires_at field to policies table")
    except Exception as e:
        db.rollback()
        print(f"Error adding expires_at field: {e}")
        raise
    finally:
        db.close()


def downgrade():
    """Remove expires_at field from Policy table."""
    db = SessionLocal()
    try:
        # Remove expires_at column
        db.execute(text("""
            ALTER TABLE policies 
            DROP COLUMN IF EXISTS expires_at
        """))

        db.commit()
        print("Successfully removed expires_at field from policies table")
    except Exception as e:
        db.rollback()
        print(f"Error removing expires_at field: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
