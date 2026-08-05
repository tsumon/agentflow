import { useState } from 'react';
import { Bot, Play, BookOpen, Settings } from 'lucide-react';
import AgentsPage from './pages/AgentsPage';
import PlaygroundPage from './pages/PlaygroundPage';
import KnowledgePage from './pages/KnowledgePage';

type Page = 'agents' | 'playground' | 'knowledge';

const NAV_ITEMS: { id: Page; label: string; icon: React.ReactNode }[] = [
  { id: 'agents', label: 'Agents', icon: <Bot /> },
  { id: 'playground', label: 'Playground', icon: <Play /> },
  { id: 'knowledge', label: 'Knowledge', icon: <BookOpen /> },
];

export default function App() {
  const [page, setPage] = useState<Page>('agents');

  const renderPage = () => {
    switch (page) {
      case 'agents': return <AgentsPage onNavigate={setPage} />;
      case 'playground': return <PlaygroundPage />;
      case 'knowledge': return <KnowledgePage />;
    }
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="dot" />
          <span>AgentFlow</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(({ id, label, icon }) => (
            <button
              key={id}
              className={`nav-item ${page === id ? 'active' : ''}`}
              onClick={() => setPage(id)}
            >
              {icon}
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <div style={{ padding: '0 20px', marginTop: 'auto' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            AgentFlow v1.0.0
          </div>
        </div>
      </aside>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}
