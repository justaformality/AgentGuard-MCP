# AgentGuard MCP

AgentGuard MCP is an MCP-powered AI agent permission, approval, and audit platform.

It helps teams safely connect AI agents to workplace tools by registering agents and tools, enforcing permissions, requiring human approval for risky actions, and logging every tool call.

## Tech Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite for local MVP
- PostgreSQL planned for Docker setup

### Integrations
- Gemini API
- GitHub API
- MCP-style tool server

## Current Status

Phase 1: Project setup

- FastAPI backend created
- React TypeScript frontend created
- Tailwind CSS configured
- Frontend connects to backend health endpoint

## Local Development

### Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload