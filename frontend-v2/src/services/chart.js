/**
 * TradingView Chart Service
 * Manages widget lifecycle with load guard and error handling.
 * Uses BINANCE: symbols (TV doesn't index Hyperliquid directly).
 */

let _widget = null;
const DEFAULT_SYMBOL = 'BINANCE:BTCUSDT';

export function initChart(symbol = DEFAULT_SYMBOL) {
  // Guard: wait for library
  if (typeof TradingView === 'undefined') {
    const msg = document.getElementById('tv-loading-msg');
    if (msg) msg.textContent = 'Loading chart library...';
    setTimeout(() => initChart(symbol), 2000);
    return;
  }

  // Destroy previous instance
  if (_widget) {
    try { _widget.remove(); } catch (_) {}
    _widget = null;
  }

  const container = document.getElementById('tv-chart-container');
  if (!container) return;
  container.innerHTML = '';

  try {
    _widget = new TradingView.widget({
      autosize: true,
      symbol: symbol,
      interval: '15',
      timezone: 'Etc/UTC',
      theme: 'dark',
      style: '1',
      locale: 'en',
      toolbar_bg: '#0b0e11',
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: true,
      container_id: 'tv-chart-container',
      backgroundColor: '#0b0e11',
      gridLineColor: '#1e232f',
      overrides: {
        'paneProperties.background': '#0b0e11',
        'paneProperties.vertGridProperties.color': '#1e232f',
        'paneProperties.horzGridProperties.color': '#1e232f',
        'mainSeriesProperties.candleStyle.upColor': '#22c55e',
        'mainSeriesProperties.candleStyle.downColor': '#ef4444',
        'mainSeriesProperties.candleStyle.wickUpColor': '#22c55e',
        'mainSeriesProperties.candleStyle.wickDownColor': '#ef4444',
      },
      loading_screen: { backgroundColor: '#0b0e11', foregroundColor: '#94a3b8' },
    });
  } catch (err) {
    console.error('[Chart] Init error:', err);
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full text-slate-500 p-8">
        <div class="text-2xl mb-2">⚠️</div>
        <div class="text-sm font-medium">Chart failed to initialize</div>
        <div class="text-xs mt-1">${err.message}</div>
        <button onclick="window.__retryChart && window.__retryChart()" class="mt-3 px-4 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-500">Retry</button>
      </div>`;
  }
}

// Expose retry globally for error button
window.__retryChart = () => {
  const sel = document.getElementById('tv-pair-selector');
  initChart(sel ? sel.value : DEFAULT_SYMBOL);
};

export function updateChart(symbol) {
  if (symbol) initChart(symbol);
}

export function destroyChart() {
  if (_widget) {
    try { _widget.remove(); } catch (_) {}
    _widget = null;
  }
}
