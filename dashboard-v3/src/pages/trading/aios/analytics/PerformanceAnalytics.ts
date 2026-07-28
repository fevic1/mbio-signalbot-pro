export interface Performance {

wins:number;

losses:number;

}


export function calculatePerformance(
data:Performance
){

const total =
data.wins+
data.losses;


return {

winRate:
total===0
?
0
:
data.wins/total*100

};

}
