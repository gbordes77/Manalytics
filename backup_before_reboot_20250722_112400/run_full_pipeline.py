#!/usr/bin/env python3
"""
Script to run the complete pipeline with integrated visualizations
"""

import argparse
import asyncio
import logging
import os
import sys
import webbrowser
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append("src")

from src.orchestrator import ManalyticsOrchestrator


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("pipeline.log")],
    )


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Manalytics complete pipeline")
    parser.add_argument(
        "--format",
        default="Standard",
        choices=["Standard", "Modern", "Legacy", "Pioneer", "Pauper"],
        help="Tournament format to analyze",
    )
    parser.add_argument(
        "--start-date", default="2025-07-02", help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date", default="2025-07-12", help="End date (YYYY-MM-DD)"
    )
    return parser.parse_args()


async def main():
    """Run the complete pipeline"""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("🚀 STARTING MANALYTICS COMPLETE PIPELINE")

        # Parse arguments
        args = parse_arguments()

        format_name = args.format
        start_date = args.start_date
        end_date = args.end_date

        logger.info(f"📅 Period: {start_date} to {end_date}")
        logger.info(f"🎯 Format: {format_name}")

        # Create orchestrator
        orchestrator = ManalyticsOrchestrator()

        # Run complete pipeline
        result = await orchestrator.run_pipeline(format_name, start_date, end_date)

        logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("📊 All visualizations have been generated automatically")

        # Use main filename from result
        main_filename = result["main_filename"]
        logger.info(
            f"🌐 Open {result['analysis_folder']}/{main_filename} to view results"
        )

        # NEW: Automatically open dashboard in browser
        dashboard_path = os.path.join(
            "Analyses", result["analysis_folder"], main_filename
        )
        absolute_path = os.path.abspath(dashboard_path)
        analysis_folder_path = os.path.abspath(
            os.path.join("Analyses", result["analysis_folder"])
        )

        logger.info(f"🚀 Automatically opening dashboard: {absolute_path}")

        try:
            # Open in default browser
            webbrowser.open(f"file://{absolute_path}")
            logger.info("✅ Dashboard opened in browser!")
        except Exception as e:
            logger.warning(f"⚠️ Could not automatically open dashboard: {e}")
            logger.info(f"📂 Open manually: {absolute_path}")

        # BONUS: Also open folder in file explorer
        try:
            import platform
            import time

            # Wait a bit to ensure all files are created
            time.sleep(1)

            system = platform.system()

            if system == "Darwin":  # macOS
                # Force opening of main folder, not subfolder
                os.system(f'open "{analysis_folder_path}"')
                # Wait a bit then select the index.html file
                time.sleep(0.5)
                os.system(f'open -R "{absolute_path}"')
                logger.info(
                    f"📂 Analysis folder opened in Finder: {analysis_folder_path}"
                )
            elif system == "Windows":  # Windows
                os.system(f'explorer "{analysis_folder_path}"')
                logger.info("📂 Analysis folder opened in Explorer!")
            elif system == "Linux":  # Linux
                os.system(f'xdg-open "{analysis_folder_path}"')
                logger.info("📂 Analysis folder opened in file explorer!")
        except Exception as e:
            logger.warning(f"⚠️ Could not automatically open folder: {e}")
            logger.info(f"📂 Open manually: {analysis_folder_path}")

        return result

    except Exception as e:
        logger.error(f"❌ PIPELINE ERROR: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return False

    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\n🎯 SUCCESS! Dashboard opened automatically!")
        print(f"📂 Folder: Analyses/{result['analysis_folder']}/")
        print(f"🌐 File: Analyses/{result['analysis_folder']}/{result['main_filename']}")
    else:
        print("\n❌ FAILURE! Check logs for more details")
    sys.exit(0 if result else 1)
