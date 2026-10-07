const LABELS = {
  pending_review: 'Pending review',
  changes_requested: 'Changes requested',
}

function StatusBadge({ status }) {
  const value = String(status || 'unknown')
  const normalized = value.toLowerCase()
  const label = LABELS[normalized] || value.replaceAll('_', ' ')

  return <span className={`badge ${normalized}`}>{label}</span>
}

export default StatusBadge
