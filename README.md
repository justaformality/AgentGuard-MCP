# AgentGuard MCP - AI Agent Permission & Audit Platform

AgentGuard MCP is an AI agent governance platform built around the **Model Context Protocol (MCP)**.

It acts as a control layer between AI agents and the tools they want to use, enforcing **per-agent permissions, risk-based policies, human approval gates, and audit logging** before tool calls are executed.

The project demonstrates how MCP-enabled agents can safely interact with workplace tools such as GitHub while maintaining human oversight over higher-impact actions.

---

## Overview

AI agents can become significantly more useful when they are allowed to interact with external tools, but giving an agent unrestricted tool access creates security and governance risks.

AgentGuard MCP addresses this by evaluating every governed tool call before execution.

For each request, AgentGuard determines:

1. Which agent is making the request
2. Whether the requested tool exists and is enabled
3. Whether the agent has permission to use that tool
4. What type of action the tool performs
5. The configured risk level of the tool
6. Whether human approval is required
7. Whether the request should be allowed, blocked, or held for approval

Every decision is then recorded in the audit log.

---

## Features

### MCP Tool Governance

AgentGuard exposes governed tools through an MCP server and routes tool calls through a central policy layer before execution.

The platform supports:

- Agent registration
- Tool registration
- Per-agent tool permissions
- Tool enable/disable controls
- Risk classification
- Human approval requirements
- Governed tool execution
- Tool-call audit logging

---

### Risk-Based Policy Engine

The policy engine evaluates AI tool calls based on:

- Agent permissions
- Tool availability
- Tool risk level
- Action type
- Approval requirements

A request can result in one of three primary outcomes:

```text
ALLOW
BLOCK
PENDING_APPROVAL
```

Low-risk actions can execute immediately.

Higher-impact actions, such as write operations, can be routed to the human approval queue before execution.

---

### Human Approval Gates

High-risk actions can require human approval before the underlying tool is allowed to execute.

For example:

```text
AI Agent
   |
   v
create_github_issue
   |
   v
Policy Engine
   |
   v
High-Risk Write Action
   |
   v
Pending Approval
   |
   +------ Reject
   |
   v
Approve & Execute
   |
   v
GitHub API
```

This allows the system to maintain human oversight over actions that modify external systems.

---

### Audit Logging

AgentGuard records governed tool activity so administrators can review what agents attempted to do.

Audit records include information such as:

- Agent
- Tool
- Timestamp
- Risk level
- Decision status
- Approval status
- Tool result or failure information

This provides a history of AI agent activity and governance decisions.

---

## Governed Tools

The current project includes MCP tools for several different types of agent actions.

### GitHub Issue Reading

Reads an existing GitHub issue using the GitHub REST API.

Example input:

```json
{
  "owner": "facebook",
  "repo": "react",
  "issue_number": 123
}
```

Because this is a read-only operation, it can be configured as a low-risk tool that executes without human approval.

---

### GitHub Pull Request Summarization

Retrieves GitHub pull request metadata and changed files, then produces a structured summary.

Example input:

```json
{
  "owner": "facebook",
  "repo": "react",
  "pull_number": 123
}
```

The tool can return information such as:

```text
Summary
Key Changes
Testing Impact
Risk Level
Risk Reasons
Recommended Checks
```

When a Gemini API key is configured, Gemini can be used to generate the structured analysis.

If Gemini is unavailable, the project supports deterministic fallback behavior so the rest of the governance system can continue operating.

---

### Test Plan Generation

AgentGuard includes AI-assisted tooling for creating structured QA test plans.

Generated test plans can include:

- Test scenarios
- Expected behavior
- Edge cases
- Validation recommendations
- Risk considerations

---

### Approval-Gated GitHub Issue Creation

Agents can request that a GitHub issue be created.

Example input:

```json
{
  "owner": "OWNER",
  "repo": "REPOSITORY",
  "title": "Example issue",
  "body": "Issue created through AgentGuard",
  "labels": []
}
```

