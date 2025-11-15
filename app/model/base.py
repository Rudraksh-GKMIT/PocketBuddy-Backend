from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class BaseModel(Base):
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),primary_key=True,default=uuid.uuid4
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
