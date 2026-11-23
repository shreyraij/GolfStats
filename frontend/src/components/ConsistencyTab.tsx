import { useEffect, useState } from 'react'
import { getPlayerConsistency } from '../api/client'
import type { ConsistencyResult } from '../api/types'
import DataSourceBadge from './DataSourceBadge'

export default function ConsistencyTab({ playerId }: { playerId: string }) {
  const [result, setResult] = useState<ConsistencyResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setResult(null)
    setError(null)
    getPlayerConsistency(playerId).then(setResult).catch((err) => setError(err.message))
  }, [playerId])

  if (error) return <p role="alert">Couldn't load consistency data: {error}</p>
  if (!result) return <p>Loading...</p>

  if (!result.reliable) {
    return (
      <div>
        <DataSourceBadge source={result.data_source} />
        <p>Not enough round data yet for a reliable consistency reading ({result.rounds_counted} rounds).</p>
      </div>
    )
  }

  return (
    <div>
      <DataSourceBadge source={result.data_source} />
      <p>Birdie rate: {((result.birdie_rate ?? 0) * 100).toFixed(1)}%</p>
      <p>Bogey-or-worse rate: {((result.bogey_or_worse_rate ?? 0) * 100).toFixed(1)}%</p>
      <p>Volatility score: {result.volatility_score}</p>
      <p>Based on {result.rounds_counted} rounds ({result.total_holes} holes).</p>
    </div>
  )
}
