/**
 * SSE Connection Manager
 * Connects to /api/dashboard/stream and dispatches typed events via EventBus.
 * THIS MODULE IS NEVER MODIFIED WHEN ADDING NEW PAGES OR COMPONENTS.
 */
import { eventBus } from '../event-bus.js';

let _eventSource = null;
let _reconnectTimer = null;
const RECONNECT_DELAY_MS = 5000;
const SSE_ENDPOINT = '/api/dashboard/stream';

function updateConnectionStatus(status, text) {
  const dot = document.getElementById('connection-status');
  const label = document.getElementById('connection-text');
  if (dot) dot.className = `status-dot ${status}`;
  if (label) label.textContent = text;
}

function handleMessage(rawData) {
  try {
    const data = JSON.parse(rawData);
    if (data.error) return;

    // Dispatch granular events so modules subscribe only to what they need
    eventBus.dispatch('sse:overview', {
      balance: data.balance ?? 0,
      equity: data.equity ?? 0,
      deployed_pct: data.deployed_pct ?? 0,
      daily_pnl_pct: data.daily_pnl_pct ?? 0,
      realized_pnl_usd: data.realized_pnl_usd ?? 0,
      unrealized_pnl_usd: data.unrealized_pnl_usd ?? 0,
      win_rate: data.win_rate ?? 'N/A',
    });

    if (Array.isArray(data.positions)) {
      eventBus.dispatch('sse:positions', data.positions);
    }

    if (Array.isArray(data.grids)) {
      eventBus.dispatch('sse:grids', data.grids);
    }

    // Header bar updates
    const headerEquity = document.getElementById('header-equity');
    const headerPnl = document.getElementById('header-pnl');
    if (headerEquity) headerEquity.textContent = `$${(data.equity ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    if (headerPnl) {
      const pnl = data.unrealized_pnl_usd ?? 0;
      headerPnl.textContent = `${pnl >= 0 ? '+' : ''}$${Math.abs(pnl).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      headerPnl.className = `text-sm font-semibold ${pnl > 0 ? 'pnl-positive' : pnl < 0 ? 'pnl-negative' : 'pnl-neutral'}`;
    }
  } catch (err) {
    console.error('[SSE] Parse error:', err);
  }
}

export function connectSSE() {
  if (_eventSource) {
    _eventSource.close();
    _eventSource = null;
  }
  if (_reconnectTimer) {
    clearTimeout(_reconnectTimer);
    _reconnectTimer = null;
  }

  _eventSource = new EventSource(SSE_ENDPOINT, { withCredentials: true });

  _eventSource.onopen = () => {
    updateConnectionStatus('connected', 'Live');
    eventBus.dispatch('sse:connected', {});
  };

  _eventSource.onmessage = (e) => handleMessage(e.data);

  _eventSource.onerror = () => {
    updateConnectionStatus('disconnected', 'Reconnecting...');
    eventBus.dispatch('sse:disconnected', {});
    _eventSource.close();
    _eventSource = null;
    _reconnectTimer = setTimeout(connectSSE, RECONNECT_DELAY_MS);
  };
}

export function disconnectSSE() {
  if (_reconnectTimer) clearTimeout(_reconnectTimer);
  if (_eventSource) _eventSource.close();
  _eventSource = null;
  updateConnectionStatus('disconnected', 'Disconnected');
}