Because creating an issue modifies an external system, it is treated as a higher-risk write action.

Instead of immediately calling GitHub:

```text
Agent Request
     |
     v
Policy Engine
     |
     v
Pending Approval
     |
     v
Human Review
   /     \
Reject   Approve
           |
           v
     Execute GitHub Action
           |
           v
        Audit Log
```

---

## MCP Security Checks

AgentGuard also includes security checks designed to identify potentially unsafe MCP tool behavior and suspicious tool descriptions.

The scanner checks for patterns involving:

- Instructions to ignore previous rules
- Prompt-injection-style instructions
- Unauthorized write behavior
- Destructive operations
- Arbitrary command execution
- Requests for credentials, tokens, or secrets
- Excessively broad permissions
- Suspicious privilege escalation
- Tools whose described behavior does not match their expected permissions

These checks help demonstrate how MCP tool definitions themselves can become part of an AI-agent security boundary.

---

## Governance Dashboard

AgentGuard includes a React dashboard for viewing and managing the governance system.

The dashboard contains the following sections.

### Overview

Displays high-level governance information including:

- Registered agents
- Enabled tools
- Pending approvals
- Audit events
- Recent tool activity

---

### Agents

View registered AI agents and manage the tools each agent is permitted to use.

This implements per-agent least-privilege tool access.

---

### Tools

View governed tools and their configuration, including:

- Tool name
- Category
- Risk level
- Action type
- Approval requirement
- Enabled/disabled state

---

### Approval Queue

Review high-risk requests waiting for human authorization.

Administrators can:

```text
Approve & Execute
```

or:

```text
Reject
```

Approved requests are passed to the tool execution layer.

Rejected requests are prevented from executing.

---

### Audit Log

View the history of governed AI activity.

The audit interface shows information such as:

```text
Timestamp
Agent
Tool
Status
Risk
Approval Status
Execution Result
```

---

### Governed Tool Runner

The dashboard also contains a tool runner that can be used to manually demonstrate AgentGuard's governance flow.

A user can select:

```text
Agent
Tool
Input
```

and submit the request through the same governance layer used by MCP tool calls.

This makes it easy to demonstrate both:

```text
Low-Risk Request
        |
        v
Policy Allows
        |
        v
Execute
        |
        v
Audit
```

and:

```text
High-Risk Request
        |
        v
Policy Requires Approval
        |
        v
Approval Queue
```

---

## Architecture

```text
                       AI Agent / MCP Client
                                |
                                v
                     +----------------------+
                     |   AgentGuard MCP     |
                     |       Server         |
                     +----------+-----------+
                                |
                                v
                     +----------------------+
                     |  Governed Executor   |
                     +----------+-----------+
                                |
                                v
                     +----------------------+
                     |    Policy Engine     |
                     +----------+-----------+
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
          Allowed Request               Approval Required
                 |                             |
                 v                             v
          Tool Execution                Approval Queue
                 |                       /          \
                 |                   Reject       Approve
                 |                                  |
                 +----------------------------------+
                                |
                                v
                         External Tool/API
                                |
                                v
                            Audit Log
```

The React dashboard communicates with the FastAPI backend to manage agents, permissions, tools, approvals, governed executions, and audit history.

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- MCP Python SDK / FastMCP
- Pytest
- Requests
- GitHub REST API
- Google Gemini API

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

### Infrastructure

- Docker
- Docker Compose

---

## Project Structure

