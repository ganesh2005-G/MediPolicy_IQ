import axios from 'axios';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token and X-Tenant-ID to outgoing requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const tenantId = localStorage.getItem('tenant_id');
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId;
  }
  return config;
}, (error) => Promise.reject(error));

export const authAPI = {
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const res = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return res.data;
  },
  getCurrentUser: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  }
};

export const claimsAPI = {
  getClaims: async () => (await api.get('/claims/')).data,
  submitClaim: async (claimData) => (await api.post('/claims/', claimData)).data,
  getPatients: async () => (await api.get('/patients/')).data,
  getPolicies: async () => (await api.get('/policies/')).data,
};

export const ocrAPI = {
  processDocument: async (docType, sampleType) => {
    const formData = new FormData();
    formData.append('doc_type', docType);
    formData.append('sample_type', sampleType);
    return (await api.post('/ocr/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })).data;
  }
};

export const ragAPI = {
  queryPolicy: async (query, policyNumber) => (await api.post('/rag/query', { query, policy_number: policyNumber })).data
};

export const analyticsAPI = {
  getDashboard: async () => (await api.get('/analytics/dashboard')).data
};

export default api;
