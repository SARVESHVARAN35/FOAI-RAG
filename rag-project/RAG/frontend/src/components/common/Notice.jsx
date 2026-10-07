import { AlertCircle, CheckCircle2, Info } from 'lucide-react'

const ICONS = {
  error: AlertCircle,
  success: CheckCircle2,
  warning: AlertCircle,
  info: Info,
}

function Notice({ children, tone = 'info', className = '' }) {
  const Icon = ICONS[tone] || Info

  return (
    <div className={`notice ${tone} ${className}`} role={tone === 'error' ? 'alert' : 'status'}>
      <Icon className="notice-icon" size={15} aria-hidden="true" />
      <div>{children}</div>
    </div>
  )
}

export default Notice
