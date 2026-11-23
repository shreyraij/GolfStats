import type { ConsistencyResult, RankingsResponse, WeatherPerformanceResult } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function getJSON<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`)
  if (!response.ok) {
    throw new Error(`${path} failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function getRankings(limit = 200): Promise<RankingsResponse> {
  return getJSON(`/rankings?limit=${limit}`)
}

export function getPlayerConsistency(playerId: string): Promise<ConsistencyResult> {
  return getJSON(`/players/${playerId}/metrics/consistency`)
}

export function getPlayerWeatherPerformance(playerId: string): Promise<WeatherPerformanceResult> {
  return getJSON(`/players/${playerId}/metrics/weather-performance`)
}
