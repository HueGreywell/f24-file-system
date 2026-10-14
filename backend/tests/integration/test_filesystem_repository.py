from uuid import UUID, uuid4

import pytest

from app.entities.exceptions import DuplicateNameException, EntryNotFoundException
from app.entities.file import File
from app.entities.folder import Folder

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


async def test_add_file_with_missing_parent_raises_not_found(repository):
    with pytest.raises(EntryNotFoundException):
        await repository.add_file(File(id=uuid4(), parent_id=uuid4(), name="orphan.txt"))


async def test_add_folder_with_missing_parent_raises_not_found(repository):
    with pytest.raises(EntryNotFoundException):
        await repository.add_folder(Folder(id=uuid4(), parent_id=uuid4(), name="Orphan"))


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

    assert [r.file.name for r in results] == ["Resume.pdf"]


async def test_search_all_files_respects_limit(repository):
    for i in range(15):
        await repository.add_file(
            File(id=uuid4(), parent_id=ROOT_ID, name=f"bulk-{i:02d}.txt")
        )

    results = await repository.search_all_files("bulk-", 10)

    assert len(results) == 10


async def test_search_all_files_treats_underscore_as_literal(repository):
    await repository.add_file(File(id=uuid4(), parent_id=ROOT_ID, name="my_file.txt"))
    await repository.add_file(File(id=uuid4(), parent_id=ROOT_ID, name="myXfile.txt"))

    results = await repository.search_all_files("my_f", 10)

    assert [r.file.name for r in results] == ["my_file.txt"]


async def test_search_exact_in_folder_requires_full_name_match(repository):
    assert await repository.search_exact_in_folder("resume", DOCUMENTS_ID, 10) == []

    results = await repository.search_exact_in_folder("resume.pdf", DOCUMENTS_ID, 10)
    assert [r.file.name for r in results] == ["Resume.pdf"]


async def test_search_exact_in_folder_is_scoped_to_that_folder(repository):
    # CoverLetter.docx lives in Documents, not in its Projects subfolder.
    results = await repository.search_exact_in_folder(
        "coverletter.docx", PROJECTS_ID, 10
    )
    assert results == []


async def test_search_result_path_is_truncated_like_folder_path(repository):
    deep_folder_id = uuid4()
    await repository.add_folder(
        Folder(id=uuid4(), parent_id=ROOT_ID, name="a" * 200)
    )
    first_level_id = [
        f.id for f in (await repository.get_children(ROOT_ID)) if f.name == "a" * 200
    ][0]
    await repository.add_folder(
        Folder(id=deep_folder_id, parent_id=first_level_id, name="b" * 200)
    )
    await repository.add_file(
        File(id=uuid4(), parent_id=deep_folder_id, name="f.txt")
    )

    folder_path = await repository.get_folder_path(deep_folder_id)
    results = await repository.search_exact_in_folder("f.txt", deep_folder_id, 10)

    assert len(folder_path) == 255
    assert folder_path.startswith("...")
    assert len(results[0].path) == 255
    assert results[0].path.startswith("...")
    assert results[0].path.endswith("f.txt")
