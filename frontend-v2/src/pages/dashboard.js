/**
 * Dashboard Page
 * Subscribes to sse:overview events for live metric updates.
 * Includes: Metric cards, TradingView chart, System Health, Recent Trades.
 */
import { eventBus } from '../event-bus.js';
import { initChart, destroyChart, updateChart } from '../services/chart.js';
import { getHealth, getTradeHistory } from '../api/dashboard.js';

// Formatting utilities (local to dashboard, no global pollution)
const fmtUsd = (v) => '$' + Math.abs(v ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtPnl = (v) => ((v ?? 0) >= 0 ? '+' : '-') + fmtUsd(v);
const pnlClass = (v) => (v ?? 0) > 0 ? 'pnl-positive' : (v ?? 0) < 0 ? 'pnl-negative' : 'pnl-neutral';

let _unsubscribers = [];

function renderMetrics() {
  return `
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
      <div class="card"><div class="metric-label mb-1">Balance</div><div id="dash-balance" class="metric-value text-white">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Equity</div><div id="dash-equity" class="metric-value text-white">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Deployed</div><div id="dash-deployed" class="metric-value text-white">0%</div></div>
      <div class="card"><div class="metric-label mb-1">Daily PnL</div><div id="dash-daily-pnl" class="metric-value pnl-neutral">0.00%</div></div>
      <div class="card"><div class="metric-label mb-1">Realized PnL</div><div id="dash-realized" class="text-xl font-bold pnl-neutral">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Unrealized PnL</div><div id="dash-unrealized" class="text-xl font-bold pnl-neutral">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Win Rate</div><div id="dash-winrate" class="text-xl font-bold text-white">N/A</div></div>
    </div>`;
}

function renderChart() {
  return `
    <div class="card !p-0 mb-6" style="min-height: 500px;">
      <div class="flex items-center justify-between px-4 py-3 border-b border-dark-border">
        <h3 class="text-lg font-bold text-white">📈 Market Chart</h3>
        <select id="tv-pair-selector" class="bg-slate-800 border border-slate-700 text-white text-sm rounded px-3 py-1">
          <option value="BINANCE:BTCUSDT">BTC/USDT</option>
          <option value="BINANCE:ETHUSDT">ETH/USDT</option>
          <option value="BINANCE:SOLUSDT">SOL/USDT</option>
          <option value="BINANCE:XRPUSDT">XRP/USDT</option>
          <option value="BINANCE:AVAXUSDT">AVAX/USDT</option>
          <option value="BINANCE:LINKUSDT">LINK/USDT</option>
          <option value="BINANCE:DOGEUSDT">DOGE/USDT</option>
          <option value="BINANCE:HYPEUSDT">HYPE/USDT</option>
        </select>
      </div>
      <div id="tv-chart-container" style="width:100%; height:480px;">
        <div class="flex items-center justify-center h-full text-slate-500 text-sm" id="tv-loading-msg">Loading chart...</div>
      </div>
    </div>`;
}

function renderHealthAndTrades() {
  return `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="card">
        <div class="metric-label mb-3">System Health</div>
        <div id="dash-health-checks" class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div class="text-slate-500">Loading...</div>
        </div>
      </div>
      <div class="card">
        <div class="flex items-center justify-between mb-3">
          <div class="metric-label">Recent Trades</div>
          <button id="dash-export-csv" class="btn btn-primary text-xs py-1 px-3">Export CSV</button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead><tr class="text-slate-500 border-b border-dark-border">
              <th class="text-left py-2">Time</th>
              <th class="text-left py-2">Asset</th>
              <th class="text-left py-2">Side</th>
              <th class="text-right py-2">PnL</th>
            </tr></thead>
            <tbody id="dash-recent-trades">
              <tr><td colspan="4" class="text-center py-4 text-slate-500">Loading...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>`;
}

function updateMetrics(data) {
  const set = (id, text, cls) => {
    const el = document.getElementById(id);
    if (el) { el.textContent = text; if (cls) el.className = cls; }
  };

  set('dash-balance', fmtUsd(data.balance));
  set('dash-equity', fmtUsd(data.equity));
  set('dash-deployed', `${data.deployed_pct ?? 0}%`);
  
  const dpEl = document.getElementById('dash-daily-pnl');
  if (dpEl) {
    dpEl.textContent = `${(data.daily_pnl_pct ?? 0) >= 0 ? '+' : ''}${(data.daily_pnl_pct ?? 0).toFixed(2)}%`;
    dpEl.className = `metric-value ${pnlClass(data.daily_pnl_pct)}`;
  }

  set('dash-realized', fmtPnl(data.realized_pnl_usd), `text-xl font-bold ${pnlClass(data.realized_pnl_usd)}`);
  set('dash-unrealized', fmtPnl(data.unrealized_pnl_usd), `text-xl font-bold ${pnlClass(data.unrealized_pnl_usd)}`);
  set('dash-winrate', data.win_rate || 'N/A', 'text-xl font-bold text-white');
}

async function loadHealth() {
  const result = await getHealth();
  const el = document.getElementById('dash-health-checks');
  if (!el || !result.ok) return;
  
  const checks = result.data?.checks || {};
  el.innerHTML = Object.entries(checks).map(([k, v]) => 
    `<div class="flex items-center gap-2">${v ? '✅' : '❌'} <span class="${v ? 'text-green-400' : 'text-red-400'}">${k.replace(/_/g, ' ')}</span></div>`
  ).join('');
}

async function loadRecentTrades() {
  const result = await getTradeHistory(10);
  const tbody = document.getElementById('dash-recent-trades');
  if (!tbody || !result.ok) return;

  const trades = result.data?.trades || [];
  if (!trades.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-slate-500">No recent trades</td></tr>';
    return;
  }

  tbody.innerHTML = trades.map(t => {
    const time = (t.closed_at || t.opened_at || '').substring(11, 19);
    const pc = (t.pnl ?? 0) >= 0 ? 'text-green-400' : 'text-red-400';
    return `<tr class="border-b border-dark-border/50">
      <td class="py-2 text-slate-400">${time}</td>
      <td class="py-2 font-medium">${t.asset}</td>
      <td class="py-2"><span class="badge ${t.side === 'BUY' ? 'badge-buy' : 'badge-sell'}">${t.side}</span></td>
      <td class="py-2 text-right ${pc}">${fmtPnl(t.pnl)}</td>
    </tr>`;
  }).join('');
}

export function render(container) {
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-white">Dashboard Overview</h1>
    </div>
    ${renderMetrics()}
    ${renderChart()}
    ${renderHealthAndTrades()}
  `;

  // Wire chart pair selector
  const selector = document.getElementById('tv-pair-selector');
  if (selector) {
    selector.addEventListener('change', (e) => updateChart(e.target.value));
  }

  // Initialize chart after DOM is ready
  setTimeout(() => initChart(selector?.value || 'BINANCE:BTCUSDT'), 200);

  // Load one-shot data
  loadHealth();
  loadRecentTrades();

  // Subscribe to live SSE updates
  _unsubscribers.push(eventBus.on('sse:overview', updateMetrics));
}

export function destroy() {
  _unsubscribers.forEach(unsub => unsub());
  _unsubscribers = [];
  destroyChart();
}
