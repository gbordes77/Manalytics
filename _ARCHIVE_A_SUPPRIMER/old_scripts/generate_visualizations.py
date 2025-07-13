#!/usr/bin/env python3
"""
Script principal pour générer toutes les visualisations Manalytics
Utilise exclusivement les vraies données de tournois
"""

import sys
import logging
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append('src')

from python.visualizations.matchup_matrix import MatchupMatrixGenerator
from python.visualizations.metagame_charts import MetagameChartsGenerator

def setup_logging():
    """Configure le logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Génère toutes les visualisations"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Démarrage de la génération complète des visualisations Manalytics")
    
    # Créer le répertoire de sortie
    output_dir = Path("analysis_output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # 1. Générer la matrice de matchups
        logger.info("📊 Génération de la matrice de matchups...")
        matrix_generator = MatchupMatrixGenerator()
        matrix_report = matrix_generator.generate_full_report(str(output_dir))
        
        logger.info(f"✅ Matrice de matchups générée:")
        logger.info(f"   - Archétypes: {matrix_report['metadata']['archetypes_count']}")
        logger.info(f"   - Tournois: {matrix_report['metadata']['total_tournaments']}")
        logger.info(f"   - Joueurs: {matrix_report['metadata']['total_players']}")
        
        # 2. Générer tous les graphiques de métagame
        logger.info("📈 Génération de tous les graphiques de métagame...")
        metagame_generator = MetagameChartsGenerator()
        metagame_report = metagame_generator.generate_all_charts(str(output_dir))
        
        logger.info(f"✅ Graphiques de métagame générés:")
        for chart_name in metagame_report['charts'].keys():
            logger.info(f"   - {chart_name}")
        
        # 3. Résumé complet
        all_files = []
        all_files.extend(matrix_report['files'].values())
        all_files.extend(metagame_report['files'].values())
        
        logger.info("🎯 Génération terminée avec succès!")
        logger.info(f"📁 Répertoire de sortie: {output_dir.absolute()}")
        logger.info("📊 Visualisations générées:")
        logger.info("   • Matrice de matchups (heatmap interactive)")
        logger.info("   • Part de métagame des archétypes (bar chart horizontal)")
        logger.info("   • Winrates avec intervalles de confiance (scatter + barres d'erreur)")
        logger.info("   • Classification par tiers (scatter plot)")
        logger.info("   • Winrate vs présence (bubble chart)")
        logger.info("   • Top archétypes performants (bar chart)")
        
        logger.info("💾 Exports de données:")
        logger.info("   • CSV et JSON pour tous les graphiques")
        logger.info("   • Statistiques détaillées par archétype")
        logger.info("   • Données des top performers")
        
        logger.info("🎨 Caractéristiques:")
        logger.info("   • Palette heatmap violet→vert")
        logger.info("   • Intervalles de confiance 95% (méthode Wilson)")
        logger.info("   • Tooltips interactifs")
        logger.info("   • Données 100% réelles de tournois")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 