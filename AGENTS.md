# AGENTS.md - AI Portal Project Guide

This file provides essential information for AI coding agents working on the AI Portal project.

---

## Project Overview

**AI Portal** is a unified enterprise AI entry point that integrates multiple AI capabilities into a single portal:
- Native chat (direct chat with AI models)
- Skill chat (AI with specialized system prompts)
- Knowledge base via WebSDK embedding
- Legacy WebSDK app integration
- Iframe-based third-party app integration

**Architecture**: FastAPI backend (BFF pattern) + React (Vite) frontend

```
[Mock SSO / Future Real SSO]
          │
          ▼
      [Portal Web UI] (React + Vite)
          │
          ▼
     [FastAPI BFF] (Python 3.12+)
   ├─ Auth / ACL / Catalog
   ├─ Session Center (native+skill)
   ├─ Launch Record Center (websdk+iframe)
   ├─ OpenCodeAdapter
   ├─ SkillChatAdapter
   ├─ WebSDKAdapter
   ├─ IframeAdapter
   └─ OpenWorkAdapter
          │
   ┌──────┼───────────────┐
   ▼      ▼               ▼
OpenCode  OpenWork        WebSDK/Iframe Apps
```

---

## Technology Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI 0.115+
- **Server**: Uvicorn 0.32+
- **Dependencies**: 
  - Pydantic 2.10+ (data validation)
  - PyJWT 2.10+ (authentication)
  - httpx 0.28+ (HTTP client)
  - redis 5.2+ (optional storage)
  - python-multipart 0.0.20+ (form parsing)
- **Configuration**: Pydantic Settings with `.env` file
- **Package Manager**: pip with `requirements.txt` and `pyproject.toml`

### Frontend
- **Language**: TypeScript 5.7+
- **Framework**: React 18
- **Build Tool**: Vite 6.0+
- **Routing**: React Router DOM 6.28+
- **Styling**: Tailwind CSS 3.4+
- **HTTP Client**: Axios 1.7+
- **Icons**: Lucide React 0.468+
- **Markdown**: react-markdown, remark-gfm, remark-math, rehype-katex
- **Package Manager**: npm

### Frontend V2 Features (2026-03-28)
- **New Layout**: Three-column design (Resource Sidebar + Chat Area + Workspace)
- **Resource Sidebar**: Collapsible groups with card-style resource display
- **Markdown Support**: Full markdown rendering with tables, math formulas, code highlighting
- **Auto-resizing Input**: Dynamic height textarea with max 200px limit
- **Unique Icons**: Gradient backgrounds for each resource type

### Infrastructure
- **Storage**: Memory (dev) / Redis 7 (prod)
- **Container**: Docker Compose for Redis service
- **Authentication**: JWT Cookie-based with mock SSO fallback

---

## Project Structure

