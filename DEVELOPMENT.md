# Development Guide

Welcome to the AgentIAM development guide! This document explains how to set up your local environment and begin contributing.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional, but recommended for database)
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
   ```

4. **Database Setup**:
   You can use the provided Docker Compose file to spin up PostgreSQL, or use a local SQLite database for development.
   By default, tests use SQLite. To run the app with PostgreSQL:
   ```bash
   docker-compose up -d db
   ```

5. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

6. **Run Tests**:
   Ensure you run the tests before submitting a PR.
   ```bash
   PYTHONPATH=. pytest
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
   The app will be available at `http://localhost:5173`.

## Docker Compose (Full Stack)

To run the entire stack (Frontend, Backend, DB) via Docker:

```bash
docker-compose up --build
```

## Pull Request Process

1. Check the GitHub issues for a task to work on. Look for `good-first-issue` if you are new!
2. Fork the repository and create your branch from `main`.
3. Ensure your code passes all tests and linting.
4. Update documentation if necessary.
5. Submit a pull request referencing the issue number.
