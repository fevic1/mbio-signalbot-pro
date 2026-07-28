import { useOverlayStore } from "@/pages/trading/overlays/state/overlayStore";

const groups = [
  {
    id:"institutional",
    label:"Institutional"
  },
  {
    id:"ict",
    label:"ICT"
  },
  {
    id:"market-profile",
    label:"Market Profile"
  },
  {
    id:"volume",
    label:"Volume"
  },
  {
    id:"execution",
    label:"Execution"
  },
  {
    id:"risk",
    label:"Risk"
  }
];

export default function OverlayControlPanel(){

const {
 activeGroups,
 toggleGroup,
 enableAll,
 disableAll
}=useOverlayStore();


return (
<div className="absolute right-4 top-4 z-50 w-64 rounded-lg border border-white/10 bg-black/80 p-4 text-white">

<div className="mb-3 text-sm font-semibold">
Overlay Controls
</div>


<div className="mb-3 flex gap-2">

<button
className="rounded bg-green-600 px-2 py-1 text-xs"
onClick={enableAll}
>
All
</button>

<button
className="rounded bg-red-600 px-2 py-1 text-xs"
onClick={disableAll}
>
None
</button>

</div>


<div className="space-y-2">

{
groups.map(group=>{

const active =
activeGroups.includes(group.id);

return (

<label
key={group.id}
className="flex cursor-pointer items-center justify-between text-sm"
>

<span>
{group.label}
</span>


<input
type="checkbox"
checked={active}
onChange={()=>toggleGroup(group.id)}
/>


</label>

)

})
}

</div>

</div>
);

}
