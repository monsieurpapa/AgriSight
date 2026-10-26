import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import { isTransientAuthError } from '../lib/authRetry';
import { authAPI } from '../lib/authAPI';

// Regression: a 429 (or 5xx / network error) from /api/auth/user/ during the
// initial session check was treated as "not authenticated", so a throttled or
// restarting backend bounced logged-in users to /landing.
// Report: .gstack/qa-reports/qa-report-agrisight-2026-10-26.md (P0 #1)

vi.mock('../lib/authAPI', () => ({
  authAPI: {
    getConfig: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

const Status = () => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <span>loading</span>;
  return <span>{isAuthenticated ? 'authenticated' : 'anonymous'}</span>;
};

describe('AuthContext session check', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    authAPI.getConfig.mockResolvedValue({ data: { rbac: {} } });
    authAPI.getCurrentUser.mockReset();
  });
  afterEach(() => vi.useRealTimers());

  it('classifies transient vs. definitive errors', () => {
    expect(isTransientAuthError({ status: 429 })).toBe(true);
    expect(isTransientAuthError({ status: 503 })).toBe(true);
    expect(isTransientAuthError({ type: 'NETWORK_ERROR', status: 0 })).toBe(true);
    expect(isTransientAuthError({ status: 403 })).toBe(false);
    expect(isTransientAuthError({ status: 401 })).toBe(false);
    expect(isTransientAuthError(new Error('boom'))).toBe(false);
  });

  it('stays logged in when the first session check is rate limited', async () => {
    authAPI.getCurrentUser
      .mockRejectedValueOnce({ status: 429, message: 'Too many requests' })
      .mockResolvedValueOnce({ data: { email: 'a@b.c', user_type_code: 'admin' } });

    render(<AuthProvider><Status /></AuthProvider>);
    await act(async () => { await vi.advanceTimersByTimeAsync(1500); });

    expect(await screen.findByText('authenticated')).toBeTruthy();
    expect(authAPI.getCurrentUser).toHaveBeenCalledTimes(2);
  });

  it('does not retry a definitive 403', async () => {
    authAPI.getCurrentUser.mockRejectedValue({ status: 403, message: 'Forbidden' });

    render(<AuthProvider><Status /></AuthProvider>);

    expect(await screen.findByText('anonymous')).toBeTruthy();
    expect(authAPI.getCurrentUser).toHaveBeenCalledTimes(1);
  });
});
