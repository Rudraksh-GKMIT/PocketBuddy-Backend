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

