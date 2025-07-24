#!/usr/bin/env python3
"""
Test Melee web authentication with proper cookie handling.
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import logging
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_melee_web_auth():
    """Test web-based authentication."""
    base_url = "https://melee.gg"
    email = "gbordes64@gmail.com"
    password = "Ctr0Dur!"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Browser headers
        client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        
        # Try different login URLs
        login_urls = [
            f"{base_url}/Login",
            f"{base_url}/Account/Login",
            f"{base_url}/Account/SignIn",
            f"{base_url}/signin"
        ]
        
        for login_url in login_urls:
            logger.info(f"\nTrying login URL: {login_url}")
            try:
                response = await client.get(login_url)
                logger.info(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for forms
                    forms = soup.find_all('form')
                    logger.info(f"Found {len(forms)} forms")
                    
                    # Look for password fields
                    password_fields = soup.find_all('input', {'type': 'password'})
                    logger.info(f"Found {len(password_fields)} password fields")
                    
                    if password_fields:
                        logger.info("This looks like a traditional login page!")
                        
                        # Find CSRF token
                        csrf_token = None
                        for inp in soup.find_all('input', {'type': 'hidden'}):
                            name = inp.get('name', '')
                            if 'token' in name.lower() or 'csrf' in name.lower():
                                csrf_token = inp.get('value')
                                logger.info(f"Found token: {name} = {csrf_token[:20]}...")
                        
                        # Find form action
                        if forms:
                            form = forms[0]
                            action = form.get('action', '')
                            method = form.get('method', 'POST')
                            logger.info(f"Form action: {action}, method: {method}")
                            
                            # Try to login
                            if csrf_token:
                                login_data = {
                                    'Email': email,
                                    'Password': password
                                }
                                
                                if csrf_token:
                                    login_data['__RequestVerificationToken'] = csrf_token
                                
                                # Submit login
                                submit_url = urljoin(base_url, action) if action else login_url.replace('/Login', '/SignInPassword').replace('/SignIn', '/SignInPassword')
                                logger.info(f"Submitting to: {submit_url}")
                                
                                response = await client.post(
                                    submit_url,
                                    data=login_data,
                                    headers={'Referer': login_url}
                                )
                                
                                logger.info(f"Login response: {response.status_code}")
                                logger.info(f"Cookies: {list(client.cookies.keys())}")
                                
                                # Check if we're logged in
                                if any('auth' in k.lower() or 'session' in k.lower() for k in client.cookies.keys()):
                                    logger.info("Login appears successful!")
                                    return True
                    
                    # Check for passwordless auth
                    email_only_fields = soup.find_all('input', {'type': 'email'})
                    if email_only_fields and not password_fields:
                        logger.info("This appears to be passwordless authentication!")
                        logger.info("Melee may have switched to magic link authentication")
                
            except Exception as e:
                logger.error(f"Error with {login_url}: {e}")
        
        return False

from urllib.parse import urljoin

if __name__ == "__main__":
    asyncio.run(test_melee_web_auth())