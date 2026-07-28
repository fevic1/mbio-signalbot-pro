import {
  TradeSetup
} from "../../intelligence/types";


import {
  validateRisk
} from "../../intelligence/RiskGate";


import {
  validateOrder
} from "../risk/OrderRiskCheck";


import {
  OrderRequest
} from "../types";


export interface ExecutionRequest {

setup:TradeSetup;

order:OrderRequest;

riskPercent:number;

}


export function validateExecution(
request:ExecutionRequest
){

const risk =
validateRisk({

confidence:
request.setup.confidence,

riskPercent:
request.riskPercent

});


if(!risk.approved){

return {

approved:false,

stage:"risk",

reason:risk.reason

};

}



const order =
validateOrder(
request.order
);


if(!order.approved){

return {

approved:false,

stage:"order",

reason:order.reason

};

}


return {

approved:true,

stage:"ready",

reason:
"Execution approved"

};

}
