from enum import Enum
from sqlalchemy import Column, Enum as SQLEnum, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.model.base import BaseModel


class TypeEnum(str, Enum):
    food = "food"
    travel = "travel"
    shopping = "shopping"
    entertainment = "entertainment"
    bills = "bills"
    other = "other"


class Transaction(BaseModel):
    __tablename__ = "transactions"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type = Column(
        SQLEnum(
            TypeEnum,
            name="type_enum",   
            create_type=False   
        ),
        nullable=False,
    )

    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
