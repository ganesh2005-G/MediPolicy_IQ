import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, FileText, Scan, Sliders, Bot, ShieldAlert } from 'lucide-react';

const Sidebar = () => {
  const { role } = useAuth();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['admin', 'doctor', 'claim_processor', 'patient'] },
    { path: '/claims', label: 'Claims Adjudication', icon: FileText, roles: ['admin', 'doctor', 'claim_processor', 'patient'] },
    { path: '/ocr', label: 'OCR Document Suite', icon: Scan, roles: ['admin', 'doctor', 'claim_processor'] },
    { path: '/policy-rules', label: 'Dynamic Rule Engine', icon: Sliders, roles: ['admin', 'claim_processor'] },
    { path: '/ai-assistant', label: 'AI Policy Assistant (RAG)', icon: Bot, roles: ['admin', 'doctor', 'claim_processor', 'patient'] },
    { path: '/fraud-analytics', label: 'Fraud Analytics & Risk', icon: ShieldAlert, roles: ['admin', 'claim_processor'] },
  ];

  const allowedItems = navItems.filter(item => item.roles.includes(role || 'patient'));

  return (
    <aside style={{
      width: '260px',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-color)',
      padding: '1.5rem 1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '0.5rem'
    }}>
      <div style={{ padding: '0 0.75rem 1rem', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Platform Navigation
      </div>

      {allowedItems.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.path}
            to={item.path}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.85rem',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              fontWeight: '600',
              fontSize: '0.9rem',
              color: isActive ? '#ffffff' : 'var(--text-secondary)',
              background: isActive ? 'var(--gradient-brand)' : 'transparent',
              boxShadow: isActive ? '0 4px 15px rgba(6, 182, 212, 0.25)' : 'none',
              transition: 'all 0.2s ease'
            })}
          >
            <Icon size={18} />
            {item.label}
          </NavLink>
        );
      })}
    </aside>
  );
};

export default Sidebar;
