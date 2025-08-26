import asyncio

from .bridge import NotificationBridge
from .logger_config import logger


def main():
    
    bridge = NotificationBridge()
    asyncio.run(bridge.run())

if __name__ == "__main__":
    main()
