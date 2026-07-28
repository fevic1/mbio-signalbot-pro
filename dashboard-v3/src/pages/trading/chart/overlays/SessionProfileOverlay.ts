import {
 POCOverlay
} from "./POCOverlay";

import {
 Candle
} from "../../market/state/marketStore";

import {
 ChartOverlay
} from "./OverlayBridge";


export class SessionProfileOverlay implements ChartOverlay {


private sessions:POCOverlay[]=[];


constructor(
private candles:Candle[]
){}


attach(chart:any){

const groups =
this.splitSessions();


groups.forEach(group=>{

const overlay =
new POCOverlay(group);

overlay.attach(chart);

this.sessions.push(
overlay
);

});

}


update(candles:Candle[]){

this.candles=candles;

}


detach(){

this.sessions.forEach(
x=>x.detach()
);

this.sessions=[];

}


private splitSessions(){

const size =
Math.floor(
this.candles.length/3
);


return [

this.candles.slice(0,size),

this.candles.slice(size,size*2),

this.candles.slice(size*2)

];

}

}
