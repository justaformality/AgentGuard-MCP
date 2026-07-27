from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tool
from app.schemas import ToolCreate, ToolRead, ToolUpdate

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.get("", response_model=list[ToolRead])
def get_tools(db: Session = Depends(get_db)):
    return db.query(Tool).order_by(Tool.id).all()


@router.post("", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
def create_tool(tool_data: ToolCreate, db: Session = Depends(get_db)):
    existing_tool = db.query(Tool).filter(Tool.name == tool_data.name).first()

    if existing_tool:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tool with this name already exists.",
        )

    tool = Tool(**tool_data.model_dump())

    db.add(tool)
    db.commit()
    db.refresh(tool)

    return tool


@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found.",
        )

    return tool


@router.put("/{tool_id}", response_model=ToolRead)
def update_tool(
    tool_id: int,
    tool_data: ToolUpdate,
    db: Session = Depends(get_db),
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found.",
        )

    update_data = tool_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(tool, field, value)

    db.commit()
    db.refresh(tool)

    return tool