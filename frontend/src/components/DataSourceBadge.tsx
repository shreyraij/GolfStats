import type { DataSource } from '../api/types'

/** Renders only when the backend is serving the fictional sample fixture. */
export default function DataSourceBadge({ source }: { source: DataSource }) {
  if (source !== 'sample') return null
  return (
    <span
      className="sample-badge"
      title="Fictional players and stats. Set DATAGOLF_API_KEY on the backend for live data."
    >
      Sample data
    </span>
  )
}
