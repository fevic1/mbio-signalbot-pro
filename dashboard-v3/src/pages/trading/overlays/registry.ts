import { OverlayDefinition } from "./types";

export const overlayRegistry: OverlayDefinition[] = [

{
 id:"asia-range",
 name:"Asia Range",
 type:"range",
 group:"institutional",
 color:"cyan",
 enabled:true
},

{
 id:"london-range",
 name:"London Range",
 type:"range",
 group:"institutional",
 color:"cyan",
 enabled:true
},

{
 id:"new-york-range",
 name:"New York Range",
 type:"range",
 group:"institutional",
 color:"cyan",
 enabled:true
},

{
 id:"previous-day-high",
 name:"Previous Day High",
 type:"line",
 group:"market-profile",
 color:"cyan",
 enabled:true
},

{
 id:"previous-day-low",
 name:"Previous Day Low",
 type:"line",
 group:"market-profile",
 color:"cyan",
 enabled:true
},

{
 id:"weekly-levels",
 name:"Weekly Levels",
 type:"range",
 group:"market-profile",
 color:"cyan",
 enabled:true
},

{
 id:"monthly-levels",
 name:"Monthly Levels",
 type:"range",
 group:"market-profile",
 color:"cyan",
 enabled:true
},

{
 id:"fair-value-gap",
 name:"Fair Value Gap",
 type:"zone",
 group:"ict",
 color:"cyan",
 enabled:true
},

{
 id:"order-block",
 name:"Order Block",
 type:"zone",
 group:"ict",
 color:"cyan",
 enabled:true
},

{
 id:"liquidity-pool",
 name:"Liquidity Pool",
 type:"zone",
 group:"ict",
 color:"cyan",
 enabled:true
},

{
 id:"poc",
 name:"Point Of Control",
 type:"line",
 group:"volume",
 color:"cyan",
 enabled:true
},

{
 id:"high-volume-node",
 name:"High Volume Node",
 type:"zone",
 group:"volume",
 color:"cyan",
 enabled:true
},

{
 id:"low-volume-node",
 name:"Low Volume Node",
 type:"zone",
 group:"volume",
 color:"cyan",
 enabled:true
},

{
 id:"opening-gap",
 name:"Opening Gap",
 type:"zone",
 group:"execution",
 color:"cyan",
 enabled:true
},

{
 id:"opening-range",
 name:"Opening Range",
 type:"range",
 group:"execution",
 color:"cyan",
 enabled:true
},

{
 id:"stop-zone",
 name:"Stop Zone",
 type:"zone",
 group:"risk",
 color:"cyan",
 enabled:true
},

{
 id:"target-zone",
 name:"Target Zone",
 type:"zone",
 group:"risk",
 color:"cyan",
 enabled:true
},
];