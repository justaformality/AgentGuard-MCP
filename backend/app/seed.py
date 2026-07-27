from sqlalchemy.orm import Session

from app.models import Agent, Permission, Tool


def seed_database(db: Session):
    existing_agent = db.query(Agent).first()
    existing_tool = db.query(Tool).first()

    if existing_agent or existing_tool:
        print("Seed data already exists. Skipping seed.")
        return

    qa_agent = Agent(
        name="QA Agent",
        role="Generates test plans, analyzes failures, and drafts bug reports.",
        status="active",
        allowed_tools=[
            "search_docs",
            "read_github_issue",
            "generate_test_plan",
            "analyze_logs",
            "create_github_issue",
            "create_mock_ticket",
            "generate_ai_test_plan",
            "summarize_issue",
            "classify_tool_risk",
            "scan_tool_description", 
        ],
        blocked_tools=[
            "run_terminal_command",
            "trigger_deployment",
        ],
        approval_rules={
            "high_risk_tools_require_approval": True,
            "write_actions_require_approval": True,
        },
    )

    code_review_agent = Agent(
        name="Code Review Agent",
        role="Summarizes pull requests, detects missing tests, and reviews code risk.",
        status="active",
        allowed_tools=[
            "summarize_pull_request",
            "read_github_issue",
            "generate_test_plan",
            "post_pr_comment",
        ],
        blocked_tools=[
            "run_terminal_command",
            "trigger_deployment",
        ],
        approval_rules={
            "high_risk_tools_require_approval": True,
            "write_actions_require_approval": True,
        },
    )

    release_agent = Agent(
        name="Release Agent",
        role="Creates release checklists and summarizes release readiness.",
        status="active",
        allowed_tools=[
            "search_docs",
            "summarize_pull_request",
            "analyze_logs",
            "generate_test_plan",
        ],
        blocked_tools=[
            "create_github_issue",
            "post_pr_comment",
            "run_terminal_command",
            "trigger_deployment",
        ],
        approval_rules={
            "high_risk_tools_require_approval": True,
            "write_actions_require_approval": True,
        },
    )

    tools = [
        Tool(
            name="search_docs",
            description="Search internal documentation and return relevant text snippets.",
            category="Documentation",
            risk_level="Low",
            action_type="Read",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="read_github_issue",
            description="Read a GitHub issue title, body, labels, and comments.",
            category="GitHub",
            risk_level="Low",
            action_type="Read",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="summarize_pull_request",
            description="Summarize pull request changes, affected files, and possible testing impact.",
            category="GitHub",
            risk_level="Medium",
            action_type="Generate",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="generate_test_plan",
            description="Generate manual test cases, edge cases, and regression checklist items.",
            category="QA",
            risk_level="Medium",
            action_type="Generate",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="analyze_logs",
            description="Analyze CI logs or application logs and summarize likely failure causes.",
            category="Debugging",
            risk_level="Medium",
            action_type="Generate",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="generate_ai_test_plan",
            description="Use Gemini API to generate a workplace-quality QA test plan from requirements.",
            category="AI QA",
            risk_level="Medium",
            action_type="Generate",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="summarize_issue",
            description="Use Gemini API to summarize a software issue for engineering and QA teams.",
            category="AI Engineering",
            risk_level="Medium",
            action_type="Generate",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="classify_tool_risk",
            description="Use Gemini API to classify the risk level and action type of an MCP tool.",
            category="AI Security",
            risk_level="Medium",
            action_type="Generate",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="scan_tool_description",
            description="Use Gemini API to scan an MCP tool description for prompt injection, unsafe actions, and governance risks.",
            category="AI Security",
            risk_level="Medium",
            action_type="Generate",
            requires_approval=False,
            enabled=True,
        ),
        Tool(
            name="create_mock_ticket",
            description="Create a mock internal bug or QA follow-up ticket.",
            category="Ticketing",
            risk_level="High",
            action_type="Write",
            requires_approval=True,
            enabled=True,
        ),
        Tool(
            name="create_github_issue",
            description="Create a new GitHub issue in a repository.",
            category="GitHub",
            risk_level="High",
            action_type="Write",
            requires_approval=True,
            enabled=True,
        ),
        Tool(
            name="post_pr_comment",
            description="Post a comment on a GitHub pull request.",
            category="GitHub",
            risk_level="High",
            action_type="Write",
            requires_approval=True,
            enabled=True,
        ),
        Tool(
            name="run_terminal_command",
            description="Run a terminal command in the project environment.",
            category="Execution",
            risk_level="High",
            action_type="Execute",
            requires_approval=True,
            enabled=False,
        ),
    ]

    db.add_all([qa_agent, code_review_agent, release_agent])
    db.add_all(tools)
    db.commit()

    all_agents = db.query(Agent).all()
    all_tools = db.query(Tool).all()

    tool_by_name = {tool.name: tool for tool in all_tools}

    permissions = []

    for agent in all_agents:
        for tool_name in agent.allowed_tools:
            tool = tool_by_name.get(tool_name)
            if tool:
                permissions.append(
                    Permission(
                        agent_id=agent.id,
                        tool_id=tool.id,
                        access_level="allowed",
                        requires_approval_override=None,
                    )
                )

        for tool_name in agent.blocked_tools:
            tool = tool_by_name.get(tool_name)
            if tool:
                permissions.append(
                    Permission(
                        agent_id=agent.id,
                        tool_id=tool.id,
                        access_level="blocked",
                        requires_approval_override=None,
                    )
                )

    db.add_all(permissions)
    db.commit()

    print("Database seeded successfully.")