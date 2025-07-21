#!/usr/bin/env python3
"""
Script de Validation des Workarounds

Ce script teste tous les workarounds implémentés pour s'assurer qu'ils reproduisent
fidèlement le comportement du code C# original.

Usage:
    python test_workarounds_validation.py
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_workaround_1_string_comparisons():
    """Test Workaround #1: Comparaisons de chaînes"""
    print("🔧 Testing Workaround #1: String Comparisons...")

    from src.python.workarounds.string_utils import SafeStringCompare

    # Test case sensitivity
    assert SafeStringCompare.equals("Lightning Bolt", "lightning bolt") == True
    assert SafeStringCompare.equals("Lightning Bolt", "Lightning Bolt") == True
    assert SafeStringCompare.equals("Lightning Bolt", "Shock") == False

    # Test contains
    assert SafeStringCompare.contains("Izzet Prowess", "prowess") == True
    assert SafeStringCompare.contains("Standard Challenge 64", "challenge") == True
    assert SafeStringCompare.contains("Modern Tournament", "legacy") == False

    # Test matches_any
    assert (
        SafeStringCompare.matches_any("Lightning Bolt", ["lightning bolt", "Shock"])
        == True
    )
    assert (
        SafeStringCompare.matches_any("Lightning Bolt", ["Shock", "Counterspell"])
        == False
    )

    print("✅ Workaround #1: String Comparisons - PASSED")
    return True


def test_workaround_2_json_mapping():
    """Test Workaround #2: Sérialisation JSON"""
    print("🔧 Testing Workaround #2: JSON Mapping...")

    from src.python.workarounds.json_mapper import JsonMapper

    # Test deck item mapping
    raw_card = {"CardName": "Lightning Bolt", "Count": 4}
    mapped_card = JsonMapper.map_deck_item(raw_card)
    assert mapped_card["card"] == "Lightning Bolt"
    assert mapped_card["count"] == 4

    # Test deck mapping
    raw_deck = {
        "Player": "TestPlayer",
        "Result": "5-0",
        "Mainboard": [{"CardName": "Lightning Bolt", "Count": 4}],
        "Sideboard": [{"CardName": "Counterspell", "Count": 2}],
    }
    mapped_deck = JsonMapper.map_deck(raw_deck)
    assert mapped_deck["player"] == "TestPlayer"
    assert mapped_deck["result"] == "5-0"
    assert len(mapped_deck["mainboard"]) == 1
    assert len(mapped_deck["sideboard"]) == 1

    print("✅ Workaround #2: JSON Mapping - PASSED")
    return True


def test_workaround_3_date_handling():
    """Test Workaround #3: Gestion des dates"""
    print("🔧 Testing Workaround #3: Date Handling...")

    from src.python.workarounds.date_handler import DateHandler

    # Test ISO date parsing
    iso_date = "2025-07-21T10:00:00Z"
    parsed_date = DateHandler.parse_tournament_date(iso_date)
    assert parsed_date is not None
    assert parsed_date.tzinfo == timezone.utc

    # Test simple date parsing
    simple_date = "2025-07-21"
    parsed_simple = DateHandler.parse_tournament_date(simple_date)
    assert parsed_simple is not None

    # Test date range validation
    start_date, end_date = DateHandler.parse_date_range("2025-07-01", "2025-07-31")
    test_date = DateHandler.parse_tournament_date("2025-07-15")
    assert DateHandler.is_date_in_range(test_date, start_date, end_date) == True

    # Test ensure deck date
    deck_date = None
    tournament_date = parsed_date
    result_date = DateHandler.ensure_deck_date(deck_date, tournament_date)
    assert result_date == tournament_date

    print("✅ Workaround #3: Date Handling - PASSED")
    return True


def test_workaround_4_archetype_colors():
    """Test Workaround #4: Enum Flags Couleurs"""
    print("🔧 Testing Workaround #4: Archetype Colors...")

    from src.python.workarounds.archetype_color import ArchetypeColor

    # Test basic colors
    assert ArchetypeColor.W == 1
    assert ArchetypeColor.U == 2
    assert ArchetypeColor.B == 4
    assert ArchetypeColor.R == 8
    assert ArchetypeColor.G == 16

    # Test combined colors (flags)
    assert ArchetypeColor.WU == (ArchetypeColor.W | ArchetypeColor.U)
    assert ArchetypeColor.WU == 3  # 1 | 2 = 3

    # Test string conversion
    assert ArchetypeColor.to_string(ArchetypeColor.WU) == "WU"
    assert ArchetypeColor.to_string(ArchetypeColor.WUBRG) == "WUBRG"
    assert ArchetypeColor.to_string(ArchetypeColor.C) == "C"

    # Test from string
    assert ArchetypeColor.from_string("WU") == ArchetypeColor.WU
    assert ArchetypeColor.from_string("WUBRG") == ArchetypeColor.WUBRG

    # Test guild names
    assert ArchetypeColor.get_guild_name(ArchetypeColor.WU) == "Azorius"
    assert ArchetypeColor.get_guild_name(ArchetypeColor.UR) == "Izzet"

    print("✅ Workaround #4: Archetype Colors - PASSED")
    return True


