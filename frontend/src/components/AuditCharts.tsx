import { useState, useEffect, useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface AuditLogEntry {
  id: number;
  agent_id: number;
  resource: string;
  action: string;
  decision: boolean;
  reason: string | null;
  timestamp: string;
}

interface TimeSeriesPoint {
  date: string;
  allow: number;
  deny: number;
}

interface AgentBreakdown {
  agent: string;
  allow: number;
  deny: number;
}

/**
 * Aggregate raw audit log entries into daily ALLOW / DENY counts.
 */
function aggregateByDay(logs: AuditLogEntry[]): TimeSeriesPoint[] {
  const buckets = new Map<string, { allow: number; deny: number }>();

  for (const log of logs) {
    const day = log.timestamp.slice(0, 10); // YYYY-MM-DD
    const entry = buckets.get(day) ?? { allow: 0, deny: 0 };
    if (log.decision) {
      entry.allow += 1;
    } else {
      entry.deny += 1;
    }
    buckets.set(day, entry);
  }

  return Array.from(buckets.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, counts]) => ({ date, ...counts }));
}

/**
 * Aggregate raw audit log entries into per-agent ALLOW / DENY counts.
 */
function aggregateByAgent(logs: AuditLogEntry[]): AgentBreakdown[] {
  const buckets = new Map<string, { allow: number; deny: number }>();

  for (const log of logs) {
    const key = `Agent #${log.agent_id}`;
    const entry = buckets.get(key) ?? { allow: 0, deny: 0 };
    if (log.decision) {
      entry.allow += 1;
    } else {
      entry.deny += 1;
    }
    buckets.set(key, entry);
  }

  return Array.from(buckets.entries())
    .map(([agent, counts]) => ({ agent, ...counts }))
    .sort((a, b) => b.allow + b.deny - (a.allow + a.deny));
}

