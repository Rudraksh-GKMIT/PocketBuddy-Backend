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


@router.get("/me", response_model=list[TransactionResponse])
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


@router.post("/", response_model=TransactionCreate)
def add_transaction(
    request: TransactionCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    user, roles = current
    new_transaction = Transaction(
        user_id=user.id,
        type=request.type,
        amount=request.amount,
        description=request.description,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: UUID,
    request: TransactionUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):

    if request.amount is not None and request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    user, roles = current
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not tx:
        raise HTTPException(status_code=404, detail="Transaction Not Found")

    if tx.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="Not allowed to update this transaction"
        )

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tx, key, value)

    db.commit()
    db.refresh(tx)

    return tx


@router.delete("/{transaction_id}")
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


@router.get("/family", response_model=list[TransactionResponse])
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
        db.query(Transaction)
        .filter(Transaction.user_id.in_(family_users), Transaction.deleted_at.is_(None))
        .all()
    )

    return transactions


@router.get("/type/{tx_type}", response_model=list[TransactionResponse])
def get_transactions_by_type(
    tx_type: str,
    scope: str = "mine",
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user, roles = current

    if scope == "mine":
        return (
            db.query(Transaction)
            .filter(
                Transaction.user_id == user.id,
                Transaction.type == tx_type,
                Transaction.deleted_at.is_(None),
            )
            .all()
        )

    if scope == "family":
        if "admin" not in roles:
            raise HTTPException(
                status_code=403, detail="Only admin can access family data."
            )

        family_users = db.query(User.id).filter(
            User.family_id == user.family_id, User.deleted_at.is_(None)
        )

        return (
            db.query(Transaction)
            .filter(
                Transaction.user_id.in_(family_users),
                Transaction.type == tx_type,
                Transaction.deleted_at.is_(None),
            )
            .all()
        )

    raise HTTPException(
        status_code=400, detail="Invalid scope. Use 'mine' or 'family'."
    )
