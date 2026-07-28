import { useState } from "react";

import {
  useIntelligenceStore
} from "../intelligence/state/intelligenceStore";

const tabs = [
  "Positions",
  "Orders",
  "History",
  "Signals",
  "AI",
  "Logs",
  "Alerts",
];


function PanelContent({
  tab,
  setup,
}: {
  tab: string;
  setup: any;
}) {

switch(tab){

case "Positions":
return (
<div className="space-y-3">

<div className="grid grid-cols-6 rounded-lg border border-white/10 bg-white/5 p-3 text-xs text-white/50">
<span>Asset</span>
<span>Side</span>
<span>Size</span>
<span>Entry</span>
<span>PnL</span>
<span>Liquidation</span>
</div>

<div className="rounded-lg border border-dashed border-white/10 p-6 text-center text-sm text-white/40">
No active positions
</div>

</div>
);


case "Orders":
return (
<div className="rounded-lg border border-dashed border-white/10 p-6 text-center text-sm text-white/40">
Open / Pending / Filled Orders
</div>
);


case "History":
return (
<div className="rounded-lg border border-dashed border-white/10 p-6 text-center text-sm text-white/40">
Execution History and Trade Journal
</div>
);


case "Signals":
return setup ? (

<div className="space-y-3">

<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<div className="flex justify-between">

<span className="text-cyan-400">
{setup.direction}
</span>

<span className="text-white/50">
{setup.symbol}
</span>

</div>

<div className="mt-3 text-white">
{setup.setup}
</div>

<div className="mt-2 text-sm text-white/50">
Confidence {setup.confidence}%
</div>

</div>


<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<div className="text-xs text-white/50">
Reasons
</div>

{setup.reasons.map(
(reason:string)=>(
<div
key={reason}
className="mt-2 text-sm text-white/70"
>
✓ {reason}
</div>
)
)}

</div>

</div>

) : (

<div className="rounded-lg border border-dashed border-white/10 p-6 text-center text-sm text-white/40">
No active signals
</div>

);


case "AI":
return (
<div className="space-y-3">

<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<div className="text-xs text-white/50">
Market Regime
</div>

<div className="mt-2 text-cyan-400">
{setup ? setup.setup : "Analyzing"}
</div>

</div>


<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<div className="text-xs text-white/50">
Agent Consensus
</div>

<div className="mt-2 text-white">
{
setup
?
`${setup.direction} confidence ${setup.confidence}%`
:
"Waiting for signal"
}
</div>

</div>

</div>
);


case "Logs":
return (
<div className="rounded-lg border border-dashed border-white/10 p-6 text-center text-sm text-white/40">
System / Execution / Strategy Logs
</div>
);


case "Alerts":
return (
<div className="rounded-lg border border-dashed border-white/10 p-6 text-center text-sm text-white/40">
Risk and Execution Alerts
</div>
);


default:
return null;

}

}


export default function BottomWorkspace() {

const [active,setActive]=useState("Positions");

const setup =
useIntelligenceStore(
state=>state.latestSetup
);


return (

<div className="flex h-full flex-col bg-gray-900">


<div className="flex h-11 border-b border-white/10">

{tabs.map((tab)=>(

<button
key={tab}
onClick={()=>setActive(tab)}
className={`px-5 text-sm transition ${
active===tab
?
"border-b-2 border-cyan-400 text-cyan-400"
:
"text-white/50 hover:text-white"
}`}
>

{tab}

</button>

))}

</div>


<div className="flex-1 overflow-auto p-4">

<PanelContent
tab={active}
setup={setup}
/>

</div>


</div>

);

}
