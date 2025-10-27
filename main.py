from test_logger import DBService
from src.logger import get_logger

logger = get_logger(__name__)   # <-- Here, __name__ = "__main__"

if __name__ == "__main__":
    logger.info("Starting main...")
    db = DBService()
    db.connect()
