#!/usr/bin/env python3
"""
Test de l'API Melee pour voir tous les formats disponibles
"""

import json
from datetime import datetime, timezone

import requests


def test_melee_all_formats():
    """Test de l'API Melee pour tous les formats"""

    # Configuration - période plus large
    start_date = datetime(2025, 6, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 7, 20, tzinfo=timezone.utc)

    # URL
    url = "https://melee.gg/Decklist/TournamentSearch"

    # Paramètres
    params = {
        "draw": "1",
        "columns[0][data]": "ID",
        "columns[0][name]": "ID",
        "columns[0][searchable]": "false",
        "columns[0][orderable]": "false",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "Name",
        "columns[1][name]": "Name",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "StartDate",
        "columns[2][name]": "StartDate",
        "columns[2][searchable]": "false",
        "columns[2][orderable]": "true",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "Status",
        "columns[3][name]": "Status",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "columns[4][data]": "Format",
        "columns[4][name]": "Format",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "true",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",
        "columns[5][data]": "OrganizationName",
        "columns[5][name]": "OrganizationName",
        "columns[5][searchable]": "true",
        "columns[5][orderable]": "true",
        "columns[5][search][value]": "",
        "columns[5][search][regex]": "false",
        "columns[6][data]": "Decklists",
        "columns[6][name]": "Decklists",
        "columns[6][searchable]": "true",
        "columns[6][orderable]": "true",
        "columns[6][search][value]": "",
        "columns[6][search][regex]": "false",
        "order[0][column]": "2",
        "order[0][dir]": "desc",
        "start": "0",
        "length": "100",  # Plus de résultats
        "search[value]": "",
        "search[regex]": "false",
        "q": "",
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
    }

    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }

    print("🔍 Test de l'API Melee - Tous formats...")
    print(
        f"Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
    )

    try:
        response = requests.post(url, data=params, headers=headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            print(f"✅ JSON valide")
            print(f"Nombre total de tournois: {data.get('recordsFiltered', 0)}")
            print(f"Tournois dans cette page: {len(data.get('data', []))}")

            # Analyse des formats
            formats = {}
            for tournament in data.get("data", []):
                format_desc = tournament.get("FormatDescription", "Unknown")
                if format_desc not in formats:
                    formats[format_desc] = 0
                formats[format_desc] += 1

            print(f"\n📊 Formats trouvés:")
            for format_name, count in sorted(formats.items()):
                print(f"  • {format_name}: {count} tournois")

            # Affichage des premiers tournois
            print(f"\n📋 Premiers tournois:")
            for i, tournament in enumerate(data.get("data", [])[:5]):
                print(
                    f"  {i+1}. {tournament.get('Name', 'Unknown')} - {tournament.get('FormatDescription', 'Unknown')} - {tournament.get('StartDate', 'Unknown')}"
                )

        else:
            print(f"❌ Erreur HTTP: {response.status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_melee_all_formats()
