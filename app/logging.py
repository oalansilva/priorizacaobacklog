"""Configuração centralizada de logging estruturado."""

from __future__ import annotations

import logging
from typing import Optional

import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """Configura logging padrão + structlog."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


configure_logging()


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Retorna logger estruturado."""

    return structlog.get_logger(name)


