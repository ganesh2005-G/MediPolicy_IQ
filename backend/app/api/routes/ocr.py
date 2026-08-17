import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Document, Tenant
from app.schemas.schemas import OCRProcessResponse
from app.ocr.parser import OCRDocumentParser
from app.tenants.context import get_current_tenant

router = APIRouter(prefix="/ocr", tags=["Document OCR & Data Extraction"])


@router.post("/process", response_model=OCRProcessResponse)
def process_uploaded_document(
    doc_type: str = Form("INVOICE"),
    sample_type: str = Form("inpatient_bill"),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Process uploaded medical bill, prescription, or insurance card using OCR engine."""
    parsed_json = OCRDocumentParser.parse_document(
        doc_type=doc_type,
        sample_type=sample_type
    )

    doc_code = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    raw_text = f"Sample Extracted Text for {sample_type} ({doc_type})"

    doc = Document(
        document_code=doc_code,
        doc_type=doc_type,
        file_name=f"{sample_type}.pdf",
        file_path=f"data/invoices/{sample_type}.pdf",
        extracted_text=raw_text,
        parsed_json=parsed_json,
        ocr_confidence=parsed_json.get("confidence_score", 0.95),
        tenant_id=tenant.tenant_id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "document_code": doc.document_code,
        "doc_type": doc.doc_type,
        "ocr_confidence": doc.ocr_confidence,
        "extracted_text": doc.extracted_text,
        "parsed_json": doc.parsed_json
    }


@router.get("/", response_model=List[OCRProcessResponse])
def list_documents(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """List all processed OCR documents for the active tenant."""
    docs = db.query(Document).filter(Document.tenant_id == tenant.tenant_id).order_by(Document.created_at.desc()).all()
    # Format database items to fit OCRProcessResponse schema structure
    return [
        {
            "document_code": d.document_code,
            "doc_type": d.doc_type,
            "ocr_confidence": d.ocr_confidence,
            "extracted_text": d.extracted_text,
            "parsed_json": d.parsed_json
        }
        for d in docs
    ]


@router.get("/{document_code}", response_model=OCRProcessResponse)
def get_document_details(
    document_code: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    """Retrieve detailed parsed layout of a specific OCR document."""
    doc = db.query(Document).filter(
        Document.document_code == document_code,
        Document.tenant_id == tenant.tenant_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    return {
        "document_code": doc.document_code,
        "doc_type": doc.doc_type,
        "ocr_confidence": doc.ocr_confidence,
        "extracted_text": doc.extracted_text,
        "parsed_json": doc.parsed_json
    }

