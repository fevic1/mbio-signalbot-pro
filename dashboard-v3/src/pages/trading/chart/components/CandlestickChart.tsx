import {
  createChart,
  ColorType,
  IChartApi
} from "lightweight-charts";

import {
  useEffect,
  useRef
} from "react";

import { Candle } from "../../market/state/marketStore";


export default function CandlestickChart({
  candles: _candles
}:{
  candles:Candle[]
}){

const container =
useRef<HTMLDivElement|null>(null);


const chart =
useRef<IChartApi|null>(null);


useEffect(()=>{

if(!container.current){
 return;
}


const instance =
createChart(
container.current,
{
autoSize:true,

layout:{
background:{
type:ColorType.Solid,
color:"#000000"
},

textColor:"#ffffff"
}

});


chart.current = instance;


return ()=>{

try{

instance.remove();

}catch(e){

console.warn(
"chart cleanup ignored",
e
);

}


chart.current=null;


};


},[]);



return (

<div
ref={container}
className="h-full w-full min-h-[400px] bg-black"
/>

);

}
