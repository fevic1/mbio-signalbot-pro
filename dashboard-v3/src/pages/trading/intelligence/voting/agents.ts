import {
TradeSetup
} from "../types";

import {
AgentDecision
} from "./types";


export function technicalAgent(
setup:TradeSetup
):AgentDecision{

return {

agent:"Technical",

vote:setup.direction,

confidence:
setup.confidence,

reason:
"Price structure analysis"

};

}



export function skepticAgent(
setup:TradeSetup
):AgentDecision{

return {

agent:"Skeptic",

vote:
setup.confidence > 80
?
setup.direction
:
"NO_TRADE",

confidence:40,

reason:
"Challenges weak setups"

};

}



export function riskAgent(
setup:TradeSetup
):AgentDecision{

return {

agent:"Risk",

vote:
setup.confidence >=70
?
setup.direction
:
"NO_TRADE",

confidence:70,

reason:
"Risk validation"

};

}
