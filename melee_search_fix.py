#!/usr/bin/env python3
"""Patch pour corriger l'endpoint de recherche Melee."""

def patch_melee_scraper():
    """Patch the search endpoint in melee_scraper.py"""
    
    # Read the current file
    with open('src/scrapers/melee_scraper.py', 'r') as f:
        content = f.read()
    
    # Replace the search endpoint
    old_line = 'search_response = await self.client.post(f"{self.base_url}/Tournament/SearchTournaments",'
    new_line = 'search_response = await self.client.post(f"{self.base_url}/Tournament/SearchResults",'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ Found and replaced SearchTournaments with SearchResults")
    else:
        # Try another pattern
        old_pattern = '/Tournament/SearchTournaments'
        new_pattern = '/Tournament/SearchResults'
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print("✅ Found and replaced SearchTournaments pattern")
        else:
            print("❌ Could not find SearchTournaments endpoint to replace")
            return False
    
    # Write the patched file
    with open('src/scrapers/melee_scraper.py', 'w') as f:
        f.write(content)
    
    print("✅ Melee scraper patched successfully")
    return True

if __name__ == "__main__":
    patch_melee_scraper()