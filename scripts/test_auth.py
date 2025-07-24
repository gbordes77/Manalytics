#!/usr/bin/env python3
"""
Test script for JWT authentication.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import json
from config.settings import settings

def test_auth_flow():
    """Test the complete authentication flow."""
    base_url = "http://localhost:8000"
    
    print("🔐 Testing JWT Authentication Flow\n")
    
    # Test 1: Login with credentials
    print("1. Testing login endpoint...")
    login_data = {
        "username": "admin",
        "password": "changeme"
    }
    
    try:
        with httpx.Client() as client:
            # Test login
            response = client.post(
                f"{base_url}/api/auth/token",
                data=login_data  # Form data, not JSON
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"✅ Login successful!")
                print(f"   Token type: {token_data['token_type']}")
                print(f"   Token (first 20 chars): {access_token[:20]}...")
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
            
            # Test 2: Access protected endpoint without token
            print("\n2. Testing protected endpoint WITHOUT token...")
            response = client.get(f"{base_url}/api/decks")
            print(f"   Status: {response.status_code} (should be 401)")
            if response.status_code == 401:
                print("✅ Correctly rejected unauthorized request")
            else:
                print("❌ Expected 401, got", response.status_code)
            
            # Test 3: Access protected endpoint with token
            print("\n3. Testing protected endpoint WITH token...")
            headers = {"Authorization": f"Bearer {access_token}"}
            response = client.get(f"{base_url}/api/decks", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Successfully accessed protected endpoint")
            else:
                print(f"❌ Failed to access: {response.text}")
            
            # Test 4: Get current user info
            print("\n4. Testing /me endpoint...")
            response = client.get(f"{base_url}/api/auth/me", headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                print("✅ User info retrieved:")
                print(f"   Username: {user_info['username']}")
                print(f"   Email: {user_info['email']}")
                print(f"   Is Admin: {user_info['is_admin']}")
            else:
                print(f"❌ Failed to get user info: {response.status_code}")
            
            # Test 5: Test public endpoints still work
            print("\n5. Testing public endpoints...")
            response = client.get(f"{base_url}/api/health")
            if response.status_code == 200:
                print("✅ Public health endpoint accessible")
            else:
                print("❌ Public endpoint failed")
                
    except httpx.ConnectError:
        print("❌ Could not connect to API. Is it running?")
        print("   Start with: docker-compose up api")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def generate_test_token():
    """Generate a test token for development."""
    from src.api.auth import create_access_token
    from datetime import timedelta
    
    print("\n📝 Generating test token for development...")
    
    # Create a token that expires in 7 days
    access_token = create_access_token(
        data={"sub": "admin"},
        expires_delta=timedelta(days=7)
    )
    
    print(f"\nTest token (valid for 7 days):")
    print(f"{access_token}")
    print(f"\nUse in curl:")
    print(f'curl -H "Authorization: Bearer {access_token}" http://localhost:8000/api/decks')
    print(f"\nUse in Python:")
    print(f'headers = {{"Authorization": "Bearer {access_token}"}}')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test JWT authentication")
    parser.add_argument("--generate-token", action="store_true", help="Generate a test token")
    args = parser.parse_args()
    
    if args.generate_token:
        generate_test_token()
    else:
        test_auth_flow()