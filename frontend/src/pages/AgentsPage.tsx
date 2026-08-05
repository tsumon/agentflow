import { useEffect, useState } from 'react';
import { Play, Zap, ChevronRight } from 'lucide-react';
import { api, Agent } from '../services/api';

interface Props {
  onNavigate: (page: 'playground') => void;
}

export default function AgentsPage({ onNavigate }: Props) {
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    api.listAgents().then(setAgents).catch(console.error);
  }, []);

  const roleClass = (role: string) => {
    const map: Record<string, string> = {
      planner: 'role-planner',
      executor: 'role-executor',
      reviewer: 'role-reviewer',
    };
    return map[role] || '';
  };

  return (
    <div>
      <h1 className="welcome-title">AgentFlow</h1>
      <p className="welcome-sub">
        Enterprise Multi-Agent Collaboration Platform — Plan, Execute, Review
      </p>

      <div className="card">
        <div className="card-header">
          <Zap size={18} color="var(--accent)" />
          Pipeline: Plan → Execute → Review
        </div>
        <div className="pipeline-status">
          <div className="pipeline-step active">
            <Bot size={14} /> Planner
          </div>
          <span className="pipeline-arrow">→</span>
          <div className="pipeline-step">
            <Play size={14} /> Executor
          </div>
          <span className="pipeline-arrow">→</span>
          <div className="pipeline-step">
            <Zap size={14} /> Reviewer
          </div>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 12 }}>
          Tasks flow through three specialized agents: a Planner decomposes goals,
          an Executor carries out steps with tools, and a Reviewer validates quality.
        </p>
        <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => onNavigate('playground')}>
          Try it now <ChevronRight size={14} />
        </button>
      </div>

      <h3 style={{ marginBottom: 16, fontSize: '1rem' }}>Available Agents</h3>
      <div className="agent-grid">
        {agents.map((agent) => (
          <div key={agent.role} className="agent-card">
            <span className={`role-badge ${roleClass(agent.role)}`}>{agent.role}</span>
            <h4>{agent.name}</h4>
            <p>{agent.description}</p>
            <div className="tool-tags">
              {agent.tools.map((t) => (
                <span key={t} className="tool-tag">{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Bot({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );
}
