import { useEffect } from "react";

import { useMarketStore } from "../state/marketStore";
import { connectMarketData } from "../providers/MarketDataProvider";


export function useMarketData(
symbol:string,
exchange:"hyperliquid"|"bybit" = "hyperliquid"
){

const candles =
useMarketStore(
state=>state.candles[symbol] ?? []
);


useEffect(()=>{

const disconnect =
connectMarketData(
exchange,
symbol
);


return ()=>{
disconnect();
};

},[
symbol,
exchange
]);


return candles;

}
