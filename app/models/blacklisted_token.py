from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func

from app.db.base import Base


class BlacklistedToken(Base):
    """
    Stores invalidated JWT tokens so logout is enforced server-side.
    Tokens are checked on every protected request.
    """
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, nullable=False, index=True)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)  # for future cleanup jobs

    def __repr__(self):
        return f"<BlacklistedToken(id={self.id}, blacklisted_at={self.blacklisted_at})>"
