import React, { useState } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from './AuthContext';
import { authAPI } from '../lib/authAPI';

// Regression: unmemoized hasPermission (and its siblings) in AuthContext were
// recreated on every AuthProvider render. Dashboard.jsx's data-fetch
// useEffect depends on [hasPermission], so an unstable reference there
// retriggers the effect on every unrelated render — React logged "Maximum
// update depth exceeded" once the dashboard could actually render at all.
// Found by /qa on 2026-07-30, while verifying the ISSUE-004 fix.
// Report: .gstack/qa-reports/qa-report-agrisight-2026-07-30.md

vi.mock('../lib/authAPI', () => ({
  authAPI: {
    getConfig: vi.fn(),
    getCurrentUser: vi.fn(),
  },
}));

const capturedRefs = [];

const Consumer = () => {
  const { hasPermission } = useAuth();
  capturedRefs.push(hasPermission);
  return <span>consumer</span>;
};

// The tick state lives ABOVE AuthProvider so that bumping it re-renders
// AuthProvider itself (not just its children) — that's what actually
// re-executes AuthProvider's function body and would recreate an unmemoized
// hasPermission. A tick state placed inside AuthProvider's children wouldn't
// exercise this bug at all, since re-rendering a child never re-renders its
// parent.
const Harness = () => {
  const [, setTick] = useState(0);
  return (
    <div>
      <button onClick={() => setTick((t) => t + 1)}>rerender</button>
      <AuthProvider>
        <Consumer />
      </AuthProvider>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    capturedRefs.length = 0;
    authAPI.getConfig.mockResolvedValue({ data: { rbac: {} } });
    authAPI.getCurrentUser.mockRejectedValue(new Error('not authenticated'));
  });

  it('keeps hasPermission referentially stable across unrelated re-renders', async () => {
    const user = userEvent.setup();

    render(<Harness />);

    await screen.findByText('consumer');
    const firstRef = capturedRefs[capturedRefs.length - 1];

    await act(async () => {
      await user.click(screen.getByText('rerender'));
    });
    await act(async () => {
      await user.click(screen.getByText('rerender'));
    });

    const lastRef = capturedRefs[capturedRefs.length - 1];
    expect(lastRef).toBe(firstRef);
  });
});
