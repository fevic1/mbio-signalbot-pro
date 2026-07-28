interface DCABuilderProps {
  onContinue: () => void;
}

export default function DCABuilder({
onContinue,
}:DCABuilderProps){

return (

<div className="flex h-full flex-col overflow-y-auto bg-gray-950 p-4">

<h2 className="mb-4 text-sm font-semibold text-white">
DCA Builder
</h2>


<div className="space-y-3">

{[
"Entry Price",
"Investment",
"Safety Orders",
"Price Step",
"Volume Scale",
"Step Scale",
"Take Profit",
"Trailing TP",
"Stop Loss"
].map(
(field)=>(
<div key={field}>

<label className="mb-1 block text-xs text-white/50">
{field}
</label>

<input
className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white"
/>

</div>
)
)}


<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<h3 className="text-sm text-white">
Live Preview
</h3>

<div className="mt-3 text-xs text-white/50 space-y-1">

<div>Average Entry</div>
<div>Maximum Capital</div>
<div>Worst Drawdown</div>
<div>Expected Orders</div>
<div>Risk Level</div>

</div>

</div>


<button
onClick={onContinue}
className="rounded-lg bg-cyan-500/20 py-3 text-cyan-400"
>
Continue to Risk Review
</button>


</div>

</div>

);

}
