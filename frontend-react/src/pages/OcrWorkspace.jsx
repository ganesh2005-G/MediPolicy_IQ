import React, { useState } from 'react';
import { ocrAPI } from '../services/api';
import { Scan, Upload, FileText, CheckCircle2 } from 'lucide-react';

const OcrWorkspace = () => {
  const [docType, setDocType] = useState('INVOICE');
  const [sampleType, setSampleType] = useState('inpatient_bill');
  const [loading, setLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);

  const handleProcessOcr = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await ocrAPI.processDocument(docType, sampleType);
      setOcrResult(res);
    } catch (err) {
      alert("OCR Processing failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '800' }}>AI Medical Document OCR Suite</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Extract structured entities, billing codes, and items from medical documents</p>
      </div>

      <div className="grid-cols-2">
        {/* Left Side Settings */}
        <div className="glass-card" style={{ padding: '2rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '1.5rem' }}>Document Processing Setup</h3>

          <form onSubmit={handleProcessOcr}>
            <div className="input-group">
              <label className="input-label">Document Category</label>
              <select className="input-field" value={docType} onChange={(e) => setDocType(e.target.value)}>
                <option value="INVOICE">INVOICE / BILL</option>
                <option value="PRESCRIPTION">PRESCRIPTION</option>
                <option value="INSURANCE_CARD">INSURANCE CARD</option>
                <option value="MEDICAL_REPORT">MEDICAL REPORT</option>
              </select>
            </div>

            <div className="input-group">
              <label className="input-label">Sample Document Preset</label>
              <select className="input-field" value={sampleType} onChange={(e) => setSampleType(e.target.value)}>
                <option value="inpatient_bill">Inpatient Medical Bill ($150,000)</option>
                <option value="prescription">Doctor Cardiology Prescription ($2,300)</option>
                <option value="insurance_card">Policy Member Insurance Card</option>
              </select>
            </div>

            {/* Simulated File Upload Box */}
            <div style={{
              border: '2px dashed var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '2rem',
              textAlign: 'center',
              background: 'rgba(255,255,255,0.01)',
              marginBottom: '1.5rem',
              cursor: 'pointer'
            }}>
              <Upload size={32} color="var(--accent-cyan)" style={{ marginBottom: '0.5rem' }} />
              <p style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-primary)' }}>Drop Medical PDF / JPG here</p>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Supported formats: PDF, PNG, JPEG up to 25MB</span>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.8rem' }} disabled={loading}>
              <Scan size={18} /> {loading ? 'Extracting Text & Entities...' : 'Run OCR & Extract JSON'}
            </button>
          </form>
        </div>

        {/* Right Side OCR Results */}
        <div className="glass-card" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700' }}>Extracted Structured Output</h3>
            {ocrResult && (
              <span className="badge badge-approved">
                <CheckCircle2 size={12} /> {ocrResult.ocr_confidence * 100}% Confidence
              </span>
            )}
          </div>

          {ocrResult ? (
            <div>
              <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1rem', padding: '0.85rem', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Doc Code</span>
                  <strong style={{ color: 'var(--accent-cyan)' }}>{ocrResult.document_code}</strong>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Type</span>
                  <strong>{ocrResult.doc_type}</strong>
                </div>
              </div>

              <h4 style={{ fontSize: '0.9rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Parsed JSON Payload</h4>
              <pre style={{
                background: 'rgba(15,23,42,0.85)',
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
                fontSize: '0.825rem',
                color: '#34d399',
                maxHeight: '400px',
                overflowY: 'auto'
              }}>
                {JSON.stringify(ocrResult.parsed_json, null, 2)}
              </pre>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <FileText size={48} style={{ opacity: 0.3, marginBottom: '1rem' }} />
              <p>Select a document preset and click 'Run OCR & Extract JSON' to view parsed entities.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OcrWorkspace;
