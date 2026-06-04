import logging
from logtail import LogtailHandler

from app.core.config import settings

def set_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)


    fmt = logging.Formatter(
        "%(asctime)s- %(name)s- %(levelname)s- %(message)s"
    )

    console_log = logging.StreamHandler()
    file_log = logging.FileHandler("app.log")
    better_stack_handler = LogtailHandler(source_token=settings.LOG_TOKEN)

    console_log.setFormatter(fmt)
    file_log.setFormatter(fmt)
    better_stack_handler.setFormatter(fmt)

    logger.handlers = [console_log, file_log, better_stack_handler]

