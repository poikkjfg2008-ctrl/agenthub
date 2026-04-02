"""FastAPI application entry point for AI Portal"""

import uuid
import json
from contextlib import asynccontextmanager
from typing import List, Optional, AsyncIterator
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request, Query, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import settings
from .models import (
    Resource, LaunchResponse, Message, SkillInfo, EmbedConfig, IframeConfig,
    ResourceType, LaunchMode, PortalSession, LaunchRecord, SessionBinding,
    PortalMessage, ContextScope, EnrichedPortalSession
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


class StreamMessageChunk(BaseModel):
    """SSE stream chunk for message response"""
    type: str  # "chunk" | "done" | "error"
    content: Optional[str] = None
    message_id: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Response for file upload"""
    file_id: str
    file_name: str
    file_type: str
    file_size: int
    url: str


class ContextUpdateRequest(BaseModel):
    """Request to update context scope"""
    payload: dict
    summary: Optional[str] = None


# Helpers

async def _get_session_or_404(portal_session_id: str, user) -> PortalSession:
    session = await storage.get_session(portal_session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {portal_session_id}"
        )
    if session.user_emp_no != user.emp_no:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session"
        )
    return session


async def _get_active_binding(portal_session_id: str) -> SessionBinding:
    bindings = await storage.get_bindings_by_session(portal_session_id)
    for binding in bindings:
        if binding.binding_status == "active":
            return binding
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No active binding found for session: {portal_session_id}"
    )


async def _save_portal_message(
    portal_session_id: str,
    role: str,
    text: str,
    trace_id: Optional[str] = None,
    metadata: Optional[dict] = None
) -> PortalMessage:
    message = PortalMessage(
        message_id=str(uuid.uuid4()),
        portal_session_id=portal_session_id,
        role=role,
        text=text,
        trace_id=trace_id,
        metadata=metadata or {}
    )
    await storage.save_message(message)
    return message


def _update_session_preview(session: PortalSession, text: str) -> None:
    session.last_message_at = datetime.utcnow()
    session.last_message_preview = text[:120] if text else None
    session.updated_at = datetime.utcnow()


def _enrich_session(session: PortalSession) -> dict:
    snapshot = session.resource_snapshot or {}
    resource_name = snapshot.get("resource_name", session.resource_id)
    return {
        "portal_session_id": session.portal_session_id,
        "resource_id": session.resource_id,
        "resource_type": session.resource_type,
        "resource_name": resource_name,
        "user_emp_no": session.user_emp_no,
        "title": session.title,
        "status": session.status,
        "resource_snapshot": snapshot,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        "last_message_at": session.last_message_at.isoformat() if session.last_message_at else None,
        "last_message_preview": session.last_message_preview,
        "parent_session_id": session.parent_session_id,
        "metadata": session.metadata,
    }


def _build_resource_snapshot(resource: Resource) -> dict:
    return {
        "resource_id": resource.id,
        "resource_name": resource.name,
        "resource_type": resource.type.value,
        "launch_mode": resource.launch_mode.value,
        "group": resource.group,
        "description": resource.description,
        "workspace_id": resource.config.workspace_id,
        "skill_name": resource.config.skill_name,
        "starter_prompts": resource.config.starter_prompts,
        "model": resource.config.model,
        "iframe_url": resource.config.iframe_url,
        "script_url": resource.config.script_url,
        "app_key": resource.config.app_key,
        "base_url": resource.config.base_url,
    }


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
    Creates a PortalSession + SessionBinding for all resource types.
    """
    resource = catalog_service.get_resource_by_id(resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found: {resource_id}"
        )

    if not acl_service.check_resource_access(resource, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resource"
        )

    portal_session_id = str(uuid.uuid4())
    snapshot = _build_resource_snapshot(resource)

    portal_session = PortalSession(
        portal_session_id=portal_session_id,
        resource_id=resource_id,
        resource_type=resource.type.value,
        user_emp_no=user.emp_no,
        title=resource.name,
        resource_snapshot=snapshot,
        metadata={"adapter": "opencode" if resource.type != ResourceType.SKILL_CHAT else "skill_chat"}
    )

    if resource.launch_mode == LaunchMode.NATIVE:
        user_context = {
            "emp_no": user.emp_no,
            "name": user.name,
            "dept": user.dept,
            "email": user.email
        }
        config = resource.config.model_dump()

        if resource.type == ResourceType.SKILL_CHAT:
            engine_session_id = await skill_chat_adapter.create_session(
                resource_id, user_context, config
            )
            adapter_name = "skill_chat"
            skill_name = resource.config.skill_name or resource_id
        else:
            engine_session_id = await opencode_adapter.create_session(
                resource_id, user_context, config
            )
            adapter_name = "opencode"
            skill_name = None

        binding = SessionBinding(
            binding_id=str(uuid.uuid4()),
            portal_session_id=portal_session_id,
            engine_type="opencode",
            adapter=adapter_name,
            engine_session_id=engine_session_id,
            workspace_id=resource.config.workspace_id or "default",
            skill_name=skill_name,
        )
        await storage.save_binding(binding)
        await storage.save_session(portal_session)

        return LaunchResponse(
            kind=LaunchMode.NATIVE,
            portal_session_id=portal_session.portal_session_id
        )

    elif resource.launch_mode == LaunchMode.WEBSDK:
        launch_record = websdk_adapter.create_launch_record(resource, user)
        await storage.save_launch(launch_record)

        binding = SessionBinding(
            binding_id=str(uuid.uuid4()),
            portal_session_id=portal_session_id,
            engine_type="websdk",
            adapter="websdk",
            external_session_ref=launch_record.launch_id,
            workspace_id=resource.config.workspace_id or "default",
        )
        await storage.save_binding(binding)
        await storage.save_session(portal_session)

        return LaunchResponse(
            kind=LaunchMode.WEBSDK,
            launch_id=launch_record.launch_id
        )

    elif resource.launch_mode == LaunchMode.IFRAME:
        launch_record = iframe_adapter.create_launch_record(resource, user)
        await storage.save_launch(launch_record)

        binding = SessionBinding(
            binding_id=str(uuid.uuid4()),
            portal_session_id=portal_session_id,
            engine_type="iframe",
            adapter="iframe",
            external_session_ref=launch_record.launch_id,
            workspace_id=resource.config.workspace_id or "default",
        )
        await storage.save_binding(binding)
        await storage.save_session(portal_session)

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
async def list_sessions(
    user: CurrentUser,
    limit: int = Query(50, ge=1, le=100),
    resource_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None, alias="type"),
    status: Optional[str] = Query(None),
):
    """
    List user's sessions sorted by time with optional filters.
    Returns enriched sessions including resource_name and last_message_preview.
    """
    sessions = await storage.list_user_sessions(
        user.emp_no, limit=limit, resource_id=resource_id, resource_type=type, status=status
    )
    enriched = [_enrich_session(s) for s in sessions]
    return {"sessions": enriched}


@app.get("/api/sessions/{portal_session_id}")
async def get_session(portal_session_id: str, user: CurrentUser):
    """
    Get session details by ID
    """
    session = await _get_session_or_404(portal_session_id, user)
    return _enrich_session(session)


@app.get("/api/sessions/{portal_session_id}/messages", response_model=List[Message])
async def get_session_messages(portal_session_id: str, user: CurrentUser):
    """
    Get messages for a session.
    Returns PortalMessage records. Falls back to engine and backfills if local store is empty.
    """
    session = await _get_session_or_404(portal_session_id, user)

    portal_messages = await storage.list_session_messages(portal_session_id, limit=500)

    if portal_messages:
        return [
            Message(
                role=msg.role,
                text=msg.text,
                timestamp=msg.created_at
            )
            for msg in portal_messages
        ]

    # Migration / fallback: fetch from engine and backfill
    binding = await _get_active_binding(portal_session_id)
    adapter_name = session.metadata.get("adapter", "opencode")

    if adapter_name == "skill_chat":
        messages = await skill_chat_adapter.get_messages(binding.engine_session_id)
    else:
        messages = await opencode_adapter.get_messages(binding.engine_session_id)

    # Backfill into PortalMessage store
    for msg in messages:
        await _save_portal_message(
            portal_session_id=portal_session_id,
            role=msg.role,
            text=msg.text,
        )

    return messages


