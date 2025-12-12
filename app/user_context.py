from contextvars import ContextVar
from typing import Optional

user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
