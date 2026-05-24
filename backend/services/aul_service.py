from sqlalchemy.orm import Session
from sqlalchemy import func
from models.ai_usage_log import AIUsageLog
from schemas.ai_usage_log_schema import UsageSummary


def list_logs(db: Session, limit: int = 50) -> list[AIUsageLog]:
    return db.query(AIUsageLog).order_by(AIUsageLog.created_at.desc()).limit(limit).all()


def get_log(db: Session, log_id: int) -> AIUsageLog | None:
    return db.query(AIUsageLog).filter(AIUsageLog.id == log_id).first()


def create_log(db: Session, **kwargs) -> AIUsageLog:
    log = AIUsageLog(**kwargs); db.add(log); db.commit(); db.refresh(log); return log


def get_summary(db: Session) -> UsageSummary:
    logs = db.query(AIUsageLog).all()
    total_tokens = sum(l.total_tokens or 0 for l in logs)
    total_cost = sum(l.estimated_cost or 0 for l in logs)

    by_feature: dict[str, dict] = {}
    by_model: dict[str, dict] = {}
    for l in logs:
        f = l.feature_name or "other"
        if f not in by_feature: by_feature[f] = {"feature": f, "calls": 0, "tokens": 0, "cost": 0.0}
        by_feature[f]["calls"] += 1; by_feature[f]["tokens"] += (l.total_tokens or 0); by_feature[f]["cost"] += (l.estimated_cost or 0)
        m = l.model or "unknown"
        if m not in by_model: by_model[m] = {"model": m, "calls": 0, "tokens": 0, "cost": 0.0}
        by_model[m]["calls"] += 1; by_model[m]["tokens"] += (l.total_tokens or 0); by_model[m]["cost"] += (l.estimated_cost or 0)

    return UsageSummary(
        total_calls=len(logs), total_success=sum(1 for l in logs if l.status == "success"),
        total_error=sum(1 for l in logs if l.status == "error"), total_tokens=total_tokens,
        total_estimated_cost=round(total_cost, 6),
        currency="USD",
        by_feature=list(by_feature.values()), by_model=list(by_model.values()),
    )
