<div align="center">

# AgentIAM

**Identity & Access Management for AI Agents**

AI agents are becoming digital employees. Employees have permissions. AI agents should too.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)](#)
[![Security](https://img.shields.io/badge/security-audited-blue?style=flat-square)](#)
[![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/SHAURYASANYAL3/AgentIAM?style=flat-square&color=gold)](#)
[![Issues](https://img.shields.io/github/issues/SHAURYASANYAL3/AgentIAM?style=flat-square)](#)
[![Discord](https://img.shields.io/badge/Discord-Join_Community-5865F2?style=flat-square&logo=discord)](#)

</div>

---

## 🚨 The Problem

Current AI agents often receive **unrestricted access** to mission-critical infrastructure:

* GitHub Repositories
* Production Databases
* Payment APIs
* File Systems
* Internal Admin Tools

This is incredibly dangerous. An autonomous agent with uncontrolled access can accidentally drop a database table, leak a private key, or commit destructive code. 

**An AI agent running `DROP TABLE users;` because of a prompt injection shouldn't succeed.**

---

## 💡 The Solution

**AgentIAM** brings AWS IAM-style access control to autonomous agents.

It provides a centralized service to evaluate, enforce, and audit permissions when AI agents interact with external tools, APIs, and resources. By inserting an authorization layer between your agent and your infrastructure, you ensure that agents can only perform actions explicitly permitted by their assigned policies.

Why do AI systems need authorization? Because trust is not a security strategy.

---

## 🏗️ Architecture

```text
    ┌─────────────────┐
    │                 │
    │    AI Agent     │
    │                 │
    └────────┬────────┘
             │ Request to execute action
             ▼
    ┌─────────────────┐
    │                 │
    │    AgentIAM     │
    │                 │
    │  ┌───────────┐  │
    │  │  Policy   │  │
    │  │  Engine   │  │
    │  └─────┬─────┘  │
    │        │        │
    │  ┌─────▼─────┐  │
    │  │ Authz     │  │
    │  │ Layer     │  │
    │  └─────┬─────┘  │
    │        │        │
    │  ┌─────▼─────┐  │
    │  │  Audit    │  │
    │  │  Logger   │  │
    │  └───────────┘  │
    └────────┬────────┘
             │ Action Approved / Denied
             ▼
    ┌─────────────────┐
    │                 │
    │      Tools      │
    │  (DB, API, etc) │
    └─────────────────┘
```

---

## ✨ Features

### Available Features
* **Agent Registry**: Centralized management of your AI agents.
* **Policy Engine**: Define permissions using intuitive YAML-based policies.
* **Authorization Engine**: Dynamically evaluate permissions before execution.
* **Audit Logging**: Immutable ledger of all permission checks and decisions.
* **JWT Authentication**: Secure access to the management dashboard.
* **PostgreSQL Support**: Reliable and scalable data storage.
* **Docker Support**: Containerized for seamless deployment.
* **CI/CD**: Fully automated linting, testing, and security scanning.

### Planned Features
* **Dark Mode Dashboard**
* **LangChain / LlamaIndex Integrations**
* **Data Visualization for Audit Logs**
* **Policy Versioning & History**
* **Role-Based Access Control (RBAC)**

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/SHAURYASANYAL3/AgentIAM.git
cd AgentIAM
```

### 2. Run with Docker Compose
The easiest way to get started is using Docker:
```bash
docker compose up -d
```

* Dashboard: `http://localhost:3000`
* API Docs: `http://localhost:8000/docs`

### 3. Local Development Setup (Manual)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 📖 Example Usage

### 1. Define a Policy
Create a YAML policy restricting an agent to read-only database access:

```yaml
permissions:
  database:
    read: true
    write: false
    delete: false
```

> 📖 See the full [YAML Policy Schema Reference](docs/POLICY_SCHEMA.md) for all supported fields, wildcards, and examples.

### 2. Check Permission (API)
When the agent tries to perform an action, ping AgentIAM:

```bash
curl -X POST http://localhost:8000/api/v1/authz/check \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_123",
    "action": "database:write",
    "resource": "production_db"
  }'
```

### 3. Receive Decision & Audit
The engine responds immediately and logs the interaction:

```json
{
  "allowed": false,
  "reason": "Explicit DENY for action 'database:write'",
  "audit_id": "aud_987654321"
}
```

---

## ⚖️ Why AgentIAM?

| Feature | AgentIAM | Traditional Agent Frameworks |
|---------|:--------:|:--------------------------:|
| **Authorization** | Centralized & decoupled | Hardcoded in prompts |
| **Audit Logs** | Immutable, structured ledger | Messy print statements |
| **Policy Enforcement** | Pre-execution strict gating | Post-execution realization |
| **AI Governance** | Built-in compliance trails | Often non-existent |
| **Access Control** | IAM-style YAML policies | Ad-hoc tool removal |

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend API** | FastAPI (Python 3.10+) | High-performance, async API routes |
| **Frontend** | React / Vite / Node.js 18+ | Responsive management dashboard |
| **Database** | PostgreSQL | Persistent storage for agents & logs |
| **DevOps** | Docker / GitHub Actions | Containerization & CI/CD pipeline |
| **Security** | Bandit, Safety, MyPy | Static analysis & vulnerability scanning |

---

## 📸 Screenshots

> *Placeholder: Dashboard Overview*
> 
> ![Dashboard Overview](https://via.placeholder.com/800x450.png?text=AgentIAM+Dashboard)

> *Placeholder: Policy Editor*
> 
> ![Policy Editor](https://via.placeholder.com/800x450.png?text=YAML+Policy+Editor)

---

## 🗺️ Roadmap

**v0.1 (Current MVP)**
* Core backend architecture and YAML policy engine
* Agent creation and audit logging

**v0.2**
* Dark mode dashboard and policy editor with syntax highlighting
* CIDR-based IP restrictions and rate limiting

**v0.3**
* LangChain/LlamaIndex integration guides
* Webhooks for Slack/Discord notifications on DENIED actions

**v1.0**
* Open Policy Agent (OPA) integration research
* Comprehensive security audits and official DockerHub images

*See the full [ROADMAP.md](ROADMAP.md) for more details.*

---

## ❓ Frequently Asked Questions

### General

**Q: What is AgentIAM?**
A: AgentIAM is an Identity & Access Management system designed specifically for AI agents. It provides centralized authorization, policy enforcement, and audit logging to ensure AI agents only perform actions they are explicitly permitted to do.

**Q: Why do AI agents need IAM?**
A: AI agents increasingly interact with production systems (databases, APIs, file systems). Without proper access control, a misbehaving agent—or one affected by prompt injection—can cause serious damage. AgentIAM adds a pre-execution authorization layer, similar to how AWS IAM controls human access.

**Q: How does AgentIAM differ from simply removing tools from an agent?**
A: Removing tools is a blunt approach that limits agent capability. AgentIAM provides fine-grained, policy-based control: you can allow an agent to read a database but not write to it, or permit API calls only to specific endpoints. It also provides audit trails for compliance.

### Installation & Setup

**Q: What are the prerequisites?**
A: You need Python 3.10+, PostgreSQL, and optionally Docker. The frontend requires Node.js 18+.

**Q: Can I run AgentIAM without Docker?**
A: Yes. You can run the FastAPI backend directly with `uvicorn` and the frontend with `npm run dev`. See [DEVELOPMENT.md](DEVELOPMENT.md) for local setup instructions.

**Q: How do I configure the database connection?**
A: Set the `SQLALCHEMY_DATABASE_URI` environment variable (e.g., `postgresql://user:***@localhost:5432/agentiam`). The application uses this to connect to PostgreSQL. You can also configure individual `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` variables.

### Policies & Authorization

**Q: How do I define permissions for an agent?**
A: Create a YAML policy file that specifies allowed actions, resources, and conditions. Assign the policy to an agent via the dashboard or API.

**Q: Can an agent have multiple policies?**
A: Not yet. Policy assignment to agents is currently one-to-one. Multi-policy assignment per agent is planned for a future release. The authorization engine evaluates the assigned policy to determine access.

**Q: What happens when an agent tries to perform a denied action?**
A: The authorization engine returns a DENIED response, and the action is blocked. The event is logged in the immutable audit ledger with full context (agent ID, requested resource, action, decision, reason, and timestamp).

### Security

**Q: Is AgentIAM production-ready?**
A: AgentIAM is currently an MVP (v0.1). It is suitable for development and testing. For production use, review the security considerations in [DEVELOPMENT.md](DEVELOPMENT.md) and follow the hardening recommendations.

**Q: How are audit logs protected?**
A: Audit logs are write-once through the API (created during authorization checks via `POST /check-permission`). The API only exposes read endpoints (`GET /` and `GET /{id}`) with no update or delete routes. The audit logger captures every authorization check, regardless of outcome.

**Q: Does AgentIAM support multi-tenancy?**
A: Not yet. Multi-tenancy support is planned for a future release (see Roadmap). Currently, all agents and policies exist in a single namespace.

### Integration

**Q: Can I use AgentIAM with LangChain or LlamaIndex?**
A: Integration guides for LangChain and LlamaIndex are planned for v0.3. You can wrap AgentIAM's authorization check around any tool call today using the REST API.

**Q: Does AgentIAM support webhook notifications?**
A: Not yet. Webhook support for Slack/Discord notifications on denied actions is planned for v0.3.

**Q: What programming languages does the SDK support?**
A: The API is REST-based and can be called from any language. See the API documentation for request/response formats. Community-contributed SDKs for various languages are welcome.

---

## 🤝 Contributing

We welcome contributions of all sizes! Here is our standard workflow:

1. **Find an Issue**: Look for issues tagged `difficulty:beginner`, `difficulty:easy`, `difficulty:medium`, `difficulty:hard`, or `difficulty:expert`.
2. **Claim the Issue**: Comment on the issue to claim it and mention a maintainer.
3. **Inform Discord**: Drop a message in our Discord community.
4. **Wait for Assignment**: Ensure a maintainer assigns the issue to you.
5. **Submit a PR**: Fork the repo, create your branch, and submit a Pull Request.

Please review our [CONTRIBUTING.md](CONTRIBUTING.md) and [DEVELOPMENT.md](DEVELOPMENT.md) before getting started.

---

## 💬 Community

* **Discord**: [Join the Server](#) (Get help, discuss architecture, and chat with contributors)
* **GitHub Discussions**: [Ask Questions](#)
* **Issues**: [Report a Bug or Request a Feature](#)

---

## 📜 License

AgentIAM is released under the [Apache 2.0 License](LICENSE).

## FAQ

### What is AgentIAM?
AgentIAM is an Identity and Access Management agent for AI workflows.

### How do I get started?
```bash
git clone https://github.com/SHAURYASANYAL3/AgentIAM
npm install
npm run dev
```

### What providers are supported?
Currently supporting AWS IAM, with GCP and Azure on the roadmap.

### How do I contribute?
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
