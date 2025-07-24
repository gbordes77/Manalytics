#!/usr/bin/env python3
"""
Test MTGO scraper for different formats to understand URL patterns.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from src.scrapers.mtgo_scraper import MTGOScraper
from src.utils.logging_config import setup_logging
import logging
import re
from bs4 import BeautifulSoup

setup_logging()
logger = logging.getLogger(__name__)

async def analyze_mtgo_structure():
    """Analyze MTGO decklists page structure for different formats."""
    
    # Create a scraper instance just to use its methods
    scraper = MTGOScraper("standard")
    
    async with scraper:
        # Fetch the main decklists page
        decklists_url = "https://www.mtgo.com/decklists"
        logger.info(f"Fetching main decklists page: {decklists_url}")
        
        content = await scraper._fetch_url(decklists_url)
        if not content:
            logger.error("Failed to fetch decklists page")
            return
        
        # Parse and analyze
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all links that might be tournament links
        all_links = soup.find_all('a', href=True)
        
        # Categorize links by format
        format_links = {
            "standard": [],
            "modern": [],
            "legacy": [],
            "vintage": [],
            "pioneer": [],
            "pauper": []
        }
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if it's a decklist link
            if '/decklist/' in href:
                for fmt in format_links:
                    if f'/decklist/{fmt}' in href:
                        format_links[fmt].append({
                            'href': href,
                            'text': text,
                            'full_url': f"https://www.mtgo.com{href}" if href.startswith('/') else href
                        })
        
        # Report findings
        logger.info("\n=== MTGO Decklists Analysis ===")
        for fmt, links in format_links.items():
            logger.info(f"\n{fmt.upper()}: {len(links)} links found")
            if links:
                # Show first 3 links as examples
                for i, link_info in enumerate(links[:3]):
                    logger.info(f"  Example {i+1}:")
                    logger.info(f"    Text: {link_info['text']}")
                    logger.info(f"    Href: {link_info['href']}")
                    logger.info(f"    Full URL: {link_info['full_url']}")

async def test_specific_formats():
    """Test scraping for both Standard and Modern to see the difference."""
    start_date = datetime(2025, 7, 20)
    end_date = datetime(2025, 7, 24)
    
    formats_to_test = ["standard", "modern"]
    
    for format_name in formats_to_test:
        logger.info(f"\n=== Testing {format_name.upper()} format ===")
        
        scraper = MTGOScraper(format_name)
        async with scraper:
            tournaments = await scraper.scrape_tournaments(start_date, end_date)
            
            logger.info(f"Found {len(tournaments)} {format_name} tournaments")
            
            if tournaments:
                for t in tournaments:
                    logger.info(f"  {t['date']} - {t['name']} - {len(t.get('decklists', []))} decks")
                    logger.info(f"    URL: {t['url']}")
            else:
                # Let's debug what's happening
                logger.info(f"No tournaments found for {format_name}")
                
                # Try to fetch the decklists page and see what we get
                decklists_url = f"{scraper.base_url}/decklists"
                content = await scraper._fetch_url(decklists_url)
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    format_slug = scraper.format_mapping.get(format_name.lower())
                    pattern = f'/decklist/{format_slug}'
                    links = soup.find_all('a', href=re.compile(pattern))
                    logger.info(f"  Found {len(links)} links matching pattern '{pattern}'")
                    
                    # Show first few links for debugging
                    for link in links[:5]:
                        logger.info(f"    Link: {link.get('href')} - Text: {link.get_text(strip=True)[:50]}...")

if __name__ == "__main__":
    asyncio.run(analyze_mtgo_structure())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_specific_formats())