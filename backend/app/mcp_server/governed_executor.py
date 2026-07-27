from typing import Any

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Agent, ApprovalRequest, AuditLog, Tool
from app.services.policy_engine import policy_engine
from app.tool_server.tool_runner import ToolExecutionError, execute_tool


def _save_audit_log(
    db: Session,
    *,
    agent: Agent | None,
    tool: Tool | None,
    input_summary: str,
    output_summary: str | None,
    status: str,
    risk_level: str | None,
    approval_status: str | None,
    error_message: str | None,
) -> AuditLog:
    audit_log = AuditLog(
        agent_id=agent.id if agent else None,
        tool_id=tool.id if tool else None,
        agent_name=agent.name if agent else None,
        tool_name=tool.name if tool else None,
        input_summary=input_summary,
        output_summary=output_summary,
        status=status,
        risk_level=risk_level,
        approval_status=approval_status,
        error_message=error_message,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def run_governed_tool(
    *,
    agent_id: int,
    tool_name: str,
    input_text: str,
) -> dict[str, Any]:
    """
    Execute a tool through the AgentGuard MCP governance layer.

    This function is shared by:
    - REST API routes
    - Real MCP SDK tools

    Every tool call is:
    - checked by policy
    - approval-gated when necessary
    - written to the audit log
    """

    db = SessionLocal()

    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        tool = db.query(Tool).filter(Tool.name == tool_name).first()

        decision = policy_engine.evaluate(agent, tool)

        if agent is None:
            return {
                "status": "blocked",
                "message": decision.reason,
                "agent_id": agent_id,
                "tool_name": tool_name,
                "audit_log_id": None,
            }

        if tool is None:
            audit_log = _save_audit_log(
                db,
                agent=agent,
                tool=None,
                input_summary=input_text,
                output_summary=None,
                status="blocked",
                risk_level=None,
                approval_status="not_required",
                error_message=decision.reason,
            )

            return {
                "status": "blocked",
                "message": decision.reason,
                "agent_name": agent.name,
                "tool_name": tool_name,
                "audit_log_id": audit_log.id,
            }

        if decision.status == "blocked":
            audit_log = _save_audit_log(
                db,
                agent=agent,
                tool=tool,
                input_summary=input_text,
                output_summary=None,
                status="blocked",
                risk_level=decision.risk_level,
                approval_status=decision.approval_status,
                error_message=decision.reason,
            )

            return {
                "status": "blocked",
                "message": decision.reason,
                "agent_name": agent.name,
                "tool_name": tool.name,
                "audit_log_id": audit_log.id,
            }

        if decision.status == "pending_approval":
            approval_request = ApprovalRequest(
                agent_id=agent.id,
                tool_id=tool.id,
                input_summary=input_text,
                proposed_action={
                    "tool_name": tool.name,
                    "input_text": input_text,
                    "reason": decision.reason,
                    "policy_metadata": decision.metadata or {},
                },
                status="pending",
            )

            db.add(approval_request)
            db.commit()
            db.refresh(approval_request)

            audit_log = _save_audit_log(
                db,
                agent=agent,
                tool=tool,
                input_summary=input_text,
                output_summary="Tool call sent to human approval queue.",
                status="pending_approval",
                risk_level=decision.risk_level,
                approval_status="pending",
                error_message=None,
            )

            return {
                "status": "pending_approval",
                "message": decision.reason,
                "agent_name": agent.name,
                "tool_name": tool.name,
                "approval_request_id": approval_request.id,
                "audit_log_id": audit_log.id,
            }

        try:
            tool_result = execute_tool(
                tool_name=tool.name,
                input_text=input_text,
            )

            output_summary = tool_result.get(
                "summary",
                f"Tool '{tool.name}' completed successfully.",
            )

            audit_log = _save_audit_log(
                db,
                agent=agent,
                tool=tool,
                input_summary=input_text,
                output_summary=output_summary,
                status="completed",
                risk_level=decision.risk_level,
                approval_status=decision.approval_status,
                error_message=None,
            )

            return {
                "status": "completed",
                "message": "Tool call completed successfully.",
                "agent_name": agent.name,
                "tool_name": tool.name,
                "audit_log_id": audit_log.id,
                "result": tool_result,
            }

        except ToolExecutionError as exc:
            audit_log = _save_audit_log(
                db,
                agent=agent,
                tool=tool,
                input_summary=input_text,
                output_summary=None,
                status="failed",
                risk_level=decision.risk_level,
                approval_status=decision.approval_status,
                error_message=str(exc),
            )

            return {
                "status": "failed",
                "message": str(exc),
                "agent_name": agent.name,
                "tool_name": tool.name,
                "audit_log_id": audit_log.id,
            }

    finally:
        db.close()