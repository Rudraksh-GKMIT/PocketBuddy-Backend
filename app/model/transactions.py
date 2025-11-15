from sqlalchemy import Column , String, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from app.model.base import BaseModel


class Transaction(BaseModel):
    __tablename__ = "transactions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,index=True
    )
    type = Column(String, nullable=False)  # e.g., 'need', 'luxary'
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
