function Panel({ title, subtitle, action, children, className = '' }) {
  return (
    <section className={`surface ${className}`}>
      {(title || subtitle || action) && (
        <div className="surface-header">
          <div>
            {title && <h2 className="surface-title">{title}</h2>}
            {subtitle && <p className="surface-subtitle">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  )
}

export default Panel
