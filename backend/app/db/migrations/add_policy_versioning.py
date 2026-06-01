"""
Migration script to add policy versioning.

Run this script to:
1. Add current_version column to policies table
2. Create policy_versions table
"""

from sqlalchemy import text
from app.db.session import SessionLocal


def upgrade():
    """Add policy versioning support."""
    db = SessionLocal()
    try:
        # Add current_version column to policies table
        db.execute(text("""
            ALTER TABLE policies 
            ADD COLUMN IF NOT EXISTS current_version INTEGER DEFAULT 1 NOT NULL
        """))
        
        # Create policy_versions table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS policy_versions (
                id SERIAL PRIMARY KEY,
                policy_id INTEGER NOT NULL REFERENCES policies(id),
                version INTEGER NOT NULL,
                policy_yaml TEXT NOT NULL,
                change_reason TEXT,
                changed_by VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(policy_id, version)
            )
        """))
        
        db.commit()
        print("Successfully added policy versioning support")
    except Exception as e:
        db.rollback()
        print(f"Error adding policy versioning: {e}")
        raise
    finally:
        db.close()


def downgrade():
    """Remove policy versioning support."""
    db = SessionLocal()
    try:
        # Drop policy_versions table
        db.execute(text("DROP TABLE IF EXISTS policy_versions"))
        
        # Remove current_version column from policies table
        db.execute(text("""
            ALTER TABLE policies 
            DROP COLUMN IF EXISTS current_version
        """))
        
        db.commit()
        print("Successfully removed policy versioning support")
    except Exception as e:
        db.rollback()
        print(f"Error removing policy versioning: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
