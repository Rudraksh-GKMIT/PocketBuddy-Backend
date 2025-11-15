from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel


class Family(BaseModel):
    __tablename__ = "families"

    name = Column(String, nullable=False)

    # Relationships
    users = relationship("User", back_populates="family", cascade="all, delete")


class User(BaseModel):
    __tablename__ = "users"

    family_id = Column(
            UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

    # Relationships
    family = relationship("Family", back_populates="users")
    roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete", passive_deletes=True
    )


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, unique=True, nullable=False)

    # Relationships
    user_roles = relationship("UserRole", back_populates="role")


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")
