import { useEffect, useState } from 'react'
import { getPlayerWeatherPerformance } from '../api/client'
import type { WeatherPerformanceResult } from '../api/types'
import DataSourceBadge from './DataSourceBadge'

export default function WeatherPerformanceTab({ playerId }: { playerId: string }) {
  const [result, setResult] = useState<WeatherPerformanceResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setResult(null)
    setError(null)
    getPlayerWeatherPerformance(playerId).then(setResult).catch((err) => setError(err.message))
  }, [playerId])

  if (error) return <p role="alert">Couldn't load weather performance data: {error}</p>
  if (!result) return <p>Loading...</p>

  return (
    <div>
      <DataSourceBadge source={result.data_source} />
      <section>
        <h3>Wind</h3>
        {result.wind_result_reliable ? (
          <p>
            Avg score to par — windy: {result.avg_score_to_par_windy}, calm: {result.avg_score_to_par_calm} (
            {result.wind_rounds_sample_size} windy rounds)
          </p>
        ) : (
          <p>Not enough windy-round data yet ({result.wind_rounds_sample_size} rounds).</p>
        )}
      </section>
      <section>
        <h3>Rain</h3>
        {result.rain_result_reliable ? (
          <p>
            Avg score to par — rain: {result.avg_score_to_par_rain}, dry: {result.avg_score_to_par_dry} (
            {result.rain_rounds_sample_size} rain rounds)
          </p>
        ) : (
          <p>Not enough rain-round data yet ({result.rain_rounds_sample_size} rounds).</p>
        )}
      </section>
    </div>
  )
}
