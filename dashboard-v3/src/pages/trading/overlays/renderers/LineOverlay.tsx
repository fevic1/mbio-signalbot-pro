import { OverlayDefinition } from "../types";

export default function LineOverlay({
 overlay
}:{
 overlay:OverlayDefinition
}){

return (
<div
className="pointer-events-none absolute border-l-2 border-dashed"
style={{
left:overlay.position?.left ?? "50%",
top:overlay.position?.top ?? "20%",
height:overlay.position?.height ?? "60%"
}}
/>
);

}
