"""
Migration script to add integrity fields to the AuditLog table.

Run this script to add previous_hash and entry_hash columns to the audit_logs table.
"""

from sqlalchemy import text
from app.db.session import SessionLocal


def upgrade():
    """Add integrity fields to AuditLog table."""
    db = SessionLocal()
    try:
        # Add previous_hash column
        db.execute(text("""
            ALTER TABLE audit_logs 
            ADD COLUMN IF NOT EXISTS previous_hash VARCHAR(64) NULL
        """))
        
        # Add entry_hash column
        db.execute(text("""
            ALTER TABLE audit_logs 
            ADD COLUMN IF NOT EXISTS entry_hash VARCHAR(64) NOT NULL DEFAULT ''
        """))
        
        db.commit()
        print("Successfully added integrity fields to audit_logs table")
    except Exception as e:
        db.rollback()
        print(f"Error adding integrity fields: {e}")
        raise
    finally:
        db.close()


def downgrade():
    """Remove integrity fields from AuditLog table."""
    db = SessionLocal()
    try:
        db.execute(text("""
            ALTER TABLE audit_logs 
            DROP COLUMN IF EXISTS previous_hash,
            DROP COLUMN IF EXISTS entry_hash
        """))
        
        db.commit()
        print("Successfully removed integrity fields from audit_logs table")
    except Exception as e:
        db.rollback()
        print(f"Error removing integrity fields: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
