import { overlayRegistry } from "../overlays/registry";
import { useOverlayStore } from "../overlays/state/overlayStore";

import ZoneOverlay from "../overlays/renderers/ZoneOverlay";
import LineOverlay from "../overlays/renderers/LineOverlay";

export default function OverlayRenderer(){

const activeGroups =
useOverlayStore(
state=>state.activeGroups
);


return (
<>

{
overlayRegistry
.filter(
overlay =>
overlay.enabled &&
activeGroups.includes(overlay.group)
)
.map(overlay=>{

switch(overlay.type){

case "zone":
case "range":

return (
<ZoneOverlay
key={overlay.id}
overlay={overlay}
/>
);


case "line":

return (
<LineOverlay
key={overlay.id}
overlay={overlay}
/>
);


default:
return null;

}

})
}

</>
);

}
