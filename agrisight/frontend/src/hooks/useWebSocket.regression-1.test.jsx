import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import useWebSocket from './useWebSocket';

// Regression: ISSUE-003 — WebSocketContext passed a brand-new options object
// (and a brand-new onMessage function) on every render. Because useWebSocket's
// `connect` callback depended on the whole `options` object, its identity
// changed every render, which retriggered the mount effect and tore down /
// reopened the socket on every render — a runaway reconnect loop that hung
// the app blank right after login.
// Found by /qa on 2026-07-30. Report: .gstack/qa-reports/qa-report-agrisight-2026-07-30.md

class MockWebSocket {
  static instances = [];

  constructor(url) {
    this.url = url;
    this.readyState = 0; // CONNECTING
    MockWebSocket.instances.push(this);
  }

  send() {}

  close(code = 1000, reason = '') {
    this.readyState = 3; // CLOSED
    if (this.onclose) this.onclose({ code, reason });
  }
}

describe('useWebSocket', () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.stubGlobal('WebSocket', MockWebSocket);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('does not reopen the socket when the caller passes a new options object with the same values on rerender', () => {
    const url = 'ws://localhost:8080/ws/';

    const { rerender } = renderHook(
      ({ onMessage }) =>
        useWebSocket(url, {
          authToken: null,
          onMessage,
          maxReconnectAttempts: 5,
          reconnectInterval: 3000,
          shouldConnect: true,
        }),
      { initialProps: { onMessage: () => {} } }
    );

    expect(MockWebSocket.instances).toHaveLength(1);

    // Simulate WebSocketContext re-rendering with a brand-new inline
    // onMessage function and options object (same primitive values) — this
    // is exactly what happened on every state update in the real provider.
    rerender({ onMessage: () => {} });
    rerender({ onMessage: () => {} });
    rerender({ onMessage: () => {} });

    expect(MockWebSocket.instances).toHaveLength(1);
  });

  it('does reconnect when the url actually changes', () => {
    const { rerender } = renderHook(({ url }) => useWebSocket(url, { shouldConnect: true }), {
      initialProps: { url: 'ws://localhost:8080/ws/' },
    });

    expect(MockWebSocket.instances).toHaveLength(1);

    rerender({ url: 'ws://localhost:8080/ws/region/abc/' });

    expect(MockWebSocket.instances).toHaveLength(2);
  });
});
