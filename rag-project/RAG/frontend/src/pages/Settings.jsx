import { useEffect, useState } from 'react'
import { Check, RefreshCw, Server, Settings2 } from 'lucide-react'
import Notice from '../components/common/Notice.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'
import { ApiError, API_BASE_URL, getBackendHealth } from '../services/api.js'

function Settings() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function refreshHealth() {
    setLoading(true)
    setError('')
    try {
      setHealth(await getBackendHealth())
    } catch (requestError) {
      setHealth(null)
      setError(requestError instanceof ApiError ? requestError.message : 'Unable to check backend status.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let active = true
    getBackendHealth()
      .then((data) => {
        if (active) setHealth(data)
      })
      .catch((requestError) => {
        if (active) {
          setHealth(null)
          setError(requestError instanceof ApiError ? requestError.message : 'Unable to check backend status.')
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <>
      <PageHeading
        eyebrow="Workspace configuration"
        title="Settings"
        description="View frontend connectivity and system integration status."
      />

      <div className="settings-grid">
        <nav className="surface settings-nav" aria-label="Settings sections">
          <button className="settings-nav-item selected" type="button"><Server size={13} className="mr-2 inline" />System</button>
          <button className="settings-nav-item" type="button" disabled>API configuration</button>
          <button className="settings-nav-item" type="button" disabled>Appearance</button>
          <button className="settings-nav-item" type="button" disabled>Account</button>
        </nav>
        <div className="grid gap-4">
          <Panel title="Backend connection" subtitle="Health information returned by the FastAPI service">
            <div className="surface-body">
              {error && <div className="mb-4"><Notice tone="error">{error}</Notice></div>}
              <div className="settings-row">
                <div>
                  <div className="settings-row-title">Backend</div>
                  <div className="settings-row-copy">Configured API base URL</div>
                </div>
                <div className="flex items-center gap-3">
                  <code className="rounded bg-slate-100 px-2 py-1 text-[10px] text-slate-600">{API_BASE_URL}</code>
                  <span className={`badge ${health ? health.status === 'ok' ? 'approved' : 'pending_review' : 'rejected'}`}>
                    {loading ? 'Checking' : health ? health.status === 'ok' ? 'Connected' : 'Degraded' : 'Disconnected'}
                  </span>
                </div>
              </div>
              {health && (
                <>
                  <div className="settings-row">
                    <div><div className="settings-row-title">Application</div></div>
                    <div className="text-xs text-slate-600">{health.app || '—'}</div>
                  </div>
                  <div className="settings-row">
                    <div><div className="settings-row-title">Environment</div></div>
                    <div className="text-xs text-slate-600">{health.environment || '—'}</div>
                  </div>
                  <div className="settings-row">
                    <div><div className="settings-row-title">Database</div></div>
                    <span className={`badge ${health.database === 'up' ? 'approved' : 'rejected'}`}>
                      {health.database === 'up' ? <Check size={11} /> : null}{health.database || 'Unknown'}
                    </span>
                  </div>
                </>
              )}
              <div className="form-actions">
                <button className="button button-secondary" type="button" onClick={refreshHealth} disabled={loading}>
                  <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Check connection
                </button>
              </div>
            </div>
          </Panel>
          <Panel title="Security note" subtitle="Secrets remain server-side">
            <div className="surface-body">
              <Notice><Settings2 size={14} /> API keys, database passwords, and signing secrets are not read or displayed in the frontend.</Notice>
            </div>
          </Panel>
        </div>
      </div>
    </>
  )
}

export default Settings
