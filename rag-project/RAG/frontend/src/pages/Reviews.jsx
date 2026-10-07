import { ClipboardCheck } from 'lucide-react'
import EmptyState from '../components/common/EmptyState.jsx'
import Notice from '../components/common/Notice.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'

function Reviews() {
  return (
    <>
      <PageHeading
        eyebrow="Quality and governance"
        title="Resolution reviews"
        description="Review submitted work before approved outcomes become searchable knowledge."
      />
      <div className="mb-4">
        <Notice tone="warning">Review queue and decision endpoints are not implemented in the backend yet. Approval, rejection, and change requests are unavailable.</Notice>
      </div>
      <Panel title="Pending review queue" subtitle="Approval workflows must be enforced by backend authorization">
        <div className="table-scroll">
          <table className="data-table">
            <thead><tr><th>Incident</th><th>Root cause</th><th>Resolution</th><th>Steps taken</th><th>Submitted by</th><th>Submitted at</th><th>Review action</th></tr></thead>
          </table>
        </div>
        <EmptyState
          title="No pending reviews"
          description="The backend does not provide resolution review data yet. Review actions will be connected only when server-side permissions and endpoints are available."
          icon={ClipboardCheck}
        />
      </Panel>
    </>
  )
}

export default Reviews
