// Session check retry policy for transient failures (rate limit, server restart, network blip)
export const AUTH_CHECK_RETRY_DELAYS_MS = [1000, 2000];
export const AUTH_CHECK_TIMEOUT_MS = 10000;

export const isTransientAuthError = (error) => {
  if (error?.type === 'NETWORK_ERROR' || error?.type === 'TIMEOUT') return true;
  const status = error?.status ?? error?.response?.status;
  return status === 408 || status === 429 || (typeof status === 'number' && status >= 500);
};
