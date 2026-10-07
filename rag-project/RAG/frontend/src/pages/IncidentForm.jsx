import { useState } from 'react'
import { ArrowLeft, CircleHelp } from 'lucide-react'
import { Link } from 'react-router-dom'
import Notice from '../components/common/Notice.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'

function IncidentForm() {
  const [form, setForm] = useState({ title: '', errorCode: '', service: '', description: '' })
  const setField = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }))

  return (
    <>
      <PageHeading
        eyebrow="Incident register"
        title="Create incident"
        description="Capture the initial symptoms and affected service."
      >
        <Link className="button button-secondary" to="/incidents"><ArrowLeft size={14} /> Back to incidents</Link>
      </PageHeading>

      <Panel title="Incident details" subtitle="Fields are ready for the incident API integration">
        <div className="surface-body">
          <div className="mb-5">
            <Notice tone="warning">
              Incident creation is not enabled because the backend currently has no incident creation endpoint. Your entries will not be saved.
            </Notice>
          </div>
          <form onSubmit={(event) => event.preventDefault()}>
            <div className="form-grid">
              <label className="field full-width">
                <span className="field-label">Title <span aria-hidden="true">*</span></span>
                <input className="input" value={form.title} onChange={setField('title')} placeholder="e.g. Payment API timeout after deployment" required />
              </label>
              <label className="field">
                <span className="field-label">Error code</span>
                <input className="input" value={form.errorCode} onChange={setField('errorCode')} placeholder="e.g. 504" />
              </label>
              <label className="field">
                <span className="field-label">Service</span>
                <input className="input" value={form.service} onChange={setField('service')} placeholder="e.g. Payment API" />
              </label>
              <label className="field full-width">
                <span className="field-label">Description <span aria-hidden="true">*</span></span>
                <textarea className="textarea" value={form.description} onChange={setField('description')} placeholder="Describe the symptoms, when they began, and any recent changes..." required />
              </label>
            </div>
            <div className="form-actions">
              <Link className="button button-secondary" to="/incidents">Cancel</Link>
              <button className="button button-primary" type="submit" disabled title="Waiting for the backend incident endpoint">
                Create incident
              </button>
            </div>
          </form>
        </div>
      </Panel>
      <div className="mt-4">
        <Notice><CircleHelp size={14} /> The current working backend feature is the source-grounded AI assistant. <Link className="font-semibold underline" to="/assistant">Open assistant</Link>.</Notice>
      </div>
    </>
  )
}

export default IncidentForm
