"""Story Bible 读取服务 —— 从本地 JSON 文件加载世界观设定。"""

import json
import re
from pathlib import Path

from pydantic import ValidationError

from schemas.story_bible import StoryBible

# 仓库根目录：backend/services/ -> backend/ -> 仓库根
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
NOVELS_ROOT = REPO_ROOT / "novels"
PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def load_story_bible(project_id: str) -> StoryBible:
    """加载指定项目的 Story Bible。

    Args:
        project_id: 项目 ID，对应 novels/{project_id}/ 目录。

    Returns:
        StoryBible 模型实例。

    Raises:
        FileNotFoundError: story-bible.json 不存在。
        ValueError: JSON 不合法或数据校验失败。
    """
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise ValueError("project_id 只能包含字母、数字、短横线和下划线。")

    project_dir = (NOVELS_ROOT / project_id).resolve()
    novels_root = NOVELS_ROOT.resolve()
    if project_dir != novels_root and novels_root not in project_dir.parents:
        raise ValueError("project_id 不能指向 novels 目录之外。")

    file_path = project_dir / "story-bible.json"

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Story Bible 文件不存在：{file_path}。"
            f" 请确认项目 ID {project_id} 正确且已创建 story-bible.json。"
        )

    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Story Bible 文件 JSON 格式不合法：{file_path}。错误：{exc}"
        ) from exc

    try:
        return StoryBible.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(
            f"Story Bible 数据校验失败：{file_path}。错误：{exc}"
        ) from exc
