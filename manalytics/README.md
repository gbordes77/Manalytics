# MTG Analytics Pipeline

A pipeline for collecting, processing, and visualizing Magic: The Gathering tournament data.

## Overview

This project consolidates several existing tools to create a complete pipeline for analyzing Magic: The Gathering tournament data. It allows collecting data from MTGO and MTGMelee platforms, processing it to categorize decks by archetypes, and generating visualizations to analyze the metagame.

## Core Rules

- **ALWAYS USE REAL DATA**: Never use example or mock data. All analyses must be based on real tournament data from MTGO and MTGMelee.
- **PRESERVE CODE INTEGRITY**: Always maintain the original functionality of the source repositories.
- **DOCUMENT ALL DECISIONS**: Maintain complete traceability of technical choices.
- **RESPECT RATE LIMITS**: Always adhere to the rate limits of the data sources to avoid being blocked.

## Architecture

The pipeline is organized into three main phases:

1. **Data Collection**: Extraction of tournament data from MTGO and MTGMelee
2. **Data Processing**: Categorization of decks by archetypes according to defined rules
3. **Visualization**: Generation of matchup matrices and other visualizations

## Project Structure

```
manalytics/
├── data-collection/
│   ├── scraper/               # mtg_decklist_scrapper
│   │   ├── mtgo/             # Original MTGO code
│   │   └── mtgmelee/         # MTGMelee API extension
│   ├── raw-cache/            # MTG_decklistcache
│   └── processed-cache/      # MTGODecklistCache
├── data-treatment/
│   ├── parser/               # MTGOArchetypeParser
│   └── format-rules/         # MTGOFormatData
├── visualization/
│   └── r-analysis/           # R-Meta-Analysis
├── config/
│   └── sources.json          # Data sources configuration
├── data/                     # Generated data
└── docs/                     # Documentation
```

## Installation

### Prerequisites

- Git
- Python 3.8+
- R 4.0+ (for visualization)

### Automatic Installation

#### For Unix/Linux/macOS

```bash
./setup.sh
```

#### For Windows

```powershell
.\setup.ps1
```

These scripts will:
1. Clone the 6 required GitHub repositories
2. Place them in the appropriate folder structure
3. Generate an installation report

### Manual Installation

If you prefer to install manually, follow these steps:

1. Clone this repository
2. Clone the following repositories into the corresponding folders:
   - [mtg_decklist_scrapper](https://github.com/fbettega/mtg_decklist_scrapper) → data-collection/scraper/mtgo
   - [MTG_decklistcache](https://github.com/fbettega/MTG_decklistcache) → data-collection/raw-cache
   - [MTGODecklistCache](https://github.com/Jiliac/MTGODecklistCache) → data-collection/processed-cache
   - [MTGOArchetypeParser](https://github.com/Badaro/MTGOArchetypeParser) → data-treatment/parser
   - [MTGOFormatData](https://github.com/Badaro/MTGOFormatData) → data-treatment/format-rules
   - [R-Meta-Analysis](https://github.com/Jiliac/R-Meta-Analysis) → visualization/r-analysis

## Configuration

Before using the pipeline, you need to configure the data sources in the `config/sources.json` file. This file contains:

- MTGO URLs to scrape
- MTGMelee API endpoints
- Configuration parameters for scraping and API

For the MTGMelee API, you'll need to add your credentials in a `config/credentials.json` file (not included for security reasons).

## Usage

### Quick Analysis (Recommended)

The easiest way to run a complete analysis is using the orchestrator:

#### Interactive Mode

```bash
# Launch the interactive analyzer
python analyze.py
```

This will guide you through selecting a format and date range, then automatically run the entire pipeline.

#### Command Line Mode

```bash
# Analyze Standard from July 1st to today
python orchestrator.py --format standard --start-date 2024-07-01 --end-date 2024-07-22

# Analyze Modern for the last 30 days
python orchestrator.py --format modern --start-date 2024-06-22 --end-date 2024-07-22

# Analyze Pioneer with verbose output
python orchestrator.py --format pioneer --start-date 2024-07-01 --end-date 2024-07-22 --verbose
```

The orchestrator will:
1. Check if data is available in caches
2. Collect fresh data from MTGO and MTGMelee if needed
3. Process and categorize the data
4. Generate visualizations and analysis
5. Create an HTML report
6. Automatically open the results in your browser

Results are saved in the `analyses/` folder with timestamps.

### Manual Pipeline Execution

If you prefer to run individual components:

#### 1. Data Collection

##### From MTGO

```bash
# Collect Standard data from the last 7 days
python data-collection/scraper/mtgo/main.py --format standard --days 7

# Collect Modern data from the last 7 days
python data-collection/scraper/mtgo/main.py --format modern --days 7
```

##### From MTGMelee

```bash
# Collect Standard data from the last 7 days
python data-collection/scraper/mtgmelee/main.py --format standard --days 7

# Collect Modern data from the last 7 days
python data-collection/scraper/mtgmelee/main.py --format modern --days 7
```

#### 2. Data Processing

```bash
# Process Standard data
python data-treatment/parser/main.py --format standard

# Process Modern data
python data-treatment/parser/main.py --format modern
```

#### 3. Visualization

```bash
# Generate a matchup matrix for Standard
Rscript visualization/r-analysis/generate_matrix.R --format standard

# Generate a matchup matrix for Modern
Rscript visualization/r-analysis/generate_matrix.R --format modern
```

## Documentation

For more information, check the documentation in the `docs/` folder:

- [Architecture](docs/ARCHITECTURE.md): Detailed description of the architecture
- [Data Formats](docs/DATA_FORMATS.md): Description of data formats
- [Quick Start Guide](docs/QUICKSTART.md): Guide to get started quickly

## Troubleshooting

### Why scripts might not work while they work for Jiliac

The scripts may not work immediately for several reasons:

1. **Environment differences**: Jiliac's environment might have specific configurations, paths, or dependencies that are not present in your environment.

2. **Missing credentials**: Some scripts require API credentials or tokens that Jiliac has configured but are not included in the public repositories.

3. **Path configurations**: The original scripts might have hardcoded paths that work in Jiliac's environment but need to be adjusted for your setup.

4. **Version differences**: Different versions of Python, R, or dependencies can cause compatibility issues.

5. **Integration points**: The repositories were originally designed to work independently, not as part of a unified pipeline.

To resolve these issues:
- Check the logs for specific error messages
- Verify that all dependencies are installed
- Ensure paths are correctly configured for your environment
- Make sure all required credentials are properly set up

## Credits

This project integrates the following repositories:

- [mtg_decklist_scrapper](https://github.com/fbettega/mtg_decklist_scrapper) by fbettega
- [MTG_decklistcache](https://github.com/fbettega/MTG_decklistcache) by fbettega
- [MTGODecklistCache](https://github.com/Jiliac/MTGODecklistCache) by Jiliac
- [MTGOArchetypeParser](https://github.com/Badaro/MTGOArchetypeParser) by Badaro
- [MTGOFormatData](https://github.com/Badaro/MTGOFormatData) by Badaro
- [R-Meta-Analysis](https://github.com/Jiliac/R-Meta-Analysis) by Jiliac (fork of Aliquanto3)