import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Stethoscope, UserCheck, User, LogIn, Sparkles, CheckCircle2 } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [email, setEmail] = useState('admin@medipolicy.iq');
  const [password, setPassword] = useState('Admin123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const demoPresets = [
    { role: 'Admin', email: 'admin@medipolicy.iq', pass: 'Admin123!', icon: ShieldCheck, color: '#3b82f6', desc: 'Full System & Rule Config Rights' },
    { role: 'Doctor', email: 'doctor@medipolicy.iq', pass: 'Doctor123!', icon: Stethoscope, color: '#10b981', desc: 'Medical OCR & Claim Upload' },
    { role: 'Processor', email: 'processor@medipolicy.iq', pass: 'Processor123!', icon: User, color: '#8b5cf6', desc: 'Claim Adjudication & Fraud Audit' },
    { role: 'Patient', email: 'patient@medipolicy.iq', pass: 'Patient123!', icon: UserCheck, color: '#06b6d4', desc: 'View Coverage & RAG Policy Chat' },
  ];

  const handleLogin = async (e) => {
    e?.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid email or password credentials');
    } finally {
      setLoading(false);
    }
  };

  const handlePresetSelect = (preset) => {
    setEmail(preset.email);
    setPassword(preset.pass);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at 50% 20%, #1e293b 0%, #0b0f19 100%)',
      padding: '2rem'
    }}>
      <div style={{
        maxWidth: '960px',
        width: '100%',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '2.5rem',
        alignItems: 'center'
      }}>
        
        {/* Left Side Branding */}
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(59, 130, 246, 0.1)', padding: '0.4rem 0.9rem', borderRadius: 'var(--radius-full)', border: '1px solid rgba(59, 130, 246, 0.3)', color: 'var(--accent-cyan)', fontSize: '0.85rem', fontWeight: '700', marginBottom: '1.5rem' }}>
            <Sparkles size={16} /> MediPolicy_IQ Platform v1.0
          </div>
          <h1 style={{ fontSize: '2.75rem', fontWeight: '800', lineHeight: 1.15, marginBottom: '1rem', background: 'linear-gradient(135deg, #ffffff 0%, #94a3b8 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            AI-Powered Healthcare Claims Intelligence
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', marginBottom: '2rem' }}>
            Automating claim adjudication, Coordination of Benefits (COB), medical document OCR, and explainable AI fraud detection.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {[
              "Dynamic Database Policy Rule Engine",
              "Multi-Policy Coordination of Benefits (COB)",
              "ICD-10 & CPT Medical Coding Verification",
              "Natural Language Policy RAG Assistant"
            ].map((feat, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', color: 'var(--text-primary)', fontSize: '0.925rem' }}>
                <CheckCircle2 size={18} color="#10b981" />
                <span>{feat}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side Login Card */}
        <div className="glass-card" style={{ padding: '2.5rem' }}>
          <div style={{ marginBottom: '1.75rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.35rem' }}>Sign In to Portal</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Select a quick demo persona or enter credentials below</p>
          </div>

          {/* Quick Persona Demo Selector */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.65rem', marginBottom: '1.5rem' }}>
            {demoPresets.map((p) => {
              const Icon = p.icon;
              const isSelected = email === p.email;
              return (
                <button
                  key={p.role}
                  type="button"
                  onClick={() => handlePresetSelect(p)}
                  style={{
                    padding: '0.65rem',
                    borderRadius: 'var(--radius-md)',
                    border: `1px solid ${isSelected ? p.color : 'var(--border-color)'}`,
                    background: isSelected ? `${p.color}15` : 'rgba(255,255,255,0.02)',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                    <Icon size={16} color={p.color} />
                    <span style={{ fontSize: '0.85rem', fontWeight: '700', color: isSelected ? '#fff' : 'var(--text-secondary)' }}>
                      {p.role} Login
                    </span>
                  </div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>{p.desc}</span>
                </button>
              );
            })}
          </div>

          {error && (
            <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', color: '#f87171', padding: '0.75rem', borderRadius: 'var(--radius-md)', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleLogin}>
            <div className="input-group">
              <label className="input-label">Email Address</label>
              <input
                type="email"
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="input-group" style={{ marginBottom: '1.5rem' }}>
              <label className="input-label">Password</label>
              <input
                type="password"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.8rem' }} disabled={loading}>
              <LogIn size={18} /> {loading ? 'Signing In...' : 'Authenticate Portal'}
            </button>
          </form>
        </div>

      </div>
    </div>
  );
};

export default Login;
