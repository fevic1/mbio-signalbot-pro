/**
 * Dashboard Data API
 * Wraps /api/dashboard/* read endpoints.
 */
import { get } from './client.js';

export function getOverview() {
  return get('/overview');
}

export function getHealth() {
  return get('/health');
}

export function getAnalytics() {
  return get('/analytics');
}

export function getTradeHistory(limit = 100) {
  return get(`/trade-history?limit=${limit}`);
}

export function getSystemStatus() {
  return get('/system/status');
}

export function getConfigCurrent() {
  return get('/config/current');
}

export function getConfigDefaults() {
  return get('/config/defaults');
}

export function getConfigAssets() {
  return get('/config/assets');
}

export function getOrphanedSignals() {
  return get('/signals/orphaned');
}

export function getAlertConfig() {
  return get('/alerts/config');
}

export function getAuditLog(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return get(`/audit-log${qs ? '?' + qs : ''}`);
}
