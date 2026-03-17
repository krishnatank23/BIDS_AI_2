"""
SQLAlchemy ORM models for the Brand Identity Builder.
Tables: projects, agent_outputs, brand_kits
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(128), nullable=True, index=True)
    idea = Column(Text, nullable=False)
    current_step = Column(Integer, default=0)
    status = Column(String(32), default="created")  # created | running | completed
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    agent_outputs = relationship(
        "AgentOutput", back_populates="project", cascade="all, delete-orphan"
    )
    brand_kit = relationship(
        "BrandKit", back_populates="project", uselist=False, cascade="all, delete-orphan"
    )


class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_name = Column(String(64), nullable=False, index=True)
    output_json = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    project = relationship("Project", back_populates="agent_outputs")


class BrandKit(Base):
    __tablename__ = "brand_kits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    final_output = Column(JSON, nullable=True)
    export_path = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    project = relationship("Project", back_populates="brand_kit")
