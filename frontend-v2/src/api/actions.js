/**
 * Trading Actions API
 * All write operations require OTP verification.
 * OTP flow is handled by auth.js — these functions accept otp as parameter.
 */
import { post } from './client.js';

export function openDca(params, otp) {
  return post('/dca/open', { ...params, otp });
}

export function openGrid(params, otp) {
  return post('/grid/open', { ...params, otp });
}

export function submitMarketOrder(params, otp) {
  return post('/order/market', { ...params, otp });
}

export function submitLimitOrder(params, otp) {
  return post('/order/limit', { ...params, otp });
}

export function emergencyStop(otp) {
  return post('/emergency-stop', { otp });
}

export function saveAlertConfig(config) {
  return post('/alerts/config', config);
}
