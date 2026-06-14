import { useState, useEffect, useCallback } from 'react';
import './AuditLogList.css';

interface AuditLog {
  id: number;
  agent_id: number;
  resource: string;
  action: string;
  decision: boolean;
  reason: string | null;
  timestamp: string;
}

interface AuditLogListProps {
  apiBase?: string;
}

export function AuditLogList({ apiBase = '/api/v1' }: AuditLogListProps) {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = useCallback(async (signal?: AbortSignal) => {
    try {
      const response = await fetch(`${apiBase}/audit/?limit=50`, { signal });
      if (!response.ok) {
        throw new Error(`Failed to fetch audit logs: ${response.statusText}`);
      }
      const data = await response.json();
      setLogs(data);
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      setError(err instanceof Error ? err.message : 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  useEffect(() => {
    const controller = new AbortController();
    // Use microtask to avoid synchronous state update warning in React 19
    Promise.resolve().then(() => {
      if (!controller.signal.aborted) {
        fetchLogs(controller.signal);
      }
    });
    return () => controller.abort();
  }, [fetchLogs]);

  if (loading) return <div className="audit-log-loading">Loading logs...</div>;
  if (error) return <div className="audit-log-error">Error: {error}</div>;

  return (
    <div className="audit-log-list">
      <div className="audit-log-header">
        <h2>Recent Audit Logs</h2>
        <button className="refresh-btn" onClick={() => fetchLogs()}>Refresh</button>
      </div>
      
      <div className="table-container">
        <table className="audit-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Agent ID</th>
              <th>Resource</th>
              <th>Action</th>
              <th>Decision</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className={log.decision ? 'row-allow' : 'row-deny'}>
                <td className="timestamp-cell">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="agent-id-cell">#{log.agent_id}</td>
                <td className="resource-cell"><code>{log.resource}</code></td>
                <td className="action-cell"><span className="action-tag">{log.action}</span></td>
                <td className="decision-cell">
                  <span className={`decision-badge ${log.decision ? 'allow' : 'deny'}`}>
                    {log.decision ? 'ALLOW' : 'DENY'}
                  </span>
                </td>
                <td className="reason-cell">{log.reason}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '24px' }}>
                  No audit logs found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
