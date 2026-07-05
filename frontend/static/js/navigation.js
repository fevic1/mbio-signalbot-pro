/**
 * MBIO SignalBot Pro - Navigation Module
 * Phase 12 Migration: Implements HTML xxxx.md showPage() pattern
 * 
 * Dependencies: sse.js (loaded before this file)
 * Preserves ALL existing page-specific init calls from original showPage()
 */

// === Global State (shared with sse.js and inline scripts) ===
var configDefaults = {};
var currentUser = null;
var pendingAction = null;
var availableAssets = [];
var fullConfig = {};
var equityChartInstance = null;
var _positionsCache = [];
var _sortCol = 'upnl';
var _sortAsc = false;
var _filterAsset = '';

// === URL Route Mapping ===
var _pageRouteMap = {
    'dashboard': '/dashboard', 'positions': '/dashboard', 'orders': '/dashboard',
    'grids': '/robots', 'create': '/robots',
    'history': '/analytics', 'analytics': '/analytics', 'audit': '/analytics',
    'config': '/settings', 'safety': '/settings', 'reconcile': '/settings',
    'sysmon': '/settings', 'alerts': '/settings'
};
var _routePageMap = {
    '/dashboard': 'dashboard', '/robots': 'grids',
    '/analytics': 'history', '/settings': 'config'
};

// === Core Navigation Function (HTML xxxx.md Pattern) ===
function showPage(pageName, btnElement) {
    // 1. Hide all main content pages
    document.querySelectorAll('main > div[id^="page-"]').forEach(function(page) {
        page.style.display = 'none';
    });

    // 2. Show target page
    var target = document.getElementById('page-' + pageName);
    if (target) target.style.display = 'block';

    // 3. Update active button style (HTML xxxx.md pattern)
    document.querySelectorAll('nav button.nav-item').forEach(function(btn) {
        btn.classList.remove('bg-[#1e232f]', 'text-[#5d3ef2]');
    });
    if (btnElement) {
        btnElement.classList.add('bg-[#1e232f]', 'text-[#5d3ef2]');
    }

    // 4. Preserve ALL existing init calls from original showPage()
    if (typeof hideBotForms === 'function') hideBotForms();
    if (pageName === 'history' && typeof loadTradeHistory === 'function') loadTradeHistory();
    if (pageName === 'analytics' && typeof loadAnalytics === 'function') loadAnalytics();
    if (pageName === 'config' && typeof loadConfigForEdit === 'function') loadConfigForEdit();
    if (pageName === 'safety' && typeof loadSafetyPanel === 'function') loadSafetyPanel();
    if (pageName === 'audit' && typeof loadAuditLog === 'function') loadAuditLog();
    if (pageName === 'reconcile' && typeof loadOrphanedSignals === 'function') loadOrphanedSignals();
    if (pageName === 'sysmon' && typeof loadSystemMonitor === 'function') loadSystemMonitor();
    if (pageName === 'alerts' && typeof loadAlertConfig === 'function') loadAlertConfig();
    if (pageName === 'dashboard' && typeof loadRecentTrades === 'function') loadRecentTrades();
}

// === URL Routing ===
function navigateTo(page, el) {
    showPage(page, el);
    var route = _pageRouteMap[page] || '/dashboard';
    if (window.location.pathname !== route) {
        history.pushState({page: page}, '', route);
    }
}

window.addEventListener('popstate', function(e) {
    var page = (e.state && e.state.page) ? e.state.page : (_routePageMap[window.location.pathname] || 'dashboard');
    var navEl = document.querySelector('button.nav-item[onclick*="' + page + '"]');
    showPage(page, navEl);
});

// === Initial Load ===
document.addEventListener('DOMContentLoaded', function() {
    // Resolve initial page from URL
    var path = window.location.pathname;
    var initialPage = _routePageMap[path] || 'dashboard';
    var navEl = document.querySelector('button.nav-item[onclick*="' + initialPage + '"]');
    showPage(initialPage, navEl);

    // Start SSE connection (from sse.js)
    if (typeof connectSSE === 'function') connectSSE();

    // Load initial health check (from sse.js)
    if (typeof loadInitialHealth === 'function') loadInitialHealth();

    // Load user info
    if (typeof MBIO_API !== 'undefined') {
        MBIO_API.getMe().then(function(r) {
            if (r.ok && r.data) {
                currentUser = r.data;
                var nameEl = document.getElementById('user-name');
                var roleEl = document.getElementById('user-role');
                if (nameEl) nameEl.textContent = r.data.name || r.data.email || 'User';
                if (roleEl) roleEl.textContent = r.data.role || 'USER';
            }
        });
    }
});
