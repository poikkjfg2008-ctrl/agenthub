"""Trace middleware for request tracking and logging"""

import uuid
import json
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


logger = logging.getLogger(__name__)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields from record
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id
        if hasattr(record, "emp_no"):
            log_data["emp_no"] = record.emp_no
        if hasattr(record, "resource_id"):
            log_data["resource_id"] = record.resource_id
        if hasattr(record, "portal_session_id"):
            log_data["portal_session_id"] = record.portal_session_id
        if hasattr(record, "engine_session_id"):
            log_data["engine_session_id"] = record.engine_session_id
        if hasattr(record, "adapter"):
            log_data["adapter"] = record.adapter
        if hasattr(record, "cost_ms"):
            log_data["cost_ms"] = record.cost_ms

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class TraceContext:
    """Context for trace information"""

    def __init__(
        self,
        trace_id: str,
        emp_no: str | None = None,
        resource_id: str | None = None,
        portal_session_id: str | None = None,
        engine_session_id: str | None = None,
        adapter: str | None = None
    ):
        self.trace_id = trace_id
        self.emp_no = emp_no
        self.resource_id = resource_id
        self.portal_session_id = portal_session_id
        self.engine_session_id = engine_session_id
        self.adapter = adapter


class TraceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add trace_id to all requests and log request/response
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Configure logging with JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add trace context"""
        # Generate or extract trace_id
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())

        # Get user from request state if authenticated
        emp_no = None
        if hasattr(request.state, "user"):
            emp_no = request.state.user.emp_no

        # Start timing
        start_time = time.time()

        # Add trace context to request state
        request.state.trace_context = TraceContext(
            trace_id=trace_id,
            emp_no=emp_no
        )

        # Add trace_id to request headers for downstream
        request.headers.__dict__["_list"].append((b"x-trace-id", trace_id.encode()))

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log request with trace context
            log_data = {
                "trace_id": trace_id,
                "emp_no": emp_no,
                "path": request.url.path,
                "method": request.method,
                "status": response.status_code,
                "cost_ms": duration_ms
            }

            logger.info(f"Request completed", extra=log_data)

            # Add trace_id to response headers
            response.headers["X-Trace-ID"] = trace_id

            return response

        except Exception as e:
            # Calculate duration for failed request
            duration_ms = int((time.time() - start_time) * 1000)

            # Log error with trace context
            log_data = {
                "trace_id": trace_id,
                "emp_no": emp_no,
                "path": request.url.path,
                "method": request.method,
                "status": 500,
                "cost_ms": duration_ms,
                "error": str(e)
            }

            logger.error(f"Request failed", extra=log_data)
            raise
