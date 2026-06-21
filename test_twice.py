import urllib.request
import urllib.error
import json
import uuid

def register():
    data = json.dumps({
        'first_name': 'Test2', 
        'last_name': 'User2', 
        'email': f'test_{uuid.uuid4()}@example.com', 
        'password': 'password123', 
        'role': 'EMPLOYEE',
        'phone': str(uuid.uuid4().int)[:10]
    }).encode('utf-8')

    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/register', 
        data=data, 
        headers={'Content-Type': 'application/json'}
    )
    try:
        response = urllib.request.urlopen(req)
        print("STATUS:", response.status)
        return True
    except urllib.error.HTTPError as e:
        print("ERROR STATUS:", e.code)
        return False
    except Exception as e:
        print("EXCEPTION:", str(e))
        return False

# We can't run this directly because server is not running in background.
# But I can write a script that instantiates the TestClient and does it twice!
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_test_client():
    email = f"test_{uuid.uuid4()}@example.com"
    phone = str(uuid.uuid4().int)[:10]
    
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": "password123",
        "role": "EMPLOYEE",
        "phone": phone
    }
    
    print("First registration:")
    resp1 = client.post("/api/v1/auth/register", json=payload)
    print("STATUS 1:", resp1.status_code)
    
    print("Second registration (should fail):")
    resp2 = client.post("/api/v1/auth/register", json=payload)
    print("STATUS 2:", resp2.status_code)

if __name__ == "__main__":
    run_test_client()
