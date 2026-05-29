# AgentIAM Architecture

AgentIAM is an Identity and Access Management (IAM) layer for AI Agents. It provides a centralized service to evaluate, enforce, and audit permissions when AI agents interact with external tools, APIs, and resources.

## System Overview

The system consists of the following high-level components:

1.  **Frontend (Dashboard)**: A React-based web application for managing agents, policies, and viewing audit logs.
2.  **Backend (API & Authz Engine)**: A FastAPI Python service that handles policy evaluation, user authentication, and data persistence.
3.  **Database**: A PostgreSQL database for storing agents, users, YAML-based policies, and audit logs.

## Backend Architecture

The backend follows Clean Architecture and Domain-Driven Design principles:

### Layers

- **API Layer (`app/api`)**: FastAPI routers and endpoints. Handles HTTP requests, input validation (via Pydantic schemas), and response formatting.
- **Service Layer (`app/services`)**: Business logic. `AuthzService` handles the core permission evaluation logic against YAML policies. `PolicyService` handles YAML validation.
- **Repository Layer (`app/repositories`)**: Data access layer using SQLAlchemy. Abstracts database operations from the services.
- **Models (`app/models`)**: SQLAlchemy ORM models defining the database schema.
- **Schemas (`app/schemas`)**: Pydantic models for data validation, serialization, and API definitions.

### Authentication & Authorization (Admin Users)

- Standard JWT-based authentication for dashboard users.
- Role-Based Access Control (RBAC) is implemented (Admin vs Viewer roles).
- Passwords are hashed using bcrypt.

### Agent Authorization Flow

When an agent wants to perform an action:

1.  A system (e.g., LangChain tool wrapper, API Gateway) sends a `POST /api/v1/audit/check-permission` request with `agent_id`, `resource`, and `action`.
2.  `AuthzService.check_permission` fetches the Agent's policy.
3.  The policy (stored as YAML) is parsed and evaluated.
    - Explicit matches (e.g., `action: true` or `action: false`) take precedence.
    - Wildcards (e.g., `*: true`) are supported at the resource and action levels.
4.  The decision (ALLOW/DENY) is recorded via `AuditLogRepository`.
5.  The response is returned to the caller.

## Frontend Architecture

- **Framework**: React 18 with TypeScript.
- **Build Tool**: Vite for fast bundling and HMR.
- **Routing**: React Router (to be implemented for multi-page dashboard).
- **Styling**: Vanilla CSS with CSS Variables for theme support (Dark mode readiness).

## Database Schema

- `User`: Dashboard administrators.
- `Agent`: Represents an AI agent identity.
- `Policy`: A 1-to-1 relationship with `Agent`. Contains the YAML definition of permissions.
- `AuditLog`: Immutable ledger of all authorization decisions.

## Security Considerations

- **Policy Validation**: YAML policies are strictly validated upon creation/update to prevent injection or malformed logic.
- **Audit Immutability**: Currently stored in standard tables. Future iterations should add cryptographic verification to detect tampering.
- **API Protection**: The `check-permission` endpoint currently allows open access for MVP demonstration but is designed to be secured via API keys or internal networking.
