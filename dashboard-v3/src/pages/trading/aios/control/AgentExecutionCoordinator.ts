import {
TradeSetup
} from "../../intelligence/types";


export interface AgentResult {

approved:boolean;

reason:string;

}


export class AgentExecutionCoordinator {


async evaluate(
setup:TradeSetup
):Promise<AgentResult>{


if(
setup.confidence < 70
){

return {

approved:false,

reason:
"Confidence below threshold"

};

}


return {

approved:true,

reason:
"Agents approved setup"

};

}


}
