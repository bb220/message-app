from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

engine = create_engine('sqlite:///messages.db', echo=True)

Base = declarative_base()

# Table definitions
class Message(Base):
    __tablename__ = 'messages'

    # Helper function to convert to dict
    def to_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }
    
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

def init_db():
    """Create all tables"""
    Base.metadata.create_all(engine)

def get_session():
    """ Get a database session """
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session()