/**
 * Modal Wiring Service
 * Connects OTP and Emergency Stop modals (in index.html shell) 
 * to auth.js service and actions API.
 * Dashboard-native execution. No external messaging dependencies.
 */
import { eventBus } from '../event-bus.js';
import { confirmOtp, closeOtpModal, requestOtp } from './auth.js';
import { emergencyStop } from '../api/actions.js';

// === OTP MODAL WIRING ===

function wireOtpModal() {
  const confirmBtn = document.getElementById('otp-confirm-btn');
  const resendBtn = document.getElementById('otp-resend-btn');
  const cancelBtn = document.getElementById('otp-cancel-btn');
  const otpInput = document.getElementById('otp-input');

  if (confirmBtn) {
    confirmBtn.addEventListener('click', async () => {
      const code = otpInput?.value?.trim() || '';
      await confirmOtp(code);
    });
  }

  if (resendBtn) {
    resendBtn.addEventListener('click', async () => {
      resendBtn.disabled = true;
      resendBtn.textContent = 'Sending...';
      try {
        await requestOtp();
        eventBus.dispatch('toast', { message: 'New OTP code sent', type: 'info' });
      } finally {
        resendBtn.disabled = false;
        resendBtn.textContent = 'Resend';
      }
    });
  }

  if (cancelBtn) {
    cancelBtn.addEventListener('click', closeOtpModal);
  }

  // Allow Enter key to confirm
  if (otpInput) {
    otpInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        confirmBtn?.click();
      }
    });
  }

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const otpModal = document.getElementById('otp-modal');
      if (otpModal && !otpModal.classList.contains('hidden')) {
        closeOtpModal();
      }
      const estopModal = document.getElementById('estop-modal');
      if (estopModal && !estopModal.classList.contains('hidden')) {
        closeEstopModal();
      }
    }
  });
}

// === EMERGENCY STOP MODAL WIRING ===

function closeEstopModal() {
  const modal = document.getElementById('estop-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
  const input = document.getElementById('estop-confirm-input');
  if (input) input.value = '';
  const errEl = document.getElementById('estop-error');
  if (errEl) errEl.style.display = 'none';
}

function openEstopModal() {
  const modal = document.getElementById('estop-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }
  const input = document.getElementById('estop-confirm-input');
  if (input) {
    input.value = '';
    input.focus();
  }
  const errEl = document.getElementById('estop-error');
  if (errEl) errEl.style.display = 'none';
}

async function executeEmergencyStop() {
  const input = document.getElementById('estop-confirm-input');
  const errEl = document.getElementById('estop-error');
  const confirmBtn = document.getElementById('estop-confirm-btn');
  
  const confirmText = input?.value?.trim() || '';
  if (confirmText !== 'STOP') {
    if (errEl) {
      errEl.textContent = 'Type STOP exactly to confirm';
      errEl.style.display = 'block';
    }
    return;
  }

  if (confirmBtn) {
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'EXECUTING...';
  }

  try {
    // Emergency stop uses OTP=000000 as per existing backend convention
    const result = await emergencyStop('000000');
    
    if (result.ok) {
      closeEstopModal();
      eventBus.dispatch('toast', { 
        message: '🚨 EMERGENCY STOP EXECUTED — All positions closed', 
        type: 'error', 
        duration: 8000 
      });
      // Force refresh of positions and grids
      eventBus.dispatch('action:completed', { endpoint: '/emergency-stop', result });
    } else {
      if (errEl) {
        errEl.textContent = result.error || 'Emergency stop failed';
        errEl.style.display = 'block';
      }
    }
  } catch (err) {
    if (errEl) {
      errEl.textContent = `Network error: ${err.message}`;
      errEl.style.display = 'block';
    }
  } finally {
    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.textContent = 'EXECUTE STOP';
    }
  }
}

function wireEstopModal() {
  const confirmBtn = document.getElementById('estop-confirm-btn');
  const cancelBtn = document.getElementById('estop-cancel-btn');
  const confirmInput = document.getElementById('estop-confirm-input');

  if (confirmBtn) {
    confirmBtn.addEventListener('click', executeEmergencyStop);
  }

  if (cancelBtn) {
    cancelBtn.addEventListener('click', closeEstopModal);
  }

  // Allow Enter key in confirm input
  if (confirmInput) {
    confirmInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        confirmBtn?.click();
      }
    });
  }

  // Expose open function globally for settings page E-Stop button
  window.__openEstopModal = openEstopModal;
}

// === ACTION COMPLETION HANDLER ===

function wireActionCompletion() {
  eventBus.on('action:completed', ({ endpoint }) => {
    console.log(`[Modal] Action completed: ${endpoint}`);
    
    // Refresh relevant data based on which action was executed
    if (endpoint.includes('/grid/open') || endpoint.includes('/dca/open')) {
      // Grid/DCA opened — SSE will push updated grids automatically
      eventBus.dispatch('toast', { message: 'Bot created successfully', type: 'success' });
    }
    
    if (endpoint.includes('/order/market') || endpoint.includes('/order/limit')) {
      // Order placed — SSE will push updated positions automatically
      eventBus.dispatch('toast', { message: 'Order submitted successfully', type: 'success' });
    }
    
    if (endpoint.includes('/emergency-stop')) {
      // Positions closed — SSE will push empty positions array
      // Already handled above with specific toast
    }
  });
}

// === INITIALIZATION ===

export function initModals() {
  wireOtpModal();
  wireEstopModal();
  wireActionCompletion();
  console.log('[Modals] OTP + Emergency Stop wired (dashboard-native)');
}
