import {
OrderRequest
} from "../types";


export function validateOrder(
order:OrderRequest
){

if(
order.quantity <=0
){

return {

approved:false,

reason:
"Invalid quantity"

};

}


if(
!order.symbol
){

return {

approved:false,

reason:
"Missing symbol"

};

}


return {

approved:true,

reason:
"Order passed"

};

}
