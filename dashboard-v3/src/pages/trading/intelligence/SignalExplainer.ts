import {
TradeSetup
} from "./types";


export function explainSignal(
setup:TradeSetup
){

return {

summary:

`${setup.direction} ${setup.setup} detected on ${setup.symbol}`,

reasoning:

setup.reasons.join(
". "
),

confidence:

setup.confidence

};

}
