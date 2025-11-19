from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.model.users import User
from app.schema.schema import MemberCreate, MemberUpdate
from app.utils.auth import get_current_user, get_password_hash
from app.model.users import UserRole, Role
from uuid import UUID
from app.constants import MEMBER
from datetime import datetime
from app.model.transactions import Transaction

router = APIRouter(prefix="/api/admin", tags=["admin"])


# To see the members of your family
@router.get("/members/family")
def get_my_member(db: Session = Depends(get_db), current=Depends(get_current_user)):
    user, roles = current

    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only admin can view members")

    result = (
        db.query(User)
        .filter(
            User.family_id == user.family_id,
            User.id != user.id,
            User.deleted_at.is_(None),
        )
        .all()
    )
    return result


# To add member in your family
@router.post("/members")
def add_member(
    request: MemberCreate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user, roles = current

    # Check admin permission
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only admin can add members")

    # Get the admin's family_id
    family_id = user.family_id

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists can't you it")

    # Create new user
    new_user = User(
        name=request.name,
        email=request.email,
        password=get_password_hash(request.password),
        family_id=family_id,
    )
    db.add(new_user)
    db.flush()

    # Assign member role
    member_role = db.query(Role).filter(Role.name == MEMBER).first()
    user_role = UserRole(user_id=new_user.id, role_id=member_role.id)
    db.add(user_role)
    db.commit()
    db.refresh(new_user)

    return {"message": "Member added successfully"}


# Edit existing Member data
@router.put("/members/{member_id}")
def edit_member(
    member_id: UUID,
    request: MemberUpdate,
    db: Session = Depends(get_db),
    current=Depends(get_current_user),
):
    user, roles = current

    # Check admin access
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only admin can edit members")

    # Find member
    member = db.query(User).filter(User.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Update details
    if request.name is not None:
        member.name = request.name

    if request.email is not None:
        member.email = request.email

    existing_user = db.query(User).filter(User.email == request.email,User.id != member_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Member already exists")

    if request.password is not None:
        member.password = get_password_hash(request.password)

    db.commit()
    db.refresh(member)

    return {"message": "Member updated successfully"}


@router.delete("/members/{member_id}")
def delete_member(
    member_id: UUID, db: Session = Depends(get_db), current=Depends(get_current_user)
):
    user, roles = current

    # Check for role
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Only admin can delete members")

    # Finding the member
    member = db.query(User).filter(User.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Admin can't delete themselves
    if user.id == member_id:
        raise HTTPException(400, "Admin cannot delete themselves")

    if member.deleted_at:
        raise HTTPException(status_code=400, detail="Member is already deleted")

    db.query(Transaction).filter(
        Transaction.user_id == member_id,
        Transaction.deleted_at.is_(None)
    ).update(
        {Transaction.deleted_at: datetime.utcnow()},
        synchronize_session=False,
    )
    member.deleted_at = datetime.utcnow()

    db.commit()

    return {"message": "Member deleted successfully"}
