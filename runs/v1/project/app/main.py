from fastapi import FastAPI, Depends, HTTPException, Header, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timedelta
import os
import jwt
import bcrypt
from typing import Annotated, List, Optional, Literal
from app.database import Base, engine, get_db
from app.routers import project_router, task_router, auth_router
from app.schemas import UserCreate, UserResponse, TokenResponse, ProjectCreate, ProjectResponse, ProjectListResponse, TaskCreate, TaskResponse, TaskListResponse
from app.auth import get_current_user, get_current_user_or_raise

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="member")
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="tasks")
    title = Column(String)
    description = Column(String)
    status = Column(String, default="todo")
    __table_args__ = {"extend_existing": True}

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Management API"}
