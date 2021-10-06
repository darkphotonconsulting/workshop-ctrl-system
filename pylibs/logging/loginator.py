import logging
import sys
#from pylibs.logging.loginator import Loginator

class CustomFormatter(logging.Formatter):
    """CustomFormatter - A colorful and loud formatter for the logging module

    This is an override for the default logging.Formatter class.
    """

    blue = "\u001b[38;5;20m"
    #grey = "\x1b[38;21m"
    grey = "\u001b[38;5;240m"
    #yellow = "\x1b[33;21m"
    yellow = "\u001b[38;5;11m"
    #red = "\x1b[31;20m"
    red = "\u001b[38;5;160m"
    #bold_red = "\x1b[31;1m"
    bold_red = "\u001b[38;5;196m"
    #reset = "\x1b[0m"
    reset = "\u001b[0m"
    format = "executionTime: [%(asctime)s] - moduleName: [%(name)s] - logLevel: [%(levelname)s] - msgContents: %(message)s lineOfCode: (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: "\U0001F527 " + grey + "> "*10 + format + reset,
        logging.INFO: "\U0001F37A " + blue + "> "*10 + format + reset,
        logging.WARNING: "\U0001F449 " + yellow + "> "*10 +  format + reset,
        logging.ERROR: "\U0001F53A " + red + "> "*10 + format + reset,
        logging.CRITICAL: "\U0001F92F " + bold_red + "> "*10 + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Loginator():
    """Loginator - Super snazzy stream log outputs for scripts and stuffs
    """
    def __init__(self,
            logger: logging.Logger = logging.getLogger(name=__file__),
            logger_format: CustomFormatter = CustomFormatter(),
            logger_level: str = 'NOTSET'
    ) -> None:
        """Make a super snazzy Loginator object to stream your messages with Class

        Args:
            logger (logging.Logger, optional): [A logger object, if omitted, one will be created]. Defaults to logging.getLogger(name=__file__).
            logger_format (CustomFormatter, optional): [a logging.Formatter class]. Defaults to CustomFormatter().
            logger_level (str, optional): [The logging level for the logger, by default, all messages are streamed]. Defaults to 'NOTSET'.
        """
        self.logger_levels = {
            "NOTSET": 0,
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        logger.handlers = []
        logger.root.handlers = []
        logging.basicConfig(
           level=logging.NOTSET
        )
        ## levels
        logger.level = self.logger_levels[logger_level.upper()]
        ## handle streaming to console
        stream_handler = logging.StreamHandler(


        )
        stream_handler.setFormatter(logger_format)
        logger.addHandler(stream_handler)
        #print(logger.root.handlers)
        self.logger = logger
        self.logger.root.handlers = []
        #self.logger.info(f"hello from: {self.logger}")
        #print(f"the logger is: {self.logger}")

    def get_logger(self
    ) -> logging.Logger:
        """return the logger instance associated with class object"""
        return self.logger

    def set_logger(self,
        logger: logging.Logger
    ) -> None:
        """[summary]

        Args:
            logger (logging.Logger): override the instances logger (untested)
        """
        self.logger = logger
