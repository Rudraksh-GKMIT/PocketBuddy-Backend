from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.database import get_db
from app.db.seeding import seed_roles
from app.constants import ADMIN

router = APIRouter(prefix="/api/transaction",tags= ["Transaction"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
