import { BrowserRouter, Route, Routes } from 'react-router-dom'
import PlayerProfilePage from './pages/PlayerProfilePage'
import RankingsPage from './pages/RankingsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RankingsPage />} />
        <Route path="/players/:playerId" element={<PlayerProfilePage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
