export function RiskSummaryCard() {

  return (

    <div className="
      rounded-2xl
      border
      border-white/10
      bg-white/5
      p-6
    ">

      <h2 className="font-bold">
        Risk Allocation
      </h2>


      <div className="mt-5 space-y-4">


        <Row
          label="Capital Allocation"
          value="2.0%"
        />

        <Row
          label="Max Exposure"
          value="$5,000"
        />

        <Row
          label="Risk State"
          value="GREEN"
        />


      </div>


    </div>

  );
}


function Row({
 label,
 value
}:{
 label:string;
 value:string;
}){

 return (

  <div className="
    flex
    justify-between
    text-sm
  ">

    <span className="text-white/40">
      {label}
    </span>

    <span>
      {value}
    </span>

  </div>

 );

}
