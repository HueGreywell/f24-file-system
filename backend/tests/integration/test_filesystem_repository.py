from uuid import UUID, uuid4

import pytest

from app.entities.file import File
from app.entities.folder import Folder
from app.services.exceptions import DuplicateNameException

# Fixed ids seeded by backend/migrations/0003_seed_data.sql.
ROOT_ID = UUID("00000000-0000-0000-0000-000000000000")
DOCUMENTS_ID = UUID("32d73ba3-84d0-4ff2-ae07-6d12f200b792")
PROJECTS_ID = UUID("b8fad0ed-54a6-474d-a51b-0ed702dfe4b9")


async def test_add_file_duplicate_name_in_same_folder_raises(repository):
    await repository.add_file(File(id=uuid4(), parent_id=ROOT_ID, name="Unique.txt"))

    with pytest.raises(DuplicateNameException):
        await repository.add_file(File(id=uuid4(), parent_id=ROOT_ID, name="unique.txt"))


async def test_add_folder_name_conflicting_with_sibling_file_raises(repository):
    await repository.add_file(File(id=uuid4(), parent_id=ROOT_ID, name="Shared"))

    with pytest.raises(DuplicateNameException):
        await repository.add_folder(Folder(id=uuid4(), parent_id=ROOT_ID, name="shared"))


async def test_cascade_delete_removes_children(repository, connection):
    folder_id = uuid4()
    file_id = uuid4()
    await repository.add_folder(Folder(id=folder_id, parent_id=ROOT_ID, name="Temp"))
    await repository.add_file(File(id=file_id, parent_id=folder_id, name="child.txt"))

    await repository.delete_folder(folder_id)

    assert await repository.get_folder(folder_id) is None
    row = await connection.fetchrow("SELECT 1 FROM files WHERE id = $1", file_id)
    assert row is None


async def test_get_folder_path_builds_full_path(repository):
    assert await repository.get_folder_path(PROJECTS_ID) == "home/Documents/Projects"


async def test_search_all_files_matches_prefix_case_insensitively(repository):
    results = await repository.search_all_files("re", 10)

    assert [r.name for r in results] == ["Resume.pdf"]


async def test_search_all_files_respects_limit(repository):
    for i in range(15):
        await repository.add_file(
            File(id=uuid4(), parent_id=ROOT_ID, name=f"bulk-{i:02d}.txt")
        )

    results = await repository.search_all_files("bulk-", 10)

    assert len(results) == 10


async def test_search_exact_in_folder_requires_full_name_match(repository):
    assert await repository.search_exact_in_folder("resume", DOCUMENTS_ID, 10) == []

    results = await repository.search_exact_in_folder("resume.pdf", DOCUMENTS_ID, 10)
    assert [r.name for r in results] == ["Resume.pdf"]


async def test_search_exact_in_folder_is_scoped_to_that_folder(repository):
    # CoverLetter.docx lives in Documents, not in its Projects subfolder.
    results = await repository.search_exact_in_folder(
        "coverletter.docx", PROJECTS_ID, 10
    )
    assert results == []
