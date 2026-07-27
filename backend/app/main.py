from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routes import agents, approvals, audit_logs, demo, tools
from app.seed import seed_database

app = FastAPI(
    title="AgentGuard MCP API",
    description="Backend API for AgentGuard MCP: AI agent permissions, approvals, and audit logging.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        seed_database(db)
    finally:
        db.close()


app.include_router(agents.router)
app.include_router(tools.router)
app.include_router(approvals.router)
app.include_router(audit_logs.router)
app.include_router(demo.router)


@app.get("/")
def root():
    return {
        "message": "AgentGuard MCP backend is running",
        "environment": settings.environment,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "agentguard-mcp-backend",
    }