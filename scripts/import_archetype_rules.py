#!/usr/bin/env python3
"""
Import archetype rules from MTGOFormatData repository.
This script downloads all Standard archetype definitions AND card colors.
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

class ArchetypeRulesImporter:
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/Badaro/MTGOFormatData/master"
        self.standard_url = f"{self.base_url}/Formats/Standard"
        self.output_dir = Path("data/archetype_rules")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_archetype_list(self):
        """Get list of all archetype files from GitHub API"""
        api_url = "https://api.github.com/repos/Badaro/MTGOFormatData/contents/Formats/Standard/Archetypes"
        response = requests.get(api_url)
        if response.status_code == 200:
            return [f['name'] for f in response.json() if f['name'].endswith('.json')]
        return []
    
    def download_archetype(self, filename):
        """Download a single archetype definition"""
        url = f"{self.standard_url}/Archetypes/{filename}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def download_special_files(self):
        """Download color_overrides.json and metas.json"""
        standard_dir = self.output_dir / "standard"
        standard_dir.mkdir(exist_ok=True)
        
        special_files = ['color_overrides.json', 'metas.json']
        
        for filename in special_files:
            url = f"{self.standard_url}/{filename}"
            response = requests.get(url)
            if response.status_code == 200:
                output_path = standard_dir / filename
                with open(output_path, 'w') as f:
                    json.dump(response.json(), f, indent=2)
                print(f"✓ Downloaded {filename}")
    
    def download_card_colors(self):
        """Download the global card_colors.json file"""
        url = f"{self.base_url}/Formats/card_colors.json"
        response = requests.get(url)
        if response.status_code == 200:
            output_path = self.output_dir / "card_colors.json"
            with open(output_path, 'w') as f:
                json.dump(response.json(), f, indent=2)
            print(f"✓ Downloaded card_colors.json (color detection database)")
    
    def import_all_rules(self):
        """Import all archetype rules from MTGOFormatData"""
        print("🎯 Starting archetype rules import...")
        
        # Download card colors database FIRST
        self.download_card_colors()
        
        # Download special files
        self.download_special_files()
        
        # Create archetypes subdirectory
        standard_dir = self.output_dir / "standard"
        archetypes_dir = standard_dir / "archetypes"
        archetypes_dir.mkdir(exist_ok=True)
        
        # Get list of archetypes
        archetype_files = self.fetch_archetype_list()
        print(f"📊 Found {len(archetype_files)} archetype definitions")
        
        # Download each archetype
        success_count = 0
        for filename in archetype_files:
            archetype_data = self.download_archetype(filename)
            if archetype_data:
                output_path = archetypes_dir / filename
                with open(output_path, 'w') as f:
                    json.dump(archetype_data, f, indent=2)
                success_count += 1
                print(f"✓ {filename}")
            else:
                print(f"✗ Failed to download {filename}")
        
        # Create summary
        summary = {
            "imported_at": datetime.now().isoformat(),
            "source": "github.com/Badaro/MTGOFormatData",
            "format": "Standard",
            "total_archetypes": success_count,
            "archetype_files": archetype_files
        }
        
        with open(self.output_dir / "import_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Import complete! {success_count}/{len(archetype_files)} archetypes imported")
        print(f"📁 Saved to: {self.output_dir}")
        print(f"🎨 Card colors database downloaded")
        print(f"📋 Standard format rules ready")
        
        return success_count

if __name__ == "__main__":
    importer = ArchetypeRulesImporter()
    importer.import_all_rules()