```
agenthub/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point, all routes
│   │   ├── config.py               # Pydantic settings
│   │   ├── models.py               # Pydantic models (Resource, UserCtx, etc.)
│   │   ├── adapters/
│   │   │   ├── base.py             # ExecutionAdapter ABC
│   │   │   ├── opencode.py         # Native chat adapter (OpenCode API)
│   │   │   ├── skill_chat.py       # Skill mode adapter
│   │   │   ├── websdk.py           # WebSDK launch adapter
│   │   │   ├── iframe.py           # Iframe embed adapter
│   │   │   └── openwork.py         # OpenWork API adapter (skills)
│   │   ├── auth/
│   │   │   ├── service.py          # JWT generation/validation
│   │   │   ├── deps.py             # FastAPI dependencies (CurrentUser)
│   │   │   └── routes.py           # Auth endpoints (/api/auth/*)
│   │   ├── catalog/
│   │   │   └── service.py          # Resource catalog loading from JSON
│   │   ├── acl/
│   │   │   └── service.py          # Access control (resource filtering)
│   │   ├── store/
│   │   │   ├── __init__.py         # Store selector (Redis/Memory)
│   │   │   ├── memory_store.py     # In-memory storage
│   │   │   └── redis_store.py      # Redis persistence
│   │   └── logging/
│   │       └── middleware.py       # Trace ID middleware
│   ├── config/
│   │   └── resources.json          # Resource catalog configuration
│   ├── tests/
│   │   ├── test_api.py             # Full API tests
│   │   ├── test_api_simple.py      # Quick smoke tests
│   │   ├── test_preflight_check.py # Preflight check tests
│   │   └── run_backend_tests.sh    # Test runner script
│   ├── pyproject.toml              # Python project config
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Main app with router
│   │   ├── api.ts                  # API client (axios)
│   │   ├── types.ts                # TypeScript interfaces
│   │   ├── main.tsx                # Entry point
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx   # Native/skill chat UI with Markdown support
│   │   │   ├── SessionSidebar.tsx  # Session list sidebar
│   │   │   ├── ResourceSidebar.tsx # Resource sidebar (V2) - collapsible groups
│   │   │   ├── ResourceCard.tsx    # Resource card component
│   │   │   ├── WorkspacePane.tsx   # WebSDK container
│   │   │   └── IframeWorkspace.tsx # Iframe embed component
│   │   ├── styles/
│   │   │   └── globals.css         # Global styles + Tailwind
│   │   └── tests/                  # Frontend tests
│   │       ├── test_frontend.js
│   │       └── test_frontend.tsx
│   ├── public/                     # Static assets
│   ├── package.json                # NPM config
│   ├── tsconfig.json               # TypeScript config
│   ├── tailwind.config.js          # Tailwind config
│   ├── vite.config.ts              # Vite config
│   └── .env                        # Frontend env vars
├── public/
│   └── sdk-host.html               # WebSDK host page for iframe
├── scripts/
│   ├── start.sh                    # Start all services
│   ├── stop.sh                     # Stop all services
│   ├── test.sh                     # Run tests
│   └── preflight_check.py          # Pre-start checks
├── logs/                           # Service logs
├── docker-compose.yml              # Redis service
└── docs/                           # Documentation
```

---

## Build and Development Commands

### Quick Start (Recommended)

```bash
# Start all services (backend + frontend) with preflight checks
./scripts/start.sh

# Stop all services
./scripts/stop.sh

# Run preflight checks only
python3 scripts/preflight_check.py

# CI mode (no network checks)
python scripts/preflight_check.py --no-network
```

### Backend Development

```bash
cd backend

# Install dependencies
/home/yy/python312/bin/python -m pip install -r requirements.txt

# Run development server (with hot reload)
/home/yy/python312/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
/home/yy/python312/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

### Testing

```bash
# Run all tests
./scripts/test.sh

# Backend tests only
cd backend && /home/yy/python312/bin/python tests/test_api_simple.py
cd backend && /home/yy/python312/bin/python tests/test_api.py
```

---

## Service URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **OpenAPI Docs**: http://localhost:8000/docs
- **Redis** (if enabled): redis://localhost:6379

---

## Environment Configuration

### Backend (`backend/.env`)

```bash
# Server
PORT=8000
HOST=0.0.0.0
RELOAD=true

# Storage
USE_REDIS=false                    # Set true for Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
AUTH_MOCK_FALLBACK_ENABLED=false   # Dev only: fallback to mock user

# OpenCode API
OPENCODE_BASE_URL=http://127.0.0.1:4096
OPENCODE_USERNAME=opencode
OPENCODE_PASSWORD=your-password

# OpenWork API
OPENWORK_BASE_URL=http://127.0.0.1:8787
OPENWORK_TOKEN=your-token

# Portal
PORTAL_NAME=AI Portal
RESOURCES_PATH=config/resources.json

# Logging
LOG_LEVEL=INFO
```

### Frontend (`frontend/.env`)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AI Portal
```

---

## Code Style Guidelines

### Python (Backend)

- **Style**: PEP 8
- **Docstrings**: Google style
- **Type Hints**: Use typing module for function signatures
- **Async**: Prefer async/await for I/O operations
- **Imports**: Group as: stdlib, third-party, local
- **Naming**: snake_case for functions/variables, PascalCase for classes

Example:
```python
"""Module docstring."""

from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .models import Resource


class ResourceService:
    """Service for resource operations."""
    
    async def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get resource by ID.
        
        Args:
            resource_id: The resource identifier.
            
        Returns:
            Resource if found, None otherwise.
        """
        pass
```

### TypeScript (Frontend)

- **Style**: ESLint recommended + React Hooks rules
- **Types**: Define interfaces in `types.ts`, avoid `any`
- **Components**: Functional components with hooks
- **Naming**: PascalCase for components/types, camelCase for functions/variables
- **Imports**: Group as: React, third-party, local (use `@/` for aliases)