@app.post("/api/sessions/{portal_session_id}/messages")
async def send_session_message(
    portal_session_id: str,
    body: SendMessageRequest,
    request: Request,
    user: CurrentUser
):
    """
    Send a message to a session (non-streaming)
    Persists user message, calls adapter, persists assistant message, and updates session preview.
    """
    import traceback

    try:
        session = await _get_session_or_404(portal_session_id, user)
        binding = await _get_active_binding(portal_session_id)

        trace_context = getattr(request.state, "trace_context", None)
        trace_id = getattr(trace_context, "trace_id", None)

        # Persist user message
        await _save_portal_message(
            portal_session_id=portal_session_id,
            role="user",
            text=body.text,
            trace_id=trace_id,
        )

        adapter_name = session.metadata.get("adapter", "opencode")

        if adapter_name == "skill_chat":
            response = await skill_chat_adapter.send_message(
                binding.engine_session_id,
                body.text,
                trace_id,
                skill_name=binding.skill_name,
            )
        else:
            response = await opencode_adapter.send_message(
                binding.engine_session_id,
                body.text,
                trace_id,
            )

        # Persist assistant message
        await _save_portal_message(
            portal_session_id=portal_session_id,
            role="assistant",
            text=response,
            trace_id=trace_id,
        )

        _update_session_preview(session, response)
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


async def stream_message_response(
    portal_session_id: str,
    body: SendMessageRequest,
    request: Request,
    user: CurrentUser
):
    """
    Generator for SSE streaming response with Portal message persistence
    """
    accumulated = ""
    assistant_message_id = ""

    try:
        session = await _get_session_or_404(portal_session_id, user)
        binding = await _get_active_binding(portal_session_id)

        trace_context = getattr(request.state, "trace_context", None)
        trace_id = getattr(trace_context, "trace_id", None)

        # Persist user message
        await _save_portal_message(
            portal_session_id=portal_session_id,
            role="user",
            text=body.text,
            trace_id=trace_id,
        )

        adapter_name = session.metadata.get("adapter", "opencode")
        message_id = str(uuid.uuid4())
        assistant_message_id = message_id

        yield f"data: {json.dumps({'type': 'start', 'message_id': message_id})}\n\n"

        if adapter_name == "skill_chat":
            stream_iter = skill_chat_adapter.send_message_stream(
                binding.engine_session_id,
                body.text,
                trace_id,
                skill_name=binding.skill_name,
            )
        else:
            stream_iter = opencode_adapter.send_message_stream(
                binding.engine_session_id,
                body.text,
                trace_id,
            )

        async for chunk in stream_iter:
            accumulated += chunk
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'message_id': message_id})}\n\n"

        # Persist assistant message after stream completes
        await _save_portal_message(
            portal_session_id=portal_session_id,
            role="assistant",
            text=accumulated,
            trace_id=trace_id,
        )

        _update_session_preview(session, accumulated)
        await storage.save_session(session)

        yield f"data: {json.dumps({'type': 'done', 'message_id': message_id})}\n\n"

    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"ERROR in send_session_message_stream: {error_detail}")

        # If we accumulated some text but hit an error, still try to persist it
        if accumulated:
            try:
                await _save_portal_message(
                    portal_session_id=portal_session_id,
                    role="assistant",
                    text=accumulated,
                    trace_id=getattr(request.state, "trace_context", None) and getattr(request.state.trace_context, "trace_id", None),
                )
                session = await storage.get_session(portal_session_id)
                if session:
                    _update_session_preview(session, accumulated)
                    await storage.save_session(session)
            except Exception:
                pass

        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


