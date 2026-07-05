/**
 * Settings Page
 * Multi-tab settings: Config, Safety, Reconcile, System Monitor, Audit Log, Alerts.
 * All tabs loaded on demand via API modules.
 */
import { eventBus } from '../event-bus.js';
import { getCurrentConfig, getHealth, getSystemStatus, getOrphanedSignals, getAuditLog, getAlertConfig } from '../api/dashboard.js';
// Emergency stop handled by modal-wiring.js

let _activeTab = 'config';

function showSettingsTab(tab, btnEl) {
  _activeTab = tab;
  ['config', 'safety', 'reconcile', 'sysmon', 'audit', 'alerts'].forEach(t => {
    const el = document.getElementById(`settings-${t}`);
    if (el) el.style.display = t === tab ? 'block' : 'none';
  });
  document.querySelectorAll('.settings-tab-btn').forEach(b => {
    b.classList.remove('bg-accent-primary', 'text-white');
    b.classList.add('bg-slate-800', 'text-slate-400');
  });
  if (btnEl) {
    btnEl.classList.remove('bg-slate-800', 'text-slate-400');
    btnEl.classList.add('bg-accent-primary', 'text-white');
  }
  // Load tab-specific data
  if (tab === 'config') loadConfig();
  if (tab === 'safety') loadSafety();
  if (tab === 'reconcile') loadReconcile();
  if (tab === 'sysmon') loadSysMon();
  if (tab === 'audit') loadAudit();
  if (tab === 'alerts') loadAlerts();
}

async function loadConfig() {
  const r = await getCurrentConfig();
  const el = document.getElementById('cfg-content');
  if (!el) return;
  if (!r.ok) { el.innerHTML = '<div class="text-red-400">Failed to load config</div>'; return; }
  const cfg = r.data || {};
  el.innerHTML = `<pre class="text-xs text-slate-300 overflow-auto max-h-[500px] p-4 bg-slate-900 rounded-lg">${JSON.stringify(cfg, null, 2)}</pre>`;
}

async function loadSafety() {
  const r = await getHealth();
  const el = document.getElementById('safe-content');
  if (!el) return;
  if (!r.ok) { el.innerHTML = '<div class="text-red-400">Failed to load safety data</div>'; return; }
  const checks = r.data?.checks || {};
  el.innerHTML = `
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      ${Object.entries(checks).map(([k, v]) => `
        <div class="card text-center">
          <div class="text-2xl mb-1">${v ? '✅' : '❌'}</div>
          <div class="text-sm ${v ? 'text-green-400' : 'text-red-400'}">${k.replace(/_/g, ' ')}</div>
        </div>
      `).join('')}
    </div>
    <div class="card border-red-800">
      <h3 class="text-lg font-bold text-red-400 mb-3">⚠️ Emergency Stop</h3>
      <p class="text-sm text-slate-400 mb-4">Close ALL positions and cancel ALL pending orders immediately.</p>
      <button id="btn-emergency-stop" class="btn-danger w-full">EXECUTE EMERGENCY STOP</button>
    </div>
  `;
  document.getElementById('btn-emergency-stop')?.addEventListener('click', () => {
    if (typeof window.__openEstopModal === 'function') {
      window.__openEstopModal();
    } else {
      eventBus.dispatch('toast', { message: 'Emergency stop modal not available', type: 'error' });
    }
  });
}

async function loadReconcile() {
  const r = await getOrphanedSignals();
  const tbody = document.getElementById('orphan-table');
  const noOrph = document.getElementById('no-orphans');
  if (!tbody) return;
  const signals = (r.ok && Array.isArray(r.data)) ? r.data : [];
  if (!signals.length) {
    tbody.innerHTML = '';
    if (noOrph) noOrph.style.display = 'block';
    return;
  }
  if (noOrph) noOrph.style.display = 'none';
  tbody.innerHTML = signals.map(s => `
    <tr class="border-b border-dark-border/50">
      <td class="py-2 px-4 text-xs text-slate-400">${(s.timestamp || '').substring(0, 19)}</td>
      <td class="py-2 px-4 font-medium">${s.asset || '-'}</td>
      <td class="py-2 px-4">${s.signal_type || '-'}</td>
      <td class="py-2 px-4 text-xs text-slate-400">${s.reason || '-'}</td>
    </tr>
  `).join('');
}

