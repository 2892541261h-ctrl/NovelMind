"""Project dashboard service - aggregates V1 project status."""

from database import SessionLocal
from services.reference_novel_service import list_profiles
from services.sb_service import list_bibles as list_bibles_svc
from services.cc_service import list_cards
from services.we_service import list_entries
from services.cp_service import list_plans
from services.chapter_draft_service import list_drafts
from services.formal_chapter_service import list_chapters as list_formal
from services.cs_service import list_summaries
from services.pt_service import get_open_threads
from services.cr_service import list_reviews
from services.aul_service import get_summary as get_usage_summary


def get_dashboard_summary(project_id: int) -> dict:
    db = SessionLocal()
    try:
        profiles = list_profiles(db, project_id)
        bibles = list_bibles_svc(db, project_id)
        cards = list_cards(db, project_id)
        entries = list_entries(db, project_id)
        plans = list_plans(db, project_id)
        drafts = list_drafts(db, project_id)
        formal = list_formal(db, project_id)
        summaries = list_summaries(db, project_id)
        open_threads = get_open_threads(db, project_id)
        reviews = list_reviews(db, project_id)
    finally:
        db.close()

    try:
        usage = get_usage_summary(db if 'db' in dir() else SessionLocal())
    except Exception:
        usage = None

    return {
        "project_id": project_id,
        "reference_profile_count": len(profiles),
        "has_reference_profile": len(profiles) > 0,
        "story_bible_count": len(bibles),
        "has_story_bible": len(bibles) > 0,
        "character_card_count": len(cards),
        "world_entry_count": len(entries),
        "chapter_plan_count": len(plans),
        "draft_count": len(drafts),
        "formal_chapter_count": len(formal),
        "next_chapter_number": max([c.chapter_number for c in formal], default=0) + 1,
        "chapter_summary_count": len(summaries),
        "open_plot_thread_count": len(open_threads),
        "review_count": len(reviews),
        "usage_call_count": usage.total_calls if usage else 0,
        "estimated_total_cost": usage.total_estimated_cost if usage else 0.0,
    }
