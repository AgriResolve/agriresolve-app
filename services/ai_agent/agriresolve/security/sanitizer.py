"""
Security and Input Sanitization Module for AgriResolve.
Detects and neutralizes prompt injection in untrusted evidence and documents.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Patterns commonly used in prompt injection attacks within agricultural documents or party claims
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|directives|prompts)", re.IGNORECASE),
    re.compile(r"disregard\s+(the\s+)?(contract|rules|guidelines|instructions)", re.IGNORECASE),
    re.compile(r"(system\s+override|administrator\s+mode|developer\s+mode|god\s+mode)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(an?\s+)?unrestricted", re.IGNORECASE),
    re.compile(r"reveal\s+(all\s+)?(confidential|secrets|api\s*keys|passwords)", re.IGNORECASE),
    re.compile(r"output\s+the\s+(system\s+prompt|initial\s+prompt)", re.IGNORECASE),
    re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"\[\s*system\s*:\s*execute", re.IGNORECASE),
    re.compile(r"rule\s+violation:\s*force\s+finding", re.IGNORECASE),
]


class EvidenceSanitizer:
    """
    Sanitizes untrusted evidence to prevent prompt injection and unauthorized command execution.
    """

    @classmethod
    def inspect_and_defuse(cls, text: str) -> Tuple[str, bool, List[str]]:
        """
        Scans text for prompt injection patterns.
        Returns:
            (defused_text, injection_detected, detected_patterns)
        """
        if not text:
            return "", False, []

        detected: List[str] = []
        for pattern in PROMPT_INJECTION_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                detected.append(pattern.pattern)

        if not detected:
            return text, False, []

        # Defuse by neutralizing injection commands and wrapping in strict quoted untrusted data block
        defused = text
        for pattern in PROMPT_INJECTION_PATTERNS:
            defused = pattern.sub("[POTENTIAL_PROMPT_INJECTION_DEFUSED]", defused)

        return defused, True, detected

    @classmethod
    def wrap_as_untrusted_data(cls, text: str, source_id: str) -> str:
        """
        Wraps content in explicit untrusted data markers so the LLM power layer
        processes it strictly as passive documentary evidence rather than operational commands.
        """
        defused, flagged, _ = cls.inspect_and_defuse(text)
        flag_banner = "\n[SECURITY WARNING: Potential prompt injection sequence detected and defused in this document]" if flagged else ""
        return (
            f"<untrusted_document_evidence source_id='{source_id}'>{flag_banner}\n"
            f"{defused}\n"
            f"</untrusted_document_evidence>"
        )
