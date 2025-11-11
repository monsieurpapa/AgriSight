import apiClient from './apiClient';

// This module wraps the centralized apiClient to avoid duplicate axios instances
// and duplicated CSRF handling. It preserves the previous authAPI method shapes
// (returning objects with a `data` property where the rest of the app expects it)
// while delegating network calls to apiClient.

const wrap = (data) => ({ data });

export const authAPI = {
  async getConfig() {
    const data = await apiClient.get('/api/auth/config/');
    return wrap(data);
  },

  async login({ email, password }) {
    // Ensure CSRF token is loaded
    try {
      await apiClient.getCsrfToken();
    } catch (e) {
      // continue; apiClient will handle errors
    }

    const resp = await apiClient.post('/api/auth/login/', { email, password });

    // resp may include { user } or may be empty; if missing, fetch /user/
    let user = resp?.user;
    if (!user) {
      const me = await apiClient.get('/api/auth/user/');
      user = me;
    }
    return { user };
  },

  async logout() {
    try {
      await apiClient.post('/api/auth/logout/');
      return { data: null };
    } catch (e) {
      console.error('Logout error:', e);
      return { data: null };
    }
  },

  async register(payload) {
    const data = await apiClient.post('/api/auth/registration/', payload);
    return wrap(data);
  },

  async getCurrentUser() {
    const data = await apiClient.get('/api/auth/user/');
    return wrap(data);
  },

  async updateUser(dataPayload) {
    const data = await apiClient.patch('/api/auth/user/', dataPayload);
    return wrap(data);
  },

  async changePassword(passwordData) {
    const data = await apiClient.post('/api/auth/password/change/', passwordData);
    return wrap(data);
  },

  async requestPasswordReset(email) {
    const data = await apiClient.post('/api/auth/password/reset/', { email });
    return wrap(data);
  },

  async confirmPasswordReset(resetData) {
    const data = await apiClient.post('/api/auth/password/reset/confirm/', resetData);
    return wrap(data);
  },

  async verifyEmail(key) {
    const data = await apiClient.post('/api/auth/registration/verify-email/', { key });
    return wrap(data);
  },

  async resendEmailVerification(email) {
    const data = await apiClient.post('/api/auth/registration/resend-email/', { email });
    return wrap(data);
  },

  async googleLogin(accessToken) {
    const resp = await apiClient.post('/api/auth/google/', { access_token: accessToken });
    const user = resp?.user;
    return { user };
  },

  async facebookLogin(accessToken) {
    const resp = await apiClient.post('/api/auth/facebook/', { access_token: accessToken });
    const user = resp?.user;
    return { user };
  },

  async githubLogin(accessToken) {
    const resp = await apiClient.post('/api/auth/github/', { access_token: accessToken });
    const user = resp?.user;
    return { user };
  },
};

export default authAPI;