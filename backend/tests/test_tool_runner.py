import pytest

from app.tool_server.tool_runner import (
    ToolExecutionError,
    execute_tool,
    list_available_tools,
)


def test_list_available_tools_contains_expected_tools():
    tools = list_available_tools()

    assert "search_docs" in tools
    assert "generate_test_plan" in tools
    assert "analyze_logs" in tools
    assert "create_mock_ticket" in tools


def test_execute_generate_test_plan():
    result = execute_tool(
        "generate_test_plan",
        "Generate a test plan for password reset.",
    )

    assert result["tool_name"] == "generate_test_plan"
    assert result["status"] == "success"
    assert "test_cases" in result["data"]
    assert len(result["data"]["test_cases"]) > 0


def test_execute_analyze_logs_detects_patterns():
    result = execute_tool(
        "analyze_logs",
        "AssertionError expected 200 but got 500. Connection refused.",
    )

    assert result["tool_name"] == "analyze_logs"
    assert result["status"] == "success"
    assert len(result["data"]["possible_causes"]) > 0
    assert len(result["data"]["recommended_actions"]) > 0


def test_unknown_tool_raises_error():
    with pytest.raises(ToolExecutionError):
        execute_tool("unknown_tool", "hello")