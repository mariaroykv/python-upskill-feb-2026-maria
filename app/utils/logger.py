import logging
import sys


class Logger:
    logger: logging.Logger

    def __init__(self):
        _logger = logging.getLogger(__name__)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        _logger.setLevel(level="INFO")

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        _logger.addHandler(console_handler)
        _logger.propagate = False  # Prevent double logging
        self.logger = _logger

    def info(self, message: str):
        self.logger.info(msg=message, stacklevel=2)

    def warning(self, message: str):
        self.logger.warning(msg=message, stacklevel=2)

    def error(self, message: str):
        self.logger.error(msg=message, stacklevel=2)

    def debug(self, message: str):
        self.logger.debug(msg=message, stacklevel=2)

    def exception(self, message: str, exception: Exception):
        log_message = f"{message} : {exception}"
        self.logger.exception(msg=log_message, exc_info=True, stacklevel=2)


logger = Logger()


class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage().lower()
        if "/api/v1/health" in msg and "200" in msg:
            return False
        return True


def get_uvicorn_logger_config():
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"
            },
            "access": {
                "format": "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
            },
        },
        "filters": {
            "health_check_filter": {
                "()": "app.utils.logger.HealthCheckFilter",
            },
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "level": "INFO",
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "filters": ["health_check_filter"],
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
