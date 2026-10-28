"""
Stable ID generation module per Meterless World Model specification.
IDs are deterministic, content-addressed, and never renumbered.
Same input -> same ID. Survives re-imports and schema migrations.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional


def canonical_json_string(data: Any) -> str:
    """
    Serializes data to a deterministic, sorted, whitespace-normalized string.
    """
    if isinstance(data, dict):
        return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    elif isinstance(data, (list, tuple)):
        return json.dumps(data, separators=(",", ":"), default=str)
    else:
        return str(data).strip().lower()


def compute_content_checksum(data: Any) -> str:
    """
    Computes a sha256 checksum over arbitrary content for provenance tracking.
    """
    raw = canonical_json_string(data).encode("utf-8")
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def compute_stable_entity_id(entity_type: str, canonical_key: str) -> str:
    """
    Computes a stable content-addressed entity ID:
        id = {entity_type}:{hash(entity_type + canonical_key)}
    """
    clean_type = entity_type.strip().lower()
    clean_key = canonical_key.strip().lower()
    payload = f"{clean_type}:{clean_key}".encode("utf-8")
    hash_digest = hashlib.sha256(payload).hexdigest()[:16]
    # Human-readable slug prefix if key is simple alphanumeric
    slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in clean_key)[:24].strip("_-")
    if slug:
        return f"{clean_type}:{slug}_{hash_digest[:8]}"
    return f"{clean_type}:{hash_digest}"


def compute_stable_context_id(context_type: str, canonical_key: str, parent_id: Optional[str] = None) -> str:
    """
    Computes a stable context ID:
        id = {context_type}:{hash(context_type + canonical_key + parent?)}
    """
    clean_type = context_type.strip().lower()
    clean_key = canonical_key.strip().lower()
    payload = f"{clean_type}:{clean_key}:{parent_id or 'root'}".encode("utf-8")
    hash_digest = hashlib.sha256(payload).hexdigest()[:16]
    slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in clean_key)[:24].strip("_-")
    if slug:
        return f"ctx_{clean_type}:{slug}_{hash_digest[:8]}"
    return f"ctx_{clean_type}:{hash_digest}"


def compute_stable_relationship_id(
    from_id: str,
    rel_type: str,
    to_id: str,
    context_id: Optional[str] = None,
) -> str:
    """
    Computes a stable relationship ID:
        id = rel_{hash(from + type + to + context)}
    """
    payload = f"{from_id}:{rel_type}:{to_id}:{context_id or 'global'}".encode("utf-8")
    hash_digest = hashlib.sha256(payload).hexdigest()[:16]
    return f"rel_{hash_digest}"
