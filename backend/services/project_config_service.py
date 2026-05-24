"""项目配置只读服务 —— 读取 novels/{project_id}/ 下的配置文件。"""

import json
import re
from pathlib import Path

from schemas.project_config import (
    AutomationConfig,
    OutlineConfig,
    StyleProfileConfig,
    SummariesList,
    SummaryFileEntry,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
NOVELS_ROOT = REPO_ROOT / "novels"
PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

# summaries 目录支持的扩展名
SUMMARY_EXTENSIONS = {".md", ".txt", ".json"}
IGNORED_NAMES = {".gitkeep"}


def load_outline(project_id: str) -> OutlineConfig:
    """读取 outline.json。

    Raises:
        ValueError: project_id 非法。
        FileNotFoundError: 文件不存在。
        ValueError: JSON 格式错误。
    """
    return _read_json_config(project_id, "outline.json", OutlineConfig)


def load_style_profile(project_id: str) -> StyleProfileConfig:
    """读取 style-profile.json。"""
    return _read_json_config(project_id, "style-profile.json", StyleProfileConfig)


def load_automation(project_id: str) -> AutomationConfig:
    """读取 automation.json。"""
    return _read_json_config(project_id, "automation.json", AutomationConfig)


def list_summaries(project_id: str) -> SummariesList:
    """列出 summaries 目录下的摘要文件。

    summaries 目录不存在或为空时返回空列表。
    """
    _validate_project_id(project_id)

    project_dir = _resolve_project_dir(project_id)
    if not project_dir.is_dir():
        raise FileNotFoundError(
            f"小说项目目录不存在：{project_dir}。"
            f" 请确认项目 ID {project_id} 正确。"
        )

    summaries_dir = project_dir / "summaries"
    if not summaries_dir.is_dir():
        return SummariesList(project_id=project_id, files=[])

    files: list[SummaryFileEntry] = []
    for entry in sorted(summaries_dir.iterdir()):
        if not entry.is_file():
            continue
        if entry.name in IGNORED_NAMES or entry.name.startswith("."):
            continue
        suffix = entry.suffix.lower()
        if suffix not in SUMMARY_EXTENSIONS:
            continue
        files.append(SummaryFileEntry(
            filename=entry.name,
            file_type=suffix,
        ))

    return SummariesList(project_id=project_id, files=files)


def _validate_project_id(project_id: str) -> None:
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise ValueError("project_id 只能包含字母、数字、短横线和下划线。")

    project_dir = (NOVELS_ROOT / project_id).resolve()
    novels_root = NOVELS_ROOT.resolve()
    if project_dir != novels_root and novels_root not in project_dir.parents:
        raise ValueError("project_id 不能指向 novels 目录之外。")


def _resolve_project_dir(project_id: str) -> Path:
    return NOVELS_ROOT / project_id


def _read_json_config(project_id: str, filename: str, model_cls):
    """通用 JSON 配置文件读取器。"""
    _validate_project_id(project_id)

    project_dir = _resolve_project_dir(project_id)
    if not project_dir.is_dir():
        raise FileNotFoundError(
            f"小说项目目录不存在：{project_dir}。"
            f" 请确认项目 ID {project_id} 正确。"
        )

    file_path = project_dir / filename
    if not file_path.is_file():
        raise FileNotFoundError(
            f"配置文件不存在：{file_path}。"
            f" 请确认项目 ID {project_id} 已创建 {filename}。"
        )

    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"配置文件 JSON 格式不合法：{file_path}。错误：{exc}"
        ) from exc

    if not isinstance(raw, dict):
        raise ValueError(
            f"配置文件内容应为 JSON 对象：{file_path}。"
        )

    try:
        return model_cls.model_validate(raw)
    except Exception as exc:
        raise ValueError(
            f"配置文件数据校验失败：{file_path}。错误：{exc}"
        ) from exc
