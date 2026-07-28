import { useEffect } from "react";

import {
  useMarketStore
} from "../../market/state/marketStore";

import {
  detectSetup
} from "../SetupDetector";

import {
  useIntelligenceStore
} from "../state/intelligenceStore";


export function useSetupDetection(
symbol:string
){

const candles =
useMarketStore(
state=>state.candles[symbol] ?? []
);


const setSetup =
useIntelligenceStore(
state=>state.setSetup
);


useEffect(()=>{

const setup =
detectSetup(
symbol,
candles
);


setSetup(setup);


},[
symbol,
candles,
setSetup
]);


}
