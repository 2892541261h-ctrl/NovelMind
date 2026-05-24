"""Chapter Review service - AI-powered quality checks via backend/ai/gateway.py."""

import json

from sqlalchemy.orm import Session

from ai.gateway import generate_text
from ai.types import AIMessage, AIRequest
from models.chapter_review import ChapterReview


def list_reviews(db: Session, project_id: int) -> list[ChapterReview]:
    return db.query(ChapterReview).filter(ChapterReview.project_id == project_id).order_by(ChapterReview.chapter_number.desc()).all()


def get_review(db: Session, review_id: int) -> ChapterReview | None:
    return db.query(ChapterReview).filter(ChapterReview.id == review_id).first()


def get_latest_for_chapter(db: Session, project_id: int, chapter_number: int) -> ChapterReview | None:
    return db.query(ChapterReview).filter(
        ChapterReview.project_id == project_id, ChapterReview.chapter_number == chapter_number
    ).order_by(ChapterReview.created_at.desc()).first()


def delete_review(db: Session, review_id: int) -> bool:
    r = db.query(ChapterReview).filter(ChapterReview.id == review_id).first()
    if not r: return False
    db.delete(r); db.commit(); return True


async def review_content(db: Session, project_id: int, chapter_number: int, content: str,
                         draft_id: int | None = None, formal_chapter_id: int | None = None,
                         writing_goal: str = "", plan_goal: str = "",
                         ) -> ChapterReview:
    prompt = _review_prompt(project_id, chapter_number, content, writing_goal, plan_goal)
    ai_req = AIRequest(task="chapter_review", messages=[
        AIMessage(role="system", content=_REVIEW_SYSTEM),
        AIMessage(role="user", content=prompt),
    ])
    resp = await generate_text(ai_req)
    if resp.error:
        raise ValueError(f"AI review generation failed: {resp.error}")
    scores = _parse_scores(resp.content)

    review = ChapterReview(
        project_id=project_id, draft_id=draft_id, formal_chapter_id=formal_chapter_id,
        chapter_number=chapter_number, issues=scores.get("issues", ""), suggestions=scores.get("suggestions", ""),
        overall_score=scores.get("overall", 5.0), continuity_score=scores.get("continuity", 5.0),
        character_consistency_score=scores.get("character", 5.0), pacing_score=scores.get("pacing", 5.0),
        style_score=scores.get("style", 5.0), originality_score=scores.get("originality", 5.0),
        goal_alignment_score=scores.get("goal_alignment", 5.0),
    )
    db.add(review); db.commit(); db.refresh(review); return review


async def suggest_rewrite(db: Session, content: str, issues: str, title: str) -> dict:
    prompt = _rewrite_prompt(content, issues, title)
    ai_req = AIRequest(task="suggest_rewrite", messages=[
        AIMessage(role="system", content="你是章节改写建议专家。不要直接覆盖原文，只提供建议文本供用户参考。"),
        AIMessage(role="user", content=prompt),
    ])
    resp = await generate_text(ai_req)
    if resp.error:
        raise ValueError(f"AI rewrite suggestion failed: {resp.error}")
    content = resp.content or ""
    return {
        "suggested_title": title,
        "suggested_outline": _extract_section(content, "outline", ""),
        "suggested_revision_notes": _extract_section(content, "notes", ""),
        "suggested_text": _extract_section(content, "text", content[:500]),
    }


_REVIEW_SYSTEM = (
    "你是长篇小说章节质量检查专家。你的任务是评估章节质量并给出具体建议。"
    "不要输出解释过程，直接输出 JSON 格式结果。"
)


def _review_prompt(project_id: int, chapter_number: int, content: str, goal: str, plan_goal: str) -> str:
    return (
        f"请评估以下章节的质量。输出 JSON，包含以下字段（每项 1-10 分）：\n"
        f"overall, continuity, character, pacing, style, originality, goal_alignment\n"
        f"issues: 发现的具体问题列表（中文）\n"
        f"suggestions: 修改建议（中文）\n\n"
        f"检查维度：\n"
        f"1. 是否保持人物性格一致\n"
        f"2. 是否有明显重复上一章内容\n"
        f"3. 是否有节奏问题\n"
        f"4. 是否有突兀转折\n"
        f"5. 是否有原创性风险（复制参考小说角色/地名/组织/剧情）\n"
        f"6. 是否完成写作目标\n"
        f"7. 叙事连贯性\n\n"
        f"{'写作目标: ' + goal if goal else ''}\n"
        f"{'章节计划目标: ' + plan_goal if plan_goal else ''}\n\n"
        f"项目 {project_id} 第 {chapter_number} 章：\n{content[:3000]}"
    )


def _rewrite_prompt(content: str, issues: str, title: str) -> str:
    return (
        f"根据以下问题和原文，提供改写建议。输出格式：\n"
        f"[outline] 建议的改写大纲\n"
        f"[notes] 改写要点\n"
        f"[text] 建议改写后的文本\n\n"
        f"原标题: {title}\n"
        f"发现问题: {issues}\n\n"
        f"原文:\n{content[:2500]}"
    )


def _parse_scores(text: str) -> dict:
    try:
        if "{" in text:
            return json.loads(text[text.index("{"):text.rindex("}")+1])
    except (json.JSONDecodeError, ValueError):
        pass
    # fallback: mock scores
    return {
        "overall": 7.0, "continuity": 7.0, "character": 7.0, "pacing": 7.0,
        "style": 7.0, "originality": 8.0, "goal_alignment": 7.0,
        "issues": "AI Gateway returned non-JSON. Scores are default mock values.",
        "suggestions": "Check AI Gateway configuration.",
    }


def _extract_section(text: str, tag: str, default: str) -> str:
    if not text:
        return default
    try:
        start = text.lower().index(f"[{tag}]")
        rest = text[start + len(tag) + 2:]
        for end_tag in ["[outline]", "[notes]", "[text]", "[issues]", "[suggestions]"]:
            end_pos = rest.lower().find(f"[{end_tag}]")
            if end_pos > 0: return rest[:end_pos].strip()
        return rest.strip()[:500]
    except ValueError:
        return default
