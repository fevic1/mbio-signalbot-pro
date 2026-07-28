import {
Candle
} from "../market/state/marketStore";


import {
TradeSetup
} from "./types";


export function detectSetup(
symbol:string,
candles:Candle[]
):TradeSetup|null{


if(candles.length < 10){
return null;
}


const last =
candles[candles.length-1];


const previous =
candles[candles.length-2];



if(
last.close > previous.high
){

return {

symbol,

direction:"LONG",

setup:
"Momentum Breakout",

confidence:50,

reasons:[
"Previous high broken",
"Positive candle displacement"
],

timestamp:
Date.now()

};

}



if(
last.close < previous.low
){

return {

symbol,

direction:"SHORT",

setup:
"Momentum Breakdown",

confidence:50,

reasons:[
"Previous low broken",
"Negative candle displacement"
],

timestamp:
Date.now()

};

}


return null;

}
