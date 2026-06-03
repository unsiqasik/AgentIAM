# AgentIAM Roadmap

This roadmap outlines the planned development and feature milestones for AgentIAM.

## MVP (Completed)
*Features:*
- Core backend architecture with FastAPI and PostgreSQL.
- React/Vite frontend dashboard with full API integration.
- Dynamic YAML policy evaluation engine with CIDR IP restrictions.
- Agent management (List, Create, Select).
- Audit & Analytics Dashboard (Charts + Live Log Feed).
- Secure YAML validation and DoS protection.
- Structured JSON logging.

## v0.2 (In Progress)
*Features:*
- Implement Dark Mode in the frontend dashboard.
- Policy versioning and history tracking.
- Add "Copy to Clipboard" for Agent IDs (Done).

*Security Improvements:*
- Support CIDR-based IP restrictions in policies (Done).
- Implement rate limiting for `check_permission` endpoint.
- Enforce password complexity requirements (Done).

*Technical Debt:*
- Add structured logging across the backend service (Done).
- Optimize audit log database queries with indexes (Done).

## v0.3
*Integrations:*
- LangChain / LlamaIndex official integration guides and examples.
- Webhooks for Slack/Discord notifications on DENIED critical actions.

*Observability:*
- Data visualization for audit logs (charts showing ALLOW vs DENY).
- Search and filter capabilities for the Audit Logs page.

## v0.4
*Scaling:*
- Implement policy versioning and history.
- Support for temporary/expiring policies (`expires_at`).

*Performance:*
- Prometheus metrics endpoint.
- Caching layer for frequently accessed policies.

## v0.5
*Enterprise Features:*
- Role-Based Access Control (RBAC) UI for dashboard users.
- Support multi-factor authentication (MFA) for administrators.
- Audit Log cryptographic integrity checks.
- "Dry Run" mode for testing policies without enforcement.

## v1.0
*Production Ready:*
- OPA (Open Policy Agent) integration research and potential migration.
- Comprehensive security audit and penetration testing.
- Official Docker images published to DockerHub.
- High-availability deployment guides (Kubernetes/Helm).
