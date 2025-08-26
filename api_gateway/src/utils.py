from fastapi.responses import JSONResponse
from .logger_config import logger  # Add this import
from typing import Optional, List
from functools import lru_cache
import os
from dotenv import load_dotenv

def custom_error(message: str, code: int = 400):
    logger.error(f"Error response: {code} - {message}")
    return JSONResponse(
        status_code=code,
        content={"error": {"code": code, "message": message}}
    )

@lru_cache()
def load_environment(required_vars: Optional[List[str]] = None) -> bool:
    """Load environment variables with validation"""
    try:
        load_dotenv()
        if required_vars:
            missing = [var for var in required_vars if not os.getenv(var)]
            if missing:
                print(f"Missing required environment variables: {missing}")  # Use print since logger isn't set up
                return False
        return True
    except Exception as e:
        print(f"Failed to load environment: {str(e)}")  # Use print since logger isn't set up
        return False
