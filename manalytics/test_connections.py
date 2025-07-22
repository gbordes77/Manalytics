#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Connectivity test for the MTG Analytics pipeline.
This script checks connectivity with MTGO and MTGMelee data sources.
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime
from urllib.parse import urljoin

# Colors for messages
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_info(message):
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {message}")

def log_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {message}")

def log_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {message}")

def log_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {message}")

def load_config():
    """Load configuration from sources.json file."""
    config_path = os.path.join(os.path.dirname(__file__), "config", "sources.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        log_error(f"JSON format error in configuration file: {config_path}")
        sys.exit(1)

def load_credentials():
    """Load credentials from credentials.json file if it exists."""
    credentials_path = os.path.join(os.path.dirname(__file__), "config", "credentials.json")
    try:
        with open(credentials_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_warning(f"Credentials file not found: {credentials_path}")
        return None
    except json.JSONDecodeError:
        log_error(f"JSON format error in credentials file: {credentials_path}")
        return None

def test_mtgo_connection(config):
    """Test connection to MTGO URLs."""
    log_info("Testing connection to MTGO URLs...")
    
    mtgo_config = config.get("mtgo", {})
    if not mtgo_config:
        log_error("MTGO configuration not found in sources.json")
        return False
    
    # Test one URL of each type
    test_urls = []
    for url_type in ["base_urls", "challenge_urls", "preliminary_urls", "showcase_urls", "super_qualifier_urls", "premier_urls"]:
        urls = mtgo_config.get(url_type, {})
        if urls and "standard" in urls:
            test_urls.append((url_type, urls["standard"]))
    
    if not test_urls:
        log_error("No MTGO URLs found in configuration")
        return False
    
    success_count = 0
    failure_count = 0
    
    for url_type, url in test_urls:
        try:
            log_info(f"Testing {url_type}: {url}")
            headers = {
                "User-Agent": mtgo_config.get("scraping_config", {}).get("user_agent", "Mozilla/5.0")
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                log_success(f"Successful connection to {url_type}")
                success_count += 1
            else:
                log_error(f"Connection failed to {url_type}: Code {response.status_code}")
                failure_count += 1
        except requests.RequestException as e:
            log_error(f"Error connecting to {url_type}: {str(e)}")
            failure_count += 1
        
        # Pause to avoid being blocked
        time.sleep(1)
    
    log_info(f"MTGO test completed: {success_count} successes, {failure_count} failures")
    return success_count > 0

def test_mtgmelee_connection(config, credentials=None):
    """Test connection to MTGMelee API."""
    log_info("Testing connection to MTGMelee API...")
    
    mtgmelee_config = config.get("mtgmelee", {})
    if not mtgmelee_config:
        log_error("MTGMelee configuration not found in sources.json")
        return False
    
    api_config = mtgmelee_config.get("api", {})
    if not api_config:
        log_error("MTGMelee API configuration not found in sources.json")
        return False
    
    base_url = api_config.get("base_url")
    if not base_url:
        log_error("MTGMelee API base URL not found in configuration")
        return False
    
    # Test without authentication
    try:
        log_info(f"Testing connection to MTGMelee API (without auth): {base_url}")
        response = requests.get(urljoin(base_url, "tournaments"), params={"pageSize": 1}, timeout=10)
        
        if response.status_code == 200:
            log_success("Successful connection to MTGMelee API (without auth)")
            return True
        else:
            log_warning(f"Connection failed to MTGMelee API (without auth): Code {response.status_code}")
    except requests.RequestException as e:
        log_error(f"Error connecting to MTGMelee API (without auth): {str(e)}")
    
    # Test with authentication if credentials are available
    if credentials and "mtgmelee" in credentials:
        try:
            log_info("Testing connection to MTGMelee API (with auth)")
            
            auth_url = api_config.get("auth", {}).get("login_url")
            if not auth_url:
                log_error("MTGMelee authentication URL not found in configuration")
                return False
            
            auth_data = {
                "username": credentials["mtgmelee"].get("username"),
                "password": credentials["mtgmelee"].get("password")
            }
            
            auth_response = requests.post(auth_url, json=auth_data, timeout=10)
            
            if auth_response.status_code == 200:
                token = auth_response.json().get("token")
                if token:
                    log_success("Successful authentication to MTGMelee API")
                    
                    # Test an authenticated endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get(
                        urljoin(base_url, "tournaments"), 
                        headers=headers, 
                        params={"pageSize": 1}, 
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        log_success("Successful authenticated connection to MTGMelee API")
                        return True
                    else:
                        log_error(f"Authenticated connection failed to MTGMelee API: Code {response.status_code}")
                else:
                    log_error("Authentication token not found in response")
            else:
                log_error(f"Authentication failed to MTGMelee API: Code {auth_response.status_code}")
        except requests.RequestException as e:
            log_error(f"Error during authentication to MTGMelee API: {str(e)}")
        except json.JSONDecodeError:
            log_error("Error decoding JSON response from MTGMelee API")
    else:
        log_warning("MTGMelee credentials not found, authentication test skipped")
    
    return False

def generate_report(mtgo_success, mtgmelee_success):
    """Generate a test report."""
    report_dir = os.path.join(os.path.dirname(__file__), "docs")
    os.makedirs(report_dir, exist_ok=True)
    
    report_path = os.path.join(report_dir, "connection_test_report.md")
    
    with open(report_path, 'w') as f:
        f.write("# Connectivity Test Report\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- MTGO: {'✅ Connected' if mtgo_success else '❌ Not connected'}\n")
        f.write(f"- MTGMelee: {'✅ Connected' if mtgmelee_success else '❌ Not connected'}\n\n")
        
        f.write("## Details\n\n")
        
        f.write("### MTGO\n\n")
        if mtgo_success:
            f.write("Connection to MTGO URLs was successful. Scraping should work correctly.\n\n")
        else:
            f.write("Connection to MTGO URLs failed. Check your internet connection and the URLs in the configuration.\n\n")
        
        f.write("### MTGMelee\n\n")
        if mtgmelee_success:
            f.write("Connection to MTGMelee API was successful. Integration should work correctly.\n\n")
        else:
            f.write("Connection to MTGMelee API failed. Check your internet connection, API endpoints, and credentials.\n\n")
        
        f.write("## Next steps\n\n")
        if mtgo_success and mtgmelee_success:
            f.write("All connections are functional. You can start using the pipeline.\n")
        else:
            f.write("Some connections failed. Resolve the issues before using the pipeline.\n")
    
    log_info(f"Report generated: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Connectivity test for the MTG Analytics pipeline")
    parser.add_argument("--mtgo-only", action="store_true", help="Test only MTGO connection")
    parser.add_argument("--mtgmelee-only", action="store_true", help="Test only MTGMelee connection")
    args = parser.parse_args()
    
    log_info("Starting connectivity tests...")
    
    config = load_config()
    credentials = load_credentials()
    
    mtgo_success = False
    mtgmelee_success = False
    
    if not args.mtgmelee_only:
        mtgo_success = test_mtgo_connection(config)
    
    if not args.mtgo_only:
        mtgmelee_success = test_mtgmelee_connection(config, credentials)
    
    generate_report(mtgo_success, mtgmelee_success)
    
    if (not args.mtgmelee_only and not mtgo_success) or (not args.mtgo_only and not mtgmelee_success):
        log_warning("Some tests failed. Check the report for details.")
        return 1
    else:
        log_success("All requested tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())