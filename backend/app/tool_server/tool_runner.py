from typing import Any, Callable

from app.tool_server.ai_tools import (
    classify_tool_risk,
    generate_ai_test_plan,
    scan_tool_description,
    summarize_issue,
)
from app.tool_server.github_tools import (
    create_github_issue,
    read_github_issue,
    summarize_pull_request,
)
from app.tool_server.mcp_tools import (
    analyze_logs,
    create_mock_ticket,
    generate_test_plan,
    read_mock_issue,
    search_docs,
)

ToolFunction = Callable[[str], dict[str, Any]]


TOOL_REGISTRY: dict[str, ToolFunction] = {
    "search_docs": search_docs,
    "read_mock_issue": read_mock_issue,
    "generate_test_plan": generate_test_plan,
    "create_mock_ticket": create_mock_ticket,
    "analyze_logs": analyze_logs,
    "generate_ai_test_plan": generate_ai_test_plan,
    "summarize_issue": summarize_issue,
    "classify_tool_risk": classify_tool_risk,
    "scan_tool_description": scan_tool_description,
    "read_github_issue": read_github_issue,
    "summarize_pull_request": summarize_pull_request,
    "create_github_issue": create_github_issue,
}


class ToolExecutionError(Exception):
    pass


def list_available_tools() -> list[str]:
    return sorted(TOOL_REGISTRY.keys())


def execute_tool(tool_name: str, input_text: str) -> dict[str, Any]:
    tool_function = TOOL_REGISTRY.get(tool_name)

    if tool_function is None:
        raise ToolExecutionError(
            f"No executable tool found for '{tool_name}'. "
            f"Available tools: {', '.join(list_available_tools())}"
        )

    try:
        return tool_function(input_text)
    except Exception as exc:
        raise ToolExecutionError(
            f"Tool '{tool_name}' failed during execution: {str(exc)}"
        ) from exc