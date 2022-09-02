import logging


class CustomFormatter(logging.Formatter):

    blue = "\x1b[36;49m"
    green = "\x1b[32;49m"
    yellow = "\x1b[33;49m"
    red = "\x1b[31;49m"
    reset = "\x1b[0m"

    formatStr = "%(asctime)s [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: blue + formatStr + reset,
        logging.INFO: green + formatStr + reset,
        logging.WARNING: yellow + formatStr + reset,
        logging.ERROR: red + formatStr + reset,
        logging.CRITICAL: red + formatStr + reset,
    }

    def format(self, record):
        formatStr = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(formatStr)

        return formatter.format(record)
