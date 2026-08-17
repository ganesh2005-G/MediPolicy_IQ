from typing import Dict, Any, List
from app.services.medical_coding import MedicalCodingService


class ClaimFraudDetectionService:
    """Enterprise AI & Rule-based Fraud Risk Scoring Engine for Healthcare Claims."""

    @staticmethod
    def evaluate_fraud_risk(
        claim_data: Dict[str, Any],
        items: List[Dict[str, Any]],
        hospital_is_network: bool
    ) -> Dict[str, Any]:
        risk_score = 5.0  # Base risk
        flags: List[str] = []

        total_billed = claim_data.get("total_billed_amount", 0.0)
        diagnosis_code = claim_data.get("diagnosis_code")

        # 1. Billed Amount Anomaly
        if total_billed > 500000.0:
            risk_score += 25.0
            flags.append("HIGH_VALUE_CLAIM: Billed amount exceeds 500,000 baseline threshold")
        elif total_billed > 200000.0:
            risk_score += 10.0
            flags.append("MEDIUM_VALUE_CLAIM: Billed amount exceeds 200,000 threshold")

        # 2. Diagnosis vs Length of Stay validation
        if diagnosis_code:
            icd_info = MedicalCodingService.lookup_icd10(diagnosis_code)
            if icd_info:
                std_days = icd_info.get("standard_length_of_stay_days", 3)
                claimed_days = claim_data.get("length_of_stay_days", 1)
                if claimed_days > std_days * 2:
                    risk_score += 20.0
                    flags.append(f"EXCESSIVE_LENGTH_OF_STAY: Claimed {claimed_days} days vs standard {std_days} days for {diagnosis_code}")

        # 3. Item Level CPT Overbilling check
        for item in items:
            cpt = item.get("cpt_code")
            billed = item.get("billed_amount", 0.0)
            cpt_val = MedicalCodingService.validate_item_coding(cpt, billed)
            if not cpt_val["is_valid"]:
                risk_score += 15.0
                flags.append(cpt_val["flag"])

        # 4. Non-network Hospital Anomaly
        if not hospital_is_network:
            risk_score += 15.0
            flags.append("NON_NETWORK_HOSPITAL: Hospital operates outside cashless verified network")

        # Cap score between 0 and 100
        risk_score = min(100.0, max(0.0, risk_score))

        is_flagged = risk_score >= 60.0
        if is_flagged:
            recommendation = "FLAGGED_FOR_AUDIT: High fraud risk score detected. Manual investigation required."
        elif risk_score >= 35.0:
            recommendation = "MANUAL_REVIEW: Moderate risk score. Review supporting documentation before approval."
        else:
            recommendation = "AUTO_APPROVE_RECOMMENDED: Low fraud risk profile. Meets standard adjudication criteria."

        return {
            "fraud_risk_score": round(risk_score, 1),
            "is_fraud_flagged": is_flagged,
            "risk_level": "HIGH" if risk_score >= 60 else ("MEDIUM" if risk_score >= 35 else "LOW"),
            "risk_flags": flags,
            "ai_recommendation": recommendation
        }
