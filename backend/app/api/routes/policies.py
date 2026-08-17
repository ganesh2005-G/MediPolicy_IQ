from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Policy, PolicyRule, Insurer
from app.schemas.schemas import (
    PolicyCreate, PolicyResponse, PolicyRuleCreate, PolicyRuleResponse, InsurerCreate, InsurerResponse
)

router = APIRouter(prefix="/policies", tags=["Policy & Rule Engine Management"])


@router.post("/insurers", response_model=InsurerResponse)
def create_insurer(insurer_in: InsurerCreate, db: Session = Depends(get_db)):
    insurer = Insurer(**insurer_in.model_dump())
    db.add(insurer)
    db.commit()
    db.refresh(insurer)
    return insurer


@router.get("/insurers", response_model=List[InsurerResponse])
def list_insurers(db: Session = Depends(get_db)):
    return db.query(Insurer).all()


@router.post("/", response_model=PolicyResponse)
def create_policy(policy_in: PolicyCreate, db: Session = Depends(get_db)):
    existing = db.query(Policy).filter(Policy.policy_number == policy_in.policy_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Policy with number already exists.")

    policy = Policy(**policy_in.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/", response_model=List[PolicyResponse])
def list_policies(db: Session = Depends(get_db)):
    return db.query(Policy).all()


@router.post("/{policy_id}/rules", response_model=PolicyRuleResponse)
def add_rule_to_policy(policy_id: int, rule_in: PolicyRuleCreate, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found.")

    rule = PolicyRule(policy_id=policy_id, **rule_in.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
