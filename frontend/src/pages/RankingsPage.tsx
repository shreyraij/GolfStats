import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getRankings } from '../api/client'
import type { DataSource, RankingEntry } from '../api/types'
import DataSourceBadge from '../components/DataSourceBadge'

export default function RankingsPage() {
  const [rankings, setRankings] = useState<RankingEntry[]>([])
  const [dataSource, setDataSource] = useState<DataSource | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getRankings(200)
      .then((res) => {
        setRankings(res.rankings)
        setDataSource(res.data_source)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Loading rankings...</p>
  if (error) return <p role="alert">Couldn't load rankings: {error}</p>

  return (
    <div>
      <h1>
        {dataSource === 'sample' ? `Top ${rankings.length}` : 'Top 200'} World Golf Rankings{' '}
        {dataSource && <DataSourceBadge source={dataSource} />}
      </h1>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Player</th>
            <th>Country</th>
          </tr>
        </thead>
        <tbody>
          {rankings.map((entry) => (
            <tr key={entry.player_id}>
              <td>{entry.owgr_rank}</td>
              <td>
                <Link to={`/players/${entry.player_id}`}>{entry.player_name}</Link>
              </td>
              <td>{entry.country ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