@app.post("/api/sessions/{portal_session_id}/messages/stream")
async def send_session_message_stream(
    portal_session_id: str,
    body: SendMessageRequest,
    request: Request,
    user: CurrentUser
):
    """
    Send a message to a session with SSE streaming response
    """
    return StreamingResponse(
        stream_message_response(portal_session_id, body, request, user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/api/sessions/{portal_session_id}/archive")
async def archive_session(portal_session_id: str, user: CurrentUser):
    """
    Archive a session
    """
    session = await _get_session_or_404(portal_session_id, user)
    session.status = "archived"
    session.updated_at = datetime.utcnow()
    await storage.save_session(session)
    return {"success": True, "status": "archived"}


@app.post("/api/sessions/{portal_session_id}/upload", response_model=FileUploadResponse)
async def upload_file_to_session(
    portal_session_id: str,
    user: CurrentUser,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
):
    """
    Upload a file to a session
    """
    try:
        session = await _get_session_or_404(portal_session_id, user)
        binding = await _get_active_binding(portal_session_id)

        adapter_name = session.metadata.get("adapter", "opencode")

        if adapter_name == "skill_chat":
            result = await skill_chat_adapter.upload_file(
                binding.engine_session_id,
                file,
                description
            )
        else:
            result = await opencode_adapter.upload_file(
                binding.engine_session_id,
                file,
                description
            )

        return FileUploadResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@app.get("/api/sessions/{portal_session_id}/context")
async def get_session_context(portal_session_id: str, user: CurrentUser):
    """
    Get resolved context for a session by merging applicable scopes.
    """
    session = await _get_session_or_404(portal_session_id, user)

    user_key = user.emp_no
    user_resource_key = f"{user.emp_no}:{session.resource_id}"
    session_key = portal_session_id

    global_ctx = await storage.get_contexts_by_scope("global", "global", limit=1)
    user_ctx = await storage.get_contexts_by_scope("user", user_key, limit=1)
    user_res_ctx = await storage.get_contexts_by_scope("user_resource", user_resource_key, limit=1)
    session_ctx = await storage.get_contexts_by_scope("session", session_key, limit=1)

    merged = {}
    for ctx in reversed(global_ctx + user_ctx + user_res_ctx + session_ctx):
        merged.update(ctx.payload or {})

    return {
        "portal_session_id": portal_session_id,
        "scopes": {
            "global": global_ctx[0].payload if global_ctx else {},
            "user": user_ctx[0].payload if user_ctx else {},
            "user_resource": user_res_ctx[0].payload if user_res_ctx else {},
            "session": session_ctx[0].payload if session_ctx else {},
        },
        "merged": merged,
    }


@app.get("/api/launches/{launch_id}/embed-config", response_model=EmbedConfig)
async def get_embed_config(launch_id: str, user: CurrentUser):
    """
    Get WebSDK embed configuration for a launch
    """
    launch = await storage.get_launch(launch_id)
    if not launch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Launch not found: {launch_id}"
        )

    if launch.user_emp_no != user.emp_no:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this launch"
        )

    resource = catalog_service.get_resource_by_id(launch.resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found: {launch.resource_id}"
        )

    if resource.launch_mode != LaunchMode.WEBSDK:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource '{resource.name}' is not a WebSDK resource. Launch mode: {resource.launch_mode}"
        )

    embed_config = websdk_adapter.get_embed_config(launch, resource)
    return embed_config


@app.get("/api/launches/{launch_id}/iframe-config", response_model=IframeConfig)
async def get_iframe_config(launch_id: str, user: CurrentUser):
    """
    Get iframe embed configuration for a launch
    """
    launch = await storage.get_launch(launch_id)
    if not launch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Launch not found: {launch_id}"
        )

    if launch.user_emp_no != user.emp_no:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this launch"
        )

    resource = catalog_service.get_resource_by_id(launch.resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found: {launch.resource_id}"
        )

    if resource.launch_mode != LaunchMode.IFRAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource '{resource.name}' is not an iframe resource. Launch mode: {resource.launch_mode}"
        )

    iframe_config = iframe_adapter.get_iframe_config(launch, resource)
    return iframe_config


@app.get("/api/skills", response_model=List[SkillInfo])
async def list_skills(user: CurrentUser):
    """
    List all skills with installation status
    """
    skill_resources = catalog_service.get_skill_resources()

    skills = []
    for resource in skill_resources:
        if not acl_service.check_resource_access(resource, user):
            continue

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


@app.patch("/api/contexts/user-resource/{resource_id}")
async def update_user_resource_context(
    resource_id: str,
    body: ContextUpdateRequest,
    user: CurrentUser
):
    """
    Update user-resource level context scope
    """
    scope_key = f"{user.emp_no}:{resource_id}"

    contexts = await storage.get_contexts_by_scope("user_resource", scope_key, limit=1)

    if contexts:
        context = contexts[0]
        context.payload = body.payload
        context.summary = body.summary
        context.updated_at = datetime.utcnow()
    else:
        context = ContextScope(
            context_id=str(uuid.uuid4()),
            scope_type="user_resource",
            scope_key=scope_key,
            payload=body.payload,
            summary=body.summary,
        )

    await storage.save_context(context)
    return {"success": True, "context_id": context.context_id}


@app.post("/api/admin/resources/sync")
async def admin_sync_resources(
    workspace_id: str = Query("default"),
    user: CurrentUser = None,  # In real impl, require admin role
):
    """
    Trigger resource sync from OpenWork.
    """
    # Import here to avoid circular issues
    from scripts.sync_resources import sync_resources

    merged = await sync_resources(workspace_id=workspace_id, reload_catalog=True)
    return {"success": True, "count": len(merged), "workspace_id": workspace_id}


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

    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url=f"/api/auth/mock-login?emp_no=E10001",
            status_code=status.HTTP_302_FOUND
        )

    frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
    if os.path.exists(frontend_path):
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        index_path = os.path.join(frontend_path, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)

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
