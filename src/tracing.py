import contextvars
import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")


def get_trace_id() -> str:
    return _trace_id.get()


def set_trace_id(value: str) -> None:
    _trace_id.set(value)


def new_trace_id() -> str:
    return str(uuid.uuid4())


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = _trace_id.get() or "-"
        return True


_logger = logging.getLogger(__name__)


class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        tid = request.headers.get("X-Trace-Id") or new_trace_id()
        set_trace_id(tid)
        response = await call_next(request)
        _logger.info("%s %s %d", request.method, request.url.path, response.status_code)
        response.headers["X-Trace-Id"] = tid
        return response


def configure_logging() -> None:
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] trace=%(trace_id)s %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    handler.addFilter(TraceIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
