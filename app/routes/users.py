from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import app.model.users as users
import app.schema.schema as schema
import app.utils.auth as auth
from app.db.database import get_db
from app.db.seeding import seed_roles
from app.constants import ADMIN

router = APIRouter(prefix="/api/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/all")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(users.User).all()


@router.post("/register")
def register_admin(request: schema.UserCreate, db: Session = Depends(get_db)):
    seed_roles(db)

    if db.query(users.User).filter(users.User.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Creating new family
    new_family = users.Family(name=request.family_name)
    db.add(new_family)
    db.commit()
    db.refresh(new_family)

    # Creating admin user
    hashed_pw = pwd_context.hash(request.password)
    new_user = users.User(
        name=request.name,
        email=request.email,
        password=hashed_pw,
        family_id=new_family.id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Assigning admin role
    admin_role = db.query(users.Role).filter(users.Role.name == ADMIN).first()
    user_role = users.UserRole(user_id=new_user.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()

    return {
        "message": f"Admin {new_user.name} registered successfully",
        "family_id": new_family.id,
    }

