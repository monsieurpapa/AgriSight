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
        const token = localStorage.getItem('access_token');
        const refresh = localStorage.getItem('refresh_token');

        if (token || refresh) {
          // Verify token is still valid by getting current user
          try {
            const response = await authAPI.getCurrentUser();
            dispatch({
              type: AUTH_ACTIONS.LOGIN_SUCCESS,
              payload: {
                user: response.data,
              },
            });
          } catch (error) {
            // Token is invalid, clear storage
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
          }
        } else {
          dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (credentials) => {
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
  };

  // Register function
  const register = async (userData) => {
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
  };

  // Logout function
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  // Social login functions
  const googleLogin = async (accessToken) => {
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
  };

  const facebookLogin = async (accessToken) => {
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
  };

  const githubLogin = async (accessToken) => {
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
  };

  // Password reset functions
  const requestPasswordReset = async (email) => {
    try {
      await authAPI.requestPasswordReset(email);
      return { success: true, message: 'Password reset email sent.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  };

  const confirmPasswordReset = async (resetData) => {
    try {
      await authAPI.confirmPasswordReset(resetData);
      return { success: true, message: 'Password reset successful.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  };

  // Email verification functions
  const verifyEmail = async (key) => {
    try {
      await authAPI.verifyEmail(key);
      return { success: true, message: 'Email verified successfully.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  };

  const resendEmailVerification = async (email) => {
    try {
      await authAPI.resendEmailVerification(email);
      return { success: true, message: 'Verification email sent.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  };

  // Update user function
  const updateUser = async (userData) => {
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
  };

  // Change password function
  const changePassword = async (passwordData) => {
    try {
      await authAPI.changePassword(passwordData);
      return { success: true, message: 'Password changed successfully.' };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      return { success: false, error: errorMessage };
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Utility functions
  const hasRole = (role) => {
    if (!state.user) return false;
    return state.user.user_type_code === role;
  };

  const isAdmin = () => hasRole('admin');

  const value = {
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
  };

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
