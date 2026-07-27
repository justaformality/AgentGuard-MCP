from datetime import datetime, timezone
from typing import Any


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def search_docs(input_text: str) -> dict[str, Any]:
    """
    MCP-style tool that searches mock company documentation.

    Later, this can become a real RAG/documentation search tool.
    """

    mock_docs = [
        {
            "title": "Password Reset QA Guide",
            "snippet": "Password reset should validate email format, expired tokens, reused tokens, and rate limits.",
        },
        {
            "title": "Release Checklist",
            "snippet": "Before release, confirm CI passing, regression tests completed, and high-risk areas reviewed.",
        },
        {
            "title": "Bug Reporting Standard",
            "snippet": "Every bug report should include steps to reproduce, expected result, actual result, severity, and environment.",
        },
    ]

    matching_docs = [
        doc for doc in mock_docs
        if any(word.lower() in doc["snippet"].lower() for word in input_text.split())
    ]

    if not matching_docs:
        matching_docs = mock_docs[:1]

    return {
        "tool_name": "search_docs",
        "status": "success",
        "summary": f"Found {len(matching_docs)} relevant documentation result(s).",
        "data": {
            "query": input_text,
            "results": matching_docs,
        },
        "created_at": _timestamp(),
    }


def read_mock_issue(input_text: str) -> dict[str, Any]:
    """
    MCP-style tool that returns a mock GitHub/Jira-style issue.

    Later, this will be replaced by the real GitHub issue reader.
    """

    return {
        "tool_name": "read_mock_issue",
        "status": "success",
        "summary": "Mock issue retrieved successfully.",
        "data": {
            "issue_id": "MOCK-101",
            "title": "Password reset fails when token is expired",
            "description": (
                "Users see a generic error message when attempting to reset "
                "their password using an expired token."
            ),
            "severity": "Medium",
            "component": "Authentication",
            "labels": ["bug", "auth", "password-reset"],
            "source_input": input_text,
        },
        "created_at": _timestamp(),
    }


def generate_test_plan(input_text: str) -> dict[str, Any]:
    """
    MCP-style tool that generates a structured QA test plan.

    Later, Gemini will generate a richer version.
    """

    feature = input_text.strip()

    test_cases = [
        {
            "id": "TC-001",
            "title": "Valid user can complete the main flow",
            "type": "Positive",
            "steps": [
                "Open the feature page.",
                "Enter valid input data.",
                "Submit the form or complete the action.",
                "Verify the success message or expected result.",
            ],
            "expected_result": "The user completes the flow successfully.",
        },
        {
            "id": "TC-002",
            "title": "Invalid input shows clear validation error",
            "type": "Negative",
            "steps": [
                "Open the feature page.",
                "Enter invalid or incomplete input.",
                "Submit the form.",
                "Observe validation behavior.",
            ],
            "expected_result": "The system shows a clear error message and prevents invalid submission.",
        },
        {
            "id": "TC-003",
            "title": "Empty required fields are handled correctly",
            "type": "Edge Case",
            "steps": [
                "Open the feature page.",
                "Leave required fields blank.",
                "Submit the form.",
            ],
            "expected_result": "The system highlights required fields and explains what is missing.",
        },
        {
            "id": "TC-004",
            "title": "User can recover from an error state",
            "type": "Recovery",
            "steps": [
                "Trigger an error using invalid data.",
                "Correct the input.",
                "Submit again.",
            ],
            "expected_result": "The system allows the user to recover and complete the flow.",
        },
    ]

    regression_checklist = [
        "Verify happy path still works.",
        "Verify invalid input handling.",
        "Verify error messages are user-friendly.",
        "Verify page refresh does not break the flow.",
        "Verify mobile/responsive behavior.",
        "Verify no sensitive data is exposed in errors.",
    ]

    return {
        "tool_name": "generate_test_plan",
        "status": "success",
        "summary": f"Generated a QA test plan for: {feature}",
        "data": {
            "feature": feature,
            "test_cases": test_cases,
            "regression_checklist": regression_checklist,
            "risk_notes": [
                "Authentication, payment, database, and permission-related flows should be treated as higher risk.",
                "Add automation coverage for the highest-value happy path and at least two negative paths.",
            ],
        },
        "created_at": _timestamp(),
    }


def create_mock_ticket(input_text: str) -> dict[str, Any]:
    """
    MCP-style tool that creates a mock ticket.

    This simulates a future GitHub/Jira issue creation tool.
    """

    ticket_id = f"MOCK-TICKET-{int(datetime.now().timestamp())}"

    return {
        "tool_name": "create_mock_ticket",
        "status": "success",
        "summary": f"Created mock ticket {ticket_id}.",
        "data": {
            "ticket_id": ticket_id,
            "title": "AI-generated follow-up task",
            "description": input_text,
            "status": "Open",
            "priority": "Medium",
            "source": "AgentGuard MCP",
        },
        "created_at": _timestamp(),
    }


def analyze_logs(input_text: str) -> dict[str, Any]:
    """
    MCP-style tool that analyzes CI or application logs.

    Later, Gemini can improve the diagnosis.
    """

    lower_text = input_text.lower()

    possible_causes = []
    recommended_actions = []

    if "timeout" in lower_text:
        possible_causes.append("The failure may be related to a timeout or slow service response.")
        recommended_actions.append("Check network calls, wait conditions, and service response times.")

    if "assert" in lower_text or "expected" in lower_text:
        possible_causes.append("The failure may be caused by an assertion mismatch.")
        recommended_actions.append("Compare expected vs actual values and verify whether the UI/API behavior changed.")

    if "connection refused" in lower_text or "failed to connect" in lower_text:
        possible_causes.append("The failure may be caused by a service or database connection issue.")
        recommended_actions.append("Confirm the backend, database, or dependent service is running.")

    if "not found" in lower_text or "404" in lower_text:
        possible_causes.append("The failure may be caused by a missing route, missing resource, or incorrect URL.")
        recommended_actions.append("Verify endpoint paths, test data, and route configuration.")

    if not possible_causes:
        possible_causes.append("No obvious failure pattern detected from the provided logs.")
        recommended_actions.append("Review the full stack trace and reproduce the issue locally.")

    return {
        "tool_name": "analyze_logs",
        "status": "success",
        "summary": "Log analysis completed.",
        "data": {
            "possible_causes": possible_causes,
            "recommended_actions": recommended_actions,
            "raw_log_excerpt": input_text[:500],
        },
        "created_at": _timestamp(),
    }