import { useState } from "react";

import QuickTicket from "./QuickTicket";
import StrategySelector from "./StrategySelector";


export type BuilderView =
  | "ticket"
  | "strategy"
  | "builder"
  | "risk"
  | "deploy";


export default function BuilderRouter() {

const [view,setView] =
useState<BuilderView>("ticket");


return (

<div className="flex h-full flex-col overflow-hidden bg-gray-950">


{view==="ticket" && (

<QuickTicket

onCreateBot={()=>
setView("strategy")
}

/>

)}


{view==="strategy" && (

<StrategySelector

onBack={()=>
setView("ticket")
}

onSelectStrategy={()=>
setView("builder")
}

/>

)}


{view==="builder" && (

<div className="flex h-full items-center justify-center text-white/50">

Strategy Builder

</div>

)}


{view==="risk" && (

<div className="flex h-full items-center justify-center text-white/50">

Risk Review

</div>

)}


{view==="deploy" && (

<div className="flex h-full items-center justify-center text-white/50">

Deploy Confirmation

</div>

)}


</div>

);

}
