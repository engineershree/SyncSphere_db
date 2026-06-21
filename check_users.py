import os
import sys

sys.path.append(os.path.dirname(__file__))

from app.db.session import SessionLocal
from app.models.user import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total users in DB: {len(users)}")
        for u in users:
            print(f"User: {u.email}, is_deleted: {u.is_deleted}")
    finally:
        db.close()

if __name__ == '__main__':
    check_users()
