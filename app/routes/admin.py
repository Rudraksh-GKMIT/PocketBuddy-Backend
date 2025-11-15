from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.model.users import User
from app.schema.schema import MemberCreate, MemberUpdate
from app.utils.auth import get_current_user, get_password_hash
from app.model.users import UserRole, Role
from uuid import UUID

router = APIRouter(prefix="/api/admin", tags=["admin"])
