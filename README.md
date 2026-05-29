# AgentIAM

**Identity and Access Management for AI Agents**

AgentIAM provides a centralized service to evaluate, enforce, and audit permissions when AI agents interact with external tools, APIs, and resources.

## 🚀 Features

- **Centralized Policy Management**: Define what your AI agents can and cannot do using intuitive YAML-based policies.
- **Strict Authorization Engine**: Evaluate permissions dynamically before agents execute critical actions.
- **Comprehensive Audit Trail**: Maintain an immutable ledger of every authorization decision for security and compliance.
- **Modern Tech Stack**: Built with FastAPI (Python) for a high-performance backend and React/Vite for a responsive dashboard.

## 🏗️ Architecture

The system consists of three main components:
1. **Frontend (Dashboard)**: React-based web application for managing agents, policies, and viewing audit logs.
2. **Backend (API & Authz Engine)**: FastAPI Python service handling policy evaluation, user authentication, and data persistence.
3. **Database**: PostgreSQL for storing agents, policies, and audit logs.

For detailed architecture information, please see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🛠️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## 🤝 Contributing

We welcome contributions! Please see our [DEVELOPMENT.md](DEVELOPMENT.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to set up your environment, run tests, and submit Pull Requests. 

For first-time contributors, check out [FIRST_CONTRIBUTION.md](FIRST_CONTRIBUTION.md).

## 🔒 Security

For our security policy and how to report vulnerabilities, please read [SECURITY.md](SECURITY.md).

## 🗺️ Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and technical improvements.

## 📜 License

This project is licensed under the terms described in the [LICENSE](LICENSE) file.
