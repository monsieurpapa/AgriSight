import axios from 'axios';

// Align with Vite env naming and allow fallback in Docker
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Axios instance
const http = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Access token handling
let accessToken = localStorage.getItem('access_token') || null;
let isRefreshing = false;
let refreshQueue = [];

const setAccessToken = (token) => {
  accessToken = token;
  if (token) {
    localStorage.setItem('access_token', token);
  } else {
    localStorage.removeItem('access_token');
  }
};

const setRefreshToken = (token) => {
  if (token) {
    localStorage.setItem('refresh_token', token);
  } else {
    localStorage.removeItem('refresh_token');
  }
};

// Attach Authorization header
http.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Handle 401s and try refresh
http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return http(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        const resp = await axios.post(
          `${API_BASE_URL}/api/auth/refresh/`,
          { refresh: refreshToken },
          { withCredentials: true }
        );

        const newAccess = resp.data.access;
        const newRefresh = resp.data.refresh || refreshToken;
        setAccessToken(newAccess);
        setRefreshToken(newRefresh);

        refreshQueue.forEach((p) => p.resolve(newAccess));
        refreshQueue = [];

        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return http(originalRequest);
      } catch (refreshErr) {
        refreshQueue.forEach((p) => p.reject(refreshErr));
        refreshQueue = [];
        setAccessToken(null);
        setRefreshToken(null);
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  getConfig() {
    return http.get('/api/auth/config/');
  },
  async login({ email, password }) {
    const resp = await http.post('/api/auth/login/', { email, password });
    const { access, refresh } = resp.data || {};
    if (access) setAccessToken(access);
    if (refresh) setRefreshToken(refresh);

    // Prefer server-provided user payload; otherwise fetch current user
    let user = resp.data?.user;
    if (!user) {
      try {
        const me = await http.get('/api/auth/user/');
        user = me.data;
      } catch (e) {
        // swallow; caller will handle error reporting
      }
    }
    return { user };
  },
  async logout() {
    try {
      await http.post('/api/auth/logout/');
    } finally {
      setAccessToken(null);
      setRefreshToken(null);
    }
  },
  async register(payload) {
    return http.post('/api/auth/registration/', payload);
  },
  getCurrentUser() {
    return http.get('/api/auth/user/');
  },
  updateUser(data) {
    return http.put('/api/auth/user/', data);
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
    const { access, refresh, user } = resp.data;
    if (access) setAccessToken(access);
    if (refresh) setRefreshToken(refresh);
    return { user };
  },
  async facebookLogin(accessToken) {
    const resp = await http.post('/api/auth/facebook/', { access_token: accessToken });
    const { access, refresh, user } = resp.data;
    if (access) setAccessToken(access);
    if (refresh) setRefreshToken(refresh);
    return { user };
  },
  async githubLogin(accessToken) {
    const resp = await http.post('/api/auth/github/', { access_token: accessToken });
    const { access, refresh, user } = resp.data;
    if (access) setAccessToken(access);
    if (refresh) setRefreshToken(refresh);
    return { user };
  },
};

export default authAPI;


