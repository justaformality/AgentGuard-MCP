from app.models import Agent, Tool
from app.services.policy_engine import policy_engine


def make_agent(
    name="QA Agent",
    status="active",
    allowed_tools=None,
    blocked_tools=None,
    approval_rules=None,
):
    return Agent(
        id=1,
        name=name,
        role="Test agent",
        status=status,
        allowed_tools=allowed_tools or [],
        blocked_tools=blocked_tools or [],
        approval_rules=approval_rules
        or {
            "high_risk_tools_require_approval": True,
            "write_actions_require_approval": True,
        },
    )


def make_tool(
    name="generate_test_plan",
    enabled=True,
    risk_level="Low",
    action_type="Read",
    requires_approval=False,
):
    return Tool(
        id=1,
        name=name,
        description="Test tool",
        category="Testing",
        risk_level=risk_level,
        action_type=action_type,
        requires_approval=requires_approval,
        enabled=enabled,
    )


def test_allowed_low_risk_tool():
    agent = make_agent(allowed_tools=["generate_test_plan"])
    tool = make_tool(
        name="generate_test_plan",
        risk_level="Low",
        action_type="Generate",
        requires_approval=False,
    )

    decision = policy_engine.evaluate(agent, tool)

    assert decision.status == "allowed"
    assert decision.allowed is True
    assert decision.requires_approval is False
    assert decision.approval_status == "not_required"


def test_blocked_tool():
    agent = make_agent(
        allowed_tools=["generate_test_plan"],
        blocked_tools=["run_terminal_command"],
    )

    tool = make_tool(
        name="run_terminal_command",
        risk_level="High",
        action_type="Execute",
        requires_approval=True,
    )

    decision = policy_engine.evaluate(agent, tool)

    assert decision.status == "blocked"
    assert decision.allowed is False
    assert decision.requires_approval is False
    assert "blocked" in decision.reason.lower()


def test_high_risk_tool_requires_approval():
    agent = make_agent(allowed_tools=["create_github_issue"])

    tool = make_tool(
        name="create_github_issue",
        risk_level="High",
        action_type="Write",
        requires_approval=True,
    )

    decision = policy_engine.evaluate(agent, tool)

    assert decision.status == "pending_approval"
    assert decision.allowed is False
    assert decision.requires_approval is True
    assert decision.approval_status == "pending"


def test_disabled_tool_is_blocked():
    agent = make_agent(allowed_tools=["generate_test_plan"])

    tool = make_tool(
        name="generate_test_plan",
        enabled=False,
        risk_level="Low",
        action_type="Generate",
        requires_approval=False,
    )

    decision = policy_engine.evaluate(agent, tool)

    assert decision.status == "blocked"
    assert decision.allowed is False
    assert "disabled" in decision.reason.lower()


def test_inactive_agent_is_blocked():
    agent = make_agent(
        status="inactive",
        allowed_tools=["generate_test_plan"],
    )

    tool = make_tool(
        name="generate_test_plan",
        risk_level="Low",
        action_type="Generate",
        requires_approval=False,
    )

    decision = policy_engine.evaluate(agent, tool)

    assert decision.status == "blocked"
    assert decision.allowed is False
    assert "not active" in decision.reason.lower()


def test_tool_not_in_allowed_tools_is_blocked():
    agent = make_agent(allowed_tools=["search_docs"])

    tool = make_tool(
        name="generate_test_plan",
        risk_level="Low",
        action_type="Generate",
        requires_approval=False,
    )

    decision = policy_engine.evaluate(agent, tool)

    assert decision.status == "blocked"
    assert decision.allowed is False
    assert "not allowed" in decision.reason.lower()


def test_unknown_agent_is_blocked():
    tool = make_tool(
        name="generate_test_plan",
        risk_level="Low",
        action_type="Generate",
        requires_approval=False,
    )

    decision = policy_engine.evaluate(None, tool)

    assert decision.status == "blocked"
    assert decision.allowed is False
    assert decision.metadata["error_code"] == "unknown_agent"


def test_unknown_tool_is_blocked():
    agent = make_agent(allowed_tools=["generate_test_plan"])

    decision = policy_engine.evaluate(agent, None)

    assert decision.status == "blocked"
    assert decision.allowed is False
    assert decision.metadata["error_code"] == "unknown_tool"


def test_write_action_requires_approval_even_if_medium_risk():
    agent = make_agent(allowed_tools=["post_pr_comment"])

    tool = make_tool(
        name="post_pr_comment",
        risk_level="Medium",
        action_type="Write",
        requires_approval=False,
    )

    decision = policy_engine.evaluate(agent, tool)

    assert decision.status == "pending_approval"
    assert decision.allowed is False
    assert decision.requires_approval is True
    assert "write" in decision.reason.lower()