"""
Deterministic Agricultural Calculation Engine for AgriResolve.
Performs verifiable calculations for weight, moisture shrinkage, unit conversion, and financial adjustments.
Never guesses formulas or applies unauthorized financial penalties.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from ..models.investigation import CalculationStep


class CalculationError(Exception):
    """Raised when calculation inputs are invalid or units are incompatible."""
    pass


class AgriculturalCalculator:
    """
    Deterministic mathematical operations for grain quantity and moisture disputes.
    """

    @classmethod
    def convert_to_kg(cls, value: float, unit: str) -> float:
        """
        Converts quantity to kilograms. Supported: 'kg', 'MT', 'metric_ton', 'tons', 'tonnes'.
        """
        u = unit.strip().lower()
        if u in ("kg", "kilogram", "kilograms"):
            return float(value)
        elif u in ("mt", "metric_ton", "metric_tons", "tons", "tonnes", "t"):
            return float(value) * 1000.0
        else:
            raise CalculationError(f"Unsupported or unverified unit for mass conversion: '{unit}'")

    @classmethod
    def calculate_weight_variance(
        cls,
        contract_qty: float,
        contract_unit: str,
        delivered_qty: float,
        delivered_unit: str,
        source_term_ref: str = "Contractual delivery specifications",
    ) -> CalculationStep:
        """
        Calculates the raw weight variance (Delivered - Contract).
        Negative result indicates a delivery shortfall.
        """
        contract_kg = cls.convert_to_kg(contract_qty, contract_unit)
        delivered_kg = cls.convert_to_kg(delivered_qty, delivered_unit)
        variance_kg = delivered_kg - contract_kg
        pct_variance = (variance_kg / contract_kg) * 100.0 if contract_kg > 0 else 0.0

        return CalculationStep(
            calculation_name="Weight Variance Calculation",
            formula="delivered_quantity_kg - contract_quantity_kg",
            inputs={
                "contract_quantity_original": contract_qty,
                "contract_unit": contract_unit,
                "contract_quantity_kg": contract_kg,
                "delivered_quantity_original": delivered_qty,
                "delivered_unit": delivered_unit,
                "delivered_quantity_kg": delivered_kg,
                "percentage_variance": round(pct_variance, 2),
            },
            result=round(variance_kg, 2),
            unit="kg",
            source_term_reference=source_term_ref,
            is_verified=True,
        )

    @classmethod
    def check_tolerance(
        cls,
        contract_qty_kg: float,
        delivered_qty_kg: float,
        tolerance_pct: Optional[float],
        source_term_ref: str,
    ) -> Tuple[bool, CalculationStep]:
        """
        Checks whether delivery falls within contractual tolerance (e.g. +/- 5%).
        """
        if tolerance_pct is None:
            raise CalculationError("Tolerance percentage not verified in contract or applicable standards.")

        allowed_min = contract_qty_kg * (1.0 - (tolerance_pct / 100.0))
        allowed_max = contract_qty_kg * (1.0 + (tolerance_pct / 100.0))
        within_tolerance = allowed_min <= delivered_qty_kg <= allowed_max

        step = CalculationStep(
            calculation_name="Contractual Tolerance Check",
            formula="contract_kg * (1 - tolerance/100) <= delivered_kg <= contract_kg * (1 + tolerance/100)",
            inputs={
                "contract_qty_kg": contract_qty_kg,
                "delivered_qty_kg": delivered_qty_kg,
                "tolerance_pct": tolerance_pct,
                "allowed_minimum_kg": round(allowed_min, 2),
                "allowed_maximum_kg": round(allowed_max, 2),
                "within_tolerance": within_tolerance,
            },
            result=float(within_tolerance),
            unit="boolean_flag",
            source_term_reference=source_term_ref,
            is_verified=True,
        )
        return within_tolerance, step

    @classmethod
    def calculate_moisture_shrinkage(
        cls,
        delivered_weight_kg: float,
        actual_moisture_pct: float,
        contract_base_moisture_pct: float,
        handling_loss_pct: float = 0.0,
        source_term_ref: str = "Standard Grain Moisture Shrinkage (Minary Formula)",
    ) -> CalculationStep:
        """
        Computes adjusted dry/base equivalent weight using the standard agricultural Minary Shrinkage formula:
            Adjusted Weight = Delivered Weight * ((100 - Actual Moisture) / (100 - Base Moisture)) - (Handling Loss)
        """
        if contract_base_moisture_pct >= 100.0 or actual_moisture_pct >= 100.0:
            raise CalculationError("Moisture percentage cannot equal or exceed 100%.")

        if actual_moisture_pct < 0 or contract_base_moisture_pct < 0:
            raise CalculationError("Moisture percentage cannot be negative.")

        dry_matter_factor = (100.0 - actual_moisture_pct) / (100.0 - contract_base_moisture_pct)
        water_shrink_weight_kg = delivered_weight_kg * dry_matter_factor
        handling_loss_kg = delivered_weight_kg * (handling_loss_pct / 100.0)
        final_adjusted_weight_kg = max(0.0, water_shrink_weight_kg - handling_loss_kg)
        shrinkage_loss_kg = delivered_weight_kg - final_adjusted_weight_kg

        return CalculationStep(
            calculation_name="Moisture Shrinkage Adjustment",
            formula="delivered_kg * ((100 - actual_moisture) / (100 - base_moisture)) - handling_loss_kg",
            inputs={
                "delivered_weight_kg": delivered_weight_kg,
                "actual_moisture_pct": actual_moisture_pct,
                "contract_base_moisture_pct": contract_base_moisture_pct,
                "handling_loss_pct": handling_loss_pct,
                "water_loss_kg": round(delivered_weight_kg - water_shrink_weight_kg, 2),
                "handling_loss_kg": round(handling_loss_kg, 2),
                "total_shrinkage_kg": round(shrinkage_loss_kg, 2),
            },
            result=round(final_adjusted_weight_kg, 2),
            unit="kg",
            source_term_reference=source_term_ref,
            is_verified=True,
        )

    @classmethod
    def calculate_verified_financial_impact(
        cls,
        settlement_weight_kg: float,
        contract_price_per_unit: float,
        price_unit: str,
        penalty_deduction: float = 0.0,
        currency: str = "USD",
        source_term_ref: str = "Contract Pricing Clause",
    ) -> CalculationStep:
        """
        Calculates financial payable amount strictly based on verified contract pricing and verified weight.
        """
        # Convert price unit to per-kg if needed
        u = price_unit.strip().lower()
        if u in ("kg", "kilogram"):
            price_per_kg = contract_price_per_unit
        elif u in ("mt", "metric_ton", "ton"):
            price_per_kg = contract_price_per_unit / 1000.0
        else:
            raise CalculationError(f"Unsupported price unit: '{price_unit}'")

        gross_amount = settlement_weight_kg * price_per_kg
        net_payable = max(0.0, gross_amount - penalty_deduction)

        return CalculationStep(
            calculation_name="Verified Payable Amount Calculation",
            formula="(settlement_weight_kg * price_per_kg) - penalty_deduction",
            inputs={
                "settlement_weight_kg": settlement_weight_kg,
                "contract_unit_price": contract_price_per_unit,
                "price_unit": price_unit,
                "price_per_kg": round(price_per_kg, 4),
                "gross_payable": round(gross_amount, 2),
                "penalty_deduction": round(penalty_deduction, 2),
                "currency": currency,
            },
            result=round(net_payable, 2),
            unit=currency,
            source_term_reference=source_term_ref,
            is_verified=True,
        )
