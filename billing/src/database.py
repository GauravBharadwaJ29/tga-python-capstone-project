from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import POSTGRES_URI, SQL_DEBUG, ErrorMessages
from .logger_config import logger
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

try:
    logger.info(f"Initializing database connection with URI: {POSTGRES_URI}")
    engine = create_async_engine(POSTGRES_URI, echo=SQL_DEBUG)
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    Base = declarative_base()
    logger.info("Database configuration completed")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise RuntimeError(ErrorMessages.DATABASE_CONNECTION_FAILED.format(str(e)))
