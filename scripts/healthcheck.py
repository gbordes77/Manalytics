#!/usr/bin/env python3
# scripts/healthcheck.py - Comprehensive health check script

import asyncio
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple
import httpx
import psycopg2
import redis
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

from config.settings import settings

console = Console()

class HealthChecker:
    """Comprehensive health checker for all Manalytics services."""
    
    def __init__(self):
        self.checks = []
        
    async def check_api(self) -> Tuple[str, bool, str]:
        """Check API health."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:8000/api/health",
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return "API", True, f"v{data.get('version', 'unknown')}"
                else:
                    return "API", False, f"Status: {response.status_code}"
        except Exception as e:
            return "API", False, str(e)
    
    def check_database(self) -> Tuple[str, bool, str]:
        """Check database health."""
        try:
            conn = psycopg2.connect(settings.DATABASE_URL)
            cursor = conn.cursor()
            
            # Check basic connectivity
            cursor.execute("SELECT 1")
            
            # Get some stats
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM tournaments) as tournaments,
                    (SELECT COUNT(*) FROM decklists) as decklists,
                    (SELECT COUNT(*) FROM archetypes) as archetypes
            """)
            stats = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return "Database", True, f"T:{stats[0]} D:{stats[1]} A:{stats[2]}"
        except Exception as e:
            return "Database", False, str(e)
    
    def check_redis(self) -> Tuple[str, bool, str]:
        """Check Redis health."""
        try:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            
            info = r.info()
            memory_mb = info.get('used_memory', 0) / 1024 / 1024
            keys = r.dbsize()
            
            return "Redis", True, f"Keys: {keys}, Mem: {memory_mb:.1f}MB"
        except Exception as e:
            return "Redis", False, str(e)
    
    async def check_scrapers(self) -> List[Tuple[str, bool, str]]:
        """Check scraper endpoints."""
        results = []
        
        scrapers = {
            "MTGO": settings.MTGO_BASE_URL,
            "Melee": settings.MELEE_BASE_URL
        }
        
        async with httpx.AsyncClient() as client:
            for name, url in scrapers.items():
                try:
                    response = await client.head(url, timeout=5.0)
                    if response.status_code < 400:
                        results.append((f"Scraper:{name}", True, "Reachable"))
                    else:
                        results.append((f"Scraper:{name}", False, f"Status: {response.status_code}"))
                except Exception as e:
                    results.append((f"Scraper:{name}", False, "Unreachable"))
        
        return results
    
    def check_disk_space(self) -> Tuple[str, bool, str]:
        """Check available disk space."""
        import shutil
        
        try:
            total, used, free = shutil.disk_usage("/")
            free_gb = free // (2**30)
            used_percent = (used / total) * 100
            
            status = free_gb > 1  # Warn if less than 1GB free
            
            return "Disk Space", status, f"{free_gb}GB free ({used_percent:.1f}% used)"
        except Exception as e:
            return "Disk Space", False, str(e)
    
    async def run_all_checks(self) -> List[Tuple[str, bool, str]]:
        """Run all health checks."""
        results = []
        
        # Async checks
        api_check = await self.check_api()
        results.append(api_check)
        
        # Sync checks
        results.append(self.check_database())
        results.append(self.check_redis())
        results.append(self.check_disk_space())
        
        # Scraper checks
        scraper_results = await self.check_scrapers()
        results.extend(scraper_results)
        
        return results
    
    def display_results(self, results: List[Tuple[str, bool, str]]):
        """Display health check results in a nice table."""
        table = Table(title="🏥 Manalytics Health Check")
        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")
        
        all_healthy = True
        
        for service, healthy, details in results:
            status = "✅ Healthy" if healthy else "❌ Unhealthy"
            status_style = "green" if healthy else "red"
            table.add_row(service, f"[{status_style}]{status}[/]", details)
            
            if not healthy:
                all_healthy = False
        
        console.print(table)
        
        # Overall status
        if all_healthy:
            console.print("\n[green]✅ All systems operational![/]")
        else:
            console.print("\n[red]❌ Some systems need attention![/]")
        
        return all_healthy
    
    async def continuous_monitoring(self, interval: int = 30):
        """Run continuous monitoring."""
        console.print(f"Starting continuous monitoring (interval: {interval}s)")
        console.print("Press Ctrl+C to stop\n")
        
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                results = await self.run_all_checks()
                
                # Create table
                table = Table(title=f"🏥 Manalytics Health Monitor - {timestamp}")
                table.add_column("Service", style="cyan", no_wrap=True)
                table.add_column("Status", style="bold")
                table.add_column("Details", style="dim")
                
                for service, healthy, details in results:
                    status = "✅" if healthy else "❌"
                    status_style = "green" if healthy else "red"
                    table.add_row(service, f"[{status_style}]{status}[/]", details)
                
                live.update(Panel(table))
                
                await asyncio.sleep(interval)


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manalytics Health Checker")
    parser.add_argument(
        "--continuous", "-c",
        action="store_true",
        help="Run continuous monitoring"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="Monitoring interval in seconds (default: 30)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    
    if args.continuous:
        try:
            await checker.continuous_monitoring(args.interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped by user[/]")
    else:
        results = await checker.run_all_checks()
        
        if args.json:
            # JSON output for automation
            output = {
                "timestamp": datetime.now().isoformat(),
                "checks": [
                    {"service": s, "healthy": h, "details": d}
                    for s, h, d in results
                ],
                "overall_healthy": all(h for _, h, _ in results)
            }
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            all_healthy = checker.display_results(results)
            sys.exit(0 if all_healthy else 1)


if __name__ == "__main__":
    asyncio.run(main())