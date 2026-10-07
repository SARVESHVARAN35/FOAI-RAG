import { useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { BACKEND_STATUS_EVENT, getBackendHealth } from '../../services/api.js'
import Header from './Header.jsx'
import Sidebar from './Sidebar.jsx'

function AppLayout() {
  const [backendOnline, setBackendOnline] = useState(null)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    let active = true

    function checkBackend() {
      getBackendHealth()
        .then((health) => {
          if (active) setBackendOnline(health?.status === 'ok' || health?.status === 'degraded')
        })
        .catch(() => {
          if (active) setBackendOnline(false)
        })
    }

    function handleBackendStatus(event) {
      if (active) setBackendOnline(event.detail.online)
    }

    window.addEventListener(BACKEND_STATUS_EVENT, handleBackendStatus)
    checkBackend()
    const healthCheck = window.setInterval(checkBackend, 15000)

    return () => {
      active = false
      window.removeEventListener(BACKEND_STATUS_EVENT, handleBackendStatus)
      window.clearInterval(healthCheck)
    }
  }, [])

  return (
    <div className="app-shell">
      <Sidebar open={menuOpen} onNavigate={() => setMenuOpen(false)} />
      <button
        className={`sidebar-overlay ${menuOpen ? 'visible' : ''}`}
        type="button"
        aria-label="Close navigation"
        onClick={() => setMenuOpen(false)}
        tabIndex={menuOpen ? 0 : -1}
      />
      <div className="main-column">
        <Header
          backendOnline={backendOnline}
          onMenuClick={() => setMenuOpen((open) => !open)}
        />
        <main className="content-area">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AppLayout
