import urllib.request
import urllib.parse
import json
import uuid

BASE_URL = "http://127.0.0.1:5000/api/v1"

def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    print(f"\n--- {method} {endpoint} ---")
    
    headers = {}
    if data is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(data).encode('utf-8')
    if token:
        headers['Authorization'] = f"Bearer {token}"
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            print(f"Status: {status}")
            try:
                print(json.dumps(json.loads(body), indent=2))
                return json.loads(body)
            except:
                print(body)
                return body
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8')
        print(f"Status: {status} (HTTPError)")
        try:
            print(json.dumps(json.loads(body), indent=2))
        except:
            print(body)
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_all():
    print("Starting API Tests...\n")
    
    # 1. Register
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    password = "securepassword123"
    
    register_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "phone": f"+1000{unique_id}",
        "password": password,
        "role": "EMPLOYEE"
    }
    
    print("1. Testing Register API...")
    reg_response = make_request("POST", "/auth/register", data=register_data)
    
    if not reg_response:
        print("Registration failed. Cannot proceed with all tests.")
        return
        
    # 2. Login
    print("\n2. Testing Login API...")
    login_data = {
        "email": email,
        "password": password
    }
    login_response = make_request("POST", "/auth/login", data=login_data)
    
    if not login_response:
        print("Login failed.")
        return
        
    access_token = login_response.get("access_token")
    refresh_token = login_response.get("refresh_token")
    user_id = login_response.get("user", {}).get("id")
    
    # 3. Get Current User Info
    print("\n3. Testing Get Current User API...")
    make_request("GET", "/auth/me", token=access_token)
    
    # 4. Refresh Token
    print("\n4. Testing Refresh Token API...")
    refresh_response = make_request("POST", "/auth/refresh", token=refresh_token)
    if refresh_response and "access_token" in refresh_response:
        access_token = refresh_response["access_token"]
        print("Successfully refreshed token.")
        
    # 5. Update User (Using self)
    print("\n5. Testing Update User API...")
    update_data = {
        "first_name": "UpdatedName",
        "timezone": "America/New_York"
    }
    make_request("PUT", f"/users/{user_id}", data=update_data, token=access_token)
    
    # 6. Get User by ID (Self)
    print("\n6. Testing Get User by ID API...")
    make_request("GET", f"/users/{user_id}", token=access_token)
    
    # 7. Get All Users (Requires Admin)
    # Since we are an EMPLOYEE, this should return 403 Forbidden
    print("\n7. Testing Get All Users API (Should be 403 Forbidden for Employee)...")
    make_request("GET", "/users/", token=access_token)
    
    # 8. Logout
    print("\n8. Testing Logout API...")
    make_request("POST", "/auth/logout", token=access_token)
    
    # 9. Test Token Blacklisting (Should fail after logout)
    print("\n9. Testing blacklisted token (Should be Unauthorized)...")
    make_request("GET", "/auth/me", token=access_token)

if __name__ == "__main__":
    test_all()
