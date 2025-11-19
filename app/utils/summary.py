from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
from app.model.transactions import Transaction

def get_summary(db: Session, user_ids):
    """Reusable summary generator for any list of user IDs."""
    
    # --- Total spent ---
    total_spent = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id.in_(user_ids), Transaction.deleted_at.is_(None))
        .scalar()
    ) or 0

    # --- This Month ---
    now = datetime.utcnow()
    year_expr = extract("year", Transaction.created_at)
    month_expr = extract("month", Transaction.created_at)

    this_month_total = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id.in_(user_ids),
            Transaction.deleted_at.is_(None),
            year_expr == now.year,
            month_expr == now.month,
        )
        .scalar()
    ) or 0

    # --- Category summary ---
    raw_categories = (
        db.query(Transaction.type, func.sum(Transaction.amount))
        .filter(Transaction.user_id.in_(user_ids), Transaction.deleted_at.is_(None))
        .group_by(Transaction.type)
        .all()
    )

    type_summary = [
        {"type": t, "total": round(float(total), 2)}
        for t, total in raw_categories
    ]


    # --- Multiple top categories ---
    if type_summary:
        max_total = max(item["total"] for item in type_summary)
        top_categories = [i["type"] for i in type_summary if i["total"] == max_total]
    else:
        top_categories = []

    return round(float(total_spent),2), round(float(this_month_total),2), type_summary, top_categories
