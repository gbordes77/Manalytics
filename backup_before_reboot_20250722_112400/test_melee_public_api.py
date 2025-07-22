#!/usr/bin/env python3
"""
Test de l'API publique Melee avec l'endpoint correct
"""

import json
from datetime import datetime, timezone

import requests


def test_melee_public_api():
    """Test de l'API publique Melee"""

    # Configuration
    start_date = datetime(2025, 7, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 7, 20, tzinfo=timezone.utc)

    # URL correcte basée sur Badaro
    url = "https://melee.gg/Decklist/TournamentSearch"

    # Paramètres basés sur Badaro
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
        "length": "25",
        "search[value]": "",
        "search[regex]": "false",
        "q": "",
        "startDate": f"{start_date.strftime('%Y-%m-%d')}T00%3A00%3A00.000Z",
        "endDate": f"{end_date.strftime('%Y-%m-%d')}T23%3A59%3A59.999Z",
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

    print("🔍 Test de l'API publique Melee...")
    print(f"URL: {url}")
    print(
        f"Période: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}"
    )

    try:
        response = requests.post(url, data=params, headers=headers)

        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response length: {len(response.text)}")
        print(f"Response preview: {response.text[:500]}...")

        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                print(f"✅ JSON valide")
                print(f"Keys: {list(data.keys())}")
                if "data" in data:
                    print(f"Nombre de tournois: {len(data['data'])}")
                    if data["data"]:
                        print(
                            f"Premier tournoi: {json.dumps(data['data'][0], indent=2)}"
                        )

                        # Filtrage Standard
                        standard_count = 0
                        for tournament in data["data"]:
                            format_desc = tournament.get("Format", "").lower()
                            if "standard" in format_desc:
                                standard_count += 1
                        print(f"Tournois Standard: {standard_count}")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur JSON: {e}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")

    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_melee_public_api()
