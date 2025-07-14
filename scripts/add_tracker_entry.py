#!/usr/bin/env python3
"""
Script pour ajouter automatiquement une entrée dans MODIFICATION_TRACKER.md
Usage:
  python scripts/add_tracker_entry.py --name "Claude" --files "docs/test.py" \
    --description "test modification"
  python scripts/add_tracker_entry.py  # Mode interactif (ancien comportement)
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


def get_user_input():
    """Collecte les informations nécessaires auprès de l'utilisateur."""
    print("🔧 Ajout d'une entrée dans MODIFICATION_TRACKER.md")
    print("=" * 50)

    # Nom de l'intervenant
    print("📝 Nom de l'assistant (ex: Claude, GPT-4, Gemini, etc.)")
    name = input("Nom de l'assistant : ").strip()
    if not name:
        print("❌ Le nom de l'assistant est obligatoire")
        sys.exit(1)

    # Date et heure actuelles
    now = datetime.now()
    datetime_str = now.strftime("%Y-%m-%d %H:%M")

    # Nom avec date/heure
    full_name = f"{name}_{now.strftime('%Y-%m-%d_%H-%M')}"

    print(f"✅ Nom complet généré: {full_name}")

    # Fichier(s) concerné(s)
    files = input("Fichier(s) concerné(s) (ex: src/orchestrator.py) : ").strip()
    if not files:
        print("❌ Au moins un fichier est obligatoire")
        sys.exit(1)

    # Type de modification
    print("\nType de modification :")
    print("1. AJOUT")
    print("2. MODIFICATION")
    print("3. SUPPRESSION")
    type_choice = input("Choix (1-3) : ").strip()

    type_map = {"1": "AJOUT", "2": "MODIFICATION", "3": "SUPPRESSION"}
    mod_type = type_map.get(type_choice, "MODIFICATION")

    # Description
    description = input("Description de la modification : ").strip()
    if not description:
        print("❌ La description est obligatoire")
        sys.exit(1)

    # Justification
    justification = input("Justification : ").strip()
    if not justification:
        justification = "Amélioration du système"

    # Tests
    tests = input("Comment tester (optionnel) : ").strip()
    if not tests:
        tests = "Tests manuels du pipeline"

    # Rollback
    rollback = input("Procédure de rollback (optionnel) : ").strip()
    if not rollback:
        rollback = "git revert du commit correspondant"

    return {
        "name": full_name,
        "datetime": datetime_str,
        "files": files,
        "type": mod_type,
        "description": description,
        "justification": justification,
        "tests": tests,
        "rollback": rollback,
    }


def get_non_interactive_input(args):
    """Collecte les informations depuis les arguments en ligne de commande."""
    now = datetime.now()
    datetime_str = now.strftime("%Y-%m-%d %H:%M")

    # Nom avec date/heure
    full_name = f"{args.name}_{now.strftime('%Y-%m-%d_%H-%M')}"

    return {
        "name": full_name,
        "datetime": datetime_str,
        "files": args.files,
        "type": args.type,
        "description": args.description,
        "justification": args.justification,
        "tests": args.tests,
        "rollback": args.rollback,
    }


def add_tracker_entry(info):
    """Ajoute l'entrée dans MODIFICATION_TRACKER.md."""
    tracker_path = Path("docs/MODIFICATION_TRACKER.md")

    if not tracker_path.exists():
        print(f"❌ Fichier {tracker_path} non trouvé")
        sys.exit(1)

    # Lire le contenu actuel
    with open(tracker_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Créer la nouvelle entrée
    entry = f"""
### [{info['datetime']}] - {info['name']}
**Fichier(s) concerné(s)** : {info['files']}
**Type** : {info['type']}
**Description** : {info['description']}
**Justification** : {info['justification']}
**Tests** : {info['tests']}
**Rollback** : {info['rollback']}
"""

    # Trouver la section historique et insérer la nouvelle entrée
    lines = content.split("\n")
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)

        # Insérer après la ligne "## 🔄 **HISTORIQUE DES MODIFICATIONS**"
        if "## 🔄 **HISTORIQUE DES MODIFICATIONS**" in line and not inserted:
            new_lines.append(entry)
            inserted = True

    # Écrire le nouveau contenu
    with open(tracker_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"✅ Entrée ajoutée dans {tracker_path}")
    print(f"📝 Nom complet : {info['name']}")
    print(f"📁 Fichier(s) : {info['files']}")
    print(f"🔧 Type : {info['type']}")

    return True


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Ajouter une entrée dans MODIFICATION_TRACKER.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python scripts/add_tracker_entry.py --name "Claude" --files "docs/test.py" \
    --description "test modification"
  python scripts/add_tracker_entry.py  # Mode interactif
        """,
    )

    parser.add_argument("--name", help="Nom de l'assistant (ex: Claude, GPT-4)")
    parser.add_argument(
        "--files", help="Fichier(s) concerné(s) (ex: src/orchestrator.py)"
    )
    parser.add_argument(
        "--type",
        choices=["AJOUT", "MODIFICATION", "SUPPRESSION"],
        default="MODIFICATION",
        help="Type de modification",
    )
    parser.add_argument("--description", help="Description de la modification")
    parser.add_argument(
        "--justification",
        default="Amélioration du système",
        help="Justification de la modification",
    )
    parser.add_argument(
        "--tests",
        default="Tests manuels du pipeline",
        help="Comment tester la modification",
    )
    parser.add_argument(
        "--rollback",
        default="git revert du commit correspondant",
        help="Procédure de rollback",
    )

    args = parser.parse_args()

    try:
        # Vérifier qu'on est dans le bon répertoire
        if not os.path.exists("docs/MODIFICATION_TRACKER.md"):
            print("❌ Veuillez exécuter ce script depuis la racine du projet Manalytics")
            sys.exit(1)

        # Mode non-interactif si les arguments requis sont fournis
        if args.name and args.files and args.description:
            print("🤖 Mode non-interactif activé")
            info = get_non_interactive_input(args)
        else:
            # Mode interactif (ancien comportement)
            info = get_user_input()

        # Ajouter l'entrée
        add_tracker_entry(info)

        print("\n" + "=" * 50)
        print("🎉 Entrée ajoutée avec succès !")
        print("📋 Prochaines étapes :")
        print("1. git add docs/MODIFICATION_TRACKER.md")
        print("2. git commit -m 'track: preparing modification'")
        print("3. Faire votre modification")
        print("4. git commit -m 'votre modification (tracked)'")

    except KeyboardInterrupt:
        print("\n❌ Opération annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
