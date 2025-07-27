#!/usr/bin/env python3
"""
Test script for the authentication system
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth_system():
    print("Testing Smart Document Assistant Authentication System\n")
    
    # Test 1: Access without login
    print("1. Testing access without login...")
    response = requests.get(f"{BASE_URL}/", allow_redirects=False)
    if response.status_code == 302 and '/login' in response.headers.get('Location', ''):
        print("✓ Correctly redirects to login page")
    else:
        print("✗ Should redirect to login")
    
    # Test 2: API access with user parameter
    print("\n2. Testing API access with user parameter...")
    response = requests.get(f"{BASE_URL}/api/search/text?q=test&user=Jeff")
    if response.status_code == 200:
        print("✓ API accessible with user parameter")
        print(f"   Response: {response.text[:100]}...")
    else:
        print("✗ API should be accessible with user parameter")
    
    # Test 3: Check status endpoint
    print("\n3. Testing status endpoint...")
    response = requests.get(f"{BASE_URL}/api/status")
    if response.status_code == 200:
        data = response.json()
        print("✓ Status endpoint accessible")
        print(f"   AI Enabled: {data.get('ai_enabled')}")
        print(f"   Google Drive: {data.get('google_drive')}")
        print(f"   Authenticated: {data.get('authenticated')}")
    
    # Test 4: Check users endpoint
    print("\n4. Testing users endpoint...")
    response = requests.get(f"{BASE_URL}/api/users")
    if response.status_code == 200:
        data = response.json()
        print("✓ Users endpoint accessible")
        print(f"   Total users: {data.get('total')}")
        print(f"   Users: {', '.join(data.get('users', []))}")
    
    print("\n5. Login form test...")
    print("   To test login, visit: http://localhost:5000/login")
    print("   Default admin credentials: Jeff / changeme")
    
    print("\n✓ Basic authentication system tests complete!")
    print("\nIMPORTANT REMINDERS:")
    print("- Change the default admin password immediately")
    print("- Add users through the admin panel at /admin")
    print("- iOS shortcuts should use the user parameter in API calls")

if __name__ == "__main__":
    print("Make sure the Flask app is running on port 5000")
    print("Run with: python3 app_flask_auth.py")
    input("Press Enter when ready to test...")
    
    try:
        test_auth_system()
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to Flask app")
        print("Make sure to run: python3 app_flask_auth.py")