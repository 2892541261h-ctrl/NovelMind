from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services import chapter_service, novel_project_service, project_config_service, story_bible_service, writer_context_service  # noqa: E402


@pytest.fixture()
def temp_project(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    temp_root = tmp_path / "repo"
    novels_root = temp_root / "novels"
    project_dir = novels_root / "demo-project"
    chapters_dir = project_dir / "chapters"
    chapters_dir.mkdir(parents=True)

    _patch_module_roots(monkeypatch, temp_root)
    return project_dir


def test_preview_next_chapter_preserves_chapter_prefix(temp_project: Path) -> None:
    _write_chapter(temp_project, "chapter-001.md", "# Chapter 1\n正文")

    preview = writer_context_service.preview_next_chapter("demo-project")

    assert preview.suggested_chapter_id == "chapter-002"
    assert preview.next_order == 2
    assert preview.would_overwrite is False


def test_preview_next_chapter_preserves_ch_prefix(temp_project: Path) -> None:
    _write_chapter(temp_project, "ch1.md", "# Chapter 1\n正文")

    preview = writer_context_service.preview_next_chapter("demo-project")

    assert preview.suggested_chapter_id == "ch2"
    assert preview.next_order == 2
    assert preview.would_overwrite is False


def test_preview_next_chapter_uses_one_when_no_chapters(temp_project: Path) -> None:
    preview = writer_context_service.preview_next_chapter("demo-project")

    assert preview.next_order == 1
    assert preview.suggested_chapter_id == "chapter-001"
    assert preview.would_overwrite is False


def test_preview_next_chapter_uses_maximum_identifiable_number(temp_project: Path) -> None:
    _write_chapter(temp_project, "chapter-001.md", "# Chapter 1\n正文")
    _write_chapter(temp_project, "chapter-010.md", "# Chapter 10\n正文")
    _write_chapter(temp_project, "chapter-003.md", "# Chapter 3\n正文")

    preview = writer_context_service.preview_next_chapter("demo-project")

    assert preview.next_order == 11
    assert preview.suggested_chapter_id == "chapter-011"


def test_preview_next_chapter_marks_existing_target_as_overwrite(temp_project: Path) -> None:
    _write_chapter(temp_project, "chapter-001.md", "# Chapter 1\n正文")
    _write_chapter(temp_project, "chapter-002.md", "# Chapter 2\n正文")

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(
            writer_context_service,
            "list_chapters",
            lambda project_id: [
                _chapter_summary("demo-project", "chapter-001", "chapter-001.md", order=1),
            ],
        )
        _write_chapter(temp_project, "chapter-002.md", "# Chapter 2\n正文")

        preview = writer_context_service.preview_next_chapter("demo-project")

        assert preview.suggested_chapter_id == "chapter-002"
        assert preview.would_overwrite is True
    finally:
        monkeypatch.undo()


def test_preview_prompt_is_local_preview_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        writer_context_service,
        "build_writer_context",
        lambda project_id: _fake_context(),
    )
    monkeypatch.setattr(
        writer_context_service,
        "preview_next_chapter",
        lambda project_id: _fake_preview(),
    )

    preview = writer_context_service.preview_prompt("demo-project")

    assert preview.uses_real_ai is False
    assert preview.provider == "mock"
    assert "MOCK" in preview.raw_prompt
    assert "backend/ai/gateway.py" not in preview.raw_prompt


def _patch_module_roots(monkeypatch: pytest.MonkeyPatch, temp_root: Path) -> None:
    novels_root = temp_root / "novels"
    module_paths = {
        chapter_service: temp_root / "backend" / "services" / "chapter_service.py",
        novel_project_service: temp_root / "backend" / "services" / "novel_project_service.py",
        project_config_service: temp_root / "backend" / "services" / "project_config_service.py",
        story_bible_service: temp_root / "backend" / "services" / "story_bible_service.py",
        writer_context_service: temp_root / "backend" / "services" / "writer_context_service.py",
    }
    for module, fake_file in module_paths.items():
        fake_file.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(module, "__file__", str(fake_file))
    for module in (
        chapter_service,
        novel_project_service,
        project_config_service,
        story_bible_service,
    ):
        monkeypatch.setattr(module, "NOVELS_ROOT", novels_root)


def _write_chapter(project_dir: Path, filename: str, content: str) -> None:
    (project_dir / "chapters" / filename).write_text(content, encoding="utf-8")


def _fake_context():
    class _StoryBible:
        class _Metadata:
            title = "Demo"
            genre = "Fantasy"

        metadata = _Metadata()
        world_rules: list[object] = []

    class _StyleProfile:
        tone = ""
        point_of_view = ""
        pace = ""

    class _Outline:
        chapters: list[dict[str, str]] = []

    return type(
        "FakeContext",
        (),
        {
            "style_profile": _StyleProfile(),
            "story_bible": _StoryBible(),
            "outline": _Outline(),
        },
    )()


def _fake_preview():
    return type(
        "FakePreview",
        (),
        {
            "next_order": 1,
            "suggested_chapter_id": "chapter-001",
            "would_overwrite": False,
        },
    )()


def _chapter_summary(
    project_id: str,
    chapter_id: str,
    filename: str,
    order: int,
):
    from schemas.chapter import ChapterSummary

    return ChapterSummary(
        project_id=project_id,
        chapter_id=chapter_id,
        title=chapter_id,
        filename=filename,
        order=order,
        word_count=0,
    )
