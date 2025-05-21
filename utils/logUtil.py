import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(module_name, log_dir="logs"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        f"%(asctime)s [%(levelname)s] [{module_name}: %(lineno)d]: %(message)s"
    )

    file_handler = RotatingFileHandler(
        f"{log_dir}/app.log",
        maxBytes=5*1024*1024,
        backupCount=2
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(formatter)
    # logger.addHandler(console_handler)

    return logger
