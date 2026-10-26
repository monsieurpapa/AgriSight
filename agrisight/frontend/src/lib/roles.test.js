import { describe, it, expect } from 'vitest';
import { getRoleCode } from './roles';

// Regression: header showed "User" for admins because AuthContext preferred
// the display label `user_type` ("Administrator") over `user_type_code`.
// Report: docs/qa/qa-report-2026-10-26.md (P1 #8)
describe('getRoleCode', () => {
  it('prefers the machine code over the display label', () => {
    expect(getRoleCode({ user_type: 'Administrator', user_type_code: 'admin' })).toBe('admin');
    expect(getRoleCode({ user_type: 'Humanitarian Organization', user_type_code: 'humanitarian' })).toBe('humanitarian');
  });
  it('falls back to user_type when no code is present', () => {
    expect(getRoleCode({ user_type: 'researcher' })).toBe('researcher');
  });
  it('handles missing users', () => {
    expect(getRoleCode(null)).toBeNull();
    expect(getRoleCode({})).toBeNull();
  });
});
