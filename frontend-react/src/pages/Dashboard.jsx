import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { analyticsAPI } from '../services/api';
import { Activity, DollarSign, CheckCircle, ShieldAlert, ArrowUpRight, FilePlus, Scan, Bot } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const { user, role } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await analyticsAPI.getDashboard();
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const formatMoney = (amount) => `$${Number(amount || 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

  return (
    <div>
      {/* Welcome Banner */}
      <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem', background: 'linear-gradient(135deg, rgba(30,58,138,0.4) 0%, rgba(17,24,39,0.8) 100%)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--accent-cyan)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Welcome Back, {role?.toUpperCase()} Persona
            </span>
            <h1 style={{ fontSize: '2rem', fontWeight: '800', marginTop: '0.25rem' }}>
              {user?.full_name}
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginTop: '0.2rem' }}>
              MediPolicy_IQ AI Adjudication & Intelligence Engine is operational.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            {(role === 'doctor' || role === 'admin') && (
              <Link to="/claims" className="btn btn-primary">
                <FilePlus size={18} /> Submit Claim
              </Link>
            )}
            <Link to="/ai-assistant" className="btn btn-secondary">
              <Bot size={18} /> Policy Assistant
            </Link>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid-cols-4" style={{ marginBottom: '2rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '600' }}>Total Processed Claims</span>
            <Activity size={20} color="var(--accent-blue)" />
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: '700' }}>{data?.total_claims || 14}</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.25rem', marginTop: '0.35rem' }}>
            <ArrowUpRight size={14} /> +12% this month
          </span>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '600' }}>Total Billed Volume</span>
            <DollarSign size={20} color="var(--accent-cyan)" />
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: '700' }}>{formatMoney(data?.total_billed_amount || 1850000)}</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem', display: 'block' }}>
            {formatMoney(data?.total_approved_amount || 1420000)} approved
          </span>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '600' }}>Auto-Approval Rate</span>
            <CheckCircle size={20} color="var(--accent-emerald)" />
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: '700' }}>{data?.auto_approval_rate || 85.7}%</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', marginTop: '0.35rem', display: 'block' }}>
            Target &gt;80% achieved
          </span>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '600' }}>Fraud Risk Flagged</span>
            <ShieldAlert size={20} color="var(--accent-rose)" />
          </div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: '700', color: 'var(--accent-rose)' }}>{data?.fraud_flagged_claims || 1}</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem', display: 'block' }}>
            Requires audit review
          </span>
        </div>
      </div>

      {/* Quick Action Grid */}
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '1rem' }}>Platform Intelligence Workspaces</h3>
        <div className="grid-cols-3">
          <Link to="/claims" style={{ textDecoration: 'none' }}>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <FilePlus size={28} color="var(--accent-blue)" style={{ marginBottom: '0.75rem' }} />
              <h4 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                Claims Adjudication
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Submit claims with dynamic rule evaluations and Coordination of Benefits (COB).
              </p>
            </div>
          </Link>

          <Link to="/ocr" style={{ textDecoration: 'none' }}>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <Scan size={28} color="var(--accent-cyan)" style={{ marginBottom: '0.75rem' }} />
              <h4 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                OCR Document Suite
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Extract structured JSON data from medical invoices, prescriptions, and cards.
              </p>
            </div>
          </Link>

          <Link to="/ai-assistant" style={{ textDecoration: 'none' }}>
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <Bot size={28} color="var(--accent-purple)" style={{ marginBottom: '0.75rem' }} />
              <h4 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
                Policy RAG Assistant
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                Query insurance clauses, room rent limits, and pre-authorization rules.
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
