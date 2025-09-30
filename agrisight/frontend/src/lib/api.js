import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const http = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Wrap response to always return .data for convenience
const get = (url, config) => http.get(url, config).then((r) => r.data);
const post = (url, data, config) => http.post(url, data, config).then((r) => r.data);

export const regionsAPI = {
  getRegions() {
    return get('/api/regions/');
  },
  getRegion(id) {
    return get(`/api/regions/${id}/`);
  },
};

export const alertsAPI = {
  getAlerts() {
    return get('/api/alerts/');
  },
};

export const reportsAPI = {
  getReports() {
    return get('/api/reports/');
  },
  createReport(payload) {
    return post('/api/reports/', payload);
  },
};

export const organizationsAPI = {
  getOrganizations() {
    return get('/api/organizations/');
  },
};

export default {
  regionsAPI,
  alertsAPI,
  reportsAPI,
  organizationsAPI,
};


