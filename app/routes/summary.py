from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from sqlalchemy import func, extract
from app.model.users import User
from app.utils.auth import get_current_user
from app.model.transactions import Transaction
from datetime import datetime
from app.utils.summary import get_summary

router = APIRouter(prefix="/api/summary", tags=["Transaction Summary"])
@router.get("/dashboard")
def user_dashboard(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    user, _ = current

    user_ids = [user.id]  # wrap in list for shared helper

    total, month_total, category_summary, top_categories = get_summary(db, user_ids)

    return {
        "user_id": user.id,
        "total_spent": total,
        "this_month": month_total,
        "type_summary": category_summary,
        "top_categories": top_categories,
    }

@router.get("/family-dashboard")
def family_dashboard(
    db: Session = Depends(get_db),
    current=Depends(get_current_user)
):
    user, roles = current

    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only admin can view this")

    family_user_ids = db.query(User.id).filter(
        User.family_id == user.family_id,
        User.deleted_at.is_(None)
    )

    total, month_total, category_summary, top_categories = get_summary(db, family_user_ids)

    return {
        "family_id": user.family_id,
        "total_family_spent": total,
        "this_month_family": month_total,
        "type_summary": category_summary,
        "top_categories": top_categories,
    }
