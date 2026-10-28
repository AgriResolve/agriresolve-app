"""
AgriResolve: Autonomous AI Agricultural Dispute Investigation Agent.
Role 1: Agent & Power Lead component package.
"""

from .config import AgriResolveConfig, PowerLayerConfig, ZetarisConfig, InvestigationPolicy
from .investigator import AgriResolveInvestigator
from .models.enums import InvestigationState, DisputeCategory, EvidenceType
from .models.investigation import InvestigationReport
from .world_model.engine import WorldModel

__version__ = "0.1.0"

__all__ = [
    "AgriResolveInvestigator",
    "AgriResolveConfig",
    "PowerLayerConfig",
    "ZetarisConfig",
    "InvestigationPolicy",
    "InvestigationState",
    "DisputeCategory",
    "EvidenceType",
    "InvestigationReport",
    "WorldModel",
]
