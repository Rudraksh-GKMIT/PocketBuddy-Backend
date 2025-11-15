from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from ..config import Config
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.model.users import User
from uuid import UUID

oauth2_scheme = HTTPBearer()

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(Config.ACCESS_TOKEN_EXPIRE_MINUTES)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        jwt_token = token.credentials
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Read user_id as STRING (UUID)
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

        # Validate UUID format
        user_id = UUID(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    # Load the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception

    # Load roles from junction table
    roles = [ur.role.name for ur in user.roles]  # ["admin", "member"]

    return user, roles
