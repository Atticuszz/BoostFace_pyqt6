# coding=utf-8
import time

from PyQt6.QtCore import pyqtSignal, QThread

from src.app.common.client.web_socket import WebSocketClient
from src.app.config import qt_logger
from src.app.view.component.console_log_widget import ConsoleLogWidget

__all__ = ['create_cloud_log']


class CloudLogM(QThread):
    """
    Cloud log model
    """
    cloud_log_data = pyqtSignal(str)  # Signal to emit new data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ws_client = WebSocketClient("cloud_logging")
        self._is_running = False

    def run(self):
        self.ws_client.start_ws()
        self._is_running = True
        while self._is_running:
            data = self.ws_client.receive()
            if isinstance(data, str):
                self.cloud_log_data.emit(data)
            else:
                qt_logger.warning(f"cloud log data type error:{data}")
            time.sleep(1)

    def stop(self):
        self._is_running = False
        self.ws_client.stop_ws()
        self.wait()


class CloudLogC:
    """
    connect console_append_text to update console log view
    """

    def __init__(self, model: CloudLogM, view: ConsoleLogWidget):
        self.model = model
        self.view = view
        self.model.cloud_log_data.connect(self.view.append_text)
        self.view.close_event = self.model.stop
        self.model.start()


def create_cloud_log(parent=None) -> CloudLogC:
    """
    create cloud log
    :param parent:
    """
    _model = CloudLogM()
    _view = ConsoleLogWidget(parent)
    _controller = CloudLogC(_model, _view)
    return _controller
