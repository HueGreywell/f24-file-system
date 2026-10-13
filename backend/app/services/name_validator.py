from app.services.exceptions import InvalidNameException

MAX_LENGTH = 255


def normalize(name: str | None) -> str:
    if name is None:
        raise InvalidNameException("Name is required.")

    normalized = name.strip()
    if len(normalized) == 0:
        raise InvalidNameException("Name must not be empty.")
    if len(normalized) > MAX_LENGTH:
        raise InvalidNameException(f"Name must be at most {MAX_LENGTH} characters.")
    if "/" in normalized or "\\" in normalized:
        raise InvalidNameException("Name must not contain '/' or '\\'.")

    return normalized
