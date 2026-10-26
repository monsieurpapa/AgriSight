import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import { authAPI } from '../lib/authAPI';

// Regression: /api/auth/user/ returns user_type="Administrator" (label) and
// user_type_code="admin". AuthContext used the label as the role, so the
// header showed "User" and role-table permission lookups missed.
// Report: docs/qa/qa-report-2026-10-26.md (P1 #8)

vi.mock('../lib/authAPI', () => ({
  authAPI: { getConfig: vi.fn(), getCurrentUser: vi.fn() },
}));

const Probe = () => {
  const { isLoading, getUserTypeLabel, getUserType, hasPermission } = useAuth();
  if (isLoading) return <span>loading</span>;
  return (
    <span>
      {`${getUserType()}|${getUserTypeLabel()}|${hasPermission('generate_reports')}|${hasPermission('admin_access')}`}
    </span>
  );
};

describe('AuthContext roles', () => {
  beforeEach(() => {
    authAPI.getConfig.mockResolvedValue({ data: { rbac: {} } });
  });

  it('labels an admin as Administrator', async () => {
    authAPI.getCurrentUser.mockResolvedValue({
      data: { email: 'a@x.org', user_type: 'Administrator', user_type_code: 'admin', permissions: [] },
    });
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(await screen.findByText('admin|Administrator|true|true')).toBeTruthy();
  });

  it('applies role permissions from the role code', async () => {
    authAPI.getCurrentUser.mockResolvedValue({
      data: { email: 'h@x.org', user_type: 'Humanitarian Organization', user_type_code: 'humanitarian', permissions: [] },
    });
    render(<AuthProvider><Probe /></AuthProvider>);
    expect(await screen.findByText('humanitarian|Humanitarian Organization|true|false')).toBeTruthy();
  });
});
