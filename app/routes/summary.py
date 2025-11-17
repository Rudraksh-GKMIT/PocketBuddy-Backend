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
        .filter(Transaction.user_id == user.id, User.deleted_at.is_(None))
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
        .filter(Transaction.user_id.in_(family_user))
        .scalar()
    )

    return {"family_id": user.family_id, "total_family_expense": total}

