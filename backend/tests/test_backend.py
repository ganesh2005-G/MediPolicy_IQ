import os
import sys
import pytest

# Ensure backend root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.rules.engine import PolicyRuleEngine
from app.services.cob_service import CoordinationOfBenefitsService
from app.services.fraud_service import ClaimFraudDetectionService
from app.models.models import Policy, Hospital, PolicyRule

client = TestClient(app)


def test_root_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert "<div id=\"root\"></div>" in response.text

    docs_res = client.get("/docs")
    assert docs_res.status_code == 200




def test_cob_calculation():
    pol_primary = Policy(
        policy_number="POL-TEST-1",
        sum_insured=500000.0,
        deductible=10000.0,
        copay_percentage=10.0
    )
    pol_secondary = Policy(
        policy_number="POL-TEST-2",
        sum_insured=500000.0,
        deductible=5000.0,
        copay_percentage=5.0
    )

    result = CoordinationOfBenefitsService.calculate_cob(
        total_billed=100000.0,
        primary_policy=pol_primary,
        secondary_policy=pol_secondary
    )

    assert result["total_billed"] == 100000.0
    assert result["primary_deductible_applied"] == 10000.0
    assert result["primary_approved_amount"] == 81000.0  # (100k - 10k) * 0.90
    assert result["secondary_policy_applied"] is True


def test_fraud_risk_evaluation():
    claim_meta = {
        "total_billed_amount": 600000.0,  # High value claim (>500k)
        "diagnosis_code": "J18.9",
        "length_of_stay_days": 14  # High stay (standard 5 days)
    }
    items = []

    fraud_res = ClaimFraudDetectionService.evaluate_fraud_risk(
        claim_data=claim_meta,
        items=items,
        hospital_is_network=False  # Non network penalty
    )

    assert fraud_res["fraud_risk_score"] >= 60.0
    assert fraud_res["is_fraud_flagged"] is True
    assert "HIGH_VALUE_CLAIM: Billed amount exceeds 500,000 baseline threshold" in fraud_res["risk_flags"]


def test_rule_engine_non_network_penalty():
    pol = Policy(policy_number="POL-1", pre_auth_required=False, room_rent_cap_per_day=5000.0)
    hospital = Hospital(name="Non Network Hosp", is_cashless_network=False)
    rule = PolicyRule(
        rule_name="NON_NET_15",
        rule_category="NETWORK",
        expression="non_network_hospital",
        action="PENALTY",
        penalty_percentage=15.0,
        is_active=True
    )

    res = PolicyRuleEngine.evaluate_claim_against_policy(
        policy=pol,
        hospital=hospital,
        claim_data={"total_billed_amount": 100000.0},
        items=[],
        rules=[rule]
    )

    assert res.total_deductions == 15000.0
    assert "NON_NET_15" in res.passed_rules
