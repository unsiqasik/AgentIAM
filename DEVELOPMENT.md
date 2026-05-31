# Development Guide

Welcome to the AgentIAM development guide! This document explains how to set up your local environment and contribute according to our quality standards.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Git

## Backend Setup (FastAPI)

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install ruff black mypy pytest pytest-cov bandit safety httpx
   ```

4. **Linting & Formatting**:
   Before committing, ensure your code is linted and formatted:
   ```bash
   black .
   ruff check . --fix
   ```

5. **Type Checking**:
   We use MyPy for static type analysis:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   mypy app
   ```

6. **Running Tests**:
   Ensure all tests pass:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   pytest --cov=app
   ```

7. **Security Scanning**:
   Run local security checks:
   ```bash
   bandit -r app
   safety check -r requirements.txt
   ```

8. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup (React/Vite)

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

## Pull Request Process

1. Fork the repository and create your branch from `main`.
2. Ensure all CI checks pass locally (Lint, Type Check, Tests, Security).
3. Submit a PR using the [template](.github/pull_request_template.md).
4. A maintainer will review your PR. At least one approval is required for merge.

## Security Hardening for Production

When deploying AgentIAM in production, follow these recommendations:

1. **Change default secrets**: Replace `DEVELOPMENT_SECRET_KEY_CHANGE_ME` with a strong, randomly generated secret key.
2. **Restrict CORS origins**: Set `BACKEND_CORS_ORIS` to your specific domain(s) instead of `["*"]`.
3. **Use environment variables**: Store all sensitive configuration in environment variables or a `.env` file (never commit secrets).
4. **Enable HTTPS**: Deploy behind a reverse proxy (nginx/Cloudflare) with TLS termination.
5. **Database security**: Use a dedicated PostgreSQL user with minimal privileges; enable SSL connections.
6. **Rate limiting**: Implement rate limiting on the authorization check endpoint to prevent abuse.
7. **Audit log monitoring**: Regularly review audit logs for unusual access patterns.
8. **Dependency scanning**: Run `safety check` and `bandit` as part of your CI/CD pipeline.
