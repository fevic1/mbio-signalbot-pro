(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))i(n);new MutationObserver(n=>{for(const o of n)if(o.type==="childList")for(const a of o.addedNodes)a.tagName==="LINK"&&a.rel==="modulepreload"&&i(a)}).observe(document,{childList:!0,subtree:!0});function s(n){const o={};return n.integrity&&(o.integrity=n.integrity),n.referrerPolicy&&(o.referrerPolicy=n.referrerPolicy),n.crossOrigin==="use-credentials"?o.credentials="include":n.crossOrigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function i(n){if(n.ep)return;n.ep=!0;const o=s(n);fetch(n.href,o)}})();const u=new EventTarget,l={dispatch(e,t){u.dispatchEvent(new CustomEvent(e,{detail:t}))},on(e,t){const s=i=>t(i.detail);return u.addEventListener(e,s),()=>u.removeEventListener(e,s)},once(e,t){const s=i=>{t(i.detail),u.removeEventListener(e,s)};u.addEventListener(e,s)}};let d=null,f=null;const O=5e3,A="/api/dashboard/stream";function T(e,t){const s=document.getElementById("connection-status"),i=document.getElementById("connection-text");s&&(s.className=`status-dot ${e}`),i&&(i.textContent=t)}function D(e){try{const t=JSON.parse(e);if(t.error)return;l.dispatch("sse:overview",{balance:t.balance??0,equity:t.equity??0,deployed_pct:t.deployed_pct??0,daily_pnl_pct:t.daily_pnl_pct??0,realized_pnl_usd:t.realized_pnl_usd??0,unrealized_pnl_usd:t.unrealized_pnl_usd??0,win_rate:t.win_rate??"N/A"}),Array.isArray(t.positions)&&l.dispatch("sse:positions",t.positions),Array.isArray(t.grids)&&l.dispatch("sse:grids",t.grids);const s=document.getElementById("header-equity"),i=document.getElementById("header-pnl");if(s&&(s.textContent=`$${(t.equity??0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2})}`),i){const n=t.unrealized_pnl_usd??0;i.textContent=`${n>=0?"+":""}$${Math.abs(n).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2})}`,i.className=`text-sm font-semibold ${n>0?"pnl-positive":n<0?"pnl-negative":"pnl-neutral"}`}}catch(t){console.error("[SSE] Parse error:",t)}}function L(){d&&(d.close(),d=null),f&&(clearTimeout(f),f=null),d=new EventSource(A,{withCredentials:!0}),d.onopen=()=>{T("connected","Live"),l.dispatch("sse:connected",{})},d.onmessage=e=>D(e.data),d.onerror=()=>{T("disconnected","Reconnecting..."),l.dispatch("sse:disconnected",{}),d.close(),d=null,f=setTimeout(L,O)}}const U="/api/dashboard";async function N(e,t={}){const s=e.startsWith("http")?e:`${U}${e}`,i={credentials:"include",...t};i.body&&typeof i.body=="object"&&(i.headers={"Content-Type":"application/json",...i.headers||{}},i.body=JSON.stringify(i.body));try{const n=await fetch(s,i);let o=null;try{o=await n.json()}catch{}return{ok:n.ok,status:n.status,data:o,error:!n.ok&&(o!=null&&o.detail)?o.detail:null}}catch(n){return{ok:!1,status:0,data:null,error:`Network error: ${n.message}`}}}function w(e){return N(e,{method:"GET"})}function j(e,t){return N(e,{method:"POST",body:t})}async function z(){const e=await w("/auth/me");if(e.ok&&e.data){e.data;const t=document.getElementById("user-name"),s=document.getElementById("user-role");t&&(t.textContent=e.data.name||e.data.email||"User"),s&&(s.textContent=(e.data.role||"USER").toUpperCase()),l.dispatch("auth:user-loaded",e.data)}return e}async function H(){await j("/auth/logout",{}),window.location.href="/login"}const C={success:"bg-green-600 border-green-500",error:"bg-red-600 border-red-500",warning:"bg-yellow-600 border-yellow-500",info:"bg-blue-600 border-blue-500"},$={success:"✅",error:"❌",warning:"⚠️",info:"📢"};function k(e,t="info",s=3e3){const i=document.getElementById("toast-container");if(!i)return;const n=document.createElement("div");n.className=`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border ${C[t]||C.info} text-white min-w-[300px] animate-slide-in`,n.innerHTML=`
    <span class="text-xl">${$[t]||$.info}</span>
    <span class="flex-1 font-medium text-sm">${e}</span>
    <button class="text-white/70 hover:text-white">&times;</button>
  `,n.querySelector("button").addEventListener("click",()=>n.remove()),i.appendChild(n),setTimeout(()=>{n.style.opacity="0",n.style.transform="translateX(100%)",n.style.transition="all 0.3s ease",setTimeout(()=>n.remove(),300)},s)}l.on("toast",({message:e,type:t,duration:s})=>{k(e,t,s)});const S={};let m=null;function r(e,t){S[e]=t}function g(e,t=!0){const s=e.startsWith("/")?e:`/${e}`,i=S[s];if(!i){console.warn(`[Router] No route registered for: ${s}`);return}t&&window.location.pathname!==s&&history.pushState({path:s},"",s);const n=document.getElementById("page-container");n&&(m&&typeof m.destroy=="function"&&m.destroy(),n.innerHTML="",m=i,typeof i.render=="function"?i.render(n):typeof i=="function"&&i(n),l.dispatch("nav:change",{path:s}))}function q(){window.addEventListener("popstate",s=>{var n;const i=((n=s.state)==null?void 0:n.path)||"/dashboard";g(i,!1)});const e=window.location.pathname,t=S[e]?e:"/dashboard";g(t,!1)}const R=[{category:null,label:"📊 Dashboard",path:"/dashboard",icon:""},{category:"Trading",label:"📈 Positions",path:"/positions",icon:""},{category:null,label:"📝 Order Desk",path:"/orders",icon:""},{category:null,label:"🔲 Grid Bots",path:"/robots",icon:""},{category:null,label:"➕ Create Bot",path:"/create",icon:""},{category:"Analytics",label:"📜 Trade History",path:"/history",icon:""},{category:null,label:"📉 Performance",path:"/analytics",icon:""},{category:null,label:"📋 Audit Log",path:"/audit",icon:""},{category:"System",label:"⚙ Config",path:"/config",icon:""},{category:null,label:"🛡 Safety",path:"/safety",icon:""},{category:null,label:"🔧 Reconcile",path:"/reconcile",icon:""},{category:null,label:"🖥 System",path:"/sysmon",icon:""},{category:null,label:"🔔 Alerts",path:"/alerts",icon:""}],h={"/dashboard":"/dashboard","/positions":"/positions","/orders":"/orders","/robots":"/robots","/create":"/robots","/history":"/history","/analytics":"/analytics","/audit":"/audit","/config":"/config","/safety":"/config","/reconcile":"/config","/sysmon":"/config","/alerts":"/config"};let B="/dashboard";function F(){const e=document.getElementById("sidebar");if(!e)return;let t=`
    <div class="p-4 border-b border-dark-border">
      <div class="text-xl font-bold text-white flex items-center gap-2">🤖 MBIO</div>
      <div class="mt-3 space-y-1">
        <div class="flex items-center justify-between mb-2">
          <span class="metric-label">Equity</span>
          <span id="sidebar-equity" class="text-white font-semibold">$0.00</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="metric-label">Today P/L</span>
          <span id="sidebar-pnl" class="pnl-neutral font-semibold">$0.00</span>
        </div>
        <div class="flex items-center gap-2 mt-3 pt-2 border-t border-slate-700">
          <span id="connection-status" class="status-dot disconnected"></span>
          <span id="connection-text" class="text-xs text-slate-400">Connecting...</span>
        </div>
      </div>
    </div>
    <nav class="flex flex-col gap-1 w-full px-2 mt-4 flex-1 overflow-y-auto">
  `,s;for(const i of R){i.category&&i.category!==s&&(t+=`<div class="text-[10px] text-slate-500 font-bold uppercase px-3 py-2 mt-2">${i.category}</div>`,s=i.category);const o=h[i.path]===h[B]?"bg-[#1e232f] text-[#5d3ef2]":"";t+=`<button data-path="${i.path}" class="nav-item p-2 w-full text-left rounded hover:bg-[#1e232f] transition-colors ${o}">${i.label}</button>`}t+="</nav>",e.innerHTML=t,e.querySelectorAll("button[data-path]").forEach(i=>{i.addEventListener("click",()=>{g(i.dataset.path)})})}function G(e){B=e;const t=document.getElementById("sidebar");t&&t.querySelectorAll("button[data-path]").forEach(s=>{const i=h[s.dataset.path],n=h[e];i===n?s.classList.add("bg-[#1e232f]","text-[#5d3ef2]"):s.classList.remove("bg-[#1e232f]","text-[#5d3ef2]")})}l.on("nav:change",({path:e})=>G(e));l.on("sse:overview",e=>{const t=a=>"$"+Math.abs(a).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}),s=a=>a>0?"pnl-positive":a<0?"pnl-negative":"pnl-neutral",i=a=>(a>=0?"+":"-")+t(a),n=document.getElementById("sidebar-equity"),o=document.getElementById("sidebar-pnl");if(n&&(n.textContent=t(e.equity??0)),o){const a=e.unrealized_pnl_usd??0;o.textContent=i(a),o.className=`font-semibold ${s(a)}`}});function V(){F()}let c=null;const I="BINANCE:BTCUSDT";function b(e=I){if(typeof TradingView>"u"){const s=document.getElementById("tv-loading-msg");s&&(s.textContent="Loading chart library..."),setTimeout(()=>b(e),2e3);return}if(c){try{c.remove()}catch{}c=null}const t=document.getElementById("tv-chart-container");if(t){t.innerHTML="";try{c=new TradingView.widget({autosize:!0,symbol:e,interval:"15",timezone:"Etc/UTC",theme:"dark",style:"1",locale:"en",toolbar_bg:"#0b0e11",enable_publishing:!1,hide_top_toolbar:!1,hide_legend:!1,save_image:!0,container_id:"tv-chart-container",backgroundColor:"#0b0e11",gridLineColor:"#1e232f",overrides:{"paneProperties.background":"#0b0e11","paneProperties.vertGridProperties.color":"#1e232f","paneProperties.horzGridProperties.color":"#1e232f","mainSeriesProperties.candleStyle.upColor":"#22c55e","mainSeriesProperties.candleStyle.downColor":"#ef4444","mainSeriesProperties.candleStyle.wickUpColor":"#22c55e","mainSeriesProperties.candleStyle.wickDownColor":"#ef4444"},loading_screen:{backgroundColor:"#0b0e11",foregroundColor:"#94a3b8"}})}catch(s){console.error("[Chart] Init error:",s),t.innerHTML=`
      <div class="flex flex-col items-center justify-center h-full text-slate-500 p-8">
        <div class="text-2xl mb-2">⚠️</div>
        <div class="text-sm font-medium">Chart failed to initialize</div>
        <div class="text-xs mt-1">${s.message}</div>
        <button onclick="window.__retryChart && window.__retryChart()" class="mt-3 px-4 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-500">Retry</button>
      </div>`}}}window.__retryChart=()=>{const e=document.getElementById("tv-pair-selector");b(e?e.value:I)};function X(e){e&&b(e)}function Y(){if(c){try{c.remove()}catch{}c=null}}function K(){return w("/health")}function W(e=100){return w(`/trade-history?limit=${e}`)}const y=e=>"$"+Math.abs(e??0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}),x=e=>((e??0)>=0?"+":"-")+y(e),v=e=>(e??0)>0?"pnl-positive":(e??0)<0?"pnl-negative":"pnl-neutral";let _=[];function J(){return`
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
      <div class="card"><div class="metric-label mb-1">Balance</div><div id="dash-balance" class="metric-value text-white">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Equity</div><div id="dash-equity" class="metric-value text-white">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Deployed</div><div id="dash-deployed" class="metric-value text-white">0%</div></div>
      <div class="card"><div class="metric-label mb-1">Daily PnL</div><div id="dash-daily-pnl" class="metric-value pnl-neutral">0.00%</div></div>
      <div class="card"><div class="metric-label mb-1">Realized PnL</div><div id="dash-realized" class="text-xl font-bold pnl-neutral">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Unrealized PnL</div><div id="dash-unrealized" class="text-xl font-bold pnl-neutral">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Win Rate</div><div id="dash-winrate" class="text-xl font-bold text-white">N/A</div></div>
    </div>`}function Q(){return`
    <div class="card !p-0 mb-6" style="min-height: 500px;">
      <div class="flex items-center justify-between px-4 py-3 border-b border-dark-border">
        <h3 class="text-lg font-bold text-white">📈 Market Chart</h3>
        <select id="tv-pair-selector" class="bg-slate-800 border border-slate-700 text-white text-sm rounded px-3 py-1">
          <option value="BINANCE:BTCUSDT">BTC/USDT</option>
          <option value="BINANCE:ETHUSDT">ETH/USDT</option>
          <option value="BINANCE:SOLUSDT">SOL/USDT</option>
          <option value="BINANCE:XRPUSDT">XRP/USDT</option>
          <option value="BINANCE:AVAXUSDT">AVAX/USDT</option>
          <option value="BINANCE:LINKUSDT">LINK/USDT</option>
          <option value="BINANCE:DOGEUSDT">DOGE/USDT</option>
          <option value="BINANCE:HYPEUSDT">HYPE/USDT</option>
        </select>
      </div>
      <div id="tv-chart-container" style="width:100%; height:480px;">
        <div class="flex items-center justify-center h-full text-slate-500 text-sm" id="tv-loading-msg">Loading chart...</div>
      </div>
    </div>`}function Z(){return`
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="card">
        <div class="metric-label mb-3">System Health</div>
        <div id="dash-health-checks" class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div class="text-slate-500">Loading...</div>
        </div>
      </div>
      <div class="card">
        <div class="flex items-center justify-between mb-3">
          <div class="metric-label">Recent Trades</div>
          <button id="dash-export-csv" class="btn btn-primary text-xs py-1 px-3">Export CSV</button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead><tr class="text-slate-500 border-b border-dark-border">
              <th class="text-left py-2">Time</th>
              <th class="text-left py-2">Asset</th>
              <th class="text-left py-2">Side</th>
              <th class="text-right py-2">PnL</th>
            </tr></thead>
            <tbody id="dash-recent-trades">
              <tr><td colspan="4" class="text-center py-4 text-slate-500">Loading...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>`}function ee(e){const t=(i,n,o)=>{const a=document.getElementById(i);a&&(a.textContent=n,o&&(a.className=o))};t("dash-balance",y(e.balance)),t("dash-equity",y(e.equity)),t("dash-deployed",`${e.deployed_pct??0}%`);const s=document.getElementById("dash-daily-pnl");s&&(s.textContent=`${(e.daily_pnl_pct??0)>=0?"+":""}${(e.daily_pnl_pct??0).toFixed(2)}%`,s.className=`metric-value ${v(e.daily_pnl_pct)}`),t("dash-realized",x(e.realized_pnl_usd),`text-xl font-bold ${v(e.realized_pnl_usd)}`),t("dash-unrealized",x(e.unrealized_pnl_usd),`text-xl font-bold ${v(e.unrealized_pnl_usd)}`),t("dash-winrate",e.win_rate||"N/A","text-xl font-bold text-white")}async function te(){var i;const e=await K(),t=document.getElementById("dash-health-checks");if(!t||!e.ok)return;const s=((i=e.data)==null?void 0:i.checks)||{};t.innerHTML=Object.entries(s).map(([n,o])=>`<div class="flex items-center gap-2">${o?"✅":"❌"} <span class="${o?"text-green-400":"text-red-400"}">${n.replace(/_/g," ")}</span></div>`).join("")}async function ne(){var i;const e=await W(10),t=document.getElementById("dash-recent-trades");if(!t||!e.ok)return;const s=((i=e.data)==null?void 0:i.trades)||[];if(!s.length){t.innerHTML='<tr><td colspan="4" class="text-center py-4 text-slate-500">No recent trades</td></tr>';return}t.innerHTML=s.map(n=>{const o=(n.closed_at||n.opened_at||"").substring(11,19),a=(n.pnl??0)>=0?"text-green-400":"text-red-400";return`<tr class="border-b border-dark-border/50">
      <td class="py-2 text-slate-400">${o}</td>
      <td class="py-2 font-medium">${n.asset}</td>
      <td class="py-2"><span class="badge ${n.side==="BUY"?"badge-buy":"badge-sell"}">${n.side}</span></td>
      <td class="py-2 text-right ${a}">${x(n.pnl)}</td>
    </tr>`}).join("")}function se(e){e.innerHTML=`
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-white">Dashboard Overview</h1>
    </div>
    ${J()}
    ${Q()}
    ${Z()}
  `;const t=document.getElementById("tv-pair-selector");t&&t.addEventListener("change",s=>X(s.target.value)),setTimeout(()=>b((t==null?void 0:t.value)||"BINANCE:BTCUSDT"),200),te(),ne(),_.push(l.on("sse:overview",ee))}function ie(){_.forEach(e=>e()),_=[],Y()}const oe=Object.freeze(Object.defineProperty({__proto__:null,destroy:ie,render:se},Symbol.toStringTag,{value:"Module"}));function ae(e){e.innerHTML=`
    <div class="flex flex-col items-center justify-center h-[60vh] text-slate-500">
      <div class="text-4xl mb-4">🚧</div>
      <h1 class="text-2xl font-bold text-white mb-2">Positions Page</h1>
      <p class="text-sm">Coming in Milestone 4</p>
    </div>
  `}function re(){}const le=Object.freeze(Object.defineProperty({__proto__:null,destroy:re,render:ae},Symbol.toStringTag,{value:"Module"}));function de(e){e.innerHTML=`
    <div class="flex flex-col items-center justify-center h-[60vh] text-slate-500">
      <div class="text-4xl mb-4">🚧</div>
      <h1 class="text-2xl font-bold text-white mb-2">Orders Page</h1>
      <p class="text-sm">Coming in Milestone 4</p>
    </div>
  `}function ce(){}const ue=Object.freeze(Object.defineProperty({__proto__:null,destroy:ce,render:de},Symbol.toStringTag,{value:"Module"}));function pe(e){e.innerHTML=`
    <div class="flex flex-col items-center justify-center h-[60vh] text-slate-500">
      <div class="text-4xl mb-4">🚧</div>
      <h1 class="text-2xl font-bold text-white mb-2">Robots Page</h1>
      <p class="text-sm">Coming in Milestone 4</p>
    </div>
  `}function fe(){}const M=Object.freeze(Object.defineProperty({__proto__:null,destroy:fe,render:pe},Symbol.toStringTag,{value:"Module"}));function me(e){e.innerHTML=`
    <div class="flex flex-col items-center justify-center h-[60vh] text-slate-500">
      <div class="text-4xl mb-4">🚧</div>
      <h1 class="text-2xl font-bold text-white mb-2">Analytics Page</h1>
      <p class="text-sm">Coming in Milestone 4</p>
    </div>
  `}function he(){}const E=Object.freeze(Object.defineProperty({__proto__:null,destroy:he,render:me},Symbol.toStringTag,{value:"Module"}));function be(e){e.innerHTML=`
    <div class="flex flex-col items-center justify-center h-[60vh] text-slate-500">
      <div class="text-4xl mb-4">🚧</div>
      <h1 class="text-2xl font-bold text-white mb-2">Settings Page</h1>
      <p class="text-sm">Coming in Milestone 4</p>
    </div>
  `}function ve(){}const p=Object.freeze(Object.defineProperty({__proto__:null,destroy:ve,render:be},Symbol.toStringTag,{value:"Module"}));console.log("[MBIO v2] Application starting...");r("/dashboard",oe);r("/positions",le);r("/orders",ue);r("/robots",M);r("/create",M);r("/history",E);r("/analytics",E);r("/audit",E);r("/config",p);r("/safety",p);r("/reconcile",p);r("/sysmon",p);r("/alerts",p);V();z().then(e=>{var t;if(!e.ok){console.warn("[MBIO v2] Not authenticated, redirecting to login"),window.location.href="/login";return}console.log("[MBIO v2] User loaded:",(t=e.data)==null?void 0:t.email)});L();var P;(P=document.getElementById("logout-btn"))==null||P.addEventListener("click",H);q();l.dispatch("app:ready",{version:"2.0.0",milestone:3});console.log("[MBIO v2] ✅ Milestone 3 ready");
