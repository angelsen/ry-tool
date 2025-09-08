"""
Custom exceptions for ry.
"""


class RyError(Exception):
    """Base exception for all ry errors."""

    pass


class TemplateError(RyError):
    """Template variable not found or invalid."""

    pass


class LoaderError(RyError):
    """YAML loader tag failed."""

    pass


class ExecutorError(RyError):
    """Executor compilation or execution failed."""

    pass


class LibraryError(RyError):
    """Library not found or invalid."""

    pass
