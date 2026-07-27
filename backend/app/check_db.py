from app.database import SessionLocal
from app.models import Agent, Permission, Tool


def check_database():
    db = SessionLocal()

    try:
        agents = db.query(Agent).all()
        tools = db.query(Tool).all()
        permissions = db.query(Permission).all()

        print("\nAgents:")
        for agent in agents:
            print(f"- {agent.id}: {agent.name} ({agent.status})")

        print("\nTools:")
        for tool in tools:
            print(
                f"- {tool.id}: {tool.name} | Risk: {tool.risk_level} | "
                f"Action: {tool.action_type} | Approval: {tool.requires_approval}"
            )

        print("\nPermissions:")
        for permission in permissions:
            print(
                f"- Agent {permission.agent_id} -> Tool {permission.tool_id}: "
                f"{permission.access_level}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    check_database()