import { FileCheck2, Plus } from 'lucide-react'
import { useState } from 'react'
import EmptyState from '../components/common/EmptyState.jsx'
import Notice from '../components/common/Notice.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'

const FIELDS = ['Root cause', 'Resolution description', 'Steps taken', 'Additional notes']

function Resolutions() {
  const [formOpen, setFormOpen] = useState(false)

  return (
    <>
      <PageHeading
        eyebrow="Incident lifecycle"
        title="Resolutions"
        description="Document investigation outcomes and track their review status."
      >
        <button className="button button-primary" type="button" onClick={() => setFormOpen((open) => !open)}>
          <Plus size={14} /> {formOpen ? 'Close form' : 'New resolution'}
        </button>
      </PageHeading>

      <div className="mb-4">
        <Notice tone="warning">Resolution list and submission endpoints are not implemented in the backend. No resolution records can be saved or retrieved yet.</Notice>
      </div>

      {formOpen && (
        <div className="mb-4">
          <Panel title="Resolution form" subtitle="Form layout only — submission becomes available with the backend API">
            <div className="surface-body">
              <label className="field mb-4">
                <span className="field-label">Incident ID</span>
                <input className="input" placeholder="Incident ID" disabled />
              </label>
              {FIELDS.map((field) => (
                <label className="field mb-4" key={field}>
                  <span className="field-label">{field}</span>
                  <textarea className="textarea" placeholder={`${field}...`} disabled />
                </label>
              ))}
              <div className="form-actions">
                <button className="button button-primary" type="button" disabled>Submit resolution</button>
              </div>
            </div>
          </Panel>
        </div>
      )}

      <Panel title="Submitted resolutions" subtitle="Incident, root cause, resolution, status, submitter, and submission date">
        <div className="table-scroll">
          <table className="data-table">
            <thead><tr><th>Incident</th><th>Root cause</th><th>Resolution</th><th>Status</th><th>Submitted by</th><th>Submitted at</th><th>Action</th></tr></thead>
          </table>
        </div>
        <EmptyState title="No resolutions available" description="Resolution data will appear here after the backend resolution endpoints are implemented." icon={FileCheck2} />
      </Panel>
    </>
  )
}

export default Resolutions
