from pydantic import BaseModel, EmailStr , field_validator
from uuid import UUID
from datetime import datetime

VALID_TYPES = {"food", "travel", "shopping", "entertainment", "bills", "other"}


class Rolebase(BaseModel):
    name: str


class RoleCreate(Rolebase):
    pass


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    family_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class MemberResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class MemberUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class TransactionCreate(BaseModel):
    type: str
    amount: float
    description: str 
    
    @field_validator("type")
    def normalize_and_validate_type(cls, v):
        v = v.lower()
        if v not in VALID_TYPES:
            raise ValueError(f"Invalid transaction type '{v}'. Must be one of: {', '.join(VALID_TYPES)}")
        return v


class TransactionUpdate(BaseModel):
    type: str | None = None
    amount: float | None = None
    description: str | None = None
    
    @field_validator("type")
    def normalize_and_validate_type(cls, v):
        if v is None:
            return v
        v = v.lower()
        if v not in VALID_TYPES:
            raise ValueError(f"Invalid transaction type '{v}'. Must be one of: {', '.join(VALID_TYPES)}")
        return v


class TransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    amount: float
    description: str  | None = None
    created_at : datetime |  None = None
    class Config:
        from_attributes = True
