from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.core.constants import UserRole, ClaimStatus, ClaimType, DocumentType, PolicyType


def utc_now():
    return datetime.now(timezone.utc)


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    tenant_type = Column(String(50), nullable=False)  # HOSPITAL, INSURANCE_COMPANY, CLINIC
    primary_color = Column(String(50), default="#0ea5e9")
    secondary_color = Column(String(50), default="#0284c7")
    logo_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)


class TenantConfiguration(Base):
    __tablename__ = "tenant_configurations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), unique=True, nullable=False)
    features = Column(JSON, default=lambda: {"claims": True, "ocr": True, "ai_assistant": True})
    ai_config = Column(JSON, default=lambda: {
        "assistant_name": "MediPolicy AI",
        "tone": "professional",
        "instructions": "Help patient navigate claim details."
    })
    operating_hours = Column(JSON, default=lambda: {
        "opd_start": "09:00",
        "opd_end": "18:00",
        "emergency_service": True
    })
    created_at = Column(DateTime, default=utc_now)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.CLAIM_PROCESSOR.value, nullable=False)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    dob = Column(String(20), nullable=False)
    gender = Column(String(20), nullable=False)
    blood_group = Column(String(10), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    primary_diagnosis = Column(String(255), nullable=True)
    assigned_doctor = Column(String(255), nullable=True)
    admission_status = Column(String(50), default="INPATIENT")
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    claims = relationship("Claim", back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    doctor_code = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    specialization = Column(String(100), nullable=False)  # Cardiology, Orthopedics, etc.
    qualification = Column(String(100), default="MD / MS")
    department = Column(String(100), nullable=False)
    hospital_name = Column(String(255), default="Metro General Hospital")
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    is_on_duty = Column(Boolean, default=True)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    hospital_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    is_cashless_network = Column(Boolean, default=True)
    contact_number = Column(String(50), nullable=True)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    claims = relationship("Claim", back_populates="hospital")


class Insurer(Base):
    __tablename__ = "insurers"

    id = Column(Integer, primary_key=True, index=True)
    insurer_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=True)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    policies = relationship("Policy", back_populates="insurer")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(100), unique=True, index=True, nullable=False)
    insurer_id = Column(Integer, ForeignKey("insurers.id"), nullable=False)
    policy_type = Column(String(50), default=PolicyType.INDIVIDUAL_HEALTH.value)
    sum_insured = Column(Float, nullable=False, default=500000.0)
    deductible = Column(Float, nullable=False, default=10000.0)
    copay_percentage = Column(Float, nullable=False, default=10.0)
    room_rent_cap_per_day = Column(Float, nullable=False, default=5000.0)
    icu_rent_cap_per_day = Column(Float, nullable=False, default=10000.0)
    pre_auth_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    insurer = relationship("Insurer", back_populates="policies")
    rules = relationship("PolicyRule", back_populates="policy", cascade="all, delete-orphan")


class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    rule_name = Column(String(255), nullable=False)
    rule_category = Column(String(100), nullable=False)
    expression = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    action = Column(String(50), default="DENY")
    cap_amount = Column(Float, nullable=True)
    penalty_percentage = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    policy = relationship("Policy", back_populates="rules")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String(100), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    primary_policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    secondary_policy_id = Column(Integer, ForeignKey("policies.id"), nullable=True)

    claim_type = Column(String(50), default=ClaimType.INPATIENT.value)
    diagnosis_code = Column(String(50), nullable=True)  # ICD-10
    total_billed_amount = Column(Float, nullable=False, default=0.0)
    approved_amount = Column(Float, nullable=False, default=0.0)
    patient_payable = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), default=ClaimStatus.SUBMITTED.value)

    fraud_risk_score = Column(Float, default=0.0)
    is_fraud_flagged = Column(Boolean, default=False)
    ai_recommendation = Column(Text, nullable=True)
    decision_explanation = Column(JSON, nullable=True)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    patient = relationship("Patient", back_populates="claims")
    hospital = relationship("Hospital", back_populates="claims")
    items = relationship("ClaimItem", back_populates="claim", cascade="all, delete-orphan")


class ClaimItem(Base):
    __tablename__ = "claim_items"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    item_description = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    cpt_code = Column(String(50), nullable=True)
    icd_code = Column(String(50), nullable=True)
    billed_amount = Column(Float, nullable=False, default=0.0)
    approved_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), default="APPROVED")
    rejection_reason = Column(String(255), nullable=True)

    claim = relationship("Claim", back_populates="items")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_code = Column(String(100), unique=True, index=True, nullable=False)
    doc_type = Column(String(50), default=DocumentType.INVOICE.value)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    ocr_confidence = Column(Float, default=0.95)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    timestamp = Column(DateTime, default=utc_now)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    appointment_code = Column(String(50), unique=True, index=True, nullable=False)
    patient_name = Column(String(255), nullable=False)
    doctor_name = Column(String(255), nullable=False)
    specialization = Column(String(100), nullable=False)
    appointment_date = Column(String(50), nullable=False)
    appointment_time = Column(String(50), nullable=False)
    status = Column(String(50), default="BOOKED")
    tenant_id = Column(String(50), ForeignKey("tenants.tenant_id"), nullable=True)
    created_at = Column(DateTime, default=utc_now)
