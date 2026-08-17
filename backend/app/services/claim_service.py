import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.models import (
    Claim, ClaimItem, Patient, Hospital, Policy, PolicyRule, AuditLog
)
from app.schemas.schemas import ClaimCreate
from app.core.constants import ClaimStatus
from app.rules.engine import PolicyRuleEngine
from app.services.cob_service import CoordinationOfBenefitsService
from app.services.fraud_service import ClaimFraudDetectionService
from app.services.medical_coding import MedicalCodingService


class ClaimService:
    """Master orchestration service for Healthcare Insurance Claim adjudication."""

    @staticmethod
    def process_and_create_claim(db: Session, claim_in: ClaimCreate, tenant_id: str, user_email: str = "system") -> Claim:
        # 1. Fetch related domain entities
        patient = db.query(Patient).filter(
            Patient.id == claim_in.patient_id,
            Patient.tenant_id == tenant_id
        ).first()
        if not patient:
            raise ValueError(f"Patient ID {claim_in.patient_id} not found or does not belong to active tenant.")

        hospital = db.query(Hospital).filter(
            Hospital.id == claim_in.hospital_id,
            Hospital.tenant_id == tenant_id
        ).first()
        if not hospital:
            raise ValueError(f"Hospital ID {claim_in.hospital_id} not found or does not belong to active tenant.")

        primary_policy = db.query(Policy).filter(Policy.id == claim_in.primary_policy_id).first()
        if not primary_policy:
            raise ValueError(f"Primary Policy ID {claim_in.primary_policy_id} not found.")

        secondary_policy = None
        if claim_in.secondary_policy_id:
            secondary_policy = db.query(Policy).filter(Policy.id == claim_in.secondary_policy_id).first()

        # 2. Evaluate Dynamic Rules
        rules = db.query(PolicyRule).filter(PolicyRule.policy_id == primary_policy.id).all()
        items_dict = [item.model_dump() for item in claim_in.items]
        claim_meta = {
            "total_billed_amount": claim_in.total_billed_amount,
            "claim_type": claim_in.claim_type,
            "diagnosis_code": claim_in.diagnosis_code,
            "pre_auth_approved": True,
            "room_days": 4,
            "room_rent_billed_per_day": 7000.0
        }

        rule_res = PolicyRuleEngine.evaluate_claim_against_policy(
            policy=primary_policy,
            hospital=hospital,
            claim_data=claim_meta,
            items=items_dict,
            rules=rules
        )

        # 3. Calculate COB Benefits
        cob_res = CoordinationOfBenefitsService.calculate_cob(
            total_billed=claim_in.total_billed_amount,
            primary_policy=primary_policy,
            secondary_policy=secondary_policy
        )

        # Apply rule deductions to approved calculation
        gross_approved = cob_res["total_approved_combined"]
        final_approved = max(0.0, gross_approved - rule_res.total_deductions)
        patient_payable = max(0.0, claim_in.total_billed_amount - final_approved)

        # 4. Evaluate Fraud Risk
        fraud_res = ClaimFraudDetectionService.evaluate_fraud_risk(
            claim_data=claim_meta,
            items=items_dict,
            hospital_is_network=hospital.is_cashless_network
        )

        # Determine Claim Status
        if fraud_res["is_fraud_flagged"]:
            status = ClaimStatus.FLAGGED_FRAUD.value
        elif not rule_res.pre_auth_satisfied:
            status = ClaimStatus.UNDER_REVIEW.value
        elif final_approved == claim_in.total_billed_amount:
            status = ClaimStatus.APPROVED.value
        else:
            status = ClaimStatus.PARTIALLY_APPROVED.value

        claim_number = f"CLM-{uuid.uuid4().hex[:8].upper()}"

        # 5. Create Claim Record
        db_claim = Claim(
            claim_number=claim_number,
            patient_id=claim_in.patient_id,
            hospital_id=claim_in.hospital_id,
            primary_policy_id=claim_in.primary_policy_id,
            secondary_policy_id=claim_in.secondary_policy_id,
            claim_type=claim_in.claim_type,
            diagnosis_code=claim_in.diagnosis_code,
            total_billed_amount=claim_in.total_billed_amount,
            approved_amount=round(final_approved, 2),
            patient_payable=round(patient_payable, 2),
            status=status,
            fraud_risk_score=fraud_res["fraud_risk_score"],
            is_fraud_flagged=fraud_res["is_fraud_flagged"],
            ai_recommendation=fraud_res["ai_recommendation"],
            decision_explanation={
                "cob_breakdown": cob_res,
                "rule_evaluation": {
                    "passed_rules": rule_res.passed_rules,
                    "failed_rules": rule_res.failed_rules,
                    "total_rule_deductions": rule_res.total_deductions,
                    "adjustments": rule_res.cap_adjustments
                },
                "fraud_evaluation": fraud_res
            },
            tenant_id=tenant_id
        )
        db.add(db_claim)
        db.commit()
        db.refresh(db_claim)


        # 6. Create Claim Line Items
        for item_in in claim_in.items:
            item_approved = item_in.billed_amount
            # Proportionate item adjustment if claim is partially approved
            if claim_in.total_billed_amount > 0:
                item_ratio = item_in.billed_amount / claim_in.total_billed_amount
                item_approved = round(final_approved * item_ratio, 2)

            cpt_val = MedicalCodingService.validate_item_coding(item_in.cpt_code, item_in.billed_amount)
            item_status = "APPROVED" if cpt_val["is_valid"] else "FLAGGED"

            db_item = ClaimItem(
                claim_id=db_claim.id,
                item_description=item_in.item_description,
                category=item_in.category,
                cpt_code=item_in.cpt_code,
                icd_code=item_in.icd_code,
                billed_amount=item_in.billed_amount,
                approved_amount=item_approved,
                status=item_status,
                rejection_reason=cpt_val.get("flag")
            )
            db.add(db_item)

        # 7. Audit Log
        audit = AuditLog(
            user_email=user_email,
            action="CREATE_CLAIM",
            entity_type="CLAIM",
            entity_id=str(db_claim.id),
            details=f"Processed claim {claim_number} with status {status} and approved amount {final_approved}"
        )
        db.add(audit)
        db.commit()
        db.refresh(db_claim)

        return db_claim
