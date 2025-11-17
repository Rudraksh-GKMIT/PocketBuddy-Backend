from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.constants import ADMIN
from app.schema.schema import TransactionResponse, TransactionCreate, TransactionUpdate
from app.model.transactions import Transaction
from app.model.users import User
from app.utils.auth import get_current_user
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/api/transaction", tags=["Transaction"])


@router.get("/my", response_model=list[TransactionResponse])
def get_my_transactions(
    db: Session = Depends(get_db), current=Depends(get_current_user)
):
    user, roles = current
    transaction = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id, Transaction.deleted_at.is_(None))
        .all()
    )
    return transaction


@router.post("/add", response_model=TransactionCreate)
def add_transaction(
    request: TransactionCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user, roles = current
    new_transaction = Transaction(
        user_id=user.id,
        type=request.type,
        amount=request.amount,
        description=request.description,
    )
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction
