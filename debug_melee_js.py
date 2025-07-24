#!/usr/bin/env python3
"""
Debug Melee by examining the JavaScript to see how real calls are made.
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import re

async def debug_javascript():
    """Find how the real website makes API calls."""
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        client.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        # Get the main tournaments page
        print("=== Getting Tournament index page ===")
        tournament_page_url = "https://melee.gg/Tournament"
        response = await client.get(tournament_page_url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for DataTables initialization or AJAX calls
            scripts = soup.find_all('script')
            
            print(f"Found {len(scripts)} script tags")
            
            for i, script in enumerate(scripts):
                if script.string:
                    script_content = script.string
                    
                    # Look for DataTables or AJAX patterns
                    if any(keyword in script_content for keyword in ['DataTable', 'ajax', 'SearchTournaments', 'columns']):
                        print(f"\n=== Script {i} (relevant) ===")
                        print(script_content[:1000])
                        
                        # Extract AJAX URLs
                        ajax_matches = re.findall(r'url["\']?\s*:\s*["\']([^"\']+)', script_content)
                        for match in ajax_matches:
                            print(f"Found AJAX URL: {match}")
                        
                        # Extract column definitions
                        column_matches = re.findall(r'columns\s*:\s*\[([^\]]+)\]', script_content, re.DOTALL)
                        for match in column_matches:
                            print(f"Found columns: {match[:200]}...")
                        
                        # Look for request parameters
                        data_matches = re.findall(r'data\s*:\s*function[^}]+\{([^}]+)\}', script_content, re.DOTALL)
                        for match in data_matches:
                            print(f"Found data function: {match[:200]}...")
            
            # Also look for any hidden form fields or tokens
            hidden_inputs = soup.find_all('input', type='hidden')
            print(f"\n=== Found {len(hidden_inputs)} hidden inputs ===")
            for inp in hidden_inputs:
                name = inp.get('name', '')
                value = inp.get('value', '')[:50]
                if name:
                    print(f"  {name}: {value}")
            
            # Look for any tournament data already in the page
            if 'tournament' in response.text.lower():
                print("\n=== Looking for existing tournament data ===")
                # Search for tournament IDs or data
                tournament_patterns = [
                    r'tournament["\']?\s*:\s*["\']?(\d+)',
                    r'/Tournament/(\d+)',
                    r'tournamentId["\']?\s*:\s*["\']?(\d+)',
                ]
                
                for pattern in tournament_patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        print(f"Found tournament IDs: {matches[:10]}")
            
            # Try to find the exact DataTables configuration
            print("\n=== Looking for DataTables config ===")
            datatable_pattern = r'\$\([^)]+\)\.DataTable\s*\(\s*\{([^}]+)\}\s*\)'
            datatable_matches = re.findall(datatable_pattern, response.text, re.DOTALL)
            
            for i, match in enumerate(datatable_matches):
                print(f"DataTable config {i}:")
                print(match[:500])

if __name__ == "__main__":
    asyncio.run(debug_javascript())