/** Sample data for demo / development when no API is available. */
const SAMPLE_LOGS: AuditLogEntry[] = [
  { id: 1, agent_id: 1, resource: '/api/data', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-25T10:00:00Z' },
  { id: 2, agent_id: 1, resource: '/api/data', action: 'write', decision: false, reason: 'Write not permitted', timestamp: '2026-05-25T10:05:00Z' },
  { id: 3, agent_id: 2, resource: '/api/users', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-25T11:00:00Z' },
  { id: 4, agent_id: 1, resource: '/api/data', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-26T09:00:00Z' },
  { id: 5, agent_id: 3, resource: '/api/admin', action: 'delete', decision: false, reason: 'Admin access denied', timestamp: '2026-05-26T09:30:00Z' },
  { id: 6, agent_id: 2, resource: '/api/users', action: 'write', decision: true, reason: 'Policy allows', timestamp: '2026-05-26T10:00:00Z' },
  { id: 7, agent_id: 1, resource: '/api/data', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-27T08:00:00Z' },
  { id: 8, agent_id: 2, resource: '/api/users', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-27T08:30:00Z' },
  { id: 9, agent_id: 3, resource: '/api/admin', action: 'read', decision: false, reason: 'Admin read denied', timestamp: '2026-05-27T09:00:00Z' },
  { id: 10, agent_id: 1, resource: '/api/data', action: 'write', decision: false, reason: 'Write not permitted', timestamp: '2026-05-27T09:30:00Z' },
  { id: 11, agent_id: 2, resource: '/api/users', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-28T10:00:00Z' },
  { id: 12, agent_id: 1, resource: '/api/data', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-28T10:30:00Z' },
  { id: 13, agent_id: 3, resource: '/api/admin', action: 'write', decision: false, reason: 'Admin write denied', timestamp: '2026-05-28T11:00:00Z' },
  { id: 14, agent_id: 1, resource: '/api/data', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-29T08:00:00Z' },
  { id: 15, agent_id: 2, resource: '/api/users', action: 'write', decision: true, reason: 'Policy allows', timestamp: '2026-05-29T08:30:00Z' },
  { id: 16, agent_id: 3, resource: '/api/admin', action: 'read', decision: false, reason: 'Admin read denied', timestamp: '2026-05-29T09:00:00Z' },
  { id: 17, agent_id: 1, resource: '/api/data', action: 'write', decision: false, reason: 'Write not permitted', timestamp: '2026-05-30T10:00:00Z' },
  { id: 18, agent_id: 2, resource: '/api/users', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-30T10:30:00Z' },
  { id: 19, agent_id: 1, resource: '/api/data', action: 'read', decision: true, reason: 'Policy allows', timestamp: '2026-05-31T08:00:00Z' },
  { id: 20, agent_id: 3, resource: '/api/admin', action: 'delete', decision: false, reason: 'Admin delete denied', timestamp: '2026-05-31T09:00:00Z' },
];

interface AuditChartsProps {
  /** API base URL (e.g. "http://localhost:8000/api/v1"). If not provided, uses sample data. */
  apiBaseUrl?: string;
  /** Auth token for the audit log API. */
  authToken?: string;
}

export function AuditCharts({ apiBaseUrl, authToken }: AuditChartsProps) {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agentFilter, setAgentFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({
    start: '',
    end: '',
  });

  useEffect(() => {
    async function fetchLogs() {
      if (!apiBaseUrl) {
        // Use sample data when no API is configured
        setLogs(SAMPLE_LOGS);
        setLoading(false);
        return;
      }

      try {
        const headers: Record<string, string> = {};
        if (authToken) {
          headers['Authorization'] = `Bearer ${authToken}`;
        }

        const response = await fetch(`${apiBaseUrl}/audit/?limit=1000`, { headers });
        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }
        const data: AuditLogEntry[] = await response.json();
        setLogs(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch audit logs');
        // Fall back to sample data on error
        setLogs(SAMPLE_LOGS);
      } finally {
        setLoading(false);
      }
    }

    fetchLogs();
  }, [apiBaseUrl, authToken]);

  // Apply filters
  const filteredLogs = useMemo(() => {
    let result = logs;

    if (agentFilter !== 'all') {
      const agentId = parseInt(agentFilter, 10);
      result = result.filter((log) => log.agent_id === agentId);
    }

    if (dateRange.start) {
      result = result.filter((log) => log.timestamp.slice(0, 10) >= dateRange.start);
    }
    if (dateRange.end) {
      result = result.filter((log) => log.timestamp.slice(0, 10) <= dateRange.end);
    }

    return result;
  }, [logs, agentFilter, dateRange]);

  const timeSeriesData = useMemo(() => aggregateByDay(filteredLogs), [filteredLogs]);
  const agentBreakdown = useMemo(() => aggregateByAgent(filteredLogs), [filteredLogs]);

  const uniqueAgents = useMemo(() => {
    const ids = new Set(logs.map((l) => l.agent_id));
    return Array.from(ids).sort((a, b) => a - b);
  }, [logs]);

  const summaryStats = useMemo(() => {
    const total = filteredLogs.length;
    const allowed = filteredLogs.filter((l) => l.decision).length;
    const denied = total - allowed;
    const denyRate = total > 0 ? ((denied / total) * 100).toFixed(1) : '0';
    return { total, allowed, denied, denyRate };
  }, [filteredLogs]);

  if (loading) {
    return <div className="audit-charts-loading">Loading audit data…</div>;
  }

  return (
    <div className="audit-charts">
      <h2>Audit Log Dashboard</h2>

      {error && (
        <div className="audit-charts-error">
          ⚠️ Could not connect to API — showing sample data. ({error})
        </div>
      )}

      {/* Filters */}
      <div className="audit-filters">
        <label>
          Agent:
          <select value={agentFilter} onChange={(e) => setAgentFilter(e.target.value)}>
            <option value="all">All Agents</option>
            {uniqueAgents.map((id) => (
              <option key={id} value={id}>
                Agent #{id}
              </option>
            ))}
          </select>
        </label>
        <label>
          From:
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange((prev) => ({ ...prev, start: e.target.value }))}
          />
        </label>
        <label>
          To:
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange((prev) => ({ ...prev, end: e.target.value }))}
          />
        </label>
      </div>

      {/* Summary cards */}
      <div className="audit-summary">
        <div className="summary-card">
          <span className="summary-value">{summaryStats.total}</span>
          <span className="summary-label">Total Checks</span>
        </div>
        <div className="summary-card allow">
          <span className="summary-value">{summaryStats.allowed}</span>
          <span className="summary-label">Allowed</span>
        </div>
        <div className="summary-card deny">
          <span className="summary-value">{summaryStats.denied}</span>
          <span className="summary-label">Denied</span>
        </div>
        <div className="summary-card rate">
          <span className="summary-value">{summaryStats.denyRate}%</span>
          <span className="summary-label">Deny Rate</span>
        </div>
      </div>

      {/* Line chart — decisions over time */}
      <div className="chart-container">
        <h3>Authorization Decisions Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="allow" stroke="#22c55e" strokeWidth={2} name="Allowed" />
            <Line type="monotone" dataKey="deny" stroke="#ef4444" strokeWidth={2} name="Denied" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Bar chart — per-agent breakdown */}
      <div className="chart-container">
        <h3>Decisions by Agent</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={agentBreakdown}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="agent" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Bar dataKey="allow" fill="#22c55e" name="Allowed" />
            <Bar dataKey="deny" fill="#ef4444" name="Denied" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