```text
agentguard-mcp/
├── backend/
│   ├── app/
│   │   ├── mcp_server/
│   │   ├── policy/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── tool_server/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── seed.py
│   │
│   ├── tests/
│   │   ├── test_ai_tools.py
│   │   ├── test_github_pr_tool.py
│   │   ├── test_github_tools.py
│   │   ├── test_policy_engine.py
│   │   └── test_tool_runner.py
│   │
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── package.json
│   └── package-lock.json
│
├── docs/
├── mcp-server/
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

# Getting Started

## Prerequisites

Make sure the following are installed:

- Python 3
- Node.js
- npm
- Git

Optional integrations require:

- GitHub personal access token
- Google Gemini API key

---

## Backend Setup

From the project root:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The local SQLite database is automatically created and seeded when the backend starts.

---

## Frontend Setup

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The dashboard will be available at:

```text
http://localhost:5173
```

---

## MCP Server

To run the MCP server, activate the backend environment:

```bash
cd backend
source .venv/bin/activate
```

Then run:

```bash
python -m app.mcp_server.server
```

The MCP endpoint runs separately from the main FastAPI application.

---

# Environment Variables

Local environment configuration is stored in:

```text
backend/.env
```

Example:

```env
ENVIRONMENT=development

DATABASE_URL=sqlite:///./agentguard.db

GITHUB_TOKEN=

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

## GitHub Token

A GitHub token is required for authenticated GitHub operations, particularly write operations such as creating issues.

Do not commit your real token to GitHub.

---

## Gemini

Gemini is optional.

When configured, it can be used by AI-powered tools such as pull request summarization and test-plan generation.

The application includes fallback behavior when Gemini is not configured or unavailable.

---

# Testing

The backend includes an automated Pytest test suite.

Current test files include:

```text
test_ai_tools.py
test_github_pr_tool.py
test_github_tools.py
test_policy_engine.py
test_tool_runner.py
```

The tests cover areas including:

- Policy engine decisions
- Agent permissions
- Tool authorization
- Governed tool execution
- GitHub issue tools
- GitHub pull request summarization
- AI tool behavior and fallback behavior

Run the tests from the backend directory:

```bash
cd backend

source .venv/bin/activate

pytest -v
```

The current suite contains:

```text
22 passing tests
```

---

# Example Governance Demo

A useful way to demonstrate AgentGuard is to compare a read-only request with a write request.

## Low-Risk Example

Run:

```text
read_github_issue
```

Expected governance flow:

```text
Agent Request
      |
      v
Permission Check
      |
      v
Policy Allows
      |
      v
GitHub Read
      |
      v
Audit Log
```

---

## High-Risk Example

Run:

```text
create_github_issue
```

Expected governance flow:

```text
Agent Request
      |
      v
Permission Check
      |
      v
Policy Engine
      |
      v
Approval Required
      |
      v
Approval Queue
```

At this point no GitHub write action has occurred.

After a human selects:

```text
Approve & Execute
```

the action proceeds:

```text
Approval
   |
   v
GitHub Issue Creation
   |
   v
Audit Log
```

This demonstrates the central purpose of AgentGuard: allowing AI agents to use useful tools without automatically giving them unrestricted authority.

---

# Current Scope

AgentGuard MCP is a **portfolio-quality governance MVP** intended to demonstrate AI-agent security and MCP governance concepts.

The current implementation demonstrates:

- Model Context Protocol tool exposure
- Agent-specific permissions
- Least-privilege access
- Risk-based policy decisions
- Human-in-the-loop approvals
- GitHub tool integration
- AI-assisted analysis
- Security scanning
- Tool-call auditability
- React-based governance management
- Automated backend testing

---

## Future Production Improvements

A production deployment could expand the platform with:

- User authentication
- Role-based access control
- Multi-tenant organization support
- PostgreSQL
- Database migrations
- Encrypted secret storage
- GitHub App or OAuth authentication
- Immutable audit storage
- Rate limiting
- Distributed tracing
- Metrics and observability
- Production deployment configuration
- More comprehensive integration testing
- Frontend component testing

---

## Why AgentGuard?

AI agents become more powerful when they can interact with real systems.

That also means their actions need governance.

AgentGuard explores a simple principle:

> **Agents should only have the permissions they need, risky actions should require oversight, and every tool call should be auditable.**

The project demonstrates how MCP can be combined with traditional security concepts such as least privilege, policy enforcement, human approval, and audit logging to build safer AI-agent workflows.
