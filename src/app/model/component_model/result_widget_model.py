# coding=utf-8
import asyncio
import datetime
import json

import websockets
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

from src.app.common import signalBus
from src.app.common.client import client
from src.app.plugin.decorator import error_handler


class ResultWidgetModel(QThread):
    """ Result widget model"""
    newData = pyqtSignal(list)  # Signal to emit new data

    def __init__(self):
        super().__init__()

        self.headers = ['ID', 'Name', 'Time']
        self.column_count = len(self.headers)
        self._is_running = False

    @error_handler
    async def connect_websocket(self):
        """
        connect websocket
        """
        time_now = datetime.datetime.now()
        client_id: str = client.user['id'] + time_now.strftime('%Y%m%d%H%M%S')
        uri = f"{client.base_ws_url}/identify/ws/{client_id}"
        async with websockets.connect(uri, extra_headers=client._auth_header()) as websocket:
            while self._is_running:
                message = await websocket.recv()
                data: dict = json.loads(message)
                new_data = [data["id"], data["name"], data["time"]]
                self.newData.emit(new_data)

    def run(self):
        """ run websocket"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._is_running = True
        signalBus.is_identify_running.emit(True)
        client.login(email="zhouge1831@gmail.com", password="Zz030327#")
        loop.run_until_complete(self.connect_websocket())

    @pyqtSlot(bool)
    def update_is_running(self, state: bool):
        """ update is_running"""
        self._is_running = state

    def stop(self):
        self._is_running = False
        self.wait()
