from fastapi import APIRouter

from app.mcp_server.governed_executor import run_governed_tool
from app.schemas import RunAgentTaskRequest
from app.tool_server.tool_runner import list_available_tools

router = APIRouter(tags=["Demo Runner"])


@router.post("/run-agent-task")
def run_agent_task(request: RunAgentTaskRequest):
    return run_governed_tool(
        agent_id=request.agent_id,
        tool_name=_get_tool_name_from_id(request.tool_id),
        input_text=request.input_text,
    )


@router.get("/available-executable-tools")
def get_available_executable_tools():
    return {
        "available_tools": list_available_tools()
    }


def _get_tool_name_from_id(tool_id: int) -> str:
    from app.database import SessionLocal
    from app.models import Tool

    db = SessionLocal()

    try:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()

        if tool is None:
            return f"unknown_tool_id_{tool_id}"

        return tool.name

    finally:
        db.close()