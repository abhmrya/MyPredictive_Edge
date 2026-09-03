import logging

from app.core.config import settings
from app.utils.log_context import get_log_context


class ContextFilter(logging.Filter):
    """
    Adds request context information to every log record.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        context = get_log_context()

        record.request_id = context.get("request_id", "-")
        record.correlation_id = context.get("correlation_id", "-")
        record.user_id = context.get("user_id", "-")
        record.organization_id = context.get("organization_id", "-")
        record.http_method = context.get("http_method", "-")
        record.http_path = context.get("http_path", "-")
        record.client_ip = context.get("client_ip", "-")

        # Log metadata
        record.event_name = getattr(record, "event_name", "-")
        record.status_code = getattr(record, "status_code", "-")
        record.duration_ms = getattr(record, "duration_ms", "-")

        return True


class ContextFormatter(logging.Formatter):
    """
    Formats logs with request context and metadata.
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)

        return (
            f"{timestamp} "
            f"[{record.levelname}] "
            f"[request_id={record.request_id}] "
            f"[correlation_id={record.correlation_id}] "
            f"[user_id={record.user_id}] "
            f"[event={record.event_name}] "
            f"[status_code={record.status_code}] "
            f"[duration_ms={record.duration_ms}] "
            f"{record.getMessage()}"
        )


def setup_logger() -> logging.Logger:
    logger_instance = logging.getLogger(settings.service_name)

    logger_instance.setLevel(
        getattr(
            logging,
            settings.log_level,
            logging.INFO,
        )
    )

    if not logger_instance.handlers:
        handler = logging.StreamHandler()

        handler.setFormatter(
            ContextFormatter(
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        handler.addFilter(ContextFilter())
        logger_instance.addHandler(handler)

    logger_instance.propagate = False

    return logger_instance


logger = setup_logger()


def log_event(
    level: str,
    message: str,
    *args,
    **kwargs,
):
    """
    Central helper for application logging.
    """

    event_name = kwargs.pop("event_name", "-")
    status_code = kwargs.pop("status_code", "-")
    duration_ms = kwargs.pop("duration_ms", "-")

    extra = kwargs.pop("extra", {}).copy()

    extra.update(
        {
            "event_name": event_name,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }
    )

    log_method = getattr(
        logger,
        level.lower(),
        logger.info,
    )

    log_method(
        message,
        *args,
        extra=extra,
        **kwargs,
    )