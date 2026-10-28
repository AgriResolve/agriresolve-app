"""
Tests for AgriculturalCalculator deterministic mathematical engine.
"""

import pytest
from agriresolve.engine.calculator import AgriculturalCalculator, CalculationError


def test_unit_conversion_kg_and_mt():
    assert AgriculturalCalculator.convert_to_kg(10.0, "MT") == 10000.0
    assert AgriculturalCalculator.convert_to_kg(500.0, "kg") == 500.0
    assert AgriculturalCalculator.convert_to_kg(2.5, "metric_ton") == 2500.0

    with pytest.raises(CalculationError):
        AgriculturalCalculator.convert_to_kg(100.0, "bushels_unverified")


def test_weight_variance_calculation():
    step = AgriculturalCalculator.calculate_weight_variance(
        contract_qty=10000.0,
        contract_unit="kg",
        delivered_qty=9100.0,
        delivered_unit="kg",
    )
    assert step.result == -900.0
    assert step.unit == "kg"
    assert step.inputs["percentage_variance"] == -9.0
    assert step.is_verified is True


def test_tolerance_check():
    # 10,000 kg +/- 2% allows 9,800 to 10,200 kg
    within, step = AgriculturalCalculator.check_tolerance(
        contract_qty_kg=10000.0,
        delivered_qty_kg=9900.0,
        tolerance_pct=2.0,
        source_term_ref="Clause 3",
    )
    assert within is True
    assert step.inputs["within_tolerance"] is True

    # 9,100 kg is outside 2% tolerance
    outside, step2 = AgriculturalCalculator.check_tolerance(
        contract_qty_kg=10000.0,
        delivered_qty_kg=9100.0,
        tolerance_pct=2.0,
        source_term_ref="Clause 3",
    )
    assert outside is False
    assert step2.inputs["within_tolerance"] is False


def test_moisture_shrinkage_minary_formula():
    """
    Standard Minary Formula:
    Delivered weight = 9,100 kg
    Actual moisture = 16.0%
    Base moisture = 12.0%
    Dry matter factor = (100 - 16) / (100 - 12) = 84 / 88 = 0.954545...
    Adjusted weight = 9100 * (84/88) = 8686.36 kg
    """
    step = AgriculturalCalculator.calculate_moisture_shrinkage(
        delivered_weight_kg=9100.0,
        actual_moisture_pct=16.0,
        contract_base_moisture_pct=12.0,
    )
    assert round(step.result, 2) == 8686.36
    assert step.inputs["total_shrinkage_kg"] == round(9100.0 - 8686.36, 2)
    assert step.is_verified is True

    # Invalid moisture boundaries
    with pytest.raises(CalculationError):
        AgriculturalCalculator.calculate_moisture_shrinkage(9100.0, 105.0, 12.0)
    with pytest.raises(CalculationError):
        AgriculturalCalculator.calculate_moisture_shrinkage(9100.0, -2.0, 12.0)


def test_verified_financial_impact():
    # 8686.36 kg at $0.30/kg
    step = AgriculturalCalculator.calculate_verified_financial_impact(
        settlement_weight_kg=8686.36,
        contract_price_per_unit=0.30,
        price_unit="kg",
        penalty_deduction=0.0,
        currency="USD",
    )
    assert step.result == round(8686.36 * 0.30, 2)
    assert step.unit == "USD"
