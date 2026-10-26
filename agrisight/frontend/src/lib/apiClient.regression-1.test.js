import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import apiClient, { http, readCsrfCookie, shouldRetryRequest, retryDelayMs } from './apiClient';

// Regressions from docs/qa/qa-report-2026-10-26.md:
//  P1 #6 — retry logic was inverted: POST/PUT/DELETE were retried on 5xx
//          (registration was sent 4x), GETs never were.
//  P1 #9 — the CSRF token lived only in memory, so the first write after a
//          page reload went out without X-CSRFToken and got a 403.

const calls = [];
let responder;

const adapter = async (config) => {
  calls.push({ method: config.method, url: config.url, csrf: config.headers?.['X-CSRFToken'] });
  const { status, data = {}, headers = {} } = responder(config, calls.length);
  const response = { data, status, statusText: String(status), headers, config };
  if (status >= 400) {
    const err = new Error(`Request failed with status ${status}`);
    err.config = config;
    err.response = response;
    err.isAxiosError = true;
    throw err;
  }
  return response;
};

describe('apiClient', () => {
  const originalAdapter = http.defaults.adapter;

  beforeEach(() => {
    calls.length = 0;
    http.defaults.adapter = adapter;
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'log').mockImplementation(() => {});
    document.cookie = 'csrftoken=cookie-token-123; path=/';
  });

  afterEach(() => {
    http.defaults.adapter = originalAdapter;
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it('reads the csrftoken cookie', () => {
    expect(readCsrfCookie()).toBe('cookie-token-123');
  });

  it('sends X-CSRFToken from the cookie on the first write after a reload', async () => {
    responder = () => ({ status: 201, data: { ok: true } });
    await apiClient.post('/api/v1/api-keys/keys/', { name: 'k' });
    expect(calls).toHaveLength(1);
    expect(calls[0].csrf).toBe('cookie-token-123');
  });

  it('does not attach a CSRF header to GETs', async () => {
    responder = () => ({ status: 200 });
    await apiClient.get('/api/v1/organizations/');
    expect(calls[0].csrf).toBeUndefined();
  });

  it('never retries a failed POST', async () => {
    responder = () => ({ status: 503 });
    await expect(apiClient.post('/api/auth/registration/', {})).rejects.toMatchObject({ status: 503 });
    expect(calls).toHaveLength(1);
  });

  it('retries a GET on 503 and succeeds', async () => {
    vi.useFakeTimers();
    responder = (_c, n) => (n === 1 ? { status: 503 } : { status: 200, data: { ok: 1 } });
    const promise = apiClient.get('/api/v1/geospatial/regions/');
    await vi.advanceTimersByTimeAsync(1100);
    await expect(promise).resolves.toEqual({ ok: 1 });
    expect(calls).toHaveLength(2);
  });

  it('decides retries by method, status and attempt count', () => {
    expect(shouldRetryRequest({ method: 'get' }, 429, 0)).toBe(true);
    expect(shouldRetryRequest({ method: 'get' }, 500, 0)).toBe(false);
    expect(shouldRetryRequest({ method: 'get' }, 503, 3)).toBe(false);
    expect(shouldRetryRequest({ method: 'post' }, 503, 0)).toBe(false);
    expect(shouldRetryRequest({ method: 'delete' }, 429, 0)).toBe(false);
  });

  it('honours Retry-After, capped', () => {
    expect(retryDelayMs(0, '2')).toBe(2000);
    expect(retryDelayMs(0, '3600')).toBe(8000);
    expect(retryDelayMs(1, undefined)).toBe(2000);
  });
});
