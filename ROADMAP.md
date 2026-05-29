# AgentIAM Roadmap

This roadmap outlines the planned development and feature milestones for AgentIAM.

## MVP (Current)
*Completed Features:*
- Core backend architecture with FastAPI and PostgreSQL.
- React/Vite frontend scaffold.
- Basic YAML policy evaluation engine.
- Agent creation and management.
- Simple audit logging for permission checks.
- Issue: "Policy validation fails on empty resource list" has been fixed.

*Pending Features:*
- Initial release of the React Dashboard for Agents and Audit Logs.
- Secure YAML validation hardening.
- Basic frontend integration with the backend API.

## v0.2
*Features:*
- Implement Dark Mode in the frontend dashboard.
- Policy editor with YAML syntax highlighting.
- Add "Copy to Clipboard" for Agent IDs.

*Security Improvements:*
- Support CIDR-based IP restrictions in policies.
- Implement rate limiting for `check_permission` endpoint.
- Enforce password complexity requirements.

*Technical Debt:*
- Add structured logging across the backend service.
- Optimize audit log database queries with indexes.

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
