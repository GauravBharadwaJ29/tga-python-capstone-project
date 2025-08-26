from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import POSTGRES_URI
from .logger_config import logger
import os

try:
    logger.info(f"Initializing database connection with URI: {POSTGRES_URI}")
    engine = create_async_engine(
        POSTGRES_URI, 
        echo=os.getenv('SQL_DEBUG', '').lower() == 'true'
    )
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    Base = declarative_base()
    logger.info("Database configuration completed successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise
