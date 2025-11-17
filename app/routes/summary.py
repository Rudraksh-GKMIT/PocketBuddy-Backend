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

