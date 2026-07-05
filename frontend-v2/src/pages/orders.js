/**
 * Order Desk Page
 * Market, Limit, Stop-Limit, Trailing order forms with HIP-4 pre-validation.
 * All submissions require OTP via auth.js service.
 */
import { eventBus } from '../event-bus.js';
import { setPendingAction } from '../services/auth.js';
import { validateOrder, getAssets } from '../api/hip4.js';
import { getConfigAssets } from '../api/dashboard.js';

let _availableAssets = [];

async function loadAssets() {
  const result = await getConfigAssets();
  if (result.ok && Array.isArray(result.data)) {
    _availableAssets = result.data;
  } else {
    // Fallback: fetch from HIP-4 endpoint
    const hip4 = await getAssets('PERP');
    if (hip4.ok && Array.isArray(hip4.data?.assets)) {
      _availableAssets = hip4.data.assets.map(a => a.name || a);
    }
  }
  // Populate all asset selectors
  ['mkt-asset', 'lmt-asset', 'sl-asset', 'ts-asset'].forEach(id => {
    const sel = document.getElementById(id);
    if (!sel) return;
    sel.innerHTML = '<option value="">Select Asset</option>' +
      _availableAssets.map(a => `<option value="${a}">${a}</option>`).join('');
  });
}

function showOrderTab(tabName, btnEl) {
  ['market', 'limit', 'stoplimit', 'trailing'].forEach(t => {
    const el = document.getElementById(`order-${t}`);
    if (el) el.style.display = t === tabName ? 'block' : 'none';
  });
  document.querySelectorAll('.order-tab-btn').forEach(b => {
    b.classList.remove('bg-accent-primary', 'text-white');
    b.classList.add('bg-slate-800', 'text-slate-400');
  });
  if (btnEl) {
    btnEl.classList.remove('bg-slate-800', 'text-slate-400');
    btnEl.classList.add('bg-accent-primary', 'text-white');
  }
}

async function handleSubmitMarket() {
  const asset = document.getElementById('mkt-asset')?.value;
  const side = document.getElementById('mkt-side')?.value;
  const size = parseFloat(document.getElementById('mkt-size')?.value || '0');
  if (!asset || !side || size <= 0) {
    eventBus.dispatch('toast', { message: 'Fill all fields correctly', type: 'warning' });
    return;
  }
  setPendingAction('/api/dashboard/order/market', { asset, side, size }, `Market ${side} ${size} ${asset}`);
}

async function handleSubmitLimit() {
  const asset = document.getElementById('lmt-asset')?.value;
  const side = document.getElementById('lmt-side')?.value;
  const size = parseFloat(document.getElementById('lmt-size')?.value || '0');
  const price = parseFloat(document.getElementById('lmt-price')?.value || '0');
  if (!asset || !side || size <= 0 || price <= 0) {
    eventBus.dispatch('toast', { message: 'Fill all fields correctly', type: 'warning' });
    return;
  }
  // HIP-4 pre-validation
  const v = await validateOrder(asset, price, size);
  if (!v.success && !v.valid) {
    eventBus.dispatch('toast', { message: v.error || 'HIP-4 validation failed', type: 'error' });
    return;
  }
  setPendingAction('/api/dashboard/order/limit', {
    asset, side, size: v.rounded_size || size, price: v.rounded_price || price
  }, `Limit ${side} ${size} ${asset} @ $${(v.rounded_price || price).toLocaleString()}`);
}

