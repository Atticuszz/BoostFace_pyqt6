import asyncio
import datetime
import json

import cv2
import numpy as np
import websockets
from PyQt6.QtCore import pyqtSlot, QThread, pyqtSignal

from src.app.types import Face2Search
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
        self.sender_queue = asyncio.Queue()

    def send(self, data: Face2Search | dict | str):
        """send data to websocket"""
        try:
            self.sender_queue.put_nowait(data)
        except asyncio.QueueFull:
            qt_logger.warning("message queue is full")

    def receive(self, data: dict | str):
        """receive data from websocket"""
        raise NotImplementedError

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
                    await self._send_ws_data(websocket)
                    decoded_data: dict | str = await self._load_ws_data(websocket)
                    qt_logger.debug(f"recv decoded_data:{decoded_data}")
                    self.receive(decoded_data)
                except websockets.exceptions.ConnectionClosedError:
                    qt_logger.info(f'Connection closed: {uri}')
                    break

    # TODO: thread control

    @pyqtSlot(bool)
    def update_is_running(self, state: bool):
        """ update is_running"""
        self._is_running = state

    def stop_ws(self):
        """for closeEvent"""
        self._is_running = False
        self.wait()

    @staticmethod
    async def _load_ws_data(
            websocket: websockets.WebSocketClientProtocol) -> dict | str:
        """ load websocket data
        :exception  websockets.exceptions.ConnectionClosedError
        """

        recv_date: str | bytes = await websocket.recv()

        if isinstance(recv_date, bytes):
            # image
            nd_arr = np.frombuffer(recv_date, np.uint8)
            img = cv2.imdecode(nd_arr, cv2.IMREAD_COLOR)
            return img
        else:
            try:
                # dict
                data = json.loads(recv_date)
                qt_logger.debug(f"recv dict data:{data}")
                return data
            except json.JSONDecodeError:
                # pure utf-8 string
                qt_logger.debug(f"recv str data:{recv_date}")
                return recv_date + '\n'

    async def _send_ws_data(self, websocket: websockets.WebSocketClientProtocol):
        """ send websocket Image data
        :exception  websockets.exceptions.ConnectionClosedError
        """
        data = await self.sender_queue.get()
        if not data:
            return
        if isinstance(data, Face2Search):
            await websocket.send(data.to_schema().model_dump_json())
        else:
            try:
                data = json.dumps(data)
            except json.JSONDecodeError:
                await websocket.send(data)
