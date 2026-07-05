/**
 * Centralized API Client
 * All fetch calls go through this module.
 * Handles: credentials, JSON serialization, error extraction, typing.
 */

const BASE = '';  // Backend routes have no /api/dashboard prefix

export async function request(path, options = {}) {
  const url = path.startsWith('http') ? path : `${BASE}${path}`;
  const config = {
    credentials: 'include',
    ...options,
  };

  if (config.body && typeof config.body === 'object') {
    config.headers = { 'Content-Type': 'application/json', ...(config.headers || {}) };
    config.body = JSON.stringify(config.body);
  }

  try {
    const resp = await fetch(url, config);
    let data = null;
    try { data = await resp.json(); } catch (_) { /* non-JSON response */ }
    return {
      ok: resp.ok,
      status: resp.status,
      data,
      error: (!resp.ok && data?.detail) ? data.detail : null,
    };
  } catch (err) {
    return { ok: false, status: 0, data: null, error: `Network error: ${err.message}` };
  }
}

export function get(path) {
  return request(path, { method: 'GET' });
}

export function post(path, body) {
  return request(path, { method: 'POST', body });
}
