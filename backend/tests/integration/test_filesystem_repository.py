from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from app.entities.exceptions import DuplicateNameException, EntryNotFoundException
from app.entities.file import File
from app.entities.folder import Folder

ROOT_ID = UUID("00000000-0000-0000-0000-000000000000")


@dataclass
class Tree:
    documents_name: str
    documents_id: UUID
    projects_id: UUID
    resume_id: UUID
    cover_letter_id: UUID


@pytest.fixture
async def tree(repository) -> Tree:
    documents_name = f"Documents-{uuid4().hex[:8]}"
    documents_id = uuid4()
    projects_id = uuid4()
    resume_id = uuid4()
    cover_letter_id = uuid4()

    await repository.add_folder(Folder(id=documents_id, parent_id=ROOT_ID, name=documents_name))
    await repository.add_folder(Folder(id=projects_id, parent_id=documents_id, name="Projects"))
    await repository.add_file(File(id=resume_id, parent_id=documents_id, name="Resume.pdf"))
    await repository.add_file(
        File(id=cover_letter_id, parent_id=documents_id, name="CoverLetter.docx")
    )

    return Tree(
        documents_name=documents_name,
        documents_id=documents_id,
        projects_id=projects_id,
        resume_id=resume_id,
        cover_letter_id=cover_letter_id,
    )


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


async def test_get_folder_path_builds_full_path(repository, tree):
    expected = f"home/{tree.documents_name}/Projects"
    assert await repository.get_folder_path(tree.projects_id) == expected


async def test_search_all_files_matches_prefix_case_insensitively(repository):
    unique_prefix = uuid4().hex
    name = f"{unique_prefix.upper()}-report.txt"
    await repository.add_file(File(id=uuid4(), parent_id=ROOT_ID, name=name))

    results = await repository.search_all_files(unique_prefix.lower(), 10)

    assert [r.file.name for r in results] == [name]


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


async def test_search_prefix_in_folder_matches_case_insensitively(repository, tree):
    assert await repository.search_prefix_in_folder("vacation", tree.documents_id, 10) == []

    results = await repository.search_prefix_in_folder("resume", tree.documents_id, 10)
    assert [r.file.name for r in results] == ["Resume.pdf"]


async def test_search_prefix_in_folder_is_scoped_to_that_folder(repository, tree):
    results = await repository.search_prefix_in_folder(
        "coverletter", tree.projects_id, 10
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
    results = await repository.search_prefix_in_folder("f.txt", deep_folder_id, 10)

    assert len(folder_path) == 255
    assert folder_path.startswith("...")
    assert len(results[0].path) == 255
    assert results[0].path.startswith("...")
    assert results[0].path.endswith("f.txt")
