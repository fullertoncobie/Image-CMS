from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Direct connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./image_cms.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} 
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db_session():
    """Get a database session directly"""
    return SessionLocal()

def init_db():
    """Initialize database tables"""
    # Print to console as well for startup debugging
    print(f"Setting up database at {DATABASE_URL}")
    logger.info("Creating database tables if they don't exist")
    Base.metadata.create_all(bind=engine)
    logger.info("Database setup complete")