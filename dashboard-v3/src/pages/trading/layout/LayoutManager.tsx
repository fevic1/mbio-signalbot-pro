import ChartGrid from "./ChartGrid";
import { useLayoutStore } from "./state/layoutStore";

export default function LayoutManager(){

const setMode =
useLayoutStore(
state=>state.setMode
);


return (

<div className="relative h-full w-full">

<div className="absolute right-4 top-4 z-50 flex gap-2">

<button
className="rounded bg-white/10 px-3 py-1 text-xs text-white"
onClick={()=>setMode("single")}
>
1
</button>

<button
className="rounded bg-white/10 px-3 py-1 text-xs text-white"
onClick={()=>setMode("double")}
>
2
</button>

<button
className="rounded bg-white/10 px-3 py-1 text-xs text-white"
onClick={()=>setMode("quad")}
>
4
</button>

</div>

<ChartGrid />

</div>

);

}
