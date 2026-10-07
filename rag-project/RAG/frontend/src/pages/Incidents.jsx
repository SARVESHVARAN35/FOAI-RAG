import { useMemo, useState } from 'react'
import { BriefcaseBusiness, Plus, Search } from 'lucide-react'
import { Link } from 'react-router-dom'
import EmptyState from '../components/common/EmptyState.jsx'
import Notice from '../components/common/Notice.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'

function Incidents() {
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('ALL')
  const [service, setService] = useState('ALL')
  const hasFilters = useMemo(() => Boolean(search.trim() || status !== 'ALL' || service !== 'ALL'), [search, status, service])

  return (
    <>
      <PageHeading
        eyebrow="Operations"
        title="Incidents"
        description="Track incident records and investigate issues using approved knowledge."
      >
        <Link className="button button-primary" to="/incidents/new"><Plus size={14} /> Create incident</Link>
      </PageHeading>

      <div className="mb-4">
        <Notice>
          Incident list and create endpoints are not available in the backend yet. This page does not store or submit incident data.
        </Notice>
      </div>

      <Panel title="Incident register" subtitle="Search and filter incident records">
        <div className="surface-body">
          <div className="toolbar mb-4">
            <label className="field filter-input">
              <span className="sr-only">Search incidents</span>
              <span className="relative block">
                <Search className="absolute left-3 top-2.5 text-slate-400" size={14} aria-hidden="true" />
                <input className="input pl-9" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search incidents..." />
              </span>
            </label>
            <label>
              <span className="sr-only">Filter by status</span>
              <select className="select w-auto" value={status} onChange={(event) => setStatus(event.target.value)}>
                <option value="ALL">All statuses</option>
                <option value="OPEN">Open</option>
                <option value="INVESTIGATING">Investigating</option>
                <option value="RESOLVED">Resolved</option>
                <option value="CLOSED">Closed</option>
              </select>
            </label>
            <label>
              <span className="sr-only">Filter by service</span>
              <select className="select w-auto" value={service} onChange={(event) => setService(event.target.value)}>
                <option value="ALL">All services</option>
              </select>
            </label>
          </div>

          <div className="table-scroll">
            <table className="data-table">
              <thead><tr><th>ID</th><th>Title</th><th>Error code</th><th>Service</th><th>Status</th><th>Created</th><th>Action</th></tr></thead>
            </table>
          </div>
          <EmptyState
            title={hasFilters ? 'No matching incidents' : 'No incidents found'}
            description={hasFilters ? 'There are no incident records matching these filters.' : 'The backend does not provide incident data yet. Once implemented, incidents will appear here.'}
            icon={BriefcaseBusiness}
          />
        </div>
      </Panel>
    </>
  )
}

export default Incidents
