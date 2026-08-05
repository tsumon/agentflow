import { useEffect, useState, useCallback } from 'react';
import { Plus, Trash2, Search, FileText } from 'lucide-react';
import { api, KnowledgeDoc } from '../services/api';

export default function KnowledgePage() {
  const [docs, setDocs] = useState<KnowledgeDoc[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [docId, setDocId] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[] | null>(null);

  const loadDocs = useCallback(async () => {
    try {
      const d = await api.listKnowledge();
      setDocs(d);
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => { loadDocs(); }, [loadDocs]);

  const handleAdd = async () => {
    if (!docId.trim() || !title.trim()) return;
    try {
      await api.addKnowledge(docId, title, content);
      setDocId(''); setTitle(''); setContent(''); setShowAdd(false);
      await loadDocs();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteKnowledge(id);
      await loadDocs();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const res = await api.searchKnowledge(searchQuery);
      setSearchResults(res.results);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 4 }}>Knowledge Base</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Manage documents for RAG-powered agent context
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
          <Plus size={14} /> Add Document
        </button>
      </div>

      {/* Add form */}
      {showAdd && (
        <div className="card">
          <div className="card-header">Add New Document</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 4 }}>Document ID</label>
              <input className="input" value={docId} onChange={(e) => setDocId(e.target.value)} placeholder="unique-doc-id" />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 4 }}>Title</label>
              <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Document title" />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 4 }}>Content</label>
              <textarea className="input" value={content} onChange={(e) => setContent(e.target.value)} placeholder="Document content..." rows={6} />
            </div>
            <div>
              <button className="btn btn-primary" onClick={handleAdd}>
                <Plus size={14} /> Save Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="card">
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            className="input"
            placeholder="Search knowledge base..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            style={{ flex: 1 }}
          />
          <button className="btn btn-primary" onClick={handleSearch}>
            <Search size={14} /> Search
          </button>
        </div>

        {searchResults && (
          <div style={{ marginTop: 16 }}>
            <h4 style={{ fontSize: '0.85rem', marginBottom: 8, color: 'var(--text-secondary)' }}>
              {searchResults.length} results
            </h4>
            {searchResults.map((doc) => (
              <div key={doc.id} className="knowledge-item" style={{ marginBottom: 8 }}>
                <div>
                  <h5>{doc.title}</h5>
                  <div className="meta">{doc.content?.substring(0, 150)}...</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document list */}
      <h3 style={{ fontSize: '1rem', marginBottom: 12 }}>
        <FileText size={14} style={{ marginRight: 6 }} />
        All Documents ({docs.length})
      </h3>
      <div className="knowledge-list">
        {docs.length === 0 ? (
          <div className="empty-state">
            <FileText size={32} />
            <p>No documents yet. Add some to power your agents with context.</p>
          </div>
        ) : (
          docs.map((doc) => (
            <div key={doc.id} className="knowledge-item">
              <div>
                <h5>{doc.title}</h5>
                <div className="meta">{doc.id} — {doc.content_preview?.substring(0, 100)}...</div>
              </div>
              <button
                className="btn btn-danger"
                onClick={() => handleDelete(doc.id)}
                style={{ padding: '4px 8px' }}
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
