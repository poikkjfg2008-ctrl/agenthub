"""Core Pydantic models for AI Portal"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ResourceType(str, Enum):
    """Resource types in the portal"""
    DIRECT_CHAT = "direct_chat"
    SKILL_CHAT = "skill_chat"
    KB_WEBSDK = "kb_websdk"
    AGENT_WEBSDK = "agent_websdk"
    IFRAME = "iframe"


class LaunchMode(str, Enum):
    """Resource launch modes"""
    NATIVE = "native"  # Native chat interface
    WEBSDK = "websdk"  # WebSDK iframe embed
    IFRAME = "iframe"  # Direct iframe embed


class UserCtx(BaseModel):
    """User context from SSO"""
    emp_no: str = Field(..., description="Employee number")
    name: str = Field(..., description="User display name")
    dept: str = Field(default="demo", description="Department")
    roles: List[str] = Field(default_factory=lambda: ["employee"], description="User roles")
    email: Optional[str] = Field(None, description="Email address")


class ResourceConfig(BaseModel):
    """Base configuration for resources"""
    workspace_id: Optional[str] = None
    model: Optional[str] = None
    script_url: Optional[str] = None
    app_key: Optional[str] = None
    base_url: Optional[str] = None
    skill_name: Optional[str] = None
    starter_prompts: Optional[List[str]] = None
    iframe_url: Optional[str] = None  # Direct iframe URL for iframe mode


class Resource(BaseModel):
    """Resource catalog item"""
    id: str = Field(..., description="Unique resource identifier")
    name: str = Field(..., description="Resource display name")
    type: ResourceType = Field(..., description="Resource type")
    launch_mode: LaunchMode = Field(..., description="Launch mode")
    group: str = Field(..., description="Resource group for UI")
    description: str = Field(..., description="Resource description")
    enabled: bool = Field(default=True, description="Whether resource is enabled")
    tags: List[str] = Field(default_factory=list, description="Resource tags")
    config: ResourceConfig = Field(default_factory=ResourceConfig, description="Resource configuration")
    acl: Optional[Dict[str, Any]] = Field(default=None, description="Access control rules")


class PortalSession(BaseModel):
    """Portal session for native/skill chat"""
    portal_session_id: str = Field(..., description="Portal session UUID")
    engine_session_id: str = Field(..., description="OpenCode session ID")
    resource_id: str = Field(..., description="Resource that created this session")
    user_emp_no: str = Field(..., description="User employee number")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session metadata")


class LaunchRecord(BaseModel):
    """Launch record for WebSDK applications"""
    launch_id: str = Field(..., description="Launch record UUID")
    resource_id: str = Field(..., description="Resource that was launched")
    user_emp_no: str = Field(..., description="User employee number")
    launched_at: datetime = Field(default_factory=datetime.utcnow, description="Launch time")
    launch_token: str = Field(..., description="Launch token for WebSDK")
    user_context: Dict[str, Any] = Field(default_factory=dict, description="User context for WebSDK")


class Message(BaseModel):
    """Chat message"""
    role: str = Field(..., description="Message role: user/assistant/system")
    text: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")


class LaunchResponse(BaseModel):
    """Response from resource launch"""
    kind: LaunchMode = Field(..., description="Launch mode: native or websdk")
    portal_session_id: Optional[str] = Field(None, description="Portal session ID for native mode")
    launch_id: Optional[str] = Field(None, description="Launch ID for websdk mode")


class SkillInfo(BaseModel):
    """Skill information for skill store"""
    id: str = Field(..., description="Skill resource ID")
    name: str = Field(..., description="Skill name")
    description: str = Field(..., description="Skill description")
    installed: bool = Field(default=False, description="Whether skill is installed")
    skill_name: Optional[str] = Field(None, description="OpenCode skill name")
    starter_prompts: Optional[List[str]] = Field(None, description="Starter prompts")


class EmbedConfig(BaseModel):
    """WebSDK embed configuration"""
    script_url: str = Field(..., description="WebSDK script URL")
    app_key: str = Field(..., description="WebSDK app key")
    base_url: str = Field(..., description="WebSDK base URL")
    launch_token: str = Field(..., description="Launch token")
    user_context: Dict[str, Any] = Field(..., description="User context")


class IframeConfig(BaseModel):
    """Iframe embed configuration"""
    iframe_url: str = Field(..., description="Iframe URL to embed")
    user_context: Dict[str, Any] = Field(..., description="User context")
