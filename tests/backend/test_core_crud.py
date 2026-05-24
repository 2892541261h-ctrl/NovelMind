"""核心 CRUD 测试 —— FastAPI TestClient + 内存 SQLite，不依赖真实 AI。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402

# 使用内存 SQLite 避免污染正式数据库
TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


class TestHealthAndAI:
    """验证已有路由仍可用。"""

    def test_health_available(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_ai_test_available(self, client: TestClient) -> None:
        resp = client.get("/api/ai/test")
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "mock"
        assert data["error"] is None


class TestProjectCRUD:
    """projects 资源 CRUD 测试。"""

    def test_create_project(self, client: TestClient) -> None:
        resp = client.post("/api/projects", json={
            "title": "Test Novel",
            "genre": "Fantasy",
            "description": "A test novel",
            "target_word_count": 100000,
            "status": "planning",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test Novel"
        assert data["genre"] == "Fantasy"
        assert data["id"] >= 1

    def test_list_projects(self, client: TestClient) -> None:
        client.post("/api/projects", json={"title": "A"})
        client.post("/api/projects", json={"title": "B"})
        resp = client.get("/api/projects")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_project(self, client: TestClient) -> None:
        created = client.post("/api/projects", json={"title": "Target"}).json()
        resp = client.get(f"/api/projects/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Target"

    def test_update_project(self, client: TestClient) -> None:
        created = client.post("/api/projects", json={"title": "Old"}).json()
        resp = client.put(f"/api/projects/{created['id']}", json={"title": "New"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New"

    def test_delete_project(self, client: TestClient) -> None:
        created = client.post("/api/projects", json={"title": "DeleteMe"}).json()
        resp = client.delete(f"/api/projects/{created['id']}")
        assert resp.status_code == 204
        resp2 = client.get(f"/api/projects/{created['id']}")
        assert resp2.status_code == 404

    def test_get_nonexistent_project_returns_404(self, client: TestClient) -> None:
        resp = client.get("/api/projects/99999")
        assert resp.status_code == 404


class TestCharacterCRUD:
    """characters 资源 CRUD 测试。"""

    def test_create_character(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        resp = client.post(f"/api/projects/{proj['id']}/characters", json={
            "project_id": proj["id"],
            "name": "Hero",
            "role_type": "主角",
            "personality": "Brave and kind",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Hero"
        assert data["project_id"] == proj["id"]

    def test_list_characters_by_project(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        client.post(f"/api/projects/{proj['id']}/characters", json={
            "project_id": proj["id"], "name": "A",
        })
        client.post(f"/api/projects/{proj['id']}/characters", json={
            "project_id": proj["id"], "name": "B",
        })
        resp = client.get(f"/api/projects/{proj['id']}/characters")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_character(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        char = client.post(f"/api/projects/{proj['id']}/characters", json={
            "project_id": proj["id"], "name": "Target",
        }).json()
        resp = client.get(f"/api/characters/{char['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Target"


class TestChapterCRUD:
    """chapters 资源 CRUD 测试。"""

    def test_create_chapter(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        resp = client.post(f"/api/projects/{proj['id']}/chapters", json={
            "project_id": proj["id"],
            "chapter_number": 1,
            "title": "Chapter One",
            "content": "It was a dark and stormy night.",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Chapter One"
        assert data["chapter_number"] == 1

    def test_list_chapters_by_project(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        client.post(f"/api/projects/{proj['id']}/chapters", json={
            "project_id": proj["id"], "chapter_number": 1, "title": "Ch1",
        })
        client.post(f"/api/projects/{proj['id']}/chapters", json={
            "project_id": proj["id"], "chapter_number": 2, "title": "Ch2",
        })
        resp = client.get(f"/api/projects/{proj['id']}/chapters")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_chapter(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        ch = client.post(f"/api/projects/{proj['id']}/chapters", json={
            "project_id": proj["id"], "chapter_number": 1, "title": "Target",
        }).json()
        resp = client.get(f"/api/chapters/{ch['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Target"

    def test_delete_chapter(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        ch = client.post(f"/api/projects/{proj['id']}/chapters", json={
            "project_id": proj["id"], "chapter_number": 1, "title": "DeleteMe",
        }).json()
        resp = client.delete(f"/api/chapters/{ch['id']}")
        assert resp.status_code == 204
        resp2 = client.get(f"/api/chapters/{ch['id']}")
        assert resp2.status_code == 404


class TestOutlineCRUD:
    """outlines 资源 CRUD 测试。"""

    def test_create_outline(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        resp = client.post(f"/api/projects/{proj['id']}/outlines", json={
            "project_id": proj["id"],
            "title": "Main Outline",
            "one_sentence_pitch": "A hero's journey.",
        })
        assert resp.status_code == 201
        assert resp.json()["title"] == "Main Outline"

    def test_list_outlines(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        client.post(f"/api/projects/{proj['id']}/outlines", json={
            "project_id": proj["id"], "title": "A",
        })
        client.post(f"/api/projects/{proj['id']}/outlines", json={
            "project_id": proj["id"], "title": "B",
        })
        resp = client.get(f"/api/projects/{proj['id']}/outlines")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestWorldSettingCRUD:
    """world_settings 资源 CRUD 测试。"""

    def test_create_world_setting(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        resp = client.post(f"/api/projects/{proj['id']}/world-settings", json={
            "project_id": proj["id"],
            "name": "Magic System",
            "category": "power_system",
            "content": "Magic comes from the earth.",
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "Magic System"


class TestForeshadowingCRUD:
    """foreshadowing 资源 CRUD 测试。"""

    def test_create_foreshadowing(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        resp = client.post(f"/api/projects/{proj['id']}/foreshadowing", json={
            "project_id": proj["id"],
            "title": "Mysterious Stranger",
            "description": "A stranger appears in chapter 2.",
            "planted_chapter": 2,
            "expected_reveal_chapter": 15,
        })
        assert resp.status_code == 201
        assert resp.json()["importance"] == "medium"


class TestWritingStyleCRUD:
    """writing_styles 资源 CRUD 测试。"""

    def test_create_writing_style(self, client: TestClient) -> None:
        proj = client.post("/api/projects", json={"title": "P"}).json()
        resp = client.post(f"/api/projects/{proj['id']}/writing-styles", json={
            "project_id": proj["id"],
            "name": "Main Style",
            "sentence_style": "Short and punchy.",
            "dialogue_style": "Natural and flowing.",
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "Main Style"
