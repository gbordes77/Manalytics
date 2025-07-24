#!/usr/bin/env python3
"""
Minimal API test to identify issues
"""

import httpx
import asyncio

async def test_api():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Test health
        resp = await client.get(f"{base_url}/api/health")
        print(f"Health check: {resp.status_code} - {resp.json()}")
        
        # Login  
        resp = await client.post(
            f"{base_url}/api/auth/token",
            data={"username": "admin", "password": "changeme"}
        )
        print(f"Login: {resp.status_code}")
        
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test endpoints with trailing slash
            endpoints = [
                "/api/decks/",
                "/api/archetypes/?format=modern", 
                "/api/analysis/meta/modern"
            ]
            
            for endpoint in endpoints:
                try:
                    resp = await client.get(f"{base_url}{endpoint}", headers=headers)
                    print(f"{endpoint}: {resp.status_code}")
                    if resp.status_code != 200:
                        print(f"  Error: {resp.text[:200]}")
                except Exception as e:
                    print(f"{endpoint}: ERROR - {e}")

if __name__ == "__main__":
    asyncio.run(test_api())