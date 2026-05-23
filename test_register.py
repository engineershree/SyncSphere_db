import urllib.request
import urllib.error
import json

data = json.dumps({
    'first_name': 'Test2', 
    'last_name': 'User2', 
    'email': 'test2@example.com', 
    'password': 'password123', 
    'role': 'EMPLOYEE',
    'phone': '1234567890'
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/auth/register', 
    data=data, 
    headers={'Content-Type': 'application/json'}
)

try:
    response = urllib.request.urlopen(req)
    print("STATUS:", response.status)
    print("BODY:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("ERROR STATUS:", e.code)
    print("ERROR BODY:", e.read().decode('utf-8'))
except Exception as e:
    print("EXCEPTION:", str(e))
