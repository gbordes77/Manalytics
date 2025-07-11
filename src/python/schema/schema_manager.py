"""
Schema manager for handling evolving data formats with auto-detection.
"""

from typing import Dict, Any, Optional
import logging
from .schema_versions import MTGOSchemaV1, MTGOSchemaV2, MeleeSchemaV1, BaseSchema
from .validation_result import ValidationResult

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages different schema versions and auto-detects appropriate schema."""
    
    def __init__(self):
        """Initialize schema manager with available schemas."""
        self.schemas = {
            'mtgo_v1': MTGOSchemaV1(),
            'mtgo_v2': MTGOSchemaV2(),
            'melee_v1': MeleeSchemaV1()
        }
        
        # Detection patterns for each schema
        self.detection_patterns = {
            'melee_v1': {
                'required_fields': ['id', 'name', 'startDate'],
                'signature_fields': ['matchups', 'swiss_rounds'],
                'unique_fields': ['playerCount', 'swissRounds']
            },
            'mtgo_v2': {
                'required_fields': ['tournament_id', 'tournament_name', 'standings'],
                'signature_fields': ['companion'],
                'unique_fields': ['elimination_rounds', 'color_identity']
            },
            'mtgo_v1': {
                'required_fields': ['id', 'name', 'date', 'players'],
                'signature_fields': ['player_count', 'swiss_rounds'],
                'unique_fields': ['playoff_rounds']
            }
        }
    
    def detect_schema_version(self, data: Dict[str, Any], source: Optional[str] = None) -> str:
        """
        Auto-detect the schema version based on data structure.
        
        Args:
            data: Raw tournament data
            source: Optional source hint ('mtgo', 'melee', 'topdeck')
            
        Returns:
            Schema version identifier
        """
        try:
            # If source is provided, narrow down candidates
            if source:
                candidates = [k for k in self.schemas.keys() if k.startswith(source.lower())]
            else:
                candidates = list(self.schemas.keys())
            
            best_match = None
            best_score = 0
            
            for schema_name in candidates:
                score = self._calculate_schema_score(data, schema_name)
                logger.debug(f"Schema {schema_name} score: {score}")
                
                if score > best_score:
                    best_score = score
                    best_match = schema_name
            
            if best_match and best_score > 0.5:  # Minimum confidence threshold
                logger.info(f"Detected schema: {best_match} (confidence: {best_score:.2f})")
                return best_match
            
            # Fallback logic based on specific field patterns
            return self._fallback_detection(data, source)
            
        except Exception as e:
            logger.error(f"Error detecting schema version: {e}")
            return self._get_default_schema(source)
    
    def _calculate_schema_score(self, data: Dict[str, Any], schema_name: str) -> float:
        """Calculate confidence score for a schema match."""
        pattern = self.detection_patterns.get(schema_name, {})
        score = 0.0
        total_checks = 0
        
        # Check required fields
        required_fields = pattern.get('required_fields', [])
        if required_fields:
            required_score = sum(1 for field in required_fields if field in data) / len(required_fields)
            score += required_score * 0.4  # 40% weight for required fields
            total_checks += 0.4
        
        # Check signature fields (strong indicators)
        signature_fields = pattern.get('signature_fields', [])
        if signature_fields:
            signature_score = sum(1 for field in signature_fields if self._field_exists_deep(data, field)) / len(signature_fields)
            score += signature_score * 0.4  # 40% weight for signature fields
            total_checks += 0.4
        
        # Check unique fields (differentiators)
        unique_fields = pattern.get('unique_fields', [])
        if unique_fields:
            unique_score = sum(1 for field in unique_fields if self._field_exists_deep(data, field)) / len(unique_fields)
            score += unique_score * 0.2  # 20% weight for unique fields
            total_checks += 0.2
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _field_exists_deep(self, data: Dict[str, Any], field: str) -> bool:
        """Check if field exists in data or nested structures."""
        if field in data:
            return True
        
        # Check in nested structures
        for value in data.values():
            if isinstance(value, dict) and field in value:
                return True
            elif isinstance(value, list) and value:
                if isinstance(value[0], dict) and field in value[0]:
                    return True
        
        return False
    
    def _fallback_detection(self, data: Dict[str, Any], source: Optional[str]) -> str:
        """Fallback detection logic for edge cases."""
        # Melee-specific patterns
        if 'matchups' in data and 'swiss_rounds' in data:
            return 'melee_v1'
        
        # MTGO v2 specific patterns
        if any(self._field_exists_deep(data, field) for field in ['companion', 'color_identity']):
            return 'mtgo_v2'
        
        # MTGO v1 patterns
        if 'players' in data and 'player_count' in data:
            return 'mtgo_v1'
        
        return self._get_default_schema(source)
    
    def _get_default_schema(self, source: Optional[str]) -> str:
        """Get default schema based on source."""
        if source == 'melee':
            return 'melee_v1'
        elif source == 'mtgo':
            return 'mtgo_v1'
        else:
            return 'mtgo_v1'  # Default fallback
    
    def normalize_data(self, data: Dict[str, Any], source: Optional[str] = None) -> Dict[str, Any]:
        """
        Normalize data to unified format.
        
        Args:
            data: Raw tournament data
            source: Optional source hint
            
        Returns:
            Normalized data in unified format
        """
        try:
            schema_version = self.detect_schema_version(data, source)
            schema = self.schemas[schema_version]
            
            logger.info(f"Normalizing data using schema: {schema_version}")
            normalized = schema.normalize(data)
            
            # Add schema detection metadata
            normalized['schema_detection'] = {
                'detected_version': schema_version,
                'source_hint': source,
                'detection_confidence': self._calculate_schema_score(data, schema_version)
            }
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing data: {e}")
            raise
    
    def validate_data(self, data: Dict[str, Any], source: Optional[str] = None) -> ValidationResult:
        """
        Validate data against appropriate schema.
        
        Args:
            data: Raw tournament data
            source: Optional source hint
            
        Returns:
            ValidationResult with validation status and issues
        """
        try:
            schema_version = self.detect_schema_version(data, source)
            schema = self.schemas[schema_version]
            
            is_valid = schema.validate(data)
            issues = []
            
            if not is_valid:
                issues.append(f"Data does not conform to {schema_version} schema")
            
            # Additional validation checks
            validation_issues = self._perform_additional_validation(data, schema_version)
            issues.extend(validation_issues)
            
            severity = 'error' if not is_valid else ('warning' if issues else 'info')
            
            return ValidationResult(
                is_valid=is_valid and len(validation_issues) == 0,
                issues=issues,
                severity=severity,
                details={
                    'schema_version': schema_version,
                    'validation_checks': len(validation_issues) + 1
                }
            )
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return ValidationResult(
                is_valid=False,
                issues=[f"Validation error: {str(e)}"],
                severity='error'
            )
    
    def _perform_additional_validation(self, data: Dict[str, Any], schema_version: str) -> list:
        """Perform additional validation checks beyond basic schema validation."""
        issues = []
        
        # Check for empty or missing critical data
        if not data.get('players') and not data.get('standings'):
            issues.append("No player/standings data found")
        
        # Check date validity
        date_field = 'date' if 'date' in data else 'startDate'
        if date_field in data:
            try:
                from datetime import datetime
                if isinstance(data[date_field], str):
                    # Try to parse the date
                    datetime.fromisoformat(data[date_field].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                issues.append(f"Invalid date format: {data[date_field]}")
        
        # Check for reasonable player count
        player_count = (len(data.get('players', [])) or 
                       len(data.get('standings', [])) or 
                       data.get('playerCount', 0) or 
                       data.get('player_count', 0))
        
        if player_count == 0:
            issues.append("No players found in tournament")
        elif player_count > 10000:  # Sanity check
            issues.append(f"Unusually high player count: {player_count}")
        
        return issues
    
    def get_schema(self, schema_version: str) -> Optional[BaseSchema]:
        """Get schema instance by version."""
        return self.schemas.get(schema_version)
    
    def list_schemas(self) -> Dict[str, str]:
        """List all available schemas with descriptions."""
        return {
            name: schema.get_version() 
            for name, schema in self.schemas.items()
        }
    
    def add_schema(self, name: str, schema: BaseSchema):
        """Add a new schema version."""
        self.schemas[name] = schema
        logger.info(f"Added new schema: {name}")
    
    def get_schema_stats(self) -> Dict[str, Any]:
        """Get statistics about schema usage and detection."""
        return {
            'total_schemas': len(self.schemas),
            'available_schemas': list(self.schemas.keys()),
            'detection_patterns': len(self.detection_patterns)
        } 