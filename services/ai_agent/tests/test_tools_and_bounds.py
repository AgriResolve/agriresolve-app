"""
Tests for Tool Registry, Controlled Execution, and Policy Bounds.
"""

import pytest
from agriresolve.config import InvestigationPolicy
from agriresolve.tools.base import BaseTool, ToolResult
from agriresolve.tools.registry import PolicyLimitExceededError, ToolRegistry


class DummyEchoTool(BaseTool):
    name = "dummy_echo"
    description = "Echoes inputs for testing."

    def execute(self, message: str = "", **kwargs) -> ToolResult:
        return ToolResult(tool_name=self.name, success=True, data=message)


def test_tool_registration_and_execution():
    registry = ToolRegistry(InvestigationPolicy(max_investigation_steps=5, max_tool_calls_per_step=3))
    registry.register_tool(DummyEchoTool())

    assert registry.get_tool("dummy_echo") is not None
    assert registry.get_tool("nonexistent") is None

    registry.start_new_step()
    res = registry.execute_tool("dummy_echo", message="hello agriresolve")
    assert res.success is True
    assert res.data == "hello agriresolve"


def test_max_tool_calls_per_step_limit():
    policy = InvestigationPolicy(max_investigation_steps=5, max_tool_calls_per_step=2)
    registry = ToolRegistry(policy)
    registry.register_tool(DummyEchoTool())

    registry.start_new_step()
    registry.execute_tool("dummy_echo", message="call 1")
    registry.execute_tool("dummy_echo", message="call 2")

    with pytest.raises(PolicyLimitExceededError) as exc:
        registry.execute_tool("dummy_echo", message="call 3")
    assert "Maximum permitted tool calls per step" in str(exc.value)


def test_max_investigation_steps_limit():
    policy = InvestigationPolicy(max_investigation_steps=2, max_tool_calls_per_step=3)
    registry = ToolRegistry(policy)
    registry.register_tool(DummyEchoTool())

    registry.start_new_step()  # Step 1
    registry.start_new_step()  # Step 2

    with pytest.raises(PolicyLimitExceededError) as exc:
        registry.start_new_step()  # Step 3 exceeds max
    assert "Maximum investigation steps" in str(exc.value)
