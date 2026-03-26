# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Portal is a unified enterprise AI entry point that integrates multiple AI capabilities (native chat, skill chat, knowledge base/legacy WebSDK apps, file-based skill/config management) into a single portal.

**Architecture**: FastAPI backend (BFF) + React (Vite) frontend
- Backend: Python 3.12+, FastAPI, uvicorn
- Frontend: React 18, TypeScript, Vite, Tailwind CSS

### V1 Scope
- ✅ Unified resource catalog with grouping
- ✅ Mock SSO authentication (JWT Cookie)
- ✅ Native/skill dialogue sessions
- ✅ WebSDK resource launch records
- ✅ Memory/Redis storage abstraction
- ✅ Trace middleware + structured JSON logging

## Common Commands

### Starting the Application

```bash
# Quick start (recommended) - runs preflight checks then starts both services
./scripts/start.sh

# Stop services
./scripts/stop.sh

# Run preflight checks only
python3 scripts/preflight_check.py
# Offline/CI mode (no network checks):
python scripts/preflight_check.py --no-network
```

### Backend Development

```bash
cd backend

# Install dependencies (uses project-specific Python)
/home/yy/python312/bin/python -m pip install -r requirements.txt

# Run backend (with hot reload)
/home/yy/python312/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
/home/yy/python312/bin/python tests/test_api_simple.py
/home/yy/python312/bin/python tests/test_api.py
```

Backend runs on `http://localhost:8000` with OpenAPI docs at `/docs`

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

Frontend runs on `http://localhost:5173`

### Testing

```bash
# Run full test suite
./scripts/test.sh

# Backend tests only
cd backend && /home/yy/python312/bin/python tests/test_api.py
```

## Architecture

### Backend Structure (`backend/app/`)

```
main.py              # FastAPI app entry point, routes, lifespan
config.py            # Pydantic settings from .env
models.py            # Pydantic models (Resource, PortalSession, LaunchRecord, etc.)

adapters/
  base.py            # ExecutionAdapter ABC protocol
  opencode.py        # OpenCodeAdapter (native chat sessions)
  skill_chat.py      # SkillChatAdapter (skill mode injection)
  websdk.py          # WebSDKAdapter (launch records + embed config)
  openwork.py        # OpenWorkAdapter (skill status, engine reload)

auth/
  service.py         # Mock SSO JWT generation/validation
  deps.py            # FastAPI CurrentUser/OptionalUser dependencies
  routes.py          # Auth endpoints (/api/auth/mock-login, /api/auth/me)

catalog/
  service.py         # Resource catalog loading from resources.json

acl/
  service.py         # Access control filtering

store/
  memory_store.py    # In-memory storage (default)
  redis_store.py     # Redis storage (production)

logging/
  middleware.py      # TraceMiddleware for request tracing
```

### Frontend Structure (`frontend/src/`)

```
App.tsx              # Main router + layout, auth flow
api.ts               # axios API client with typed methods
types.ts             # TypeScript interfaces

components/
  ChatInterface.tsx  # Chat UI for native/skill sessions
  SessionSidebar.tsx # Session history sidebar
  ResourceCard.tsx   # Resource catalog card
  WorkspacePane.tsx  # WebSDK iframe container
```

### Key Design Patterns

**Adapter Pattern**: All execution backends implement `ExecutionAdapter` ABC (`adapters/base.py`). Adapters handle:
- `create_session()` - Create backend session
- `send_message()` - Send message with trace context
- `get_messages()` - Fetch history
- `close_session()` - Cleanup

**Resource Launch Modes**:
- `native` → Creates `PortalSession` (maps to OpenCode session_id)
- `websdk` → Creates `LaunchRecord` (returns launch_id for embed config)

**Storage Abstraction**: `store` module provides unified interface with MemoryStore (dev) and RedisStore (prod). Toggle via `USE_REDIS` env var.

**Frontend Routing**: Path params via `useParams()`:
- `/chat/:sessionId` - Native/skill chat
- `/launch/:launchId` - WebSDK iframe

### Environment Configuration

Backend reads from `backend/.env`:
- `USE_REDIS` / `REDIS_URL` - Enable Redis storage
- `OPENCODE_BASE_URL` / `OPENCODE_USERNAME` / `OPENCODE_PASSWORD` - OpenCode API
- `OPENWORK_BASE_URL` / `OPENWORK_TOKEN` - OpenWork API
- `RESOURCES_PATH` - Path to resources.json (default: `config/resources.json`)
- `JWT_SECRET` - JWT signing key

Resource catalog defaults to `backend/config/resources.json`.

### Execution Flow Examples

**Native Chat Launch**:
1. User clicks resource card → `POST /api/resources/{id}/launch`
2. Main.py routes to adapter based on `resource_type`
3. Adapter creates engine session → returns `engine_session_id`
4. Portal creates `PortalSession` → saves to storage
5. Frontend navigates to `/chat/{portal_session_id}`

**Sending Message**:
1. Frontend posts to `POST /api/sessions/{id}/messages`
2. Main.py retrieves session from storage, gets adapter from metadata
3. Adapter calls engine with `X-Trace-ID` header
4. Response returned to frontend, session `updated_at` refreshed

**WebSDK Launch**:
1. `POST /api/resources/{id}/launch` for websdk resource
2. WebSDKAdapter creates `LaunchRecord` with random `launch_token`
3. Frontend navigates to `/launch/{launch_id}`
4. WorkspacePane calls `GET /api/launches/{id}/embed-config`
5. `sdk-host.html` loads third-party SDK with embed config

## Important Notes

- **Python Interpreter**: Scripts use `/home/yy/python312/bin/python` (hardcoded in project scripts)
- **Preflight Checks**: Start script validates OpenCode/OpenWork endpoints + WebSDK URLs before launching
- **Skill Mode**: `SkillChatAdapter` injects system prompt - no frontend changes needed
- **WebSDK Security**: Current `launch_token` is random string; upgrade to JWT/HMAC for production
- **Trace Context**: Use `request.state.trace_context.trace_id` for distributed tracing
- **ACL Default**: "Allow if not configured" - change to default-deny for enterprise
