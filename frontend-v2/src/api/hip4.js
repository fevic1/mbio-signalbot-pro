/**
 * HIP-4 Market Spec API
 * Wraps /api/hip4/* and /api/hyperliquid/* endpoints.
 */
import { get } from './client.js';

export function getMarketSpec(asset) {
  return get(`/hip4/specs?asset=${encodeURIComponent(asset)}`);
}

export function getAssets(type) {
  const qs = type ? `?type=${encodeURIComponent(type)}` : '';
  return get(`/hyperliquid/assets${qs}`);
}

export function getPrice(asset) {
  return get(`/hip4/price?asset=${encodeURIComponent(asset)}`);
}

export function validateOrder(asset, price, size) {
  return get(`/hip4/validate?asset=${encodeURIComponent(asset)}&price=${price}&size=${size}`);
}

export function getUnifiedPositions() {
  return get('/hyperliquid/positions');
}
