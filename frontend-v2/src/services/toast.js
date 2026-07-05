/**
 * Toast Notification Service
 * Subscribes to 'toast' events on EventBus.
 */
import { eventBus } from '../event-bus.js';

const COLORS = {
  success: 'bg-green-600 border-green-500',
  error: 'bg-red-600 border-red-500',
  warning: 'bg-yellow-600 border-yellow-500',
  info: 'bg-blue-600 border-blue-500',
};

const ICONS = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: '📢',
};

export function showToast(message, type = 'info', duration = 3000) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border ${COLORS[type] || COLORS.info} text-white min-w-[300px] animate-slide-in`;
  toast.innerHTML = `
    <span class="text-xl">${ICONS[type] || ICONS.info}</span>
    <span class="flex-1 font-medium text-sm">${message}</span>
    <button class="text-white/70 hover:text-white">&times;</button>
  `;

  toast.querySelector('button').addEventListener('click', () => toast.remove());
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Auto-subscribe to toast events
eventBus.on('toast', ({ message, type, duration }) => {
  showToast(message, type, duration);
});
