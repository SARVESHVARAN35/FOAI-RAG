import { useState } from 'react'
import {
  BookOpenCheck,
  CircleHelp,
  ClipboardCheck,
  FileSearch,
  MessageSquareText,
  Search,
  ShieldCheck,
} from 'lucide-react'
import EmptyState from '../components/common/EmptyState.jsx'
import Notice from '../components/common/Notice.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'
import SourceCard from '../components/rag/SourceCard.jsx'
import StatusBadge from '../components/common/StatusBadge.jsx'
import { ApiError, queryRAG } from '../services/api.js'

const EXAMPLE_QUERY = 'My Payment API is giving 504 Gateway Timeout after deployment. What should I check?'

function IncidentAssistant() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    const value = query.trim()
    if (!value || loading) return

    setError('')
    setResult(null)
    setLoading(true)

    try {
      const response = await queryRAG(value)
      if (!response || !['ACCEPTED', 'REJECTED'].includes(response.status)) {
        throw new ApiError('The backend response did not contain a supported RAG status.')
      }
      setResult({
        ...response,
        sources: Array.isArray(response.sources) ? response.sources : [],
      })
    } catch (requestError) {
      setError(requestError instanceof ApiError
        ? requestError.message
        : 'Unable to complete the investigation. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <PageHeading
        eyebrow="Source-grounded investigation"
        title="AI incident assistant"
        description="Ask a troubleshooting question. The backend retrieves and reranks approved knowledge before generating an answer."
      />

      <div className="assistant-layout">
        <div className="assistant-main">
          <div className="surface assistant-intro">
            <span className="assistant-intro-icon"><MessageSquareText size={18} /></span>
            <div>
              <h2 className="assistant-intro-title">Investigate with approved knowledge</h2>
              <p className="assistant-intro-copy">The backend relevance gate is authoritative. When it rejects a query, no troubleshooting answer is invented.</p>
            </div>
          </div>

          <Panel title="Investigation query" subtitle="Describe the error and what you need to investigate">
            <form className="query-form" onSubmit={handleSubmit}>
              <label className="field">
                <span className="field-label">Incident symptoms or question</span>
                <textarea
                  className="textarea"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Describe your incident, error code, affected service, or recent change..."
                  rows={5}
                  required
                  maxLength={5000}
                  aria-describedby="query-guidance"
                />
              </label>
              <div className="query-form-actions">
                <span className="query-hint" id="query-guidance">Query is sent to the configured backend; avoid including passwords or secrets.</span>
                <button className="button button-primary" type="submit" disabled={loading || !query.trim()}>
                  {loading ? <><span className="spinner" aria-hidden="true" /> Investigating...</> : <><Search size={14} /> Investigate</>}
                </button>
              </div>
              <button className="button button-secondary w-fit" type="button" onClick={() => setQuery(EXAMPLE_QUERY)} disabled={loading}>
                Use the 504 example
              </button>
            </form>
          </Panel>

          {loading && (
            <Panel title="Investigation in progress">
              <div className="flex items-center gap-3 p-5 text-xs text-slate-600" role="status">
                <span className="spinner dark" aria-hidden="true" />
                Retrieving approved knowledge and generating a grounded response...
              </div>
            </Panel>
          )}

          {error && <Notice tone="error">{error}</Notice>}

          {result && (
            <Panel className="result-card">
              <div className="result-status-row">
                <div className="result-status-title">Investigation result</div>
                <StatusBadge status={result.status} />
              </div>
              <div className="answer-block">
                <div className="answer-label">{result.status === 'ACCEPTED' ? 'Knowledge found · Answer' : 'Knowledge gate · Answer'}</div>
                {result.answer
                  ? <div className="answer-content">{result.answer}</div>
                  : <Notice tone={result.status === 'REJECTED' ? 'warning' : 'error'}>
                      {result.status === 'REJECTED'
                        ? 'No sufficiently relevant approved knowledge was found for this incident.'
                        : 'The backend did not return an answer.'}
                    </Notice>}
              </div>
              <div className="answer-block">
                <div className="answer-label">Knowledge sources</div>
                {result.sources.length > 0
                  ? <div className="source-list">{result.sources.map((source, index) => (
                      <SourceCard
                        key={`${source.document || 'source'}-${source.chunk_number ?? index}`}
                        document={source.document}
                        chunkNumber={source.chunk_number}
                        score={source.score}
                      />
                    ))}</div>
                  : <EmptyState
                      title="No knowledge sources were returned"
                      description={result.status === 'REJECTED' ? 'The backend relevance gate did not find an approved source relevant enough to support an answer.' : 'The backend response did not include any source records.'}
                      icon={FileSearch}
                    />}
              </div>
            </Panel>
          )}
        </div>

        <aside className="assistant-side">
          <Panel title="How it works">
            <div className="surface-body side-list">
              <div className="side-list-item"><Search size={14} /><span>Searches the indexed knowledge base for related chunks.</span></div>
              <div className="side-list-item"><ClipboardCheck size={14} /><span>Reranks retrieved context and applies a relevance gate.</span></div>
              <div className="side-list-item"><BookOpenCheck size={14} /><span>Generates an answer grounded only in approved knowledge.</span></div>
              <div className="side-list-item"><ShieldCheck size={14} /><span>Displays the backend decision and returned source references.</span></div>
            </div>
          </Panel>
          <Panel title="Using the assistant">
            <div className="surface-body">
              <Notice><CircleHelp size={14} /> Include the error code, impacted service, symptoms, and recent changes when known. Do not enter credentials.</Notice>
            </div>
          </Panel>
        </aside>
      </div>
    </>
  )
}

export default IncidentAssistant
