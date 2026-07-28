import { HyperliquidAdapter } from "../adapters/hyperliquid";
import { BybitAdapter } from "../adapters/bybit";
import { useMarketStore, Candle } from "../state/marketStore";


export function connectMarketData(
exchange:"hyperliquid"|"bybit",
symbol:string
){

const adapter =
exchange==="hyperliquid"
?
new HyperliquidAdapter()
:
new BybitAdapter();


adapter.connect(
symbol,
(candle: Candle)=>{

useMarketStore
.getState()
.appendCandle(
symbol,
candle
);

}
);


return ()=>adapter.disconnect();

}
