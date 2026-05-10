from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.core.deps import get_current_user, get_current_hr_user
from app.models.user import User
from app.models.leave_request import LeaveRequest, LeaveStatus, LeaveType
from app.schemas.leave_request import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse

router = APIRouter()


@router.get("/", response_model=List[LeaveRequestResponse])
async def get_leave_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: LeaveStatus = Query(None),
    leave_type: LeaveType = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get leave requests.
    """
    query = db.query(LeaveRequest).filter(LeaveRequest.is_deleted == False)
    
    # Non-HR users can only see their own leave requests
    if not current_user.is_hr():
        query = query.filter(LeaveRequest.user_id == current_user.id)
    
    # Filter by status and type if provided
    if status:
        query = query.filter(LeaveRequest.status == status)
    if leave_type:
        query = query.filter(LeaveRequest.leave_type == leave_type)
    
    leave_requests = query.offset(skip).limit(limit).all()
    return leave_requests


@router.post("/", response_model=LeaveRequestResponse)
async def create_leave_request(
    leave_data: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new leave request.
    """
    leave_request = LeaveRequest(
        **leave_data.dict(),
        user_id=current_user.id
    )
    
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    
    return leave_request


@router.get("/{leave_request_id}", response_model=LeaveRequestResponse)
async def get_leave_request(
    leave_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get leave request by ID.
    """
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_request_id,
        LeaveRequest.is_deleted == False
    ).first()
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    # Check access permissions
    if (not current_user.is_hr() and 
        leave_request.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this leave request"
        )
    
    return leave_request


@router.put("/{leave_request_id}", response_model=LeaveRequestResponse)
async def update_leave_request(
    leave_request_id: int,
    leave_data: LeaveRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update leave request.
    """
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_request_id,
        LeaveRequest.is_deleted == False
    ).first()
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    # Check permissions - users can only update their own pending requests
    if (not current_user.is_hr() and 
        (leave_request.user_id != current_user.id or 
         leave_request.status != LeaveStatus.PENDING)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this leave request"
        )
    
    # Update leave request fields
    update_data = leave_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(leave_request, field, value)
    
    db.commit()
    db.refresh(leave_request)
    
    return leave_request


@router.post("/{leave_request_id}/approve")
async def approve_leave_request(
    leave_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    Approve leave request (HR only).
    """
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_request_id,
        LeaveRequest.is_deleted == False
    ).first()
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    if leave_request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request is not pending"
        )
    
    leave_request.status = LeaveStatus.APPROVED
    leave_request.approver_id = current_user.id
    
    db.commit()
    
    return {"message": "Leave request approved successfully"}


@router.post("/{leave_request_id}/reject")
async def reject_leave_request(
    leave_request_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    Reject leave request (HR only).
    """
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_request_id,
        LeaveRequest.is_deleted == False
    ).first()
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    if leave_request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request is not pending"
        )
    
    leave_request.status = LeaveStatus.REJECTED
    leave_request.approver_id = current_user.id
    leave_request.approver_comments = reason
    
    db.commit()
    
    return {"message": "Leave request rejected successfully"}
