from typing import Dict, Any, Optional

ICD10_DATABASE: Dict[str, Dict[str, Any]] = {
    "J18.9": {"description": "Pneumonia, unspecified organism", "category": "Respiratory", "standard_length_of_stay_days": 5},
    "I21.9": {"description": "Acute myocardial infarction, unspecified", "category": "Cardiovascular", "standard_length_of_stay_days": 4},
    "E11.9": {"description": "Type 2 diabetes mellitus without complications", "category": "Endocrine", "standard_length_of_stay_days": 1},
    "K35.80": {"description": "Unspecified acute appendicitis", "category": "Gastrointestinal", "standard_length_of_stay_days": 2},
    "M54.5": {"description": "Low back pain", "category": "Musculoskeletal", "standard_length_of_stay_days": 1},
    "S82.001A": {"description": "Unspecified fracture of right patella, initial encounter", "category": "Orthopedics", "standard_length_of_stay_days": 3},
}

CPT_DATABASE: Dict[str, Dict[str, Any]] = {
    "99213": {"description": "Office or outpatient visit for established patient, low-to-moderate complexity", "category": "CONSULTATION", "usual_max_fee": 2500.0},
    "99214": {"description": "Office or outpatient visit, moderate complexity", "category": "CONSULTATION", "usual_max_fee": 4000.0},
    "99291": {"description": "Critical care, evaluation and management of critically ill patient; first 30-74 minutes", "category": "ICU", "usual_max_fee": 15000.0},
    "47562": {"description": "Laparoscopic cholecystectomy", "category": "PROCEDURE", "usual_max_fee": 85000.0},
    "44970": {"description": "Laparoscopic appendectomy", "category": "PROCEDURE", "usual_max_fee": 65000.0},
    "36415": {"description": "Routine venipuncture (blood draw)", "category": "LAB", "usual_max_fee": 500.0},
    "71045": {"description": "Chest X-ray, single view", "category": "LAB", "usual_max_fee": 2000.0},
    "70450": {"description": "CT Scan Head or Brain without contrast", "category": "LAB", "usual_max_fee": 12000.0},
    "A0428": {"description": "Ambulance service, basic life support, non-emergency transport (HCPCS)", "category": "TRANSPORT", "usual_max_fee": 5000.0},
}


class MedicalCodingService:
    @staticmethod
    def lookup_icd10(code: str) -> Optional[Dict[str, Any]]:
        clean_code = code.replace("ICD10-", "").strip()
        return ICD10_DATABASE.get(clean_code)

    @staticmethod
    def lookup_cpt(code: str) -> Optional[Dict[str, Any]]:
        clean_code = code.replace("CPT-", "").strip()
        return CPT_DATABASE.get(clean_code)

    @staticmethod
    def validate_item_coding(cpt_code: Optional[str], billed_amount: float) -> Dict[str, Any]:
        """Validate if item billing is within standard baseline for the CPT code."""
        if not cpt_code:
            return {"is_valid": True, "flag": None, "usual_max_fee": None}

        info = MedicalCodingService.lookup_cpt(cpt_code)
        if not info:
            return {"is_valid": True, "flag": "UNKNOWN_CPT", "usual_max_fee": None}

        max_fee = info["usual_max_fee"]
        if billed_amount > max_fee * 1.5:
            return {
                "is_valid": False,
                "flag": f"OVERBILLED_CPT: Billed {billed_amount} exceeds usual max fee {max_fee} by >50%",
                "usual_max_fee": max_fee
            }

        return {"is_valid": True, "flag": None, "usual_max_fee": max_fee}
