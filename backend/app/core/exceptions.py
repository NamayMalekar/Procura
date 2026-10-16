class AppError(Exception):
    """Base class for expected errors."""


class NotFound(AppError):
    pass


class InvalidState(AppError):
    pass


class BrainError(AppError):
    """The decision engine could not produce a proposal."""
