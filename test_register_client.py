from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.post(
    "/api/v1/auth/register",
    json={
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "password123",
        "role": "EMPLOYEE",
        "phone": "1234567890"
    }
)

print("STATUS:", response.status_code)
print("BODY:", response.json())
