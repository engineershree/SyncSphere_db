import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from app.main import app
import uuid

def run():
    client = TestClient(app)
    email = f"test_{uuid.uuid4()}@example.com"
    
    print("Testing registration...")
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": "password123",
            "role": "EMPLOYEE",
            "phone": str(uuid.uuid4().int)[:10]
        }
    )
    print("STATUS:", resp.status_code)
    print("RESPONSE:", resp.json())
    
    print("\nTesting login...")
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "password123"}
    )
    print("LOGIN STATUS:", login_resp.status_code)

if __name__ == "__main__":
    run()
