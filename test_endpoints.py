#!/usr/bin/env python3
"""
Test script for UPAK personal cabinet endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_register():
    """Test user registration"""
    print("\n=== Testing Registration ===")
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "test@upak.space",
        "password": "StrongPass123"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get('access_token')

def test_login():
    """Test user login"""
    print("\n=== Testing Login ===")
    response = requests.post(f"{BASE_URL}/auth/token", data={
        "username": "test@upak.space",
        "password": "StrongPass123"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get('access_token')

def test_get_me(token):
    """Test GET /me endpoint"""
    print("\n=== Testing GET /me ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_cards(token):
    """Test GET /cards endpoint"""
    print("\n=== Testing GET /cards ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cards?limit=10&offset=0", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_payments(token):
    """Test GET /payments endpoint"""
    print("\n=== Testing GET /payments ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/payments?limit=10", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_create_payment(token, package='start'):
    """Test POST /payments/create endpoint"""
    print(f"\n=== Testing POST /payments/create (package={package}) ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/payments/create", 
                            headers=headers,
                            json={"package": package})
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("Starting UPAK API Tests...")
    
    # Try to register (might fail if user exists)
    try:
        token = test_register()
    except:
        # If registration fails, try login
        token = test_login()
    
    if not token:
        print("Failed to get access token!")
        return
    
    # Test all endpoints
    test_get_me(token)
    test_get_cards(token)
    test_get_payments(token)
    test_create_payment(token, 'start')
    test_create_payment(token, 'pro')
    
    print("\n=== All tests completed ===")

if __name__ == '__main__':
    main()
