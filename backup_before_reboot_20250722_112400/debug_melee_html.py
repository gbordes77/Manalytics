#!/usr/bin/env python3
"""
Debug : Analyser le HTML réel de Melee.gg
"""

import asyncio

import aiohttp
from bs4 import BeautifulSoup


async def debug_melee_html():
    print("🔍 DEBUG : Analyse HTML Melee.gg")
    print("=" * 50)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession(
        headers=headers, timeout=aiohttp.ClientTimeout(total=30)
    ) as session:

        # Test page principale
        url = "https://melee.gg/Tournament/Search?game=mtg"
        print(f"📄 Analyse: {url}")

        async with session.get(url) as response:
            print(f"Status: {response.status}")

            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                print(f"📏 Taille HTML: {len(html)} caractères")

                # Analyser la structure
                print("\n🏗️  Structure HTML:")

                # Titre de la page
                title = soup.find("title")
                if title:
                    print(f"   Titre: {title.get_text(strip=True)}")

                # Tous les liens
                all_links = soup.find_all("a", href=True)
                print(f"   Total liens: {len(all_links)}")

                # Liens contenant 'Tournament'
                tournament_related = [
                    link
                    for link in all_links
                    if "tournament" in link.get("href", "").lower()
                ]
                print(f"   Liens 'tournament': {len(tournament_related)}")

                # Liens contenant 'View'
                view_links = [
                    link for link in all_links if "view" in link.get("href", "").lower()
                ]
                print(f"   Liens 'view': {len(view_links)}")

                # Montrer quelques liens pour debug
                print("\n🔗 Premiers liens trouvés:")
                for i, link in enumerate(all_links[:10]):
                    href = link.get("href", "")
                    text = link.get_text(strip=True)[:50]
                    print(f"   {i+1}. {text} → {href}")

                # Chercher du contenu spécifique
                print("\n🎯 Recherche contenu spécifique:")

                # Texte contenant des dates récentes
                text_content = soup.get_text()
                if "2025" in text_content:
                    print("   ✅ Contient '2025'")
                else:
                    print("   ❌ Ne contient pas '2025'")

                if "July" in text_content or "Jul" in text_content:
                    print("   ✅ Contient 'July/Jul'")
                else:
                    print("   ❌ Ne contient pas 'July/Jul'")

                # Chercher des éléments avec des classes/IDs spécifiques
                print("\n🎨 Éléments avec classes:")
                elements_with_class = soup.find_all(attrs={"class": True})
                classes = set()
                for elem in elements_with_class[:20]:
                    classes.update(elem.get("class", []))

                print(f"   Classes trouvées: {sorted(list(classes))[:10]}")

                # Sauvegarder un échantillon HTML pour analyse
                with open("melee_sample.html", "w", encoding="utf-8") as f:
                    f.write(html[:5000])  # Premier 5000 caractères
                print("\n💾 Échantillon HTML sauvé dans 'melee_sample.html'")

            else:
                print(f"❌ Erreur HTTP: {response.status}")


if __name__ == "__main__":
    asyncio.run(debug_melee_html())
