import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, ShieldCheck, Stethoscope, UserCheck } from 'lucide-react';

const Navbar = () => {
  const { user, role, logout } = useAuth();

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin': return <ShieldCheck size={18} color="#3b82f6" />;
      case 'doctor': return <Stethoscope size={18} color="#10b981" />;
      case 'patient': return <UserCheck size={18} color="#06b6d4" />;
      default: return <User size={18} color="#8b5cf6" />;
    }
  };

  return (
    <header style={{
      height: '70px',
      borderBottom: '1px solid var(--border-color)',
      background: 'rgba(15, 23, 42, 0.9)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 2rem',
      position: 'sticky',
      top: 0,
      zIndex: 40
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'var(--gradient-brand)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontWeight: '700',
          fontSize: '1.2rem'
        }}>
          IQ
        </div>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--text-primary)' }}>MediPolicy_IQ</h2>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Enterprise Healthcare Claims Intelligence</p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {user && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            background: 'rgba(255,255,255,0.04)',
            padding: '0.4rem 0.9rem',
            borderRadius: 'var(--radius-full)',
            border: '1px solid var(--border-color)'
          }}>
            {getRoleIcon(role)}
            <div>
              <span style={{ fontSize: '0.85rem', fontWeight: '600', display: 'block', lineHeight: 1.2 }}>
                {user.full_name}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', textTransform: 'uppercase', fontWeight: '700' }}>
                {role} Persona
              </span>
            </div>
          </div>
        )}

        <button onClick={logout} className="btn btn-secondary" style={{ padding: '0.45rem 0.9rem', fontSize: '0.85rem' }}>
          <LogOut size={16} /> Logout
        </button>
      </div>
    </header>
  );
};

export default Navbar;
