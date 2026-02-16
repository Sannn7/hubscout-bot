"""
PostgreSQL database connection and models.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://hubscout:hubscout@localhost:5432/hubscout"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PropertyListing(Base):
    __tablename__ = "property_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String, unique=True, index=True)
    neighborhood = Column(String, index=True)
    property_type = Column(String)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    sqft = Column(Integer)
    price = Column(Float)
    listing_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    has_parking = Column(Boolean)
    pet_friendly = Column(Boolean)
    near_transit = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)