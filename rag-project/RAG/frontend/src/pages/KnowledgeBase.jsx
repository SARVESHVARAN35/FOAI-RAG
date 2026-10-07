import { useEffect, useState } from 'react'
import { BookOpen, FileUp } from 'lucide-react'
import { getKnowledgeDocuments, uploadKnowledgePdf } from '../services/api.js'
import EmptyState from '../components/common/EmptyState.jsx'
import Notice from '../components/common/Notice.jsx'
import PageHeading from '../components/common/PageHeading.jsx'
import Panel from '../components/common/Panel.jsx'

function KnowledgeBase() {
  const [uploadOpen, setUploadOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [uploadResult, setUploadResult] = useState(null)
  const [documents, setDocuments] = useState([])
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true)
  const [documentsError, setDocumentsError] = useState('')

  async function refreshKnowledgeDocuments() {
    setDocumentsError('')

    try {
      const result = await getKnowledgeDocuments()
      setDocuments(result.documents)
    } catch (error) {
      setDocumentsError(error.message || 'Knowledge documents could not be loaded.')
    } finally {
      setIsLoadingDocuments(false)
    }
  }

  useEffect(() => {
    getKnowledgeDocuments()
      .then((result) => setDocuments(result.documents))
      .catch((error) => {
        setDocumentsError(error.message || 'Knowledge documents could not be loaded.')
      })
      .finally(() => setIsLoadingDocuments(false))
  }, [])

  async function handleUpload(event) {
    event.preventDefault()
    setUploadError('')
    setUploadResult(null)

    if (!selectedFile) {
      setUploadError('Choose a PDF file before uploading.')
      return
    }

    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Only PDF files are allowed.')
      return
    }

    setIsUploading(true)

    try {
      const result = await uploadKnowledgePdf(selectedFile)
      setUploadResult(result)
      if (result.status === 'SUCCESS') {
        await refreshKnowledgeDocuments()
      }
    } catch (error) {
      setUploadError(error.message || 'The PDF could not be uploaded.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <>
      <PageHeading
        eyebrow="Approved operational knowledge"
        title="Knowledge base"
        description="Manage the trusted documents used to ground incident investigations."
      >
        <button className="button button-primary" type="button" onClick={() => setUploadOpen((open) => !open)}>
          <FileUp size={14} /> {uploadOpen ? 'Close upload' : 'Upload knowledge'}
        </button>
      </PageHeading>

      {uploadOpen && (
        <div className="mb-4">
          <Panel title="Upload knowledge PDF" subtitle="Add a PDF document to the searchable knowledge base">
            <div className="surface-body">
              <form onSubmit={handleUpload}>
                <label className="field full-width">
                  <span className="field-label">PDF document</span>
                  <input
                    className="input"
                    type="file"
                    accept="application/pdf,.pdf"
                    disabled={isUploading}
                    onChange={(event) => {
                      setSelectedFile(event.target.files?.[0] || null)
                      setUploadError('')
                      setUploadResult(null)
                    }}
                  />
                  <span className="field-help">
                    {selectedFile ? `Selected: ${selectedFile.name}` : 'Select a PDF file to index.'}
                  </span>
                </label>
                <div className="form-actions">
                  <button className="button button-primary" type="submit" disabled={isUploading}>
                    <FileUp size={14} /> {isUploading ? 'Uploading...' : 'Upload PDF'}
                  </button>
                </div>
              </form>

              {uploadError && (
                <div className="mt-4">
                  <Notice tone="error">{uploadError}</Notice>
                </div>
              )}

              {uploadResult && (
                <div className="mt-4">
                  <Notice tone={uploadResult.status === 'ALREADY_EXISTS' ? 'warning' : 'success'}>
                    {uploadResult.message}
                  </Notice>
                  {uploadResult.status === 'ALREADY_EXISTS' ? (
                    <p className="field-help mt-3">
                      {uploadResult.document} is already in the knowledge base; no new chunks were added.
                    </p>
                  ) : (
                    <dl className="detail-grid">
                      <div className="detail-field">
                        <dt className="detail-label">Document</dt>
                        <dd className="detail-value">{uploadResult.document}</dd>
                      </div>
                      <div className="detail-field">
                        <dt className="detail-label">Pages</dt>
                        <dd className="detail-value">{uploadResult.pages}</dd>
                      </div>
                      <div className="detail-field">
                        <dt className="detail-label">Chunks added</dt>
                        <dd className="detail-value">{uploadResult.chunks_added}</dd>
                      </div>
                      <div className="detail-field">
                        <dt className="detail-label">Total vectors</dt>
                        <dd className="detail-value">{uploadResult.total_vectors}</dd>
                      </div>
                    </dl>
                  )}
                </div>
              )}
            </div>
          </Panel>
        </div>
      )}

      <Panel title="Knowledge documents" subtitle="Indexed source documents and their chunk counts">
        <div className="surface-body">
          {documentsError ? (
            <Notice tone="error">{documentsError}</Notice>
          ) : isLoadingDocuments ? (
            <p className="field-help" role="status">Loading knowledge documents...</p>
          ) : documents.length > 0 ? (
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr><th>Document</th><th>Chunks</th></tr>
                </thead>
                <tbody>
                  {documents.map(({ document, chunks }) => (
                    <tr key={document}>
                      <td>{document}</td>
                      <td>{chunks}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              title="No knowledge documents available"
              description="Upload a PDF to add it to the indexed knowledge base."
              icon={BookOpen}
            />
          )}
        </div>
      </Panel>
    </>
  )
}

export default KnowledgeBase