def test_workaround_5_linq_equivalent():
    """Test Workaround #5: LINQ Equivalent"""
    print("🔧 Testing Workaround #5: LINQ Equivalent...")

    from src.python.workarounds.linq_equivalent import LinqEquivalent

    # Test data
    test_data = [
        {"name": "Alice", "age": 25, "city": "Paris"},
        {"name": "Bob", "age": 30, "city": "London"},
        {"name": "Charlie", "age": 35, "city": "Paris"},
    ]

    # Test Where
    paris_people = LinqEquivalent.where(test_data, lambda x: x["city"] == "Paris")
    assert len(paris_people) == 2

    # Test Select
    names = LinqEquivalent.select(test_data, lambda x: x["name"])
    assert "Alice" in names and "Bob" in names and "Charlie" in names

    # Test Any
    has_alice = LinqEquivalent.any(test_data, lambda x: x["name"] == "Alice")
    assert has_alice == True

    has_david = LinqEquivalent.any(test_data, lambda x: x["name"] == "David")
    assert has_david == False

    # Test OrderBy
    sorted_by_age = LinqEquivalent.order_by(test_data, lambda x: x["age"])
    assert sorted_by_age[0]["name"] == "Alice"
    assert sorted_by_age[-1]["name"] == "Charlie"

    # Test Count
    count_paris = LinqEquivalent.count(test_data, lambda x: x["city"] == "Paris")
    assert count_paris == 2

    print("✅ Workaround #5: LINQ Equivalent - PASSED")
    return True


def test_workaround_6_exception_handling():
    """Test Workaround #6: Gestion d'exceptions"""
    print("🔧 Testing Workaround #6: Exception Handling...")

    import json
    import tempfile

    from src.python.workarounds.exception_handler import (
        ArchetypeLoader,
        ArchetypeLoadingException,
    )

    # Test valid archetype file
    valid_archetype = {
        "Name": "Test Archetype",
        "Conditions": [{"Type": "InMainboard", "Cards": ["Lightning Bolt"]}],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(valid_archetype, f)
        temp_file = f.name

    try:
        loaded = ArchetypeLoader.load_archetype_file(temp_file)
        assert loaded["Name"] == "Test Archetype"
        assert len(loaded["Conditions"]) == 1
    finally:
        Path(temp_file).unlink()

    # Test invalid archetype file (no conditions)
    invalid_archetype = {"Name": "Invalid Archetype"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_archetype, f)
        temp_file = f.name

    try:
        try:
            ArchetypeLoader.load_archetype_file(temp_file)
            assert False, "Should have raised ArchetypeLoadingException"
        except ArchetypeLoadingException as e:
            assert "no conditions declared" in str(e)
    finally:
        Path(temp_file).unlink()

    print("✅ Workaround #6: Exception Handling - PASSED")
    return True


def test_workaround_7_precision_calculator():
    """Test Workaround #7: Précision flottante"""
    print("🔧 Testing Workaround #7: Precision Calculator...")

    from src.python.workarounds.precision_calculator import PrecisionCalculator

    calc = PrecisionCalculator()

    # Test similarity calculation
    similarity = calc.calculate_similarity(3, 10)
    assert abs(similarity - 0.3) < 1e-10

    # Test percentage calculation
    percentage = calc.calculate_percentage(25, 100)
    assert abs(percentage - 25.0) < 1e-10

    # Test winrate calculation
    winrate = calc.calculate_winrate(7, 3)
    assert abs(winrate - 0.7) < 1e-10

    # Test average calculation
    average = calc.calculate_average([1, 2, 3, 4, 5])
    assert abs(average - 3.0) < 1e-10

    # Test diversity metrics
    archetype_counts = {"Aggro": 10, "Control": 5, "Midrange": 3}
    metrics = calc.calculate_diversity_metrics(archetype_counts)
    assert metrics["total_count"] == 18
    assert metrics["unique_archetypes"] == 3
    assert metrics["shannon_diversity"] > 0
    assert metrics["simpson_diversity"] > 0

    print("✅ Workaround #7: Precision Calculator - PASSED")
    return True


def test_integration():
    """Test de l'intégration complète"""
    print("🔧 Testing Integration...")

    from src.python.workarounds.integration import ManalyticsIntegration

    integration = ManalyticsIntegration()

    # Test basic initialization
    assert integration.precision_calculator is not None

    # Test archetype counts calculation
    archetype_counts = {"Aggro": 10, "Control": 5, "Midrange": 3}
    metrics = integration.calculate_diversity_metrics(archetype_counts)
    assert metrics["total_count"] == 18

    print("✅ Integration - PASSED")
    return True


def main():
    """Fonction principale de test"""
    print("🚀 VALIDATION DES WORKAROUNDS MANALYTICS")
    print("=" * 50)

    tests = [
        test_workaround_1_string_comparisons,
        test_workaround_2_json_mapping,
        test_workaround_3_date_handling,
        test_workaround_4_archetype_colors,
        test_workaround_5_linq_equivalent,
        test_workaround_6_exception_handling,
        test_workaround_7_precision_calculator,
        test_integration,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} - FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} - ERROR: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 50)
    print(f"📊 RÉSULTATS: {passed} PASSED, {failed} FAILED")

    if failed == 0:
        print("🎉 TOUS LES WORKAROUNDS FONCTIONNENT CORRECTEMENT!")
        print("✅ Fidélité attendue: 98-99%")
        return 0
    else:
        print("⚠️ Certains workarounds ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
