import { useState, useEffect, useCallback } from 'react';

interface Agent {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

interface AgentListProps {
  apiBase?: string;
}

export function AgentList({ apiBase = '/api/v1' }: AgentListProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<number | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const fetchAgents = async () => {
      try {
        const response = await fetch(`${apiBase}/agents/`, { signal: controller.signal });
        if (!response.ok) {
          throw new Error(`Failed to fetch agents: ${response.statusText}`);
        }
        const data = await response.json();
        setAgents(data);
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') return;
        setError(err instanceof Error ? err.message : 'Failed to load agents');
      } finally {
        setLoading(false);
      }
    };

    fetchAgents();
    return () => controller.abort();
  }, [apiBase]);

  const copyToClipboard = useCallback(async (agentId: number) => {
    const idString = String(agentId);
    try {
      await navigator.clipboard.writeText(idString);
      setCopiedId(agentId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = idString;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      const copied = document.execCommand('copy');
      document.body.removeChild(textarea);
      if (!copied) {
        throw new Error('Clipboard copy failed');
      }
      setCopiedId(agentId);
      setTimeout(() => setCopiedId(null), 2000);
    }
  }, []);

  if (loading) {
    return <div className="agent-list-loading">Loading agents...</div>;
  }

  if (error) {
    return <div className="agent-list-error">Error: {error}</div>;
  }

  if (agents.length === 0) {
    return <div className="agent-list-empty">No agents found.</div>;
  }

  return (
    <div className="agent-list">
      <h2>Agents</h2>
      <table className="agent-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {agents.map((agent) => (
            <tr key={agent.id}>
              <td className="agent-id-cell">
                <span className="agent-id">{agent.id}</span>
                <button
                  className="copy-btn"
                  onClick={() => copyToClipboard(agent.id)}
                  title="Copy ID"
                >
                  {copiedId === agent.id ? '✓' : '📋'}
                </button>
                {copiedId === agent.id && <span className="copy-toast">Copied!</span>}
              </td>
              <td className="agent-name-cell">
                <span className="agent-name">{agent.name}</span>
              </td>
              <td className="agent-desc-cell">
                <span className="agent-description">{agent.description || 'No description'}</span>
              </td>
              <td className="agent-date-cell">
                {new Date(agent.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
