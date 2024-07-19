import logging
import sys
from logging import StreamHandler

import structlog


class LoggerFactory:
    @staticmethod
    def configure_logging(
        logger_name=None, level=logging.INFO, handler=None, processors=None
    ):
        """
        Configures the logging for the specified logger.

        :param logger_name (str): The name of the logger. If not provided, a root logger will be used.
        :param level (int): The logging level. Defaults to logging.INFO.
        :param handler (logging.Handler): The logging handler to use. If not provided, a StreamHandler with stdout will be used.
        :param processors (list): The list of structlog processors to apply. If not provided, a default set of processors will be used.

        Returns:
            structlog.BoundLogger: The configured logger.

        """
        if processors is None:
            processors = [
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ]

        # Create a new logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        # Use the provided handler or default to StreamHandler with stdout
        if handler is None:
            handler = StreamHandler(sys.stdout)

        handler.setFormatter(logging.Formatter("%(message)s"))

        # Add handler to logger if not already added
        if not logger.handlers:
            logger.addHandler(handler)

        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        return structlog.wrap_logger(logger)

    @staticmethod
    def get_logger(name=None, level=logging.INFO, handler=None, processors=None):
        """
        Retrieves a configured logger with the specified name.

        :param name (str): The name of the logger. If not provided, a root logger will be used.
        :param level (int): The logging level. Defaults to logging.INFO.
        :param handler (logging.Handler): The logging handler to use. If not provided, a StreamHandler with stdout will be used.
        :param processors (list): The list of structlog processors to apply. If not provided, a default set of processors will be used.

        Returns:
            structlog.BoundLogger: The configured logger.

        """
        return LoggerFactory.configure_logging(name, level, handler, processors)
