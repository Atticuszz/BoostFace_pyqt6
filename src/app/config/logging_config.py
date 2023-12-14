import logging

from src.app.common import signalBus


class QLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        log_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        self.setFormatter(log_format)

    def emit(self, record):
        """rewrite where and how to send logging message"""
        log_entry = self.format(record)
        # auto send log message to the bus
        signalBus.log_message.emit(log_entry)


qt_logging_handler = QLoggingHandler()
# set level to debug
logging.basicConfig(handlers=[qt_logging_handler], level=logging.DEBUG)
qt_logger = logging.getLogger()
