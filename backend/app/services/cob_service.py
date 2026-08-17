from typing import Dict, Any, Optional
from app.models.models import Policy


class CoordinationOfBenefitsService:
    """Calculates multi-policy Coordination of Benefits (COB) between Primary & Secondary Insurers."""

    @staticmethod
    def calculate_cob(
        total_billed: float,
        primary_policy: Policy,
        secondary_policy: Optional[Policy] = None
    ) -> Dict[str, Any]:

        # Primary Policy Calculation
        primary_deductible = min(primary_policy.deductible, total_billed)
        amount_after_primary_deductible = max(0.0, total_billed - primary_deductible)
        
        primary_copay_amount = (primary_policy.copay_percentage / 100.0) * amount_after_primary_deductible
        primary_eligible_amount = max(0.0, amount_after_primary_deductible - primary_copay_amount)
        primary_paid = min(primary_eligible_amount, primary_policy.sum_insured)

        uncovered_remainder = total_billed - primary_paid

        secondary_paid = 0.0
        secondary_breakdown = None

        # Secondary Policy Calculation (if present and remainder exists)
        if secondary_policy and uncovered_remainder > 0:
            sec_deductible = min(secondary_policy.deductible, uncovered_remainder)
            amount_after_sec_deductible = max(0.0, uncovered_remainder - sec_deductible)
            sec_copay = (secondary_policy.copay_percentage / 100.0) * amount_after_sec_deductible
            sec_eligible = max(0.0, amount_after_sec_deductible - sec_copay)
            secondary_paid = min(sec_eligible, secondary_policy.sum_insured)

            secondary_breakdown = {
                "policy_number": secondary_policy.policy_number,
                "uncovered_input": uncovered_remainder,
                "secondary_deductible_applied": sec_deductible,
                "secondary_copay_applied": sec_copay,
                "secondary_approved_amount": secondary_paid
            }

        total_approved = primary_paid + secondary_paid
        patient_out_of_pocket = max(0.0, total_billed - total_approved)

        return {
            "total_billed": total_billed,
            "primary_policy_number": primary_policy.policy_number,
            "primary_approved_amount": primary_paid,
            "primary_deductible_applied": primary_deductible,
            "primary_copay_applied": primary_copay_amount,
            "secondary_policy_applied": secondary_policy is not None,
            "secondary_breakdown": secondary_breakdown,
            "total_approved_combined": total_approved,
            "patient_final_out_of_pocket": patient_out_of_pocket
        }
