import React from 'react';
import { ShieldAlert, AlertOctagon, CheckCircle2, FileSearch } from 'lucide-react';

const FraudAnalytics = () => {
  const mockRiskData = [
    { claimNumber: 'CLM-A89102', score: 85.0, level: 'HIGH', flag: 'HIGH_VALUE_CLAIM (>500k)', status: 'FLAGGED_FRAUD' },
    { claimNumber: 'CLM-B77211', score: 42.5, level: 'MEDIUM', flag: 'EXCESSIVE_LENGTH_OF_STAY', status: 'UNDER_REVIEW' },
    { claimNumber: 'CLM-C10992', score: 12.0, level: 'LOW', flag: 'None', status: 'APPROVED' },
    { claimNumber: 'CLM-D44105', score: 8.0, level: 'LOW', flag: 'None', status: 'APPROVED' },
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '800' }}>Claim Fraud Risk & Audit Trail</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Explainable AI anomaly detection, length-of-stay checks, and overbilling flags</p>
      </div>

      <div className="grid-cols-3" style={{ marginBottom: '2rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '600' }}>Flagged High-Risk Claims</span>
            <AlertOctagon size={20} color="var(--accent-rose)" />
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: '700', color: 'var(--accent-rose)' }}>1</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Requires manual audit investigation</span>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '600' }}>System Average Risk Score</span>
            <ShieldAlert size={20} color="var(--accent-amber)" />
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: '700' }}>14.2 / 100</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)' }}>-2.1 vs last week</span>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '600' }}>Active Anomaly Rules</span>
            <FileSearch size={20} color="var(--accent-cyan)" />
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: '700' }}>12 Active Rules</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)' }}>100% Operational</span>
        </div>
      </div>

      {/* Flagged Claims Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '1.25rem' }}>Active Risk Monitoring Log</h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase' }}>
              <th style={{ padding: '0.85rem' }}>Claim #</th>
              <th style={{ padding: '0.85rem' }}>Fraud Score</th>
              <th style={{ padding: '0.85rem' }}>Risk Level</th>
              <th style={{ padding: '0.85rem' }}>Primary Risk Flag</th>
              <th style={{ padding: '0.85rem' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {mockRiskData.map((row, i) => (
              <tr key={i} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9rem' }}>
                <td style={{ padding: '1rem', fontWeight: '700', color: 'var(--accent-cyan)' }}>{row.claimNumber}</td>
                <td style={{ padding: '1rem', fontWeight: '700', color: row.score >= 60 ? 'var(--accent-rose)' : 'var(--accent-emerald)' }}>
                  {row.score}/100
                </td>
                <td style={{ padding: '1rem' }}>
                  <span className={`badge ${row.level === 'HIGH' ? 'badge-fraud' : (row.level === 'MEDIUM' ? 'badge-review' : 'badge-approved')}`}>
                    {row.level}
                  </span>
                </td>
                <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{row.flag}</td>
                <td style={{ padding: '1rem' }}>
                  <span className="badge badge-partially">{row.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default FraudAnalytics;
