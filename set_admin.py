"""
Script to set a user as admin
Usage: python set_admin.py your@email.com
"""
import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reports.db")
engine = create_engine(DATABASE_URL)

def set_admin(email):
    with engine.begin() as conn:
        try:
            # Update user role to admin
            result = conn.execute(
                text("UPDATE approved_users SET role = 'admin', is_active = true WHERE email = :email"),
                {"email": email}
            )
            
            if result.rowcount > 0:
                print(f"Successfully set {email} as admin!")
                print("The user can now access the Admin Panel.")
            else:
                print(f"User {email} not found in database.")
                print("Please register first, then run this script.")
            
        except Exception as e:
            print(f"Failed to set admin: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_admin.py your@email.com")
        sys.exit(1)
    
    email = sys.argv[1]
    set_admin(email)
