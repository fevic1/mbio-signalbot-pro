/**
 * MBIO SignalBot Pro - SSE Connection Manager
 * Phase 12 Migration: Isolated from frontend/index.html
 * 
 * THIS FILE IS NEVER MODIFIED DURING NAVIGATION CHANGES.
 * Contains: connectSSE(), updateOverview(), updatePositions(), updateGrids()
 *           formatUsd(), formatPnl(), pnlClass()
 * 
 * Dependencies: DOM elements must exist before connectSSE() is called.
 */

// === Shared State ===
var eventSource = null;
var _positionsCache = [];

// === Formatting Helpers ===
function formatUsd(v) {
    return '$' + Math.abs(v).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatPnl(v) {
    return (v >= 0 ? '+' : '-') + formatUsd(v);
}

function pnlClass(v) {
    return v > 0 ? 'pnl-positive' : v < 0 ? 'pnl-negative' : 'pnl-neutral';
}

// === SSE Update Functions ===
function updateOverview(d) {
    var el;
    el = document.getElementById('ov-balance');
    if (el) el.textContent = formatUsd(d.balance);
    
    el = document.getElementById('ov-equity');
    if (el) el.textContent = formatUsd(d.equity);
    
    el = document.getElementById('ov-deployed');
    if (el) el.textContent = (d.deployed_pct != null ? d.deployed_pct : 0) + '%';
    
    el = document.getElementById('ov-daily-pnl');
    if (el) {
        el.textContent = (d.daily_pnl_pct >= 0 ? '+' : '') + (d.daily_pnl_pct || 0).toFixed(2) + '%';
        el.className = 'metric-value ' + pnlClass(d.daily_pnl_pct);
    }
    
    el = document.getElementById('ov-realized');
    if (el) {
        el.textContent = formatPnl(d.realized_pnl_usd || 0);
        el.className = 'text-xl font-bold ' + pnlClass(d.realized_pnl_usd);
    }
    
    el = document.getElementById('ov-unrealized');
    if (el) {
        el.textContent = formatPnl(d.unrealized_pnl_usd || 0);
        el.className = 'text-xl font-bold ' + pnlClass(d.unrealized_pnl_usd);
    }
    
    el = document.getElementById('ov-winrate');
    if (el) el.textContent = d.win_rate || 'N/A';
    
    // Sidebar updates
    el = document.getElementById('sidebar-equity');
    if (el) el.textContent = formatUsd(d.equity);
    
    el = document.getElementById('sidebar-pnl');
    if (el) {
        el.textContent = formatPnl(d.unrealized_pnl_usd || 0);
        el.className = 'font-semibold ' + pnlClass(d.unrealized_pnl_usd);
    }
}

function updatePositions(positions) {
    _positionsCache = positions || [];
    var filterEl = document.getElementById('pos-asset-filter');
    if (filterEl && filterEl.options.length <= 1) {
        var assets = {};
        _positionsCache.forEach(function(p) { assets[p.asset] = true; });
        Object.keys(assets).sort().forEach(function(a) {
            var opt = document.createElement('option');
            opt.value = a;
            opt.textContent = a;
            filterEl.appendChild(opt);
        });
    }
    if (typeof renderFilteredPositions === 'function') {
        renderFilteredPositions();
    }
}

function updateGrids(grids) {
    var c = document.getElementById('grids-container');
    var ng = document.getElementById('no-grids');
    if (!c) return;
    
    if (!grids.length) {
        c.innerHTML = '';
        if (ng) ng.style.display = 'block';
        return;
    }
    
    if (ng) ng.style.display = 'none';
    c.innerHTML = grids.map(function(g) {
        return '<div class="card">' +
            '<div class="flex items-center justify-between mb-3">' +
                '<div class="flex items-center gap-2">' +
                    '<span class="badge badge-grid">GRID</span>' +
                    '<span class="text-lg font-bold text-white">' + g.asset + '</span>' +
                '</div>' +
                '<span class="text-xs text-slate-400">' + g.mode + '</span>' +
            '</div>' +
            '<div class="grid grid-cols-2 gap-3 text-sm">' +
                '<div><span class="metric-label">Range</span><br>$' +
                    g.lower_price.toLocaleString() + ' - $' + g.upper_price.toLocaleString() + '</div>' +
                '<div><span class="metric-label">Nodes</span><br>' +
                    g.nodes_active + '/' + g.nodes_total + '</div>' +
                '<div><span class="metric-label">Cycles</span><br>' + g.cycles + '</div>' +
                '<div><span class="metric-label">PnL</span><br>' +
                    '<span class="' + pnlClass(g.realized_pnl) + '">' +
                    formatPnl(g.realized_pnl) + '</span></div>' +
            '</div></div>';
    }).join('');
}

// === SSE Connection Manager ===
function connectSSE() {
    if (eventSource) eventSource.close();
    
    eventSource = new EventSource('/api/dashboard/stream', { withCredentials: true });
    
    eventSource.onopen = function() {
        var statusEl = document.getElementById('connection-status');
        var textEl = document.getElementById('connection-text');
        if (statusEl) statusEl.className = 'connected';
        if (textEl) textEl.textContent = 'Live';
    };
    
    eventSource.onmessage = function(e) {
        try {
            var d = JSON.parse(e.data);
            if (d.error) return;
            updateOverview(d);
            updatePositions(d.positions || []);
            updateGrids(d.grids || []);
        } catch (ex) {
            console.error('[SSE] Parse error:', ex);
        }
    };
    
    eventSource.onerror = function() {
        var statusEl = document.getElementById('connection-status');
        var textEl = document.getElementById('connection-text');
        if (statusEl) statusEl.className = 'disconnected';
        if (textEl) textEl.textContent = 'Reconnecting...';
        setTimeout(connectSSE, 5000);
    };
}

// === Initial Health Check (one-shot) ===
function loadInitialHealth() {
    fetch('/api/dashboard/health', { credentials: 'include' })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            var el = document.getElementById('health-checks');
            if (!el) return;
            var checks = d.checks || {};
            var html = '';
            for (var k in checks) {
                var v = checks[k];
                html += '<div class="flex items-center gap-2">' +
                    (v ? '\u2705' : '\u274C') +
                    ' <span class="' + (v ? 'text-green-400' : 'text-red-400') + '">' +
                    k.replace(/_/g, ' ') + '</span></div>';
            }
            el.innerHTML = html;
        })
        .catch(function() {});
}
