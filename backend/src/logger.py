# This file creates the shared logging system used throughout ToroAI.
# Workflow of this file is as follows : application event -> logger -> terminal output + log file


import logging
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    import colorlog
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False


try:
    from backend.config import LOG_LEVEL, LOG_DIR
except Exception:
    LOG_LEVEL = "INFO"
    LOG_DIR = Path("logs")
    LOG_DIR.mkdir(exist_ok=True)


# convert the log time to Los Angeles time
def los_angeles_time(timestamp):
    return datetime.fromtimestamp(
        timestamp,
        ZoneInfo("America/Los_Angeles")
    ).timetuple()


def get_logger(name):
    # get a logger with this name
    logger = logging.getLogger(name)

    # to avoid duplicate log messages
    if logger.handlers:
        return logger

    # which log level to use?
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # how the terminal log message should look
    if HAS_COLOR:
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red"
            }
        )
    else:
        console_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        )

    # make terminal logs use Los Angeles time
    console_formatter.converter = los_angeles_time

    # how the saved log file should look
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )

    # make saved logs use Los Angeles time
    file_formatter.converter = los_angeles_time

    # show logs in the terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # where is the log file saved?
    log_file = LOG_DIR / "toroai.log"

    # save logs into toroai.log 
    #pathway => backend/logs/toroai.log
    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


