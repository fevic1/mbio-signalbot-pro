import { loadOverlayPreset } from "@/pages/trading/overlays/state/presetActions";

const presets = [
{
id:"institutional",
label:"Institutional"
},
{
id:"scalping",
label:"Scalping"
},
{
id:"ict",
label:"ICT"
},
{
id:"marketProfile",
label:"Market Profile"
}
];


export default function OverlayPresetSelector(){

return (

<div className="absolute right-4 top-80 z-50 rounded-lg border border-white/10 bg-black/80 p-3 text-white">

<div className="mb-2 text-sm font-semibold">
Trading Mode
</div>

<div className="space-y-2">

{
presets.map(preset=>(

<button
key={preset.id}
className="block w-full rounded bg-white/10 px-3 py-1 text-left text-xs"
onClick={()=>
loadOverlayPreset(
preset.id as any
)
}
>
{preset.label}
</button>

))
}

</div>

</div>

);

}
