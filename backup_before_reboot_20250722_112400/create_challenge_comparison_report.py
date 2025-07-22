#!/usr/bin/env python3
"""
Rapport comparatif des Challenges MTGO
Compare nos données scrapées avec la liste fournie
"""

import json
import re
from datetime import datetime
from pathlib import Path


def extract_challenges_from_list():
    """Extrait les Challenges de la liste fournie"""

    # Liste fournie par l'utilisateur
    challenge_list = [
        "Standard Challenge 64 2025-07-01 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0112801190",
        "Standard Challenge 32 2025-07-03 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0312801623",
        "Standard Challenge 32 2025-07-04 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0412801637",
        "Standard Challenge 32 2025-07-05 - https://www.mtgo.com/decklist/standard-challenge-32-2025-05-2512801654",
        "Standard Challenge 32 2025-07-06 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-0612801677",
        "Standard Challenge 64 2025-07-07 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0712801688",
        "Standard Challenge 64 2025-07-08 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-0812801696",
        "Standard Challenge 32 2025-07-10 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1012802771",
        "Standard Challenge 32 2025-07-11 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1112802789",
        "Standard Challenge 32 2025-07-12 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1212802811",
        "Standard Challenge 32 2025-07-13 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1312802841",
        "Standard Challenge 64 2025-07-14 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-1412802856",
        "Standard Challenge 64 2025-07-15 - https://www.mtgo.com/decklist/standard-challenge-64-2025-07-1512802868",
        "Standard Challenge 32 2025-07-17 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1712803657",
        "Standard Challenge 32 2025-07-18 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1812803671",
        "Standard Challenge 32 2025-07-19 - https://www.mtgo.com/decklist/standard-challenge-32-2025-07-1912803688",
    ]

    parsed_challenges = []

    for line in challenge_list:
        # Extraire les informations
        match = re.match(
            r"(Standard Challenge \d+) (\d{4}-\d{2}-\d{2}) - (https://www\.mtgo\.com/decklist/.*?)(\d+)$",
            line,
        )
        if match:
            name = match.group(1)
            date = match.group(2)
            base_url = match.group(3)
            id_num = match.group(4)

            parsed_challenges.append(
                {
                    "name": name,
                    "date": date,
                    "url": base_url + id_num,
                    "id": id_num,
                    "source": "liste_fournie",
                }
            )

    return parsed_challenges


def load_scraped_challenges():
    """Charge les Challenges de nos données scrapées"""

    mtgo_file = Path("data/processed/mtgo_standard_july_2025.json")
    with open(mtgo_file, "r", encoding="utf-8") as f:
        mtgo_data = json.load(f)

    scraped_challenges = []

    for tournament_entry in mtgo_data:
        tournament = tournament_entry.get("tournament", {})
        name = tournament.get("Name", "")

        if "Challenge" in name:
            # Extraire l'ID de l'URI
            uri = tournament.get("Uri", "")
            id_match = re.search(r"(\d+)$", uri)
            id_num = id_match.group(1) if id_match else "unknown"

            scraped_challenges.append(
                {
                    "name": name,
                    "date": tournament.get("Date", ""),
                    "url": uri,
                    "id": id_num,
                    "deck_count": len(tournament_entry.get("decks", [])),
                    "source": "scraped",
                }
            )

    return scraped_challenges


