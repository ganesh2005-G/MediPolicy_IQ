import React, { useState, useEffect } from 'react';
import { claimsAPI } from '../services/api';
import { FileText, Plus, CheckCircle, AlertTriangle, ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';

const Claims = () => {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  const [expandedClaim, setExpandedClaim] = useState(null);

  // Form State
  const [patientId, setPatientId] = useState(1);
  const [hospitalId, setHospitalId] = useState(1);
  const [primaryPolicyId, setPrimaryPolicyId] = useState(1);
  const [claimType, setClaimType] = useState('INPATIENT');
  const [diagnosisCode, setDiagnosisCode] = useState('ICD10-J18.9');

  const [items, setItems] = useState([
    { item_description: 'Standard Room Rent (4 days)', category: 'ROOM', cpt_code: '99291', billed_amount: 28000 },
    { item_description: 'ICU Support & Monitoring', category: 'ICU', cpt_code: '99291', billed_amount: 35000 },
    { item_description: 'Laparoscopic Surgery', category: 'PROCEDURE', cpt_code: '47562', billed_amount: 65000 },
  ]);

  const loadClaims = async () => {
    try {
      const data = await claimsAPI.getClaims();
      setClaims(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClaims();
  }, []);

  const totalBilled = items.reduce((acc, curr) => acc + Number(curr.billed_amount || 0), 0);

  const handleSubmitClaim = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        patient_id: Number(patientId),
        hospital_id: Number(hospitalId),
        primary_policy_id: Number(primaryPolicyId),
        claim_type: claimType,
        diagnosis_code: diagnosisCode,
        total_billed_amount: totalBilled,
        items: items
      };
      await claimsAPI.submitClaim(payload);
      setShowNewModal(false);
      loadClaims();
    } catch (err) {
      alert("Error processing claim: " + (err.response?.data?.detail || err.message));
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'APPROVED': return <span className="badge badge-approved"><CheckCircle size={12} /> Approved</span>;
      case 'PARTIALLY_APPROVED': return <span className="badge badge-partially"><CheckCircle size={12} /> Partial</span>;
      case 'UNDER_REVIEW': return <span className="badge badge-review"><AlertTriangle size={12} /> Review</span>;
      case 'FLAGGED_FRAUD': return <span className="badge badge-fraud"><ShieldAlert size={12} /> Flagged Fraud</span>;
      default: return <span className="badge badge-review">{status}</span>;
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: '800' }}>Claims Adjudication Workspace</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Automated claim calculation, COB evaluation, and decision history</p>
        </div>

        <button onClick={() => setShowNewModal(true)} className="btn btn-primary">
          <Plus size={18} /> New Claim Entry
        </button>
      </div>

      {/* Claims List Table */}
      <div className="glass-card" style={{ padding: '1.5rem', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
              <th style={{ padding: '0.85rem' }}>Claim #</th>
              <th style={{ padding: '0.85rem' }}>Type & Code</th>
              <th style={{ padding: '0.85rem' }}>Billed ($)</th>
              <th style={{ padding: '0.85rem' }}>Approved ($)</th>
              <th style={{ padding: '0.85rem' }}>Patient Payable</th>
              <th style={{ padding: '0.85rem' }}>Fraud Score</th>
              <th style={{ padding: '0.85rem' }}>Status</th>
              <th style={{ padding: '0.85rem' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {claims.map((c) => (
              <React.Fragment key={c.id}>
                <tr style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
                  <td style={{ padding: '1rem', fontWeight: '700', color: 'var(--accent-cyan)' }}>{c.claim_number}</td>
                  <td style={{ padding: '1rem' }}>
                    <span style={{ display: 'block', fontWeight: '600' }}>{c.claim_type}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{c.diagnosis_code}</span>
                  </td>
                  <td style={{ padding: '1rem' }}>${c.total_billed_amount?.toLocaleString()}</td>
                  <td style={{ padding: '1rem', fontWeight: '700', color: 'var(--accent-emerald)' }}>${c.approved_amount?.toLocaleString()}</td>
                  <td style={{ padding: '1rem' }}>${c.patient_payable?.toLocaleString()}</td>
                  <td style={{ padding: '1rem' }}>
                    <span style={{
                      color: c.fraud_risk_score >= 60 ? 'var(--accent-rose)' : 'var(--accent-emerald)',
                      fontWeight: '700'
                    }}>
                      {c.fraud_risk_score}/100
                    </span>
                  </td>
                  <td style={{ padding: '1rem' }}>{getStatusBadge(c.status)}</td>
                  <td style={{ padding: '1rem' }}>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}
                      onClick={() => setExpandedClaim(expandedClaim === c.id ? null : c.id)}
                    >
                      {expandedClaim === c.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />} Details
                    </button>
                  </td>
                </tr>

                {/* Expanded Details Row */}
                {expandedClaim === c.id && (
                  <tr>
                    <td colSpan="8" style={{ padding: '1rem', background: 'rgba(0,0,0,0.2)' }}>
                      <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: 'rgba(255,255,255,0.02)' }}>
                        <h4 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--accent-cyan)' }}>
                          💡 AI Decision & COB Explanation
                        </h4>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                          {c.ai_recommendation}
                        </p>

                        <pre style={{
                          background: 'rgba(15,23,42,0.8)',
                          padding: '0.85rem',
                          borderRadius: 'var(--radius-md)',
                          fontSize: '0.775rem',
                          overflowX: 'auto',
                          color: '#a5b4fc'
                        }}>
                          {JSON.stringify(c.decision_explanation, null, 2)}
                        </pre>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {/* New Claim Entry Modal */}
      {showNewModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 50,
          padding: '1.5rem'
        }}>
          <div className="glass-card" style={{ maxWidth: '650px', width: '100%', padding: '2rem', maxHeight: '90vh', overflowY: 'auto' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '1.5rem' }}>Submit New Insurance Claim</h2>
            
            <form onSubmit={handleSubmitClaim}>
              <div className="grid-cols-2">
                <div className="input-group">
                  <label className="input-label">Patient ID</label>
                  <input type="number" className="input-field" value={patientId} onChange={(e) => setPatientId(e.target.value)} required />
                </div>
                <div className="input-group">
                  <label className="input-label">Hospital ID</label>
                  <input type="number" className="input-field" value={hospitalId} onChange={(e) => setHospitalId(e.target.value)} required />
                </div>
              </div>

              <div className="grid-cols-2">
                <div className="input-group">
                  <label className="input-label">Primary Policy ID</label>
                  <input type="number" className="input-field" value={primaryPolicyId} onChange={(e) => setPrimaryPolicyId(e.target.value)} required />
                </div>
                <div className="input-group">
                  <label className="input-label">Claim Type</label>
                  <select className="input-field" value={claimType} onChange={(e) => setClaimType(e.target.value)}>
                    <option value="INPATIENT">INPATIENT</option>
                    <option value="OUTPATIENT">OUTPATIENT</option>
                    <option value="EMERGENCY">EMERGENCY</option>
                    <option value="PHARMACY">PHARMACY</option>
                  </select>
                </div>
              </div>

              <div className="input-group">
                <label className="input-label">ICD-10 Diagnosis Code</label>
                <input type="text" className="input-field" value={diagnosisCode} onChange={(e) => setDiagnosisCode(e.target.value)} required />
              </div>

              <div style={{ marginTop: '1.5rem', marginBottom: '1.5rem' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '0.75rem' }}>Claim Line Items</h4>
                {items.map((it, idx) => (
                  <div key={idx} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <input type="text" className="input-field" placeholder="Description" value={it.item_description} onChange={(e) => {
                      const copy = [...items]; copy[idx].item_description = e.target.value; setItems(copy);
                    }} />
                    <input type="text" className="input-field" placeholder="Category" value={it.category} onChange={(e) => {
                      const copy = [...items]; copy[idx].category = e.target.value; setItems(copy);
                    }} />
                    <input type="text" className="input-field" placeholder="CPT Code" value={it.cpt_code} onChange={(e) => {
                      const copy = [...items]; copy[idx].cpt_code = e.target.value; setItems(copy);
                    }} />
                    <input type="number" className="input-field" placeholder="Billed ($)" value={it.billed_amount} onChange={(e) => {
                      const copy = [...items]; copy[idx].billed_amount = Number(e.target.value); setItems(copy);
                    }} />
                  </div>
                ))}
                <div style={{ textAlign: 'right', marginTop: '0.5rem', fontWeight: '700', color: 'var(--accent-cyan)' }}>
                  Total Billed: ${totalBilled.toLocaleString()}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowNewModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Run AI Adjudication & Submit</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Claims;
