from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.constants import ADMIN
from app.schema.schema import TransactionResponse, TransactionCreate, TransactionUpdate
from app.model.transactions import Transaction
from app.model.users import User
from app.utils.auth import get_current_user
from uuid import UUID

router = APIRouter(prefix="/api/transaction", tags=["Transaction"])


@router.get("/my", response_model=list[TransactionResponse])
def get_my_transactions(
    db: Session = Depends(get_db), current=Depends(get_current_user)
):
    user, roles = current
    transaction = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    return transaction

