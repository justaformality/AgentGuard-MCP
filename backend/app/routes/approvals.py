from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApprovalRequest, AuditLog
from app.schemas import (
    ApprovalActionResponse,
    ApprovalDecisionRequest,
    ApprovalRequestRead,
)
from app.tool_server.tool_runner import ToolExecutionError, execute_tool

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get("", response_model=list[ApprovalRequestRead])
def get_approvals(db: Session = Depends(get_db)):
    return (
        db.query(ApprovalRequest)
        .order_by(ApprovalRequest.created_at.desc())
        .all()
    )


@router.post(
    "/{approval_id}/approve",
    response_model=ApprovalActionResponse,
)
def approve_request(
    approval_id: int,
    decision: ApprovalDecisionRequest | None = None,
    db: Session = Depends(get_db),
):
    approval = (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found.",
        )

    if approval.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending approval requests can be approved.",
        )

    decision = decision or ApprovalDecisionRequest()

    original_input = approval.proposed_action.get(
        "input_text",
        approval.input_summary,
    )

    execution_input = decision.edited_input_text or original_input

    approval.status = "approved"
    approval.decision_reason = (
        decision.decision_reason or "Approved by human reviewer."
    )
    approval.decided_at = datetime.now(timezone.utc)

    try:
        result = execute_tool(
            tool_name=approval.tool.name,
            input_text=execution_input,
        )

        output_summary = result.get(
            "summary",
            "Approved tool executed successfully.",
        )

        audit_log = AuditLog(
            agent_id=approval.agent_id,
            tool_id=approval.tool_id,
            agent_name=approval.agent.name if approval.agent else None,
            tool_name=approval.tool.name if approval.tool else None,
            input_summary=execution_input,
            output_summary=output_summary,
            status="completed",
            risk_level=approval.tool.risk_level if approval.tool else None,
            approval_status="approved",
            error_message=None,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(approval)

        return ApprovalActionResponse(
            approval=approval,
            execution_status="completed",
            output_summary=str(result),
            error_message=None,
        )

    except ToolExecutionError as exc:
        audit_log = AuditLog(
            agent_id=approval.agent_id,
            tool_id=approval.tool_id,
            agent_name=approval.agent.name if approval.agent else None,
            tool_name=approval.tool.name if approval.tool else None,
            input_summary=execution_input,
            output_summary=None,
            status="failed",
            risk_level=approval.tool.risk_level if approval.tool else None,
            approval_status="approved",
            error_message=str(exc),
        )

        db.add(audit_log)
        db.commit()
        db.refresh(approval)

        return ApprovalActionResponse(
            approval=approval,
            execution_status="failed",
            output_summary=None,
            error_message=str(exc),
        )


@router.post("/{approval_id}/reject", response_model=ApprovalRequestRead)
def reject_request(
    approval_id: int,
    decision: ApprovalDecisionRequest | None = None,
    db: Session = Depends(get_db),
):
    approval = (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.id == approval_id)
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found.",
        )

    if approval.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending approval requests can be rejected.",
        )

    decision = decision or ApprovalDecisionRequest()

    approval.status = "rejected"
    approval.decision_reason = (
        decision.decision_reason or "Rejected by human reviewer."
    )
    approval.decided_at = datetime.now(timezone.utc)

    audit_log = AuditLog(
        agent_id=approval.agent_id,
        tool_id=approval.tool_id,
        agent_name=approval.agent.name if approval.agent else None,
        tool_name=approval.tool.name if approval.tool else None,
        input_summary=approval.input_summary,
        output_summary="Human reviewer rejected the requested action.",
        status="rejected",
        risk_level=approval.tool.risk_level if approval.tool else None,
        approval_status="rejected",
        error_message=None,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(approval)

    return approval