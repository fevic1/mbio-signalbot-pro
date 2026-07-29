import {
  useEffect,
  useRef
} from "react";

import {
  OverlayBridge
} from "../overlays/OverlayBridge";

import {
  VWAPOverlay
} from "../overlays/VWAPOverlay";

import {
  InitialBalanceOverlay
} from "../overlays/InitialBalanceOverlay";

import {
  POCOverlay
} from "../overlays/POCOverlay";

import {
  ValueAreaOverlay
} from "../overlays/ValueAreaOverlay";



import {
 VolumeProfileOverlay
} from "../overlays/VolumeProfileOverlay";

import {
 DevelopingPOCOverlay
} from "../overlays/DevelopingPOCOverlay";

import {
 SessionProfileOverlay
} from "../overlays/SessionProfileOverlay";



import {
FVGOverlay
} from "../overlays/FVGOverlay";

import {
OrderBlockOverlay
} from "../overlays/OrderBlockOverlay";

import {
LiquiditySweepOverlay
} from "../overlays/LiquiditySweepOverlay";



import {
EqualLevelsOverlay
} from "../overlays/EqualLevelsOverlay";

import {
BreakerBlockOverlay
} from "../overlays/BreakerBlockOverlay";

import {
MitigationBlockOverlay
} from "../overlays/MitigationBlockOverlay";

import {
  Candle
} from "../../market/state/marketStore";


export function useChartOverlays(
chart:any,
candles:Candle[]
){

const bridge =
useRef<OverlayBridge|null>(null);



useEffect(()=>{


if(!chart){
 return;
}


const overlayBridge =
new OverlayBridge();


overlayBridge.register(
new VWAPOverlay(
candles
)
);

overlayBridge.register(
new InitialBalanceOverlay(
candles
)
);

overlayBridge.register(
new POCOverlay(
candles
)
);

overlayBridge.register(
new ValueAreaOverlay(
candles
)
);




overlayBridge.register(
new VolumeProfileOverlay(
candles
)
);

overlayBridge.register(
new DevelopingPOCOverlay(
candles
)
);

overlayBridge.register(
new SessionProfileOverlay(
candles
)
);




overlayBridge.register(
new FVGOverlay(
candles
)
);

overlayBridge.register(
new OrderBlockOverlay(
candles
)
);

overlayBridge.register(
new LiquiditySweepOverlay(
candles
)
);




overlayBridge.register(
new EqualLevelsOverlay(
candles
)
);

overlayBridge.register(
new BreakerBlockOverlay(
candles
)
);

overlayBridge.register(
new MitigationBlockOverlay(
candles
)
);


overlayBridge.attach(
chart
);


bridge.current =
overlayBridge;



return ()=>{

overlayBridge.detach();

};


},[
chart
]);



useEffect(()=>{

bridge.current?.update(
candles
);

},[
candles
]);

}
