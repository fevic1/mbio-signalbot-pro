/**
 * MBIO SignalBot Pro v2 — Application Entry Point
 * Phase 14 Milestone 5: Navigation + Router + Dashboard
 */
import './styles/main.css';
import { eventBus } from './event-bus.js';
import { connectSSE } from './services/sse.js';
import { loadUser, logout } from './services/auth.js';
import './services/toast.js';
import { initModals } from './services/modal-wiring.js';
import { initSidebar } from './components/sidebar-nav.js';
import { registerRoute, initRouter } from './router.js';

// Import pages
import * as dashboardPage from './pages/dashboard.js';
import * as positionsPage from './pages/positions.js';
import * as ordersPage from './pages/orders.js';
import * as robotsPage from './pages/robots.js';
import * as analyticsPage from './pages/analytics.js';
import * as settingsPage from './pages/settings.js';

console.log('[MBIO v2] Application starting...');

// Register routes
registerRoute('/dashboard', dashboardPage);
registerRoute('/positions', positionsPage);
registerRoute('/orders', ordersPage);
registerRoute('/robots', robotsPage);
registerRoute('/create', robotsPage);
registerRoute('/history', analyticsPage);
registerRoute('/analytics', analyticsPage);
registerRoute('/audit', analyticsPage);
registerRoute('/config', settingsPage);
registerRoute('/safety', settingsPage);
registerRoute('/reconcile', settingsPage);
registerRoute('/sysmon', settingsPage);
registerRoute('/alerts', settingsPage);

// Initialize sidebar
initSidebar();

// Initialize auth
loadUser().then((r) => {
  if (!r.ok) {
    console.warn('[MBIO v2] Not authenticated, redirecting to login');
    window.location.href = '/login';
    return;
  }
  console.log('[MBIO v2] User loaded:', r.data?.email);
});

// Start SSE
connectSSE();

// Wire logout
document.getElementById('logout-btn')?.addEventListener('click', logout);

// Initialize modals (OTP + Emergency Stop)
initModals();

// Initialize router (resolves current URL → renders page)
initRouter();

eventBus.dispatch('app:ready', { version: '2.0.0', milestone: 5 });
console.log('[MBIO v2] ✅ Milestone 3 ready');
