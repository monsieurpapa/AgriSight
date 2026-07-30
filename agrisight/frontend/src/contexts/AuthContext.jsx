import React, { createContext, useContext, useReducer, useEffect, useCallback, useMemo } from 'react';
import { authAPI } from '../lib/authAPI';
import { getErrorMessage } from '../lib/utils';

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  authConfig: null,
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR',
  UPDATE_USER: 'UPDATE_USER',
  SET_CONFIG: 'SET_CONFIG',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_FAILURE: 'REGISTER_FAILURE',
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
      return {
        ...state,
        isLoading: true,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.REGISTER_FAILURE:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };

    case AUTH_ACTIONS.REGISTER_SUCCESS:
      return {
        ...state,
        isLoading: false,
        error: null,
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...initialState,
        isLoading: false,
        authConfig: state.authConfig, // Preserve config
      };

    case AUTH_ACTIONS.SET_LOADING:
      if (state.isLoading === action.payload) return state;
      return {
        ...state,
        isLoading: action.payload,
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      if (state.error == null) return state;
      return {
        ...state,
        error: null,
      };

    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };

    case AUTH_ACTIONS.SET_CONFIG:
      return {
        ...state,
        authConfig: action.payload,
      };

    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Load authentication configuration
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await authAPI.getConfig();
        dispatch({
          type: AUTH_ACTIONS.SET_CONFIG,
          payload: response.data,
        });
      } catch (error) {
        console.error('Failed to load auth config:', error);
      }
    };

    loadConfig();
  }, []);

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // For session authentication, check if user is authenticated by calling the user endpoint
        const response = await authAPI.getCurrentUser();
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: {
            user: response.data,
          },
        });
      } catch (error) {
        // User is not authenticated - this is normal for unauthenticated users
        console.log('User not authenticated:', error.message);
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      }
    };

    // Add timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
    }, 5000); // 5 second timeout

    initializeAuth().finally(() => {
      clearTimeout(timeoutId);
    });
  }, []);

  // Login function
  const login = useCallback(async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      const response = await authAPI.login(credentials);

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user: response.user },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  }, []);

  // Register function
  const register = useCallback(async (userData) => {
    dispatch({ type: AUTH_ACTIONS.REGISTER_START });

    try {
      const response = await authAPI.register(userData);

      dispatch({ type: AUTH_ACTIONS.REGISTER_SUCCESS });

      return {
        success: true,
        message: 'Registration successful. Please check your email to verify your account.',
        data: response.data,
      };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch({
        type: AUTH_ACTIONS.REGISTER_FAILURE,
        payload: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  }, []);

  // Logout function
  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  }, []);

  // Social login functions
  const googleLogin = useCallback(async (accessToken) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      const response = await authAPI.googleLogin(accessToken);

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user: response.user },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  }, []);

  const facebookLogin = useCallback(async (accessToken) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      const response = await authAPI.facebookLogin(accessToken);

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user: response.user },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  }, []);

  const githubLogin = useCallback(async (accessToken) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });

    try {
      const response = await authAPI.githubLogin(accessToken);

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user: response.user },
      });

      return { success: true };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  }, []);

  // Password reset functions
  const requestPasswordReset = useCallback(async (email) => {
    try {
      await authAPI.requestPasswordReset(email);
      return { success: true, message: 'Password reset email sent.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  }, []);

  const confirmPasswordReset = useCallback(async (resetData) => {
    try {
      await authAPI.confirmPasswordReset(resetData);
      return { success: true, message: 'Password reset successful.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  }, []);

  // Email verification functions
  const verifyEmail = useCallback(async (key) => {
    try {
      await authAPI.verifyEmail(key);
      return { success: true, message: 'Email verified successfully.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  }, []);

  const resendEmailVerification = useCallback(async (email) => {
    try {
      await authAPI.resendEmailVerification(email);
      return { success: true, message: 'Verification email sent.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  }, []);

  // Update user function
  const updateUser = useCallback(async (userData) => {
    try {
      const response = await authAPI.updateUser(userData);
      dispatch({
        type: AUTH_ACTIONS.UPDATE_USER,
        payload: response.data,
      });
      return { success: true };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  }, []);

  // Change password function
  const changePassword = useCallback(async (passwordData) => {
    try {
      await authAPI.changePassword(passwordData);
      return { success: true, message: 'Password changed successfully.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  }, []);

  // Clear error function
  const clearError = useCallback(() => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  }, []);

  // Utility functions
  // These read `state`, so they're recreated when (and only when) state
  // actually changes — that's correct, but they must stay useCallback-wrapped
  // rather than plain functions so consumers with them in a dependency array
  // (e.g. Dashboard.jsx's data-fetch effect) don't re-fire on every unrelated
  // AuthProvider render. Regression: an unmemoized `hasPermission` caused
  // "Maximum update depth exceeded" once the dashboard could render at all
  // (found 2026-07-30 while verifying the ISSUE-004 fix).
  const hasRole = useCallback((role) => {
    if (!state.user) return false;
    // Handle both user_type and user_type_code for backward compatibility
    return state.user.user_type === role || state.user.user_type_code === role;
  }, [state.user]);

  const isAdmin = useCallback(() => hasRole('admin'), [hasRole]);

  const hasPermission = useCallback((permission) => {
    if (!state.user) return false;

    // Admin has all permissions
    if (hasRole('admin')) return true;

    // Check user-specific permissions
    if (state.user.permissions && state.user.permissions.includes(permission)) {
      return true;
    }

    const rolePermissions =
      state.authConfig?.rbac?.role_permissions ||
      {
        'admin': ['*'], // All permissions
        'humanitarian': ['view_data', 'export_data', 'generate_reports', 'view_analytics'],
        'cooperative': ['view_data', 'view_analytics', 'manage_regions', 'view_stress_events'],
        'government': ['view_data', 'view_analytics', 'manage_organizations', 'view_all_regions'],
        'researcher': ['view_data', 'view_analytics', 'export_data', 'view_stress_events', 'view_conflict_events']
      };

    const userRole = state.user.user_type || state.user.user_type_code;
    const permissions = rolePermissions[userRole] || [];

    return permissions.includes('*') || permissions.includes(permission);
  }, [state.user, state.authConfig, hasRole]);

  const getUserType = useCallback(() => {
    if (!state.user) return null;
    return state.user.user_type || state.user.user_type_code;
  }, [state.user]);

  const getUserTypeLabel = useCallback(() => {
    const userType = getUserType();
    const labels =
      state.authConfig?.rbac?.role_labels ||
      {
        'admin': 'Administrator',
        'humanitarian': 'Humanitarian Organization',
        'cooperative': 'Agricultural Cooperative',
        'government': 'Government Agency',
        'researcher': 'Researcher'
      };
    return labels[userType] || 'User';
  }, [getUserType, state.authConfig]);

  const getDefaultPath = useCallback(() => {
    const routePriority = [
      { path: '/', permission: 'view_data' },
      { path: '/analytics', permission: 'view_analytics' },
      { path: '/reports', permission: 'generate_reports' },
      { path: '/exports', permission: 'export_data' },
      { path: '/regions', permission: 'manage_regions' },
      { path: '/stress-events', permission: 'view_stress_events' },
      { path: '/alerts', permission: 'view_data' },
      { path: '/organizations', permission: 'manage_organizations' },
    ];

    for (const route of routePriority) {
      if (hasPermission(route.permission)) {
        return route.path;
      }
    }

    return '/profile';
  }, [hasPermission]);

  const value = useMemo(() => ({
    ...state,
    login,
    register,
    logout,
    googleLogin,
    facebookLogin,
    githubLogin,
    requestPasswordReset,
    confirmPasswordReset,
    verifyEmail,
    resendEmailVerification,
    updateUser,
    changePassword,
    clearError,
    hasRole,
    isAdmin,
    hasPermission,
    getUserType,
    getUserTypeLabel,
    getDefaultPath,
  }), [
    state,
    login,
    register,
    logout,
    googleLogin,
    facebookLogin,
    githubLogin,
    requestPasswordReset,
    confirmPasswordReset,
    verifyEmail,
    resendEmailVerification,
    updateUser,
    changePassword,
    clearError,
    hasRole,
    isAdmin,
    hasPermission,
    getUserType,
    getUserTypeLabel,
    getDefaultPath,
  ]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
