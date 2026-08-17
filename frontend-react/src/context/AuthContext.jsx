import React, { createContext, useState, useEffect, useContext } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await authAPI.getCurrentUser();
          if (userData && userData.tenant_id) {
            localStorage.setItem('tenant_id', userData.tenant_id);
          }
          setUser(userData);
        } catch (err) {
          console.error("Auth session expired", err);
          logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  const login = async (username, password) => {
    const data = await authAPI.login(username, password);
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user_role', data.user_role);
    localStorage.setItem('user_email', data.user_email);
    setToken(data.access_token);
    
    // Fetch profile
    const profile = await authAPI.getCurrentUser();
    if (profile && profile.tenant_id) {
      localStorage.setItem('tenant_id', profile.tenant_id);
    }
    setUser(profile);
    return profile;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_email');
    localStorage.removeItem('tenant_id');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, role: user?.role, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
