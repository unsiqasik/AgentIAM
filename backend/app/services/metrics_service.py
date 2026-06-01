"""
Custom Prometheus metrics for AgentIAM business logic.

Provides:
- Policy evaluation metrics
- Decision metrics
- Agent activity metrics
"""

from prometheus_client import Counter, Histogram, Gauge
import time
from typing import Optional

# Policy evaluation metrics
POLICY_EVALUATION_TOTAL = Counter(
    'agentiam_policy_evaluation_total',
    'Total number of policy evaluations',
    ['resource', 'action', 'decision']
)

POLICY_EVALUATION_DURATION = Histogram(
    'agentiam_policy_evaluation_duration_seconds',
    'Time spent evaluating policies',
    ['resource', 'action'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Decision metrics
DECISIONS_TOTAL = Counter(
    'agentiam_decisions_total',
    'Total number of access decisions',
    ['decision']
)

DECISIONS_PER_SECOND = Gauge(
    'agentiam_decisions_per_second',
    'Rate of decisions per second'
)

# Agent activity metrics
ACTIVE_AGENTS = Gauge(
    'agentiam_active_agents',
    'Number of active agents'
)

AGENT_REQUESTS_TOTAL = Counter(
    'agentiam_agent_requests_total',
    'Total requests per agent',
    ['agent_id']
)

# Audit log metrics
AUDIT_LOG_ENTRIES_TOTAL = Counter(
    'agentiam_audit_log_entries_total',
    'Total number of audit log entries'
)

AUDIT_LOG_INTEGRITY_ERRORS = Counter(
    'agentiam_audit_log_integrity_errors_total',
    'Total number of audit log integrity errors detected'
)


class MetricsService:
    """Service for recording custom Prometheus metrics."""

    def __init__(self):
        self._decision_count = 0
        self._last_decision_time = time.time()

    def record_policy_evaluation(
        self,
        resource: str,
        action: str,
        decision: bool,
        duration: float
    ):
        """Record a policy evaluation."""
        decision_str = "allowed" if decision else "denied"
        
        POLICY_EVALUATION_TOTAL.labels(
            resource=resource,
            action=action,
            decision=decision_str
        ).inc()
        
        POLICY_EVALUATION_DURATION.labels(
            resource=resource,
            action=action
        ).observe(duration)

    def record_decision(self, decision: bool):
        """Record an access decision."""
        decision_str = "allowed" if decision else "denied"
        DECISIONS_TOTAL.labels(decision=decision_str).inc()
        
        # Update decisions per second
        self._decision_count += 1
        current_time = time.time()
        time_diff = current_time - self._last_decision_time
        
        if time_diff >= 1.0:
            DECISIONS_PER_SECOND.set(self._decision_count / time_diff)
            self._decision_count = 0
            self._last_decision_time = current_time

    def record_agent_request(self, agent_id: int):
        """Record a request from an agent."""
        AGENT_REQUESTS_TOTAL.labels(agent_id=str(agent_id)).inc()

    def set_active_agents(self, count: int):
        """Set the number of active agents."""
        ACTIVE_AGENTS.set(count)

    def record_audit_log_entry(self):
        """Record an audit log entry."""
        AUDIT_LOG_ENTRIES_TOTAL.inc()

    def record_integrity_error(self):
        """Record an audit log integrity error."""
        AUDIT_LOG_INTEGRITY_ERRORS.inc()


# Singleton instance
metrics_service = MetricsService()
