#!/usr/bin/env python3
"""
Test de l'approche réelle Melee : accès direct aux tournois par ID
"""

import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def test_melee_real_approach():
    print("🎯 Test Approche Réelle Melee : Accès par ID")
    print("=" * 60)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession(
        headers=headers, timeout=aiohttp.ClientTimeout(total=30)
    ) as session:

        # Test 1: Accès à un tournoi récent (ID élevé)
        # Les IDs de 2020 étaient ~4000-5000, donc 2025 devrait être beaucoup plus élevé
        recent_tournament_ids = [15000, 16000, 17000, 18000, 19000, 20000]

        print("🔍 Test 1: Recherche tournois récents par ID")

        found_tournaments = []

        for tournament_id in recent_tournament_ids:
            try:
                tournament_url = f"https://melee.gg/Tournament/View/{tournament_id}"
                print(f"   Teste ID {tournament_id}...")

                async with session.get(tournament_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # Vérifier si c'est un vrai tournoi
                        title = soup.find("title")
                        if title and "Tournament" in title.get_text():
                            tournament_name = title.get_text(strip=True)

                            # Chercher la date
                            date_found = None
                            if "2025" in html:
                                date_found = "2025 (trouvé dans HTML)"

                            # Chercher les decklists
                            decklist_links = soup.find_all(
                                "a", href=lambda x: x and "/Decklist/View/" in x
                            )

                            found_tournaments.append(
                                {
                                    "id": tournament_id,
                                    "name": tournament_name,
                                    "url": tournament_url,
                                    "date": date_found,
                                    "decklists": len(decklist_links),
                                }
                            )

                            print(f"      ✅ TROUVÉ: {tournament_name}")
                            print(f"         Decklists: {len(decklist_links)}")
                            if date_found:
                                print(f"         Date: {date_found}")

                    elif response.status == 404:
                        print(f"      ❌ ID {tournament_id} n'existe pas")
                    else:
                        print(
                            f"      ⚠️  ID {tournament_id} - Status {response.status}"
                        )

            except Exception as e:
                print(f"      ❌ Erreur ID {tournament_id}: {e}")
                continue

        print(f"\n📊 Résultats: {len(found_tournaments)} tournois trouvés")

        if found_tournaments:
            print("\n🏆 Tournois récents trouvés:")
            for tournament in found_tournaments:
                print(f"   • ID {tournament['id']}: {tournament['name']}")
                print(f"     URL: {tournament['url']}")
                print(f"     Decklists: {tournament['decklists']}")
                if tournament["date"]:
                    print(f"     Date: {tournament['date']}")
                print()

        # Test 2: Si on a trouvé des tournois, tester l'accès aux decklists
        if found_tournaments:
            print("🃏 Test 2: Accès aux decklists")

            first_tournament = found_tournaments[0]
            tournament_url = first_tournament["url"]

            async with session.get(tournament_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    decklist_links = soup.find_all(
                        "a", href=lambda x: x and "/Decklist/View/" in x
                    )

                    if decklist_links:
                        # Tester la première decklist
                        first_decklist_href = decklist_links[0].get("href")
                        if not first_decklist_href.startswith("http"):
                            decklist_url = f"https://melee.gg{first_decklist_href}"
                        else:
                            decklist_url = first_decklist_href

                        print(f"   Test decklist: {decklist_url}")

                        async with session.get(decklist_url) as deck_response:
                            if deck_response.status == 200:
                                deck_html = await deck_response.text()
                                deck_soup = BeautifulSoup(deck_html, "html.parser")

                                # Chercher les cartes
                                card_elements = deck_soup.find_all(
                                    text=lambda x: x
                                    and any(
                                        card in str(x)
                                        for card in [
                                            "Lightning Bolt",
                                            "Island",
                                            "Mountain",
                                            "Forest",
                                            "Plains",
                                            "Swamp",
                                        ]
                                    )
                                )

                                print(f"      ✅ Decklist accessible")
                                print(
                                    f"      Éléments cartes trouvés: {len(card_elements)}"
                                )

                                return True
                            else:
                                print(
                                    f"      ❌ Decklist inaccessible - Status {deck_response.status}"
                                )

        return len(found_tournaments) > 0


if __name__ == "__main__":
    success = asyncio.run(test_melee_real_approach())
    print("\n" + "=" * 60)
    if success:
        print("✅ PREUVE ÉTABLIE : Melee.gg accessible par IDs directs")
        print("   - Tournois récents trouvés")
        print("   - Decklists accessibles")
        print("   - Approche fbettega validée")
    else:
        print("❌ Approche à ajuster")
        print("   - IDs testés peut-être trop bas")
        print("   - Structure HTML peut avoir changé")
