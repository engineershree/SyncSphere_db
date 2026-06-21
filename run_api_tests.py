import urllib.request
import urllib.parse
import json
import uuid
import sys
import os
import random

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
                parsed_body = json.loads(body)
                print(json.dumps(parsed_body, indent=2))
                return parsed_body
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

def main():
    print("Verifying/Creating Admin User first...")
    try:
        from create_admin import create_default_admin
        admin = create_default_admin()
        if admin:
            print("Admin user is ready.")
    except Exception as e:
        print(f"Failed to import/run create_default_admin: {e}")

    # 1. Login as Admin
    print("\n--- 1. Login as Admin ---")
    admin_login_data = {
        "email": "admin@syncsphere.com",
        "password": "admin123"
    }
    admin_login_resp = make_request("POST", "/auth/login", data=admin_login_data)
    if not admin_login_resp:
        print("Failed to login as Admin. Exiting.")
        sys.exit(1)
    admin_token = admin_login_resp.get("access_token")

    # 2. Get All Users (Admin API)
    print("\n--- 2. Get All Users (Admin Only) ---")
    all_users_resp = make_request("GET", "/users/", token=admin_token)

    # 3. Register a New User (Employee)
    print("\n--- 3. Register a New User ---")
    unique_id = str(uuid.uuid4())[:8]
    email = f"emp_{unique_id}@example.com"
    password = "securepassword123"
    
    phone_num = random.randint(1000000000, 9999999999)
    register_data = {
        "first_name": "Employee",
        "last_name": f"User_{unique_id}",
        "email": email,
        "phone": phone_num,
        "password": password,
        "role": "EMPLOYEE"
    }
    emp_reg_resp = make_request("POST", "/auth/register", data=register_data)
    if not emp_reg_resp:
        print("Failed to register employee user.")
        sys.exit(1)

    # 4. Login as the New User
    print("\n--- 4. Login as the New User ---")
    emp_login_data = {
        "email": email,
        "password": password
    }
    emp_login_resp = make_request("POST", "/auth/login", data=emp_login_data)
    if not emp_login_resp:
        print("Failed to login as Employee.")
        sys.exit(1)
    emp_token = emp_login_resp.get("access_token")
    emp_refresh_token = emp_login_resp.get("refresh_token")
    emp_id = emp_login_resp.get("user", {}).get("id")

    # 5. Get Current User Info (/auth/me)
    print("\n--- 5. Get Current User Info (/auth/me) ---")
    make_request("GET", "/auth/me", token=emp_token)

    # 6. Refresh Token
    print("\n--- 6. Refresh Token ---")
    refresh_resp = make_request("POST", "/auth/refresh", token=emp_refresh_token)
    if refresh_resp and "access_token" in refresh_resp:
        emp_token = refresh_resp["access_token"]

    # 7. Get User by ID (Self)
    print("\n--- 7. Get User by ID (Self) ---")
    make_request("GET", f"/users/{emp_id}", token=emp_token)

    # 8. Update User (Self)
    print("\n--- 8. Update User ---")
    phone_num_upd = random.randint(1000000000, 9999999999)
    update_data = {
        "first_name": "UpdatedEmpName",
        "phone": phone_num_upd,
        "timezone": "America/New_York"
    }
    make_request("PUT", f"/users/{emp_id}", data=update_data, token=emp_token)

    # 9. Logout
    print("\n--- 9. Logout ---")
    make_request("POST", "/auth/logout", token=emp_token)

    # 9.5. Test OTP Forgot Password Flow
    print("\n--- 9.5. Testing OTP Forgot Password Flow ---")
    forgot_resp = make_request("POST", "/auth/forgot-password", data={"email": email})
    if not forgot_resp or "otp" not in forgot_resp:
        print("Failed to request OTP.")
        sys.exit(1)
    otp = forgot_resp["otp"]

    print("\n--- Testing OTP Verification ---")
    make_request("POST", "/auth/verify-otp", data={"email": email, "otp": otp})

    print("\n--- Testing Password Reset (Weak Password - Should Fail) ---")
    # This should fail due to strict password requirements
    make_request("POST", "/auth/reset-password", data={"email": email, "otp": otp, "new_password": "weak"})

    print("\n--- Testing Password Reset (Strong Password - Should Succeed) ---")
    # This should succeed
    new_secure_pw = "NewSecureP@ss123"
    make_request("POST", "/auth/reset-password", data={"email": email, "otp": otp, "new_password": new_secure_pw})

    print("\n--- Testing Login with New Password ---")
    # Verify login works with new password
    make_request("POST", "/auth/login", data={"email": email, "password": new_secure_pw})

    # 10. Delete User (Admin Only)
    print("\n--- 10. Delete User (Admin Only) ---")
    print(f"Skipping deletion of user {emp_id} so it remains visible in the database.")
    # make_request("DELETE", f"/users/{emp_id}", token=admin_token)

if __name__ == "__main__":
    main()
