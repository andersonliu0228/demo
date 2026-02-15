#!/usr/bin/env python3
"""Simple register function test"""
import requests
import random

API_BASE = "http://localhost:8000"

# Test 1: Register new user
username = f"testuser_{random.randint(1000, 9999)}"
email = f"test_{random.randint(1000, 9999)}@example.com"
password = "testpass123"

print(f"[Test 1] Registering user: {username}")
response = requests.post(f"{API_BASE}/api/v1/auth/register", json={
    "username": username,
    "email": email,
    "password": password
})
assert response.status_code == 201, f"Expected 201, got {response.status_code}"
data = response.json()
print(f"✓ Registered: {data['username']}, is_active={data['is_active']}")

# Test 2: Login with new account
print(f"\n[Test 2] Login with new account")
response = requests.post(f"{API_BASE}/api/v1/auth/login", data={
    "username": username,
    "password": password
})
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
token = response.json()["access_token"]
print(f"✓ Login successful, token: {token[:20]}...")

# Test 3: Duplicate username (should fail)
print(f"\n[Test 3] Test duplicate username (should fail)")
response = requests.post(f"{API_BASE}/api/v1/auth/register", json={
    "username": username,
    "email": f"another_{email}",
    "password": password
})
assert response.status_code == 400, f"Expected 400, got {response.status_code}"
print(f"✓ Correctly rejected duplicate username")

print("\n=== ALL TESTS PASSED ===")
