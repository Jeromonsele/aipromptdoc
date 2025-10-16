import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///prompt_gauge.db")

# sqlite needs check_same_thread=False only when using sqlite+aiosqlite or similar.
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def init_db():
    from .models import Project, Prompt, PromptVersion, Run, RunItem
    Base.metadata.create_all(bind=engine)
