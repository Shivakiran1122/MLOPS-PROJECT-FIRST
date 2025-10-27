from src.logger import get_logger
class DBService:
    def __init__(self):
        self.logger = get_logger(__name__)   # <-- Here, __name__ = "db_service"

    def connect(self):
        self.logger.info("DB connected")
