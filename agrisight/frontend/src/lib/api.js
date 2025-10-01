import axios from 'axios';

// Backend serves API at /api/v1/ so base URL should not include /api
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

const http = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// CSRF token handling for session authentication
let csrfToken = null;

const getCsrfToken = async () => {
  if (!csrfToken) {
    try {
      const response = await http.get('/api/auth/csrf/');
      csrfToken = response.data.csrfToken;
    } catch (error) {
      console.error('Failed to get CSRF token:', error);
    }
  }
  return csrfToken;
};

// Simplified request interceptor - no async operations
http.interceptors.request.use((config) => {
  // Skip CSRF for GET requests and CSRF endpoint itself
  if (config.method !== 'get' && !config.url.includes('/csrf/') && csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

// Handle CSRF token refresh on 403 responses
http.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 403 && error.response?.data?.detail?.includes('CSRF')) {
      // Clear cached CSRF token and retry
      csrfToken = null;
      const originalRequest = error.config;
      if (!originalRequest._retry) {
        originalRequest._retry = true;
        const token = await getCsrfToken();
        if (token) {
          originalRequest.headers['X-CSRFToken'] = token;
          return http(originalRequest);
        }
      }
    }
    return Promise.reject(error);
  }
);

// Wrap response to always return .data for convenience
const get = (url, config) => http.get(url, config).then((r) => r.data);
const post = (url, data, config) => http.post(url, data, config).then((r) => r.data);

export const regionsAPI = {
  getRegions() {
    return get('/api/v1/geospatial/regions/');
  },
  getRegion(id) {
    return get(`/api/v1/geospatial/regions/${id}/`);
  },
};

export const alertsAPI = {
  getAlerts() {
    return get('/api/v1/reports-alerts/alerts/');
  },
};

export const reportsAPI = {
  getReports() {
    return get('/api/v1/reports-alerts/reports/');
  },
  createReport(payload) {
    return post('/api/v1/reports-alerts/reports/', payload);
  },
};

export const organizationsAPI = {
  getOrganizations() {
    return get('/api/v1/organizations/');
  },
};

export default {
  regionsAPI,
  alertsAPI,
  reportsAPI,
  organizationsAPI,
};


