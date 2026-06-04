from app.db.dbengine import engine
from app.models.models import Base

import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("creating tables....")
    Base.metadata.create_all(bind=engine)
    logger.info("Table created successfully")

