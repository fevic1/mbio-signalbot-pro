import {
  IChartApi
} from "lightweight-charts";


export interface ChartOverlay {

  attach(
    chart:IChartApi
  ):void;


  update?(
    data:any
  ):void;


  detach():void;

}



export class OverlayBridge {

private overlays:ChartOverlay[]=[];


register(
overlay:ChartOverlay
){

this.overlays.push(
overlay
);

}


attach(
chart:IChartApi
){

this.overlays.forEach(
overlay=>
overlay.attach(chart)
);

}



update(
data:any
){

this.overlays.forEach(
overlay=>
overlay.update?.(data)
);

}



private detached=false;


detach(){

if(this.detached){
 return;
}

this.detached=true;


this.overlays.forEach(
overlay=>{

try{

overlay.detach();

}catch(error){

console.warn(
"Overlay detach failed",
error
);

}

});

this.overlays=[];

}

}