Example:
```typescript
// types.ts
export interface Resource {
  id: string;
  name: string;
  type: ResourceType;
}

// Component
import { useState, useEffect } from 'react';
import type { Resource } from './types';

interface ResourceCardProps {
  resource: Resource;
  onLaunch: (r: Resource) => void;
}

export function ResourceCard({ resource, onLaunch }: ResourceCardProps) {
  // Implementation
}
```

---

## Testing Instructions

### Backend Tests

Located in `backend/tests/`:
- `test_api.py`: Comprehensive API tests
- `test_api_simple.py`: Quick smoke tests
- `test_preflight_check.py`: Preflight check tests

Run with:
```bash
cd backend
/home/yy/python312/bin/python tests/test_api_simple.py
```

### Test Coverage Areas

1. **Health Check**: `/api/health`
2. **Auth Flow**: mock-login → me → logout
3. **Resources**: list, grouped, get by ID, launch
4. **Sessions**: list, get messages, send message
5. **WebSDK**: launch, get embed-config
6. **Iframe**: launch, get iframe-config
7. **Skills**: list with installation status
8. **Authorization**: 401 for unauthenticated requests

### Manual Testing

```bash
# Health check
curl http://localhost:8000/api/health

# Mock login (saves cookie)
curl "http://localhost:8000/api/auth/mock-login?emp_no=E10001" -c cookies.txt

# Get current user
curl http://localhost:8000/api/auth/me -b cookies.txt

# List resources
curl http://localhost:8000/api/resources -b cookies.txt

# Launch native resource
curl -X POST http://localhost:8000/api/resources/general-chat/launch -b cookies.txt
```

---

## Security Considerations

### Authentication

- Uses JWT tokens in HTTP-only cookies
- Mock login for development (`/api/auth/mock-login`)
- Real SSO should replace mock auth in production

### Authorization (ACL)

- Current: "Allow if not configured" (permissive)
- Production: Change to default-deny or least privilege

### WebSDK Security

- `launch_token` is currently a random string
- **TODO**: Upgrade to signed JWT or HMAC for production

### Iframe Security

- Iframe URLs are configured in `resources.json`
- Ensure trusted domains only

### CORS

- Default allows localhost origins
- Production: Configure actual domain in `CORS_ORIGINS`

### Secrets

- Change `JWT_SECRET` in production (strong random string)
- Store `OPENCODE_PASSWORD` and `OPENWORK_TOKEN` securely
- Never commit `.env` files to version control

---

## Key Design Patterns

### 1. Adapter Pattern

All execution backends implement `ExecutionAdapter` ABC:

```python
class ExecutionAdapter(ABC):
    @abstractmethod
    async def create_session(self, resource_id, user_context, config) -> str:
        pass
    
    @abstractmethod
    async def send_message(self, session_id, message, trace_id) -> str:
        pass
```

Adapters:
- `OpenCodeAdapter`: Native chat sessions (HTTP API to OpenCode)
- `SkillChatAdapter`: Skill mode with system prompt injection
- `WebSDKAdapter`: WebSDK launch records (returns embed config)
- `IframeAdapter`: Direct iframe embed configuration
- `OpenWorkAdapter`: Skill management and status

### 2. Storage Abstraction

Unified interface with dual implementation:
- `MemoryStore`: In-memory dict (development default)
- `RedisStore`: Redis persistence (production)

Toggle via `USE_REDIS` environment variable.

### 3. Resource Launch Modes

- `native` → Creates `PortalSession` (maps to OpenCode session_id)
- `websdk` → Creates `LaunchRecord` (returns launch_id for embed config)
- `iframe` → Creates `LaunchRecord` (returns launch_id for iframe URL)

### 4. Frontend Routing

Path params via `useParams()`:
- `/chat/:sessionId` - Native/skill chat
- `/launch/:launchId` - WebSDK iframe
- `/iframe/:launchId` - Direct iframe

### 5. Frontend Layout (V2)

Three-column responsive layout:
```
┌──────────────┬──────────────────────────────┬───────────────┐
│  Resource    │   Session Sidebar (optional) │   Chat/       │
│  Sidebar     │   + Chat Interface           │   Workspace   │
│  (w-72)      │                              │   (optional)  │
│  288px       │     flex-1                   │   380-600px   │
└──────────────┴──────────────────────────────┴───────────────┘
```

