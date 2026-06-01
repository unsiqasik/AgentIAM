"""
Migration script to add MFA fields to the User table.

Run this script to add mfa_enabled and mfa_secret columns to the users table.
"""

from sqlalchemy import text
from app.db.session import SessionLocal


def upgrade():
    """Add MFA fields to User table."""
    db = SessionLocal()
    try:
        # Add mfa_enabled column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS mfa_enabled BOOLEAN DEFAULT FALSE NOT NULL
        """))
        
        # Add mfa_secret column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS mfa_secret VARCHAR NULL
        """))
        
        db.commit()
        print("Successfully added MFA fields to users table")
    except Exception as e:
        db.rollback()
        print(f"Error adding MFA fields: {e}")
        raise
    finally:
        db.close()


def downgrade():
    """Remove MFA fields from User table."""
    db = SessionLocal()
    try:
        db.execute(text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS mfa_enabled,
            DROP COLUMN IF EXISTS mfa_secret
        """))
        
        db.commit()
        print("Successfully removed MFA fields from users table")
    except Exception as e:
        db.rollback()
        print(f"Error removing MFA fields: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
