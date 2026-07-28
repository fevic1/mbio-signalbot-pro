interface RiskReviewProps {
  onDeploy: () => void;
  onBack: () => void;
}

export default function RiskReview({
  onDeploy,
  onBack,
}: RiskReviewProps) {

return (

<div className="flex h-full flex-col overflow-y-auto bg-gray-950 p-4">

<h2 className="mb-4 text-sm font-semibold text-white">
Risk Review
</h2>


<div className="space-y-2">

{[
"Margin Available",
"Position Size",
"Exchange Limits",
"Tick Size",
"Minimum Order",
"Leverage Allowed",
"Risk Policy",
"AI Verification"
].map(
(item)=>(
<div
key={item}
className="flex justify-between rounded-lg border border-white/10 bg-white/5 px-3 py-3"
>

<span className="text-sm text-white/60">
{item}
</span>

<span className="text-sm text-green-400">
✓ Passed
</span>

</div>
)
)}


</div>


<div className="mt-5 rounded-lg border border-white/10 bg-white/5 p-4">

<div className="text-xs text-white/50">
Risk Score
</div>

<div className="mt-2 text-xl font-semibold text-green-400">
LOW
</div>

</div>


<div className="mt-5 grid grid-cols-2 gap-3">

<button
onClick={onBack}
className="rounded-lg border border-white/10 py-3 text-white/60"
>
Back
</button>


<button
onClick={onDeploy}
className="rounded-lg bg-cyan-500/20 py-3 text-cyan-400"
>
Deploy
</button>


</div>


</div>

);

}
