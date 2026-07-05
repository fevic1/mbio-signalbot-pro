/**
 * Positions Page
 * Live sortable/filterable positions table via sse:positions events.
 * DOM IDs: positions-table, no-positions, pos-asset-filter
 */
import { eventBus } from '../event-bus.js';

const fmtUsd = (v) => '$' + Math.abs(v ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtPnl = (v) => ((v ?? 0) >= 0 ? '+' : '-') + fmtUsd(v);
const pnlClass = (v) => (v ?? 0) > 0 ? 'pnl-positive' : (v ?? 0) < 0 ? 'pnl-negative' : 'pnl-neutral';

let _positionsCache = [];
let _sortCol = 'upnl';
let _sortAsc = false;
let _filterAsset = '';
let _unsubscribers = [];

function renderTable() {
  const tbody = document.getElementById('positions-table');
  const noPos = document.getElementById('no-positions');
  if (!tbody) return;

  let filtered = _positionsCache.slice();
  if (_filterAsset) {
    filtered = filtered.filter(p => p.asset === _filterAsset);
  }

  filtered.sort((a, b) => {
    let va = a[_sortCol], vb = b[_sortCol];
    if (typeof va === 'string') { va = va.toLowerCase(); vb = (vb || '').toLowerCase(); }
    if (va < vb) return _sortAsc ? -1 : 1;
    if (va > vb) return _sortAsc ? 1 : -1;
    return 0;
  });

  if (!filtered.length) {
    tbody.innerHTML = '';
    if (noPos) noPos.style.display = 'block';
    return;
  }
  if (noPos) noPos.style.display = 'none';

  tbody.innerHTML = filtered.map(p => `
    <tr class="border-b border-dark-border/50 hover:bg-dark-hover/30">
      <td class="py-3 px-4 font-medium text-white">${p.asset}</td>
      <td class="py-3 px-4"><span class="badge ${p.side === 'BUY' || p.side === 'Long' ? 'badge-buy' : 'badge-sell'}">${p.side}</span></td>
      <td class="py-3 px-4">${(p.size ?? 0).toFixed(6)}</td>
      <td class="py-3 px-4">$${(p.entry ?? 0).toLocaleString()}</td>
      <td class="py-3 px-4">$${(p.current ?? p.entry ?? 0).toLocaleString()}</td>
      <td class="py-3 px-4 ${pnlClass(p.upnl)}">${fmtPnl(p.upnl)}</td>
      <td class="py-3 px-4 ${pnlClass(p.pnl_pct)}">${(p.pnl_pct ?? 0) >= 0 ? '+' : ''}${(p.pnl_pct ?? 0).toFixed(2)}%</td>
      <td class="py-3 px-4">$${(p.margin_used ?? 0).toFixed(2)}</td>
      <td class="py-3 px-4">$${(p.liquidation_px ?? 0).toLocaleString()}</td>
      <td class="py-3 px-4">${(p.leverage ?? 1)}x</td>
      <td class="py-3 px-4 ${pnlClass(p.roe)}">${(p.roe ?? 0).toFixed(2)}%</td>
      <td class="py-3 px-4">$${(p.sl ?? 0).toLocaleString()}</td>
      <td class="py-3 px-4 text-slate-400">${p.strategy || '-'}</td>
    </tr>
  `).join('');
}

function updateFilterDropdown(positions) {
  const filterEl = document.getElementById('pos-asset-filter');
  if (!filterEl || filterEl.options.length > 1) return;
  const assets = {};
  positions.forEach(p => { assets[p.asset] = true; });
  Object.keys(assets).sort().forEach(a => {
    const opt = document.createElement('option');
    opt.value = a;
    opt.textContent = a;
    filterEl.appendChild(opt);
  });
}

function handleSort(col) {
  if (_sortCol === col) { _sortAsc = !_sortAsc; } else { _sortCol = col; _sortAsc = false; }
  // Update header indicators
  document.querySelectorAll('#positions-table-head th').forEach(th => {
    th.classList.remove('active');
    if (th.dataset.col === col) th.classList.add('active');
  });
  renderTable();
}

export function render(container) {
  container.innerHTML = `
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-white">📈 Open Positions</h1>
      <select id="pos-asset-filter" class="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-2">
        <option value="">All Assets</option>
      </select>
    </div>
    <div class="card !p-0 overflow-x-auto">
      <table class="w-full text-sm">
        <thead id="positions-table-head">
          <tr class="text-slate-500 border-b border-dark-border text-xs uppercase tracking-wider">
            <th class="sortable text-left py-3 px-4" data-col="asset">Asset</th>
            <th class="sortable text-left py-3 px-4" data-col="side">Side</th>
            <th class="sortable text-right py-3 px-4" data-col="size">Size</th>
            <th class="sortable text-right py-3 px-4" data-col="entry">Entry</th>
            <th class="sortable text-right py-3 px-4" data-col="current">Current</th>
            <th class="sortable text-right py-3 px-4 active" data-col="upnl">uPnL</th>
            <th class="sortable text-right py-3 px-4" data-col="pnl_pct">PnL %</th>
            <th class="sortable text-right py-3 px-4" data-col="margin_used">Margin</th>
            <th class="sortable text-right py-3 px-4" data-col="liquidation_px">Liq. Price</th>
            <th class="sortable text-right py-3 px-4" data-col="leverage">Lev.</th>
            <th class="sortable text-right py-3 px-4" data-col="roe">ROE</th>
            <th class="sortable text-right py-3 px-4" data-col="sl">SL</th>
            <th class="text-left py-3 px-4">Strategy</th>
          </tr>
        </thead>
        <tbody id="positions-table">
          <tr><td colspan="13" class="text-center py-8 text-slate-500">Waiting for position data...</td></tr>
        </tbody>
      </table>
      <div id="no-positions" class="hidden text-center py-8 text-slate-500">No open positions</div>
    </div>
  `;

  // Wire sort headers
  container.querySelectorAll('th.sortable').forEach(th => {
    th.addEventListener('click', () => handleSort(th.dataset.col));
  });

  // Wire asset filter
  const filterEl = document.getElementById('pos-asset-filter');
  if (filterEl) {
    filterEl.addEventListener('change', (e) => { _filterAsset = e.target.value; renderTable(); });
  }

  // Subscribe to live position updates
  _unsubscribers.push(eventBus.on('sse:positions', (positions) => {
    _positionsCache = positions || [];
    updateFilterDropdown(_positionsCache);
    renderTable();
  }));
}

export function destroy() {
  _unsubscribers.forEach(u => u());
  _unsubscribers = [];
  _positionsCache = [];
}
