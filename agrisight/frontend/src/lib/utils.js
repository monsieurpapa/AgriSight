// Utility helpers used across the frontend

// Merge class names, skipping falsy values
export function cn(...classValues) {
  return classValues.filter(Boolean).join(' ');
}

// Formatting helpers commonly used in dashboards/regions
export function formatArea(areaKm2) {
  if (areaKm2 == null || isNaN(areaKm2)) return '—';
  const value = Number(areaKm2);
  if (value < 1) return `${(value * 100).toFixed(1)} ha`;
  return `${value.toFixed(1)} km²`;
}

export function formatNumber(value) {
  if (value == null || isNaN(value)) return '—';
  return new Intl.NumberFormat().format(Number(value));
}

export function formatDate(iso, fmt = undefined) {
  // Minimal formatting; pages may pass a label formatter
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '—';
    if (fmt === 'MMM dd') {
      return d.toLocaleDateString(undefined, { month: 'short', day: '2-digit' });
    }
    return d.toLocaleString();
  } catch {
    return '—';
  }
}

export function formatRelativeTime(iso) {
  try {
    const diffMs = Date.now() - new Date(iso).getTime();
    const minutes = Math.round(diffMs / 60000);
    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.round(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.round(hours / 24);
    return `${days}d ago`;
  } catch {
    return '—';
  }
}

export function formatVegetationIndex(value) {
  if (value == null || isNaN(value)) return '—';
  return Number(value).toFixed(2);
}

export function getVegetationIndexLabel(value, type = 'NDVI') {
  const v = Number(value);
  if (isNaN(v)) return `${type}: —`;
  let label = 'Moderate';
  if (v >= 0.6) label = 'Healthy';
  else if (v <= 0.3) label = 'Stressed';
  return `${label}`;
}

export function getVegetationIndexColor(value, type = 'NDVI') {
  const v = Number(value);
  if (isNaN(v)) return '';
  if (v >= 0.6) return 'text-green-600 dark:text-green-400';
  if (v <= 0.3) return 'text-red-600 dark:text-red-400';
  return 'text-yellow-600 dark:text-yellow-400';
}

export function getRiskLevelColor(riskLevel) {
  switch (riskLevel?.toLowerCase()) {
    case 'low':
    case 'healthy':
      return 'text-green-600 dark:text-green-400';
    case 'medium':
    case 'moderate':
      return 'text-yellow-600 dark:text-yellow-400';
    case 'high':
    case 'critical':
    case 'stressed':
      return 'text-red-600 dark:text-red-400';
    default:
      return 'text-gray-600 dark:text-gray-400';
  }
}

// Normalize API/axios errors to a displayable string
export function getErrorMessage(error) {
  if (!error) return 'Unexpected error';

  // Axios-style error normalization
  const response = error.response;
  if (response) {
    const data = response.data;
    if (typeof data === 'string') return data;
    if (data?.detail) return asString(data.detail);
    if (data?.errors) return asString(data.errors);
    if (data?.message) return asString(data.message);
    if (typeof data === 'object') {
      // Collect first field error
      for (const key of Object.keys(data)) {
        const val = data[key];
        if (val) return asString(val);
      }
    }
  }

  if (error.message) return error.message;
  try {
    return JSON.stringify(error);
  } catch {
    return 'An unknown error occurred';
  }
}

function asString(value) {
  if (Array.isArray(value)) return value.map(asString).join(', ');
  if (typeof value === 'object') {
    try { return JSON.stringify(value); } catch { return 'Error'; }
  }
  return String(value);
}


