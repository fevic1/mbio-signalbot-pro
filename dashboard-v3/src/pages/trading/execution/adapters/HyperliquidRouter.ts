import {
ExchangeAdapter
} from "../ExchangeAdapter";

import {
OrderRequest,
OrderResult
} from "../types";


export class HyperliquidRouter
implements ExchangeAdapter {


async placeOrder(
_order:OrderRequest
):Promise<OrderResult>{


return {

success:false,

message:
"Hyperliquid execution adapter not connected"

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
