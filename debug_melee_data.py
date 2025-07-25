#!/usr/bin/env python3
"""
Debug de la structure des données Melee
"""
from scrape_melee_from_commit import MtgMeleeClient
import json
from datetime import datetime, timedelta

# Créer le client
client = MtgMeleeClient()
client.ensure_authenticated()

# Rechercher des tournois récents
end_date = datetime.now()
start_date = end_date - timedelta(days=1)

print("🔍 Recherche de tournois récents...")
tournaments = client.search_tournaments(start_date, end_date)

if tournaments:
    print(f"\n✅ {len(tournaments)} entrées trouvées")
    
    # Examiner la première entrée
    first = tournaments[0]
    
    print("\n📊 Structure de la première entrée:")
    print(json.dumps(first, indent=2))
    
    # Afficher toutes les clés
    print("\n🔑 Clés disponibles:")
    for key in sorted(first.keys()):
        value = first[key]
        if value:
            print(f"  - {key}: {value}")
    
    # Chercher l'ID du deck
    print("\n🔍 Recherche de l'ID du deck:")
    possible_id_keys = ['DecklistId', 'Guid', 'Id', 'DeckId', 'DeckGuid']
    for key in possible_id_keys:
        if key in first:
            print(f"  ✅ {key}: {first[key]}")
else:
    print("❌ Aucun tournoi trouvé")