async function loadSysMon() {
  const r = await getSystemStatus();
  const el = document.getElementById('sysmon-content');
  if (!el) return;
  if (!r.ok) { el.innerHTML = '<div class="text-red-400">Failed to load system status</div>'; return; }
  const d = r.data || {};
  el.innerHTML = `
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
      <div class="card"><div class="metric-label">Status</div><div class="text-lg font-bold ${d.healthy ? 'text-green-400' : 'text-red-400'}">${d.healthy ? 'HEALTHY' : 'DEGRADED'}</div></div>
      <div class="card"><div class="metric-label">Uptime</div><div class="text-lg font-bold text-white">${d.uptime || 'N/A'}</div></div>
      <div class="card"><div class="metric-label">Auto Trading</div><div class="text-lg font-bold ${d.auto_trade ? 'text-green-400' : 'text-yellow-400'}">${d.auto_trade ? 'ENABLED' : 'DISABLED'}</div></div>
    </div>
  `;
}

async function loadAudit() {
  const r = await getAuditLog({ limit: 50 });
  const tbody = document.getElementById('audit-table');
  if (!tbody) return;
  const logs = (r.ok && Array.isArray(r.data?.logs)) ? r.data.logs : [];
  tbody.innerHTML = logs.length ? logs.map(l => `
    <tr class="border-b border-dark-border/50">
      <td class="py-2 px-4 text-xs text-slate-400">${(l.timestamp || '').substring(0, 19)}</td>
      <td class="py-2 px-4 font-medium">${l.action || '-'}</td>
      <td class="py-2 px-4 text-xs">${l.user || '-'}</td>
      <td class="py-2 px-4 text-xs text-slate-400">${l.details || '-'}</td>
    </tr>
  `).join('') : '<tr><td colspan="4" class="text-center py-4 text-slate-500">No audit entries</td></tr>';
}

async function loadAlerts() {
  const r = await getAlertConfig();
  const el = document.getElementById('alerts-content');
  if (!el) return;
  if (!r.ok) { el.innerHTML = '<div class="text-red-400">Failed to load alert config</div>'; return; }
  el.innerHTML = `<pre class="text-xs text-slate-300 overflow-auto max-h-[400px] p-4 bg-slate-900 rounded-lg">${JSON.stringify(r.data, null, 2)}</pre>`;
}

export function render(container) {
  container.innerHTML = `
    <div class="mb-6"><h1 class="text-2xl font-bold text-white">⚙️ Settings</h1></div>
    <!-- Tab Buttons -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-accent-primary text-white" onclick="window.__showSettingsTab('config', this)">Config</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('safety', this)">Safety</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('reconcile', this)">Reconcile</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('sysmon', this)">System</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('audit', this)">Audit Log</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('alerts', this)">Alerts</button>
    </div>
    <!-- Tab Content -->
    <div id="settings-config"><div id="cfg-content" class="card">Loading config...</div></div>
    <div id="settings-safety" style="display:none;"><div id="safe-content" class="card">Loading safety...</div></div>
    <div id="settings-reconcile" style="display:none;">
      <div class="card !p-0 overflow-x-auto">
        <div class="px-4 py-3 border-b border-dark-border font-bold text-white">Orphaned Signals</div>
        <table class="w-full text-xs"><thead><tr class="text-slate-500 border-b border-dark-border"><th class="text-left py-2 px-4">Time</th><th class="text-left py-2 px-4">Asset</th><th class="text-left py-2 px-4">Type</th><th class="text-left py-2 px-4">Reason</th></tr></thead>
        <tbody id="orphan-table"><tr><td colspan="4" class="text-center py-4 text-slate-500">Loading...</td></tr></tbody></table>
        <div id="no-orphans" class="hidden text-center py-4 text-slate-500">No orphaned signals</div>
      </div>
    </div>
    <div id="settings-sysmon" style="display:none;"><div id="sysmon-content" class="card">Loading system status...</div></div>
    <div id="settings-audit" style="display:none;">
      <div class="card !p-0 overflow-x-auto">
        <div class="px-4 py-3 border-b border-dark-border font-bold text-white">Audit Log</div>
        <table class="w-full text-xs"><thead><tr class="text-slate-500 border-b border-dark-border"><th class="text-left py-2 px-4">Time</th><th class="text-left py-2 px-4">Action</th><th class="text-left py-2 px-4">User</th><th class="text-left py-2 px-4">Details</th></tr></thead>
        <tbody id="audit-table"><tr><td colspan="4" class="text-center py-4 text-slate-500">Loading...</td></tr></tbody></table>
      </div>
    </div>
    <div id="settings-alerts" style="display:none;"><div id="alerts-content" class="card">Loading alerts...</div></div>
  `;

  window.__showSettingsTab = showSettingsTab;
  loadConfig(); // Default tab
}

export function destroy() {
  window.__showSettingsTab = null;
}
