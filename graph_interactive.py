#!/usr/bin/env python3
"""
Générateur de graphiques interactif pour métagame MTG
Version conviviale avec interface utilisateur
"""

from graph_generator import MetagameGraphGenerator
from datetime import datetime, timedelta
import os

def print_banner():
    """Afficher la bannière"""
    print("🎯" + "=" * 60 + "🎯")
    print("    GÉNÉRATEUR DE GRAPHIQUES MÉTAGAME MTG")
    print("    Phase 3 - Manalytics Intelligence Avancée")
    print("🎯" + "=" * 60 + "🎯")

def get_format_choice():
    """Demander le format à l'utilisateur"""
    formats = {
        '1': 'Standard',
        '2': 'Modern', 
        '3': 'Legacy',
        '4': 'Pioneer',
        '5': 'Vintage',
        '6': 'Pauper'
    }
    
    print("\n📋 FORMATS DISPONIBLES:")
    for key, value in formats.items():
        print(f"  {key}. {value}")
    
    while True:
        choice = input("\n🎯 Choisissez un format (1-6): ").strip()
        if choice in formats:
            return formats[choice]
        print("❌ Choix invalide. Veuillez choisir un nombre entre 1 et 6.")

def get_date_choice():
    """Demander la date à l'utilisateur"""
    print("\n📅 SÉLECTION DE LA DATE:")
    print("  1. Aujourd'hui")
    print("  2. Il y a 1 semaine")
    print("  3. Il y a 1 mois")
    print("  4. Il y a 3 mois")
    print("  5. Date personnalisée")
    
    while True:
        choice = input("\n🎯 Choisissez une option (1-5): ").strip()
        
        if choice == '1':
            return datetime.now()
        elif choice == '2':
            return datetime.now() - timedelta(weeks=1)
        elif choice == '3':
            return datetime.now() - timedelta(days=30)
        elif choice == '4':
            return datetime.now() - timedelta(days=90)
        elif choice == '5':
            while True:
                date_str = input("📅 Entrez la date (format: YYYY-MM-DD): ").strip()
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    if date > datetime.now():
                        print("❌ La date ne peut pas être dans le futur.")
                        continue
                    return date
                except ValueError:
                    print("❌ Format invalide. Utilisez YYYY-MM-DD (ex: 2024-01-15)")
        else:
            print("❌ Choix invalide. Veuillez choisir un nombre entre 1 et 5.")

def get_days_choice():
    """Demander le nombre de jours à analyser"""
    print("\n⏰ PÉRIODE D'ANALYSE:")
    print("  1. 7 jours")
    print("  2. 14 jours")
    print("  3. 30 jours (recommandé)")
    print("  4. 60 jours")
    print("  5. Personnalisé")
    
    while True:
        choice = input("\n🎯 Choisissez une période (1-5): ").strip()
        
        if choice == '1':
            return 7
        elif choice == '2':
            return 14
        elif choice == '3':
            return 30
        elif choice == '4':
            return 60
        elif choice == '5':
            while True:
                try:
                    days = int(input("📊 Nombre de jours à analyser (1-365): "))
                    if 1 <= days <= 365:
                        return days
                    print("❌ Veuillez entrer un nombre entre 1 et 365.")
                except ValueError:
                    print("❌ Veuillez entrer un nombre valide.")
        else:
            print("❌ Choix invalide. Veuillez choisir un nombre entre 1 et 5.")

def show_results(files_created):
    """Afficher les résultats"""
    print("\n🎉 GÉNÉRATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 50)
    
    print(f"📁 {len(files_created)} graphiques créés:")
    for i, file in enumerate(files_created, 1):
        file_size = os.path.getsize(file) / 1024  # Taille en KB
        print(f"  {i}. {file} ({file_size:.1f} KB)")
    
    print("\n📊 TYPES DE GRAPHIQUES GÉNÉRÉS:")
    print("  ✅ Évolution des parts de marché")
    print("  ✅ Analyse des winrates")
    print("  ✅ Heatmap de popularité")
    print("  ✅ Dashboard complet")
    
    print("\n💡 CONSEILS D'UTILISATION:")
    print("  • Ouvrez les fichiers .png avec votre visionneuse d'images")
    print("  • Le dashboard offre une vue d'ensemble complète")
    print("  • Les graphiques sont en haute résolution (300 DPI)")
    print("  • Partagez les analyses avec votre équipe MTG!")

def main():
    """Fonction principale interactive"""
    print_banner()
    
    # Demander les paramètres à l'utilisateur
    format_name = get_format_choice()
    start_date = get_date_choice()
    days = get_days_choice()
    
    # Confirmation
    print("\n📋 RÉSUMÉ DE LA GÉNÉRATION:")
    print(f"  Format: {format_name}")
    print(f"  Date de début: {start_date.strftime('%d/%m/%Y')}")
    print(f"  Période: {days} jours")
    print(f"  Date de fin: {(start_date + timedelta(days=days)).strftime('%d/%m/%Y')}")
    
    confirm = input("\n🤔 Continuer avec ces paramètres? (o/n): ").strip().lower()
    if confirm not in ['o', 'oui', 'y', 'yes']:
        print("❌ Génération annulée.")
        return
    
    # Générer les graphiques
    print("\n🚀 GÉNÉRATION EN COURS...")
    generator = MetagameGraphGenerator()
    
    try:
        files_created = generator.generate_all_graphs(format_name, start_date, days)
        show_results(files_created)
        
        # Demander si l'utilisateur veut générer d'autres graphiques
        while True:
            another = input("\n🔄 Voulez-vous générer d'autres graphiques? (o/n): ").strip().lower()
            if another in ['o', 'oui', 'y', 'yes']:
                print("\n" + "="*60)
                main()
                break
            elif another in ['n', 'non', 'no']:
                print("\n👋 Merci d'avoir utilisé le générateur de graphiques!")
                print("🎯 Manalytics Phase 3 - Intelligence Avancée")
                break
            else:
                print("❌ Veuillez répondre par 'o' (oui) ou 'n' (non).")
                
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération: {e}")
        print("💡 Vérifiez vos paramètres et réessayez.")

if __name__ == "__main__":
    main() 