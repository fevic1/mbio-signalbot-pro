import { useEffect } from "react";

import {
useIntelligenceStore
} from "../state/intelligenceStore";


import {
runVoting
} from "../voting/runVoting";


import {
useVotingStore
} from "../voting/state/votingStore";


export function useVoting(){

const setup =
useIntelligenceStore(
state=>state.latestSetup
);


const setVoting =
useVotingStore(
state=>state.setVoting
);


useEffect(()=>{

if(!setup){
return;
}


const result =
runVoting(setup);


setVoting(
result.decisions,
result.consensus
);


},[
setup,
setVoting
]);

}
