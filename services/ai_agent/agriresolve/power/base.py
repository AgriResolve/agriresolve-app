"""
Power Layer Base Interfaces for AgriResolve.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PowerLayerNotConfiguredError(Exception):
    """
    Raised when NVIDIA Nemotron / Meterless credentials or endpoints are unconfigured.
    """
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            message
            or (
                "Power Layer (NVIDIA Nemotron / Meterless) is not configured. Missing NVIDIA_API_KEY. "
                "Per project rules, please provide your NVIDIA/Meterless API key in .env."
            )
        )


class PowerLayerClient(ABC):
    """
    Abstract interface for LLM reasoning and qualitative interpretation.
    """

    @abstractmethod
    def generate_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """
        Submits prompt to model and returns raw text response.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Returns True if live credentials are configured.
        """
        pass
