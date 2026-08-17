from typing import List, Dict, Any
from app.models.models import Policy, PolicyRule, Claim, Hospital


class RuleEvaluationResult:
    def __init__(self):
        self.passed_rules: List[str] = []
        self.failed_rules: List[str] = []
        self.cap_adjustments: List[Dict[str, Any]] = []
        self.total_deductions: float = 0.0
        self.pre_auth_satisfied: bool = True
        self.notes: List[str] = []


class PolicyRuleEngine:
    """Dynamic expression evaluator for Healthcare Insurance policies."""

    @staticmethod
    def evaluate_claim_against_policy(
        policy: Policy,
        hospital: Hospital,
        claim_data: Dict[str, Any],
        items: List[Dict[str, Any]],
        rules: List[PolicyRule]
    ) -> RuleEvaluationResult:
        result = RuleEvaluationResult()

        # 1. Pre-authorization check
        if policy.pre_auth_required and not claim_data.get("pre_auth_approved", False):
            if claim_data.get("claim_type") != "EMERGENCY":
                result.failed_rules.append("RULE_PRE_AUTH_REQUIRED")
                result.pre_auth_satisfied = False
                result.notes.append("Pre-authorization required for non-emergency inpatient treatment.")

        # 2. Cashless network check
        if not hospital.is_cashless_network:
            result.notes.append(f"Hospital {hospital.name} is non-cashless network. Claim subject to reimbursement verification.")

        # 3. Dynamic custom database rules evaluation
        for rule in rules:
            if not rule.is_active:
                continue

            expr = rule.expression.lower()
            action = rule.action.upper()

            # Rule evaluation logic based on domain expressions
            if "non_network_hospital" in expr and not hospital.is_cashless_network:
                if action == "PENALTY" and rule.penalty_percentage:
                    penalty = (rule.penalty_percentage / 100.0) * claim_data.get("total_billed_amount", 0.0)
                    result.total_deductions += penalty
                    result.cap_adjustments.append({
                        "rule": rule.rule_name,
                        "adjustment": penalty,
                        "reason": f"Applied {rule.penalty_percentage}% non-network hospital penalty"
                    })
                    result.passed_rules.append(rule.rule_name)

            elif "cosmetic_procedure" in expr:
                cosmetic_found = False
                for item in items:
                    if "cosmetic" in item.get("item_description", "").lower() or item.get("category") == "COSMETIC":
                        cosmetic_found = True
                        if action == "DENY":
                            item_amount = item.get("billed_amount", 0.0)
                            result.total_deductions += item_amount
                            result.cap_adjustments.append({
                                "rule": rule.rule_name,
                                "item": item.get("item_description"),
                                "adjustment": item_amount,
                                "reason": "Excluded: Cosmetic procedure not covered"
                            })
                if cosmetic_found:
                    result.failed_rules.append(rule.rule_name)

            elif "room_rent_cap" in expr:
                room_days = claim_data.get("room_days", 1)
                room_rent_billed = claim_data.get("room_rent_billed_per_day", 0.0)
                if room_rent_billed > policy.room_rent_cap_per_day:
                    excess_per_day = room_rent_billed - policy.room_rent_cap_per_day
                    total_excess = excess_per_day * room_days
                    result.total_deductions += total_excess
                    result.cap_adjustments.append({
                        "rule": rule.rule_name,
                        "adjustment": total_excess,
                        "reason": f"Room rent billed ({room_rent_billed}/day) exceeds cap ({policy.room_rent_cap_per_day}/day)"
                    })
                    result.failed_rules.append(rule.rule_name)

            else:
                result.passed_rules.append(rule.rule_name)

        return result
