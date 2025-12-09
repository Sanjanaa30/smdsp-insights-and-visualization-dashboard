import logging
import os
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv


class Logger:
    """
    Logger is responsible for creating and configuring a logger instance
    based on environment variables.

    Environment Variables:
        - LOG_LEVEL: The logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO.
        - LOG_MODE: Determines the output mode ("FILE" or "STREAM"). Default is STREAM.
        - CHAN_LOG_FILE: File path for the log file if LOG_MODE is FILE. Default is '4chan_crawler.log'.

    Usage:
        >>> logger= Logger("my_logger")
        >>> logger = logger.get_logger()
        >>> logger.info("This is a log message.")
    """

    def __init__(self, name, file_name: str = ""):
        load_dotenv()
        self.file_name = file_name
        self.logger = self._set_config(name)

    def _set_config(self, name):
        logger = logging.getLogger(name)
        logger.propagate = False

        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        numeric_level = getattr(logging, log_level_str, logging.INFO)
        logger.setLevel(numeric_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        log_mode = os.getenv("LOG_MODE", "STREAM").upper()

        if not logger.handlers:  # Prevent duplicate handlers
            if log_mode == "FILE":
                if self.file_name != "":
                    log_dir = os.getenv("LOG_DIR", "default.log")
                    log_file = f"{log_dir}/{self.file_name}"
                    log_dir = os.path.dirname(log_file)
                else:
                    log_file = os.getenv("LOG_FILE", "default.log")
                    log_dir = os.path.dirname(log_file)

                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)

                # Use TimedRotatingFileHandler to avoid Windows file locking issues
                fh = TimedRotatingFileHandler(
                    log_file,
                    when="midnight",
                    interval=1,
                    backupCount=7,
                    encoding="utf-8",
                    delay=True,  # Delays opening the file until first write
                )
                fh.setFormatter(formatter)
                logger.addHandler(fh)
            else:
                handler = logging.StreamHandler()
                handler.setFormatter(formatter)
                logger.addHandler(handler)

        return logger

    def get_logger(self):
        return self.logger
