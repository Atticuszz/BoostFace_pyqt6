import logging

from src.app.common import signalBus

log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s\n")


class QLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()

        self.setFormatter(log_format)

    def emit(self, record):
        """rewrite where and how to send logging message"""
        log_entry = self.format(record)
        # auto send log message to the bus
        signalBus.log_message.emit(log_entry)


qt_logging_handler = QLoggingHandler()
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)

# set level to debug
logging.basicConfig(handlers=[qt_logging_handler, stream_handler], level=logging.DEBUG)
qt_logger = logging.getLogger()
