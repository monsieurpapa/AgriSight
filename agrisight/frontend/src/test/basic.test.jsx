import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

describe('Frontend Test Harness', () => {
  it('renders a basic sanity check', () => {
    render(<div>AgriSight UI</div>);
    expect(screen.getByText('AgriSight UI')).toBeInTheDocument();
  });
});
