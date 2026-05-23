#!/usr/bin/env python3
"""
Script to create default admin credentials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash

def create_default_admin():
    """
    Create default admin user with credentials
    """
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@syncsphere.com").first()
        
        if existing_admin:
            print("Admin user already exists!")
            print(f"Email: admin@syncsphere.com")
            print("Password: admin123")
            return existing_admin
        
        # Create admin user
        admin_user = User(
            first_name="System",
            last_name="Administrator",
            email="admin@syncsphere.com",
            phone="+1234567890",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            is_phone_verified=True,
            department="IT",
            job_title="System Administrator"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Default admin user created successfully!")
        print("📧 Email: admin@syncsphere.com")
        print("🔑 Password: admin123")
        print(f"👤 User ID: {admin_user.id}")
        print(f"🔐 Role: {admin_user.role}")
        print(f"📊 Status: {admin_user.status}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def test_admin_login():
    """
    Test admin login using the API
    """
    import requests
    import json
    
    # Test login endpoint
    login_data = {
        "email": "admin@syncsphere.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin login successful!")
            print(f"🔑 Access Token: {result.get('access_token', 'N/A')[:50]}...")
            if 'refresh_token' in result:
                print(f"🔄 Refresh Token: {result['refresh_token'][:50]}...")
            print(f"🎫 Token Type: {result.get('token_type', 'N/A')}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot test login - server is not running on localhost:8000")
        print("Please start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error testing login: {e}")

if __name__ == "__main__":
    print("🚀 Creating default admin credentials...")
    admin = create_default_admin()
    
    if admin:
        print("\n🧪 Testing admin login...")
        test_admin_login()
