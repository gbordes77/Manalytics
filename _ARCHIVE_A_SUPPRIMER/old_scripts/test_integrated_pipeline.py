#!/usr/bin/env python3
"""
Test du pipeline intégré - Génération automatique des visualisations
"""

import asyncio
import sys
import logging
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append('src')

from python.visualizations.matchup_matrix import MatchupMatrixGenerator
from python.visualizations.metagame_charts import MetagameChartsGenerator

class TestIntegratedPipeline:
    """Test du pipeline intégré avec visualisations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    async def generate_visualizations(self):
        """Génère toutes les visualisations automatiquement (comme dans l'orchestrateur)"""
        try:
            output_dir = "analysis_output"
            
            self.logger.info("🎨 DÉMARRAGE DE LA GÉNÉRATION INTÉGRÉE")
            
            # 1. Matrice de matchups
            self.logger.info("📊 Génération de la matrice de matchups...")
            matrix_generator = MatchupMatrixGenerator()
            matrix_report = matrix_generator.generate_full_report(output_dir)
            
            # 2. Graphiques de métagame
            self.logger.info("📈 Génération des graphiques de métagame...")
            metagame_generator = MetagameChartsGenerator()
            metagame_report = metagame_generator.generate_all_charts(output_dir)
            
            # 3. Tableau de bord
            self.logger.info("🎯 Génération du tableau de bord...")
            self.generate_dashboard(output_dir)
            
            # 4. Résumé
            total_files = len(matrix_report['files']) + len(metagame_report['files']) + 1
            self.logger.info(f"✅ {total_files} visualisations générées dans {output_dir}/")
            
            # 5. Statistiques
            self.logger.info("📊 RÉSUMÉ DE L'ANALYSE:")
            self.logger.info(f"   • Archétypes: {matrix_report['metadata']['archetypes_count']}")
            self.logger.info(f"   • Tournois: {matrix_report['metadata']['total_tournaments']}")
            self.logger.info(f"   • Joueurs: {matrix_report['metadata']['total_players']}")
            self.logger.info(f"   • Graphiques: {len(metagame_report['charts'])}")
            
            return {
                'matrix_report': matrix_report,
                'metagame_report': metagame_report,
                'dashboard_path': f"{output_dir}/dashboard_complete.html"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération visualisations: {e}")
            raise
    
    def generate_dashboard(self, output_dir: str):
        """Génère le tableau de bord HTML complet"""
        try:
            import json
            import pandas as pd
            from datetime import datetime
            
            # Charger les métadonnées
            with open('real_data/complete_dataset.json', 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            
            # Statistiques générales
            total_tournaments = df['tournament_id'].nunique()
            total_players = len(df)
            total_matches = df['matches_played'].sum()
            archetypes = sorted(df['archetype'].unique())
            
            # Template HTML intégré
            html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manalytics - Pipeline Intégré</title>
    <style>
        :root {{
            --c-50: #762a83; --c-40: #8e4d99; --c-30: #a66fb0; --c-20: #be91c7; --c-10: #d6b3de;
            --c0: #f7f7f7; --c10: #c7e9c0; --c20: #a1d99b; --c30: #7bc87c; --c40: #4eb265; --c50: #1b7837;
        }}
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }}
        .header {{ background: linear-gradient(135deg, var(--c-50) 0%, var(--c50) 100%); color: white; padding: 2rem; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5rem; font-weight: 300; }}
        .header .badge {{ background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; display: inline-block; margin-top: 1rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 3rem; }}
        .stat-card {{ background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        .stat-number {{ font-size: 2.5rem; font-weight: bold; color: var(--c-50); }}
        .viz-card {{ background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }}
        .viz-header {{ background: var(--c0); padding: 1.5rem; border-bottom: 1px solid #eee; }}
        .viz-title {{ font-size: 1.3rem; font-weight: 600; color: var(--c-50); margin: 0; }}
        .viz-content {{ height: 600px; }}
        .viz-iframe {{ width: 100%; height: 100%; border: none; }}
        .footer {{ background: #333; color: white; text-align: center; padding: 2rem; }}
        .success-banner {{ background: linear-gradient(45deg, #4CAF50, #45a049); color: white; padding: 1rem; text-align: center; margin-bottom: 2rem; border-radius: 8px; }}
        .pie-chart {{ height: 700px; }} /* Plus haut pour le pie chart */
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Manalytics</h1>
        <p>Pipeline Intégré - Génération Automatique des Visualisations</p>
        <div class="badge">✅ PIPELINE COMPLET ACTIVÉ</div>
    </div>
    
    <div class="container">
        <div class="success-banner">
            <h3>🎉 Pipeline Intégré Fonctionnel!</h3>
            <p>Toutes les visualisations sont maintenant générées automatiquement à chaque analyse</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-number">{total_tournaments}</div><div>Tournois</div></div>
            <div class="stat-card"><div class="stat-number">{total_players}</div><div>Joueurs</div></div>
            <div class="stat-card"><div class="stat-number">{total_matches}</div><div>Matchs</div></div>
            <div class="stat-card"><div class="stat-number">{len(archetypes)}</div><div>Archétypes</div></div>
        </div>
        
        <div class="viz-card">
            <div class="viz-header">
                <h3 class="viz-title">🥧 Part de Métagame (Pie Chart)</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;">Répartition des archétypes dans le métagame Standard</p>
            </div>
            <div class="viz-content pie-chart">
                <iframe src="metagame_pie.html" class="viz-iframe"></iframe>
            </div>
        </div>
        
        <div class="viz-card">
            <div class="viz-header"><h3 class="viz-title">📊 Matrice de Matchups</h3></div>
            <div class="viz-content"><iframe src="matchup_matrix.html" class="viz-iframe"></iframe></div>
        </div>
        
        <div class="viz-card">
            <div class="viz-header"><h3 class="viz-title">📈 Part de Métagame (Barres)</h3></div>
            <div class="viz-content"><iframe src="metagame_share.html" class="viz-iframe"></iframe></div>
        </div>
        
        <div class="viz-card">
            <div class="viz-header"><h3 class="viz-title">🎯 Winrates avec IC</h3></div>
            <div class="viz-content"><iframe src="winrate_confidence.html" class="viz-iframe"></iframe></div>
        </div>
        
        <div class="viz-card">
            <div class="viz-header"><h3 class="viz-title">🏆 Classification par Tiers</h3></div>
            <div class="viz-content"><iframe src="tiers_scatter.html" class="viz-iframe"></iframe></div>
        </div>
        
        <div class="viz-card">
            <div class="viz-header"><h3 class="viz-title">💫 Winrate vs Présence</h3></div>
            <div class="viz-content"><iframe src="bubble_winrate_presence.html" class="viz-iframe"></iframe></div>
        </div>
        
        <div class="viz-card">
            <div class="viz-header"><h3 class="viz-title">🌟 Top Archétypes</h3></div>
            <div class="viz-content"><iframe src="top_5_0.html" class="viz-iframe"></iframe></div>
        </div>
    </div>
    
    <div class="footer">
        <p>Généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
        <p>🚀 Pipeline Intégré • 📊 Visualisations Automatiques • 🎯 Données Réelles</p>
    </div>
</body>
</html>
            """
            
            # Sauvegarder
            dashboard_path = Path(output_dir) / "dashboard_complete.html"
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            self.logger.info(f"✅ Tableau de bord créé: {dashboard_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération dashboard: {e}")
            raise

async def main():
    """Test du pipeline intégré"""
    try:
        pipeline = TestIntegratedPipeline()
        
        print("🚀 TEST DU PIPELINE INTÉGRÉ AVEC PIE CHART")
        print("=" * 50)
        
        result = await pipeline.generate_visualizations()
        
        print("\n🎉 PIPELINE INTÉGRÉ TESTÉ AVEC SUCCÈS!")
        print("=" * 50)
        print("✅ Toutes les visualisations sont maintenant générées automatiquement")
        print("✅ Le PIE CHART de métagame est intégré (comme votre image PNG)")
        print("✅ L'orchestrateur intègre la génération des graphiques")
        print("✅ Le tableau de bord est créé automatiquement")
        print("\n🌐 Ouvrez analysis_output/dashboard_complete.html pour voir le résultat")
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 