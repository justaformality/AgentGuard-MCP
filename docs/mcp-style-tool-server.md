# MCP-Style Tool Server

AgentGuard MCP starts with a simplified MCP-style tool server before upgrading to the real MCP SDK.

## Why start simplified?

Before exposing real MCP tools, the project first proves the core product workflow:

1. Register tools
2. Assign tools to agents
3. Evaluate tool permissions
4. Approval-gate risky actions
5. Execute safe tools
6. Log every tool call

## Current Tools

### search_docs

Searches mock internal documentation.

### read_mock_issue

Returns a mock GitHub/Jira-style issue.

### generate_test_plan

Generates manual test cases, edge cases, and a regression checklist.

### create_mock_ticket

Creates a mock ticket object. This is treated as high risk because it simulates a write action.

### analyze_logs

Analyzes application or CI logs for common failure patterns.

## Tool Runner

The tool runner maps tool names to Python functions.

Example:

```python
execute_tool("generate_test_plan", "Password reset feature")