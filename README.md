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
version: "1.0"
policies:
  - effect: "ALLOW"
    action: "database:read"
    resource: "production_db"
  - effect: "DENY"
    action: "database:write"
    resource: "*"
```

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
