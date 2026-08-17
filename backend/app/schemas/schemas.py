from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, ConfigDict


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_role: str
    user_email: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[str] = "claim_processor"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# Patient Schemas
class PatientCreate(BaseModel):
    patient_code: str
    full_name: str
    dob: str
    gender: str
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    primary_diagnosis: Optional[str] = "ICD10-J18.9 (Pneumonia)"
    assigned_doctor: Optional[str] = "Dr. Ananya Sharma"
    admission_status: Optional[str] = "INPATIENT"


class PatientResponse(PatientCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



# Hospital Schemas
class HospitalCreate(BaseModel):
    hospital_code: str
    name: str
    address: Optional[str] = None
    is_cashless_network: bool = True
    contact_number: Optional[str] = None


class HospitalResponse(HospitalCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Insurer & Policy Schemas
class InsurerCreate(BaseModel):
    insurer_code: str
    name: str
    contact_email: Optional[str] = None


class InsurerResponse(InsurerCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PolicyRuleCreate(BaseModel):
    rule_name: str
    rule_category: str
    expression: str
    description: Optional[str] = None
    action: str = "DENY"
    cap_amount: Optional[float] = None
    penalty_percentage: Optional[float] = None


class PolicyRuleResponse(PolicyRuleCreate):
    id: int
    policy_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class PolicyCreate(BaseModel):
    policy_number: str
    insurer_id: int
    policy_type: str = "INDIVIDUAL_HEALTH"
    sum_insured: float = 500000.0
    deductible: float = 10000.0
    copay_percentage: float = 10.0
    room_rent_cap_per_day: float = 5000.0
    icu_rent_cap_per_day: float = 10000.0
    pre_auth_required: bool = False


class PolicyResponse(PolicyCreate):
    id: int
    is_active: bool
    rules: List[PolicyRuleResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Claim Schemas
class ClaimItemCreate(BaseModel):
    item_description: str
    category: str
    cpt_code: Optional[str] = None
    icd_code: Optional[str] = None
    billed_amount: float


class ClaimItemResponse(ClaimItemCreate):
    id: int
    approved_amount: float
    status: str
    rejection_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClaimCreate(BaseModel):
    patient_id: int
    hospital_id: int
    primary_policy_id: int
    secondary_policy_id: Optional[int] = None
    claim_type: str = "INPATIENT"
    diagnosis_code: Optional[str] = "ICD10-J18.9"
    total_billed_amount: float
    items: List[ClaimItemCreate]


class ClaimResponse(BaseModel):
    id: int
    claim_number: str
    patient_id: int
    hospital_id: int
    primary_policy_id: int
    secondary_policy_id: Optional[int] = None
    claim_type: str
    diagnosis_code: Optional[str]
    total_billed_amount: float
    approved_amount: float
    patient_payable: float
    status: str
    fraud_risk_score: float
    is_fraud_flagged: bool
    ai_recommendation: Optional[str]
    decision_explanation: Optional[Dict[str, Any]]
    created_at: datetime
    items: List[ClaimItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


# OCR Schemas
class OCRProcessRequest(BaseModel):
    doc_type: str = "INVOICE"
    sample_type: Optional[str] = "inpatient_bill"  # inpatient_bill, prescription, insurance_card


class OCRProcessResponse(BaseModel):
    document_code: str
    doc_type: str
    ocr_confidence: float
    extracted_text: str
    parsed_json: Dict[str, Any]


# RAG & AI Assistant Schemas
class RAGQueryRequest(BaseModel):
    query: str
    policy_number: Optional[str] = None


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    confidence_score: float


# Analytics Summary Schema
class DashboardAnalyticsResponse(BaseModel):
    total_claims: int
    total_billed_amount: float
    total_approved_amount: float
    auto_approval_rate: float
    fraud_flagged_claims: int
    pending_claims: int
    recent_claims: List[ClaimResponse]


# Tenant & Onboarding Schemas
class TenantCreate(BaseModel):
    tenant_id: str
    name: str
    tenant_type: str  # HOSPITAL, INSURANCE_COMPANY, CLINIC
    primary_color: Optional[str] = "#0ea5e9"
    secondary_color: Optional[str] = "#0284c7"
    logo_url: Optional[str] = None
    admin_email: EmailStr
    admin_password: str
    admin_full_name: str
    admin_role: Optional[str] = "admin"
    features: Optional[Dict[str, Any]] = None
    ai_config: Optional[Dict[str, Any]] = None
    operating_hours: Optional[Dict[str, Any]] = None


class TenantResponse(BaseModel):
    id: int
    tenant_id: str
    name: str
    tenant_type: str
    primary_color: str
    secondary_color: str
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

