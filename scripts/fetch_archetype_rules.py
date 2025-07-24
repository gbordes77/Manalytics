import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from pathlib import Path
import click
import logging
import json

from config.settings import settings

logger = logging.getLogger(__name__)
BASE_URL = "https://raw.githubusercontent.com/Badaro/MTGOFormatData/master/Formats/"
FORMATS_TO_FETCH = ["standard", "modern", "pioneer", "legacy", "vintage", "pauper"]

# Files to fetch for each format
FORMAT_FILES = ["metas.json", "color_overrides.json"]

@click.command()
def fetch_rules():
    """
    Downloads the latest archetype rule files from the Badaro/MTGOFormatData GitHub repo
    and saves them to the seed_data directory.
    """
    click.echo("Downloading latest archetype rules...")
    output_dir = settings.RULES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with httpx.Client(timeout=30.0) as client:
        for format_name in FORMATS_TO_FETCH:
            # Create format directory
            format_dir = output_dir / format_name
            format_dir.mkdir(exist_ok=True)
            
            # Fetch metas.json and color_overrides.json for each format
            for file_name in FORMAT_FILES:
                url = f"{BASE_URL}{format_name.capitalize()}/{file_name}"
                try:
                    response = client.get(url)
                    response.raise_for_status()
                    
                    filepath = format_dir / file_name
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    click.echo(f"  -> Successfully downloaded {format_name}/{file_name}")
                except httpx.HTTPError as e:
                    click.echo(f"  -> ERROR downloading {format_name}/{file_name}: {e}")
            
            # Fetch archetypes directory listing
            archetypes_url = f"https://api.github.com/repos/Badaro/MTGOFormatData/contents/Formats/{format_name.capitalize()}/Archetypes"
            try:
                response = client.get(archetypes_url)
                if response.status_code == 200:
                    archetypes_dir = format_dir / "Archetypes"
                    archetypes_dir.mkdir(exist_ok=True)
                    
                    files = response.json()
                    for file_info in files[:10]:  # Limit to first 10 archetypes for testing
                        if file_info['name'].endswith('.json'):
                            file_url = file_info['download_url']
                            try:
                                file_response = client.get(file_url)
                                file_response.raise_for_status()
                                
                                filepath = archetypes_dir / file_info['name']
                                with open(filepath, 'w', encoding='utf-8') as f:
                                    f.write(file_response.text)
                                click.echo(f"  -> Downloaded archetype: {format_name}/Archetypes/{file_info['name']}")
                            except httpx.HTTPError as e:
                                click.echo(f"  -> ERROR downloading archetype {file_info['name']}: {e}")
            except Exception as e:
                click.echo(f"  -> Could not fetch archetypes for {format_name}: {e}")
    
    click.echo("Rule fetching complete.")

if __name__ == "__main__":
    fetch_rules()