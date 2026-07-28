interface GridBuilderProps {
  onContinue: () => void;
}

export default function GridBuilder({
  onContinue,
}: GridBuilderProps) {

return (

<div className="flex h-full flex-col overflow-y-auto bg-gray-950 p-4">

<h2 className="mb-4 text-sm font-semibold text-white">
GRID Builder
</h2>


<div className="space-y-3">


{[
"Direction",
"Upper Price",
"Lower Price",
"Grid Count",
"Spacing Mode",
"Capital",
"Leverage",
"Margin",
"Stop Loss",
"Take Profit",
"Maximum Drawdown"
].map(
(field)=>(
<div key={field}>

<label className="mb-1 block text-xs text-white/50">
{field}
</label>

<input
className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
/>

</div>
)
)}


<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<h3 className="text-sm text-white">
Live Preview
</h3>

<div className="mt-3 space-y-1 text-xs text-white/50">

<div>Estimated Orders</div>
<div>Required Margin</div>
<div>Liquidation Price</div>
<div>Expected Grid Profit</div>
<div>Estimated Fees</div>
<div>Risk Score</div>

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
