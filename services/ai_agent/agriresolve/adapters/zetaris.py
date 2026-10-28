"""
Zetaris Data Layer Adapter for AgriResolve.
Provides read-only, dispute-scoped access to the teammate-owned Zetaris lakehouse.
If unconfigured, raises an informative error without fabricating records.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional
from ..config import ZetarisConfig
from ..models.enums import EvidenceType
from ..models.evidence import EvidenceItem
from ..security.guardrails import DisputeGuardrail


class ZetarisNotConfiguredError(Exception):
    """
    Raised when live Zetaris credentials or endpoints are unconfigured.
    """
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            message
            or (
                "Zetaris integration is not configured. Missing ZETARIS_ENDPOINT and/or ZETARIS_API_KEY. "
                "Per project rules, please obtain these credentials from the Data Lead teammate."
            )
        )


class ZetarisAdapter:
    """
    Read-only adapter for querying disputes data from Zetaris lakehouse.
    """

    def __init__(self, config: ZetarisConfig):
        self.config = config

    def _execute_query(self, endpoint_path: str, dispute_id: str) -> List[Dict[str, Any]]:
        """
        Executes a scoped read-only request to the Zetaris lakehouse API.
        """
        if not self.config.is_configured:
            raise ZetarisNotConfiguredError()

        # Enforce dispute ID format and isolation
        DisputeGuardrail.validate_dispute_id(dispute_id)

        url = f"{self.config.endpoint.rstrip('/')}/{endpoint_path.lstrip('/')}?dispute_id={dispute_id}&catalog={self.config.catalog}&schema={self.config.schema}"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Accept": "application/json",
            "User-Agent": "AgriResolve-Agent/0.1.0",
        }

        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("records", [])
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Zetaris API HTTP error: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Zetaris endpoint: {e.reason}")

    def fetch_dispute_evidence(self, dispute_id: str) -> List[EvidenceItem]:
        """
        Retrieves all evidence associated with a dispute from Zetaris lakehouse.
        """
        records = self._execute_query("evidence", dispute_id)
        evidence_items: List[EvidenceItem] = []

        for rec in records:
            ev_type_str = rec.get("evidence_type", "").lower()
            try:
                ev_type = EvidenceType(ev_type_str)
            except ValueError:
                ev_type = EvidenceType.STANDARD

            item = EvidenceItem(
                source_id=rec.get("source_id", "UNKNOWN"),
                evidence_type=ev_type,
                dispute_id=dispute_id,
                title=rec.get("title", "Zetaris Record"),
                recorded_at=rec.get("recorded_at"),
                author_or_issuer=rec.get("author_or_issuer", "Zetaris Data Lake"),
                structured_data=rec.get("structured_data", {}),
                raw_content=rec.get("raw_content", ""),
                is_synthetic=False,  # Live data is not synthetic
                is_untrusted_input=True,
            )
            item.add_provenance(f"Retrieved from Zetaris lakehouse (catalog={self.config.catalog}, schema={self.config.schema})")
            evidence_items.append(item)

        return evidence_items
