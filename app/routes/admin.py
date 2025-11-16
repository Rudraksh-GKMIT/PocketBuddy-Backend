from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.model.users import User
from app.schema.schema import MemberCreate, MemberUpdate
from app.utils.auth import get_current_user, get_password_hash
from app.model.users import UserRole, Role
from uuid import UUID

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/members/family")
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

@router.put("/members/{member_id}")
def edit_member(
    member_id: int,
    request: MemberCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user, roles = current  # UNPACK TUPLE

    # Check admin access
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only admin can edit members")

    # Find member
    member = db.query(User).filter(User.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Update details
    member.name = request.name
    member.email = request.email
    member.password = get_password_hash(request.password)

    db.commit()
    db.refresh(member)

    return {"message": f"Member ID {member_id} updated successfully"}


