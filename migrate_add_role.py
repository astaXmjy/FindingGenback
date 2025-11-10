"""
Migration script to add role column to approved_users table
Run this once to update existing database
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reports.db")
engine = create_engine(DATABASE_URL)

def migrate():
    with engine.begin() as conn:
        try:
            # Try to add role column (will fail if exists, which is fine)
            try:
                print("Adding 'role' column to approved_users table...")
                conn.execute(text("ALTER TABLE approved_users ADD COLUMN role VARCHAR(50) DEFAULT 'user' NOT NULL"))
                print("Successfully added 'role' column")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("'role' column already exists")
                else:
                    raise
            
            # Update any NULL roles to 'user'
            conn.execute(text("UPDATE approved_users SET role = 'user' WHERE role IS NULL OR role = ''"))
            print("Updated NULL/empty roles to 'user'")
            
            print("\nMigration complete!")
            print("\nTo create an admin user, run:")
            print("UPDATE approved_users SET role = 'admin' WHERE email = 'your@email.com';")
            
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
