from uuid import uuid4

import pytest

from app.entities.enums import EntryType
from app.entities.folder import Folder
from app.schemas.entry import CreateEntryRequest
from app.services.exceptions import (
    CannotDeleteRootException,
    DuplicateNameException,
    EntryNotFoundException,
)
from app.services.filesystem_service import FileSystemService
from tests.fakes import FakeRepository


@pytest.fixture
def repository():
    return FakeRepository()


@pytest.fixture
def root(repository):
    folder = Folder(id=uuid4(), parent_id=None, name="home")
    repository.folders[folder.id] = folder
    return folder


@pytest.fixture
def service(repository):
    return FileSystemService(repository)


async def test_create_folder(service, root):
    entry = await service.create(root.id, CreateEntryRequest(name="Docs", type=EntryType.FOLDER))

    assert entry.type == "Folder"
    assert entry.name == "Docs"


async def test_create_file(service, root):
    entry = await service.create(
        root.id, CreateEntryRequest(name="report.txt", type=EntryType.FILE)
    )

    assert entry.type == "File"
    assert entry.name == "report.txt"


async def test_create_in_missing_parent_raises_not_found(service):
    with pytest.raises(EntryNotFoundException):
        await service.create(uuid4(), CreateEntryRequest(name="x", type=EntryType.FILE))


async def test_create_duplicate_name_propagates(service, root):
    await service.create(root.id, CreateEntryRequest(name="Docs", type=EntryType.FOLDER))

    with pytest.raises(DuplicateNameException):
        await service.create(root.id, CreateEntryRequest(name="docs", type=EntryType.FOLDER))


async def test_delete_file(service, repository, root):
    entry = await service.create(
        root.id, CreateEntryRequest(name="report.txt", type=EntryType.FILE)
    )

    await service.delete_file(entry.id)

    assert entry.id not in repository.files


async def test_delete_missing_file_raises_not_found(service):
    with pytest.raises(EntryNotFoundException):
        await service.delete_file(uuid4())


async def test_delete_root_folder_is_forbidden(service, root):
    with pytest.raises(CannotDeleteRootException):
        await service.delete_folder(root.id)


async def test_delete_missing_folder_raises_not_found(service):
    with pytest.raises(EntryNotFoundException):
        await service.delete_folder(uuid4())


async def test_delete_folder_removes_it(service, repository, root):
    entry = await service.create(root.id, CreateEntryRequest(name="Docs", type=EntryType.FOLDER))

    await service.delete_folder(entry.id)

    assert entry.id not in repository.folders


async def test_get_folder_not_found(service):
    with pytest.raises(EntryNotFoundException):
        await service.get_folder(uuid4())


async def test_get_folder_returns_children_and_path(service, root):
    await service.create(root.id, CreateEntryRequest(name="Docs", type=EntryType.FOLDER))
    await service.create(root.id, CreateEntryRequest(name="notes.txt", type=EntryType.FILE))

    contents = await service.get_folder(root.id)

    assert contents.path == "home"
    assert {child.name for child in contents.children} == {"Docs", "notes.txt"}


async def test_get_root(service, root):
    contents = await service.get_root()

    assert contents.id == root.id


async def test_search_blank_query_returns_empty(service, root):
    assert await service.search("   ", None) == []


async def test_search_without_folder_id_matches_prefix_across_all_files(service, root):
    await service.create(root.id, CreateEntryRequest(name="report.txt", type=EntryType.FILE))
    await service.create(root.id, CreateEntryRequest(name="resume.pdf", type=EntryType.FILE))

    results = await service.search("re", None)

    assert {r.name for r in results} == {"report.txt", "resume.pdf"}


async def test_search_with_folder_id_matches_exact_name_only(service, root):
    await service.create(root.id, CreateEntryRequest(name="report.txt", type=EntryType.FILE))

    assert await service.search("report", root.id) == []
    results = await service.search("report.txt", root.id)
    assert [r.name for r in results] == ["report.txt"]


async def test_search_with_missing_folder_id_raises_not_found(service):
    with pytest.raises(EntryNotFoundException):
        await service.search("report.txt", uuid4())
