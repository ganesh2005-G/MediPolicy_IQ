import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Appointment, Doctor


class PolicyRAGAssistant:
    """Retrieval-Augmented Generation (RAG) assistant for Hospital & Policy FAQ and Appointment Booking."""

    POLICY_KNOWLEDGE_BASE = [
        {
            "category": "Room Rent & ICU Caps",
            "text": "Individual Health Policy POL-1001 imposes a maximum room rent cap of 5,000 INR per day and ICU cap of 10,000 INR per day. Proportionate deductions apply to nursing and doctor consultation charges if room rent exceeds the daily limit."
        },
        {
            "category": "Pre-Authorization Requirements",
            "text": "Planned inpatient surgeries require pre-authorization approval at least 48 hours prior to admission. Emergency admissions must be notified within 24 hours of hospital entry."
        },
        {
            "category": "Exclusions & Waiting Periods",
            "text": "Pre-existing conditions (PED) have a mandatory 36-month waiting period. Cosmetic treatments, experimental procedures, and unproven therapies are strictly excluded from coverage."
        },
        {
            "category": "Coordination of Benefits (COB)",
            "text": "If covered under dual policies, primary policy deductible and co-pay apply first. Uncovered eligible expenses may be submitted to the secondary policy up to its remaining sum insured."
        },
        {
            "category": "Hospital Location & Address",
            "text": "Metro General Hospital is located at 100 Healthcare Boulevard, Suite 400, New Delhi. Phone number: +91-11-26588500."
        },
        {
            "category": "OPD Operational Timings",
            "text": "OPD clinics are open Monday to Saturday from 9:00 AM to 6:00 PM. Emergency and ICU departments are operational 24/7."
        }
    ]

    @staticmethod
    def answer_policy_query(query: str, tenant_id: str, policy_number: str = None, db: Session = None) -> Dict[str, Any]:
        """Answer natural language queries regarding hospital operations, policies, and book appointments."""
        from app.models.models import TenantConfiguration

        # 1. Resolve tenant settings dynamically from database configuration
        assistant_name = "System AI Assistant"
        instructions = ""
        tone = "helpful"

        if db:
            config = db.query(TenantConfiguration).filter(TenantConfiguration.tenant_id == tenant_id).first()
            if config:
                assistant_name = config.ai_config.get("assistant_name", assistant_name)
                instructions = config.ai_config.get("instructions", instructions)
                tone = config.ai_config.get("tone", tone)

        query_lower = query.lower()
        matching_sources: List[str] = []

        # Find matching content in knowledge base
        for entry in PolicyRAGAssistant.POLICY_KNOWLEDGE_BASE:
            if any(term in query_lower for term in entry["category"].lower().split()) or \
               any(term in query_lower for term in entry["text"].lower().split()):
                matching_sources.append(f"[{entry['category']}] {entry['text']}")

        if not matching_sources:
            matching_sources.append(PolicyRAGAssistant.POLICY_KNOWLEDGE_BASE[0]["text"])

        # Handle Appointment Booking Intent
        if any(word in query_lower for word in ["book", "appointment", "schedule", "consultation", "doctor"]):
            # Identify Doctor
            selected_doctor = None
            specialization = "General Consultation"
            
            doctors = {
                "jenkins": ("Dr. Sarah Jenkins", "Cardiology"),
                "kumar": ("Dr. Rajesh Kumar", "Orthopedics"),
                "sharma": ("Dr. Ananya Sharma", "Pulmonology"),
                "patel": ("Dr. Vikram Patel", "General Surgery"),
                "reddy": ("Dr. Meera Reddy", "Neurology")
            }

            for key, val in doctors.items():
                if key in query_lower:
                    selected_doctor, specialization = val
                    break

            if not selected_doctor:
                answer = f"Hello! I am {assistant_name}. I can help you book an appointment! Please mention the doctor or specialty you prefer. We have:\n" \
                         "- Dr. Sarah Jenkins (Cardiology)\n" \
                         "- Dr. Rajesh Kumar (Orthopedics)\n" \
                         "- Dr. Ananya Sharma (Pulmonology)\n" \
                         "- Dr. Vikram Patel (General Surgery)\n" \
                         "- Dr. Meera Reddy (Neurology)"
                return {
                    "query": query,
                    "answer": answer,
                    "sources": ["OPD Roster Knowledge Base"],
                    "confidence_score": 1.0
                }

            # Book appointment dynamically under the caller's active tenant
            apt_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            apt_time = "10:00 AM" if "morning" in query_lower else "2:30 PM"
            apt_code = f"APT-{random.randint(10000, 99999)}"

            if db:
                db_apt = Appointment(
                    appointment_code=apt_code,
                    patient_name="Eleanor Vance",
                    doctor_name=selected_doctor,
                    specialization=specialization,
                    appointment_date=apt_date,
                    appointment_time=apt_time,
                    status="BOOKED",
                    tenant_id=tenant_id
                )
                db.add(db_apt)
                db.commit()

            answer = f"📅 **Appointment Booked Successfully by {assistant_name}!**\n\n" \
                     f"**Details**:\n" \
                     f"- **Doctor**: {selected_doctor} ({specialization})\n" \
                     f"- **Date**: {apt_date} (Tomorrow)\n" \
                     f"- **Time**: {apt_time}\n" \
                     f"- **Appointment Code**: `{apt_code}`\n\n" \
                     f"Tone constraint: `{tone}`. System custom direction: `{instructions}`."
            
            return {
                "query": query,
                "answer": answer,
                "sources": [f"Appointment Scheduler Database Connection"],
                "confidence_score": 1.0
            }

        # Fallback normal QA responses
        if "room" in query_lower or "rent" in query_lower:
            answer = f"[{assistant_name} ({tone})] According to policy coverage details, private room rent is capped at 5,000 INR/day and ICU stay is capped at 10,000 INR/day."
        elif "pre-auth" in query_lower or "authorization" in query_lower:
            answer = f"[{assistant_name} ({tone})] Pre-authorization is mandatory for planned hospital admissions and must be submitted 48 hours prior to check-in."
        elif "deductible" in query_lower or "co-pay" in query_lower or "copay" in query_lower:
            answer = f"[{assistant_name} ({tone})] The policy features a fixed deductible of 10,000 INR per claim and a 10% co-payment structure."
        elif "specialt" in query_lower or "doctor" in query_lower or "departments" in query_lower:
            answer = f"[{assistant_name} ({tone})] Metro General Hospital features Cardiology (Dr. Sarah Jenkins), Orthopedics (Dr. Rajesh Kumar), Pulmonology (Dr. Ananya Sharma), General Surgery (Dr. Vikram Patel), and Neurology (Dr. Meera Reddy)."
        elif "opd" in query_lower or "timings" in query_lower or "hours" in query_lower:
            answer = f"[{assistant_name} ({tone})] OPD clinical consultation hours are 9:00 AM to 6:00 PM (Monday to Saturday)."
        elif "address" in query_lower or "location" in query_lower:
            answer = f"[{assistant_name} ({tone})] Metro General Hospital is located at 100 Healthcare Boulevard, Suite 400, New Delhi."
        else:
            answer = f"[{assistant_name} ({tone})] Hello! I am {assistant_name}. Custom instructions active: '{instructions}'. Let me know how I can assist you."

        return {
            "query": query,
            "answer": answer,
            "sources": matching_sources,
            "confidence_score": 0.95
        }

