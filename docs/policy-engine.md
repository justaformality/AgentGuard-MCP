# Policy Engine

The AgentGuard MCP policy engine decides whether an AI agent can use a tool.

It does not execute tools. It only returns a decision.

## Possible Decisions

### allowed

The tool call is safe and can run immediately.

### blocked

The tool call is not allowed. Reasons include:

- Agent does not exist
- Tool does not exist
- Agent is inactive
- Tool is disabled
- Tool is blocked for this agent
- Tool is not in the agent's allowed tools

### pending_approval

The tool call is allowed in principle but requires human approval before execution.

Reasons include:

- Tool is high risk
- Tool is a write action
- Tool is an execute action
- Tool is configured to require approval

## Why this matters

AI agents connected to workplace tools can create real risk if they are allowed to act without controls.

The policy engine creates a safety layer between the AI agent and external systems.

## Example

A QA Agent can generate a test plan automatically.

However, if the QA Agent wants to create a GitHub issue or comment on a pull request, the action must go through the human approval queue first.