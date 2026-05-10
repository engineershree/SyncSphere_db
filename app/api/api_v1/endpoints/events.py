from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.event import Event, EventStatus, EventType
from app.schemas.event import EventCreate, EventUpdate, EventResponse

router = APIRouter()


@router.get("/", response_model=List[EventResponse])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: EventStatus = Query(None),
    event_type: EventType = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get all events.
    """
    query = db.query(Event).filter(Event.is_deleted == False)
    
    # Filter by status and type if provided
    if status:
        query = query.filter(Event.status == status)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    # Non-admin users can only see published events
    if not current_user.is_admin():
        query = query.filter(
            Event.status == EventStatus.PUBLISHED,
            Event.is_public == True
        )
    
    events = query.offset(skip).limit(limit).all()
    return events


@router.post("/", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new event.
    """
    # Check if user can manage events
    if not current_user.can_manage_events():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create events"
        )
    
    event = Event(
        **event_data.dict(),
        creator_id=current_user.id,
        organizer_id=event_data.organizer_id or current_user.id
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get event by ID.
    """
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.is_deleted == False
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check access permissions
    if (not current_user.is_admin() and 
        not current_user.can_manage_events() and
        not event.is_public and
        event.creator_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this event"
        )
    
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update event information.
    """
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.is_deleted == False
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check permissions
    if (not current_user.is_admin() and 
        not current_user.can_manage_events() and
        event.creator_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this event"
        )
    
    # Update event fields
    update_data = event_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Soft delete event.
    """
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.is_deleted == False
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check permissions
    if (not current_user.is_admin() and 
        not current_user.can_manage_events() and
        event.creator_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this event"
        )
    
    event.soft_delete()
    db.commit()
    
    return {"message": "Event deleted successfully"}
