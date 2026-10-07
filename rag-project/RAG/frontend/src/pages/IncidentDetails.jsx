import { ArrowLeft, MessageSquareText } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import Notice from '../components/common/Notice.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'

function IncidentDetails() {
  const { id } = useParams()

  return (
    <>
      <PageHeading
        eyebrow="Incident register"
        title={`Incident #${id}`}
        description="Incident details cannot be loaded until the backend provides an incident lookup endpoint."
      >
        <Link className="button button-secondary" to="/incidents"><ArrowLeft size={14} /> Back to incidents</Link>
      </PageHeading>
      <div className="mb-4">
        <Notice tone="warning">No incident data is being shown: GET incident details is not implemented by the backend.</Notice>
      </div>
      <Panel title="Incident information">
        <div className="surface-body">
          <div className="detail-grid">
            {['Error code', 'Service', 'Status', 'Created by', 'Created at', 'Updated at'].map((label) => (
              <div className="detail-field" key={label}>
                <div className="detail-label">{label}</div>
                <div className="detail-value">Not available</div>
              </div>
            ))}
          </div>
          <div className="detail-field">
            <div className="detail-label">Description</div>
            <div className="detail-value">Incident details are unavailable because the backend endpoint has not been implemented.</div>
          </div>
          <div className="mt-5">
            <Link className="button button-primary" to="/assistant"><MessageSquareText size={14} /> Investigate with AI</Link>
          </div>
        </div>
      </Panel>
    </>
  )
}

export default IncidentDetails
