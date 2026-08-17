import streamlit as st
from services.api_client import APIClient

st.set_page_config(page_title="OCR Document Processing - MediPolicy_IQ", page_icon="📄", layout="wide")

st.title("📄 AI Document OCR & Data Extraction Suite")
st.caption("Extract structured data from medical bills, doctor prescriptions, and insurance cards.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Document Input Settings")
    doc_type = st.selectbox("Document Type", ["INVOICE", "PRESCRIPTION", "INSURANCE_CARD", "MEDICAL_REPORT"])
    sample_type = st.selectbox("Sample Document preset", ["inpatient_bill", "prescription", "insurance_card"])

    uploaded_file = st.file_uploader("Upload Medical PDF/Image (Optional)", type=["pdf", "png", "jpg", "jpeg"])

    if st.button("⚡ Extract & Parse Document", type="primary"):
        with st.spinner("Processing document through OCR engine and structure parser..."):
            res = APIClient.process_ocr(doc_type=doc_type, sample_type=sample_type)

        if res:
            st.session_state["ocr_res"] = res
            st.success(f"Document parsed successfully! ID: {res['document_code']}")
        else:
            st.error("Failed to run OCR engine via API backend.")

with col2:
    st.subheader("Extracted Structured Output")
    if "ocr_res" in st.session_state:
        res = st.session_state["ocr_res"]
        st.metric("OCR Confidence Score", f"{res['ocr_confidence']*100:.1f}%")
        
        st.markdown("### Parsed Data")
        st.json(res["parsed_json"])
    else:
        st.info("Select a document preset or upload a document file and click 'Extract & Parse Document'.")
