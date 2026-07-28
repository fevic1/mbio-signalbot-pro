import {
OrderRequest,
OrderResult
} from "../types";


export class PaperExecutor {


async execute(
_order:OrderRequest
):Promise<OrderResult>{


return {

success:true,

orderId:
`paper-${Date.now()}`,

message:
"Paper trade executed"

};

}


}
