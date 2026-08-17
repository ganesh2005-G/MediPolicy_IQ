import React, { useState, useEffect } from 'react';
import { claimsAPI } from '../services/api';
import { Sliders, Shield, Plus, CheckCircle } from 'lucide-react';

const PolicyRules = () => {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPolicies = async () => {
      try {
        const data = await claimsAPI.getPolicies();
        setPolicies(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPolicies();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '800' }}>Dynamic Policy Rule Engine Configurator</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Manage database-driven policy sub-limits, deductibles, co-pays, and exclusion rules</p>
      </div>

      <div className="grid-cols-2" style={{ marginBottom: '2rem' }}>
        {policies.map((p) => (
          <div key={p.id} className="glass-card" style={{ padding: '1.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div>
                <span className="badge badge-approved" style={{ marginBottom: '0.35rem' }}>{p.policy_type}</span>
                <h3 style={{ fontSize: '1.3rem', fontWeight: '700' }}>{p.policy_number}</h3>
              </div>
              <Shield size={28} color="var(--accent-blue)" />
            </div>

            <div className="grid-cols-2" style={{ gap: '1rem', background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1.25rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sum Insured</span>
                <p style={{ fontWeight: '700', fontSize: '1.1rem', color: 'var(--accent-emerald)' }}>${p.sum_insured?.toLocaleString()}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Deductible</span>
                <p style={{ fontWeight: '700', fontSize: '1.1rem' }}>${p.deductible?.toLocaleString()}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Co-pay %</span>
                <p style={{ fontWeight: '700', fontSize: '1.1rem' }}>{p.copay_percentage}%</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Room Rent Cap</span>
                <p style={{ fontWeight: '700', fontSize: '1.1rem', color: 'var(--accent-cyan)' }}>${p.room_rent_cap_per_day?.toLocaleString()}/day</p>
              </div>
            </div>

            <h4 style={{ fontSize: '0.9rem', fontWeight: '700', marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>Configured Dynamic Rules</h4>
            {p.rules && p.rules.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {p.rules.map((r) => (
                  <div key={r.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.65rem 0.85rem', background: 'rgba(15,23,42,0.6)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
                    <div>
                      <strong style={{ color: 'var(--accent-cyan)', display: 'block' }}>{r.rule_name}</strong>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Expr: {r.expression}</span>
                    </div>
                    <span className="badge badge-partially">{r.action}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No custom rules configured yet.</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PolicyRules;
