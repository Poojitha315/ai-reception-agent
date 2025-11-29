from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Call(Base):
    """
    Database model for storing call information.
    """
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    caller_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    priority = Column(String(20), nullable=False, default='Medium')
    summary = Column(Text, nullable=False)
    transcript = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'caller_name': self.caller_name,
            'phone': self.phone,
            'department': self.department,
            'priority': self.priority,
            'summary': self.summary,
            'transcript': self.transcript,
            'response': self.response
        }
