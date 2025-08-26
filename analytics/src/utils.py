import os
from dotenv import load_dotenv
from functools import lru_cache
from typing import Optional, List

from .logger_config import logger

@lru_cache()
def load_environment(required_vars: Optional[List[str]] = None) -> bool:
    """
    Load environment variables with validation.
    Args:
        required_vars: List of required environment variable names
    Returns:
        bool: True if successful
    Raises:
        ValueError: If required variables are missing
    """
    try:
        load_dotenv()
        
        if required_vars:
            missing = [var for var in required_vars if not os.getenv(var)]
            if missing:
                raise ValueError(f"Missing required environment variables: {missing}")
        
        return True
    except Exception as e:
        logger.error(f"Environment loading failed: {str(e)}", exc_info=True)
        raise

def ensure_output_dir(path: str) -> None:
    """Ensure output directory exists and is writable"""
    try:
        os.makedirs(path, exist_ok=True)
        # Test if directory is writable
        test_file = os.path.join(path, '.test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except IOError as e:
            raise PermissionError(f"Output directory {path} is not writable: {e}")
    except Exception as e:
        logger.error(f"Failed to create/verify output directory {path}: {e}")
        raise
