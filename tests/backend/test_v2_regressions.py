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

from ai.gateway import _extract_oai_content  # noqa: E402
from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402
from models.reference_profile import ReferenceProfile  # noqa: E402
from services.cr_service import _extract_section as _extract_rewrite_section  # noqa: E402
from services.dashboard_service import get_dashboard_summary  # noqa: E402
from services.reference_novel_service import _extract_section  # noqa: E402
import services.dashboard_service as dashboard_service  # noqa: E402


test_engine = create_engine(
    "sqlite://",
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


def test_reference_profile_sections_do_not_bleed_into_each_other() -> None:
    text = (
        "[worldbuilding]\n世界观结构\n"
        "[characters]\n人物原型\n"
        "[conflict]\n冲突模式\n"
        "[style]\n写作风格\n"
        "[plot]\n情节推进\n"
        "[direction]\n原创方向\n"
    )

    assert _extract_section(text, "worldbuilding") == "世界观结构"
    assert _extract_section(text, "characters") == "人物原型"
    assert _extract_section(text, "style") == "写作风格"
    assert _extract_section(text, "missing") == ""


def test_reference_profile_detail_route_uses_profiles_prefix(client: TestClient) -> None:
    project = client.post("/api/projects", json={"title": "Profile Route Project"}).json()
    novel = client.post(
        "/api/reference-novels",
        json={
            "project_id": project["id"],
            "title": "Reference",
            "author": "",
            "content": "reference text",
            "source_type": "paste",
        },
    ).json()

    db = TestSessionLocal()
    try:
        profile = ReferenceProfile(
            novel_id=novel["id"],
            project_id=project["id"],
            genre="fantasy",
            worldbuilding_pattern="world",
            character_archetypes="hero",
            conflict_patterns="conflict",
            writing_style_profile="style",
            plot_progression_model="plot",
            target_novel_direction="direction",
            confidence="medium",
            status="draft",
        )
        db.add(profile)
        db.commit()
        profile_id = profile.id
    finally:
        db.close()

    resp = client.get(f"/api/reference-novels/profiles/{profile_id}")

    assert resp.status_code == 200
    assert resp.json()["id"] == profile_id
    assert resp.json()["character_archetypes"] == "hero"


def test_dashboard_summary_degrades_when_aggregate_query_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummySession:
        def close(self) -> None:
            pass

    def broken_query(*_args, **_kwargs):
        raise RuntimeError("temporary database error")

    monkeypatch.setattr(dashboard_service, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(dashboard_service, "list_profiles", broken_query)

    summary = get_dashboard_summary(123)

    assert summary["project_id"] == 123
    assert summary["reference_profile_count"] == 0
    assert summary["draft_count"] == 0
    assert summary["usage_call_count"] == 0


def test_oai_content_extractor_supports_list_content() -> None:
    content = _extract_oai_content(
        {
            "message": {
                "content": [
                    {"type": "text", "text": "第一段"},
                    {"type": "text", "text": "第二段"},
                ]
            }
        }
    )

    assert content == "第一段第二段"


def test_rewrite_suggestion_sections_do_not_bleed_into_each_other() -> None:
    text = (
        "[outline]\n先重排冲突，再强化结尾钩子。\n"
        "[notes]\n保留主线目标，删掉重复对白。\n"
        "[text]\n这里是建议改写后的正文片段。\n"
    )

    assert _extract_rewrite_section(text, "outline", "") == "先重排冲突，再强化结尾钩子。"
    assert _extract_rewrite_section(text, "notes", "") == "保留主线目标，删掉重复对白。"
    assert _extract_rewrite_section(text, "text", "") == "这里是建议改写后的正文片段。"
