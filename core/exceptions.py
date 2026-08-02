class ApplicationError(Exception):
    """Base exception for expected application failures."""


class NotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class AuthenticationError(ApplicationError):
    pass


class AuthorizationError(ApplicationError):
    pass


class ValidationError(ApplicationError):
    pass
