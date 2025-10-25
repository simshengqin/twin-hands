"""
Joker Loader - Load jokers from CSV data.
Utility for loading and parsing joker data from jokers_structured.csv.
"""

import csv
from typing import List
from pathlib import Path

from src.resources.joker_resource import JokerResource


class JokerLoader:
    """
    Load jokers from CSV file.
    In Godot, this would be a static utility class.

    GDScript equivalent:
    class_name JokerLoader
    extends Node

    static func load_jokers_from_csv(path: String) -> Array[JokerResource]
    """

    @staticmethod
    def load_from_csv(csv_path: str) -> List[JokerResource]:
        """
        Load all jokers from CSV file.

        CSV Format:
        id,name,effect_type,trigger,condition_type,condition_value,
        bonus_type,bonus_value,per_card,grow_per,rarity,cost,priority,notes

        Args:
            csv_path: Path to CSV file

        Returns:
            List of JokerResource objects
        """
        jokers = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty rows
                if not row.get('id') or not row['id'].strip():
                    continue

                # Parse CSV data
                joker = JokerResource(
                    id=row['id'].strip(),
                    name=row['name'].strip(),
                    effect_type=row['effect_type'].strip(),
                    trigger=row['trigger'].strip(),
                    condition_type=row['condition_type'].strip(),
                    condition_value=row['condition_value'].strip(),
                    bonus_type=row['bonus_type'].strip(),
                    bonus_value=JokerLoader._parse_bonus_value(row['bonus_value']),
                    per_card=JokerLoader._parse_bool(row['per_card']),
                    grow_per=row['grow_per'].strip() if row['grow_per'].strip() else None,
                    rarity=row['rarity'].strip(),
                    cost=int(row['cost'].strip()),
                    notes=row['notes'].strip() if row.get('notes') else ""
                )

                jokers.append(joker)

        return jokers

    @staticmethod
    def load_by_priority(csv_path: str, priority: str) -> List[JokerResource]:
        """
        Load jokers filtered by priority (e.g., 'P0', 'P1', 'P2').

        Args:
            csv_path: Path to CSV file
            priority: Priority to filter by (e.g., 'P0')

        Returns:
            List of JokerResource objects matching priority
        """
        jokers = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty rows
                if not row.get('id') or not row['id'].strip():
                    continue

                # Filter by priority
                if row.get('priority', '').strip() == priority:
                    joker = JokerResource(
                        id=row['id'].strip(),
                        name=row['name'].strip(),
                        effect_type=row['effect_type'].strip(),
                        trigger=row['trigger'].strip(),
                        condition_type=row['condition_type'].strip(),
                        condition_value=row['condition_value'].strip(),
                        bonus_type=row['bonus_type'].strip(),
                        bonus_value=JokerLoader._parse_bonus_value(row['bonus_value']),
                        per_card=JokerLoader._parse_bool(row['per_card']),
                        grow_per=row['grow_per'].strip() if row['grow_per'].strip() else None,
                        rarity=row['rarity'].strip(),
                        cost=int(row['cost'].strip()),
                        notes=row['notes'].strip() if row.get('notes') else ""
                    )
                    jokers.append(joker)

        return jokers

    @staticmethod
    def load_by_id(csv_path: str, joker_id: str) -> JokerResource:
        """
        Load a single joker by ID.

        Args:
            csv_path: Path to CSV file
            joker_id: Joker ID (e.g., 'j_001')

        Returns:
            JokerResource or None if not found
        """
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row.get('id', '').strip() == joker_id:
                    return JokerResource(
                        id=row['id'].strip(),
                        name=row['name'].strip(),
                        effect_type=row['effect_type'].strip(),
                        trigger=row['trigger'].strip(),
                        condition_type=row['condition_type'].strip(),
                        condition_value=row['condition_value'].strip(),
                        bonus_type=row['bonus_type'].strip(),
                        bonus_value=JokerLoader._parse_bonus_value(row['bonus_value']),
                        per_card=JokerLoader._parse_bool(row['per_card']),
                        grow_per=row['grow_per'].strip() if row['grow_per'].strip() else None,
                        rarity=row['rarity'].strip(),
                        cost=int(row['cost'].strip()),
                        notes=row['notes'].strip() if row.get('notes') else ""
                    )

        return None

    @staticmethod
    def _parse_bonus_value(value_str: str) -> float:
        """
        Parse bonus_value from CSV.

        Handles:
        - Simple numbers: "4" -> 4.0
        - Decimals: "2.5" -> 2.5
        - Special formats: "20c4m" -> 20c4m (as string converted to float for ++ type)

        Note: For "++" bonus_type, bonus_value stays as string (e.g., "20c4m")
        and is parsed in joker_manager._apply_effect().
        """
        value_str = value_str.strip()

        # Handle special formats (++, Xm with letters)
        if 'c' in value_str or 'm' in value_str or 'x' in value_str.lower():
            # Keep as string for complex parsing later
            # But we need to return float, so return the string as-is
            # Actually, JokerResource expects float, but we handle "20c4m" specially
            return value_str

        # Simple numeric value
        try:
            return float(value_str)
        except ValueError:
            # Fallback for unexpected formats
            return 0.0

    @staticmethod
    def _parse_bool(value_str: str) -> bool:
        """
        Parse boolean from CSV.

        Accepts: "yes", "true", "1" -> True
                "no", "false", "0", "" -> False
        """
        value_str = value_str.strip().lower()
        return value_str in ['yes', 'true', '1']

    @staticmethod
    def get_default_csv_path() -> str:
        """Get default path to jokers_structured.csv."""
        # From project root: data/jokers_structured.csv
        # This assumes the script is run from project root
        return str(Path(__file__).parent.parent.parent / "data" / "jokers_structured.csv")

    @staticmethod
    def load_all_jokers() -> List[JokerResource]:
        """Load all jokers from default CSV location."""
        return JokerLoader.load_from_csv(JokerLoader.get_default_csv_path())

    @staticmethod
    def load_p0_jokers() -> List[JokerResource]:
        """Load all P0 priority jokers from default CSV location."""
        return JokerLoader.load_by_priority(JokerLoader.get_default_csv_path(), 'P0')
