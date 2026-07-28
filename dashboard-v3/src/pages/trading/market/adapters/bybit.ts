import { MarketDataAdapter } from "../providers/types";

export class BybitAdapter implements MarketDataAdapter {

private socket?:WebSocket;


connect(
symbol:string,
callback:any
){

this.socket =
new WebSocket(
"wss://stream.bybit.com/v5/public/linear"
);


this.socket.onopen=()=>{

this.socket?.send(
JSON.stringify({
op:"subscribe",
args:[
`kline.1.${symbol}`
]
})
);

};


this.socket.onmessage=(event)=>{

const data =
JSON.parse(event.data);


if(data?.data?.list?.length){

const kline = data.data.list[0];

callback({

  time: Number(kline[0]),

  open: Number(kline[1]),

  high: Number(kline[2]),

  low: Number(kline[3]),

  close: Number(kline[4]),

  volume: Number(kline[5])

});

}

};

}


disconnect(){

this.socket?.close();

}

}
