class AuthError(Exception):
    pass


class InvalidToken(AuthError):  # noqa: N818
    pass


class EmailAlreadyRegistered(AuthError):  # noqa: N818
    pass


class InvalidCredentials(AuthError):  # noqa: N818
    pass
