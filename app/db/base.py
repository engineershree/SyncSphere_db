from sqlalchemy import Column, Integer, DateTime, Boolean, String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from typing import Any, Dict
import uuid

Base = declarative_base()


class BaseModel(Base):
    """
    Base model class with common fields for all models.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def soft_delete(self):
        """
        Soft delete the record.
        """
        self.is_deleted = True
        self.deleted_at = func.now()
    
    def restore(self):
        """
        Restore soft deleted record.
        """
        self.is_deleted = False
        self.deleted_at = None
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, uuid={self.uuid})>"
