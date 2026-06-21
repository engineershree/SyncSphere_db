import os
import sys

sys.path.append(os.path.dirname(__file__))

from app.db.session import SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash
import uuid

def test_db_insert():
    db = SessionLocal()
    try:
        unique_id = str(uuid.uuid4())[:8]
        email = f"test_{unique_id}@example.com"
        
        user = User(
            first_name="Test",
            last_name="User",
            email=email,
            phone=f"1000{unique_id}",
            password_hash=get_password_hash("password123"),
            role=UserRole.EMPLOYEE,
            status=UserStatus.ACTIVE
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"User created with ID {user.id} and email {user.email}")
        
        # Check if it actually exists in a new session
        db2 = SessionLocal()
        found = db2.query(User).filter(User.email == email).first()
        if found:
            print(f"User {found.email} found in the database!")
        else:
            print("User NOT found in the database! Commit failed silently?")
        db2.close()
        
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    test_db_insert()
