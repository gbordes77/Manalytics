#!/usr/bin/env python3
"""
Quick launcher for our reference visualization.
This ensures we keep easy access to our standard visualization.
"""

from src.manalytics.visualizers import create_standard_analysis_visualization

if __name__ == "__main__":
    print("🎨 Generating Standard Analysis Visualization...")
    create_standard_analysis_visualization()
    print("✅ Done! Check data/cache/standard_analysis_no_leagues.html")