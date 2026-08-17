from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    PATIENT = "patient"
    DOCTOR = "doctor"
    HOSPITAL_ADMIN = "hospital_admin"
    INSURER_ADMIN = "insurer_admin"
    CLAIM_PROCESSOR = "claim_processor"


class ClaimStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FLAGGED_FRAUD = "FLAGGED_FRAUD"
    PARTIALLY_APPROVED = "PARTIALLY_APPROVED"


class ClaimType(str, Enum):
    INPATIENT = "INPATIENT"
    OUTPATIENT = "OUTPATIENT"
    EMERGENCY = "EMERGENCY"
    PHARMACY = "PHARMACY"
    DENTAL = "DENTAL"
    VISION = "VISION"


class DocumentType(str, Enum):
    INVOICE = "INVOICE"
    PRESCRIPTION = "PRESCRIPTION"
    INSURANCE_CARD = "INSURANCE_CARD"
    MEDICAL_REPORT = "MEDICAL_REPORT"
    POLICY_DOCUMENT = "POLICY_DOCUMENT"


class PolicyType(str, Enum):
    INDIVIDUAL_HEALTH = "INDIVIDUAL_HEALTH"
    FAMILY_FLOATER = "FAMILY_FLOATER"
    CRITICAL_ILLNESS = "CRITICAL_ILLNESS"
    GROUP_HEALTH = "GROUP_HEALTH"
    TOP_UP = "TOP_UP"


class Permission(str, Enum):
    CREATE_APPOINTMENT = "CREATE_APPOINTMENT"
    VIEW_PATIENT = "VIEW_PATIENT"
    EDIT_PATIENT = "EDIT_PATIENT"
    VIEW_CLAIM = "VIEW_CLAIM"
    APPROVE_CLAIM = "APPROVE_CLAIM"
    REJECT_CLAIM = "REJECT_CLAIM"
    UPLOAD_DOCUMENT = "UPLOAD_DOCUMENT"
    VIEW_POLICY = "VIEW_POLICY"
    MANAGE_DOCTORS = "MANAGE_DOCTORS"
    MANAGE_USERS = "MANAGE_USERS"
    VIEW_ANALYTICS = "VIEW_ANALYTICS"


ROLE_PERMISSIONS = {
    UserRole.ADMIN.value: [p.value for p in Permission],
    UserRole.HOSPITAL_ADMIN.value: [
        Permission.CREATE_APPOINTMENT.value,
        Permission.VIEW_PATIENT.value,
        Permission.EDIT_PATIENT.value,
        Permission.UPLOAD_DOCUMENT.value,
        Permission.MANAGE_DOCTORS.value,
        Permission.MANAGE_USERS.value,
        Permission.VIEW_ANALYTICS.value
    ],
    UserRole.INSURER_ADMIN.value: [
        Permission.VIEW_CLAIM.value,
        Permission.APPROVE_CLAIM.value,
        Permission.REJECT_CLAIM.value,
        Permission.VIEW_POLICY.value,
        Permission.VIEW_ANALYTICS.value
    ],
    UserRole.CLAIM_PROCESSOR.value: [
        Permission.VIEW_CLAIM.value,
        Permission.APPROVE_CLAIM.value,
        Permission.REJECT_CLAIM.value
    ],
    UserRole.DOCTOR.value: [
        Permission.VIEW_PATIENT.value,
        Permission.EDIT_PATIENT.value,
        Permission.CREATE_APPOINTMENT.value
    ],
    UserRole.PATIENT.value: [
        Permission.VIEW_PATIENT.value,
        Permission.CREATE_APPOINTMENT.value,
        Permission.VIEW_POLICY.value,
        Permission.UPLOAD_DOCUMENT.value
    ]
}