def create_comparison_html():
    """Crée le rapport HTML comparatif"""

    # Charger les données
    liste_challenges = extract_challenges_from_list()
    scraped_challenges = load_scraped_challenges()

    # Créer des dictionnaires pour faciliter la comparaison
    liste_dict = {(c["name"], c["date"], c["id"]): c for c in liste_challenges}
    scraped_dict = {(c["name"], c["date"], c["id"]): c for c in scraped_challenges}

    # Trouver les différences
    only_in_liste = set(liste_dict.keys()) - set(scraped_dict.keys())
    only_in_scraped = set(scraped_dict.keys()) - set(liste_dict.keys())
    common = set(liste_dict.keys()) & set(scraped_dict.keys())

    # Générer le HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Comparatif Challenges MTGO - Standard Juillet 2025</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
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
        .summary {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .summary h2 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        .challenge-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .challenge-table th, .challenge-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .challenge-table th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        .challenge-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .challenge-table tr:hover {{
            background-color: #e8f4f8;
        }}
        .url-link {{
            color: #3498db;
            text-decoration: none;
        }}
        .url-link:hover {{
            text-decoration: underline;
        }}
        .missing {{
            background-color: #ffebee;
            border-left: 4px solid #f44336;
        }}
        .extra {{
            background-color: #e8f5e8;
            border-left: 4px solid #4caf50;
        }}
        .common {{
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }}
        .alert {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .date-group {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            background: #f8f9fa;
        }}
        .date-header {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Rapport Comparatif Challenges MTGO - Standard Juillet 2025</h1>

        <div class="summary">
            <h2>📊 Résumé de la Comparaison</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(liste_challenges)}</div>
                    <div class="stat-label">Challenges dans la liste</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(scraped_challenges)}</div>
                    <div class="stat-label">Challenges scrapées</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(common)}</div>
                    <div class="stat-label">Challenges communes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(only_in_liste)}</div>
                    <div class="stat-label">Manquantes dans scraped</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(only_in_scraped)}</div>
                    <div class="stat-label">En plus dans scraped</div>
                </div>
            </div>
        </div>

        <div class="alert">
            <strong>⚠️ Note importante :</strong> Ce rapport compare les Challenges de la liste fournie avec celles récupérées par notre scraper.
            Les différences peuvent indiquer des Challenges multiples par jour ou des problèmes de scraping.
        </div>

        <div class="section">
            <h3>🎯 Challenges Communes ({len(common)})</h3>
            <p>Challenges présentes dans les deux sources :</p>
            <table class="challenge-table">
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Date</th>
                        <th>ID</th>
                        <th>URL</th>
                        <th>Decks (scraped)</th>
                    </tr>
                </thead>
                <tbody>
    """

    for key in sorted(common):
        name, date, id_num = key
        scraped = scraped_dict[key]
        html_content += f"""
                    <tr class="common">
                        <td>{name}</td>
                        <td>{date}</td>
                        <td>{id_num}</td>
                        <td><a href="{scraped['url']}" class="url-link" target="_blank">Voir</a></td>
                        <td>{scraped['deck_count']}</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h3>❌ Challenges Manquantes dans Scraped ({len(only_in_liste)})</h3>
            <p>Challenges dans la liste mais pas dans nos données scrapées :</p>
            <table class="challenge-table">
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Date</th>
                        <th>ID</th>
                        <th>URL</th>
                    </tr>
                </thead>
                <tbody>
    """

    for key in sorted(only_in_liste):
        name, date, id_num = key
        liste = liste_dict[key]
        html_content += f"""
                    <tr class="missing">
                        <td>{name}</td>
                        <td>{date}</td>
                        <td>{id_num}</td>
                        <td><a href="{liste['url']}" class="url-link" target="_blank">Voir</a></td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h3>➕ Challenges En Plus dans Scraped ({len(only_in_scraped)})</h3>
            <p>Challenges dans nos données scrapées mais pas dans la liste :</p>
            <table class="challenge-table">
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Date</th>
                        <th>ID</th>
                        <th>URL</th>
                        <th>Decks</th>
                    </tr>
                </thead>
                <tbody>
    """

    for key in sorted(only_in_scraped):
        name, date, id_num = key
        scraped = scraped_dict[key]
        html_content += f"""
                    <tr class="extra">
                        <td>{name}</td>
                        <td>{date}</td>
                        <td>{id_num}</td>
                        <td><a href="{scraped['url']}" class="url-link" target="_blank">Voir</a></td>
                        <td>{scraped['deck_count']}</td>
                    </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h3>📅 Analyse par Jour</h3>
    """

    # Grouper par date
    all_dates = set()
    for key in liste_dict.keys():
        all_dates.add(key[1])
    for key in scraped_dict.keys():
        all_dates.add(key[1])

    for date in sorted(all_dates):
        liste_for_date = [k for k in liste_dict.keys() if k[1] == date]
        scraped_for_date = [k for k in scraped_dict.keys() if k[1] == date]

        html_content += f"""
            <div class="date-group">
                <div class="date-header">📅 {date}</div>
                <p><strong>Liste :</strong> {len(liste_for_date)} Challenge(s)</p>
                <p><strong>Scraped :</strong> {len(scraped_for_date)} Challenge(s)</p>
        """

        if len(liste_for_date) != len(scraped_for_date):
            html_content += f"""
                <p style="color: #e74c3c;"><strong>⚠️ Différence détectée !</strong></p>
            """

        html_content += """
            </div>
        """

    html_content += (
        """
        </div>

        <div class="section">
            <h3>📋 Données Techniques</h3>
            <p><strong>Date de génération :</strong> """
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + """</p>
            <p><strong>Période analysée :</strong> 2025-07-01 à 2025-07-20</p>
            <p><strong>Format :</strong> Standard</p>
            <p><strong>Source liste :</strong> Liste fournie par l'utilisateur</p>
            <p><strong>Source scraped :</strong> Données récupérées par notre scraper MTGO</p>
        </div>
    </div>
</body>
</html>
    """
    )

    # Sauvegarder le fichier
    output_file = Path("challenge_comparison_report.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_file


def main():
    """Fonction principale"""
    try:
        output_file = create_comparison_html()
        print(f"✅ Rapport généré : {output_file}")

        # Ouvrir dans le navigateur
        import webbrowser

        webbrowser.open(f"file://{output_file.absolute()}")

    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
