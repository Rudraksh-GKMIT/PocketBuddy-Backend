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
