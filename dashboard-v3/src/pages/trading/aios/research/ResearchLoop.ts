export interface ResearchResult {

topic:string;

insight:string;

timestamp:number;

}


export class ResearchLoop {


async run(
topic:string
):Promise<ResearchResult>{


return {

topic,

insight:
"Research pending",

timestamp:
Date.now()

};

}


}
