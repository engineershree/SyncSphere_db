from sqlalchemy import Column, String, Enum, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class PermissionType(str, enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    ADMIN = "ADMIN"


class ResourceType(str, enum.Enum):
    USER = "USER"
    EVENT = "EVENT"
    LEAVE_REQUEST = "LEAVE_REQUEST"
    HOLIDAY = "HOLIDAY"
    NOTIFICATION = "NOTIFICATION"
    REPORT = "REPORT"
    SYSTEM = "SYSTEM"


class Permission(BaseModel):
    """
    Permission model for role-based access control.
    """
    __tablename__ = "permissions"
    
    # Basic Information
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    
    # Permission Details
    permission_type = Column(Enum(PermissionType), nullable=False)
    resource_type = Column(Enum(ResourceType), nullable=False)
    
    # Scope
    is_global = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Conditions (JSON string for complex conditions)
    conditions = Column(String(1000), nullable=True)  # JSON conditions for granular permissions
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, type={self.permission_type})>"
    
    def has_permission(self, resource_type: ResourceType, permission_type: PermissionType):
        return (self.resource_type == resource_type and 
                self.permission_type == permission_type and 
                self.is_active and 
                not self.is_deleted)


class RolePermission(BaseModel):
    """
    Role-Permission mapping for role-based access control.
    """
    __tablename__ = "role_permissions"
    
    # Role Information
    role = Column(String(50), nullable=False)  # SUPER_ADMIN, ADMIN, etc.
    
    # Permission Reference
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    permission = relationship("Permission")
    
    def __repr__(self):
        return f"<RolePermission(role={self.role}, permission_id={self.permission_id})>"
