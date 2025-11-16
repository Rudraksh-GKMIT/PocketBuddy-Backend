from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.model.users import User
from app.schema.schema import MemberCreate, MemberUpdate
from app.utils.auth import get_current_user, get_password_hash
from app.model.users import UserRole, Role
from uuid import UUID

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/my")
def get_my_member(db: Session = Depends(get_db), current=Depends(get_current_user)):
    user, roles = current

    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only admin can view members")

    result = (
        db.query(User)
        .filter(User.family_id == user.family_id, User.id != user.id)
        .all()
    )
    return result
