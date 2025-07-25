#!/usr/bin/env python3
"""
Test script using the working Melee scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone, timedelta
from scrapers.models.Melee_model import *
from scrapers.models.base_model import *
from scrapers.comon_tools.tools import *
import json
import argparse
from pathlib import Path

# Copy the working code
import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Optional
from dateutil import parser
from dataclasses import dataclass
from requests.cookies import RequestsCookieJar

class MtgMeleeClient:
    @staticmethod
    def get_client(load_cookies: bool = False):
        """
        Create and configure a requests session for interacting with MTG Melee.
        
        Parameters:
        - load_cookies (bool): If True, attempt to load cookies from file if still valid.
                               Defaults to False.
        
        Returns:
        - session (requests.Session): Configured requests session.
        """
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest'
        })
        if load_cookies:
            # Load cookies if still valid
            cookies_are_valid = MtgMeleeClient._cookies_valid()
            MtgMeleeClient._refresh_cookies(session, force_login=not cookies_are_valid)
            
            if cookies_are_valid:
                MtgMeleeClient._load_cookies(session)
        return session
    
    @staticmethod
    def _cookies_valid():
        if not os.path.exists(MtgMeleeConstants.COOKIE_FILE):
            return False
        try:
            with open(MtgMeleeConstants.COOKIE_FILE, "r") as f:
                data = json.load(f)
                timestamp = data.get("_timestamp")
                if not timestamp:
                    return False
                age = datetime.now() - datetime.fromtimestamp(timestamp)
                return age < timedelta(days=MtgMeleeConstants.COOKIE_MAX_AGE_DAYS)
        except Exception:
            return False

    @staticmethod
    def _load_cookies(session):
        # need to reresh __RequestVerificationToken
        with open(MtgMeleeConstants.COOKIE_FILE, "r") as f:
            data = json.load(f)
            cookies = data.get("cookies", {})
            session.cookies.update(cookies)
            
    @staticmethod
    def _refresh_cookies(session, force_login=False):
        # Initialiser la session
        session.cookies.clear()

        # Headers classiques pour accéder au formulaire de login
        classic_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://melee.gg/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        # Step 1: GET login page to extract __RequestVerificationToken
        login_page = session.get("https://melee.gg/Account/SignIn", headers=classic_headers)
        if login_page.status_code != 200:
            raise Exception(f"Failed to load login page: {login_page.status_code}")

        soup = BeautifulSoup(login_page.text, "html.parser")
        token_input = soup.find("input", {"name": "__RequestVerificationToken"})
        if not token_input:
            raise Exception("CSRF token not found in login page")
        token = token_input["value"]

        if force_login:
            # Load credentials
            if not os.path.exists(MtgMeleeConstants.CRED_FILE):
                raise FileNotFoundError("Missing login file: melee_login.json")
            with open(MtgMeleeConstants.CRED_FILE, "r") as f:
                creds = json.load(f)

            # Prepare AJAX headers and payload
            ajax_headers = {
                "User-Agent": classic_headers["User-Agent"],
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://melee.gg",
                "Referer": "https://melee.gg/Account/SignIn"
            }

            login_payload = {
                "email": creds["login"],
                "password": creds["mdp"],
                "__RequestVerificationToken": token
            }

            # Step 2: POST login
            response = session.post(
                "https://melee.gg/Account/SignInPassword",
                headers=ajax_headers,
                data=login_payload
            )

            if response.status_code != 200 or '"Error":true' in response.text:
                print("Raw response: ", response.text[:1000])
                raise Exception(f"Login failed: status={response.status_code}")

            if ".AspNet.ApplicationCookie" not in session.cookies.get_dict():
                raise Exception(f"Login did not set auth cookie properly: {session.cookies.get_dict()}")

            # Save cookies
            cookies_to_store = {
                "cookies": session.cookies.get_dict(),
                "_timestamp": time.time()
            }
            with open(MtgMeleeConstants.COOKIE_FILE, "w") as f:
                json.dump(cookies_to_store, f, indent=2)

    @staticmethod
    def normalize_spaces(data):
        return re.sub(r'\s+', ' ', data).strip()

    def get_tournaments(self, start_date, end_date):
        length_tournament_page = 500
        result = []
        draw = 1
        starting_point = 0
        seen_ids = set()

        while True:
            payload = MtgMeleeConstants.build_magic_payload(start_date, end_date, length=length_tournament_page, draw=draw, start=starting_point)
            tournament_list_url = 'https://melee.gg/Decklist/SearchDecklists'

            MAX_RETRIES = 3
            DELAY_SECONDS = 2
            
            for attempt in range(1, MAX_RETRIES + 1):
                print(f"Attempt {attempt} - Making request to Melee API...")
                response = self.get_client(load_cookies=True).post(tournament_list_url, data=payload)
                
                if response.text.strip():
                    try:
                        tournament_data = json.loads(response.text)
                        print(f"Success! Got {len(tournament_data.get('data', []))} records")
                        break
                    except json.JSONDecodeError:
                        print(f"Attempt {attempt}: Failed to parse JSON.")
                else:
                    print(f"Attempt {attempt}: Empty response.")

                if attempt < MAX_RETRIES:
                    time.sleep(DELAY_SECONDS)
            else:
                print("All attempts failed")
                return None
            
            new_tournaments = tournament_data.get("data", [])
            for tournament in new_tournaments:
                tournament_id = tournament.get('Guid')
                if tournament_id not in seen_ids:
                    result.append(tournament)
                    seen_ids.add(tournament_id)
                    
            if tournament_data["recordsFiltered"] == len(result):
                break
            if ((draw-1) * length_tournament_page) >= tournament_data["recordsFiltered"]:
                break

            draw += 1
            starting_point += length_tournament_page
            
        return result


# Simple test
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=2)
    args = parser.parse_args()
    
    start_date = datetime.now(timezone.utc) - timedelta(days=args.days)
    end_date = datetime.now(timezone.utc)
    
    print(f"Testing Melee scraper from {start_date.date()} to {end_date.date()}")
    
    client = MtgMeleeClient()
    tournaments = client.get_tournaments(start_date, end_date)
    
    if tournaments:
        print(f"\nFound {len(tournaments)} tournament records")
        # Show first few
        for t in tournaments[:5]:
            print(f"- {t.get('TournamentName')} ({t.get('FormatDescription')})")
    else:
        print("No tournaments found or error occurred")

if __name__ == "__main__":
    main()