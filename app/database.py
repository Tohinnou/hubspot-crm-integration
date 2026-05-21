from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from datetime import datetime
import os
from dotenv import load_dotenv
from app.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class HubSpotToken(Base):
    __tablename__ = "hubspot_tokens"
    
    portal_id = Column(String, primary_key=True, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

def create_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()