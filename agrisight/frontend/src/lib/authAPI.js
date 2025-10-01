import axios from 'axios';

// Align with Vite env naming and allow fallback in Docker
// Backend serves auth at /api/auth/ so base URL should not include /api
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Debug: Log the resolved API base URL
console.log('AuthAPI - Resolved API_BASE_URL:', API_BASE_URL);

// Axios instance for session-based authentication
const http = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Enable cookies for session authentication
  headers: {
    'Content-Type': 'application/json',
  },
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

export const authAPI = {
  async getConfig() {
    return http.get('/api/auth/config/');
  },
  async login({ email, password }) {
    console.log('Login request to:', `${API_BASE_URL}/api/auth/login/`);
    
    // Ensure we have a CSRF token before making the request
    if (!csrfToken) {
      await getCsrfToken();
    }
    
    const resp = await http.post('/api/auth/login/', { email, password });
    
    // For session authentication, the response should contain user data
    let user = resp.data?.user;
    if (!user) {
      try {
        const me = await http.get('/api/auth/user/');
        user = me.data;
      } catch (e) {
        console.error('Failed to fetch user after login:', e);
      }
    }
    return { user };
  },
  async logout() {
    try {
      await http.post('/api/auth/logout/');
    } catch (e) {
      console.error('Logout error:', e);
    }
  },
  async register(payload) {
    return http.post('/api/auth/registration/', payload);
  },
  getCurrentUser() {
    return http.get('/api/auth/user/');
  },
  updateUser(data) {
    return http.patch('/api/auth/user/', data);
  },
  changePassword(data) {
    return http.post('/api/auth/password/change/', data);
  },
  requestPasswordReset(email) {
    return http.post('/api/auth/password/reset/', { email });
  },
  confirmPasswordReset({ uid, token, new_password1, new_password2 }) {
    return http.post('/api/auth/password/reset/confirm/', { uid, token, new_password1, new_password2 });
  },
  verifyEmail(key) {
    return http.post('/api/auth/registration/verify-email/', { key });
  },
  resendEmailVerification(email) {
    return http.post('/api/auth/registration/resend-email/', { email });
  },
  async googleLogin(accessToken) {
    const resp = await http.post('/api/auth/google/', { access_token: accessToken });
    const { user } = resp.data;
    return { user };
  },
  async facebookLogin(accessToken) {
    const resp = await http.post('/api/auth/facebook/', { access_token: accessToken });
    const { user } = resp.data;
    return { user };
  },
  async githubLogin(accessToken) {
    const resp = await http.post('/api/auth/github/', { access_token: accessToken });
    const { user } = resp.data;
    return { user };
  },
};

export default authAPI;