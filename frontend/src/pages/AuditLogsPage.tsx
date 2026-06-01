import { useState, useEffect, useCallback } from 'react';

interface AuditLog {
  id: number;
  timestamp: string;
  agent_id: number;
  resource: string;
  action: string;
  decision: boolean;
  reason: string | null;
}

interface AuditLogsPageProps {
  apiBase?: string;
}

export function AuditLogsPage({ apiBase = '/api/v1' }: AuditLogsPageProps) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [agentIdFilter, setAgentIdFilter] = useState('');
  const [resourceFilter, setResourceFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [decisionFilter, setDecisionFilter] = useState<string>('');

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);

    const params = new URLSearchParams();
    if (agentIdFilter) params.set('agent_id', agentIdFilter);
    if (resourceFilter) params.set('resource', resourceFilter);
    if (actionFilter) params.set('action', actionFilter);
    if (decisionFilter !== '') params.set('decision', decisionFilter);
    params.set('limit', '100');

    try {
      const response = await fetch(`${apiBase}/audit/?${params.toString()}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch audit logs: ${response.statusText}`);
      }
      const data = await response.json();
      setLogs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  }, [apiBase, agentIdFilter, resourceFilter, actionFilter, decisionFilter]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleApplyFilters = () => {
    fetchLogs();
  };

  const handleClearFilters = () => {
    setAgentIdFilter('');
    setResourceFilter('');
    setActionFilter('');
    setDecisionFilter('');
  };

  const formatTimestamp = (ts: string) => {
    try {
      return new Date(ts).toLocaleString();
    } catch {
      return ts;
    }
  };

  return (
    <div className="audit-logs-page">
      <h2>Audit Logs</h2>

      {/* Filter bar */}
      <div className="filter-bar">
        <div className="filter-field">
          <label htmlFor="filter-agent-id">Agent ID</label>
          <input
            id="filter-agent-id"
            type="number"
            placeholder="e.g. 42"
            value={agentIdFilter}
            onChange={(e) => setAgentIdFilter(e.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="filter-resource">Resource</label>
          <input
            id="filter-resource"
            type="text"
            placeholder="e.g. tickets"
            value={resourceFilter}
            onChange={(e) => setResourceFilter(e.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="filter-action">Action</label>
          <input
            id="filter-action"
            type="text"
            placeholder="e.g. read"
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
          />
        </div>

        <div className="filter-field">
          <label htmlFor="filter-decision">Decision</label>
          <select
            id="filter-decision"
            value={decisionFilter}
            onChange={(e) => setDecisionFilter(e.target.value)}
          >
            <option value="">All</option>
            <option value="true">ALLOW</option>
            <option value="false">DENY</option>
          </select>
        </div>

        <div className="filter-actions">
          <button className="btn-apply" onClick={handleApplyFilters}>
            Apply
          </button>
          <button className="btn-clear" onClick={handleClearFilters}>
            Clear
          </button>
        </div>
      </div>

      {/* Results */}
      {loading && <div className="audit-logs-loading">Loading audit logs...</div>}

      {error && <div className="audit-logs-error">Error: {error}</div>}

      {!loading && !error && logs.length === 0 && (
        <div className="audit-logs-empty">No audit logs found matching the filters.</div>
      )}

      {!loading && !error && logs.length > 0 && (
        <table className="audit-logs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Timestamp</th>
              <th>Agent</th>
              <th>Resource</th>
              <th>Action</th>
              <th>Decision</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{log.id}</td>
                <td>{formatTimestamp(log.timestamp)}</td>
                <td>{log.agent_id}</td>
                <td>{log.resource}</td>
                <td>{log.action}</td>
                <td>
                  <span className={`decision-badge ${log.decision ? 'allow' : 'deny'}`}>
                    {log.decision ? 'ALLOW' : 'DENY'}
                  </span>
                </td>
                <td className="reason-cell">{log.reason || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
