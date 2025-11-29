from typing import List, Optional
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Call
import os

# Database URL
DATABASE_URL = "sqlite:///./calls.db"

# Create engine and session factory
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """
    Get a database session.
    
    Yields:
        Session: A SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_call(
    db: Session,
    transcript: str,
    summary: str,
    caller_name: Optional[str] = None,
    phone: Optional[str] = None,
    department: Optional[str] = None,
    priority: str = 'Medium',
    response: Optional[str] = None
) -> Call:
    """
    Save a new call record to the database.
    
    Args:
        db: Database session
        transcript: The full transcript of the call
        summary: Summary of the call
        caller_name: Name of the caller (optional)
        phone: Caller's phone number (optional)
        department: Department relevant to the call (optional)
        priority: Priority level (Low/Medium/High)
        response: AI-generated response (optional)
        
    Returns:
        Call: The created call record
    """
    db_call = Call(
        caller_name=caller_name,
        phone=phone,
        department=department,
        priority=priority,
        summary=summary,
        transcript=transcript,
        response=response
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call

def get_all_calls(db: Session, skip: int = 0, limit: int = 100) -> List[Call]:
    """
    Retrieve all calls from the database, ordered by most recent first.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[Call]: List of call records
    """
    return db.query(Call).order_by(Call.timestamp.desc()).offset(skip).limit(limit).all()

def get_call_by_id(db: Session, call_id: int) -> Optional[Call]:
    """
    Retrieve a single call by its ID.
    
    Args:
        db: Database session
        call_id: ID of the call to retrieve
        
    Returns:
        Call: The call record if found, None otherwise
    """
    return db.query(Call).filter(Call.id == call_id).first()

def mask_phone(phone: Optional[str]) -> str:
    """
    Mask a phone number for display (shows first 4 digits only).
    
    Args:
        phone: The phone number to mask
        
    Returns:
        str: Masked phone number (e.g., 1234******)
    """
    if not phone:
        return "N/A"
    if len(phone) <= 4:
        return phone
    return f"{phone[:4]}{'*' * (len(phone) - 4)}"
