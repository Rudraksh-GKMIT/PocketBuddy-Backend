from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import app.model.users as users , app.schema.schema as schema, app.utils.auth as auth
from app.db.database import get_db
from app.db.seeding import seed_roles
from app.constants import ADMIN

router = APIRouter(prefix="/users",tags= ["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/all")
def get_all_users(db:Session = Depends(get_db)):
    return db.query(users.User).all() 
