from pydantic import BaseModel, EmailStr
from uuid import UUID

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
    role: str | None = None


class TransactionCreate(BaseModel):
    user_id: UUID
    type: str
    amount: float
    description: str | None = None


class TransactionUpdate(BaseModel):
    type: str | None = None
    amount: float | None = None
    description: str | None = None


class TransactionResponse(BaseModel):
    id: UUID
    user_id:UUID
    type: str
    amount: float
    description: str | None

    class Config:
        from_attributes = True
