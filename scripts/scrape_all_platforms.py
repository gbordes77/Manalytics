#!/usr/bin/env python3
"""
Unified scraper for all platforms (MTGO and Melee)
Launches both scrapers in parallel for efficient data collection
"""

import asyncio
import argparse
import logging
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
import concurrent.futures
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedScraper:
    """Coordinates scraping across multiple platforms"""
    
    def __init__(self):
        self.platforms = {
            'mtgo': {
                'script': 'scrape_mtgo_tournaments_enhanced.py',
                'name': 'MTGO',
                'supports_async': False
            },
            'melee': {
                'script': 'scrape_melee_tournaments_complete_v2.py', 
                'name': 'Melee.gg',
                'supports_async': False
            }
        }
        self.results = {}
    
    def run_scraper(self, platform: str, args: List[str]) -> Dict[str, Any]:
        """Run a single scraper and capture results"""
        start_time = time.time()
        platform_info = self.platforms[platform]
        
        logger.info(f"Starting {platform_info['name']} scraper...")
        
        try:
            # Build command
            cmd = [sys.executable, platform_info['script']] + args
            
            # Run the scraper
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent  # Run from project root
            )
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                logger.info(f"✅ {platform_info['name']} scraper completed successfully in {elapsed_time:.1f}s")
                return {
                    'status': 'success',
                    'platform': platform,
                    'elapsed_time': elapsed_time,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                logger.error(f"❌ {platform_info['name']} scraper failed with code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
                return {
                    'status': 'failed',
                    'platform': platform,
                    'elapsed_time': elapsed_time,
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except Exception as e:
            logger.error(f"❌ Exception running {platform_info['name']} scraper: {e}")
            return {
                'status': 'error',
                'platform': platform,
                'elapsed_time': time.time() - start_time,
                'error': str(e)
            }
    
    def scrape_all(self, platforms: List[str], common_args: List[str], 
                   platform_specific_args: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """Run scrapers for specified platforms in parallel"""
        
        if platform_specific_args is None:
            platform_specific_args = {}
        
        logger.info(f"Starting parallel scraping for platforms: {', '.join(platforms)}")
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(platforms)) as executor:
            # Submit all scraping tasks
            future_to_platform = {}
            for platform in platforms:
                # Combine common args with platform-specific args
                args = common_args + platform_specific_args.get(platform, [])
                future = executor.submit(self.run_scraper, platform, args)
                future_to_platform[future] = platform
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    result = future.result()
                    self.results[platform] = result
                except Exception as e:
                    logger.error(f"Exception getting result for {platform}: {e}")
                    self.results[platform] = {
                        'status': 'error',
                        'platform': platform,
                        'error': str(e)
                    }
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = {
            'total_time': total_time,
            'platforms_scraped': len(platforms),
            'successful': sum(1 for r in self.results.values() if r['status'] == 'success'),
            'failed': sum(1 for r in self.results.values() if r['status'] != 'success'),
            'results': self.results
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print a nice summary of scraping results"""
        logger.info("\n" + "=" * 60)
        logger.info("SCRAPING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total time: {summary['total_time']:.1f}s")
        logger.info(f"Platforms: {summary['platforms_scraped']}")
        logger.info(f"Successful: {summary['successful']}")
        logger.info(f"Failed: {summary['failed']}")
        
        logger.info("\nDetailed Results:")
        for platform, result in summary['results'].items():
            platform_name = self.platforms[platform]['name']
            status_icon = "✅" if result['status'] == 'success' else "❌"
            elapsed = result.get('elapsed_time', 0)
            logger.info(f"  {status_icon} {platform_name}: {result['status']} ({elapsed:.1f}s)")
            
            # Extract and show key statistics from stdout if available
            if result['status'] == 'success' and 'stdout' in result:
                self._extract_stats(platform, result['stdout'])
    
    def _extract_stats(self, platform: str, stdout: str):
        """Extract key statistics from scraper output"""
        lines = stdout.split('\n')
        
        if platform == 'mtgo':
            # Look for MTGO stats
            for line in lines:
                if "Successfully scraped" in line or "Save statistics" in line:
                    logger.info(f"    → {line.strip()}")
        elif platform == 'melee':
            # Look for Melee stats
            for line in lines:
                if "Saved:" in line or "Total processed:" in line or "Save statistics" in line:
                    logger.info(f"    → {line.strip()}")
    
    def save_run_metadata(self, summary: Dict[str, Any], args: argparse.Namespace):
        """Save metadata about this scraping run"""
        metadata_dir = Path("data/metadata/scraping_runs")
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata_file = metadata_dir / f"run_{timestamp}.json"
        
        metadata = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'arguments': vars(args),
            'summary': summary,
            'platforms': list(summary['results'].keys())
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"\nRun metadata saved to: {metadata_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Unified scraper for all MTG tournament platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all platforms for Standard format
  %(prog)s --format standard --days 30
  
  # Scrape specific date range
  %(prog)s --format standard --start-date 2025-07-01 --end-date 2025-07-24
  
  # Scrape only MTGO
  %(prog)s --platforms mtgo --format modern --days 7
  
  # Scrape with different settings per platform
  %(prog)s --format standard --days 30 --mtgo-types challenge,showcase --include-leagues
  
  # Generate reports after scraping
  %(prog)s --format standard --days 30 --generate-report
  
  # Dry run to see what would be scraped
  %(prog)s --format standard --days 7 --dry-run
        """
    )
    
    # Common arguments
    parser.add_argument("--platforms", type=str, default="mtgo,melee",
                       help="Comma-separated list of platforms to scrape (default: mtgo,melee)")
    parser.add_argument("--format", type=str, required=True,
                       help="Format to scrape (standard, modern, legacy, etc)")
    parser.add_argument("--days", type=int,
                       help="Number of days to look back")
    parser.add_argument("--start-date", type=str,
                       help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str,
                       help="End date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int,
                       help="Limit number of tournaments per platform")
    parser.add_argument("--force-redownload", action="store_true",
                       help="Force redownload even if already processed")
    parser.add_argument("--generate-report", action="store_true",
                       help="Generate detailed reports after scraping")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be scraped without downloading")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    # Platform-specific arguments
    parser.add_argument("--include-leagues", action="store_true",
                       help="Include league tournaments (applies to both platforms)")
    parser.add_argument("--mtgo-types", type=str,
                       help="MTGO-specific: Tournament types to include")
    parser.add_argument("--melee-exclude-types", type=str,
                       help="Melee-specific: Tournament types to exclude")
    
    args = parser.parse_args()
    
    # Determine platforms to scrape
    platforms = [p.strip() for p in args.platforms.split(',')]
    
    # Validate platforms
    scraper = UnifiedScraper()
    invalid_platforms = [p for p in platforms if p not in scraper.platforms]
    if invalid_platforms:
        logger.error(f"Invalid platforms: {', '.join(invalid_platforms)}")
        logger.error(f"Valid platforms: {', '.join(scraper.platforms.keys())}")
        return 1
    
    # Build common arguments
    common_args = [
        "--format", args.format
    ]
    
    # Add date range
    if args.days:
        common_args.extend(["--days", str(args.days)])
    if args.start_date:
        common_args.extend(["--start-date", args.start_date])
    if args.end_date:
        common_args.extend(["--end-date", args.end_date])
    
    # Add common flags
    if args.limit:
        common_args.extend(["--limit", str(args.limit)])
    if args.force_redownload:
        common_args.append("--force-redownload")
    if args.verbose:
        common_args.append("--verbose")
    if args.include_leagues:
        common_args.append("--include-leagues")
    
    # Build platform-specific arguments
    platform_specific_args = {}
    
    # MTGO-specific
    mtgo_args = []
    if args.mtgo_types:
        mtgo_args.extend(["--tournament-types", args.mtgo_types])
    if args.generate_report:
        mtgo_args.append("--generate-report")  # Only MTGO supports this
    if mtgo_args or 'mtgo' in platforms:
        platform_specific_args['mtgo'] = mtgo_args
    
    # Melee-specific
    melee_args = []
    if args.melee_exclude_types:
        melee_args.extend(["--exclude-types", args.melee_exclude_types])
    # Note: Melee doesn't support --generate-report or --dry-run
    if melee_args or 'melee' in platforms:
        platform_specific_args['melee'] = melee_args
    
    # Run scrapers
    logger.info(f"Starting unified scraping for {args.format} format")
    if args.start_date and args.end_date:
        logger.info(f"Date range: {args.start_date} to {args.end_date}")
    elif args.days:
        logger.info(f"Looking back {args.days} days")
    
    summary = scraper.scrape_all(platforms, common_args, platform_specific_args)
    
    # Print summary
    scraper.print_summary(summary)
    
    # Save metadata
    if not args.dry_run:
        scraper.save_run_metadata(summary, args)
    
    # Return appropriate exit code
    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    exit(main())