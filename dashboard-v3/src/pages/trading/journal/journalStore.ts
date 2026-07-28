import {
create
} from "zustand";

import {
TradeRecord
} from "./types";


interface JournalState {

trades:TradeRecord[];

addTrade:
(trade:TradeRecord)=>void;

}


export const useJournalStore =
create<JournalState>((set)=>({

trades:[],

addTrade:
(trade)=>
set(
state=>({

trades:[
...state.trades,
trade
]

})
)

}));
