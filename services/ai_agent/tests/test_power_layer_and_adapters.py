"""
Tests for Power Layer and Adapter integration boundaries.
"""

import pytest
from agriresolve.adapters.zetaris import ZetarisAdapter, ZetarisNotConfiguredError
from agriresolve.config import PowerLayerConfig, ZetarisConfig
from agriresolve.power.base import PowerLayerNotConfiguredError
from agriresolve.power.mock_provider import MockNemotronPowerClient
from agriresolve.power.nemotron import NemotronPowerClient


def test_nemotron_power_client_unconfigured_raises():
    unconfigured_config = PowerLayerConfig(
        api_key=None,
        base_url="https://integrate.api.nvidia.com/v1",
        model="nvidia/nemotron-4-340b-instruct",
        timeout_seconds=30.0,
    )
    client = NemotronPowerClient(unconfigured_config)
    assert client.is_available() is False

    with pytest.raises(PowerLayerNotConfiguredError) as exc:
        client.generate_reasoning("test prompt")
    assert "Missing NVIDIA_API_KEY" in str(exc.value)


def test_zetaris_adapter_unconfigured_raises():
    unconfigured_zetaris = ZetarisConfig(
        endpoint=None,
        api_key=None,
        catalog="agri_lakehouse",
        schema="disputes_gold",
    )
    adapter = ZetarisAdapter(unconfigured_zetaris)
    assert adapter.config.is_configured is False

    with pytest.raises(ZetarisNotConfiguredError) as exc:
        adapter.fetch_dispute_evidence("DISP-001")
    assert "Zetaris integration is not configured" in str(exc.value)


def test_mock_power_client():
    mock_client = MockNemotronPowerClient()
    assert mock_client.is_available() is True
    res = mock_client.generate_reasoning("test prompt")
    assert len(res) > 20
    assert len(mock_client.call_history) == 1
