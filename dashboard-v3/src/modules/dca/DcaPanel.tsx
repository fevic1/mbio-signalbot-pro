
import { useEffect, useState, useCallback } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Square } from "lucide-react"


interface DcaPosition {
  asset: string
  direction: string
  levels: number
  filled_levels: number
  active_orders: number
  base_size: number
  total_invested: number
  avg_entry: number
  entry: number
  enabled: boolean
  sl?: number
  tp1?: number
  tp2?: number
  tp3?: number
}


const POLL_INTERVAL_MS = 10000


export function DcaPanel({
  onClose
}: {
  onClose: (dca: DcaPosition) => void
}) {


  const [positions, setPositions] = useState<DcaPosition[] | null>(null)
  const [error, setError] = useState<string | null>(null)


  const fetchDca = useCallback(async () => {

    try {

      const res =
        await apiFetch<{
          positions: DcaPosition[]
          count: number
        }>("/dca_status")


      setPositions(res.positions)
      setError(null)

    } catch (e) {

      setError(
        e instanceof ApiError
          ? e.message
          : "Failed to load DCA positions"
      )

    }

  }, [])



  useEffect(() => {

    fetchDca()

    const id =
      setInterval(
        fetchDca,
        POLL_INTERVAL_MS
      )

    return () => clearInterval(id)

  }, [fetchDca])



  if (error && !positions) {

    return (
      <div className="
        rounded-md
        border
        border-short/40
        bg-short/10
        p-3
        text-xs
        text-short
      ">
        {error}
      </div>
    )

  }



  if (!positions) {

    return (
      <p className="text-sm text-muted-foreground">
        Loading DCA positions…
      </p>
    )

  }



  if (positions.length === 0) {

    return (
      <p className="text-sm text-muted-foreground">
        No active DCA positions.
      </p>
    )

  }



  return (

    <div className="space-y-4">


      {positions.map((d) => (

        <Card
          key={d.asset}
          className="
            rounded-2xl
            border-white/10
            bg-white/5
          "
        >


          <CardHeader>


            <div className="
              flex
              justify-between
              items-center
            ">


              <div className="flex gap-3 items-center">

                <span className="
                  text-lg
                  font-bold
                ">
                  {d.asset}
                </span>


                <Badge
                  variant={
                    d.direction === "LONG"
                      ? "long"
                      : "short"
                  }
                >
                  {d.direction}
                </Badge>

              </div>



              <Button
                size="icon"
                variant="ghost"
                onClick={() => onClose(d)}
              >

                <Square
                  className="
                    h-3.5
                    w-3.5
                    text-short
                  "
                />

              </Button>


            </div>



          </CardHeader>




          <CardContent>


            <div className="mb-5">


              <div className="
                flex
                justify-between
                text-xs
                text-muted-foreground
                mb-2
              ">

                <span>
                  Accumulation Progress
                </span>

                <span>
                  {d.filled_levels}/{d.levels}
                </span>

              </div>



              <div className="
                h-2
                rounded-full
                bg-white/10
              ">

                <div
                  className="
                    h-full
                    rounded-full
                    bg-green-400
                  "
                  style={{
                    width:
                      `${Math.min(
                        100,
                        (d.filled_levels / d.levels) * 100
                      )}%`
                  }}
                />

              </div>


            </div>




            <div className="
              grid
              grid-cols-4
              gap-4
              text-xs
              font-mono
            ">


              <Metric
                label="Entry"
                value={`$${d.entry.toLocaleString()}`}
              />


              <Metric
                label="Average Entry"
                value={`$${d.avg_entry.toLocaleString()}`}
              />


              <Metric
                label="Exposure"
                value={`$${d.total_invested.toFixed(2)}`}
              />


              <Metric
                label="Base Size"
                value={`${d.base_size}`}
              />


              <Metric
                label="Stop Loss"
                value={
                  d.sl
                    ? `$${d.sl.toLocaleString()}`
                    : "—"
                }
              />


              <Metric
                label="TP1"
                value={
                  d.tp1
                    ? `$${d.tp1.toLocaleString()}`
                    : "—"
                }
              />


              <Metric
                label="TP2"
                value={
                  d.tp2
                    ? `$${d.tp2.toLocaleString()}`
                    : "—"
                }
              />


              <Metric
                label="TP3"
                value={
                  d.tp3
                    ? `$${d.tp3.toLocaleString()}`
                    : "—"
                }
              />


            </div>


          </CardContent>


        </Card>

      ))}


    </div>

  )

}



function Metric({
  label,
  value
}: {
  label:string
  value:string
}) {

  return (

    <div>

      <div className="
        text-muted-foreground
      ">
        {label}
      </div>

      <div>
        {value}
      </div>

    </div>

  )

}
