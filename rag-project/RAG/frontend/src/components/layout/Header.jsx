import { Menu, ShieldCheck } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth/useAuth.js'

const TITLES = {
  '/dashboard': 'Dashboard',
  '/incidents': 'Incidents',
  '/assistant': 'AI Assistant',
  '/resolutions': 'Resolutions',
  '/reviews': 'Reviews',
  '/knowledge': 'Knowledge Base',
  '/settings': 'Settings',
}

function Header({ backendOnline, onMenuClick }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const title = location.pathname.startsWith('/incidents/')
    ? location.pathname.endsWith('/new') ? 'Create incident' : 'Incident details'
    : TITLES[location.pathname] || 'Dashboard'

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button
          className="mobile-menu-button"
          type="button"
          aria-label="Open navigation"
          aria-expanded={undefined}
          onClick={onMenuClick}
        >
          <Menu size={17} />
        </button>
        <div className="topbar-label">
          <Link to="/dashboard">Operations</Link>
          <span aria-hidden="true">/</span>
          <strong>{title}</strong>
        </div>
      </div>
      <div className="topbar-right">
        <div className="header-status" aria-live="polite">
          <span className={`status-dot ${backendOnline ? 'online' : backendOnline === false ? 'offline' : ''}`} />
          Backend {backendOnline ? 'connected' : backendOnline === false ? 'disconnected' : 'checking'}
        </div>
        <span className="header-user" title={user?.email}>
          {user?.name} · {user?.role?.replaceAll('_', ' ')}
        </span>
        <button className="button button-secondary header-logout" type="button" onClick={logout}>
          Sign out
        </button>
        <ShieldCheck size={17} color="#718096" aria-label="Approved knowledge workflow" />
      </div>
    </header>
  )
}

export default Header
