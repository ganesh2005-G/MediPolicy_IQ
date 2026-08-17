from sqlalchemy.orm import Session
from app.models.models import (
    Tenant,
    TenantConfiguration,
    User,
    Patient,
    Doctor,
    Hospital,
    Insurer,
    Policy,
    PolicyRule,
    Claim,
    ClaimItem,
)
from app.core.security import get_password_hash


def seed_initial_data(db: Session):
    """Populate database with multi-tenant demonstration data."""

    # 1. Seed Demo Tenants
    tenant1 = db.query(Tenant).filter(Tenant.tenant_id == "hospital_001").first()
    if not tenant1:
        tenant1 = Tenant(
            tenant_id="hospital_001",
            name="Medicare Central Hospital",
            tenant_type="HOSPITAL",
            primary_color="#0ea5e9",
            secondary_color="#0284c7"
        )
        db.add(tenant1)
        db.commit()
        db.refresh(tenant1)

        config1 = TenantConfiguration(
            tenant_id="hospital_001",
            features={"claims": True, "ocr": True, "ai_assistant": True},
            ai_config={
                "assistant_name": "Medicare Central AI",
                "tone": "professional",
                "instructions": "Answer OPD schedule, doctor list, and booking queries."
            },
            operating_hours={"opd_start": "09:00", "opd_end": "18:00", "emergency_service": True}
        )
        db.add(config1)
        db.commit()

    tenant2 = db.query(Tenant).filter(Tenant.tenant_id == "insurer_001").first()
    if not tenant2:
        tenant2 = Tenant(
            tenant_id="insurer_001",
            name="Aegis Healthcare Mutual",
            tenant_type="INSURANCE_COMPANY",
            primary_color="#10b981",
            secondary_color="#047857"
        )
        db.add(tenant2)
        db.commit()
        db.refresh(tenant2)

        config2 = TenantConfiguration(
            tenant_id="insurer_001",
            features={"claims": True, "ocr": True, "ai_assistant": True},
            ai_config={
                "assistant_name": "Aegis Policy Navigator",
                "tone": "helpful",
                "instructions": "Guide policy holders through copay, deductible, and limit details."
            },
            operating_hours={"opd_start": "09:00", "opd_end": "17:00", "emergency_service": False}
        )
        db.add(config2)
        db.commit()

    # 2. Multi-Role Demo Users
    demo_users = [
        ("admin@medipolicy.iq", "Admin123!", "System Administrator", "admin", "hospital_001"),
        ("doctor@medipolicy.iq", "Doctor123!", "Dr. Sarah Jenkins, MD", "doctor", "hospital_001"),
        ("processor@medipolicy.iq", "Processor123!", "Mark Vance (Claims Officer)", "claim_processor", "insurer_001"),
        ("patient@medipolicy.iq", "Patient123!", "Eleanor Vance (Insured Patient)", "patient", "hospital_001"),
    ]

    for email, pwd, name, role, tid in demo_users:
        if not db.query(User).filter(User.email == email).first():
            usr = User(
                email=email,
                hashed_password=get_password_hash(pwd),
                full_name=name,
                role=role,
                tenant_id=tid
            )
            db.add(usr)
    db.commit()

    # 3. Insurers
    insurer1 = db.query(Insurer).filter(Insurer.insurer_code == "INS-AEGIS").first()
    if not insurer1:
        insurer1 = Insurer(
            insurer_code="INS-AEGIS",
            name="Aegis Healthcare Mutual Insurance",
            contact_email="claims@aegishealth.com",
            tenant_id="insurer_001"
        )
        db.add(insurer1)
        db.commit()
        db.refresh(insurer1)

    insurer2 = db.query(Insurer).filter(Insurer.insurer_code == "INS-APEX").first()
    if not insurer2:
        insurer2 = Insurer(
            insurer_code="INS-APEX",
            name="Apex Global Assurance",
            contact_email="support@apexassurance.com",
            tenant_id="insurer_001"
        )
        db.add(insurer2)
        db.commit()
        db.refresh(insurer2)

    # 4. Policies & Rules
    pol1 = db.query(Policy).filter(Policy.policy_number == "POL-1001-INDIVIDUAL").first()
    if not pol1:
        pol1 = Policy(
            policy_number="POL-1001-INDIVIDUAL",
            insurer_id=insurer1.id,
            policy_type="INDIVIDUAL_HEALTH",
            sum_insured=500000.0,
            deductible=10000.0,
            copay_percentage=10.0,
            room_rent_cap_per_day=5000.0,
            icu_rent_cap_per_day=10000.0,
            pre_auth_required=True,
            tenant_id="insurer_001"
        )
        db.add(pol1)
        db.commit()
        db.refresh(pol1)

        rule1 = PolicyRule(
            policy_id=pol1.id,
            rule_name="NON_NETWORK_PENALTY_15",
            rule_category="NETWORK",
            expression="non_network_hospital",
            description="Deduct 15% for non-cashless network hospital admissions",
            action="PENALTY",
            penalty_percentage=15.0
        )
        rule2 = PolicyRule(
            policy_id=pol1.id,
            rule_name="COSMETIC_EXCLUSION",
            rule_category="EXCLUSION",
            expression="cosmetic_procedure",
            description="Exclude cosmetic or aesthetic procedures",
            action="DENY"
        )
        db.add_all([rule1, rule2])

    # 5. Hospital Facilities
    hosp1 = db.query(Hospital).filter(Hospital.hospital_code == "HOSP-METRO").first()
    if not hosp1:
        hosp1 = Hospital(
            hospital_code="HOSP-METRO",
            name="Metro General Hospital (New Delhi)",
            address="100 Healthcare Boulevard, Suite 400",
            is_cashless_network=True,
            contact_number="+91-11-26588500",
            tenant_id="hospital_001"
        )
        db.add(hosp1)

    hosp2 = db.query(Hospital).filter(Hospital.hospital_code == "HOSP-AIIMS").first()
    if not hosp2:
        hosp2 = Hospital(
            hospital_code="HOSP-AIIMS",
            name="AIIMS Specialty Hospital",
            address="Ansari Nagar, New Delhi",
            is_cashless_network=True,
            contact_number="+91-11-26588700",
            tenant_id="hospital_001"
        )
        db.add(hosp2)

    # 6. Hospital Doctors Directory
    doctors_data = [
        ("DOC-101", "Dr. Sarah Jenkins", "Cardiology", "MD (Cardiology), FACC", "Cardiovascular Department", "+91-9811002233", "s.jenkins@metrohealth.in"),
        ("DOC-102", "Dr. Rajesh Kumar", "Orthopedics", "MS (Ortho), D.Ortho", "Orthopedic & Joint Surgery", "+91-9811003344", "r.kumar@metrohealth.in"),
        ("DOC-103", "Dr. Ananya Sharma", "Pulmonology", "MD (Chest Diseases)", "Respiratory Medicine", "+91-9811004455", "a.sharma@metrohealth.in"),
        ("DOC-104", "Dr. Vikram Patel", "General Surgery", "MS (General Surgery)", "Surgical Care Unit", "+91-9811005566", "v.patel@metrohealth.in"),
        ("DOC-105", "Dr. Meera Reddy", "Neurology", "DM (Neurology), MD", "Neuroscience Institute", "+91-9811006677", "m.reddy@metrohealth.in"),
    ]

    for dcode, dname, dspec, dqual, ddept, dphone, demail in doctors_data:
        if not db.query(Doctor).filter(Doctor.doctor_code == dcode).first():
            doc = Doctor(
                doctor_code=dcode,
                full_name=dname,
                specialization=dspec,
                qualification=dqual,
                department=ddept,
                hospital_name="Metro General Hospital",
                phone=dphone,
                email=demail,
                is_on_duty=True,
                tenant_id="hospital_001"
            )
            db.add(doc)

    # 7. Hospital Patients Directory
    patients_data = [
        ("PAT-9082", "Eleanor Vance", "1988-04-12", "Female", "O+", "+91-9876543210", "742 Evergreen Terrace, New Delhi", "ICD10-J18.9 (Pneumonia)", "Dr. Ananya Sharma"),
        ("PAT-4011", "Robert Miller", "1975-09-20", "Male", "A+", "+91-9876543211", "45 Civil Lines, Gurgaon", "ICD10-I21.9 (Myocardial Infarction)", "Dr. Sarah Jenkins"),
        ("PAT-7720", "Priya Nair", "1992-03-15", "Female", "B+", "+91-9876543212", "12 Park Street, Noida", "ICD10-E11.9 (Type 2 Diabetes)", "Dr. Sarah Jenkins"),
        ("PAT-3381", "Amitav Ghosh", "1982-11-05", "Male", "AB+", "+91-9876543213", "88 MG Road, New Delhi", "ICD10-K35.80 (Acute Appendicitis)", "Dr. Vikram Patel"),
        ("PAT-5102", "Sunita Verma", "1968-07-30", "Female", "O-", "+91-9876543214", "102 Vasant Kunj, New Delhi", "ICD10-S82.001A (Patella Fracture)", "Dr. Rajesh Kumar"),
    ]

    for pcode, pname, pdob, pgen, pblood, pphone, paddr, pdiag, pdoc in patients_data:
        if not db.query(Patient).filter(Patient.patient_code == pcode).first():
            pat = Patient(
                patient_code=pcode,
                full_name=pname,
                dob=pdob,
                gender=pgen,
                blood_group=pblood,
                phone=pphone,
                address=paddr,
                primary_diagnosis=pdiag,
                assigned_doctor=pdoc,
                admission_status="INPATIENT",
                tenant_id="hospital_001"
            )
            db.add(pat)

    db.commit()

    # 8. Seed Sample Claim
    pat1 = db.query(Patient).filter(Patient.patient_code == "PAT-9082").first()
    hosp1 = db.query(Hospital).filter(Hospital.hospital_code == "HOSP-METRO").first()
    pol1 = db.query(Policy).filter(Policy.policy_number == "POL-1001-INDIVIDUAL").first()

    if pat1 and hosp1 and pol1:
        existing_claim = db.query(Claim).filter(Claim.claim_number == "CLM-ELN001").first()
        if not existing_claim:
            clm = Claim(
                claim_number="CLM-ELN001",
                patient_id=pat1.id,
                hospital_id=hosp1.id,
                primary_policy_id=pol1.id,
                claim_type="INPATIENT",
                diagnosis_code="ICD10-J18.9",
                total_billed_amount=210000.0,
                approved_amount=189000.0,
                patient_payable=21000.0,
                status="APPROVED",
                fraud_risk_score=15.0,
                is_fraud_flagged=False,
                ai_recommendation="Low risk claim. Fully approved.",
                decision_explanation={
                    "cob_breakdown": {
                        "total_billed": 210000.0,
                        "total_approved_combined": 189000.0
                    }
                },
                tenant_id="insurer_001"
            )
            db.add(clm)
            db.commit()
            db.refresh(clm)

            items = [
                ClaimItem(claim_id=clm.id, item_description="Semi-Private Room Stay (5 Days @ 8,000/day)", category="ROOM", cpt_code="99291", billed_amount=40000.0, approved_amount=36000.0, status="APPROVED"),
                ClaimItem(claim_id=clm.id, item_description="Inpatient Pharmacy & Antibiotics (IV fluids)", category="PHARMACY", cpt_code="99070", billed_amount=32000.0, approved_amount=28800.0, status="APPROVED"),
                ClaimItem(claim_id=clm.id, item_description="Surgical Ward Fee & Laparoscopic Procedure", category="SURGERY", cpt_code="47562", billed_amount=120000.0, approved_amount=108000.0, status="APPROVED"),
                ClaimItem(claim_id=clm.id, item_description="High-Resolution Chest CT Scan & Lab Panel", category="LABORATORY", cpt_code="70450", billed_amount=18000.0, approved_amount=16200.0, status="APPROVED"),
            ]
            db.add_all(items)
            db.commit()
