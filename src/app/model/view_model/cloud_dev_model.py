# coding=utf-8

from PyQt6.QtCore import pyqtSignal

from src.app.common.client import WebSocketThread, client
from src.types import Image


class CloudServerModel(WebSocketThread):
    """
    :var server_info: dict, server information
    """
    cloud_dev_data = pyqtSignal(str)  # Signal to emit new data

    def __init__(self):
        super().__init__(ws_type="cloud_logging")
        self.server_info = {
            'domain': "www.digitalocean.com",
            'location': 'New York',
            'OS': 'Ubuntu 20.04',
            'CPU': '4 vCPU',
            'RAM': '8 GB',
            'GPU': 'NVIDIA RTX 3080',
            'Storage': '1 TB',
        }
        client.login(email="zhouge1831@gmail.com", password="Zz030327#")

    def working(self, data: dict | str | Image):
        if not isinstance(data, str):
            raise TypeError("data must be str")
        self.cloud_dev_data.emit(data)
