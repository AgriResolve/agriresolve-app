"""
Configuration module for AgriResolve.
Reads settings from environment variables and provides policy limits and connection settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load local .env file if available
load_dotenv()


@dataclass(frozen=True)
class PowerLayerConfig:
    api_key: Optional[str]
    base_url: str
    model: str
    timeout_seconds: float

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"))


@dataclass(frozen=True)
class ZetarisConfig:
    endpoint: Optional[str]
    api_key: Optional[str]
    catalog: str
    schema: str

    @property
    def is_configured(self) -> bool:
        return bool(
            self.endpoint
            and not self.endpoint.startswith("https://zetaris.example.com")
            and self.api_key
            and not self.api_key.startswith("your_")
        )


@dataclass(frozen=True)
class InvestigationPolicy:
    max_investigation_steps: int = 6
    max_tool_calls_per_step: int = 4
    require_deterministic_calc: bool = True
    allow_unverified_financials: bool = False


@dataclass(frozen=True)
class AgriResolveConfig:
    power: PowerLayerConfig
    zetaris: ZetarisConfig
    policy: InvestigationPolicy

    @classmethod
    def from_env(cls) -> AgriResolveConfig:
        power = PowerLayerConfig(
            api_key=os.getenv("NVIDIA_API_KEY"),
            base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
            model=os.getenv("NVIDIA_MODEL", "nvidia/nemotron-4-340b-instruct"),
            timeout_seconds=float(os.getenv("NVIDIA_TIMEOUT_SECONDS", "60.0")),
        )
        zetaris = ZetarisConfig(
            endpoint=os.getenv("ZETARIS_ENDPOINT"),
            api_key=os.getenv("ZETARIS_API_KEY"),
            catalog=os.getenv("ZETARIS_CATALOG", "agri_lakehouse"),
            schema=os.getenv("ZETARIS_SCHEMA", "disputes_gold"),
        )
        policy = InvestigationPolicy(
            max_investigation_steps=int(os.getenv("MAX_INVESTIGATION_STEPS", "6")),
            max_tool_calls_per_step=int(os.getenv("MAX_TOOL_CALLS_PER_STEP", "4")),
        )
        return cls(power=power, zetaris=zetaris, policy=policy)
