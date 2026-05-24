"""Chapter 只读服务 —— 扫描 novels/{project_id}/chapters/ 下已有章节文件。"""

import re
from pathlib import Path

from schemas.chapter import ChapterContent, ChapterSummary

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
NOVELS_ROOT = REPO_ROOT / "novels"

PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
CHAPTER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

# 支持的章节文件扩展名
CHAPTER_EXTENSIONS = {".md", ".txt"}

# 忽略的文件名
IGNORED_NAMES = {".gitkeep"}

# 提取 markdown 一级标题：行首 "# " 开头到行尾
MD_HEADING_PATTERN = re.compile(r"^#\s+(.+)$")

# 提取文件名中的首个连续数字
FILENAME_DIGITS_PATTERN = re.compile(r"(\d+)")


def list_chapters(project_id: str) -> list[ChapterSummary]:
    """列出指定项目的所有章节摘要。

    如果 chapters 目录不存在，返回空列表。
    """
    _validate_project_id(project_id)

    project_dir = _resolve_project_dir(project_id)
    if not project_dir.is_dir():
        raise FileNotFoundError(
            f"小说项目目录不存在：{project_dir}。"
            f" 请确认项目 ID {project_id} 正确。"
        )

    chapters_dir = project_dir / "chapters"
    if not chapters_dir.is_dir():
        return []

    chapters: list[ChapterSummary] = []
    order = 0

    for entry in sorted(chapters_dir.iterdir()):
        if not entry.is_file():
            continue
        if entry.name in IGNORED_NAMES or entry.name.startswith("."):
            continue
        if entry.suffix.lower() not in CHAPTER_EXTENSIONS:
            continue

        chapter_id = entry.stem
        if not CHAPTER_ID_PATTERN.fullmatch(chapter_id):
            continue

        order += 1
        chapters.append(
            _build_summary(
                project_id=project_id,
                chapter_id=chapter_id,
                filename=entry.name,
                file_path=entry,
                order=order,
            )
        )

    return chapters


def get_chapter(project_id: str, chapter_id: str) -> ChapterContent:
    """获取指定章节的完整内容。

    Raises:
        ValueError: project_id 或 chapter_id 非法。
        FileNotFoundError: 项目目录、chapters 目录或章节文件不存在。
    """
    _validate_project_id(project_id)
    _validate_chapter_id(chapter_id)

    project_dir = _resolve_project_dir(project_id)
    if not project_dir.is_dir():
        raise FileNotFoundError(
            f"小说项目目录不存在：{project_dir}。"
            f" 请确认项目 ID {project_id} 正确。"
        )

    chapters_dir = project_dir / "chapters"
    if not chapters_dir.is_dir():
        raise FileNotFoundError(
            f"chapters 目录不存在：{chapters_dir}。"
            f" 请确认项目 ID {project_id} 正确。"
        )

    # 查找匹配的章节文件
    file_path = None
    for ext in CHAPTER_EXTENSIONS:
        candidate = chapters_dir / f"{chapter_id}{ext}"
        if candidate.is_file():
            file_path = candidate
            break

    if file_path is None:
        raise FileNotFoundError(
            f"章节 {chapter_id} 不存在于 {chapters_dir}。"
            f" 支持的格式：{', '.join(CHAPTER_EXTENSIONS)}。"
        )

    content = file_path.read_text(encoding="utf-8")
    title = _extract_title(content) or chapter_id
    word_count = _count_chars(content)
    order = _extract_order_from_filename(file_path.name)
    if order == 0:
        order = _derive_order_from_directory(chapters_dir, chapter_id)

    return ChapterContent(
        project_id=project_id,
        chapter_id=chapter_id,
        title=title,
        filename=file_path.name,
        order=order,
        word_count=word_count,
        exists=True,
        content=content,
    )


def _validate_project_id(project_id: str) -> None:
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise ValueError("project_id 只能包含字母、数字、短横线和下划线。")

    project_dir = (NOVELS_ROOT / project_id).resolve()
    novels_root = NOVELS_ROOT.resolve()
    if project_dir != novels_root and novels_root not in project_dir.parents:
        raise ValueError("project_id 不能指向 novels 目录之外。")


def _validate_chapter_id(chapter_id: str) -> None:
    if not CHAPTER_ID_PATTERN.fullmatch(chapter_id):
        raise ValueError("chapter_id 只能包含字母、数字、短横线和下划线。")


def _resolve_project_dir(project_id: str) -> Path:
    return NOVELS_ROOT / project_id


def _extract_title(content: str) -> str:
    """从文本第一行提取 markdown 一级标题。"""
    first_line = content.split("\n", 1)[0].strip()
    match = MD_HEADING_PATTERN.match(first_line)
    if match:
        return match.group(1).strip()
    return ""


def _count_chars(content: str) -> int:
    """统计文本字符数（对中文采用简单字符计数）。"""
    # 去除空白字符后计数
    return len(content.replace(" ", "").replace("\n", "").replace("\r", ""))


def _extract_order_from_filename(filename: str) -> int:
    """从文件名中提取第一个连续数字作为 order。"""
    match = FILENAME_DIGITS_PATTERN.search(filename)
    if match:
        return int(match.group(1))
    return 0


def _derive_order_from_directory(chapters_dir: Path, chapter_id: str) -> int:
    """从目录排序中推导章节 order。"""
    order = 0
    for entry in sorted(chapters_dir.iterdir()):
        if not entry.is_file():
            continue
        if entry.name in IGNORED_NAMES or entry.name.startswith("."):
            continue
        if entry.suffix.lower() not in CHAPTER_EXTENSIONS:
            continue
        if not CHAPTER_ID_PATTERN.fullmatch(entry.stem):
            continue
        order += 1
        if entry.stem == chapter_id:
            return order
    return 0


def _build_summary(
    project_id: str,
    chapter_id: str,
    filename: str,
    file_path: Path,
    order: int,
) -> ChapterSummary:
    """从文件构建 ChapterSummary。"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return ChapterSummary(
            project_id=project_id,
            chapter_id=chapter_id,
            title=chapter_id,
            filename=filename,
            order=order,
            word_count=0,
        )

    title = _extract_title(content) or chapter_id
    word_count = _count_chars(content)
    file_order = _extract_order_from_filename(filename)
    if file_order > 0:
        order = file_order

    return ChapterSummary(
        project_id=project_id,
        chapter_id=chapter_id,
        title=title,
        filename=filename,
        order=order,
        word_count=word_count,
    )
