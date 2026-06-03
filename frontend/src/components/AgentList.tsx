import { useState, useEffect, useCallback } from 'react';

interface Agent {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

interface AgentListProps {
  apiBase?: string;
  onSelectAgent?: (id: number) => void;
}

export function AgentList({ apiBase = '/api/v1', onSelectAgent }: AgentListProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const [newName, setNewName] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const fetchAgents = useCallback(async (signal?: AbortSignal) => {
    try {
      const response = await fetch(`${apiBase}/agents/`, { signal });
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
  }, [apiBase]);

  useEffect(() => {
    const controller = new AbortController();
    // Use microtask to avoid synchronous state update warning in React 19
    Promise.resolve().then(() => {
      if (!controller.signal.aborted) {
        fetchAgents(controller.signal);
      }
    });
    return () => controller.abort();
  }, [fetchAgents]);

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;

    setIsCreating(true);
    try {
      const response = await fetch(`${apiBase}/agents/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newName,
          description: newDescription || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create agent');
      }

      setNewName('');
      setNewDescription('');
      await fetchAgents();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error creating agent');
    } finally {
      setIsCreating(false);
    }
  };

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
      <div className="agent-list-header">
        <h2>Agents</h2>
        <form className="create-agent-form" onSubmit={handleCreateAgent}>
          <input
            type="text"
            placeholder="Agent Name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            disabled={isCreating}
            required
          />
          <input
            type="text"
            placeholder="Description (optional)"
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            disabled={isCreating}
          />
          <button type="submit" disabled={isCreating || !newName.trim()}>
            {isCreating ? 'Creating...' : 'Add Agent'}
          </button>
        </form>
      </div>
      
      <table className="agent-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Created</th>
            <th>Actions</th>
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
              <td className="agent-actions-cell">
                <button
                  className="edit-policy-btn"
                  onClick={() => onSelectAgent?.(agent.id)}
                >
                  Edit Policy
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
