"""FastAPI application entry point for AI Portal"""

import uuid
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import settings
from .models import (
    Resource, LaunchResponse, Message, SkillInfo, EmbedConfig, IframeConfig,
    ResourceType, LaunchMode
)
from .auth.deps import CurrentUser, OptionalUser
from .auth.routes import router as auth_router
from .catalog.service import catalog_service
from .acl.service import acl_service
from .adapters.opencode import OpenCodeAdapter
from .adapters.skill_chat import SkillChatAdapter
from .adapters.websdk import WebSDKAdapter
from .adapters.iframe import IframeAdapter
from .adapters.openwork import OpenWorkAdapter
from .store import store as storage
from .logging.middleware import TraceMiddleware


# Adapters instances
opencode_adapter = OpenCodeAdapter()
skill_chat_adapter = SkillChatAdapter()
websdk_adapter = WebSDKAdapter()
iframe_adapter = IframeAdapter()
openwork_adapter = OpenWorkAdapter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🚀 {settings.portal_name} starting up...")
    print(f"📦 Loaded {len(catalog_service.get_resources())} resources")
    print(f"🔗 Redis: {settings.redis_url}")
    print(f"🤖 OpenCode: {settings.opencode_base_url}")
    print(f"🛠️  OpenWork: {settings.openwork_base_url}")

    yield

    # Shutdown
    print("👋 Shutting down...")
    await opencode_adapter.close()
    await skill_chat_adapter.close()
    await openwork_adapter.close()

    # Close storage if Redis
    if hasattr(storage, 'close_async'):
        await storage.close_async()


# Create FastAPI app
app = FastAPI(
    title=settings.portal_name,
    description="Unified entry point for enterprise AI resources",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trace middleware
app.add_middleware(TraceMiddleware)

# Include auth routes
app.include_router(auth_router)

# Mount static files directory for sdk-host.html
from pathlib import Path
static_dir = Path(__file__).parent.parent.parent / "public"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Request models
class SendMessageRequest(BaseModel):
    """Request to send message"""
    text: str


# API Routes

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "portal_name": settings.portal_name,
        "version": "1.0.0"
    }


@app.get("/api/resources", response_model=List[Resource])
async def list_resources(user: CurrentUser):
    """
    List all resources accessible to current user
    """
    resources = catalog_service.get_resources()
    accessible_resources = acl_service.filter_accessible_resources(resources, user)
    return accessible_resources


@app.get("/api/resources/grouped")
async def list_resources_grouped(user: CurrentUser):
    """
    List resources grouped by category
    """
    resources = catalog_service.get_resources()
    accessible_resources = acl_service.filter_accessible_resources(resources, user)

    groups = {}
    for resource in accessible_resources:
        group = resource.group or "Other"
        if group not in groups:
            groups[group] = []
        groups[group].append(resource)

    return groups


@app.get("/api/resources/{resource_id}", response_model=Resource)
async def get_resource(resource_id: str, user: CurrentUser):
    """
    Get resource details by ID
    """
    resource = catalog_service.get_resource_by_id(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found: {resource_id}"
        )

    # Check access
    if not acl_service.check_resource_access(resource, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource"
        )

    return resource


