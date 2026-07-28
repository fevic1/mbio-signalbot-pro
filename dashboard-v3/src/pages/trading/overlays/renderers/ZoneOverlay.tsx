import { OverlayDefinition } from "../types";

export default function ZoneOverlay({
 overlay
}:{
 overlay: OverlayDefinition
}) {

return (
<div
className="pointer-events-none absolute rounded border border-dashed opacity-60"
style={{
left:overlay.position?.left ?? "40%",
top:overlay.position?.top ?? "30%",
width:overlay.position?.width ?? "20%",
height:overlay.position?.height ?? "15%"
}}
>
<div className="absolute -top-4 text-[9px]">
{overlay.name}
</div>
</div>
);

}
