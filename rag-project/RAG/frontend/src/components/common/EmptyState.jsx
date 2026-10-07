import { Inbox } from 'lucide-react'

function EmptyState({
  title = 'Nothing to show yet',
  description,
  icon: Icon = Inbox,
  action,
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon" aria-hidden="true"><Icon size={17} /></div>
      <h3 className="empty-title">{title}</h3>
      {description && <p className="empty-copy">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

export default EmptyState
