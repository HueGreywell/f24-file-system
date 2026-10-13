class DomainException(Exception):
    status_code: int = 400

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class InvalidNameException(DomainException):
    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__("INVALID_NAME", message)


class EntryNotFoundException(DomainException):
    status_code = 404

    def __init__(self, message: str) -> None:
        super().__init__("NOT_FOUND", message)


class CannotDeleteRootException(DomainException):
    status_code = 400

    def __init__(self, message: str) -> None:
        super().__init__("CANNOT_DELETE_ROOT", message)


class DuplicateNameException(DomainException):
    status_code = 409

    def __init__(self, message: str) -> None:
        super().__init__("DUPLICATE_NAME", message)
