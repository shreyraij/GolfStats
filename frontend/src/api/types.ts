/** "sample" = fictional fixture served when the backend has no DATAGOLF_API_KEY. */
export type DataSource = 'sample' | 'datagolf'

export interface RankingsResponse {
  data_source: DataSource
  rankings: RankingEntry[]
}

export interface RankingEntry {
  owgr_rank: number
  player_id: string
  player_name: string
  country: string | null
}

export interface ConsistencyResult {
  data_source: DataSource
  player_id: string
  rounds_counted: number
  total_holes: number
  birdie_rate: number | null
  bogey_or_worse_rate: number | null
  volatility_score: number | null
  reliable: boolean
}

export interface WeatherPerformanceResult {
  data_source: DataSource
  player_id: string
  avg_score_to_par_windy: number | null
  avg_score_to_par_calm: number | null
  wind_rounds_sample_size: number
  wind_result_reliable: boolean
  avg_score_to_par_rain: number | null
  avg_score_to_par_dry: number | null
  rain_rounds_sample_size: number
  rain_result_reliable: boolean
}
