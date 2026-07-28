interface DeployConfirmationProps {
  onDeploy: () => void;
  onBack: () => void;
}

export default function DeployConfirmation({
  onDeploy,
  onBack,
}: DeployConfirmationProps) {

return (

<div className="flex h-full flex-col overflow-y-auto bg-gray-950 p-4">

<h2 className="mb-4 text-sm font-semibold text-white">
Deploy Confirmation
</h2>


<div className="space-y-3">


<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<div className="text-xs text-white/50">
Strategy
</div>

<div className="mt-1 text-white">
GRID Bot
</div>

</div>


<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<div className="text-xs text-white/50">
Validation Status
</div>

<div className="mt-2 space-y-2 text-sm">

<div className="flex justify-between">
<span className="text-white/60">
Risk Review
</span>

<span className="text-green-400">
PASSED
</span>

</div>


<div className="flex justify-between">
<span className="text-white/60">
AI Verification
</span>

<span className="text-green-400">
PASSED
</span>

</div>


<div className="flex justify-between">
<span className="text-white/60">
Exchange Connection
</span>

<span className="text-green-400">
READY
</span>

</div>

</div>

</div>


<div className="grid grid-cols-2 gap-3 pt-4">

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
Deploy Bot
</button>


</div>


</div>

</div>

);

}
