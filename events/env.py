from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://username:password@localhost:5432/doodle_app"
)

# Alternative SQLite for development
# DATABASE_URL = "sqlite:///./doodle_app.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True  # Verify connections before using them
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for FastAPI or regular session getter"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database (create all tables)"""
    from .models import Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all tables (use with caution!)"""
    from .models import Base
    Base.metadata.drop_all(bind=engine)