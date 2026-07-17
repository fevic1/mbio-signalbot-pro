import { useMemo } from 'react'

interface SparklineProps {
  data: number[]
  width?: number
  height?: number
  color?: string
}

export function Sparkline({ data, width = 80, height = 30, color }: SparklineProps) {
  const path = useMemo(() => {
    if (!data || data.length === 0) return ''
    
    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1
    
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width
      const y = height - ((value - min) / range) * height
      return `${x},${y}`
    })
    
    return `M ${points.join(' L ')}`
  }, [data, width, height])

  const strokeColor = color || (data.length >= 2 && data[data.length - 1] >= data[0] ? '#22c55e' : '#ef4444')

  if (!path) return <div className="w-20 h-8" />

  return (
    <svg width={width} height={height} className="overflow-visible">
      <path
        d={path}
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
