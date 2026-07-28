import {
OrderRequest,
OrderResult
} from "./types";


export interface ExchangeAdapter {


placeOrder(
order:OrderRequest
):Promise<OrderResult>;


cancelOrder(
orderId:string
):Promise<OrderResult>;


}
