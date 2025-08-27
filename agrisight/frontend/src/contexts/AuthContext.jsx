import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authAPI } from '../lib/api';
import { getErrorMessage } from '../lib/utils';

// Initial state
const initialState = {
  user: null,
  organization: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
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
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        organization: action.payload.organization,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };
    
    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        organization: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...initialState,
        isLoading: false,
      };
    
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };
    
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };
    
    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
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

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('authToken');
        const user = localStorage.getItem('user');
        const organization = localStorage.getItem('organization');

        if (token && user) {
          // Verify token is still valid
          try {
            const currentUser = await authAPI.getCurrentUser();
            dispatch({
              type: AUTH_ACTIONS.LOGIN_SUCCESS,
              payload: {
                user: currentUser,
                organization: organization ? JSON.parse(organization) : null,
                token,
              },
            });
          } catch (error) {
            // Token is invalid, clear storage
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            localStorage.removeItem('organization');
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
      const { token, user, organization } = response;

      // Store in localStorage
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));
      if (organization) {
        localStorage.setItem('organization', JSON.stringify(organization));
      }

      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: { user, organization, token },
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

  // Logout function
  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear localStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      localStorage.removeItem('organization');
      
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  // Register function
  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    
    try {
      const response = await authAPI.register(userData);
      
      // Registration successful, but may require approval
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
      
      return { 
        success: true, 
        message: response.message || 'Registration successful. Please wait for approval.',
        requiresApproval: response.requires_approval || false,
      };
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  };

  // Update user function
  const updateUser = (userData) => {
    dispatch({
      type: AUTH_ACTIONS.UPDATE_USER,
      payload: userData,
    });
    
    // Update localStorage
    const updatedUser = { ...state.user, ...userData };
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // Check if user has permission
  const hasPermission = (permission) => {
    if (!state.user || !state.user.permissions) return false;
    return state.user.permissions.includes(permission);
  };

  // Check if user has role
  const hasRole = (role) => {
    if (!state.user) return false;
    return state.user.role === role;
  };

  // Check if user can access region
  const canAccessRegion = (regionId) => {
    if (!state.user || !state.organization) return false;
    
    // Admin users can access all regions
    if (state.user.role === 'admin') return true;
    
    // Check if region is in organization's accessible regions
    if (state.organization.accessible_regions) {
      return state.organization.accessible_regions.includes(regionId);
    }
    
    return false;
  };

  const value = {
    ...state,
    login,
    logout,
    register,
    updateUser,
    clearError,
    hasPermission,
    hasRole,
    canAccessRegion,
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

