# AgentIAM Architecture

AgentIAM is an Identity and Access Management (IAM) layer designed for AI Agents. It provides a centralized service to evaluate, enforce, and audit permissions when AI agents interact with external tools, APIs, and resources.

## System Overview

The system consists of the following high-level components:

1.  **Frontend (Dashboard)**: A React-based web application for managing agents, policies, and viewing audit logs.
2.  **Backend (API & Authz Engine)**: A FastAPI Python service that handles policy evaluation, user authentication, and data persistence.
3.  **Database**: A PostgreSQL database for storing agents, users, YAML-based policies, and audit logs.

## Infrastructure & CI/CD

AgentIAM follows modern DevOps practices with a robust CI/CD pipeline:

- **Continuous Integration**:
    - **Linting**: Automated code style enforcement via Ruff and Black.
    - **Type Checking**: Static analysis via MyPy.
    - **Security Scanning**: Automated vulnerability detection via Bandit and Safety.
    - **Testing**: Multi-version Python testing (3.10 - 3.13) via Pytest.
- **Continuous Deployment**: Docker-ready architecture for seamless containerized deployments.

## Backend Architecture

The backend follows Clean Architecture and Domain-Driven Design principles:

### Layers

- **API Layer (`app/api`)**: FastAPI routers and endpoints. Handles HTTP requests and input validation via Pydantic.
- **Service Layer (`app/services`)**: Business logic. `AuthzService` handles the core permission evaluation logic against YAML policies.
- **Repository Layer (`app/repositories`)**: Data access layer using SQLAlchemy.
- **Models & Schemas**: SQLAlchemy models for persistence and Pydantic schemas for data transfer.

## Security Posture

- **Policy Validation**: YAML policies are strictly validated upon creation/update to prevent injection or malformed logic.
- **Audit Ledger**: Every authorization decision is recorded in an immutable audit log.
- **Authentication**: JWT-based authentication for dashboard users with secure password hashing via bcrypt.

## Development Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and technical improvements.
