from contextvars import ContextVar

_log_context: ContextVar[dict] = ContextVar("log_context", default={})


def set_log_context(**kwargs):
    """
    Set the log context for the current request.
    This function updates the log context with the provided keyword arguments.
    """
    context = _log_context.get().copy()
    context.update(kwargs)
    _log_context.set(context)

def get_log_context() -> dict:
    """
    Get the log context for the current request.
    This function returns the current log context as a dictionary.
    """
    return _log_context.get()

def clear_log_context():
    """
    Clear the log context for the current request.
    This function resets the log context to an empty dictionary.
    """
    _log_context.set({})