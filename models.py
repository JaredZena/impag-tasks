from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Date,
    ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from flask import request
from config import database_url
from urllib.parse import urlparse, parse_qs, urlencode

Base = declarative_base()


class TaskUser(Base):
    __tablename__ = "task_user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default="member", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    tasks_created = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    tasks_assigned = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    comments = relationship("TaskComment", back_populates="user")
    categories_created = relationship("TaskCategory", back_populates="creator")


class TaskCategory(Base):
    __tablename__ = "task_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#6366f1", nullable=False)
    icon = Column(String(50), nullable=True)
    created_by = Column(Integer, ForeignKey("task_user.id"), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("TaskUser", back_populates="categories_created")
    tasks = relationship("Task", back_populates="category")


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False, index=True)
    priority = Column(String(10), default="medium", nullable=False)
    due_date = Column(Date, nullable=True)
    category_id = Column(Integer, ForeignKey("task_category.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("task_user.id"), nullable=False, index=True)
    assigned_to = Column(Integer, ForeignKey("task_user.id"), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("TaskUser", foreign_keys=[created_by], back_populates="tasks_created")
    assignee = relationship("TaskUser", foreign_keys=[assigned_to], back_populates="tasks_assigned")
    category = relationship("TaskCategory", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan",
                            order_by="TaskComment.created_at.asc()")


class TaskComment(Base):
    __tablename__ = "task_comment"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("task_user.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    task = relationship("Task", back_populates="comments")
    user = relationship("TaskUser", back_populates="comments")


# --- Database connection (same Neon pattern as impag-quot) ---

parsed_url = urlparse(database_url)
endpoint_id = parsed_url.hostname.split('.')[0]

query_params = parse_qs(parsed_url.query)
query_params['options'] = [f'endpoint={endpoint_id}']
new_query = urlencode(query_params, doseq=True)

modified_url = parsed_url._replace(query=new_query).geturl()
if not modified_url.startswith('postgresql+psycopg2://'):
    modified_url = modified_url.replace('postgresql://', 'postgresql+psycopg2://')

engine = create_engine(
    modified_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"application_name": "impag-tasks"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_task_user(db):
    """Get the task_user record for the currently authenticated user."""
    email = request.user_info["email"]
    user = db.query(TaskUser).filter(
        TaskUser.email == email,
        TaskUser.is_active == True
    ).first()
    return user
