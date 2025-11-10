"""
Database Schemas for Freelance Platform

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name.

- User -> "user"
- Project -> "project"
- Message -> "message"
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    """
    Users of the platform (clients or admins)
    Collection: user
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    avatar_url: Optional[str] = Field(None, description="Profile avatar image URL")
    is_admin: bool = Field(False, description="Admin privileges")
    is_active: bool = Field(True, description="Whether the user is active")

class Project(BaseModel):
    """
    Projects created by users
    Collection: project
    """
    user_id: str = Field(..., description="Owner user id (stringified ObjectId)")
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(None, description="Project description / brief")
    status: str = Field("new", description="Project status: new, in_progress, completed, archived")
    tags: List[str] = Field(default_factory=list, description="Tech or domain tags")
    budget_min: Optional[float] = Field(None, ge=0, description="Minimum budget")
    budget_max: Optional[float] = Field(None, ge=0, description="Maximum budget")
    deadline: Optional[datetime] = Field(None, description="Desired deadline")

class Message(BaseModel):
    """
    Chat messages tied to a project
    Collection: message
    """
    project_id: str = Field(..., description="Related project id (stringified ObjectId)")
    author_id: str = Field(..., description="User id of the author (stringified ObjectId)")
    author_name: str = Field(..., description="Name shown in chat")
    role: str = Field("user", description="user | admin")
    content: str = Field(..., description="Message content")
