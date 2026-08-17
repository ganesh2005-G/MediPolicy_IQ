from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.schemas import RAGQueryRequest, RAGQueryResponse
from app.ai.rag.assistant import PolicyRAGAssistant

router = APIRouter(prefix="/rag", tags=["AI Policy Chat Assistant (RAG)"])


@router.post("/query", response_model=RAGQueryResponse)
def query_policy_assistant(request: RAGQueryRequest, db: Session = Depends(get_db)):
    """Query Policy Assistant using natural language to clarify clauses and coverage limits."""
    result = PolicyRAGAssistant.answer_policy_query(
        query=request.query,
        policy_number=request.policy_number,
        db=db
    )
    return result

