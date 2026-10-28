"""
Deterministic Mock / Stub Power Client for testing and evaluation.
Explicitly labeled as MOCK to satisfy anti-fabrication guidelines.
"""

from __future__ import annotations

from typing import Callable, Optional
from .base import PowerLayerClient


class MockNemotronPowerClient(PowerLayerClient):
    """
    Simulated Nemotron client for deterministic testing of error handling,
    malformed output recovery, and pipeline execution without API keys.
    """

    def __init__(self, response_generator: Optional[Callable[[str], str]] = None):
        self.response_generator = response_generator
        self.call_history = []

    def is_available(self) -> bool:
        return True

    def generate_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        self.call_history.append({"prompt": prompt, "system_prompt": system_prompt})
        if self.response_generator:
            return self.response_generator(prompt)
        return (
            "Based on the documentary records, Contract CTR-2026-M101 specifies 10,000 kg maize at 12.0% moisture. "
            "Weighbridge GRN-2026-881 certifies 9,100 kg delivered. Laboratory report QC-2026-402 establishes 16.0% moisture. "
            "The contractual Minary formula dictates a moisture shrinkage deduction. However, the buyer's arbitrary $180 "
            "penalty is not supported by contract terms."
        )
