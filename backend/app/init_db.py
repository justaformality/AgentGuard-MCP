from app.database import Base, SessionLocal, engine
from app.models import Agent, ApprovalRequest, AuditLog, Permission, Tool
from app.seed import seed_database


def init_database():
    print("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    print("Tables created successfully.")

    db = SessionLocal()

    try:
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    init_database()