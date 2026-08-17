from fastapi import APIRouter
from app.api.routes import auth, patients, policies, claims, ocr, rag, analytics, hospitals, appointments, health, tenants

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(hospitals.router)
api_router.include_router(policies.router)
api_router.include_router(claims.router)
api_router.include_router(ocr.router)
api_router.include_router(rag.router)
api_router.include_router(analytics.router)
api_router.include_router(appointments.router)
api_router.include_router(health.router)
api_router.include_router(tenants.router)




