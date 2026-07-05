/**
 * MBIO SignalBot Pro - Centralized API Module
 * Phase 12 Migration: Extracted from frontend/index.html
 * 
 * All wrappers include credentials:'include' for cookie session auth.
 * Returns {ok: boolean, data: object|null, error: string|null}
 * 
 * THIS MODULE WRAPS EXISTING BACKEND ENDPOINTS ONLY.
 * No new endpoints created. No REST polling. No WebSocket.
 */

var MBIO_API = (function() {
    'use strict';

    var BASE = '/api/dashboard';

    /**
     * Core fetch wrapper with consistent error handling
     */
    async function request(path, options) {
        options = options || {};
        options.credentials = 'include';
        if (options.body && typeof options.body === 'object') {
            options.headers = options.headers || {};
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }
        try {
            var resp = await fetch(BASE + path, options);
            var data = null;
            try { data = await resp.json(); } catch(e) { data = null; }
            return { ok: resp.ok, status: resp.status, data: data, error: (!resp.ok && data && data.detail) ? data.detail : null };
        } catch (err) {
            return { ok: false, status: 0, data: null, error: 'Network error: ' + err.message };
        }
    }

    // === AUTH ===
    function logout() {
        return request('/auth/logout', { method: 'POST' });
    }

    function getMe() {
        return request('/auth/me');
    }

    function requestOtp() {
        return request('/auth/otp/request', { method: 'POST' });
    }

    // === DATA ===
    function getOverview() {
        return request('/overview');
    }

    function getHealth() {
        return request('/health');
    }

    function getAnalytics() {
        return request('/analytics');
    }

    function getSystemStatus() {
        return request('/system/status');
    }

    // === TRADES ===
    function getTradeHistory(limit) {
        limit = limit || 100;
        return request('/trade-history?limit=' + limit);
    }

    // === CONFIG ===
    function getCurrentConfig() {
        return request('/config/current');
    }

    function getConfigDefaults() {
        return request('/config/defaults');
    }

    function getConfigAssets() {
        return request('/config/assets');
    }

    // === ACTIONS (OTP-Protected) ===
    function emergencyStop(otp) {
        return request('/emergency-stop', { method: 'POST', body: { otp: otp } });
    }

    function openDca(params, otp) {
        params.otp = otp;
        return request('/dca/open', { method: 'POST', body: params });
    }

    function openGrid(params, otp) {
        params.otp = otp;
        return request('/grid/open', { method: 'POST', body: params });
    }

    function submitMarketOrder(params, otp) {
        params.otp = otp;
        return request('/order/market', { method: 'POST', body: params });
    }

    function submitLimitOrder(params, otp) {
        params.otp = otp;
        return request('/order/limit', { method: 'POST', body: params });
    }

    // === OTHER ===
    function getOrphanedSignals() {
        return request('/signals/orphaned');
    }

    function getAlertConfig() {
        return request('/alerts/config');
    }

    function saveAlertConfig(config) {
        return request('/alerts/config', { method: 'POST', body: config });
    }

    function getAuditLog(params) {
        var qs = new URLSearchParams(params || {}).toString();
        return request('/audit-log' + (qs ? '?' + qs : ''));
    }

    function getPrice(asset) {
        return request('/price/' + encodeURIComponent(asset));
    }

    // === HIP-4 PLACEHOLDER (Future: UPDATE.md integration) ===
    function getHip4Spec(asset) {
        // Backend endpoint not yet implemented. Returns stub.
        return Promise.resolve({ ok: false, data: null, error: 'HIP-4 spec endpoint not yet available' });
    }

    // Public API
    return {
        logout: logout,
        getMe: getMe,
        requestOtp: requestOtp,
        getOverview: getOverview,
        getHealth: getHealth,
        getAnalytics: getAnalytics,
        getSystemStatus: getSystemStatus,
        getTradeHistory: getTradeHistory,
        getCurrentConfig: getCurrentConfig,
        getConfigDefaults: getConfigDefaults,
        getConfigAssets: getConfigAssets,
        emergencyStop: emergencyStop,
        openDca: openDca,
        openGrid: openGrid,
        submitMarketOrder: submitMarketOrder,
        submitLimitOrder: submitLimitOrder,
        getOrphanedSignals: getOrphanedSignals,
        getAlertConfig: getAlertConfig,
        saveAlertConfig: saveAlertConfig,
        getAuditLog: getAuditLog,
        getPrice: getPrice,
        getHip4Spec: getHip4Spec,
        _request: request  // Exposed for custom endpoint calls
    };
})();
