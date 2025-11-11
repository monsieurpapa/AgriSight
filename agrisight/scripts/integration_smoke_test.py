#!/usr/bin/env python3
"""
Integration smoke test for AgriSight authentication and health endpoints.

This script performs a small flow against a running local stack (backend + frontend):
  - GET /api/auth/csrf/ to obtain CSRF token
  - POST /api/auth/registration/ to create a new test user (unique email)
  - POST /api/auth/login/ to authenticate the user (session cookie)
  - GET /api/auth/user/ to confirm authenticated user data
  - GET /api/health/ (or /api/health/detailed/) to confirm system health

Run locally after starting the stack (Docker Compose or local run):

PowerShell example:
  cd agrisight\agrisight
  python .\scripts\integration_smoke_test.py --base http://localhost:8000

Note: The script uses the requests library. Install it with `pip install requests` if needed.
"""
import argparse
import sys
import time
import json
import random
import string
from datetime import datetime

import requests


def random_email():
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"smoke_{ts}_{rand}@example.com"


def main(base_url: str):
    s = requests.Session()
    s.headers.update({'Accept': 'application/json'})

    print(f"Base URL: {base_url}")

    # 1) Get CSRF token
    try:
        r = s.get(f"{base_url}/api/auth/csrf/", timeout=10)
        r.raise_for_status()
        data = r.json()
        csrf_token = data.get('csrfToken') or data.get('csrf') or None
        print("CSRF endpoint returned:", data)
    except Exception as e:
        print("FAILED: Could not fetch CSRF token:", e)
        return 2

    if csrf_token is None:
        # Some setups may set cookie-only; try to use cookie
        csrf_token = s.cookies.get('csrftoken')

    if not csrf_token:
        print("WARNING: No CSRF token found in response or cookies; POSTs may fail.")

    # 2) Register a test user
    test_email = random_email()
    password = 'TestPass123!'
    registration_payload = {
        'email': test_email,
        'first_name': 'Smoke',
        'last_name': 'Tester',
        'user_type': 'researcher',
        'password': password,
        'password_confirm': password,
    }

    headers = {}
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token

    print(f"Registering test user: {test_email}")
    try:
        r = s.post(f"{base_url}/api/auth/registration/", json=registration_payload, headers=headers, timeout=15)
        # registration may require email verification depending on settings; accept 201/200/400 (duplicate)
        print("Registration status:", r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text[:400])
    except Exception as e:
        print("FAILED: Registration request error:", e)
        return 3

    # 3) Login
    login_payload = {
        'email': test_email,
        'password': password,
    }
    # Refresh CSRF token if server set new cookie
    csrf_token = s.cookies.get('csrftoken') or csrf_token
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token

    print("Attempting login...")
    try:
        r = s.post(f"{base_url}/api/auth/login/", json=login_payload, headers=headers, timeout=15)
        print("Login status:", r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text[:400])
        if r.status_code not in (200, 201):
            print("Login failed; server responded with non-success status. Exiting.")
            return 4
    except Exception as e:
        print("FAILED: Login request error:", e)
        return 4

    # 4) Get current user
    try:
        r = s.get(f"{base_url}/api/auth/user/", timeout=10)
        print("Current user status:", r.status_code)
        user_data = r.json() if r.status_code == 200 else None
        print("User data:", json.dumps(user_data, indent=2) if user_data else r.text[:400])
        if r.status_code != 200:
            print("Authenticated user endpoint did not return 200; login may have failed.")
            return 5
    except Exception as e:
        print("FAILED: Could not fetch current user:", e)
        return 5

    # 5) Health check
    health_endpoints = ['/api/health/', '/api/health/detailed/', '/api/health/check/']
    health_ok = False
    for ep in health_endpoints:
        try:
            r = s.get(f"{base_url}{ep}", timeout=8)
            if r.status_code == 200:
                print(f"Health endpoint {ep} OK:", r.json() if r.headers.get('content-type','').startswith('application/json') else r.text[:200])
                health_ok = True
                break
            else:
                print(f"Health endpoint {ep} returned {r.status_code}")
        except Exception as e:
            print(f"Health endpoint {ep} error:", e)

    if not health_ok:
        print("WARNING: No health endpoint returned 200. This may be fine depending on your deployment.")

    print("Smoke test completed. Please inspect messages above for any failures.")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AgriSight integration smoke test')
    parser.add_argument('--base', dest='base', default='http://localhost:8000', help='Base URL for the backend (default: http://localhost:8000)')
    args = parser.parse_args()
    sys.exit(main(args.base))
