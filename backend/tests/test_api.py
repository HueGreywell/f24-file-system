from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_service
from app.entities.folder import Folder
from app.main import app
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


@pytest.fixture(autouse=True)
def override_service(repository):
    app.dependency_overrides[get_service] = lambda: FileSystemService(repository)
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_get_root(client, root):
    response = await client.get("/folders")

    assert response.status_code == 200
    assert response.json()["id"] == str(root.id)


async def test_create_folder_returns_201(client, root):
    response = await client.post(f"/folders/{root.id}", json={"name": "Docs", "type": "Folder"})

    assert response.status_code == 201
    assert response.json()["name"] == "Docs"


async def test_create_with_blank_name_returns_400(client, root):
    response = await client.post(f"/folders/{root.id}", json={"name": "  ", "type": "File"})

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_NAME"


async def test_create_in_missing_parent_returns_404(client):
    response = await client.post(f"/folders/{uuid4()}", json={"name": "x", "type": "File"})

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_create_duplicate_returns_409(client, root):
    await client.post(f"/folders/{root.id}", json={"name": "Docs", "type": "Folder"})
    response = await client.post(f"/folders/{root.id}", json={"name": "Docs", "type": "Folder"})

    assert response.status_code == 409
    assert response.json()["code"] == "DUPLICATE_NAME"


async def test_delete_root_folder_returns_400(client, root):
    response = await client.delete(f"/folders/{root.id}")

    assert response.status_code == 400
    assert response.json()["code"] == "CANNOT_DELETE_ROOT"


async def test_delete_missing_file_returns_404(client):
    response = await client.delete(f"/files/{uuid4()}")

    assert response.status_code == 404


async def test_invalid_id_returns_404(client):
    response = await client.get("/folders/not-a-uuid")

    assert response.status_code == 404


async def test_search_across_all_files(client, root):
    await client.post(f"/folders/{root.id}", json={"name": "report.txt", "type": "File"})
    await client.post(f"/folders/{root.id}", json={"name": "resume.pdf", "type": "File"})

    response = await client.get("/files/search", params={"query": "re"})

    assert response.status_code == 200
    assert {r["name"] for r in response.json()} == {"report.txt", "resume.pdf"}


async def test_search_exact_in_folder(client, root):
    await client.post(f"/folders/{root.id}", json={"name": "report.txt", "type": "File"})

    response = await client.get(
        "/files/search", params={"query": "report.txt", "folderId": str(root.id)}
    )

    assert response.status_code == 200
    assert [r["name"] for r in response.json()] == ["report.txt"]
