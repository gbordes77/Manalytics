#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MTG Analytics Pipeline Orchestrator
This script orchestrates the entire pipeline from data collection to analysis visualization.
"""

import os
import sys
import json
import argparse
import logging
import subprocess
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('orchestrator')

class MTGAnalyticsOrchestrator:
    """Main orchestrator for the MTG Analytics pipeline."""
    
    def __init__(self, base_dir=None):
        """Initialize the orchestrator."""
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.config = self._load_config()
        self.analysis_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _load_config(self):
        """Load configuration from sources.json."""
        config_path = os.path.join(self.base_dir, "config", "sources.json")
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"JSON format error in configuration file: {config_path}")
            return {}
    
    def _calculate_days_between(self, start_date, end_date):
        """Calculate the number of days between two dates."""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return (end - start).days + 1  # Include both start and end dates
        except ValueError as e:
            logger.error(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")
            return None
    
    def _check_data_availability(self, format_name, start_date, end_date):
        """Check if data is available in caches for the specified period."""
        logger.info(f"Checking data availability for {format_name} from {start_date} to {end_date}...")
        
        raw_cache_dir = os.path.join(self.base_dir, "data-collection", "raw-cache")
        processed_cache_dir = os.path.join(self.base_dir, "data-collection", "processed-cache")
        
        # Check if cache directories exist
        if not os.path.exists(raw_cache_dir):
            logger.info("Raw cache directory not found. Data collection needed.")
            return False
        
        if not os.path.exists(processed_cache_dir):
            logger.info("Processed cache directory not found. Data collection needed.")
            return False
        
        # Simple check: if we have any recent data files, assume we have some data
        # In a more sophisticated implementation, we would check date ranges and formats
        raw_files = [f for f in os.listdir(raw_cache_dir) if f.endswith('.json')]
        processed_files = [f for f in os.listdir(processed_cache_dir) if f.endswith('.json')]
        
        if len(raw_files) == 0 or len(processed_files) == 0:
            logger.info("No data files found in caches. Data collection needed.")
            return False
        
        logger.info(f"Found {len(raw_files)} raw files and {len(processed_files)} processed files.")
        
        # For now, assume we need fresh data if we're asking for recent data
        # In a production system, we would implement more sophisticated date checking
        days = self._calculate_days_between(start_date, end_date)
        if days and days <= 30:  # If asking for data from last 30 days, collect fresh data
            logger.info("Recent data requested. Will collect fresh data to ensure completeness.")
            return False
        
        logger.info("Existing data found. Skipping data collection.")
        return True
    
    def _run_command(self, command, description, cwd=None):
        """Run a shell command and handle errors."""
        logger.info(f"Running: {description}")
        logger.debug(f"Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.base_dir,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✅ {description} completed successfully")
            if result.stdout:
                logger.debug(f"Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {description} failed with exit code {e.returncode}")
            if e.stdout:
                logger.error(f"Stdout: {e.stdout}")
            if e.stderr:
                logger.error(f"Stderr: {e.stderr}")
            return False
        except FileNotFoundError as e:
            logger.error(f"❌ Command not found: {e}")
            return False
    
    def _collect_mtgo_data(self, format_name, days):
        """Collect data from MTGO."""
        logger.info(f"Collecting MTGO data for {format_name} (last {days} days)...")
        
        mtgo_script = os.path.join(self.base_dir, "data-collection", "scraper", "mtgo", "main.py")
        if not os.path.exists(mtgo_script):
            logger.warning("MTGO scraper not found. Skipping MTGO data collection.")
            return True
        
        command = ["python3", mtgo_script, "--format", format_name, "--days", str(days)]
        return self._run_command(command, f"MTGO data collection for {format_name}")
    
    def _collect_mtgmelee_data(self, format_name, days):
        """Collect data from MTGMelee."""
        logger.info(f"Collecting MTGMelee data for {format_name} (last {days} days)...")
        
        mtgmelee_script = os.path.join(self.base_dir, "data-collection", "scraper", "mtgmelee", "main.py")
        if not os.path.exists(mtgmelee_script):
            logger.warning("MTGMelee scraper not found. Skipping MTGMelee data collection.")
            return True
        
        command = ["python3", mtgmelee_script, "--format", format_name, "--days", str(days)]
        return self._run_command(command, f"MTGMelee data collection for {format_name}")
    
    def _process_data(self, format_name):
        """Process and categorize the collected data."""
        logger.info(f"Processing data for {format_name}...")
        
        parser_script = os.path.join(self.base_dir, "data-treatment", "parser", "main.py")
        if not os.path.exists(parser_script):
            logger.warning("Data parser not found. Skipping data processing.")
            return True
        
        command = ["python3", parser_script, "--format", format_name]
        return self._run_command(command, f"Data processing for {format_name}")
    
    def _generate_visualizations(self, format_name, output_dir):
        """Generate visualizations and analysis."""
        logger.info(f"Generating visualizations for {format_name}...")
        
        r_script = os.path.join(self.base_dir, "visualization", "r-analysis", "generate_matrix.R")
        if not os.path.exists(r_script):
            logger.warning("R visualization script not found. Skipping visualization generation.")
            return True
        
        command = ["Rscript", r_script, "--format", format_name, "--output", output_dir]
        return self._run_command(command, f"Visualization generation for {format_name}")
    
    def _create_analysis_report(self, format_name, start_date, end_date, output_dir):
        """Create an HTML analysis report."""
        logger.info("Creating analysis report...")
        
        report_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MTG Analytics Report - {format_name.title()}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .info-box {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .visualization {{
            text-align: center;
            margin: 30px 0;
        }}
        .visualization img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>MTG Analytics Report - {format_name.title()} Format</h1>
        
        <div class="info-box">
            <h2>Analysis Details</h2>
            <p><strong>Format:</strong> {format_name.title()}</p>
            <p><strong>Analysis Period:</strong> {start_date} to {end_date}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Analysis ID:</strong> {self.analysis_timestamp}</p>
        </div>
        
        <div class="visualization">
            <h2>Matchup Matrix</h2>
            <p>This matrix shows win rates between different archetypes.</p>
            <img src="matchup_matrix.png" alt="Matchup Matrix" style="max-width: 100%; height: auto;">
        </div>
        
        <div class="visualization">
            <h2>Metagame Breakdown</h2>
            <p>This chart shows the popularity of each archetype in the format.</p>
            <img src="metagame_breakdown.png" alt="Metagame Breakdown" style="max-width: 100%; height: auto;">
        </div>
        
        <div class="info-box">
            <h2>Data Sources</h2>
            <ul>
                <li>MTGO Tournament Results</li>
                <li>MTGMelee Tournament Data</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by MTG Analytics Pipeline</p>
            <p>Analysis timestamp: {self.analysis_timestamp}</p>
        </div>
    </div>
</body>
</html>
        """
        
        report_path = os.path.join(output_dir, "analysis_report.html")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Analysis report created: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Failed to create analysis report: {e}")
            return None
    
    def _open_in_browser(self, file_path):
        """Open the analysis report in the default web browser."""
        try:
            file_url = f"file://{os.path.abspath(file_path)}"
            webbrowser.open(file_url)
            logger.info(f"Opening analysis report in browser: {file_url}")
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
    
    def run_analysis(self, format_name, start_date, end_date):
        """Run the complete analysis pipeline."""
        logger.info(f"🚀 Starting MTG Analytics Pipeline")
        logger.info(f"Format: {format_name}")
        logger.info(f"Period: {start_date} to {end_date}")
        
        # Calculate days for data collection
        days = self._calculate_days_between(start_date, end_date)
        if days is None:
            logger.error("Invalid date range. Aborting analysis.")
            return False
        
        logger.info(f"Analysis period: {days} days")
        
        # Create output directory
        analyses_dir = os.path.join(self.base_dir, "analyses")
        analysis_dir = os.path.join(analyses_dir, f"{format_name}_{self.analysis_timestamp}")
        os.makedirs(analysis_dir, exist_ok=True)
        logger.info(f"Analysis output directory: {analysis_dir}")
        
        # Step 1: Check data availability
        data_available = self._check_data_availability(format_name, start_date, end_date)
        
        # Step 2: Collect data if needed
        if not data_available:
            logger.info("📥 Data collection phase")
            
            # Collect MTGO data
            if not self._collect_mtgo_data(format_name, days):
                logger.warning("MTGO data collection failed, but continuing...")
            
            # Collect MTGMelee data
            if not self._collect_mtgmelee_data(format_name, days):
                logger.warning("MTGMelee data collection failed, but continuing...")
        else:
            logger.info("📋 Using existing cached data")
        
        # Step 3: Process data
        logger.info("⚙️ Data processing phase")
        if not self._process_data(format_name):
            logger.error("Data processing failed. Aborting analysis.")
            return False
        
        # Step 4: Generate visualizations
        logger.info("📊 Visualization generation phase")
        if not self._generate_visualizations(format_name, analysis_dir):
            logger.warning("Visualization generation failed, but continuing...")
        
        # Step 5: Create analysis report
        logger.info("📄 Creating analysis report")
        report_path = self._create_analysis_report(format_name, start_date, end_date, analysis_dir)
        
        # Step 6: Open in browser
        if report_path:
            logger.info("🌐 Opening analysis in browser")
            self._open_in_browser(report_path)
        
        logger.info(f"✅ Analysis completed successfully!")
        logger.info(f"📁 Results saved to: {analysis_dir}")
        
        return True

def main():
    """Main function to run the orchestrator."""
    parser = argparse.ArgumentParser(
        description="MTG Analytics Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze Standard from July 1st to today
  python orchestrator.py --format standard --start-date 2024-07-01 --end-date 2024-07-22
  
  # Analyze Modern for the last month
  python orchestrator.py --format modern --start-date 2024-06-22 --end-date 2024-07-22
        """
    )
    
    parser.add_argument(
        "--format",
        required=True,
        choices=["standard", "modern", "pioneer", "legacy", "vintage", "pauper"],
        help="MTG format to analyze"
    )
    
    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date for analysis (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "--end-date",
        required=True,
        help="End date for analysis (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run orchestrator
    orchestrator = MTGAnalyticsOrchestrator()
    success = orchestrator.run_analysis(args.format, args.start_date, args.end_date)
    
    if success:
        logger.info("🎉 Pipeline completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()