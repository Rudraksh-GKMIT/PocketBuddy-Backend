from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import app.model.users as users
import app.schema.schema as schema
import app.utils.auth as auth
from app.db.database import get_db
from app.db.seeding import seed_roles
from app.constants import ADMIN
from app.utils.auth import verify_password

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

@router.post("/login", response_model=schema.Token)
def login_user(request: schema.UserLogin, db: Session = Depends(get_db)):
    user = db.query(users.User).filter(users.User.email == request.email).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_role = (
        db.query(users.Role.name)
        .join(users.UserRole, users.Role.id == users.UserRole.role_id)
        .filter(users.UserRole.user_id == user.id)
        .first()
    )

    token_data = {
        "user_id": str(user.id),
        "family_id": str(user.family_id),
        "role": user_role.name if user_role else "unknown",
    }

    access_token = auth.create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}