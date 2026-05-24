from database import SessionLocal
from services.sb_service import list_bibles as list_bibles_svc
from services.cc_service import list_cards
from services.we_service import list_entries
from services.cp_service import get_plan_by_number
from services.cs_service import get_recent_summaries
from services.pt_service import get_open_threads


def get_continuity_snapshot(project_id: int, chapter_number: int) -> dict:
    db = SessionLocal()
    try:
        bibles = list_bibles_svc(db, project_id)
        cards = list_cards(db, project_id)
        entries = list_entries(db, project_id)
        plan = get_plan_by_number(db, project_id, chapter_number)
        recent = get_recent_summaries(db, project_id, limit=3)
        open_threads = get_open_threads(db, project_id)
    finally:
        db.close()

    return {
        "project_id": project_id,
        "chapter_number": chapter_number,
        "has_story_bible": len(bibles) > 0,
        "character_count": len(cards),
        "world_entry_count": len(entries),
        "has_chapter_plan": plan is not None,
        "plan_title": plan.title if plan else "",
        "plan_goal": plan.goal[:200] if plan and plan.goal else "",
        "recent_summary_count": len(recent),
        "recent_unresolved": [s.unresolved_threads[:120] for s in recent if s.unresolved_threads][:3],
        "open_plot_thread_count": len(open_threads),
        "open_thread_titles": [t.title for t in open_threads[:5]],
    }
