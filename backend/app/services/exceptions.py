class DomainException(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class InvalidNameException(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__("INVALID_NAME", message)


class EntryNotFoundException(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__("NOT_FOUND", message)

class CannotDeleteRootException(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__("CANNOT_DELETE_ROOT", message)
