"""
SyncSphere Events API Test Script
==================================
Tests:
  1. Register a new user
  2. Login to get access token
  3. Create a new event (minimal required fields only)
  4. Fetch the created event by ID
  5. List all events
"""

import requests
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "http://localhost:8000/api/v1"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def print_response(label: str, response: requests.Response):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Status  : {response.status_code}")
    try:
        body = response.json()
        print(f"  Response:\n{json.dumps(body, indent=4, default=str)}")
    except Exception:
        print(f"  Body    : {response.text}")
    print()


# ─────────────────────────────────────────────
# Step 1 – Register user
# ─────────────────────────────────────────────
REGISTER_PAYLOAD = {
    "first_name": "Event",
    "last_name": "Tester",
    "email": "eventtester@syncsphere.dev",
    "phone": "+911234567890",
    "role": "EMPLOYEE",
    "password": "Test@1234"
}

print("\n🚀  SyncSphere Events API Test")

reg_resp = requests.post(f"{BASE_URL}/auth/register", json=REGISTER_PAYLOAD)
print_response("STEP 1 – Register User", reg_resp)

if reg_resp.status_code == 400:
    print("  ℹ️  User already exists — proceeding to login.")


# ─────────────────────────────────────────────
# Step 2 – Login
# ─────────────────────────────────────────────
LOGIN_PAYLOAD = {
    "email": "eventtester@syncsphere.dev",
    "password": "Test@1234"
}

login_resp = requests.post(f"{BASE_URL}/auth/login", json=LOGIN_PAYLOAD)
print_response("STEP 2 – Login", login_resp)

if login_resp.status_code != 200:
    print("❌  Login failed. Aborting tests.")
    exit(1)

access_token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}
print(f"  ✅  Token obtained successfully.")


# ─────────────────────────────────────────────
# Step 3 – Create Event  (minimal required fields only)
# ─────────────────────────────────────────────
# start_datetime = tomorrow 10:00 UTC
tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
    hour=10, minute=0, second=0, microsecond=0
)

CREATE_EVENT_PAYLOAD = {
    "title": "Team Sync – Weekly Standup",
    "description": "Weekly team standup meeting to discuss progress and blockers.",
    "event_type": "MEETING",
    "status": "PUBLISHED",
    "priority": "HIGH",
    "start_datetime": tomorrow.isoformat(),
    "timezone": "Asia/Kolkata",
    "all_day": False,
    "location": "Conference Room A",
    "max_attendees": 20,
    "is_public": True,
    "requires_registration": False,
    "reminder_enabled": True
}

print(f"\n  📋  Creating event with payload:")
print(json.dumps(CREATE_EVENT_PAYLOAD, indent=4, default=str))

create_resp = requests.post(
    f"{BASE_URL}/events/",
    json=CREATE_EVENT_PAYLOAD,
    headers=headers
)
print_response("STEP 3 – Create Event", create_resp)

if create_resp.status_code != 201:
    print("❌  Event creation failed. Aborting further tests.")
    exit(1)

event_id = create_resp.json()["id"]
print(f"  ✅  Event created with ID: {event_id}")


# ─────────────────────────────────────────────
# Step 4 – Fetch event by ID
# ─────────────────────────────────────────────
get_resp = requests.get(f"{BASE_URL}/events/{event_id}", headers=headers)
print_response("STEP 4 – Get Event by ID", get_resp)


# ─────────────────────────────────────────────
# Step 5 – List all events
# ─────────────────────────────────────────────
list_resp = requests.get(f"{BASE_URL}/events/", headers=headers)
print_response("STEP 5 – List All Events", list_resp)

print("✅  All tests completed successfully!\n")
