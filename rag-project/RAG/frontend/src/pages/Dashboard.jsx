import {
  ArrowRight,
  BadgeCheck,
  BookOpen,
  BriefcaseBusiness,
  ClipboardList,
  FileCheck2,
  GitBranch,
  MessageSquareText,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import EmptyState from '../components/common/EmptyState.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'

const METRICS = [
  { label: 'Total incidents', icon: BriefcaseBusiness },
  { label: 'Open incidents', icon: ClipboardList },
  { label: 'Pending reviews', icon: FileCheck2 },
  { label: 'Approved knowledge', icon: BookOpen },
]

const WORKFLOW = [
  { label: 'Incident', icon: BriefcaseBusiness },
  { label: 'Investigate', icon: MessageSquareText },
  { label: 'Resolution', icon: FileCheck2 },
  { label: 'Review', icon: ClipboardList },
  { label: 'Approval', icon: BadgeCheck },
  { label: 'Knowledge', icon: BookOpen },
  { label: 'Future retrieval', icon: GitBranch },
]

function Dashboard() {
  return (
    <>
      <PageHeading
        eyebrow="IT operations overview"
        title="Good day"
        description="A source-grounded workspace for investigating incidents and building trusted operational knowledge."
      >
        <Link className="button button-primary" to="/assistant">
          Open AI assistant <ArrowRight size={14} />
        </Link>
      </PageHeading>

      <div className="metric-grid">
        {METRICS.map(({ label, icon: Icon }) => (
          <article className="metric-card" key={label}>
            <div className="flex items-center justify-between">
              <span className="metric-label">{label}</span>
              <Icon size={15} color="#8090a5" aria-hidden="true" />
            </div>
            <div className="metric-value" aria-label="No data available">—</div>
            <div className="metric-note">No data available from the current backend</div>
          </article>
        ))}
      </div>

      <div className="dashboard-grid">
        <Panel title="Recent incidents" subtitle="Incident records from the operations workspace">
          <EmptyState
            title="No incident data available"
            description="Incident list endpoints are not implemented in the backend yet."
            icon={BriefcaseBusiness}
            action={<Link className="button button-secondary" to="/incidents">View incidents</Link>}
          />
        </Panel>
        <Panel title="Knowledge activity" subtitle="Recently approved or added knowledge">
          <EmptyState
            title="No knowledge activity available"
            description="Knowledge management endpoints are not implemented in the backend yet."
            icon={BookOpen}
            action={<Link className="button button-secondary" to="/knowledge">Open knowledge base</Link>}
          />
        </Panel>
      </div>

      <Panel title="Incident-to-knowledge lifecycle" subtitle="Approved resolutions can enrich retrieval for future incidents">
        <div className="surface-body">
          <div className="workflow" aria-label="Incident, investigate, resolution, review, approval, knowledge, future retrieval">
            {WORKFLOW.map(({ label, icon: Icon }, index) => (
              <div className="contents" key={label}>
                <div className="workflow-step">
                  <span className="workflow-icon"><Icon size={15} /></span>
                  <span className="workflow-label">{label}</span>
                </div>
                {index < WORKFLOW.length - 1 && (
                  <ArrowRight className="workflow-arrow" size={13} aria-hidden="true" />
                )}
              </div>
            ))}
          </div>
        </div>
      </Panel>
    </>
  )
}

export default Dashboard
