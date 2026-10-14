from enum import Enum

from pydantic import BaseModel


class ValidationSeverity(str, Enum):
    error = "error"
    warning = "warning"


class ValidationIssue(BaseModel):
    rule_id: str
    severity: ValidationSeverity
    message: str
    field: str | None = None
