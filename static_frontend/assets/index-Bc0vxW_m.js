(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const i of document.querySelectorAll('link[rel="modulepreload"]'))n(i);new MutationObserver(i=>{for(const a of i)if(a.type==="childList")for(const l of a.addedNodes)l.tagName==="LINK"&&l.rel==="modulepreload"&&n(l)}).observe(document,{childList:!0,subtree:!0});function s(i){const a={};return i.integrity&&(a.integrity=i.integrity),i.referrerPolicy&&(a.referrerPolicy=i.referrerPolicy),i.crossOrigin==="use-credentials"?a.credentials="include":i.crossOrigin==="anonymous"?a.credentials="omit":a.credentials="same-origin",a}function n(i){if(i.ep)return;i.ep=!0;const a=s(i);fetch(i.href,a)}})();const f=new EventTarget,o={dispatch(t,e){f.dispatchEvent(new CustomEvent(t,{detail:e}))},on(t,e){const s=n=>e(n.detail);return f.addEventListener(t,s),()=>f.removeEventListener(t,s)},once(t,e){const s=n=>{e(n.detail),f.removeEventListener(t,s)};f.addEventListener(t,s)}};let p=null,_=null;const ut=5e3,mt="/api/dashboard/stream";function K(t,e){const s=document.getElementById("connection-status"),n=document.getElementById("connection-text");s&&(s.className=`status-dot ${t}`),n&&(n.textContent=e)}function bt(t){try{const e=JSON.parse(t);if(e.error)return;o.dispatch("sse:overview",{balance:e.balance??0,equity:e.equity??0,deployed_pct:e.deployed_pct??0,daily_pnl_pct:e.daily_pnl_pct??0,realized_pnl_usd:e.realized_pnl_usd??0,unrealized_pnl_usd:e.unrealized_pnl_usd??0,win_rate:e.win_rate??"N/A"}),Array.isArray(e.positions)&&o.dispatch("sse:positions",e.positions),Array.isArray(e.grids)&&o.dispatch("sse:grids",e.grids);const s=document.getElementById("header-equity"),n=document.getElementById("header-pnl");if(s&&(s.textContent=`$${(e.equity??0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2})}`),n){const i=e.unrealized_pnl_usd??0;n.textContent=`${i>=0?"+":""}$${Math.abs(i).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2})}`,n.className=`text-sm font-semibold ${i>0?"pnl-positive":i<0?"pnl-negative":"pnl-neutral"}`}}catch(e){console.error("[SSE] Parse error:",e)}}function st(){p&&(p.close(),p=null),_&&(clearTimeout(_),_=null),p=new EventSource(mt,{withCredentials:!0}),p.onopen=()=>{K("connected","Live"),o.dispatch("sse:connected",{})},p.onmessage=t=>bt(t.data),p.onerror=()=>{K("disconnected","Reconnecting..."),o.dispatch("sse:disconnected",{}),p.close(),p=null,_=setTimeout(st,ut)}}const yt="/api/dashboard";async function nt(t,e={}){const s=t.startsWith("http")?t:`${yt}${t}`,n={credentials:"include",...e};n.body&&typeof n.body=="object"&&(n.headers={"Content-Type":"application/json",...n.headers||{}},n.body=JSON.stringify(n.body));try{const i=await fetch(s,n);let a=null;try{a=await i.json()}catch{}return{ok:i.ok,status:i.status,data:a,error:!i.ok&&(a!=null&&a.detail)?a.detail:null}}catch(i){return{ok:!1,status:0,data:null,error:`Network error: ${i.message}`}}}function B(t){return nt(t,{method:"GET"})}function I(t,e){return nt(t,{method:"POST",body:e})}let g=null;async function gt(){const t=await B("/auth/me");if(t.ok&&t.data){t.data;const e=document.getElementById("user-name"),s=document.getElementById("user-role");e&&(e.textContent=t.data.name||t.data.email||"User"),s&&(s.textContent=(t.data.role||"USER").toUpperCase()),o.dispatch("auth:user-loaded",t.data)}return t}async function ft(){await I("/auth/logout",{}),window.location.href="/login"}function C(t,e,s){g={endpoint:t,payload:e,description:s},document.getElementById("otp-description").textContent=s,document.getElementById("otp-input").value="",document.getElementById("otp-error").style.display="none",document.getElementById("otp-modal").classList.remove("hidden"),document.getElementById("otp-modal").classList.add("flex"),document.getElementById("otp-input").focus()}function U(){g=null,document.getElementById("otp-modal").classList.add("hidden"),document.getElementById("otp-modal").classList.remove("flex")}async function vt(){const t=await I("/auth/otp/request",{});return t.ok||o.dispatch("toast",{message:t.error||"Failed to send OTP",type:"error"}),t}async function ht(t){var s;if(!g)return{ok:!1,error:"No pending action"};if(!t||t.length!==6)return{ok:!1,error:"Enter 6-digit OTP"};const e=document.getElementById("otp-confirm-btn");e&&(e.disabled=!0,e.textContent="Executing...");try{const n=await I(g.endpoint,{...g.payload,otp:t});if(n.ok)U(),o.dispatch("toast",{message:((s=n.data)==null?void 0:s.message)||"Action completed",type:"success"}),o.dispatch("action:completed",{endpoint:g.endpoint,result:n});else{const i=document.getElementById("otp-error");i&&(i.textContent=n.error||"Action failed",i.style.display="block")}return n}finally{e&&(e.disabled=!1,e.textContent="Confirm")}}const Q={success:"bg-green-600 border-green-500",error:"bg-red-600 border-red-500",warning:"bg-yellow-600 border-yellow-500",info:"bg-blue-600 border-blue-500"},Z={success:"✅",error:"❌",warning:"⚠️",info:"📢"};function xt(t,e="info",s=3e3){const n=document.getElementById("toast-container");if(!n)return;const i=document.createElement("div");i.className=`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border ${Q[e]||Q.info} text-white min-w-[300px] animate-slide-in`,i.innerHTML=`
    <span class="text-xl">${Z[e]||Z.info}</span>
    <span class="flex-1 font-medium text-sm">${t}</span>
    <button class="text-white/70 hover:text-white">&times;</button>
  `,i.querySelector("button").addEventListener("click",()=>i.remove()),n.appendChild(i),setTimeout(()=>{i.style.opacity="0",i.style.transform="translateX(100%)",i.style.transition="all 0.3s ease",setTimeout(()=>i.remove(),300)},s)}o.on("toast",({message:t,type:e,duration:s})=>{xt(t,e,s)});function wt(t){return I("/emergency-stop",{otp:t})}function Et(){const t=document.getElementById("otp-confirm-btn"),e=document.getElementById("otp-resend-btn"),s=document.getElementById("otp-cancel-btn"),n=document.getElementById("otp-input");t&&t.addEventListener("click",async()=>{var a;const i=((a=n==null?void 0:n.value)==null?void 0:a.trim())||"";await ht(i)}),e&&e.addEventListener("click",async()=>{e.disabled=!0,e.textContent="Sending...";try{await vt(),o.dispatch("toast",{message:"New OTP code sent",type:"info"})}finally{e.disabled=!1,e.textContent="Resend"}}),s&&s.addEventListener("click",U),n&&n.addEventListener("keydown",i=>{i.key==="Enter"&&(i.preventDefault(),t==null||t.click())}),document.addEventListener("keydown",i=>{if(i.key==="Escape"){const a=document.getElementById("otp-modal");a&&!a.classList.contains("hidden")&&U();const l=document.getElementById("estop-modal");l&&!l.classList.contains("hidden")&&Y()}})}function Y(){const t=document.getElementById("estop-modal");t&&(t.classList.add("hidden"),t.classList.remove("flex"));const e=document.getElementById("estop-confirm-input");e&&(e.value="");const s=document.getElementById("estop-error");s&&(s.style.display="none")}function _t(){const t=document.getElementById("estop-modal");t&&(t.classList.remove("hidden"),t.classList.add("flex"));const e=document.getElementById("estop-confirm-input");e&&(e.value="",e.focus());const s=document.getElementById("estop-error");s&&(s.style.display="none")}async function Lt(){var i;const t=document.getElementById("estop-confirm-input"),e=document.getElementById("estop-error"),s=document.getElementById("estop-confirm-btn");if((((i=t==null?void 0:t.value)==null?void 0:i.trim())||"")!=="STOP"){e&&(e.textContent="Type STOP exactly to confirm",e.style.display="block");return}s&&(s.disabled=!0,s.textContent="EXECUTING...");try{const a=await wt("000000");a.ok?(Y(),o.dispatch("toast",{message:"🚨 EMERGENCY STOP EXECUTED — All positions closed",type:"error",duration:8e3}),o.dispatch("action:completed",{endpoint:"/emergency-stop",result:a})):e&&(e.textContent=a.error||"Emergency stop failed",e.style.display="block")}catch(a){e&&(e.textContent=`Network error: ${a.message}`,e.style.display="block")}finally{s&&(s.disabled=!1,s.textContent="EXECUTE STOP")}}function St(){const t=document.getElementById("estop-confirm-btn"),e=document.getElementById("estop-cancel-btn"),s=document.getElementById("estop-confirm-input");t&&t.addEventListener("click",Lt),e&&e.addEventListener("click",Y),s&&s.addEventListener("keydown",n=>{n.key==="Enter"&&(n.preventDefault(),t==null||t.click())}),window.__openEstopModal=_t}function $t(){o.on("action:completed",({endpoint:t})=>{console.log(`[Modal] Action completed: ${t}`),(t.includes("/grid/open")||t.includes("/dca/open"))&&o.dispatch("toast",{message:"Bot created successfully",type:"success"}),(t.includes("/order/market")||t.includes("/order/limit"))&&o.dispatch("toast",{message:"Order submitted successfully",type:"success"}),t.includes("/emergency-stop")})}function kt(){Et(),St(),$t(),console.log("[Modals] OTP + Emergency Stop wired (dashboard-native)")}const V={};let L=null;function c(t,e){V[t]=e}function D(t,e=!0){const s=t.startsWith("/")?t:`/${t}`,n=V[s];if(!n){console.warn(`[Router] No route registered for: ${s}`);return}e&&window.location.pathname!==s&&history.pushState({path:s},"",s);const i=document.getElementById("page-container");i&&(L&&typeof L.destroy=="function"&&L.destroy(),i.innerHTML="",L=n,typeof n.render=="function"?n.render(i):typeof n=="function"&&n(i),o.dispatch("nav:change",{path:s}))}function Tt(){window.addEventListener("popstate",s=>{var i;const n=((i=s.state)==null?void 0:i.path)||"/dashboard";D(n,!1)});const t=window.location.pathname,e=V[t]?t:"/dashboard";D(e,!1)}const Bt=[{category:null,label:"📊 Dashboard",path:"/dashboard",icon:""},{category:"Trading",label:"📈 Positions",path:"/positions",icon:""},{category:null,label:"📝 Order Desk",path:"/orders",icon:""},{category:null,label:"🔲 Grid Bots",path:"/robots",icon:""},{category:null,label:"➕ Create Bot",path:"/create",icon:""},{category:"Analytics",label:"📜 Trade History",path:"/history",icon:""},{category:null,label:"📉 Performance",path:"/analytics",icon:""},{category:null,label:"📋 Audit Log",path:"/audit",icon:""},{category:"System",label:"⚙ Config",path:"/config",icon:""},{category:null,label:"🛡 Safety",path:"/safety",icon:""},{category:null,label:"🔧 Reconcile",path:"/reconcile",icon:""},{category:null,label:"🖥 System",path:"/sysmon",icon:""},{category:null,label:"🔔 Alerts",path:"/alerts",icon:""}],S={"/dashboard":"/dashboard","/positions":"/positions","/orders":"/orders","/robots":"/robots","/create":"/robots","/history":"/history","/analytics":"/analytics","/audit":"/audit","/config":"/config","/safety":"/config","/reconcile":"/config","/sysmon":"/config","/alerts":"/config"};let it="/dashboard";function It(){const t=document.getElementById("sidebar");if(!t)return;let e=`
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
  `,s;for(const n of Bt){n.category&&n.category!==s&&(e+=`<div class="text-[10px] text-slate-500 font-bold uppercase px-3 py-2 mt-2">${n.category}</div>`,s=n.category);const a=S[n.path]===S[it]?"bg-[#1e232f] text-[#5d3ef2]":"";e+=`<button data-path="${n.path}" class="nav-item p-2 w-full text-left rounded hover:bg-[#1e232f] transition-colors ${a}">${n.label}</button>`}e+="</nav>",t.innerHTML=e,t.querySelectorAll("button[data-path]").forEach(n=>{n.addEventListener("click",()=>{D(n.dataset.path)})})}function Ct(t){it=t;const e=document.getElementById("sidebar");e&&e.querySelectorAll("button[data-path]").forEach(s=>{const n=S[s.dataset.path],i=S[t];n===i?s.classList.add("bg-[#1e232f]","text-[#5d3ef2]"):s.classList.remove("bg-[#1e232f]","text-[#5d3ef2]")})}o.on("nav:change",({path:t})=>Ct(t));o.on("sse:overview",t=>{const e=l=>"$"+Math.abs(l).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}),s=l=>l>0?"pnl-positive":l<0?"pnl-negative":"pnl-neutral",n=l=>(l>=0?"+":"-")+e(l),i=document.getElementById("sidebar-equity"),a=document.getElementById("sidebar-pnl");if(i&&(i.textContent=e(t.equity??0)),a){const l=t.unrealized_pnl_usd??0;a.textContent=n(l),a.className=`font-semibold ${s(l)}`}});function At(){It()}let y=null;const at="BINANCE:BTCUSDT";function A(t=at){if(typeof TradingView>"u"){const s=document.getElementById("tv-loading-msg");s&&(s.textContent="Loading chart library..."),setTimeout(()=>A(t),2e3);return}if(y){try{y.remove()}catch{}y=null}const e=document.getElementById("tv-chart-container");if(e){e.innerHTML="";try{y=new TradingView.widget({autosize:!0,symbol:t,interval:"15",timezone:"Etc/UTC",theme:"dark",style:"1",locale:"en",toolbar_bg:"#0b0e11",enable_publishing:!1,hide_top_toolbar:!1,hide_legend:!1,save_image:!0,container_id:"tv-chart-container",backgroundColor:"#0b0e11",gridLineColor:"#1e232f",overrides:{"paneProperties.background":"#0b0e11","paneProperties.vertGridProperties.color":"#1e232f","paneProperties.horzGridProperties.color":"#1e232f","mainSeriesProperties.candleStyle.upColor":"#22c55e","mainSeriesProperties.candleStyle.downColor":"#ef4444","mainSeriesProperties.candleStyle.wickUpColor":"#22c55e","mainSeriesProperties.candleStyle.wickDownColor":"#ef4444"},loading_screen:{backgroundColor:"#0b0e11",foregroundColor:"#94a3b8"}})}catch(s){console.error("[Chart] Init error:",s),e.innerHTML=`
      <div class="flex flex-col items-center justify-center h-full text-slate-500 p-8">
        <div class="text-2xl mb-2">⚠️</div>
        <div class="text-sm font-medium">Chart failed to initialize</div>
        <div class="text-xs mt-1">${s.message}</div>
        <button onclick="window.__retryChart && window.__retryChart()" class="mt-3 px-4 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-500">Retry</button>
      </div>`}}}window.__retryChart=()=>{const t=document.getElementById("tv-pair-selector");A(t?t.value:at)};function Pt(t){t&&A(t)}function Mt(){if(y){try{y.remove()}catch{}y=null}}const Ot="/api";async function u(t,e={}){const s=`${Ot}${t}`,n=await fetch(s,{credentials:"include",...e,headers:{"Content-Type":"application/json",...e.headers}});if(!n.ok)throw new Error(`API error: ${n.statusText}`);return n.json()}async function lt(){return u("/dashboard/health")}async function zt(){return u("/dashboard/analytics")}async function X(t=100){return u(`/dashboard/trade-history?limit=${t}`)}async function Nt(){return u("/system/status")}async function Ut(){return u("/config/current")}async function ot(){return u("/config/assets")}async function Dt(){return u("/signals/orphaned")}async function Ft(t=100){return u(`/dashboard/audit-log?limit=${t}`)}async function Ht(){return u("/dashboard/alert-config")}const F=t=>"$"+Math.abs(t??0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}),H=t=>((t??0)>=0?"+":"-")+F(t),O=t=>(t??0)>0?"pnl-positive":(t??0)<0?"pnl-negative":"pnl-neutral";let j=[];function jt(){return`
    <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
      <div class="card"><div class="metric-label mb-1">Balance</div><div id="dash-balance" class="metric-value text-white">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Equity</div><div id="dash-equity" class="metric-value text-white">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Deployed</div><div id="dash-deployed" class="metric-value text-white">0%</div></div>
      <div class="card"><div class="metric-label mb-1">Daily PnL</div><div id="dash-daily-pnl" class="metric-value pnl-neutral">0.00%</div></div>
      <div class="card"><div class="metric-label mb-1">Realized PnL</div><div id="dash-realized" class="text-xl font-bold pnl-neutral">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Unrealized PnL</div><div id="dash-unrealized" class="text-xl font-bold pnl-neutral">$0.00</div></div>
      <div class="card"><div class="metric-label mb-1">Win Rate</div><div id="dash-winrate" class="text-xl font-bold text-white">N/A</div></div>
    </div>`}function Rt(){return`
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
    </div>`}function qt(){return`
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
    </div>`}function Gt(t){const e=(n,i,a)=>{const l=document.getElementById(n);l&&(l.textContent=i,a&&(l.className=a))};e("dash-balance",F(t.balance)),e("dash-equity",F(t.equity)),e("dash-deployed",`${t.deployed_pct??0}%`);const s=document.getElementById("dash-daily-pnl");s&&(s.textContent=`${(t.daily_pnl_pct??0)>=0?"+":""}${(t.daily_pnl_pct??0).toFixed(2)}%`,s.className=`metric-value ${O(t.daily_pnl_pct)}`),e("dash-realized",H(t.realized_pnl_usd),`text-xl font-bold ${O(t.realized_pnl_usd)}`),e("dash-unrealized",H(t.unrealized_pnl_usd),`text-xl font-bold ${O(t.unrealized_pnl_usd)}`),e("dash-winrate",t.win_rate||"N/A","text-xl font-bold text-white")}async function Yt(){var n;const t=await lt(),e=document.getElementById("dash-health-checks");if(!e||!t.ok)return;const s=((n=t.data)==null?void 0:n.checks)||{};e.innerHTML=Object.entries(s).map(([i,a])=>`<div class="flex items-center gap-2">${a?"✅":"❌"} <span class="${a?"text-green-400":"text-red-400"}">${i.replace(/_/g," ")}</span></div>`).join("")}async function Vt(){var n;const t=await X(10),e=document.getElementById("dash-recent-trades");if(!e||!t.ok)return;const s=((n=t.data)==null?void 0:n.trades)||[];if(!s.length){e.innerHTML='<tr><td colspan="4" class="text-center py-4 text-slate-500">No recent trades</td></tr>';return}e.innerHTML=s.map(i=>{const a=(i.closed_at||i.opened_at||"").substring(11,19),l=(i.pnl??0)>=0?"text-green-400":"text-red-400";return`<tr class="border-b border-dark-border/50">
      <td class="py-2 text-slate-400">${a}</td>
      <td class="py-2 font-medium">${i.asset}</td>
      <td class="py-2"><span class="badge ${i.side==="BUY"?"badge-buy":"badge-sell"}">${i.side}</span></td>
      <td class="py-2 text-right ${l}">${H(i.pnl)}</td>
    </tr>`}).join("")}function Xt(t){t.innerHTML=`
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-white">Dashboard Overview</h1>
    </div>
    ${jt()}
    ${Rt()}
    ${qt()}
  `;const e=document.getElementById("tv-pair-selector");e&&e.addEventListener("change",s=>Pt(s.target.value)),setTimeout(()=>A((e==null?void 0:e.value)||"BINANCE:BTCUSDT"),200),Yt(),Vt(),j.push(o.on("sse:overview",Gt))}function Wt(){j.forEach(t=>t()),j=[],Mt()}const Jt=Object.freeze(Object.defineProperty({__proto__:null,destroy:Wt,render:Xt},Symbol.toStringTag,{value:"Module"})),Kt=t=>"$"+Math.abs(t??0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}),Qt=t=>((t??0)>=0?"+":"-")+Kt(t),z=t=>(t??0)>0?"pnl-positive":(t??0)<0?"pnl-negative":"pnl-neutral";let $=[],k="upnl",v=!1,R="",q=[];function G(){const t=document.getElementById("positions-table"),e=document.getElementById("no-positions");if(!t)return;let s=$.slice();if(R&&(s=s.filter(n=>n.asset===R)),s.sort((n,i)=>{let a=n[k],l=i[k];return typeof a=="string"&&(a=a.toLowerCase(),l=(l||"").toLowerCase()),a<l?v?-1:1:a>l?v?1:-1:0}),!s.length){t.innerHTML="",e&&(e.style.display="block");return}e&&(e.style.display="none"),t.innerHTML=s.map(n=>`
    <tr class="border-b border-dark-border/50 hover:bg-dark-hover/30">
      <td class="py-3 px-4 font-medium text-white">${n.asset}</td>
      <td class="py-3 px-4"><span class="badge ${n.side==="BUY"||n.side==="Long"?"badge-buy":"badge-sell"}">${n.side}</span></td>
      <td class="py-3 px-4">${(n.size??0).toFixed(6)}</td>
      <td class="py-3 px-4">$${(n.entry??0).toLocaleString()}</td>
      <td class="py-3 px-4">$${(n.current??n.entry??0).toLocaleString()}</td>
      <td class="py-3 px-4 ${z(n.upnl)}">${Qt(n.upnl)}</td>
      <td class="py-3 px-4 ${z(n.pnl_pct)}">${(n.pnl_pct??0)>=0?"+":""}${(n.pnl_pct??0).toFixed(2)}%</td>
      <td class="py-3 px-4">$${(n.margin_used??0).toFixed(2)}</td>
      <td class="py-3 px-4">$${(n.liquidation_px??0).toLocaleString()}</td>
      <td class="py-3 px-4">${n.leverage??1}x</td>
      <td class="py-3 px-4 ${z(n.roe)}">${(n.roe??0).toFixed(2)}%</td>
      <td class="py-3 px-4">$${(n.sl??0).toLocaleString()}</td>
      <td class="py-3 px-4 text-slate-400">${n.strategy||"-"}</td>
    </tr>
  `).join("")}function Zt(t){const e=document.getElementById("pos-asset-filter");if(!e||e.options.length>1)return;const s={};t.forEach(n=>{s[n.asset]=!0}),Object.keys(s).sort().forEach(n=>{const i=document.createElement("option");i.value=n,i.textContent=n,e.appendChild(i)})}function te(t){k===t?v=!v:(k=t,v=!1),document.querySelectorAll("#positions-table-head th").forEach(e=>{e.classList.remove("active"),e.dataset.col===t&&e.classList.add("active")}),G()}function ee(t){t.innerHTML=`
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
  `,t.querySelectorAll("th.sortable").forEach(s=>{s.addEventListener("click",()=>te(s.dataset.col))});const e=document.getElementById("pos-asset-filter");e&&e.addEventListener("change",s=>{R=s.target.value,G()}),q.push(o.on("sse:positions",s=>{$=s||[],Zt($),G()}))}function se(){q.forEach(t=>t()),q=[],$=[]}const ne=Object.freeze(Object.defineProperty({__proto__:null,destroy:se,render:ee},Symbol.toStringTag,{value:"Module"}));function ie(t){const e=`?type=${encodeURIComponent(t)}`;return B(`/hyperliquid/assets${e}`)}function ae(t){return B(`/hip4/price?asset=${encodeURIComponent(t)}`)}function le(t,e,s){return B(`/hip4/validate?asset=${encodeURIComponent(t)}&price=${e}&size=${s}`)}let N=[];async function oe(){var e;const t=await ot();if(t.ok&&Array.isArray(t.data))N=t.data;else{const s=await ie("PERP");s.ok&&Array.isArray((e=s.data)==null?void 0:e.assets)&&(N=s.data.assets.map(n=>n.name||n))}["mkt-asset","lmt-asset","sl-asset","ts-asset"].forEach(s=>{const n=document.getElementById(s);n&&(n.innerHTML='<option value="">Select Asset</option>'+N.map(i=>`<option value="${i}">${i}</option>`).join(""))})}function de(t,e){["market","limit","stoplimit","trailing"].forEach(s=>{const n=document.getElementById(`order-${s}`);n&&(n.style.display=s===t?"block":"none")}),document.querySelectorAll(".order-tab-btn").forEach(s=>{s.classList.remove("bg-accent-primary","text-white"),s.classList.add("bg-slate-800","text-slate-400")}),e&&(e.classList.remove("bg-slate-800","text-slate-400"),e.classList.add("bg-accent-primary","text-white"))}async function re(){var n,i,a;const t=(n=document.getElementById("mkt-asset"))==null?void 0:n.value,e=(i=document.getElementById("mkt-side"))==null?void 0:i.value,s=parseFloat(((a=document.getElementById("mkt-size"))==null?void 0:a.value)||"0");if(!t||!e||s<=0){o.dispatch("toast",{message:"Fill all fields correctly",type:"warning"});return}C("/api/dashboard/order/market",{asset:t,side:e,size:s},`Market ${e} ${s} ${t}`)}async function ce(){var a,l,r,d;const t=(a=document.getElementById("lmt-asset"))==null?void 0:a.value,e=(l=document.getElementById("lmt-side"))==null?void 0:l.value,s=parseFloat(((r=document.getElementById("lmt-size"))==null?void 0:r.value)||"0"),n=parseFloat(((d=document.getElementById("lmt-price"))==null?void 0:d.value)||"0");if(!t||!e||s<=0||n<=0){o.dispatch("toast",{message:"Fill all fields correctly",type:"warning"});return}const i=await le(t,n,s);if(!i.success&&!i.valid){o.dispatch("toast",{message:i.error||"HIP-4 validation failed",type:"error"});return}C("/api/dashboard/order/limit",{asset:t,side:e,size:i.rounded_size||s,price:i.rounded_price||n},`Limit ${e} ${s} ${t} @ $${(i.rounded_price||n).toLocaleString()}`)}function pe(t){var e,s;t.innerHTML=`
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
  `,window.__showOrderTab=de,(e=document.getElementById("btn-submit-market"))==null||e.addEventListener("click",re),(s=document.getElementById("btn-submit-limit"))==null||s.addEventListener("click",ce),oe()}function ue(){window.__showOrderTab=null}const me=Object.freeze(Object.defineProperty({__proto__:null,destroy:ue,render:pe},Symbol.toStringTag,{value:"Module"})),be=t=>"$"+Math.abs(t??0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}),ye=t=>((t??0)>=0?"+":"-")+be(t),ge=t=>(t??0)>0?"pnl-positive":(t??0)<0?"pnl-negative":"pnl-neutral";let h=[],T=[];function fe(t){const e=document.getElementById("grids-container"),s=document.getElementById("no-grids");if(e){if(!t.length){e.innerHTML="",s&&(s.style.display="block");return}s&&(s.style.display="none"),e.innerHTML=t.map(n=>`
    <div class="card">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <span class="badge badge-grid">GRID</span>
          <span class="text-lg font-bold text-white">${n.asset}</span>
        </div>
        <span class="text-xs text-slate-400">${n.mode||"RANGE"}</span>
      </div>
      <div class="grid grid-cols-2 gap-3 text-sm">
        <div><span class="metric-label">Range</span><br>$${(n.lower_price??0).toLocaleString()} - $${(n.upper_price??0).toLocaleString()}</div>
        <div><span class="metric-label">Nodes</span><br>${n.nodes_active??0}/${n.nodes_total??0}</div>
        <div><span class="metric-label">Cycles</span><br>${n.cycles??0}</div>
        <div><span class="metric-label">PnL</span><br><span class="${ge(n.realized_pnl)}">${ye(n.realized_pnl)}</span></div>
      </div>
    </div>
  `).join("")}}function ve(t){var e,s;(e=document.getElementById("grid-form"))==null||e.style.setProperty("display",t==="grid"?"block":"none"),(s=document.getElementById("dca-form"))==null||s.style.setProperty("display",t==="dca"?"block":"none")}async function he(){var e,s;const t=(e=document.getElementById("grid-asset"))==null?void 0:e.value;if(t)try{const n=await ae(t);if(n.ok&&((s=n.data)!=null&&s.price)){const i=n.data.price,a=i*.05,l=document.getElementById("grid-lower"),r=document.getElementById("grid-upper");l&&(l.value=(i-a).toFixed(2)),r&&(r.value=(i+a).toFixed(2))}}catch{}}async function xe(){var a,l,r,d,b;const t=(a=document.getElementById("grid-asset"))==null?void 0:a.value,e=parseFloat(((l=document.getElementById("grid-lower"))==null?void 0:l.value)||"0"),s=parseFloat(((r=document.getElementById("grid-upper"))==null?void 0:r.value)||"0"),n=parseFloat(((d=document.getElementById("grid-investment"))==null?void 0:d.value)||"0"),i=parseInt(((b=document.getElementById("grid-nodes"))==null?void 0:b.value)||"10");if(!t||e>=s||n<=0){o.dispatch("toast",{message:"Lower must be < Upper, investment > 0",type:"warning"});return}C("/api/dashboard/grid/open",{asset:t,lower_price:e,upper_price:s,investment_amount:n,num_nodes:i},`Open Grid Bot: ${t} [$${e.toLocaleString()} - $${s.toLocaleString()}]`)}async function we(){var a,l,r,d,b;const t=(a=document.getElementById("dca-asset"))==null?void 0:a.value,e=(l=document.getElementById("dca-side"))==null?void 0:l.value,s=parseFloat(((r=document.getElementById("dca-base-size"))==null?void 0:r.value)||"0"),n=parseFloat(((d=document.getElementById("dca-tp"))==null?void 0:d.value)||"0"),i=parseFloat(((b=document.getElementById("dca-sl"))==null?void 0:b.value)||"0");if(!t||!e||s<=0){o.dispatch("toast",{message:"Fill all DCA fields correctly",type:"warning"});return}C("/api/dashboard/dca/open",{asset:t,side:e,base_order_size:s,take_profit_pct:n,stop_loss_pct:i},`Open DCA Bot: ${e} ${t}`)}async function Ee(){const t=await ot(),e=t.ok&&Array.isArray(t.data)?t.data:["BTC","ETH","SOL","XRP","AVAX"];["grid-asset","dca-asset"].forEach(s=>{const n=document.getElementById(s);n&&(n.innerHTML=e.map(i=>`<option value="${i}">${i}</option>`).join(""))})}function _e(t){const e=document.getElementById("grids-tab-cards"),s=document.getElementById("grids-tab-viz");e&&(e.style.display=t==="cards"?"block":"none"),s&&(s.style.display=t==="viz"?"block":"none"),t==="viz"&&Le()}function Le(){const t=document.getElementById("grid-viz-canvas"),e=document.getElementById("viz-no-data");if(!t)return;const s=t.getContext("2d"),n=t.width=t.parentElement.clientWidth,i=t.height=400;if(s.clearRect(0,0,n,i),!h.length){e&&(e.style.display="block");return}e&&(e.style.display="none");const a=h[0],l=a.lower_price??0,r=a.upper_price??0,d=a.nodes_total??10,b=(r-l)/d,m=40,w=i-m*2;s.strokeStyle="#5d3ef2",s.lineWidth=1,s.font="11px monospace",s.fillStyle="#94a3b8";for(let E=0;E<=d;E++){const pt=l+b*E,M=m+w-E/d*w;s.beginPath(),s.moveTo(m,M),s.lineTo(n-m,M),s.stroke(),s.fillText(`$${pt.toFixed(2)}`,2,M+4)}const J=(l+r)/2,P=m+w-(J-l)/(r-l)*w;s.strokeStyle="#22c55e",s.lineWidth=2,s.beginPath(),s.moveTo(m,P),s.lineTo(n-m,P),s.stroke(),s.fillStyle="#22c55e",s.fillText(`← Current ~$${J.toFixed(2)}`,n-m+5,P+4)}function Se(t){var e,s;t.innerHTML=`
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
  `,window.__showCreateForm=ve,window.__autoFillGrid=he,window.__showGridsTab=_e,(e=document.getElementById("btn-submit-grid"))==null||e.addEventListener("click",xe),(s=document.getElementById("btn-submit-dca"))==null||s.addEventListener("click",we),Ee(),T.push(o.on("sse:grids",n=>{h=n||[],fe(h)})),T.push(o.on("sse:positions",n=>{}))}function $e(){T.forEach(t=>t()),T=[],h=[],window.__showCreateForm=null,window.__autoFillGrid=null,window.__showGridsTab=null}const dt=Object.freeze(Object.defineProperty({__proto__:null,destroy:$e,render:Se},Symbol.toStringTag,{value:"Module"})),ke=t=>"$"+Math.abs(t??0).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}),rt=t=>((t??0)>=0?"+":"-")+ke(t),tt=t=>(t??0)>0?"pnl-positive":(t??0)<0?"pnl-negative":"pnl-neutral";async function Te(){var i;const t=await X(100),e=document.getElementById("history-table"),s=document.getElementById("no-history");if(!e)return;const n=t.ok&&Array.isArray((i=t.data)==null?void 0:i.trades)?t.data.trades:[];if(!n.length){e.innerHTML="",s&&(s.style.display="block");return}s&&(s.style.display="none"),e.innerHTML=n.map(a=>`<tr class="border-b border-dark-border/50 hover:bg-dark-hover/30">
      <td class="py-2 px-4 text-slate-400 text-xs">${(a.closed_at||a.opened_at||"").substring(0,19).replace("T"," ")}</td>
      <td class="py-2 px-4 font-medium">${a.asset}</td>
      <td class="py-2 px-4"><span class="badge ${a.side==="BUY"?"badge-buy":"badge-sell"}">${a.side}</span></td>
      <td class="py-2 px-4 text-right">${(a.size??0).toFixed(6)}</td>
      <td class="py-2 px-4 text-right">$${(a.entry_price??0).toLocaleString()}</td>
      <td class="py-2 px-4 text-right">$${(a.exit_price??0).toLocaleString()}</td>
      <td class="py-2 px-4 text-right ${tt(a.pnl)}">${rt(a.pnl)}</td>
      <td class="py-2 px-4 text-right ${tt(a.pnl_pct)}">${(a.pnl_pct??0)>=0?"+":""}${(a.pnl_pct??0).toFixed(2)}%</td>
      <td class="py-2 px-4 text-slate-400 text-xs">${a.strategy||"-"}</td>
    </tr>`).join("")}async function Be(){const t=await zt();if(!t.ok||!t.data)return;const e=t.data,s=(n,i)=>{const a=document.getElementById(n);a&&(a.textContent=i)};s("an-total-pnl",rt(e.total_pnl)),s("an-winrate",`${(e.win_rate??0).toFixed(1)}%`),s("an-sharpe",(e.sharpe_ratio??0).toFixed(2)),s("an-max-dd",`${(e.max_drawdown??0).toFixed(2)}%`),s("an-pf",(e.profit_factor??0).toFixed(2)),s("an-trades",e.total_trades??0)}function Ie(){X(1e3).then(t=>{var r;if(!t.ok||!Array.isArray((r=t.data)==null?void 0:r.trades))return;const e=["Time","Asset","Side","Size","Entry","Exit","PnL","PnL%","Strategy"],s=t.data.trades.map(d=>[d.closed_at||d.opened_at||"",d.asset,d.side,d.size,d.entry_price,d.exit_price,d.pnl,d.pnl_pct,d.strategy]),n=[e.join(","),...s.map(d=>d.join(","))].join(`
`),i=new Blob([n],{type:"text/csv"}),a=URL.createObjectURL(i),l=document.createElement("a");l.href=a,l.download=`mbio_trades_${new Date().toISOString().slice(0,10)}.csv`,l.click(),URL.revokeObjectURL(a),o.dispatch("toast",{message:"CSV exported successfully",type:"success"})})}function Ce(t){var e;t.innerHTML=`
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-white">📈 Analytics</h1>
      <button class="btn-primary text-sm" id="btn-export-csv">Export CSV</button>
    </div>
    <!-- Performance Metrics -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      <div class="card"><div class="metric-label mb-1">Total PnL</div><div id="an-total-pnl" class="text-xl font-bold pnl-neutral">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Win Rate</div><div id="an-winrate" class="text-xl font-bold text-white">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Sharpe Ratio</div><div id="an-sharpe" class="text-xl font-bold text-white">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Max Drawdown</div><div id="an-max-dd" class="text-xl font-bold text-red-400">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Profit Factor</div><div id="an-pf" class="text-xl font-bold text-white">Loading...</div></div>
      <div class="card"><div class="metric-label mb-1">Total Trades</div><div id="an-trades" class="text-xl font-bold text-white">Loading...</div></div>
    </div>
    <!-- Charts Placeholder (Chart.js integration in M5) -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <div class="card"><div class="metric-label mb-3">Daily PnL Chart</div><div id="daily-pnl-chart" class="h-48 flex items-center justify-center text-slate-500 text-sm">Chart.js integration pending</div></div>
      <div class="card"><div class="metric-label mb-3">Monthly Returns Heatmap</div><div id="monthly-heatmap" class="h-48 flex items-center justify-center text-slate-500 text-sm">Chart.js integration pending</div></div>
    </div>
    <!-- Trade History Table -->
    <div class="card !p-0 overflow-x-auto">
      <div class="px-4 py-3 border-b border-dark-border font-bold text-white">Trade History</div>
      <table class="w-full text-xs">
        <thead><tr class="text-slate-500 border-b border-dark-border uppercase tracking-wider">
          <th class="text-left py-2 px-4">Time</th><th class="text-left py-2 px-4">Asset</th>
          <th class="text-left py-2 px-4">Side</th><th class="text-right py-2 px-4">Size</th>
          <th class="text-right py-2 px-4">Entry</th><th class="text-right py-2 px-4">Exit</th>
          <th class="text-right py-2 px-4">PnL</th><th class="text-right py-2 px-4">PnL%</th>
          <th class="text-left py-2 px-4">Strategy</th>
        </tr></thead>
        <tbody id="history-table">
          <tr><td colspan="9" class="text-center py-8 text-slate-500">Loading trades...</td></tr>
        </tbody>
      </table>
      <div id="no-history" class="hidden text-center py-8 text-slate-500">No trade history</div>
    </div>
  `,(e=document.getElementById("btn-export-csv"))==null||e.addEventListener("click",Ie),Te(),Be()}function Ae(){}const W=Object.freeze(Object.defineProperty({__proto__:null,destroy:Ae,render:Ce},Symbol.toStringTag,{value:"Module"}));function Pe(t,e){["config","safety","reconcile","sysmon","audit","alerts"].forEach(s=>{const n=document.getElementById(`settings-${s}`);n&&(n.style.display=s===t?"block":"none")}),document.querySelectorAll(".settings-tab-btn").forEach(s=>{s.classList.remove("bg-accent-primary","text-white"),s.classList.add("bg-slate-800","text-slate-400")}),e&&(e.classList.remove("bg-slate-800","text-slate-400"),e.classList.add("bg-accent-primary","text-white")),t==="config"&&ct(),t==="safety"&&Me(),t==="reconcile"&&Oe(),t==="sysmon"&&ze(),t==="audit"&&Ne(),t==="alerts"&&Ue()}async function ct(){const t=await Ut(),e=document.getElementById("cfg-content");if(!e)return;if(!t.ok){e.innerHTML='<div class="text-red-400">Failed to load config</div>';return}const s=t.data||{};e.innerHTML=`<pre class="text-xs text-slate-300 overflow-auto max-h-[500px] p-4 bg-slate-900 rounded-lg">${JSON.stringify(s,null,2)}</pre>`}async function Me(){var n,i;const t=await lt(),e=document.getElementById("safe-content");if(!e)return;if(!t.ok){e.innerHTML='<div class="text-red-400">Failed to load safety data</div>';return}const s=((n=t.data)==null?void 0:n.checks)||{};e.innerHTML=`
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      ${Object.entries(s).map(([a,l])=>`
        <div class="card text-center">
          <div class="text-2xl mb-1">${l?"✅":"❌"}</div>
          <div class="text-sm ${l?"text-green-400":"text-red-400"}">${a.replace(/_/g," ")}</div>
        </div>
      `).join("")}
    </div>
    <div class="card border-red-800">
      <h3 class="text-lg font-bold text-red-400 mb-3">⚠️ Emergency Stop</h3>
      <p class="text-sm text-slate-400 mb-4">Close ALL positions and cancel ALL pending orders immediately.</p>
      <button id="btn-emergency-stop" class="btn-danger w-full">EXECUTE EMERGENCY STOP</button>
    </div>
  `,(i=document.getElementById("btn-emergency-stop"))==null||i.addEventListener("click",()=>{typeof window.__openEstopModal=="function"?window.__openEstopModal():o.dispatch("toast",{message:"Emergency stop modal not available",type:"error"})})}async function Oe(){const t=await Dt(),e=document.getElementById("orphan-table"),s=document.getElementById("no-orphans");if(!e)return;const n=t.ok&&Array.isArray(t.data)?t.data:[];if(!n.length){e.innerHTML="",s&&(s.style.display="block");return}s&&(s.style.display="none"),e.innerHTML=n.map(i=>`
    <tr class="border-b border-dark-border/50">
      <td class="py-2 px-4 text-xs text-slate-400">${(i.timestamp||"").substring(0,19)}</td>
      <td class="py-2 px-4 font-medium">${i.asset||"-"}</td>
      <td class="py-2 px-4">${i.signal_type||"-"}</td>
      <td class="py-2 px-4 text-xs text-slate-400">${i.reason||"-"}</td>
    </tr>
  `).join("")}async function ze(){const t=await Nt(),e=document.getElementById("sysmon-content");if(!e)return;if(!t.ok){e.innerHTML='<div class="text-red-400">Failed to load system status</div>';return}const s=t.data||{};e.innerHTML=`
    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
      <div class="card"><div class="metric-label">Status</div><div class="text-lg font-bold ${s.healthy?"text-green-400":"text-red-400"}">${s.healthy?"HEALTHY":"DEGRADED"}</div></div>
      <div class="card"><div class="metric-label">Uptime</div><div class="text-lg font-bold text-white">${s.uptime||"N/A"}</div></div>
      <div class="card"><div class="metric-label">Auto Trading</div><div class="text-lg font-bold ${s.auto_trade?"text-green-400":"text-yellow-400"}">${s.auto_trade?"ENABLED":"DISABLED"}</div></div>
    </div>
  `}async function Ne(){var n;const t=await Ft({limit:50}),e=document.getElementById("audit-table");if(!e)return;const s=t.ok&&Array.isArray((n=t.data)==null?void 0:n.logs)?t.data.logs:[];e.innerHTML=s.length?s.map(i=>`
    <tr class="border-b border-dark-border/50">
      <td class="py-2 px-4 text-xs text-slate-400">${(i.timestamp||"").substring(0,19)}</td>
      <td class="py-2 px-4 font-medium">${i.action||"-"}</td>
      <td class="py-2 px-4 text-xs">${i.user||"-"}</td>
      <td class="py-2 px-4 text-xs text-slate-400">${i.details||"-"}</td>
    </tr>
  `).join(""):'<tr><td colspan="4" class="text-center py-4 text-slate-500">No audit entries</td></tr>'}async function Ue(){const t=await Ht(),e=document.getElementById("alerts-content");if(e){if(!t.ok){e.innerHTML='<div class="text-red-400">Failed to load alert config</div>';return}e.innerHTML=`<pre class="text-xs text-slate-300 overflow-auto max-h-[400px] p-4 bg-slate-900 rounded-lg">${JSON.stringify(t.data,null,2)}</pre>`}}function De(t){t.innerHTML=`
    <div class="mb-6"><h1 class="text-2xl font-bold text-white">⚙️ Settings</h1></div>
    <!-- Tab Buttons -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-accent-primary text-white" onclick="window.__showSettingsTab('config', this)">Config</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('safety', this)">Safety</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('reconcile', this)">Reconcile</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('sysmon', this)">System</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('audit', this)">Audit Log</button>
      <button class="settings-tab-btn px-4 py-2 rounded-lg text-sm font-medium bg-slate-800 text-slate-400" onclick="window.__showSettingsTab('alerts', this)">Alerts</button>
    </div>
    <!-- Tab Content -->
    <div id="settings-config"><div id="cfg-content" class="card">Loading config...</div></div>
    <div id="settings-safety" style="display:none;"><div id="safe-content" class="card">Loading safety...</div></div>
    <div id="settings-reconcile" style="display:none;">
      <div class="card !p-0 overflow-x-auto">
        <div class="px-4 py-3 border-b border-dark-border font-bold text-white">Orphaned Signals</div>
        <table class="w-full text-xs"><thead><tr class="text-slate-500 border-b border-dark-border"><th class="text-left py-2 px-4">Time</th><th class="text-left py-2 px-4">Asset</th><th class="text-left py-2 px-4">Type</th><th class="text-left py-2 px-4">Reason</th></tr></thead>
        <tbody id="orphan-table"><tr><td colspan="4" class="text-center py-4 text-slate-500">Loading...</td></tr></tbody></table>
        <div id="no-orphans" class="hidden text-center py-4 text-slate-500">No orphaned signals</div>
      </div>
    </div>
    <div id="settings-sysmon" style="display:none;"><div id="sysmon-content" class="card">Loading system status...</div></div>
    <div id="settings-audit" style="display:none;">
      <div class="card !p-0 overflow-x-auto">
        <div class="px-4 py-3 border-b border-dark-border font-bold text-white">Audit Log</div>
        <table class="w-full text-xs"><thead><tr class="text-slate-500 border-b border-dark-border"><th class="text-left py-2 px-4">Time</th><th class="text-left py-2 px-4">Action</th><th class="text-left py-2 px-4">User</th><th class="text-left py-2 px-4">Details</th></tr></thead>
        <tbody id="audit-table"><tr><td colspan="4" class="text-center py-4 text-slate-500">Loading...</td></tr></tbody></table>
      </div>
    </div>
    <div id="settings-alerts" style="display:none;"><div id="alerts-content" class="card">Loading alerts...</div></div>
  `,window.__showSettingsTab=Pe,ct()}function Fe(){window.__showSettingsTab=null}const x=Object.freeze(Object.defineProperty({__proto__:null,destroy:Fe,render:De},Symbol.toStringTag,{value:"Module"}));console.log("[MBIO v2] Application starting...");c("/dashboard",Jt);c("/positions",ne);c("/orders",me);c("/robots",dt);c("/create",dt);c("/history",W);c("/analytics",W);c("/audit",W);c("/config",x);c("/safety",x);c("/reconcile",x);c("/sysmon",x);c("/alerts",x);At();gt().then(t=>{var e;if(!t.ok){console.warn("[MBIO v2] Not authenticated, redirecting to login"),window.location.href="/login";return}console.log("[MBIO v2] User loaded:",(e=t.data)==null?void 0:e.email)});st();var et;(et=document.getElementById("logout-btn"))==null||et.addEventListener("click",ft);kt();Tt();o.dispatch("app:ready",{version:"2.0.0",milestone:5});console.log("[MBIO v2] ✅ Milestone 3 ready");
