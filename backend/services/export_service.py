from database import SessionLocal
from services.formal_chapter_service import list_chapters


def export_markdown(project_id: int) -> str:
    db = SessionLocal()
    try:
        chapters = list_chapters(db, project_id)
    finally:
        db.close()
    if not chapters:
        return ""
    lines = []
    for ch in chapters:
        lines.append(f"# {ch.title or f'Chapter {ch.chapter_number}'}")
        lines.append("")
        lines.append(ch.content or "")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def export_txt(project_id: int) -> str:
    db = SessionLocal()
    try:
        chapters = list_chapters(db, project_id)
    finally:
        db.close()
    if not chapters:
        return ""
    lines = []
    for ch in chapters:
        lines.append(f"{ch.title or f'Chapter {ch.chapter_number}'}")
        lines.append("")
        lines.append(ch.content or "")
        lines.append("")
        lines.append("=" * 40)
        lines.append("")
    return "\n".join(lines)
