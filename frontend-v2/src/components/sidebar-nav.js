/**
 * Sidebar Navigation Component
 * Implements HTML xxxx.md button pattern with EventBus-driven active state.
 * Categories: Main, Trading, Analytics, System
 */
import { eventBus } from '../event-bus.js';
import { navigateTo } from '../router.js';

const NAV_ITEMS = [
  { category: null, label: '📊 Dashboard', path: '/dashboard', icon: '' },
  { category: 'Trading', label: '📈 Positions', path: '/positions', icon: '' },
  { category: null, label: '📝 Order Desk', path: '/orders', icon: '' },
  { category: null, label: '🔲 Grid Bots', path: '/robots', icon: '' },
  { category: null, label: '➕ Create Bot', path: '/create', icon: '' },
  { category: 'Analytics', label: '📜 Trade History', path: '/history', icon: '' },
  { category: null, label: '📉 Performance', path: '/analytics', icon: '' },
  { category: null, label: '📋 Audit Log', path: '/audit', icon: '' },
  { category: 'System', label: '⚙ Config', path: '/config', icon: '' },
  { category: null, label: '🛡 Safety', path: '/safety', icon: '' },
  { category: null, label: '🔧 Reconcile', path: '/reconcile', icon: '' },
  { category: null, label: '🖥 System', path: '/sysmon', icon: '' },
  { category: null, label: '🔔 Alerts', path: '/alerts', icon: '' },
];

// Map paths to their parent route for sidebar highlighting
const PATH_TO_PARENT = {
  '/dashboard': '/dashboard',
  '/positions': '/positions',
  '/orders': '/orders',
  '/robots': '/robots',
  '/create': '/robots',
  '/history': '/history',
  '/analytics': '/analytics',
  '/audit': '/audit',
  '/config': '/config',
  '/safety': '/config',
  '/reconcile': '/config',
  '/sysmon': '/config',
  '/alerts': '/config',
};

let _activePath = '/dashboard';

function renderNav() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  let html = `
    <div class="p-4 border-b border-dark-border">
      <div class="text-xl font-bold text-white flex items-center gap-2">🤖 MBIO</div>
      <div class="mt-3 space-y-1">
        <div class="flex items-center justify-between mb-2">
          <span class="metric-label">Equity</span>
          <span id="sidebar-equity" class="text-white font-semibold">$0.00</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="metric-label">Today P/L</span>
          <span id="sidebar-pnl" class="pnl-neutral font-semibold">$0.00</span>
        </div>
        <div class="flex items-center gap-2 mt-3 pt-2 border-t border-slate-700">
          <span id="connection-status" class="status-dot disconnected"></span>
          <span id="connection-text" class="text-xs text-slate-400">Connecting...</span>
        </div>
      </div>
    </div>
    <nav class="flex flex-col gap-1 w-full px-2 mt-4 flex-1 overflow-y-auto">
  `;

  let lastCategory = undefined;
  for (const item of NAV_ITEMS) {
    if (item.category && item.category !== lastCategory) {
      html += `<div class="text-[10px] text-slate-500 font-bold uppercase px-3 py-2 mt-2">${item.category}</div>`;
      lastCategory = item.category;
    }
    const isActive = PATH_TO_PARENT[item.path] === PATH_TO_PARENT[_activePath];
    const activeClass = isActive ? 'bg-[#1e232f] text-[#5d3ef2]' : '';
    html += `<button data-path="${item.path}" class="nav-item p-2 w-full text-left rounded hover:bg-[#1e232f] transition-colors ${activeClass}">${item.label}</button>`;
  }

  html += '</nav>';
  sidebar.innerHTML = html;

  // Attach click handlers
  sidebar.querySelectorAll('button[data-path]').forEach(btn => {
    btn.addEventListener('click', () => {
      navigateTo(btn.dataset.path);
    });
  });
}

function updateActiveState(path) {
  _activePath = path;
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  sidebar.querySelectorAll('button[data-path]').forEach(btn => {
    const btnParent = PATH_TO_PARENT[btn.dataset.path];
    const currentParent = PATH_TO_PARENT[path];
    if (btnParent === currentParent) {
      btn.classList.add('bg-[#1e232f]', 'text-[#5d3ef2]');
    } else {
      btn.classList.remove('bg-[#1e232f]', 'text-[#5d3ef2]');
    }
  });
}

// Subscribe to navigation events
eventBus.on('nav:change', ({ path }) => updateActiveState(path));

// Subscribe to SSE overview for sidebar equity/PnL updates
eventBus.on('sse:overview', (data) => {
  const fmtUsd = (v) => '$' + Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const pnlClass = (v) => v > 0 ? 'pnl-positive' : v < 0 ? 'pnl-negative' : 'pnl-neutral';
  const fmtPnl = (v) => (v >= 0 ? '+' : '-') + fmtUsd(v);

  const eqEl = document.getElementById('sidebar-equity');
  const pnlEl = document.getElementById('sidebar-pnl');
  if (eqEl) eqEl.textContent = fmtUsd(data.equity ?? 0);
  if (pnlEl) {
    const pnl = data.unrealized_pnl_usd ?? 0;
    pnlEl.textContent = fmtPnl(pnl);
    pnlEl.className = `font-semibold ${pnlClass(pnl)}`;
  }
});

export function initSidebar() {
  renderNav();
}
