from dataclasses import dataclass
from typing import Any

from app.models import Agent, Tool


@dataclass
class PolicyDecision:
    status: str
    allowed: bool
    requires_approval: bool
    reason: str
    approval_status: str
    risk_level: str | None = None
    metadata: dict[str, Any] | None = None


class PolicyEngine:
    """
    PolicyEngine decides whether an AI agent is allowed to use a tool.

    It does not execute tools.
    It only answers:
    - allowed
    - blocked
    - pending_approval
    """

    HIGH_RISK_LEVEL = "high"
    WRITE_ACTION_TYPES = {"write", "execute"}

    def evaluate(self, agent: Agent | None, tool: Tool | None) -> PolicyDecision:
        if agent is None:
            return PolicyDecision(
                status="blocked",
                allowed=False,
                requires_approval=False,
                reason="Agent not found.",
                approval_status="not_required",
                risk_level=None,
                metadata={"error_code": "unknown_agent"},
            )

        if tool is None:
            return PolicyDecision(
                status="blocked",
                allowed=False,
                requires_approval=False,
                reason="Tool not found.",
                approval_status="not_required",
                risk_level=None,
                metadata={"error_code": "unknown_tool"},
            )

        risk_level = tool.risk_level or "Unknown"
        normalized_risk = risk_level.lower()
        normalized_action_type = (tool.action_type or "").lower()

        if agent.status.lower() != "active":
            return PolicyDecision(
                status="blocked",
                allowed=False,
                requires_approval=False,
                reason="Agent is not active.",
                approval_status="not_required",
                risk_level=risk_level,
                metadata={"error_code": "inactive_agent"},
            )

        if not tool.enabled:
            return PolicyDecision(
                status="blocked",
                allowed=False,
                requires_approval=False,
                reason="Tool is disabled.",
                approval_status="not_required",
                risk_level=risk_level,
                metadata={"error_code": "disabled_tool"},
            )

        if tool.name in agent.blocked_tools:
            return PolicyDecision(
                status="blocked",
                allowed=False,
                requires_approval=False,
                reason="This tool is blocked for this agent.",
                approval_status="not_required",
                risk_level=risk_level,
                metadata={
                    "error_code": "tool_blocked_for_agent",
                    "tool_name": tool.name,
                    "agent_name": agent.name,
                },
            )

        if tool.name not in agent.allowed_tools:
            return PolicyDecision(
                status="blocked",
                allowed=False,
                requires_approval=False,
                reason="This agent is not allowed to use this tool.",
                approval_status="not_required",
                risk_level=risk_level,
                metadata={
                    "error_code": "tool_not_allowed_for_agent",
                    "tool_name": tool.name,
                    "agent_name": agent.name,
                },
            )

        approval_rules = agent.approval_rules or {}

        high_risk_requires_approval = approval_rules.get(
            "high_risk_tools_require_approval",
            True,
        )

        write_actions_require_approval = approval_rules.get(
            "write_actions_require_approval",
            True,
        )

        is_high_risk = normalized_risk == self.HIGH_RISK_LEVEL
        is_write_or_execute = normalized_action_type in self.WRITE_ACTION_TYPES

        approval_reasons = []

        if tool.requires_approval:
            approval_reasons.append("Tool is configured to require approval.")

        if is_high_risk and high_risk_requires_approval:
            approval_reasons.append("High-risk tools require human approval.")

        if is_write_or_execute and write_actions_require_approval:
            approval_reasons.append("Write or execute actions require human approval.")

        if approval_reasons:
            return PolicyDecision(
                status="pending_approval",
                allowed=False,
                requires_approval=True,
                reason=" ".join(approval_reasons),
                approval_status="pending",
                risk_level=risk_level,
                metadata={
                    "tool_name": tool.name,
                    "agent_name": agent.name,
                    "action_type": tool.action_type,
                    "approval_reasons": approval_reasons,
                },
            )

        return PolicyDecision(
            status="allowed",
            allowed=True,
            requires_approval=False,
            reason="Tool call is allowed by policy.",
            approval_status="not_required",
            risk_level=risk_level,
            metadata={
                "tool_name": tool.name,
                "agent_name": agent.name,
                "action_type": tool.action_type,
            },
        )


policy_engine = PolicyEngine()