@app.post("/api/resources/{resource_id}/launch", response_model=LaunchResponse)
async def launch_resource(resource_id: str, user: CurrentUser):
    """
    Launch a resource (create session or generate launch token)
    """
    # Get resource
    resource = catalog_service.get_resource_by_id(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found: {resource_id}"
        )

    # Check access
    if not acl_service.check_resource_access(resource, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource"
        )

    # Launch based on resource type
    if resource.launch_mode == LaunchMode.NATIVE:
        # Native mode - create session
        user_context = {
            "emp_no": user.emp_no,
            "name": user.name,
            "dept": user.dept,
            "email": user.email
        }

        config = resource.config.model_dump()

        # Choose adapter based on resource type
        if resource.type == ResourceType.SKILL_CHAT:
            engine_session_id = await skill_chat_adapter.create_session(
                resource_id,
                user_context,
                config
            )
            adapter_name = "skill_chat"
        else:
            engine_session_id = await opencode_adapter.create_session(
                resource_id,
                user_context,
                config
            )
            adapter_name = "opencode"

        # Create portal session
        from .models import PortalSession
        portal_session = PortalSession(
            portal_session_id=str(uuid.uuid4()),
            engine_session_id=engine_session_id,
            resource_id=resource_id,
            user_emp_no=user.emp_no,
            metadata={"adapter": adapter_name}
        )

        # Save to Redis
        await storage.save_session(portal_session)

        return LaunchResponse(
            kind=LaunchMode.NATIVE,
            portal_session_id=portal_session.portal_session_id
        )

    elif resource.launch_mode == LaunchMode.WEBSDK:
        # WebSDK mode - create launch record
        launch_record = websdk_adapter.create_launch_record(resource, user)

        # Save to storage
        await storage.save_launch(launch_record)

        return LaunchResponse(
            kind=LaunchMode.WEBSDK,
            launch_id=launch_record.launch_id
        )

    elif resource.launch_mode == LaunchMode.IFRAME:
        # Iframe mode - create launch record
        launch_record = iframe_adapter.create_launch_record(resource, user)

        # Save to storage
        await storage.save_launch(launch_record)

        return LaunchResponse(
            kind=LaunchMode.IFRAME,
            launch_id=launch_record.launch_id
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported launch mode: {resource.launch_mode}"
        )


@app.get("/api/sessions")
async def list_sessions(user: CurrentUser, limit: int = Query(50, ge=1, le=100)):
    """
    List user's native/skill sessions
    """
    sessions = await storage.list_user_sessions(user.emp_no, limit)
    return {"sessions": [s.model_dump() for s in sessions]}


@app.get("/api/sessions/{portal_session_id}")
async def get_session(
    portal_session_id: str,
    user: CurrentUser
):
    """
    Get session details by ID
    """
    # Get session
    session = await storage.get_session(portal_session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {portal_session_id}"
        )

    # Verify ownership
    if session.user_emp_no != user.emp_no:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session"
        )

    return session.model_dump()


@app.get("/api/sessions/{portal_session_id}/messages", response_model=List[Message])
async def get_session_messages(
    portal_session_id: str,
    user: CurrentUser
):
    """
    Get messages for a session
    """
    # Get session
    session = await storage.get_session(portal_session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {portal_session_id}"
        )

    # Verify ownership
    if session.user_emp_no != user.emp_no:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session"
        )

    # Get adapter from metadata
    adapter_name = session.metadata.get("adapter", "opencode")

    # Fetch messages from engine
    if adapter_name == "skill_chat":
        messages = await skill_chat_adapter.get_messages(session.engine_session_id)
    else:
        messages = await opencode_adapter.get_messages(session.engine_session_id)

    return messages


@app.post("/api/sessions/{portal_session_id}/messages")
async def send_session_message(
    portal_session_id: str,
    body: SendMessageRequest,
    request: Request,
    user: CurrentUser
):
    """
    Send a message to a session
    """
    import traceback
    
    try:
        # Get session
        session = await storage.get_session(portal_session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {portal_session_id}"
            )

        # Verify ownership
        if session.user_emp_no != user.emp_no:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )

        # Get adapter from metadata
        adapter_name = session.metadata.get("adapter", "opencode")

        # Send message via adapter
        trace_context = getattr(request.state, "trace_context", None)
        trace_id = getattr(trace_context, "trace_id", None)

        if adapter_name == "skill_chat":
            response = await skill_chat_adapter.send_message(
                session.engine_session_id,
                body.text,
                trace_id
            )
        else:
            response = await opencode_adapter.send_message(
                session.engine_session_id,
                body.text,
                trace_id
            )

        session.updated_at = datetime.utcnow()
        await storage.save_session(session)

        return {"response": response}
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"ERROR in send_session_message: {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@app.get("/api/launches/{launch_id}/embed-config", response_model=EmbedConfig)
async def get_embed_config(launch_id: str, user: CurrentUser):
    """
    Get WebSDK embed configuration for a launch
    """
    # Get launch record
    launch = await storage.get_launch(launch_id)
    if not launch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Launch not found: {launch_id}"
        )

    # Verify ownership
    if launch.user_emp_no != user.emp_no:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this launch"
        )

    # Get resource
    resource = catalog_service.get_resource_by_id(launch.resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found: {launch.resource_id}"
        )

    # Verify resource is WebSDK mode
    if resource.launch_mode != LaunchMode.WEBSDK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource '{resource.name}' is not a WebSDK resource. Launch mode: {resource.launch_mode}"
        )

    # Generate embed config
    embed_config = websdk_adapter.get_embed_config(launch, resource)
    return embed_config


