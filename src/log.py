import logging

from coloredlogs import ColoredFormatter

logs = logging.getLogger("FixMiYouShe")
logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))
root_logger = logging.getLogger()
root_logger.setLevel(logging.ERROR)
root_logger.addHandler(logging_handler)
logging.basicConfig(level=logging.INFO)
logs.setLevel(logging.INFO)
logger = logging.getLogger("FixMiYouShe")
