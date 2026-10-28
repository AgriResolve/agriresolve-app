"""
Security Guardrails: Dispute scoping, ID validation, and access control.
"""

from __future__ import annotations

import re


DISPUTE_ID_REGEX = re.compile(r"^[A-Za-z0-9_\-\.]{3,64}$")
FORBIDDEN_QUERY_CHARACTERS = re.compile(r"['\";\-\-/\\]")


class SecurityError(Exception):
    """Raised when an unauthorized access or security violation occurs."""
    pass


class DisputeGuardrail:
    """
    Validates dispute identifiers and ensures queries do not violate tenant or dispute isolation.
    """

    @classmethod
    def validate_dispute_id(cls, dispute_id: str) -> str:
        """
        Validates dispute ID format. Raises SecurityError if invalid or suspicious.
        """
        if not dispute_id or not isinstance(dispute_id, str):
            raise SecurityError("Dispute ID must be a non-empty string.")

        dispute_id = dispute_id.strip()

        # Check for path traversal or SQL injection indicators
        if ".." in dispute_id or "/" in dispute_id or "\\" in dispute_id:
            raise SecurityError(f"Directory traversal or invalid path character detected in dispute_id: {dispute_id}")

        if any(term in dispute_id.upper() for term in ["SELECT", "DROP", "UNION", "OR 1=1", "--"]):
            raise SecurityError(f"SQL injection attempt detected in dispute_id: {dispute_id}")

        if not DISPUTE_ID_REGEX.match(dispute_id):
            raise SecurityError(f"Invalid dispute ID format: '{dispute_id}'. Must be 3-64 alphanumeric characters, dashes, dots, or underscores.")

        return dispute_id

    @classmethod
    def assert_same_dispute(cls, active_dispute_id: str, requested_dispute_id: str) -> None:
        """
        Enforces that queries or evidence processing only touch the active authorized dispute.
        """
        active = cls.validate_dispute_id(active_dispute_id)
        requested = cls.validate_dispute_id(requested_dispute_id)

        if active != requested:
            raise SecurityError(
                f"Unauthorized access: Current investigation is scoped to dispute '{active}', "
                f"but query requested dispute '{requested}'."
            )