- **Default Resource**: Auto-loads `general-chat` on startup
- **Resource Switching**: Click resource in sidebar to switch chat
- **Workspace Toggle**: WebSDK/iframe resources can toggle right workspace panel

---

## Resource Types

| Type | Launch Mode | Description |
|------|-------------|-------------|
| `direct_chat` | native | General chat with AI models |
| `skill_chat` | native | Specialized chat with system prompts |
| `kb_websdk` | websdk | Knowledge base via WebSDK |
| `agent_websdk` | websdk | Agent applications via WebSDK |
| `iframe` | iframe | Direct iframe embed |

---

## Important Files to Know

### Critical Backend Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI entry, all routes |
| `app/config.py` | Settings from environment |
| `app/models.py` | All Pydantic models |
| `app/adapters/base.py` | Adapter protocol |
| `config/resources.json` | Resource catalog |

### Critical Frontend Files

| File | Purpose |
|------|---------|
| `src/App.tsx` | Router and main layout (V2 three-column design) |
| `src/api.ts` | All API calls |
| `src/types.ts` | TypeScript interfaces |
| `src/components/ResourceSidebar.tsx` | Resource sidebar with collapsible groups |
| `src/components/ChatInterface.tsx` | Chat UI with Markdown support |
| `src/styles/globals.css` | Global styles + Tailwind + Markdown styles |
| `public/sdk-host.html` | WebSDK container |
| `docs/FRONTEND_UI_V2_DEVELOPMENT.md` | V2 UI development documentation |

---

## Common Issues and Solutions

### Issue: OpenCode connection errors

**Solution**: Check `OPENCODE_BASE_URL`, `OPENCODE_USERNAME`, `OPENCODE_PASSWORD` in `backend/.env`

### Issue: WebSDK blank page

**Solution**: 
1. Check `/api/launches/{launch_id}/embed-config` returns correct data
2. Verify `public/sdk-host.html` loads without errors
3. Check browser console for CORS or script loading errors

### Issue: Redis connection failed

**Solution**: 
1. Start Redis: `docker-compose up -d redis`
2. Or set `USE_REDIS=false` for memory storage

### Issue: Frontend can't connect to backend

**Solution**: 
1. Ensure backend is running on port 8000
2. Check `VITE_API_BASE_URL` in `frontend/.env`
3. Verify CORS settings in backend

---

## API Endpoints

### Health
- `GET /api/health` - Health check

### Authentication
- `GET /api/auth/mock-login?emp_no={id}` - Mock login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Resources
- `GET /api/resources` - List all resources
- `GET /api/resources/grouped` - List resources by group
- `GET /api/resources/{id}` - Get resource details
- `POST /api/resources/{id}/launch` - Launch resource

### Sessions (Native/Skill)
- `GET /api/sessions` - List user sessions
- `GET /api/sessions/{id}/messages` - Get session messages
- `POST /api/sessions/{id}/messages` - Send message

### Launches (WebSDK/Iframe)
- `GET /api/launches` - List launch records
- `GET /api/launches/{id}/embed-config` - Get WebSDK config
- `GET /api/launches/{id}/iframe-config` - Get iframe config

### Skills
- `GET /api/skills` - List skills with status

---

## Documentation References

- [QUICKSTART.md](QUICKSTART.md): 5-minute startup guide
- [API.md](API.md): Complete API reference
- [DEVELOPMENT.md](DEVELOPMENT.md): Development workflow
- [IMPLEMENTATION.md](IMPLEMENTATION.md): V1 design and architecture
- [FRONTEND_UI_V2_DEVELOPMENT.md](docs/FRONTEND_UI_V2_DEVELOPMENT.md): V2 UI development documentation (NEW)
- [PRESTART_CONDITIONS.md](PRESTART_CONDITIONS.md): Pre-flight check details
- [WEBSDK_EMBEDDING_GUIDE.md](WEBSDK_EMBEDDING_GUIDE.md): WebSDK configuration
- [TEST_REPORT.md](TEST_REPORT.md): Testing guidelines

---

## Language Note

This project uses **Chinese** as the primary language for:
- User-facing UI text
- Resource names and descriptions
- Documentation files (most)
- Comments in code (mixed with English)

Maintain consistency with existing language usage when modifying code or documentation.
