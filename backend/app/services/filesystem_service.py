from app.repositores.protocols import FileSystemRepositoryProtocol

class FileSystemService:
    def __init__(self, repository: FileSystemRepositoryProtocol) -> None:
        self._repository = repository

