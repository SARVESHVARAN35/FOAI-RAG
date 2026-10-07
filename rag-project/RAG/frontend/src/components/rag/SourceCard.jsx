import { FileText } from 'lucide-react'

function SourceCard({ document, chunkNumber, score }) {
  const parsedScore = Number(score)

  return (
    <article className="source-card">
      <div className="source-card-heading">
        <FileText size={13} aria-hidden="true" />
        Knowledge source
      </div>
      <div className="source-document">{document || 'Unnamed source'}</div>
      <div className="source-meta">
        <span>Chunk {chunkNumber ?? '—'}</span>
        <span>Relevance: {Number.isFinite(parsedScore) ? parsedScore.toFixed(2) : '—'}</span>
      </div>
    </article>
  )
}

export default SourceCard
