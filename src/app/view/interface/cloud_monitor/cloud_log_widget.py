# coding=utf-8
from PyQt6.QtCore import pyqtSignal

from src.app.common.client import WebSocketThread
from src.app.types import Image
from src.app.view.component.console_log_widget import ConsoleLogWidget

__all__ = ['create_cloud_log']


class CloudLogM(WebSocketThread):
    """
    Cloud log model
    """
    cloud_log_data = pyqtSignal(str)  # Signal to emit new data

    def __init__(self):
        super().__init__(ws_type="cloud_logging")

    def working(self, data: dict | str | Image):
        if not isinstance(data, str):
            raise TypeError("data must be str")
        self.cloud_log_data.emit(data)


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
