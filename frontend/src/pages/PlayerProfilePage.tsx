import { useState } from 'react'
import { useParams } from 'react-router-dom'
import ComingSoonTab from '../components/ComingSoonTab'
import ConsistencyTab from '../components/ConsistencyTab'
import WeatherPerformanceTab from '../components/WeatherPerformanceTab'

const TABS = [
  { key: 'consistency', label: 'Consistency' },
  { key: 'weather', label: 'Weather Performance' },
  { key: 'clutch', label: 'Clutch Factor' },
  { key: 'course-fit', label: 'Course Fit' },
] as const

type TabKey = (typeof TABS)[number]['key']

export default function PlayerProfilePage() {
  const { playerId } = useParams<{ playerId: string }>()
  const [activeTab, setActiveTab] = useState<TabKey>('consistency')

  if (!playerId) return null

  return (
    <div>
      <h1>Player {playerId}</h1>
      <nav>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            disabled={activeTab === tab.key}
          >
            {tab.label}
          </button>
        ))}
      </nav>
      <div>
        {activeTab === 'consistency' && <ConsistencyTab playerId={playerId} />}
        {activeTab === 'weather' && <WeatherPerformanceTab playerId={playerId} />}
        {activeTab === 'clutch' && (
          <ComingSoonTab reason="needs field-wide hole-by-hole data to reconstruct leaderboard position (see CLAUDE.md)" />
        )}
        {activeTab === 'course-fit' && (
          <ComingSoonTab reason="needs curated course attribute data (fairway width, bunker counts — see CLAUDE.md)" />
        )}
      </div>
    </div>
  )
}