@app.get("/api/launches/{launch_id}/iframe-config", response_model=IframeConfig)
async def get_iframe_config(launch_id: str, user: CurrentUser):
    """
    Get iframe embed configuration for a launch
    """
    # Get launch record
    launch = await storage.get_launch(launch_id)
    if not launch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Launch not found: {launch_id}"
        )

    # Verify ownership
    if launch.user_emp_no != user.emp_no:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this launch"
        )

    # Get resource
    resource = catalog_service.get_resource_by_id(launch.resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found: {launch.resource_id}"
        )

    # Verify resource is iframe mode
    if resource.launch_mode != LaunchMode.IFRAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource '{resource.name}' is not an iframe resource. Launch mode: {resource.launch_mode}"
        )

    # Generate iframe config
    iframe_config = iframe_adapter.get_iframe_config(launch, resource)
    return iframe_config


@app.get("/api/skills", response_model=List[SkillInfo])
async def list_skills(user: CurrentUser):
    """
    List all skills with installation status
    """
    # Get skill resources
    skill_resources = catalog_service.get_skill_resources()

    skills = []
    for resource in skill_resources:
        # Check if skill is accessible
        if not acl_service.check_resource_access(resource, user):
            continue

        # Get skill status from OpenWork
        skill_name = resource.config.skill_name
        skill_status = await openwork_adapter.get_skill_status(
            skill_name,
            resource.config.workspace_id or "default"
        )

        skills.append(SkillInfo(
            id=resource.id,
            name=resource.name,
            description=resource.description,
            installed=skill_status.get("installed", False),
            skill_name=skill_name,
            starter_prompts=resource.config.starter_prompts
        ))

    return skills


@app.get("/api/launches")
async def list_launches(user: CurrentUser, limit: int = Query(50, ge=1, le=100)):
    """
    List user's WebSDK launches
    """
    launches = await storage.list_user_launches(user.emp_no, limit)
    return {"launches": [l.model_dump() for l in launches]}


# Serve sdk-host.html explicitly
@app.get("/sdk-host.html")
async def serve_sdk_host():
    """Serve the WebSDK host page"""
    import os
    sdk_host_path = os.path.join(os.path.dirname(__file__), "../../public/sdk-host.html")
    if os.path.exists(sdk_host_path):
        return FileResponse(
            sdk_host_path,
            media_type="text/html",
            headers={"Cache-Control": "no-cache"}
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="sdk-host.html not found"
    )


# Serve frontend (for development/prod)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str, user: OptionalUser = None):
    """
    Serve frontend application
    Redirect to login if not authenticated
    """
    import os

    # Check if user is authenticated
    if not user:
        # Redirect to mock login page (in production, redirect to SSO)
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url=f"/api/auth/mock-login?emp_no=E10001",
            status_code=status.HTTP_302_FOUND
        )

    # Try to serve static file
    frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
    if os.path.exists(frontend_path):
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Return index.html for SPA routes
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)

    # Fallback response
    return {
        "message": f"{settings.portal_name} API",
        "docs": "/docs",
        "user": user.model_dump() if user else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
