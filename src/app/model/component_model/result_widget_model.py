# coding=utf-8

from PyQt6.QtCore import pyqtSignal

from src.app.common import signalBus
from src.app.common.client import client, WebSocketThread
from src.app.plugin.decorator import error_handler
from src.types import Image


class ResultWidgetModel(WebSocketThread):
    """ Result widget model"""
    newData = pyqtSignal(list)  # Signal to emit new data
    running_signal = signalBus.is_identify_running

    def __init__(self):
        super().__init__(ws_type="identify")
        client.login(email="zhouge1831@gmail.com", password="Zz030327#")
        self.headers = ['ID', 'Name', 'Time']
        self.column_count = len(self.headers)
        self._is_running = False

    @error_handler
    def working(self, data: dict | str | Image):
        """add your working in websocket"""
        if not isinstance(data, dict):
            raise TypeError("data must be dict")
        new_data = [data["id"], data["name"], data["time"]]
        self.newData.emit(new_data)
