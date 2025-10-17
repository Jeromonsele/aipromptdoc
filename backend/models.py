from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Float, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from db import Base

# Version lifecycle constants
VERSION_STATES = {
    "draft": "Experimental or WIP prompt",
    "test": "Under evaluation or in active testing",
    "prod": "Approved, stable version"
}

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Prompt(Base):
    __tablename__ = "prompts"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    style: Mapped[str] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(50), default="plain")
    body: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(String(200), default="")
    created_by: Mapped[str] = mapped_column(String(120), default="anonymous")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project = relationship("Project", backref="prompts")

class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.id"), nullable=True)
    version_label: Mapped[str] = mapped_column(String(50), default="scratchpad")
    model: Mapped[str] = mapped_column(String(120), default="gpt-4o-mini")
    params_json: Mapped[str] = mapped_column(Text, default="{}")
    changelog: Mapped[str] = mapped_column(Text, default="")
    is_prod: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    prompt = relationship("Prompt", backref="versions")

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    prompt_version_id: Mapped[int] = mapped_column(ForeignKey("prompt_versions.id"))
    style: Mapped[str] = mapped_column(String(50), default="directive")
    model: Mapped[str] = mapped_column(String(120), default="gpt-4o-mini")
    params_json: Mapped[str] = mapped_column(Text, default="{}")
    source: Mapped[str] = mapped_column(String(50), default="web")  # web, api, cli, notebook, etc.
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    run_items = relationship("RunItem", backref="run")

class RunItem(Base):
    __tablename__ = "run_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    input_ref: Mapped[str] = mapped_column(Text)
    output_ref: Mapped[str] = mapped_column(Text)
    pass_bool: Mapped[bool] = mapped_column(Boolean, default=False)
    similarity: Mapped[float] = mapped_column(Float, default=0.0)
    judge_score: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PromptScore(Base):
    __tablename__ = "prompt_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    prompt_text: Mapped[str] = mapped_column(Text)
    score: Mapped[int] = mapped_column(Integer)
    problems_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class PromptTransformation(Base):
    __tablename__ = "prompt_transformations"
    id: Mapped[int] = mapped_column(primary_key=True)
    before_id: Mapped[int] = mapped_column(ForeignKey("prompt_scores.id"))
    after_prompt_text: Mapped[str] = mapped_column(Text)
    after_score: Mapped[int] = mapped_column(Integer)
    fixes_json: Mapped[str] = mapped_column(Text, default="[]")
    improvement_pct: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    before_score = relationship("PromptScore", foreign_keys=[before_id])
