import { useState } from 'react';
import { Send, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { api, TaskResult } from '../services/api';

export default function PlaygroundPage() {
  const [task, setTask] = useState('');
  const [kbQuery, setKbQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TaskResult | null>(null);
  const [error, setError] = useState('');

  const handleRun = async () => {
    if (!task.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await api.runTask(task, kbQuery);
      setResult(res);
    } catch (e: any) {
      setError(e.message || 'Task execution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: 8 }}>Playground</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 24 }}>
        Run tasks through the AgentFlow pipeline and see how Plan → Execute → Review works.
      </p>

      <div className="card">
        <div className="card-header">Run Task</div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 4 }}>
            Task Description
          </label>
          <textarea
            className="input"
            placeholder="Describe what you want the agents to do...&#10;&#10;Example: Analyze the pros and cons of microservices vs monolith architecture and give a recommendation."
            value={task}
            onChange={(e) => setTask(e.target.value)}
            rows={4}
          />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 4 }}>
            Knowledge Base Query (optional)
          </label>
          <input
            className="input"
            placeholder="Search knowledge base for context..."
            value={kbQuery}
            onChange={(e) => setKbQuery(e.target.value)}
          />
        </div>

        <button
          className="btn btn-primary"
          onClick={handleRun}
          disabled={loading || !task.trim()}
        >
          {loading ? (
            <><Loader2 size={14} className="spinner" style={{ borderColor: 'transparent', borderTopColor: 'white' }} /> Running...</>
          ) : (
            <><Send size={14} /> Execute Pipeline</>
          )}
        </button>
      </div>

      {error && (
        <div className="card" style={{ borderColor: 'var(--danger)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--danger)' }}>
            <AlertCircle size={16} /> {error}
          </div>
        </div>
      )}

      {result && (
        <>
          {/* Plan */}
          <div className="card">
            <div className="card-header">
              <CheckCircle size={16} color="var(--accent)" />
              Plan {result.plan?.estimated_complexity && (
                <span className={`badge ${result.plan.estimated_complexity === 'high' ? 'badge-warning' : 'badge-info'}`}>
                  {result.plan.estimated_complexity}
                </span>
              )}
            </div>
            {result.plan?.goal && (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 12 }}>
                Goal: {result.plan.goal}
              </p>
            )}
            {result.plan?.steps ? (
              <div>
                {result.plan.steps.map((step: any) => (
                  <div key={step.step} style={{
                    padding: '10px 14px',
                    background: 'var(--bg-secondary)',
                    borderRadius: 'var(--radius)',
                    marginBottom: 6,
                    fontSize: '0.85rem',
                    borderLeft: `3px solid var(--accent)`,
                  }}>
                    <strong>Step {step.step}: {step.name}</strong>
                    <div style={{ color: 'var(--text-secondary)', marginTop: 2 }}>{step.action}</div>
                    {step.tool && <span className="tool-tag" style={{ marginTop: 4 }}>{step.tool}</span>}
                  </div>
                ))}
              </div>
            ) : (
              <div className="pre-block">{JSON.stringify(result.plan, null, 2)}</div>
            )}
          </div>

          {/* Execution */}
          <div className="card">
            <div className="card-header">
              <CheckCircle size={16} color="var(--success)" />
              Execution Result
            </div>
            <div className="pre-block">{result.execution_result}</div>
          </div>

          {/* Review */}
          <div className="card">
            <div className="card-header">
              <CheckCircle size={16} color="var(--warning)" />
              Review {result.review?.verdict && (
                <span className={`badge ${result.review.verdict === 'pass' ? 'badge-success' : 'badge-warning'}`}>
                  {result.review.verdict}
                  {result.review.score ? ` ${result.review.score}/10` : ''}
                </span>
              )}
            </div>
            {result.review?.strengths && (
              <div className="result-section">
                <h4>Strengths</h4>
                <ul style={{ paddingLeft: 20, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {result.review.strengths.map((s: string, i: number) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.review?.weaknesses && result.review.weaknesses.length > 0 && (
              <div className="result-section">
                <h4>Weaknesses</h4>
                <ul style={{ paddingLeft: 20, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {result.review.weaknesses.map((w: string, i: number) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>
            )}
            {!result.review?.verdict && (
              <div className="pre-block">{JSON.stringify(result.review, null, 2)}</div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
