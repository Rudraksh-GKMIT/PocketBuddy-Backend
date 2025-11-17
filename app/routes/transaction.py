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


@router.post("/transactions", response_model=TransactionCreate)
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


@router.put("/transaction/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: UUID,
    request: TransactionUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user, roles = current
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    if tx.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this record")
    if request.type is not None:
        tx.type = request.type
    if request.amount is not None:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        tx.amount = request.amount
    if request.description is not None:
        tx.description = request.description
    db.commit()
    db.refresh(tx)

    return tx


@router.delete("/transaction/{transaction_id}")
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user, roles = current
    transaction_id = UUID(str(transaction_id))
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if tx.deleted_at:
        raise HTTPException(status_code=400, detail="Transaction is already deleted")
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction Not Found")
    if tx.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this record")
    tx.deleted_at = datetime.utcnow()

    db.commit()

    return {"message": "Transaction deleted successfully"}


@router.get("/transactions/family", response_model=list[TransactionResponse])
def get_family_transaction(
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user, roles = current
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only Admin can asscess it.")

    family_users = db.query(User.id).filter(
        User.family_id == user.family_id, User.deleted_at.is_(None)
    )

    transactions = (
        db.query(Transaction).filter(Transaction.user_id.in_(family_users)).all()
    )

    return transactions


@router.get("/type/{tx_type}", response_model=list[TransactionResponse])
def get_transaction_by_type(
    tx_type: str, db: Session = Depends(get_db), current=Depends(get_current_user)
):
    user, roles = current
    type_data = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user.id,
            User.deleted_at.is_(None),
            User.deleted_at.is_(None),
            Transaction.type == tx_type,
        )
        .all()
    )

    return type_data


@router.get("/family/type/{tx_type}", response_model=list[TransactionResponse])
def get_transaction_by_family_type(
    tx_type: str, db: Session = Depends(get_db), current=Depends(get_current_user)
):
    user, roles = current
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only Admin can access it.")
    family_users = db.query(User.id).filter(
        User.family_id == user.family_id, User.deleted_at.is_(None)
    )

    type_data = (
        db.query(Transaction)
        .filter(Transaction.user_id.in_(family_users), Transaction.type == tx_type)
        .all()
    )

    return type_data
