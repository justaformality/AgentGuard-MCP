from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    role: str = Field(..., min_length=2, max_length=255)
    status: str = "active"
    allowed_tools: list[str] = []
    blocked_tools: list[str] = []
    approval_rules: dict[str, Any] = {}


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    status: str | None = None
    allowed_tools: list[str] | None = None
    blocked_tools: list[str] | None = None
    approval_rules: dict[str, Any] | None = None


class AgentRead(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ToolBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: str = Field(..., min_length=5)
    category: str = Field(..., min_length=2, max_length=100)
    risk_level: str
    action_type: str
    requires_approval: bool = False
    enabled: bool = True


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    risk_level: str | None = None
    action_type: str | None = None
    requires_approval: bool | None = None
    enabled: bool | None = None


class ToolRead(ToolBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PermissionBase(BaseModel):
    agent_id: int
    tool_id: int
    access_level: str = "allowed"
    requires_approval_override: bool | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApprovalRequestBase(BaseModel):
    agent_id: int
    tool_id: int
    input_summary: str
    proposed_action: dict[str, Any] = {}
    status: str = "pending"
    decision_reason: str | None = None


class ApprovalRequestCreate(ApprovalRequestBase):
    pass


class ApprovalRequestRead(ApprovalRequestBase):
    id: int
    created_at: datetime
    decided_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogBase(BaseModel):
    agent_id: int | None = None
    tool_id: int | None = None
    agent_name: str | None = None
    tool_name: str | None = None
    input_summary: str
    output_summary: str | None = None
    status: str
    risk_level: str | None = None
    approval_status: str | None = None
    error_message: str | None = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RunAgentTaskRequest(BaseModel):
    agent_id: int
    tool_id: int
    input_text: str = Field(..., min_length=1)


class RunAgentTaskResponse(BaseModel):
    status: str
    message: str
    agent_name: str | None = None
    tool_name: str | None = None
    audit_log_id: int | None = None
    approval_request_id: int | None = None
    output_summary: str | None = None

class ApprovalDecisionRequest(BaseModel):
    edited_input_text: str | None = None
    decision_reason: str | None = None


class ApprovalActionResponse(BaseModel):
    approval: ApprovalRequestRead
    execution_status: str
    output_summary: str | None = None
    error_message: str | None = None