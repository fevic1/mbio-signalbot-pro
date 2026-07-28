import {
  ArrowLeft,
  Pause,
  Play,
  Square,
} from "lucide-react";

import {
  Bot
} from "./BotCard";


interface BotDetailPanelProps {

  bot: Bot;

  onBack: () => void;

}


export default function BotDetailPanel({
  bot,
  onBack,
}: BotDetailPanelProps) {


return (

<div className="flex h-full flex-col overflow-hidden bg-gray-950">


<div className="flex items-center gap-3 border-b border-white/10 px-4 py-3">

<button
onClick={onBack}
className="text-white/50 hover:text-white"
>
<ArrowLeft className="h-4 w-4"/>
</button>


<div>

<div className="text-sm font-semibold text-white">
{bot.strategy} {bot.asset}
</div>

<div className="text-xs text-white/50">
Bot Detail
</div>

</div>

</div>


<div className="flex-1 overflow-y-auto p-4 space-y-4">


<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<div className="text-xs text-white/50">
Status
</div>

<div className="mt-2 text-green-400">
{bot.status}
</div>

</div>



<div className="grid grid-cols-2 gap-3">


<div className="rounded-lg border border-white/10 bg-white/5 p-3">

<div className="text-xs text-white/40">
PnL
</div>

<div className="mt-1 text-white">
{bot.pnl}
</div>

</div>



<div className="rounded-lg border border-white/10 bg-white/5 p-3">

<div className="text-xs text-white/40">
Runtime
</div>

<div className="mt-1 text-white">
{bot.runtime}
</div>

</div>


</div>



<div className="rounded-lg border border-white/10 bg-white/5 p-4">

<div className="mb-3 text-xs text-white/50">
Operations
</div>


<div className="grid grid-cols-3 gap-2">


<button className="flex items-center justify-center gap-1 rounded-lg bg-green-500/20 py-2 text-xs text-green-400">

<Play className="h-3 w-3"/>

Resume

</button>


<button className="flex items-center justify-center gap-1 rounded-lg bg-yellow-500/20 py-2 text-xs text-yellow-400">

<Pause className="h-3 w-3"/>

Pause

</button>


<button className="flex items-center justify-center gap-1 rounded-lg bg-red-500/20 py-2 text-xs text-red-400">

<Square className="h-3 w-3"/>

Stop

</button>


</div>

</div>



<div className="rounded-lg border border-dashed border-white/10 p-5 text-center text-xs text-white/40">

Orders / Grid Levels / Execution History

</div>


</div>


</div>

);

}
