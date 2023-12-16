import asyncio
import datetime
import json
from threading import Thread
from typing import Any

import cv2
import numpy as np
import websockets
from PyQt6.QtCore import pyqtSlot, QThread, pyqtSignal
from cv2 import Mat
from numpy import ndarray, dtype
from websockets import WebSocketClientProtocol

from src.app.types import Face2Search, WebsocketRSData
from .client import client
from ...config import qt_logger
from ...utils.decorator import error_handler


class WebSocketDataProcessor:
    """WebSocket data processor"""

    def _decode(self, data: str |
                bytes) -> dict | str | Mat | ndarray[Any, dtype] | ndarray:
        """decode data"""
        raise NotImplementedError

    def _encode(self, data: dict | WebsocketRSData |
                str | bytes) -> str | bytes:
        """encode data"""
        raise NotImplementedError


class WebSocketBase(Thread, WebSocketDataProcessor):
    """
    WebSocket client for sending and receiving messages.

    Methods to be implemented by subclasses:
    - send(data): Sends data through the WebSocket.
    - receive(): Receives data from the WebSocket.
    - start(): Starts the WebSocket connection.
    - stop(): Stops the WebSocket connection.
    """

    def send(self, data: dict | WebsocketRSData | str | bytes):
        """
        Send data through the WebSocket.

        :param data: Data to be sent.
        """
        raise NotImplementedError

    def receive(
            self) -> dict | str | Mat | ndarray[Any, dtype] | ndarray | None:
        """
        Receive data from the WebSocket.

        Returns the received data.
        """
        raise NotImplementedError

    def start_ws(self):
        """
        Start the WebSocket connection as your want.
        """
        super().start()

    def stop_ws(self):
        """
        Stop the WebSocket connection.
        """
        raise NotImplementedError


class WebSocketClient(WebSocketBase):
    """WebsocketClient thread"""

    def __init__(self, ws_type: str | None = None):
        super().__init__()
        self._is_running = False
        self.ws_type: str | None = ws_type
        self.sender_queue = asyncio.Queue()
        self.receiver_queue = asyncio.Queue()
        self.base_url = f"{client.base_ws_url}/identify/{self.ws_type}/ws/"

    def start_ws(self):
        """ start websocket"""
        self._is_running = True
        super().start_ws()
        qt_logger.info(f"{self.base_url} : websocket started")

    def stop_ws(self):
        """stop websocket"""
        self._is_running = False
        self.join()
        qt_logger.info(f"{self.base_url} : websocket stopped")

    def send(self, data: dict | WebsocketRSData | str | bytes):
        """send data to websocket"""
        try:
            self.sender_queue.put_nowait(data)
        except asyncio.QueueFull:
            qt_logger.warning(f"{self.base_url} : sender queue is full")

    def receive(
            self) -> dict | str | Mat | ndarray[Any, dtype] | ndarray | None:
        """receive data from websocket"""
        try:
            return self.receiver_queue.get_nowait()
        except asyncio.QueueEmpty:
            qt_logger.warning(f"{self.base_url} : receiver queue is empty")
            return None

    def run(self):
        """ run websocket"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._connect_websocket())

    async def _connect_websocket(self):
        """connect websocket"""
        time_now = datetime.datetime.now()
        client_id: str = client.user['id'] + time_now.strftime('%Y%m%d%H%M%S')
        uri = self.base_url + client_id
        qt_logger.debug(f"{self.base_url} : websocket connecting")
        async with websockets.connect(uri) as websocket:
            qt_logger.debug(f"{self.base_url} : websocket creating tasks")
            consumer_task = asyncio.create_task(
                self._receive_messages(websocket))
            producer_task = asyncio.create_task(self._send_messages(websocket))
            qt_logger.debug(f"{self.base_url} : websocket connected")
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_EXCEPTION,
            )

            for task in pending:
                task.cancel()

    async def _receive_messages(self, websocket: WebSocketClientProtocol):
        qt_logger.debug(f"{self.base_url} : start receive messages")
        while self._is_running:
            try:
                message = await websocket.recv()
                decoded = self._decode(message)
                await self.receiver_queue.put(decoded)
            except websockets.exceptions.ConnectionClosedError:
                qt_logger.info(f'{self.base_url} : Connection closed')
                break

    async def _send_messages(self, websocket: WebSocketClientProtocol):
        qt_logger.debug(f"{self.base_url} : start send messages")
        while self._is_running:
            try:
                data = await self.sender_queue.get()
                encoded = self._encode(data)
                await websocket.send(encoded)
                self.sender_queue.task_done()
            except websockets.exceptions.ConnectionClosedError:
                qt_logger.info(f'{self.base_url} : Connection closed')
                break

    def _decode(self, data: str |
                bytes) -> dict | str | Mat | ndarray[Any, dtype] | ndarray:
        if isinstance(data, bytes):
            # image
            nd_arr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nd_arr, cv2.IMREAD_COLOR)
            return img
        elif isinstance(data, str):
            try:
                # dict
                data = json.loads(data)
                # qt_logger.debug(f"recv dict data:{data}")
                return data
            except json.JSONDecodeError:
                # pure utf-8 string
                # qt_logger.debug(f"recv str data:{data}")
                return data + '\n'
        else:
            raise TypeError(f"can not decode data:{data}")

    def _encode(self, data: dict | WebsocketRSData |
                str | bytes) -> str | bytes:
        if isinstance(data, WebsocketRSData):
            return data.to_schema().model_dump_json()
        elif isinstance(data, dict):
            return json.dumps(data)
        elif isinstance(data, str) or isinstance(data, bytes):
            return data
        else:
            raise TypeError(f"can not encode data:{data}")


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

        uri = self.base_url + client_id
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
