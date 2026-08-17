import re
from typing import Dict, Any


class OCRDocumentParser:
    """Document processing engine for extracting structured data from medical invoices & prescriptions."""

    @staticmethod
    def parse_document(doc_type: str, raw_text: str = "", sample_type: str = "inpatient_bill") -> Dict[str, Any]:
        """Extract structured entities from raw document text or generated mock sample."""

        if sample_type == "inpatient_bill":
            return {
                "patient_name": "Eleanor Vance",
                "patient_code": "PAT-9082",
                "hospital_name": "Metro General Hospital",
                "bill_number": "INV-2026-8891",
                "admission_date": "2026-07-20",
                "discharge_date": "2026-07-24",
                "diagnosis_icd": "ICD10-J18.9",
                "line_items": [
                    {"description": "Standard Room Rent (4 days)", "category": "ROOM", "billed_amount": 28000.0, "cpt": "99291"},
                    {"description": "ICU Support & Monitoring", "category": "ICU", "billed_amount": 35000.0, "cpt": "99291"},
                    {"description": "Laparoscopic Surgical Procedure", "category": "PROCEDURE", "billed_amount": 65000.0, "cpt": "47562"},
                    {"description": "Pharmacy & Antibiotics", "category": "PHARMACY", "billed_amount": 14500.0, "cpt": "36415"},
                    {"description": "Chest X-Ray & Blood Panels", "category": "LAB", "billed_amount": 7500.0, "cpt": "71045"},
                ],
                "total_billed": 150000.0,
                "confidence_score": 0.96
            }

        elif sample_type == "prescription":
            return {
                "patient_name": "Robert Miller",
                "doctor_name": "Dr. Sarah Jenkins, MD (Cardiology)",
                "prescription_date": "2026-07-25",
                "medications": [
                    {"name": "Atorvastatin 20mg", "dosage": "Once daily", "duration": "30 days", "cost": 1200.0},
                    {"name": "Metoprolol 50mg", "dosage": "Twice daily", "duration": "30 days", "cost": 850.0},
                    {"name": "Aspirin 81mg", "dosage": "Once daily", "duration": "30 days", "cost": 250.0}
                ],
                "total_billed": 2300.0,
                "confidence_score": 0.94
            }

        elif sample_type == "insurance_card":
            return {
                "policy_number": "POL-882190-X",
                "insured_name": "Eleanor Vance",
                "insurer_name": "Aegis Healthcare Mutual",
                "sum_insured": 1000000.0,
                "valid_until": "2027-12-31",
                "tpa_code": "TPA-GLOBAL-01",
                "confidence_score": 0.98
            }

        else:
            return {
                "raw_text_extracted": raw_text[:200] if raw_text else "No document text",
                "total_billed": 5000.0,
                "confidence_score": 0.85
            }
