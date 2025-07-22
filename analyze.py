#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick launcher for MTG Analytics Pipeline
This script provides a simplified interface to run analyses.
"""

import sys
import subprocess
from datetime import datetime, timedelta

def main():
    print("🃏 MTG Analytics Pipeline - Quick Launcher")
    print("=" * 50)
    
    # Get format
    print("\nAvailable formats:")
    formats = ["standard", "modern", "pioneer", "legacy", "vintage", "pauper"]
    for i, fmt in enumerate(formats, 1):
        print(f"  {i}. {fmt.title()}")
    
    while True:
        try:
            choice = input("\nSelect format (1-6): ").strip()
            format_idx = int(choice) - 1
            if 0 <= format_idx < len(formats):
                selected_format = formats[format_idx]
                break
            else:
                print("Invalid choice. Please select 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Get date range
    print(f"\n📅 Date Range for {selected_format.title()} Analysis")
    print("Choose an option:")
    print("  1. Last 7 days")
    print("  2. Last 30 days")
    print("  3. Since July 1st, 2024")
    print("  4. Custom date range")
    
    while True:
        try:
            date_choice = input("\nSelect date range (1-4): ").strip()
            today = datetime.now()
            
            if date_choice == "1":
                start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
                break
            elif date_choice == "2":
                start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
                break
            elif date_choice == "3":
                start_date = "2024-07-01"
                end_date = today.strftime("%Y-%m-%d")
                break
            elif date_choice == "4":
                start_date = input("Enter start date (YYYY-MM-DD): ").strip()
                end_date = input("Enter end date (YYYY-MM-DD): ").strip()
                
                # Validate date format
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.strptime(end_date, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    continue
            else:
                print("Invalid choice. Please select 1-4.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            sys.exit(0)
    
    # Confirm and run
    print(f"\n🔍 Analysis Configuration:")
    print(f"  Format: {selected_format.title()}")
    print(f"  Start Date: {start_date}")
    print(f"  End Date: {end_date}")
    
    confirm = input("\nProceed with analysis? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Analysis cancelled.")
        sys.exit(0)
    
    # Run the orchestrator
    print(f"\n🚀 Starting analysis...")
    print("This may take several minutes depending on the amount of data to process.")
    
    try:
        cmd = [
            sys.executable, "orchestrator.py",
            "--format", selected_format,
            "--start-date", start_date,
            "--end-date", end_date,
            "--verbose"
        ]
        
        result = subprocess.run(cmd, check=True)
        print("\n✅ Analysis completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Analysis failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Analysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()