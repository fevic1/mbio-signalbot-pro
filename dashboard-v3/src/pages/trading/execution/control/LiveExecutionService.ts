import {
  ExchangeAdapter
} from "../ExchangeAdapter";


import {
  LivePermissionGate
} from "../LivePermissionGate";


import {
  OrderRequest,
  OrderResult
} from "../types";


import {
  validateOrder
} from "../risk/OrderRiskCheck";


export class LiveExecutionService {


constructor(
private gate:LivePermissionGate,
private exchange:ExchangeAdapter
){}



async placeOrder(
order:OrderRequest
):Promise<OrderResult>{


const validation =
validateOrder(order);


if(!validation.approved){

return {

success:false,

message:
validation.reason

};

}



if(!this.gate.canTrade()){

return {

success:false,

message:
"Live trading disabled"

};

}



return this.exchange.placeOrder(order);

}



async cancelOrder(
orderId:string
):Promise<OrderResult>{


if(!this.gate.canTrade()){

return {

success:false,

message:
"Live trading disabled"

};

}


return this.exchange.cancelOrder(
orderId
);


}


}
