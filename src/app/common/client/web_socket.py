import asyncio
import datetime
import json

import cv2
import numpy as np
import websockets
from PyQt6.QtCore import pyqtSlot, QThread, pyqtSignal

from src.app.types import Image
from .client import client
from ...config import qt_logger
from ...utils.decorator import error_handler


class WebSocketThread(QThread):
    """Websocket thread
    :var ws_type: str, websocket type
    """
    running_signal = pyqtSignal(bool)

    def __init__(self, ws_type: str | None = None):
        super().__init__()
        self._is_running = False
        self.ws_type: str | None = ws_type

    def working(self, data: dict | str | Image):
        """add your working in websocket"""
        pass

    def run(self):
        """ run websocket"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._is_running = True
        if not self.running_signal:
            raise ValueError("running_signal must be set")
        self.running_signal.emit(True)
        loop.run_until_complete(self.connect_websocket())

    @error_handler
    async def connect_websocket(self):
        """
        connect websocket
        """
        time_now = datetime.datetime.now()
        client_id: str = client.user['id'] + time_now.strftime('%Y%m%d%H%M%S')
        if not self.ws_type:
            raise TypeError("ws_type must be set")
        uri = f"{client.base_ws_url}/identify/{self.ws_type}/ws/{client_id}"
        async with websockets.connect(uri, extra_headers=client._auth_header()) as websocket:
            while self._is_running:
                try:
                    decoded_data: dict | str | Image = await self._load_ws_data(websocket)
                except websockets.exceptions.ConnectionClosedError:
                    qt_logger.info(f'Connection closed: {uri}')
                    break

                self.working(decoded_data)

    @pyqtSlot(bool)
    def update_is_running(self, state: bool):
        """ update is_running"""
        self._is_running = state

    def stop(self):
        """for closeEvent"""
        self._is_running = False
        self.wait()

    @staticmethod
    async def _load_ws_data(
            websocket: websockets.WebSocketClientProtocol) -> dict | str | Image:
        """ load websocket data
        :exception  websockets.exceptions.ConnectionClosedError
        """

        recv_date: str | bytes | Image = await websocket.recv()

        if isinstance(recv_date, bytes):
            # image
            nd_arr = np.frombuffer(recv_date, np.uint8)
            img = cv2.imdecode(nd_arr, cv2.IMREAD_COLOR)
            return img
        else:
            try:
                # dict
                return json.loads(recv_date)
            except json.JSONDecodeError:
                # pure utf-8 string
                return recv_date + '\n'
