from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from sqlalchemy import func, extract
from app.model.users import User
from app.utils.auth import get_current_user
from app.model.transactions import Transaction
from datetime import datetime
import calendar

router = APIRouter(prefix="/api/transaction/summary", tags=["Transaction Summary"])


@router.get("/me")
def get_my_transaction(
    db: Session = Depends(get_db), current=Depends(get_current_user)
):
    user, roles = current
    total = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == user.id, Transaction.deleted_at.is_(None))
        .scalar()
    )
    return {"user_id": user.id, "total_expense": total}


@router.get("/family")
def get_family_transaction(
    db: Session = Depends(get_db), current=Depends(get_current_user)
):
    user, roles = current
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only admin can view this")

    family_user = db.query(User.id).filter(
        User.family_id == user.family_id, User.deleted_at.is_(None)
    )
    total = (
        db.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id.in_(family_user), Transaction.deleted_at.is_(None))
        .scalar()
    )

    return {"family_id": user.family_id, "total_family_expense": total}


@router.get("/type")
def summary_by_type(db: Session = Depends(get_db), current=Depends(get_current_user)):
    user, roles = current

    results = (
        db.query(Transaction.type, func.sum(Transaction.amount))
        .filter(Transaction.user_id == user.id,Transaction.deleted_at.is_(None))
        .group_by(Transaction.type)
        .all()
    )

    type_summary = [{"type": t, "total": total} for t, total in results]

    return {"user_id": user.id, "type_summary": type_summary}

@router.get("/monthly")
def monthly_transaction(
    mode: str = "all",
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    user, roles = current

    year_expr = extract("year", Transaction.created_at)
    month_expr = extract("month", Transaction.created_at)

    if mode == "current":
        now = datetime.utcnow()
        total = (
            db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == user.id,
                Transaction.deleted_at.is_(None),
                year_expr == now.year,
                month_expr == now.month,
            )
            .scalar()
        )
        return {
            "user_id": user.id,
            "year": now.year,
            "month": now.month,
            "total": total or 0,
        }

    # mode = "all"
    result = (
        db.query(
            year_expr.label("year"),
            month_expr.label("month"),
            func.sum(Transaction.amount).label("total"),
        )
        .filter(Transaction.user_id == user.id, Transaction.deleted_at.is_(None))
        .group_by(year_expr, month_expr)
        .order_by(year_expr, month_expr)
        .all()
    )

    monthly_data = [
        {
            "year": int(row.year),
            "month": calendar.month_name[int(row.month)],
            "total": row.total,
        }
        for row in result
    ]

    return {"user_id": user.id, "monthly_summary": monthly_data}
