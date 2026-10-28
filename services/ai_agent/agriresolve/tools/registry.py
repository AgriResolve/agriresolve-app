"""
Controlled Tool Registry and Execution Policy Engine for AgriResolve.
Enforces per-step tool call limits, total investigation bounds, and logs invocations.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ..config import InvestigationPolicy
from .base import BaseTool, ToolResult

logger = logging.getLogger("agriresolve.tools")


class PolicyLimitExceededError(Exception):
    """Raised when investigation steps or tool invocations exceed configured safety bounds."""
    pass


class ToolRegistry:
    """
    Manages controlled tools and enforces execution guardrails.
    """

    def __init__(self, policy: Optional[InvestigationPolicy] = None):
        self.policy = policy or InvestigationPolicy()
        self._tools: Dict[str, BaseTool] = {}
        self.call_history: List[Dict[str, Any]] = []
        self._calls_in_current_step: int = 0
        self._total_steps_executed: int = 0

    def register_tool(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def reset_session(self) -> None:
        """
        Resets per-session execution counters for a new investigation workflow.
        """
        self._total_steps_executed = 0
        self._calls_in_current_step = 0

    def start_new_step(self) -> None:
        """
        Advances the investigation step counter and resets per-step call count.
        """
        if self._total_steps_executed >= self.policy.max_investigation_steps:
            raise PolicyLimitExceededError(
                f"Maximum investigation steps ({self.policy.max_investigation_steps}) reached. Bounding execution to prevent endless loops."
            )
        self._total_steps_executed += 1
        self._calls_in_current_step = 0

    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Executes a controlled tool subject to policy checks.
        """
        if self._calls_in_current_step >= self.policy.max_tool_calls_per_step:
            raise PolicyLimitExceededError(
                f"Maximum permitted tool calls per step ({self.policy.max_tool_calls_per_step}) exceeded."
            )

        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' is not an authorized or registered controlled tool.",
            )

        self._calls_in_current_step += 1
        result = tool.execute(**kwargs)

        self.call_history.append({
            "step": self._total_steps_executed,
            "tool": tool_name,
            "success": result.success,
            "error": result.error,
        })
        return result
