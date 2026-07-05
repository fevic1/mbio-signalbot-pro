/**
 * Robots Page
 * Grid bot cards, DCA/Grid creation forms, Canvas visualizer.
 * Live updates via sse:grids and sse:positions events.
 */
import { eventBus } from '../event-bus.js';
import { setPendingAction } from '../services/auth.js';
import { getConfigAssets } from '../api/dashboard.js';
import { getPrice } from '../api/hip4.js';

const fmtUsd = (v) => '$' + Math.abs(v ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtPnl = (v) => ((v ?? 0) >= 0 ? '+' : '-') + fmtUsd(v);
const pnlClass = (v) => (v ?? 0) > 0 ? 'pnl-positive' : (v ?? 0) < 0 ? 'pnl-negative' : 'pnl-neutral';

let _gridsCache = [];
let _positionsCache = [];
let _unsubscribers = [];

function renderBotCards(grids) {
  const c = document.getElementById('grids-container');
  const ng = document.getElementById('no-grids');
  if (!c) return;

  if (!grids.length) {
    c.innerHTML = '';
    if (ng) ng.style.display = 'block';
    return;
  }
  if (ng) ng.style.display = 'none';

  c.innerHTML = grids.map(g => `
    <div class="card">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <span class="badge badge-grid">GRID</span>
          <span class="text-lg font-bold text-white">${g.asset}</span>
        </div>
        <span class="text-xs text-slate-400">${g.mode || 'RANGE'}</span>
      </div>
      <div class="grid grid-cols-2 gap-3 text-sm">
        <div><span class="metric-label">Range</span><br>$${(g.lower_price ?? 0).toLocaleString()} - $${(g.upper_price ?? 0).toLocaleString()}</div>
        <div><span class="metric-label">Nodes</span><br>${g.nodes_active ?? 0}/${g.nodes_total ?? 0}</div>
        <div><span class="metric-label">Cycles</span><br>${g.cycles ?? 0}</div>
        <div><span class="metric-label">PnL</span><br><span class="${pnlClass(g.realized_pnl)}">${fmtPnl(g.realized_pnl)}</span></div>
      </div>
    </div>
  `).join('');
}

function showCreateForm(type) {
  document.getElementById('grid-form')?.style.setProperty('display', type === 'grid' ? 'block' : 'none');
  document.getElementById('dca-form')?.style.setProperty('display', type === 'dca' ? 'block' : 'none');
}

async function autoFillGridForm() {
  const asset = document.getElementById('grid-asset')?.value;
  if (!asset) return;
  try {
    const r = await getPrice(asset);
    if (r.ok && r.data?.price) {
      const mid = r.data.price;
      const range = mid * 0.05;
      const lp = document.getElementById('grid-lower');
      const up = document.getElementById('grid-upper');
      if (lp) lp.value = (mid - range).toFixed(2);
      if (up) up.value = (mid + range).toFixed(2);
    }
  } catch (_) {}
}

async function handleSubmitGrid() {
  const asset = document.getElementById('grid-asset')?.value;
  const lp = parseFloat(document.getElementById('grid-lower')?.value || '0');
  const up = parseFloat(document.getElementById('grid-upper')?.value || '0');
  const inv = parseFloat(document.getElementById('grid-investment')?.value || '0');
  const nodes = parseInt(document.getElementById('grid-nodes')?.value || '10');
  if (!asset || lp >= up || inv <= 0) {
    eventBus.dispatch('toast', { message: 'Lower must be < Upper, investment > 0', type: 'warning' });
    return;
  }
  setPendingAction('/api/dashboard/grid/open', {
    asset, lower_price: lp, upper_price: up, investment_amount: inv, num_nodes: nodes
  }, `Open Grid Bot: ${asset} [$${lp.toLocaleString()} - $${up.toLocaleString()}]`);
}

async function handleSubmitDca() {
  const asset = document.getElementById('dca-asset')?.value;
  const side = document.getElementById('dca-side')?.value;
  const base = parseFloat(document.getElementById('dca-base-size')?.value || '0');
  const tp = parseFloat(document.getElementById('dca-tp')?.value || '0');
  const sl = parseFloat(document.getElementById('dca-sl')?.value || '0');
  if (!asset || !side || base <= 0) {
    eventBus.dispatch('toast', { message: 'Fill all DCA fields correctly', type: 'warning' });
    return;
  }
  setPendingAction('/api/dashboard/dca/open', {
    asset, side, base_order_size: base, take_profit_pct: tp, stop_loss_pct: sl
  }, `Open DCA Bot: ${side} ${asset}`);
}

async function loadAssetOptions() {
  const r = await getConfigAssets();
  const assets = (r.ok && Array.isArray(r.data)) ? r.data : ['BTC', 'ETH', 'SOL', 'XRP', 'AVAX'];
  ['grid-asset', 'dca-asset'].forEach(id => {
    const sel = document.getElementById(id);
    if (!sel) return;
    sel.innerHTML = assets.map(a => `<option value="${a}">${a}</option>`).join('');
  });
}

function showGridsTab(tab) {
  const cards = document.getElementById('grids-tab-cards');
  const viz = document.getElementById('grids-tab-viz');
  if (cards) cards.style.display = tab === 'cards' ? 'block' : 'none';
  if (viz) viz.style.display = tab === 'viz' ? 'block' : 'none';
  if (tab === 'viz') renderGridVisualizer();
}

function renderGridVisualizer() {
  const canvas = document.getElementById('grid-viz-canvas');
  const noData = document.getElementById('viz-no-data');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width = canvas.parentElement.clientWidth;
  const h = canvas.height = 400;
  ctx.clearRect(0, 0, w, h);

  if (!_gridsCache.length) {
    if (noData) noData.style.display = 'block';
    return;
  }
  if (noData) noData.style.display = 'none';

  // Simple visualization: draw grid levels for first active grid
  const g = _gridsCache[0];
  const lp = g.lower_price ?? 0;
  const up = g.upper_price ?? 0;
  const nodes = g.nodes_total ?? 10;
  const step = (up - lp) / nodes;
  const padding = 40;
  const drawH = h - padding * 2;

  ctx.strokeStyle = '#5d3ef2';
  ctx.lineWidth = 1;
  ctx.font = '11px monospace';
  ctx.fillStyle = '#94a3b8';

  for (let i = 0; i <= nodes; i++) {
    const price = lp + step * i;
    const y = padding + drawH - (i / nodes) * drawH;
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(w - padding, y);
    ctx.stroke();
    ctx.fillText(`$${price.toFixed(2)}`, 2, y + 4);
  }

  // Draw current price indicator if available
  const currentPrice = (lp + up) / 2; // Approximate
  const cy = padding + drawH - ((currentPrice - lp) / (up - lp)) * drawH;
  ctx.strokeStyle = '#22c55e';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(padding, cy);
  ctx.lineTo(w - padding, cy);
  ctx.stroke();
  ctx.fillStyle = '#22c55e';
  ctx.fillText(`← Current ~$${currentPrice.toFixed(2)}`, w - padding + 5, cy + 4);
}

export function render(container) {
  container.innerHTML = `
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-white">🤖 My Robots</h1>
      <div class="flex gap-2">
        <button class="btn-primary text-sm" onclick="document.getElementById('create-bot-panel').style.display='block'">➕ Create Bot</button>
      </div>
    </div>
    <!-- Create Bot Panel (hidden by default) -->
    <div id="create-bot-panel" class="card mb-6" style="display:none;">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-white">Create New Bot</h3>
        <button class="text-slate-500 hover:text-white" onclick="document.getElementById('create-bot-panel').style.display='none'">&times;</button>
      </div>
      <div class="flex gap-2 mb-4">
        <button class="btn-secondary text-sm" onclick="window.__showCreateForm('grid')">Grid Bot</button>
        <button class="btn-secondary text-sm" onclick="window.__showCreateForm('dca')">DCA Bot</button>
      </div>
      <!-- Grid Form -->
      <div id="grid-form" style="display:none;">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div><label class="metric-label block mb-1">Asset</label><select id="grid-asset" class="w-full" onchange="window.__autoFillGrid()"></select></div>
          <div><label class="metric-label block mb-1">Investment ($)</label><input id="grid-investment" type="number" step="1" value="10" class="w-full"></div>
          <div><label class="metric-label block mb-1">Lower Price</label><input id="grid-lower" type="number" step="any" class="w-full"></div>
          <div><label class="metric-label block mb-1">Upper Price</label><input id="grid-upper" type="number" step="any" class="w-full"></div>
          <div><label class="metric-label block mb-1">Num Nodes</label><input id="grid-nodes" type="number" step="1" value="10" class="w-full"></div>
        </div>
        <button class="btn-primary w-full" id="btn-submit-grid">Open Grid Bot</button>
      </div>
      <!-- DCA Form -->
      <div id="dca-form" style="display:none;">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div><label class="metric-label block mb-1">Asset</label><select id="dca-asset" class="w-full"></select></div>
          <div><label class="metric-label block mb-1">Side</label><select id="dca-side" class="w-full"><option value="BUY">BUY</option><option value="SELL">SELL</option></select></div>
          <div><label class="metric-label block mb-1">Base Order Size</label><input id="dca-base-size" type="number" step="any" class="w-full"></div>
          <div><label class="metric-label block mb-1">Take Profit %</label><input id="dca-tp" type="number" step="any" value="1.5" class="w-full"></div>
          <div><label class="metric-label block mb-1">Stop Loss %</label><input id="dca-sl" type="number" step="any" value="3.0" class="w-full"></div>
        </div>
        <button class="btn-primary w-full" id="btn-submit-dca">Open DCA Bot</button>
      </div>
    </div>
    <!-- Active Bots Tabs -->
    <div class="flex gap-2 mb-4">
      <button class="btn-secondary text-sm" onclick="window.__showGridsTab('cards')">📋 Cards</button>
      <button class="btn-secondary text-sm" onclick="window.__showGridsTab('viz')">📊 Visualizer</button>
    </div>
    <div id="grids-tab-cards">
      <div id="grids-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
      <div id="no-grids" class="card text-center py-8 text-slate-500">No active bots</div>
    </div>
    <div id="grids-tab-viz" style="display:none;">
      <div class="card !p-0">
        <div class="px-4 py-3 border-b border-dark-border flex items-center justify-between">
          <span class="font-bold text-white">Grid Visualizer</span>
          <select id="viz-asset-select" class="bg-slate-800 border border-slate-700 text-white text-sm rounded px-2 py-1"></select>
        </div>
        <div class="relative" style="height:400px;">
          <canvas id="grid-viz-canvas" class="w-full h-full"></canvas>
          <div id="viz-no-data" class="absolute inset-0 flex items-center justify-center text-slate-500">No grid data to visualize</div>
        </div>
      </div>
    </div>
  `;

  // Expose functions for onclick handlers
  window.__showCreateForm = showCreateForm;
  window.__autoFillGrid = autoFillGridForm;
  window.__showGridsTab = showGridsTab;

  // Wire submit buttons
  document.getElementById('btn-submit-grid')?.addEventListener('click', handleSubmitGrid);
  document.getElementById('btn-submit-dca')?.addEventListener('click', handleSubmitDca);

  // Load assets
  loadAssetOptions();

  // Subscribe to live updates
  _unsubscribers.push(eventBus.on('sse:grids', (grids) => {
    _gridsCache = grids || [];
    renderBotCards(_gridsCache);
  }));
  _unsubscribers.push(eventBus.on('sse:positions', (positions) => {
    _positionsCache = positions || [];
  }));
}

export function destroy() {
  _unsubscribers.forEach(u => u());
  _unsubscribers = [];
  _gridsCache = [];
  _positionsCache = [];
  window.__showCreateForm = null;
  window.__autoFillGrid = null;
  window.__showGridsTab = null;
}
