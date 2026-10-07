import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../auth/useAuth.js'
import {
  BookOpen,
  BriefcaseBusiness,
  ClipboardCheck,
  FileCheck2,
  LayoutDashboard,
  MessageSquareText,
  Settings2,
  ShieldCheck,
} from 'lucide-react'

const NAVIGATION = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Incidents', to: '/incidents', icon: BriefcaseBusiness },
  { label: 'AI Assistant', to: '/assistant', icon: MessageSquareText },
  { label: 'Resolutions', to: '/resolutions', icon: FileCheck2 },
  { label: 'Reviews', to: '/reviews', icon: ClipboardCheck },
  { label: 'Knowledge Base', to: '/knowledge', icon: BookOpen },
]

function Sidebar({ open, onNavigate }) {
  const { user } = useAuth()
  const [settingsActive, setSettingsActive] = useState(false)
  const navigation = NAVIGATION.filter(({ to }) => {
    if (to === '/reviews') return ['IT_LEAD', 'ADMIN'].includes(user?.role)
    if (to === '/knowledge') return user?.role === 'ADMIN'
    return true
  })

  return (
    <aside className={`sidebar ${open ? 'open' : ''}`} aria-label="Main navigation">
      <NavLink className="brand" to="/dashboard" onClick={onNavigate}>
        <span className="brand-mark"><ShieldCheck size={19} /></span>
        <span>
          <span className="brand-name">Ops Knowledge</span>
          <span className="brand-caption">Incident intelligence</span>
        </span>
      </NavLink>

      <div className="nav-section-label">Workspace</div>
      <nav className="nav-list">
        {navigation.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            to={to}
            onClick={onNavigate}
          >
            <Icon size={16} strokeWidth={1.8} aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <NavLink
          className={({ isActive }) => `nav-link ${isActive || settingsActive ? 'active' : ''}`}
          to="/settings"
          onClick={() => {
            setSettingsActive(true)
            onNavigate?.()
          }}
        >
          <Settings2 size={16} strokeWidth={1.8} aria-hidden="true" />
          <span>Settings</span>
        </NavLink>
        <div className="workspace-card">
          <div className="workspace-card-title">Source-grounded support</div>
          <p className="workspace-card-copy">
            Answers use approved knowledge retrieved by the backend.
          </p>
        </div>
        <div className="sidebar-footer">Enterprise IT Knowledge Assistant</div>
      </div>
    </aside>
  )
}

export default Sidebar
