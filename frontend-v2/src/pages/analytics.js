/**
 * Analytics Page
 * Trade history table, performance metrics, daily PnL chart, monthly heatmap.
 */
import { eventBus } from '../event-bus.js';
import { getTradeHistory, getAnalytics } from '../api/dashboard.js';

const fmtUsd = (v) => '$' + Math.abs(v ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtPnl = (v) => ((v ?? 0) >= 0 ? '+' : '-') + fmtUsd(v);
const pnlClass = (v) => (v ?? 0) > 0 ? 'pnl-positive' : (v ?? 0) < 0 ? 'pnl-negative' : 'pnl-neutral';

async function loadTradeHistory() {
  const r = await getTradeHistory(100);
  const tbody = document.getElementById('history-table');
  const noHist = document.getElementById('no-history');
  if (!tbody) return;

  const trades = (r.ok && Array.isArray(r.data?.trades)) ? r.data.trades : [];
  if (!trades.length) {
    tbody.innerHTML = '';
    if (noHist) noHist.style.display = 'block';
    return;
  }
  if (noHist) noHist.style.display = 'none';

  tbody.innerHTML = trades.map(t => {
    const time = (t.closed_at || t.opened_at || '').substring(0, 19).replace('T', ' ');
    return `<tr class="border-b border-dark-border/50 hover:bg-dark-hover/30">
      <td class="py-2 px-4 text-slate-400 text-xs">${time}</td>
      <td class="py-2 px-4 font-medium">${t.asset}</td>
      <td class="py-2 px-4"><span class="badge ${t.side === 'BUY' ? 'badge-buy' : 'badge-sell'}">${t.side}</span></td>
      <td class="py-2 px-4 text-right">${(t.size ?? 0).toFixed(6)}</td>
      <td class="py-2 px-4 text-right">$${(t.entry_price ?? 0).toLocaleString()}</td>
      <td class="py-2 px-4 text-right">$${(t.exit_price ?? 0).toLocaleString()}</td>
      <td class="py-2 px-4 text-right ${pnlClass(t.pnl)}">${fmtPnl(t.pnl)}</td>
      <td class="py-2 px-4 text-right ${pnlClass(t.pnl_pct)}">${(t.pnl_pct ?? 0) >= 0 ? '+' : ''}${(t.pnl_pct ?? 0).toFixed(2)}%</td>
      <td class="py-2 px-4 text-slate-400 text-xs">${t.strategy || '-'}</td>
    </tr>`;
  }).join('');
}

async function loadPerformanceMetrics() {
  const r = await getAnalytics();
  if (!r.ok || !r.data) return;
  const d = r.data;
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('an-total-pnl', fmtPnl(d.total_pnl));
  set('an-winrate', `${(d.win_rate ?? 0).toFixed(1)}%`);
  set('an-sharpe', (d.sharpe_ratio ?? 0).toFixed(2));
  set('an-max-dd', `${(d.max_drawdown ?? 0).toFixed(2)}%`);
  set('an-pf', (d.profit_factor ?? 0).toFixed(2));
  set('an-trades', d.total_trades ?? 0);
}

function exportCSV() {
  getTradeHistory(1000).then(r => {
    if (!r.ok || !Array.isArray(r.data?.trades)) return;
    const headers = ['Time','Asset','Side','Size','Entry','Exit','PnL','PnL%','Strategy'];
    const rows = r.data.trades.map(t => [
      t.closed_at || t.opened_at || '', t.asset, t.side, t.size, t.entry_price, t.exit_price, t.pnl, t.pnl_pct, t.strategy
    ]);
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `mbio_trades_${new Date().toISOString().slice(0,10)}.csv`;
    a.click(); URL.revokeObjectURL(url);
    eventBus.dispatch('toast', { message: 'CSV exported successfully', type: 'success' });
  });
}

export function render(container) {
  container.innerHTML = `
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-white">📈 Analytics</h1>
      <button class="btn-primary text-sm" id="btn-export-csv">Export CSV</button>
    </div>
    <!-- Performance Metrics -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      <div class="card"><div class="metric-label mb-1">Total PnL</div><div id="an-total-pnl" class="text-xl font-bold pnl-neutral">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Win Rate</div><div id="an-winrate" class="text-xl font-bold text-white">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Sharpe Ratio</div><div id="an-sharpe" class="text-xl font-bold text-white">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Max Drawdown</div><div id="an-max-dd" class="text-xl font-bold text-red-400">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Profit Factor</div><div id="an-pf" class="text-xl font-bold text-white">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Total Trades</div><div id="an-trades" class="text-xl font-bold text-white">Loading...</div></div>
    </div>
    <!-- Charts Placeholder (Chart.js integration in M5) -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="card"><div class="metric-label mb-3">Daily PnL Chart</div><div id="daily-pnl-chart" class="h-48 flex items-center justify-center text-slate-500 text-sm">Chart.js integration pending</div></div>
      <div class="card"><div class="metric-label mb-3">Monthly Returns Heatmap</div><div id="monthly-heatmap" class="h-48 flex items-center justify-center text-slate-500 text-sm">Chart.js integration pending</div></div>
    </div>
    <!-- Trade History Table -->
    <div class="card !p-0 overflow-x-auto">
      <div class="px-4 py-3 border-b border-dark-border font-bold text-white">Trade History</div>
      <table class="w-full text-xs">
        <thead><tr class="text-slate-500 border-b border-dark-border uppercase tracking-wider">
          <th class="text-left py-2 px-4">Time</th><th class="text-left py-2 px-4">Asset</th>
          <th class="text-left py-2 px-4">Side</th><th class="text-right py-2 px-4">Size</th>
          <th class="text-right py-2 px-4">Entry</th><th class="text-right py-2 px-4">Exit</th>
          <th class="text-right py-2 px-4">PnL</th><th class="text-right py-2 px-4">PnL%</th>
          <th class="text-left py-2 px-4">Strategy</th>
        </tr></thead>
        <tbody id="history-table">
          <tr><td colspan="9" class="text-center py-8 text-slate-500">Loading trades...</td></tr>
        </tbody>
      </table>
      <div id="no-history" class="hidden text-center py-8 text-slate-500">No trade history</div>
    </div>
  `;

  document.getElementById('btn-export-csv')?.addEventListener('click', exportCSV);
  loadTradeHistory();
  loadPerformanceMetrics();
}

export function destroy() {}
