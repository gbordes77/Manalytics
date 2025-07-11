"""
Validation result classes for schema and data validation.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    QUARANTINE = "quarantine"


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    issues: List[str]
    severity: str
    details: Optional[dict] = None
    
    def __post_init__(self):
        """Validate severity level."""
        if self.severity not in [s.value for s in ValidationSeverity]:
            raise ValueError(f"Invalid severity: {self.severity}")
    
    def add_issue(self, issue: str):
        """Add a validation issue."""
        self.issues.append(issue)
        if self.is_valid and self.severity in ['error', 'critical', 'quarantine']:
            self.is_valid = False
    
    def get_severity_level(self) -> ValidationSeverity:
        """Get severity as enum."""
        return ValidationSeverity(self.severity)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'is_valid': self.is_valid,
            'issues': self.issues,
            'severity': self.severity,
            'details': self.details
        } 