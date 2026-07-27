import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.database import SessionLocal
from app.mcp_server.governed_executor import run_governed_tool
from app.models import Agent, Tool

mcp = FastMCP(
    name="AgentGuard MCP",
    instructions=(
        "AgentGuard MCP exposes governed workplace tools for AI agents. "
        "Every request is evaluated by a permission policy engine. "
        "High-risk write actions require human approval before execution."
    ),
    host="127.0.0.1",
    port=8001,
    stateless_http=True,
    json_response=True,
)


def _json_input(payload: dict[str, Any]) -> str:
    return json.dumps(payload)


@mcp.tool()
def list_registered_agents() -> dict[str, Any]:
    """
    List AI agents registered in AgentGuard MCP.

    Returns agent IDs, names, roles, and statuses.
    Use the returned agent ID when invoking governed tools.
    """

    db = SessionLocal()

    try:
        agents = db.query(Agent).order_by(Agent.id).all()

        return {
            "status": "success",
            "agents": [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "role": agent.role,
                    "status": agent.status,
                    "allowed_tools": agent.allowed_tools,
                    "blocked_tools": agent.blocked_tools,
                }
                for agent in agents
            ],
        }

    finally:
        db.close()


@mcp.tool()
def list_registered_tools() -> dict[str, Any]:
    """
    List tools registered in AgentGuard MCP.

    Returns tool names, descriptions, categories, risk levels,
    action types, approval requirements, and enabled statuses.
    """

    db = SessionLocal()

    try:
        tools = db.query(Tool).order_by(Tool.id).all()

        return {
            "status": "success",
            "tools": [
                {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "risk_level": tool.risk_level,
                    "action_type": tool.action_type,
                    "requires_approval": tool.requires_approval,
                    "enabled": tool.enabled,
                }
                for tool in tools
            ],
        }

    finally:
        db.close()


@mcp.tool()
def search_company_docs(
    agent_id: int,
    query: str,
) -> dict[str, Any]:
    """
    Search internal-style company documentation.

    This is a governed read-only tool.

    Args:
        agent_id: Registered AgentGuard MCP agent ID.
        query: Search terms or workplace question.
    """

    return run_governed_tool(
        agent_id=agent_id,
        tool_name="search_docs",
        input_text=query,
    )


@mcp.tool()
def generate_ai_qa_test_plan(
    agent_id: int,
    requirement: str,
) -> dict[str, Any]:
    """
    Generate an AI-powered QA test plan from a user story or requirement.

    This tool produces manual tests, automation candidates,
    edge cases, and a regression checklist.

    Args:
        agent_id: Registered AgentGuard MCP agent ID.
        requirement: Feature requirement or user story.
    """

    return run_governed_tool(
        agent_id=agent_id,
        tool_name="generate_ai_test_plan",
        input_text=requirement,
    )


@mcp.tool()
def analyze_ci_logs(
    agent_id: int,
    logs: str,
) -> dict[str, Any]:
    """
    Analyze CI logs or application logs for likely failure patterns.

    Args:
        agent_id: Registered AgentGuard MCP agent ID.
        logs: CI log text, test failure output, or stack trace.
    """

    return run_governed_tool(
        agent_id=agent_id,
        tool_name="analyze_logs",
        input_text=logs,
    )


@mcp.tool()
def scan_mcp_tool_description(
    agent_id: int,
    description: str,
) -> dict[str, Any]:
    """
    Scan an MCP tool description for security and governance risks.

    The scan looks for unsafe execution, vague scope,
    prompt-injection-style instructions, secret access,
    and missing constraints.

    Args:
        agent_id: Registered AgentGuard MCP agent ID.
        description: MCP tool description to evaluate.
    """

    return run_governed_tool(
        agent_id=agent_id,
        tool_name="scan_tool_description",
        input_text=description,
    )


@mcp.tool()
def read_github_issue(
    agent_id: int,
    owner: str,
    repo: str,
    issue_number: int,
) -> dict[str, Any]:
    """
    Read a GitHub issue through a governed read-only tool.

    Args:
        agent_id: Registered AgentGuard MCP agent ID.
        owner: GitHub repository owner.
        repo: GitHub repository name.
        issue_number: GitHub issue number.
    """

    return run_governed_tool(
        agent_id=agent_id,
        tool_name="read_github_issue",
        input_text=_json_input(
            {
                "owner": owner,
                "repo": repo,
                "issue_number": issue_number,
            }
        ),
    )


@mcp.tool()
def summarize_github_pull_request(
    agent_id: int,
    owner: str,
    repo: str,
    pull_number: int,
) -> dict[str, Any]:
    """Summarize a GitHub pull request through AgentGuard governance."""
    return run_governed_tool(
        agent_id=agent_id,
        tool_name="summarize_pull_request",
        input_text=_json_input({
            "owner": owner, "repo": repo, "pull_number": pull_number
        }),
    )


@mcp.tool()
def request_create_github_issue(
    agent_id: int,
    owner: str,
    repo: str,
    title: str,
    body: str,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """
    Request creation of a GitHub issue.

    This is a high-risk write action.
    AgentGuard MCP should send it to the human approval queue
    before the GitHub API is called.

    Args:
        agent_id: Registered AgentGuard MCP agent ID.
        owner: GitHub repository owner.
        repo: GitHub repository name.
        title: Proposed GitHub issue title.
        body: Proposed GitHub issue body.
        labels: Optional GitHub labels.
    """

    return run_governed_tool(
        agent_id=agent_id,
        tool_name="create_github_issue",
        input_text=_json_input(
            {
                "owner": owner,
                "repo": repo,
                "title": title,
                "body": body,
                "labels": labels or [],
            }
        ),
    )


@mcp.resource("agentguard://policy-model")
def get_policy_model() -> str:
    """
    Return a human-readable description of the AgentGuard MCP safety model.
    """

    return json.dumps(
        {
            "platform": "AgentGuard MCP",
            "policy_decisions": [
                "allowed",
                "blocked",
                "pending_approval",
            ],
            "automatic_actions": [
                "read-only tools",
                "approved low-risk tools",
                "approved generation tools",
            ],
            "approval_gated_actions": [
                "write actions",
                "execute actions",
                "high-risk tools",
                "GitHub issue creation",
            ],
            "audit_logging": True,
            "human_in_the_loop": True,
        },
        indent=2,
    )


@mcp.prompt()
def review_risky_tool(
    tool_description: str,
) -> str:
    """
    Create a security-review prompt for an MCP tool description.
    """

    return (
        "Review the following MCP tool description for security risks. "
        "Identify prompt injection language, excessive permissions, "
        "unsafe write actions, execution risks, missing constraints, "
        "and whether human approval is required.\n\n"
        f"Tool description:\n{tool_description}"
    )


def main():
    """
    Run AgentGuard MCP over Streamable HTTP.

    MCP clients connect to:
    http://127.0.0.1:8001/mcp
    """

    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()