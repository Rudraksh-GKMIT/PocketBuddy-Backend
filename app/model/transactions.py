from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float


from .base import BaseModel

class Transaction(BaseModel):
    __tablename__ = "transactions"

    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # e.g., 'need', 'luxary'
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)


