import { MarketDataAdapter } from "../providers/types";

export class HyperliquidAdapter implements MarketDataAdapter {

private socket?: WebSocket;

private symbol?: string;

private callback?: (candle:any)=>void;

private reconnectTimer?: ReturnType<typeof setTimeout>;

private reconnectAttempts = 0;

private stopped = false;


connect(
symbol:string,
callback:(candle:any)=>void
){

this.symbol = symbol;
this.callback = callback;
this.stopped = false;

this.openConnection();

}


private openConnection(){

if(this.stopped || !this.symbol){
return;
}


this.socket =
new WebSocket(
"wss://api.hyperliquid.xyz/ws"
);


this.socket.onopen = ()=>{

this.reconnectAttempts = 0;


this.socket?.send(
JSON.stringify({
method:"subscribe",
subscription:{
type:"candle",
coin:this.symbol,
interval:"1m"
}
})
);


};



this.socket.onmessage = (event)=>{

const data =
JSON.parse(event.data);

console.log("HYPERLIQUID RAW", data);


if(data?.data){

const candle=data.data;


this.callback?.({

time:candle.t ?? candle.time,

open:Number(candle.o ?? candle.open),

high:Number(candle.h ?? candle.high),

low:Number(candle.l ?? candle.low),

close:Number(candle.c ?? candle.close),

volume:Number(candle.v ?? candle.volume ?? 0)

});

}

};



this.socket.onerror=()=>{

this.socket?.close();

};



this.socket.onclose=()=>{

if(!this.stopped){

this.scheduleReconnect();

}

};

}



private scheduleReconnect(){

if(this.reconnectTimer){
return;
}


this.reconnectAttempts++;


const delay =
Math.min(
5000 * this.reconnectAttempts,
30000
);


this.reconnectTimer =
setTimeout(()=>{

this.reconnectTimer=undefined;

this.openConnection();


},delay);

}



disconnect(){

this.stopped=true;


if(this.reconnectTimer){

clearTimeout(
this.reconnectTimer
);

this.reconnectTimer=undefined;

}


this.socket?.close();


this.socket=undefined;

}

}
