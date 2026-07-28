import {
ExchangeAdapter
} from "../ExchangeAdapter";

import {
OrderRequest,
OrderResult
} from "../types";


export class BybitRouter
implements ExchangeAdapter {


async placeOrder(
_order:OrderRequest
):Promise<OrderResult>{


return {

success:false,

message:
"Bybit execution adapter not connected"

};

}



async cancelOrder(
_orderId:string
):Promise<OrderResult>{


return {

success:false,

message:
"Cancel not connected"

};

}


}
