/**
 * MBIO Live Data Wiring
 * Connects frontend HTML elements to MBIO_API backend endpoints.
 */
(function() {
    'use strict';

    // Helper to safely update text content
    function setText(id, value, prefix = '', suffix = '') {
        const el = document.getElementById(id);
        if (el) el.textContent = prefix + (value !== null && value !== undefined ? value : 'N/A') + suffix;
    }

    // Helper to format currency
    function formatUSD(val) {
        return '$' + (parseFloat(val) || 0).toFixed(2);
    }

    // Helper to format percentage and set color class
    function setPnL(id, val) {
        const el = document.getElementById(id);
        if (!el) return;
        const num = parseFloat(val) || 0;
        el.textContent = (num >= 0 ? '+' : '') + num.toFixed(2) + '%';
        el.className = 'metric-value ' + (num > 0 ? 'text-green-400' : (num < 0 ? 'text-red-400' : 'text-slate-400'));
    }

    // 1. Update Dashboard Overview Metrics
    async function updateDashboardOverview() {
        try {
            const res = await MBIO_API.getOverview();
            if (res.ok && res.data) {
                const d = res.data;
                setText('ov-balance', formatUSD(d.balance || d.account_balance));
                setText('ov-equity', formatUSD(d.equity || d.account_equity));
                setText('ov-deployed', (parseFloat(d.deployed_pct || d.deployed) || 0).toFixed(1) + '%');
                setPnL('ov-daily-pnl', d.daily_pnl_pct || d.daily_pnl);
                setText('ov-realized', formatUSD(d.realized_pnl));
                setText('ov-unrealized', formatUSD(d.unrealized_pnl));
                setText('ov-winrate', (parseFloat(d.win_rate) || 0).toFixed(1) + '%');
            }
        } catch (e) { console.error('Overview update failed:', e); }
    }

    // 2. Update Recent Trades Table
    async function updateRecentTrades() {
        try {
            const res = await MBIO_API.getTradeHistory(10);
            const tbody = document.getElementById('recent-trades-body');
            if (!tbody) return;

            if (res.ok && res.data && res.data.trades && res.data.trades.length > 0) {
                tbody.innerHTML = res.data.trades.map(trade => {
                    const pnl = parseFloat(trade.pnl) || 0;
                    const pnlClass = pnl >= 0 ? 'text-green-400' : 'text-red-400';
                    const sideClass = (trade.side || '').toUpperCase().includes('BUY') ? 'text-green-400' : 'text-red-400';
                    return `
                        <tr class="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                            <td class="py-3 text-slate-400">${trade.time || trade.timestamp || 'N/A'}</td>
                            <td class="py-3 font-medium text-white">${trade.asset || trade.coin || 'N/A'}</td>
                            <td class="py-3 ${sideClass} font-semibold">${trade.side || 'N/A'}</td>
                            <td class="py-3 text-right ${pnlClass} font-semibold">${formatUSD(pnl)}</td>
                        </tr>
                    `;
                }).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center py-6 text-slate-500">No recent trades</td></tr>';
            }
        } catch (e) { console.error('Trades update failed:', e); }
    }

    // 3. Update System Monitoring (Settings Page)
    async function updateSystemMonitoring() {
        try {
            const res = await MBIO_API.getSystemStatus();
            if (res.ok && res.data) {
                const d = res.data;
                setText('sys-uptime', d.uptime || 'N/A');
                setText('sys-autotrade', d.auto_trading ? 'ENABLED' : 'DISABLED');
                
                const healthyEl = document.getElementById('sys-healthy');
                if (healthyEl) {
                    healthyEl.textContent = d.healthy ? 'YES' : 'NO';
                    healthyEl.className = 'metric-value ' + (d.healthy ? 'text-green-400' : 'text-red-400');
                }

                const tbody = document.getElementById('sysmon-table');
                if (tbody && d.tasks && Array.isArray(d.tasks)) {
                    tbody.innerHTML = d.tasks.map(task => {
                        const statusClass = (task.status === 'running' || task.status === 'active') ? 'text-green-400' : 'text-red-400';
                        return `
                            <tr class="border-b border-slate-800 hover:bg-slate-800/50">
                                <td class="py-3 text-white font-medium capitalize">${(task.name || 'Unknown').replace(/_/g, ' ')}</td>
                                <td class="py-3 ${statusClass} font-semibold capitalize">${task.status || 'unknown'}</td>
                                <td class="py-3 text-slate-400">${task.last_run || 'N/A'}</td>
                                <td class="py-3 text-slate-400">${task.errors || 0}</td>
                            </tr>
                        `;
                    }).join('');
                }
            }
        } catch (e) { console.error('System status update failed:', e); }
    }

    // 4. Update Health Checks (Dashboard)
    async function updateHealthChecks() {
        try {
            const res = await MBIO_API.getHealth();
            const container = document.getElementById('health-checks');
            if (container && res.ok && res.data && res.data.checks) {
                container.innerHTML = Object.entries(res.data.checks).map(([key, val]) => {
                    const isOk = val === 'ok' || val === true || val === 'healthy';
                    return `
                        <div class="flex items-center gap-2 p-2 rounded bg-slate-800/50 border border-slate-700">
                            <span class="w-2 h-2 rounded-full ${isOk ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500'}"></span>
                            <span class="text-slate-300 text-xs capitalize">${key.replace(/_/g, ' ')}</span>
                        </div>
                    `;
                }).join('');
            }
        } catch (e) { console.error('Health update failed:', e); }
    }

    // Initialize and set up 5-second polling for a "live" feel
    function initLiveWiring() {
        console.log('[MBIO] Live data wiring initialized');
        updateDashboardOverview();
        updateRecentTrades();
        updateSystemMonitoring();
        updateHealthChecks();

        setInterval(() => {
            updateDashboardOverview();
            updateRecentTrades();
            updateSystemMonitoring();
            updateHealthChecks();
        }, 5000); // 5-second refresh interval
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLiveWiring);
    } else {
        initLiveWiring();
    }
})();
