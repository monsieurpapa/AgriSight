import axios from 'axios';

// Backend serves API at /api/ so base URL should not include /api
const resolveBaseUrl = () => {
  const envBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL;
  const normalized =
    envBase && envBase !== '/'
      ? envBase.replace(/\/$/, '')
      : '';

  if (normalized) return normalized;

  if (import.meta.env.DEV) {
    return 'http://localhost:8000';
  }

  if (typeof window !== 'undefined') {
    return window.location.origin;
  }

  return '';
};

const API_BASE_URL = resolveBaseUrl();

// Debug: Log the resolved API base URL
console.log('API Client - Resolved API_BASE_URL:', API_BASE_URL);

// Create axios instance with default configuration
export const http = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Enable cookies for session authentication
  timeout: 30000, // 30 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// CSRF token handling for session authentication
let csrfToken = null;

const SAFE_METHODS = ['get', 'head', 'options'];

// Django sets the `csrftoken` cookie (and rotates it on login). Cookies are
// not port-scoped, so the SPA can read it in dev (5173 -> 8000) and prod.
export const readCsrfCookie = () => {
  if (typeof document === 'undefined' || !document.cookie) return null;
  const match = document.cookie.split(';').map((c) => c.trim()).find((c) => c.startsWith('csrftoken='));
  return match ? decodeURIComponent(match.slice('csrftoken='.length)) : null;
};

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

// Request interceptor
http.interceptors.request.use(
  async (config) => {
    const method = (config.method || 'get').toLowerCase();
    // Add CSRF token to unsafe requests. Previously the token lived only in
    // memory, so the first write after any full page load went out without
    // it and was rejected with 403 "CSRF token missing". Prefer the cookie
    // (always current, survives reloads and the rotation on login), then the
    // cached value, then fetch one.
    if (!SAFE_METHODS.includes(method) && !(config.url || '').includes('/csrf/')) {
      const token = readCsrfCookie() || csrfToken || (await getCsrfToken());
      if (token) {
        config.headers['X-CSRFToken'] = token;
      }
    }

    // Add request timestamp for debugging
    config.metadata = { startTime: new Date() };

    return config;
  },
  (error) => {
    return Promise.reject(createAPIError(error, 'REQUEST_ERROR'));
  }
);

// Only idempotent requests are retried automatically. Retrying a POST/PUT/
// PATCH/DELETE after a 5xx can apply the write twice (registration was sent
// 4x when the server returned 500).
// 500 is excluded: it is usually a deterministic server bug, and retrying only
// delays the error the user needs to see.
export const RETRYABLE_STATUSES = [408, 429, 502, 503, 504];
export const MAX_RETRIES = 3;
const MAX_RETRY_DELAY_MS = 8000;

export const shouldRetryRequest = (config, status, attempt) =>
  !config?.noRetry &&
  SAFE_METHODS.includes((config?.method || 'get').toLowerCase()) &&
  RETRYABLE_STATUSES.includes(status) &&
  attempt < MAX_RETRIES;

export const retryDelayMs = (attempt, retryAfterHeader) => {
  const retryAfterSeconds = Number(retryAfterHeader);
  if (Number.isFinite(retryAfterSeconds) && retryAfterSeconds > 0) {
    return Math.min(retryAfterSeconds * 1000, MAX_RETRY_DELAY_MS);
  }
  return Math.min(Math.pow(2, attempt) * 1000, MAX_RETRY_DELAY_MS);
};