export function render(container) {
  container.innerHTML = `
    <div class="mb-6"><h1 class="text-2xl font-bold text-white">📝 Order Desk</h1></div>
    <!-- Tab Buttons -->
    <div class="flex gap-2 mb-6">
      <button class="order-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-accent-primary text-white" onclick="window.__showOrderTab('market', this)">Market</button>
      <button class="order-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showOrderTab('limit', this)">Limit</button>
      <button class="order-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showOrderTab('stoplimit', this)">Stop-Limit</button>
      <button class="order-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showOrderTab('trailing', this)">Trailing</button>
    </div>
    <!-- Market Order Form -->
    <div id="order-market" class="card max-w-2xl">
      <h3 class="text-lg font-bold text-white mb-4">Market Order</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div><label class="metric-label block mb-1">Asset</label><select id="mkt-asset" class="w-full"></select></div>
        <div><label class="metric-label block mb-1">Side</label><select id="mkt-side" class="w-full"><option value="BUY">BUY</option><option value="SELL">SELL</option></select></div>
        <div><label class="metric-label block mb-1">Size</label><input id="mkt-size" type="number" step="any" placeholder="0.00" class="w-full"></div>
      </div>
      <button id="btn-submit-market" class="btn-primary w-full">Submit Market Order</button>
    </div>
    <!-- Limit Order Form -->
    <div id="order-limit" class="card max-w-2xl" style="display:none;">
      <h3 class="text-lg font-bold text-white mb-4">Limit Order</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div><label class="metric-label block mb-1">Asset</label><select id="lmt-asset" class="w-full"></select></div>
        <div><label class="metric-label block mb-1">Side</label><select id="lmt-side" class="w-full"><option value="BUY">BUY</option><option value="SELL">SELL</option></select></div>
        <div><label class="metric-label block mb-1">Size</label><input id="lmt-size" type="number" step="any" placeholder="0.00" class="w-full"></div>
        <div><label class="metric-label block mb-1">Price</label><input id="lmt-price" type="number" step="any" placeholder="0.00" class="w-full"></div>
      </div>
      <button id="btn-submit-limit" class="btn-primary w-full">Submit Limit Order</button>
    </div>
    <!-- Stop-Limit Form (Placeholder) -->
    <div id="order-stoplimit" class="card max-w-2xl" style="display:none;">
      <h3 class="text-lg font-bold text-white mb-4">Stop-Limit Order</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div><label class="metric-label block mb-1">Asset</label><select id="sl-asset" class="w-full"></select></div>
        <div><label class="metric-label block mb-1">Side</label><select id="sl-side" class="w-full"><option value="BUY">BUY</option><option value="SELL">SELL</option></select></div>
        <div><label class="metric-label block mb-1">Size</label><input id="sl-size" type="number" step="any" class="w-full"></div>
        <div><label class="metric-label block mb-1">Stop Price</label><input id="sl-stop" type="number" step="any" class="w-full"></div>
        <div><label class="metric-label block mb-1">Limit Price</label><input id="sl-limit" type="number" step="any" class="w-full"></div>
      </div>
      <button class="btn-secondary w-full">Coming Soon</button>
    </div>
    <!-- Trailing Form (Placeholder) -->
    <div id="order-trailing" class="card max-w-2xl" style="display:none;">
      <h3 class="text-lg font-bold text-white mb-4">Trailing Stop</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div><label class="metric-label block mb-1">Asset</label><select id="ts-asset" class="w-full"></select></div>
        <div><label class="metric-label block mb-1">Side</label><select id="ts-side" class="w-full"><option value="BUY">BUY</option><option value="SELL">SELL</option></select></div>
        <div><label class="metric-label block mb-1">Size</label><input id="ts-size" type="number" step="any" class="w-full"></div>
        <div><label class="metric-label block mb-1">Trail %</label><input id="ts-trail" type="number" step="any" class="w-full"></div>
      </div>
      <button class="btn-secondary w-full">Coming Soon</button>
    </div>
  `;

  // Expose tab switcher globally for onclick handlers
  window.__showOrderTab = showOrderTab;

  // Wire submit buttons
  document.getElementById('btn-submit-market')?.addEventListener('click', handleSubmitMarket);
  document.getElementById('btn-submit-limit')?.addEventListener('click', handleSubmitLimit);

  // Load assets for dropdowns
  loadAssets();
}

export function destroy() {
  window.__showOrderTab = null;
}
