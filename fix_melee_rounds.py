#!/usr/bin/env python3
"""
Fix pour récupérer les Round Standings en utilisant le bon format de payload
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.models.Melee_model import MtgMeleeConstants
from scrape_melee_flexible import MtgMeleeClientFlexible
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_round_standings_with_proper_payload():
    """Tester avec le payload correct depuis MtgMeleeConstants"""
    
    client = MtgMeleeClientFlexible()
    client.ensure_authenticated()
    
    # Tournoi Boa
    tournament_id = 304273
    round_id = "1060187"  # Premier round
    
    logger.info(f"🎯 Test avec le payload correct")
    logger.info(f"Tournament ID: {tournament_id}")
    logger.info(f"Round ID: {round_id}")
    
    # Utiliser le payload depuis les constants
    payload_template = MtgMeleeConstants.ROUND_PAGE_PARAMETERS
    
    # Remplacer les placeholders
    payload_str = payload_template.replace("{start}", "0").replace("{roundId}", round_id)
    
    # Convertir en dictionnaire
    payload = {}
    for param in payload_str.split('&'):
        if '=' in param:
            key, value = param.split('=', 1)
            # Décoder les %5B et %5D
            key = key.replace('%5B', '[').replace('%5D', ']')
            value = value.replace('%3A', ':').replace('%2B', '+')
            payload[key] = value
    
    logger.info(f"\n📝 Payload construit avec {len(payload)} paramètres")
    
    try:
        response = client.session.post(
            MtgMeleeConstants.ROUND_PAGE,
            data=payload_str,  # Envoyer comme string URL-encoded
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            }
        )
        
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'data' in data:
                    logger.info(f"✅ Succès! {len(data['data'])} résultats")
                    
                    # Afficher quelques résultats
                    for i, entry in enumerate(data['data'][:3]):
                        player = entry.get('Team', {}).get('Players', [{}])[0].get('DisplayName', 'Unknown')
                        rank = entry.get('Rank', '?')
                        record = entry.get('MatchRecord', '?')
                        logger.info(f"   #{rank} {player} - {record}")
                else:
                    logger.warning(f"Pas de 'data': {list(data.keys())}")
            except Exception as e:
                logger.error(f"Erreur parsing JSON: {e}")
                logger.info(f"Réponse: {response.text[:500]}")
        else:
            logger.error(f"Erreur HTTP: {response.status_code}")
            logger.info(f"Réponse: {response.text[:500]}")
            
    except Exception as e:
        logger.error(f"Erreur requête: {e}")


if __name__ == "__main__":
    test_round_standings_with_proper_payload()