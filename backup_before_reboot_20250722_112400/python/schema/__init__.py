"""
Schema management module for handling evolving data formats.
"""

from .schema_manager import SchemaManager
from .schema_versions import MeleeSchemaV1, MTGOSchemaV1, MTGOSchemaV2
from .validation_result import ValidationResult

__all__ = [
    "SchemaManager",
    "MTGOSchemaV1",
    "MTGOSchemaV2",
    "MeleeSchemaV1",
    "ValidationResult",
]
