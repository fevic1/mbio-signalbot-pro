/**
 * Authentication Service
 * Manages session state, OTP flow, and logout.
 * Dashboard-native authentication. No external messaging dependencies.
 */
import { post, get } from '../api/client.js';
import { eventBus } from '../event-bus.js';

let _currentUser = null;
let _pendingAction = null;

export async function loadUser() {
  const result = await get('/auth/me');
  if (result.ok && result.data) {
    _currentUser = result.data;
    const nameEl = document.getElementById('user-name');
    const roleEl = document.getElementById('user-role');
    if (nameEl) nameEl.textContent = result.data.name || result.data.email || 'User';
    if (roleEl) roleEl.textContent = (result.data.role || 'USER').toUpperCase();
    eventBus.dispatch('auth:user-loaded', result.data);
  }
  return result;
}

export function getCurrentUser() {
  return _currentUser;
}

export async function logout() {
  await post('/auth/logout', {});
  _currentUser = null;
  window.location.href = '/login';
}

// === OTP Flow (Dashboard-Native) ===

export function setPendingAction(endpoint, payload, description) {
  _pendingAction = { endpoint, payload, description };
  document.getElementById('otp-description').textContent = description;
  document.getElementById('otp-input').value = '';
  document.getElementById('otp-error').style.display = 'none';
  document.getElementById('otp-modal').classList.remove('hidden');
  document.getElementById('otp-modal').classList.add('flex');
  document.getElementById('otp-input').focus();
}

export function closeOtpModal() {
  _pendingAction = null;
  document.getElementById('otp-modal').classList.add('hidden');
  document.getElementById('otp-modal').classList.remove('flex');
}

export async function requestOtp() {
  const result = await post('/auth/otp/request', {});
  if (!result.ok) {
    eventBus.dispatch('toast', { message: result.error || 'Failed to send OTP', type: 'error' });
  }
  return result;
}

export async function confirmOtp(otpCode) {
  if (!_pendingAction) return { ok: false, error: 'No pending action' };
  if (!otpCode || otpCode.length !== 6) {
    return { ok: false, error: 'Enter 6-digit OTP' };
  }

  const confirmBtn = document.getElementById('otp-confirm-btn');
  if (confirmBtn) { confirmBtn.disabled = true; confirmBtn.textContent = 'Executing...'; }

  try {
    const result = await post(_pendingAction.endpoint, {
      ..._pendingAction.payload,
      otp: otpCode,
    });

    if (result.ok) {
      closeOtpModal();
      eventBus.dispatch('toast', { message: result.data?.message || 'Action completed', type: 'success' });
      eventBus.dispatch('action:completed', { endpoint: _pendingAction.endpoint, result });
    } else {
      const errEl = document.getElementById('otp-error');
      if (errEl) { errEl.textContent = result.error || 'Action failed'; errEl.style.display = 'block'; }
    }
    return result;
  } finally {
    if (confirmBtn) { confirmBtn.disabled = false; confirmBtn.textContent = 'Confirm'; }
  }
}

export function getPendingAction() {
  return _pendingAction;
}
