#!/usr/bin/env python3
import asyncio
import httpx
from datetime import datetime, timedelta

async def test_melee_api():
    base_url = 'https://melee.gg'
    
    async with httpx.AsyncClient() as client:
        # Search tournaments
        search_payload = {
            'draw': '1',
            'start': '0',
            'length': '100',
            'search[value]': '',
            'search[regex]': 'false'
        }
        
        print('Searching Melee tournaments...')
        response = await client.post(
            f'{base_url}/Tournament/SearchResults',
            data=search_payload,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0'
            }
        )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Found {len(data)} total tournaments')
            
            # Filter Magic tournaments
            magic_tournaments = []
            for t in data:
                if 'magic' in t.get('gameDescription', '').lower():
                    magic_tournaments.append(t)
            
            print(f'Found {len(magic_tournaments)} Magic tournaments')
            
            # Show recent ones
            print('\nRecent Magic tournaments:')
            for t in magic_tournaments[:10]:
                tid = t.get('id')
                name = t.get('name')
                date = t.get('startDate', '').split('T')[0]
                print(f'- {name} ({date}) - ID: {tid}')

if __name__ == "__main__":
    asyncio.run(test_melee_api())