// Response interceptor with comprehensive error handling and retry logic
http.interceptors.response.use(
  (response) => {
    // Log successful requests in development
    if (import.meta.env.DEV) {
      const duration = new Date() - response.config.metadata.startTime;
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`);
    }
    return response;
  },
  async (error) => {
    const apiError = createAPIError(error);
    const originalRequest = error.config;

    if (!originalRequest) {
      return Promise.reject(apiError);
    }

    // Initialize retry metadata if not present
    if (!originalRequest._retryMetadata) {
      originalRequest._retryMetadata = { count: 0 };
    }

    // Handle CSRF token refresh on 403 responses
    if (
      error.response?.status === 403 &&
      error.response?.data?.detail?.includes('CSRF')
    ) {
      if (!originalRequest._csrfRetry) {
        originalRequest._csrfRetry = true;
        csrfToken = null;
        const token = (await getCsrfToken()) || readCsrfCookie();
        if (token) {
          originalRequest.headers['X-CSRFToken'] = token;
          return http(originalRequest);
        }
      }
    }

    // Retry idempotent requests on transient failures with exponential backoff
    if (shouldRetryRequest(originalRequest, error.response?.status, originalRequest._retryMetadata.count)) {
      const retryDelay = retryDelayMs(originalRequest._retryMetadata.count, error.response?.headers?.['retry-after']);
      originalRequest._retryMetadata.count += 1;

      console.warn(
        `🔄 Retrying ${originalRequest.method?.toUpperCase()} ${originalRequest.url} (attempt ${originalRequest._retryMetadata.count}/${MAX_RETRIES}) after ${retryDelay}ms`
      );

      await new Promise((resolve) => setTimeout(resolve, retryDelay));
      return http(originalRequest);
    }

    // Handle 401 errors (authentication required)
    if (error.response?.status === 401) {
      // Clear any stored authentication data
      csrfToken = null;

      // Redirect to login if not already there
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    // Log errors in development
    if (import.meta.env.DEV) {
      console.error('❌ API Error:', apiError);
      if (originalRequest._retryMetadata.count > 0) {
        console.info(
          `Retry attempts: ${originalRequest._retryMetadata.count}/${originalRequest._retryMetadata.maxRetries}`
        );
      }
    }

    return Promise.reject(apiError);
  }
);

// Create standardized API error object
const createAPIError = (error, type = 'API_ERROR') => {
  const apiError = {
    type,
    message: 'An unexpected error occurred',
    status: 0,
    statusText: '',
    data: null,
    url: '',
    method: '',
    timestamp: new Date().toISOString(),
    originalError: error
  };

  if (error.response) {
    // Server responded with error status
    apiError.status = error.response.status;
    apiError.statusText = error.response.statusText;
    apiError.data = error.response.data;
    apiError.url = error.config?.url || '';
    apiError.method = error.config?.method?.toUpperCase() || '';
    
    // Extract meaningful error message
    if (error.response.data?.message) {
      apiError.message = error.response.data.message;
    } else if (error.response.data?.detail) {
      apiError.message = error.response.data.detail;
    } else if (error.response.data?.errors) {
      apiError.message = JSON.stringify(error.response.data.errors);
    } else if (error.response.data?.error) {
      apiError.message = error.response.data.error;
    } else if (typeof error.response.data === 'string') {
      apiError.message = error.response.data;
    } else {
      apiError.message = `Server error: ${error.response.status} ${error.response.statusText}`;
    }
  } else if (error.request) {
    // Request was made but no response received
    apiError.type = 'NETWORK_ERROR';
    apiError.message = 'Unable to connect to the server. Please check your internet connection.';
    apiError.url = error.config?.url || '';
    apiError.method = error.config?.method?.toUpperCase() || '';
  } else if (error.code === 'ECONNABORTED') {
    // Request timeout
    apiError.type = 'TIMEOUT';
    apiError.message = 'Request timed out. Please try again.';
    apiError.url = error.config?.url || '';
    apiError.method = error.config?.method?.toUpperCase() || '';
  } else {
    // Something else happened
    apiError.message = error.message || 'An unexpected error occurred';
  }

  return apiError;
};

// Enhanced API methods with error handling
const apiClient = {
  // GET request
  async get(url, config = {}) {
    try {
      const response = await http.get(url, config);
      return response.data;
    } catch (error) {
      throw error; // Re-throw the standardized error
    }
  },

  // POST request
  async post(url, data, config = {}) {
    try {
      const response = await http.post(url, data, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // PUT request
  async put(url, data, config = {}) {
    try {
      const response = await http.put(url, data, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // PATCH request
  async patch(url, data, config = {}) {
    try {
      const response = await http.patch(url, data, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // DELETE request
  async delete(url, config = {}) {
    try {
      const response = await http.delete(url, config);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Upload file
  async upload(url, formData, config = {}) {
    try {
      const response = await http.post(url, formData, {
        ...config,
        headers: {
          'Content-Type': 'multipart/form-data',
          ...config.headers,
        },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Download file
  async download(url, config = {}) {
    try {
      const response = await http.get(url, {
        ...config,
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await http.get('/api/health/', { timeout: 5000 });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get CSRF token
  async getCsrfToken() {
    try {
      const response = await http.get('/api/auth/csrf/');
      csrfToken = response.data.csrfToken;
      return csrfToken;
    } catch (error) {
      throw error;
    }
  }
};

// Utility functions for error handling
export const isNetworkError = (error) => {
  return error.type === 'NETWORK_ERROR' || error.status === 0;
};

export const isTimeoutError = (error) => {
  return error.type === 'TIMEOUT' || error.code === 'ECONNABORTED';
};

export const isAuthError = (error) => {
  return error.status === 401 || error.status === 403;
};

export const isServerError = (error) => {
  return error.status >= 500 && error.status < 600;
};

export const isClientError = (error) => {
  return error.status >= 400 && error.status < 500;
};

export const getErrorMessage = (error) => {
  if (typeof error === 'string') return error;
  if (error?.message) return error.message;
  if (error?.response?.data?.message) return error.response.data.message;
  if (error?.response?.data?.detail) return error.response.data.detail;
  return 'An unexpected error occurred';
};

export default apiClient;
